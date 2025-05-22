# Microcontrollers

Various projects for ESP32 microcontrollers using MicroPython.

## Project setup

**Note:** This project requires [uv](https://github.com/astral-sh/uv) to manage the Python environment!

Simply execute `uv sync` in the root of this repository. This will automatically setup a virtual environment and download all required Python dependencies.

## Prepare ESP32 microcontroller for MicroPython

Download the latest MicroPython firmware from the [MicroPython download page](https://micropython.org/download/ESP32_GENERIC/). Use the normal firmware as .bin file.

Erase the flash of the ESP32 microcontroller:
```bash
.venv/bin/esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
```

Flash the MicroPython firmware to the ESP32 microcontroller (replace the path to the downloaded .bin file):
```bash
.venv/bin/esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 /path/to/downloaded/ESP32_GENERIC-{DATE}-{VERSION}.bin
```

## Copy project files to ESP32 microcontroller

Sync and reboot the microcontroller (replace `{PROJECT_NAME}` with the directory of the project):
```bash
make -O PROJECT={PROJECT_NAME}
```
