document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("upload-form");
    const chartContainer = document.getElementById("chart-container");
    const chartType = document.getElementById("chart-type");
    const xAxis = document.getElementById("x-axis");
    const yAxis = document.getElementById("y-axis");
    const generateChartBtn = document.getElementById("generate-chart-btn");
    const uploadFeedback = document.getElementById("upload-feedback");
    const downloadBtn = document.getElementById("download-btn");
    
    // Function to submit upload form with AJAX
    uploadForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        
        fetch("/", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate x/y-axis selectors with data columns
                const columns = data.columns;
                xAxis.innerHTML = yAxis.innerHTML = "";
                columns.forEach(column => {
                    xAxis.innerHTML += `<option value="${column}">${column}</option>`;
                    yAxis.innerHTML += `<option value="${column}">${column}</option>`;
                });
                uploadFeedback.textContent = "File uploaded successfully!";
                uploadFeedback.style.color = "green";
            } else {
                uploadFeedback.textContent = "File upload failed. Please try again.";
            }
        })
        .catch(error => {
            console.error("Error:", error);
            uploadFeedback.textContent = "An error occurred.";
        });
    });

    // Generate chart based on selected options
    generateChartBtn.addEventListener("click", function () {
        const formData = new FormData();
        formData.append("chart_type", chartType.value);
        formData.append("x_column", xAxis.value);
        formData.append("y_column", yAxis.value);

        fetch("/generate_chart", {
            method: "POST",
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            chartContainer.innerHTML = html;
            downloadBtn.style.display = "block"; // Show download button
        })
        .catch(error => console.error("Error generating chart:", error));
    });

    // Download chart
    downloadBtn.addEventListener("click", function () {
        fetch("/download_chart", {
            method: "GET"
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = "chart.png";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error("Error downloading chart:", error));
    });
});



document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("upload-form");
    const uploadFeedback = document.getElementById("upload-feedback");
    const chartContainer = document.getElementById("chart-container");
    const generateChartBtn = document.getElementById("generate-chart-btn");
    const downloadBtn = document.getElementById("download-btn");

    uploadForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);

        fetch("/", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadFeedback.textContent = "File uploaded successfully!";
                uploadFeedback.style.color = "green";
                populateAxisOptions(data.columns);
            } else {
                uploadFeedback.textContent = "Upload failed. Please try a valid file.";
                uploadFeedback.style.color = "red";
            }
        })
        .catch(error => {
            console.error("Upload error:", error);
            uploadFeedback.textContent = "An error occurred. Please try again.";
            uploadFeedback.style.color = "red";
        });
    });

    function populateAxisOptions(columns) {
        const xAxis = document.getElementById("x-axis");
        const yAxis = document.getElementById("y-axis");
        xAxis.innerHTML = yAxis.innerHTML = "";

        columns.forEach(column => {
            xAxis.innerHTML += `<option value="${column}">${column}</option>`;
            yAxis.innerHTML += `<option value="${column}">${column}</option>`;
        });
    }

    generateChartBtn.addEventListener("click", function () {
        const chartType = document.getElementById("chart-type").value;
        const xColumn = document.getElementById("x-axis").value;
        const yColumn = document.getElementById("y-axis").value;

        const formData = new FormData();
        formData.append("chart_type", chartType);
        formData.append("x_column", xColumn);
        formData.append("y_column", yColumn);

        fetch("/generate_chart", {
            method: "POST",
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            chartContainer.innerHTML = html;
            downloadBtn.style.display = "block";
        })
        .catch(error => console.error("Chart generation error:", error));
    });
});
