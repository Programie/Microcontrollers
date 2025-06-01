#! /usr/bin/env python3

import argparse
import subprocess
import sys
import typing

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type

DEFAULT_PORT = "/dev/ttyUSB0"
DOCKER_IMAGE = "programie/esp32-tools"


def docker_run(command: list[str], device: Path | None = None, volumes: list[tuple[str, str, str]] | None = None):
    docker_command = ["docker", "run", "--rm", "-it"]

    if device:
        docker_command.append("--device")
        docker_command.append(str(device))

    if volumes:
        for volume in volumes:
            docker_command.append("-v")
            docker_command.append(":".join(volume))

    docker_command.append(DOCKER_IMAGE)

    subprocess.check_call(docker_command + command)


def execute_esptool(port: Path, arguments: list[str], volumes: list[tuple[str, str, str]] | None = None):
    docker_run(device=port, command=["esptool.py", "--port", port] + arguments, volumes=volumes)


def execute_rshell(port: Path, arguments: list[str], volumes: list[tuple[str, str, str]] | None = None):
    docker_run(device=port, command=["rshell", "--port", str(port)] + arguments, volumes=volumes)


class Action(ABC):
    def __init__(self, arg_subparser):
        self.arg_subparser = arg_subparser

    def create_subcommand(self, name: str, help: str, **kwargs):
        parser = self.arg_subparser.add_parser(name=name, help=help, **kwargs)

        parser.set_defaults(__callback__=self.run)

        return parser

    @abstractmethod
    def add_subcommand(self) -> None: pass

    @abstractmethod
    def run(self, *_: typing.Any) -> int: pass


class BuildImage(Action):
    def add_subcommand(self):
        self.create_subcommand("build-image", "build the esp32-tools Docker image")

    def run(self):
        subprocess.check_call(["docker", "build", "-t", DOCKER_IMAGE, Path(__file__).parent])


class FlashFirmware(Action):
    def add_subcommand(self):
        parser = self.create_subcommand("flash", "flash the ESP32 firmware to the connected microcontroller")
        parser.add_argument("firmware_file", help="path to the downloaded firmware file", type=Path)
        parser.add_argument("--port", help="path to the microcontroller port", type=Path, default=DEFAULT_PORT)

    def run(self, firmware_file: Path, port: Path):
        if not firmware_file.is_file():
            print(f"File not found: {firmware_file}", file=sys.stderr)
            return 1

        if not port.exists():
            print(f"Device not found: {port}", file=sys.stderr)
            return 1

        execute_esptool(port=port, arguments=["erase_flash"])
        execute_esptool(port=port, arguments=["--baud", "460800", "write_flash", "-z", "0x1000", "/esp32_firmware.bin"], volumes=[(str(firmware_file), "/esp32_firmware.bin", "ro")])

        return 0


class RebootMCU(Action):
    def add_subcommand(self):
        parser = self.create_subcommand("reboot", "reboot the connected microcontroller")
        parser.add_argument("--port", help="path to the microcontroller port", type=Path, default=DEFAULT_PORT)

    def run(self, port: Path):
        if not port.exists():
            print(f"Device not found: {port}", file=sys.stderr)
            return 1

        execute_rshell(port, ["repl", "~ import machine ~ machine.reset()~"])

        return 0

class Terminal(Action):
    def add_subcommand(self):
        parser = self.create_subcommand("terminal", "connect to serial console")
        parser.add_argument("--port", help="path to the microcontroller port", type=Path, default=DEFAULT_PORT)

    def run(self, port: Path):
        if not port.exists():
            print(f"Device not found: {port}", file=sys.stderr)
            return 1

        docker_run(["picocom", str(port), "-b", "115200"], device=port)

        return 0

class CreateProject(Action):
    def add_subcommand(self):
        parser = self.create_subcommand("create-project", "create a new project")
        parser.add_argument("project", help="name of the project")

    def run(self, project: str):
        project_path = Path(__file__).parent.joinpath(project)

        if project_path.is_dir():
            print(f"Project path already exists: {project_path}", file=sys.stderr)
            return 1

        project_path.mkdir()
        project_path.joinpath("common").symlink_to("../common")

        print(f"Project created: {project_path}")

        return 0


class SyncProject(Action):
    def add_subcommand(self):
        parser = self.create_subcommand("sync", "sync project files to the connected microcontroller")
        parser.add_argument("project", help="name of the project")
        parser.add_argument("--port", help="path to the microcontroller port", type=Path, default=DEFAULT_PORT)

    def run(self, project: str, port: Path):
        base_path = Path(__file__).parent
        common_path = base_path.joinpath("common")
        project_path = base_path.joinpath(project)

        if not project_path.is_dir():
            print(f"Project path not found: {project_path}", file=sys.stderr)
            return 1

        if not port.exists():
            print(f"Device not found: {port}", file=sys.stderr)
            return 1

        execute_rshell(port, ["rsync", "--mirror", "/project", "/pyboard"], volumes=[(str(project_path), "/project", "ro"), (str(common_path), "/project/common", "ro")])

        return 0


class Helper:
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser()
        arg_subparsers = self.arg_parser.add_subparsers(required=True)

        actions: list[Type[Action]] = [BuildImage, FlashFirmware, RebootMCU, Terminal, CreateProject, SyncProject]
        for action in actions:
            action(arg_subparser=arg_subparsers).add_subcommand()

    def run(self):
        arguments = vars(self.arg_parser.parse_args())
        callback = arguments["__callback__"]
        del arguments["__callback__"]

        return callback(**arguments)


if __name__ == "__main__":
    exit(Helper().run())
