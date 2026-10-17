
"""
LTR559 light and proximity sensor.

Measures:
    - Ambient light (lux)
    - Proximity (relative, unitless value)
"""

import random
import config
import time

# Initialise real hardware only when needed
if not config.MOCK_SENSORS:
    from ltr559 import LTR559
    sensor = LTR559()
    time.sleep(0.5)
def read():
    """Return light and proximity measurements."""

    if config.MOCK_SENSORS:
        # Simulated readings for desktop testing
        light = 350 + random.uniform(-20, 20)
        proximity = random.randint(0, 10)

    else:
        # Read the real LTR559 sensor
        light = sensor.get_lux()
        proximity = sensor.get_proximity()

    return {
        "light": round(light, 2),
        "proximity": proximity,
    }


# Test the module directly
if __name__ == "__main__":
    print("LTR559 Light Sensor Test")
    print("Mock mode:", config.MOCK_SENSORS)

    for i in range(5):
        print(read())
        time.sleep(0.5)
