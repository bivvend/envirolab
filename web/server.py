
from flask import Flask, jsonify, render_template
from flask import send_file
from flask import request
from logging_data import recorder

app = Flask(__name__)

# Function supplied by main.py
get_readings = lambda: {}
get_history = lambda: []
clear_history = lambda: None
set_selected_sensor = lambda name: False
get_selected_sensor = lambda: "temperature"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/display", methods=["GET", "POST"])
def display_selection():
    """Get or change the measurement shown on the LCD."""

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("sensor")

        if not set_selected_sensor(name):
            return jsonify({"error": "Invalid sensor"}), 400

    return jsonify({
        "sensor": get_selected_sensor()
    })


@app.route("/api/readings")
def readings():
    return jsonify(get_readings())


@app.route("/api/history")
def history():
    return jsonify(get_history())



@app.route("/api/record/start", methods=["POST"])
def start_recording():
    """Start a new experiment with an empty graph."""

    if recorder.is_recording():
        return jsonify({"error": "Already recording"}), 400

    readings = get_readings()

    if not readings:
        return jsonify({"error": "No sensor readings available"}), 400

    sensor_names = [
        name for name in readings
        if name != "timestamp"
    ]

    filename = recorder.start(sensor_names)

    # Clear previous graph data
    clear_history()

    return jsonify({
        "recording": True,
        "filename": filename.name
    })


@app.route("/api/record/stop", methods=["POST"])
def stop_recording():
    """Stop the current recording."""

    filename = recorder.stop()

    return jsonify({
        "recording": False,
        "filename": filename.name if filename else None
    })


@app.route("/api/record/status")
def recording_status():
    return jsonify(recorder.get_status())


@app.route("/api/record/download")
def download_recording():
    """Download the most recent CSV recording."""

    filename = recorder.filename

    if filename is None or not filename.exists():
        return jsonify({"error": "No recording available"}), 404

    if recorder.is_recording():
        return jsonify({"error": "Stop recording before downloading"}), 400

    return send_file(filename, as_attachment=True)
