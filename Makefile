PORT := /dev/ttyUSB0
FLASH_BIN := ESP32_GENERIC.bin
DOCKER_WORKDIR=/workdir
DOCKER_IMAGE := programie/esp32-tools
DOCKER_RUN_CMD := docker run --rm --device $(PORT) -v $(PWD):$(DOCKER_WORKDIR):ro $(DOCKER_IMAGE)
RSHELL := $(DOCKER_RUN_CMD) rshell --port $(PORT)
ESPTOOL := $(DOCKER_RUN_CMD) esptool.py --port $(PORT)

all: sync reboot

build-image:
	docker build -t $(DOCKER_IMAGE) .

sync: .require-env-PROJECT
	$(RSHELL) rsync --mirror $(DOCKER_WORKDIR)/$(PROJECT) /pyboard

reboot:
	$(RSHELL) repl "~ import machine ~ machine.reset()~"

flash: .require-file-$(FLASH_BIN)
	$(ESPTOOL) erase_flash
	$(ESPTOOL) --baud 460800 write_flash -z 0x1000 $(DOCKER_WORKDIR)/$(FLASH_BIN)

.require-env-%:
	@ if [ -z "${$*}" ]; then echo "Environment variable $* not set"; exit 1; fi

.require-file-%:
	@set -- $*; \
	if [ "$$1" = "$*" ] && [ ! -e "$$1" ]; then \
		echo "File matching '$*' not found"; \
		exit 1; \
	fi
