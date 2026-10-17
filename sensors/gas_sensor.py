
"""
MICS6814 gas sensor on the Enviro+ board.

Measures resistance changes associated with:
    - Reducing gases
    - Oxidising gases
    - NH3-related gases

Readings are in ohms, not ppm.
"""

import random
import config


# Initialise real hardware only when needed
if not config.MOCK_SENSORS:
    from enviroplus import gas


def read():
    """Return the three gas sensor resistance readings."""

    if config.MOCK_SENSORS:
        # Simulated resistance readings for desktop testing
        reducing = 100000 + random.uniform(-5000, 5000)
        oxidising = 30000 + random.uniform(-1500, 1500)
        nh3 = 70000 + random.uniform(-3500, 3500)

    else:
        # Read the real MICS6814 sensor
        readings = gas.read_all()

        reducing = readings.reducing
        oxidising = readings.oxidising
        nh3 = readings.nh3

    return {
        "gas_reducing": round(reducing, 2),
        "gas_oxidising": round(oxidising, 2),
        "gas_nh3": round(nh3, 2),
    }


# Test the module directly
if __name__ == "__main__":
    print("MICS6814 Gas Sensor Test")
    print("Mock mode:", config.MOCK_SENSORS)

    for i in range(5):
        print(read())
