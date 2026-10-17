
"""
EnviroLab LCD display.

Displays the currently selected measurement.
"""

import config


# Display labels and units
LABELS = {
    "temperature": ("Temperature", "C"),
    "humidity": ("Humidity", "%"),
    "pressure": ("Pressure", "hPa"),
    "gas_reducing": ("Reducing Gas", "Ohms"),
    "gas_oxidising": ("Oxidising Gas", "Ohms"),
    "gas_nh3": ("NH3 Gas", "Ohms"),
    "light": ("Light", "lux"),
    "proximity": ("Proximity", ""),
    "sound": ("Sound Level", "relative"),
}


if config.LCD_ENABLED and not config.MOCK_SENSORS:
    import ST7735
    from PIL import Image, ImageDraw, ImageFont

    display = ST7735.ST7735(
        port=0,
        cs=1,
        dc="GPIO9",
        backlight="GPIO12",
        rotation=config.LCD_ROTATION,
        spi_speed_hz=10000000
    )

    display.begin()

    WIDTH = display.width
    HEIGHT = display.height

    font = ImageFont.load_default()


def show(sensor_name, value):
    """Display a measurement on the LCD."""

    if not config.LCD_ENABLED or config.MOCK_SENSORS:
        return

    label, unit = LABELS.get(sensor_name, (sensor_name, ""))

    image = Image.new("RGB", (WIDTH, HEIGHT), (10, 25, 30))
    draw = ImageDraw.Draw(image)

    draw.text((10, 15), label, font=font, fill="white")

    if isinstance(value, (int, float)):
        value_text = f"{value:.2f}"
    else:
        value_text = str(value)

    draw.text((10, 55), value_text, font=font, fill="yellow")
    draw.text((10, 85), unit, font=font, fill="white")

    display.display(image)
