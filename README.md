# Microcontrollers

Various projects for ESP32 microcontrollers using MicroPython.

## Project setup

**Note:** Helper script in this repository requires Docker to execute commands.

Build the Docker image:
```bash
./helper.py build-image
```

## Prepare ESP32 microcontroller for MicroPython

Download the latest MicroPython firmware from the [MicroPython download page](https://micropython.org/download/ESP32_GENERIC/). Use the normal firmware as .bin file.

Write the MicroPython firmware to the ESP32 microcontroller:
```bash
./helper.py flash /path/to/downloaded/ESP32_GENERIC.bin
```

## Create a new project

Create a new project folder and symlink the shared files (replace `{PROJECT_NAME}` with the directory name of the project):
```bash
./helper.py create-project {PROJECT_NAME}
```

## Copy project files to ESP32 microcontroller

Sync and reboot the microcontroller (replace `{PROJECT_NAME}` with the directory name of the project):
```bash
./helper.py sync {PROJECT_NAME}
./helper.py reboot
```
