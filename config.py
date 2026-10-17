
from pathlib import Path

# Project settings
PROJECT_NAME = "EnviroLab"
MOCK_SENSORS = True

# Sensor settings
SAMPLE_INTERVAL = 5.0       # Seconds between readings
GAS_WARMUP = 60             # Initial gas sensor warm-up (seconds)

# Enable or disable measurements
SENSORS = {
    "temperature": True,
    "humidity": True,
    "pressure": True,
    "gas_reducing": True,
    "gas_oxidising": True,
    "gas_nh3": True,
    "light": False,
    "proximity": False,
    "sound": False,
}

# Web server settings
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
HISTORY_SIZE = 360          # Number of readings retained

# Data recording
DATA_DIRECTORY = Path(__file__).resolve().parent / "data"

# LCD settings
LCD_ENABLED = True
LCD_UPDATE_INTERVAL = 2.0
