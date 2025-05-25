# Microcontrollers

Various projects for ESP32 microcontrollers using MicroPython.

## Project setup

**Note:** The Makefile in this repository requires Docker to execute commands.

Build the Docker image:
```bash
make build-image
```

## Prepare ESP32 microcontroller for MicroPython

Download the latest MicroPython firmware from the [MicroPython download page](https://micropython.org/download/ESP32_GENERIC/). Use the normal firmware as .bin file.

Put the file into the root of this repository and name it `ESP32_GENERIC.bin` (i.e. remove the date and version suffix from the filename).

Write the MicroPython firmware to the ESP32 microcontroller:
```bash
make flash
```

## Copy project files to ESP32 microcontroller

Sync and reboot the microcontroller (replace `{PROJECT_NAME}` with the directory of the project):
```bash
make -O PROJECT={PROJECT_NAME}
```
