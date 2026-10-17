
"""
CSV data recorder for EnviroLab.

Thread-safe recording of environmental measurements.
"""

import csv
import threading
from datetime import datetime

import config


# Recording state
file = None
writer = None
filename = None

# Prevent simultaneous access to the recorder
lock = threading.Lock()


def start(sensor_names):
    """Start a new CSV recording."""

    global file, writer, filename

    with lock:
        if file is not None:
            raise RuntimeError("A recording is already running")

        config.DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        new_filename = (
            config.DATA_DIRECTORY / f"experiment_{timestamp}.csv"
        )

        new_file = open(
            new_filename, "w", newline="", encoding="utf-8"
        )

        try:
            new_writer = csv.DictWriter(
                new_file,
                fieldnames=["timestamp"] + list(sensor_names)
            )
            new_writer.writeheader()
            new_file.flush()

        except Exception:
            new_file.close()
            raise

        file = new_file
        writer = new_writer
        filename = new_filename

        return filename


def record(readings):
    """Write one set of readings to the CSV file."""

    with lock:
        if file is None:
            return

        writer.writerow(readings)
        file.flush()


def stop():
    """Stop recording and close the CSV file."""

    global file, writer

    with lock:
        if file is not None:
            file.close()
            file = None
            writer = None

        return filename


def is_recording():
    """Return True if recording is active."""

    with lock:
        return file is not None


def get_status():
    """Return recording state and current filename."""

    with lock:
        return {
            "recording": file is not None,
            "filename": filename.name if filename else None
        }


# Test the recorder directly
if __name__ == "__main__":
    import time
    from sensors import manager

    print("EnviroLab Recorder Test")

    readings = manager.read()
    sensor_names = [
        name for name in readings if name != "timestamp"
    ]

    path = start(sensor_names)
    print("Recording to:", path)

    try:
        for i in range(5):
            record(readings)
            print("Recorded:", readings)

            time.sleep(config.SAMPLE_INTERVAL)
            readings = manager.read()

    finally:
        stop()
        print("Recording stopped.")
