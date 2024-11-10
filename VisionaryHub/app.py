from flask import Flask, render_template, request, redirect, url_for, send_file, session
import pandas as pd
import plotly.express as px
import os
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session data

# Configuration for file uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Route for the upload page
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files.get("file")  # Use .get to avoid KeyError
        if file and file.filename.endswith(('.csv', '.xlsx')):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            session["filename"] = file.filename  # Store filename in session
            return redirect(url_for("data_summary"))
        else:
            return "Please upload a valid CSV or Excel file.", 400  # Error message if invalid file
    return render_template("upload.html")

# Route for the data summary page
@app.route("/data_summary", methods=["GET", "POST"])
def data_summary():
    filename = session.get("filename")
    if not filename:
        return redirect(url_for("upload_file"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    # Load data and generate summary
    try:
        data = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)
    except Exception as e:
        return f"Error reading file: {e}", 500  # Handle file read errors

    summary = data.describe().to_html(classes="summary-table")
    first_rows = data.head().to_html(classes="summary-table")
    
    # Render the data summary page with summary stats and first few rows
    return render_template("summary.html", summary=summary, first_rows=first_rows)

# Route for the visualization options page
@app.route("/visualization_options", methods=["GET", "POST"])
def visualization_options():
    filename = session.get("filename")
    if not filename:
        return redirect(url_for("upload_file"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    data = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)
    columns = data.columns.tolist()

    if request.method == "POST":
        chart_type = request.form.get("chart_type")
        x_column = request.form.get("x_column")
        y_column = request.form.get("y_column")

        if not chart_type or not x_column:
            return "Please select a chart type and X-axis column.", 400

        session["chart_type"] = chart_type
        session["x_column"] = x_column
        session["y_column"] = y_column if y_column else None

        return redirect(url_for("visualization_output"))

    return render_template("visualization_options.html", data_columns=columns)

# Route for generating the chart and displaying the output
# Route for generating the chart and displaying the output
@app.route("/visualization_output", methods=["GET"])
def visualization_output():
    filename = session.get("filename")
    chart_type = session.get("chart_type")
    x_column = session.get("x_column")
    y_column = session.get("y_column")

    # Confirm session data
    print("Session - Filename:", filename)
    print("Session - Chart Type:", chart_type)
    print("Session - X Column:", x_column)
    print("Session - Y Column:", y_column)

    # Verify that all required session data is present
    if not filename or not chart_type or not x_column:
        return redirect(url_for("upload_file"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    data = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)

    # Generate the appropriate chart
    try:
        if chart_type == "Bar" and y_column:
            fig = px.bar(data, x=x_column, y=y_column, title="Bar Chart")
        elif chart_type == "Line" and y_column:
            fig = px.line(data, x=x_column, y=y_column, title="Line Chart")
        elif chart_type == "Scatter" and y_column:
            fig = px.scatter(data, x=x_column, y=y_column, title="Scatter Plot")
        elif chart_type == "Histogram":
            fig = px.histogram(data, x=x_column, title="Histogram")
        else:
            return "Y-axis column is required for the selected chart type.", 400

        # Convert the chart to HTML to embed it
        graph_html = fig.to_html(full_html=False)
    except ValueError as e:
        print("Chart generation error:", e)
        return f"Error generating chart: {e}", 400

    # Pass the generated HTML to the output template
    return render_template("output.html", chart_html=graph_html)


  
# Route to download the generated chart as an image
import io  # Ensure this import is included

# Route to download the generated chart as an image
@app.route("/download_chart", methods=["POST"])
def download_chart():
    filename = session.get("filename")
    chart_type = session.get("chart_type")
    x_column = session.get("x_column")
    y_column = session.get("y_column")

    # Check for required session variables
    if not filename or not chart_type or not x_column:
        return redirect(url_for("upload_file"))

    # Load the data from the file
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    data = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)

    # Generate the appropriate chart
    try:
        if chart_type == "Bar" and y_column:
            fig = px.bar(data, x=x_column, y=y_column, title="Bar Chart")
        elif chart_type == "Line" and y_column:
            fig = px.line(data, x=x_column, y=y_column, title="Line Chart")
        elif chart_type == "Scatter" and y_column:
            fig = px.scatter(data, x=x_column, y=y_column, title="Scatter Plot")
        elif chart_type == "Histogram":
            fig = px.histogram(data, x=x_column, title="Histogram")
        else:
            return "Y-axis column is required for the selected chart type.", 400

        # Save the chart as an image to a BytesIO object
        img_bytes = io.BytesIO()
        fig.write_image(img_bytes, format="png")
        img_bytes.seek(0)  # Move cursor to start of the BytesIO object

        # Return the file as a download response
        return send_file(
            img_bytes,
            as_attachment=True,
            download_name="chart.png",
            mimetype="image/png"
        )

    except Exception as e:
        print("Error during chart generation:", e)
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
