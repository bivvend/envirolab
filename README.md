# EnviroLab

**EnviroLab** is a small, standalone environmental monitoring station for classroom experiments, built using a **Raspberry Pi Zero 2 W** and a **Pimoroni Enviro+** board.

Students connect directly to the Pi's Wi-Fi network and use a browser to view live measurements, plot graphs, select the measurement shown on the Enviro+ LCD, and record data to CSV. **No internet connection or special software is required on student laptops.**

## Features

- Live temperature, humidity and air-pressure readings
- Gas sensor resistance readings (reducing, oxidising and NH₃ channels)
- Light, proximity and relative sound measurements
- Live graph with selectable measurement
- Enviro+ LCD showing the measurement selected on the dashboard
- Start/stop CSV recording and download results
- Local Flask dashboard, with Chart.js stored locally for offline use
- Standalone `EnviroLab` Wi-Fi hotspot
- Automatic application startup via `systemd`
- Mock sensor mode for development on Windows without a Pi

> **Measurement notes:** Gas readings are raw sensor resistance values, not calibrated pollutant concentrations. Sound is a relative level, not calibrated decibels. This project does **not** require a PMS5003 particulate sensor.

## Hardware

- Raspberry Pi Zero 2 W
- Pimoroni Enviro+ HAT (connected via the 40-pin header or ribbon cable)
- microSD card with Raspberry Pi OS Lite (32-bit)
- Suitable USB power supply

Tested during development with Raspberry Pi OS Lite based on Debian 13 (Trixie).

## Quick start: using an already configured EnviroLab

1. Power the Raspberry Pi.
2. On a laptop, connect to the Wi-Fi network **`EnviroLab`** using the configured password.
3. Open **http://10.42.0.1:5000** in a browser.
4. Select a measurement to view its live graph and update the LCD.
5. Use the recording controls to start, stop and download a CSV file.

Windows may say **“No internet, secured”** when connected to the hotspot. This is expected: EnviroLab is a local network.

## Installation on a new Raspberry Pi

These are the main steps. See **`EnviroLab_Setup_Guide.docx`** if it is included in the repository for the full, tested installation procedure and troubleshooting notes.

### 1. Install Raspberry Pi OS

Flash Raspberry Pi OS Lite (32-bit) with Raspberry Pi Imager. Set a username, enable SSH and configure your initial Wi-Fi network.

Connect using SSH (assuming hostname `envirolab` and username `pi`):

```bash
ssh pi@envirolab.local
```

Update the system:

```bash
sudo apt update
sudo apt full-upgrade -y
```

### 2. Install Pimoroni's Enviro+ libraries

```bash
sudo apt install -y git python3-venv \
    libopenblas0-pthread libopenjp2-7 libfreetype6 fonts-dejavu-core

cd ~
git clone https://github.com/pimoroni/enviroplus-python.git
cd enviroplus-python
./install.sh
```

The setup described here uses Pimoroni's Python environment at:

```text
/home/pi/.virtualenvs/pimoroni
```

Enable **I²C** and **SPI** in `sudo raspi-config` if they are not already enabled.

### 3. Configure SPI for the Enviro+ LCD

Edit `/boot/firmware/config.txt`:

```bash
sudo nano /boot/firmware/config.txt
```

Comment out `dtparam=spi=on` if present and add:

```ini
#dtparam=spi=on
dtoverlay=spi0-2cs,no_miso
```

Reboot. This configuration allows the LCD to use SPI chip-select 1 and GPIO9 for D/C.

### 4. Clone EnviroLab

```bash
cd ~
git clone <THIS_REPOSITORY_URL> envirolab
cd envirolab
```

If a `requirements.txt` is included, install its dependencies into the Pimoroni environment:

```bash
~/.virtualenvs/pimoroni/bin/python -m pip install -r requirements.txt
```

Check `config.py`:

```python
MOCK_SENSORS = False
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
LCD_ENABLED = True
```

The working LCD orientation is **270°**. Set this in `display/lcd.py`, or through `LCD_ROTATION` if your version exposes that setting in `config.py`.

Run manually to test:

```bash
cd ~/envirolab
~/.virtualenvs/pimoroni/bin/python main.py
```

The dashboard is available on port **5000** at the Pi's current network address.

### 5. Start EnviroLab automatically

Create `/etc/systemd/system/envirolab.service`:

```ini
[Unit]
Description=EnviroLab Environmental Monitoring
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/envirolab
ExecStart=/home/pi/.virtualenvs/pimoroni/bin/python /home/pi/envirolab/main.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now envirolab.service
sudo systemctl status envirolab.service
```

### 6. Create the standalone Wi-Fi hotspot

The following uses NetworkManager, as provided with Raspberry Pi OS Trixie:

```bash
sudo nmcli connection add type wifi ifname wlan0 \
    con-name EnviroLab ssid EnviroLab

sudo nmcli connection modify EnviroLab \
    802-11-wireless.mode ap \
    802-11-wireless.band bg \
    ipv4.method shared \
    ipv4.addresses 10.42.0.1/24 \
    ipv6.method disabled

sudo nmcli connection modify EnviroLab \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "REPLACE_WITH_A_STRONG_PASSWORD"

sudo nmcli connection modify EnviroLab \
    connection.autoconnect yes \
    connection.autoconnect-priority 100
```

**Warning:** Activating the hotspot will disconnect an SSH session using the Pi's previous Wi-Fi connection. Have a recovery method available.

```bash
sudo nmcli connection up EnviroLab
```

Connect a laptop to the `EnviroLab` network and open **http://10.42.0.1:5000**.

## Project structure

```text
envirolab/
├── main.py                 # Sensor polling and application startup
├── config.py               # Settings and enabled sensors
├── requirements.txt
├── sensors/
│   ├── manager.py
│   ├── bme280_sensor.py
│   ├── gas_sensor.py
│   ├── light_sensor.py
│   └── sound_sensor.py
├── logging_data/
│   └── recorder.py         # CSV recording
├── display/
│   └── lcd.py              # Enviro+ LCD
├── web/
│   ├── server.py           # Flask routes and API
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── dashboard.js
│       ├── chart.umd.js
│       └── style.css
├── data/                   # CSV recordings
└── tests/
```

## Configuration

Settings are defined in `config.py`.

| Setting | Purpose |
| --- | --- |
| `MOCK_SENSORS` | `True` for simulated measurements during desktop development |
| `SAMPLE_INTERVAL` | Seconds between sensor readings |
| `SENSORS` | Dictionary enabling/disabling individual measurements |
| `GAS_WARMUP` | Gas sensor warm-up setting |
| `WEB_HOST`, `WEB_PORT` | Dashboard listening address and port |
| `HISTORY_SIZE` | Number of recent readings retained for the live graph |
| `DATA_DIRECTORY` | Location of saved CSV recordings |
| `LCD_ENABLED` | Enable or disable the physical display |

For local Windows development, use `MOCK_SENSORS = True` and install the project's web/Python dependencies in a desktop environment. Hardware-specific Pimoroni imports are skipped in mock mode.

## Recording and data

The dashboard can start and stop CSV recordings and download the recorded file. Data is stored in the `data/` directory on the Pi. CSV files include timestamps and enabled measurements.

The live graph shows recent history; it is not a replacement for saved CSV recordings.

## Maintenance and troubleshooting

Check service status:

```bash
sudo systemctl status envirolab.service
journalctl -u envirolab.service -n 50 --no-pager
```

Check hotspot status:

```bash
nmcli device status
nmcli connection show --active
```

Update the application after pulling new code:

```bash
cd ~/envirolab
git pull
sudo systemctl restart envirolab.service
```

If the LCD is blank, check `/dev/spidev0.1`, the SPI overlay and the display pin settings. If light/proximity initially returns zero, the LTR559 sensor may need a short settling delay after initialisation.

## Classroom use and safety

EnviroLab is an **educational** measurement system, not a certified air-quality, gas-safety or sound-level monitor. Do not use it to make safety-critical decisions. Keep the hotspot password private, and do not expose the Flask development server to the public internet.

## Licence

**To be decided.** Add a `LICENSE` file before publishing if you want to specify how others may use, modify or redistribute the project.
