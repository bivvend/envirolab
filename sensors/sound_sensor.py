
"""
Enviro+ microphone.

Measures relative sound amplitude using the microphone
and ADC.

The result is an ADC amplitude, not calibrated decibels.
"""

import random
import time
import config


# Initialise real hardware only when needed
if not config.MOCK_SENSORS:
    from enviroplus.noise import Noise
    microphone = Noise()


def read():
    """Measure relative sound amplitude."""

    if config.MOCK_SENSORS:
        # Simulate a changing sound level
        sound = random.randint(50, 500)

    else:
        # Collect microphone samples over a short period
        samples = microphone.get_noise_profile()

        sound = max(samples) - min(samples)

    return {
        "sound": round(float(sound), 2),
    }


# Test the module directly
if __name__ == "__main__":
    print("Microphone Test")
    print("Mock mode:", config.MOCK_SENSORS)

    for i in range(5):
        print(read())
        time.sleep(0.5)
