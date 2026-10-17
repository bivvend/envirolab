
"""
EnviroLab - Main application.

Collects sensor readings and runs the web dashboard.
"""

import time
import threading
from collections import deque

import config
from sensors import manager
from logging_data import recorder


latest_readings = {}
history = deque(maxlen=config.HISTORY_SIZE)

def clear_history():
    """Clear previous measurements from the live graph."""
    history.clear()

def collect():
    """Collect one set of sensor measurements."""

    global latest_readings

    readings = manager.read()

    latest_readings = readings
    history.append(readings)

    if recorder.is_recording():
        recorder.record(readings)

    return readings


def sensor_loop():
    """Continuously collect sensor measurements."""

    while True:
        readings = collect()
        print(readings)

        time.sleep(config.SAMPLE_INTERVAL)


def run():
    """Start the sensors and web server."""

    from web.server import app

    from web import server

    server.get_readings = lambda: latest_readings
    server.get_history = lambda: list(history)
    server.clear_history = clear_history

    print(f"Starting {config.PROJECT_NAME}")
    print(f"Mock sensors: {config.MOCK_SENSORS}")

    # Start sensor collection in the background
    thread = threading.Thread(
        target=sensor_loop,
        daemon=True
    )
    thread.start()

    # Run the web server
    try:
        server.app.run(
            host=config.WEB_HOST,
            port=config.WEB_PORT,
            debug=False,
            use_reloader=False
        )
    finally:
        recorder.stop()


if __name__ == "__main__":
    run()
