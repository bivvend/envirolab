
"""
LTR559 light and proximity sensor.

Measures:
    - Ambient light (lux)
    - Proximity (relative, unitless value)
"""

import random
import config


# Initialise real hardware only when needed
if not config.MOCK_SENSORS:
    import ltr559


def read():
    """Return light and proximity measurements."""

    if config.MOCK_SENSORS:
        # Simulated readings for desktop testing
        light = 350 + random.uniform(-20, 20)
        proximity = random.randint(0, 10)

    else:
        # Read the real LTR559 sensor
        light = ltr559.get_lux()
        proximity = ltr559.get_proximity()

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
