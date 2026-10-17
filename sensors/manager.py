
"""
Sensor manager for EnviroLab.

Collects measurements from the enabled sensors
and combines them into one dictionary.
"""

from datetime import datetime

import config


def read():
    """Read enabled sensors and return one dictionary."""

    readings = {
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

    # BME280: temperature, humidity, pressure
    if any(config.SENSORS[name] for name in
           ("temperature", "humidity", "pressure")):

        from sensors import bme280_sensor

        readings.update(bme280_sensor.read())

    # MICS6814: gas resistances
    if any(config.SENSORS[name] for name in
           ("gas_reducing", "gas_oxidising", "gas_nh3")):

        from sensors import gas_sensor

        readings.update(gas_sensor.read())

    # LTR559: light and proximity
    if config.SENSORS["light"] or config.SENSORS["proximity"]:

        from sensors import light_sensor

        readings.update(light_sensor.read())

    # Microphone: relative sound amplitude
    if config.SENSORS["sound"]:

        from sensors import sound_sensor

        readings.update(sound_sensor.read())

    # Remove measurements that are disabled
    readings = {
        name: value
        for name, value in readings.items()
        if name == "timestamp" or config.SENSORS.get(name, False)
    }

    return readings


# Test the sensor manager directly
if __name__ == "__main__":
    import time

    print("EnviroLab Sensor Manager")
    print("Mock mode:", config.MOCK_SENSORS)

    try:
        while True:
            readings = read()

            for name, value in readings.items():
                print(f"{name}: {value}")

            print("-" * 30)
            time.sleep(config.SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped.")
