
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

selected_sensor = "temperature"
latest_readings = {}
history = deque(maxlen=config.HISTORY_SIZE)

def set_selected_sensor(name):
    """Change the measurement shown on the LCD."""
    global selected_sensor

    if name in config.SENSORS and config.SENSORS[name]:
        selected_sensor = name
        return True

    return False


def get_selected_sensor():
    return selected_sensor

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

    if config.LCD_ENABLED and not config.MOCK_SENSORS:
        from display import lcd

        value = readings.get(selected_sensor)

        if value is not None:
            lcd.show(selected_sensor, value)

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
    #Connect functions
    server.get_readings = lambda: latest_readings
    server.get_history = lambda: list(history)
    server.clear_history = clear_history
    server.set_selected_sensor = set_selected_sensor
    server.get_selected_sensor = get_selected_sensor

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
