
"""
BME280 environmental sensor.

Measures temperature, humidity and atmospheric pressure.
Can use real hardware or simulated readings.
"""

import random
import config


# Initialise real hardware only when needed
if not config.MOCK_SENSORS:
    from smbus2 import SMBus
    from bme280 import BME280

    bus = SMBus(1)
    sensor = BME280(i2c_dev=bus)


def read():
    """Return temperature, humidity and pressure readings."""

    if config.MOCK_SENSORS:
        # Simulated readings for desktop development
        temperature = 22.0 + random.uniform(-0.5, 0.5)
        humidity = 50.0 + random.uniform(-2.0, 2.0)
        pressure = 1013.0 + random.uniform(-1.0, 1.0)

    else:
        # Real readings from the Enviro+ BME280
        temperature = sensor.get_temperature()
        humidity = sensor.get_humidity()
        pressure = sensor.get_pressure()

    return {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "pressure": round(pressure, 2),
    }


# Test the module directly
if __name__ == "__main__":
    print("BME280 Sensor Test")
    print("Mock mode:", config.MOCK_SENSORS)

    for i in range(5):
        print(read())
