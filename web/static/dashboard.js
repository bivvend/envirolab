
/*
EnviroLab dashboard.

Fetches measurements from Flask and displays
live sensor readings and graphs.
*/

let chart = null;
let selectedSensor = null;

// Labels and units for each measurement
const sensorLabels = {
    temperature: ["Temperature", "°C"],
    humidity: ["Humidity", "%"],
    pressure: ["Pressure", "hPa"],
    gas_reducing: ["Reducing gas resistance", "Ω"],
    gas_oxidising: ["Oxidising gas resistance", "Ω"],
    gas_nh3: ["NH3 gas resistance", "Ω"],
    light: ["Light", "lux"],
    proximity: ["Proximity", "relative"],
    sound: ["Sound amplitude", "relative"]
};


function getLabel(name) {
    return sensorLabels[name] || [name, ""];
}


function updateTable(data) {
    const table = document.getElementById("readings");
    table.innerHTML = "";

    for (const [name, value] of Object.entries(data)) {
        if (name === "timestamp") continue;

        const [label, unit] = getLabel(name);
        const row = table.insertRow();

        row.insertCell(0).textContent = label;
        row.insertCell(1).textContent = `${value} ${unit}`;
    }
}


function updateSensorSelector(data) {
    const selector = document.getElementById("sensorSelect");

    const names = Object.keys(data).filter(
        name => name !== "timestamp"
    );

    // Rebuild the selector only if sensors have changed
    const existing = Array.from(selector.options).map(
        option => option.value
    );

    if (JSON.stringify(names) === JSON.stringify(existing)) {
        return;
    }

    selector.innerHTML = "";

    for (const name of names) {
        const option = document.createElement("option");

        option.value = name;
        option.textContent = getLabel(name)[0];

        selector.appendChild(option);
    }

    if (names.includes(selectedSensor)) {
        selector.value = selectedSensor;
    } else {
        selectedSensor = names[0] || null;
        selector.value = selectedSensor || "";
    }
}


function createChart() {
    const canvas = document.getElementById("sensorChart");

    chart = new Chart(canvas, {
        type: "line",

        data: {
            labels: [],
            datasets: [{
                label: "Sensor reading",
                data: [],
                borderColor: "#247a58",
                backgroundColor: "#247a5820",
                borderWidth: 2,
                pointRadius: 1,
                tension: 0.2
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,

            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Time"
                    }
                },

                y: {
                    title: {
                        display: true,
                        text: "Measurement"
                    }
                }
            }
        }
    });
}


function updateChart(history) {
    if (!chart || !selectedSensor) return;

    const readings = history.filter(
        item => item[selectedSensor] !== undefined
    );

    const [label, unit] = getLabel(selectedSensor);

    chart.data.labels = readings.map(
        item => item.timestamp.split("T").pop()
    );

    chart.data.datasets[0].data = readings.map(
        item => item[selectedSensor]
    );

    chart.data.datasets[0].label = label;

    chart.options.scales.y.title.text =
        unit ? `${label} (${unit})` : label;

    chart.update();
}


async function updateDashboard() {
    try {
        const [readingsResponse, historyResponse] =
            await Promise.all([
                fetch("/api/readings"),
                fetch("/api/history")
            ]);

        if (!readingsResponse.ok || !historyResponse.ok) {
            throw new Error("Unable to fetch sensor data");
        }

        const readings = await readingsResponse.json();
        const history = await historyResponse.json();

        updateTable(readings);
        updateSensorSelector(readings);
        updateChart(history);

    } catch (error) {
        console.error("Dashboard update failed:", error);
    }
}


// Start dashboard
document.addEventListener("DOMContentLoaded", () => {
    createChart();

    document.getElementById("sensorSelect")
    .addEventListener("change", async event => {
        selectedSensor = event.target.value;

        await fetch("/api/display", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sensor: selectedSensor
            })
        });

        updateDashboard();
    });

    updateDashboard();
    setInterval(updateDashboard, 2000);
});


async function updateRecordingStatus() {
    const response = await fetch("/api/record/status");
    const status = await response.json();

    const indicator = document.getElementById("recordingStatus");

    indicator.textContent = status.recording
        ? "● Recording"
        : "Not recording";

    indicator.style.color = status.recording
        ? "#c62828"
        : "#555";

    document.getElementById("startButton").disabled =
        status.recording;

    document.getElementById("stopButton").disabled =
        !status.recording;

    document.getElementById("downloadButton").disabled =
        status.recording || !status.filename;

    document.getElementById("recordingFilename").textContent =
        status.filename ? `File: ${status.filename}` : "";
}


async function startRecording() {
    const response = await fetch("/api/record/start", {
        method: "POST"
    });

    if (!response.ok) {
        const result = await response.json();
        alert(result.error);
    }

    await updateRecordingStatus();
    await updateDashboard();
}


async function stopRecording() {
    const response = await fetch("/api/record/stop", {
        method: "POST"
    });

    if (!response.ok) {
        const result = await response.json();
        alert(result.error);
    }

    await updateRecordingStatus();
}


function downloadRecording() {
    window.location.href = "/api/record/download";
}


// Connect buttons once the page has loaded
document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("startButton")
        .addEventListener("click", startRecording);

    document.getElementById("stopButton")
        .addEventListener("click", stopRecording);

    document.getElementById("downloadButton")
        .addEventListener("click", downloadRecording);

    updateRecordingStatus();

    setInterval(updateRecordingStatus, 2000);
});

