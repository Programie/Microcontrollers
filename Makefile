PORT := /dev/ttyUSB0
DOCKER_WORKDIR=/workdir
DOCKER_IMAGE := programie/esp32-tools
DOCKER_RUN_CMD := docker run --rm --device $(PORT) -v $(PWD):$(DOCKER_WORKDIR):ro $(DOCKER_IMAGE)
RSHELL := $(DOCKER_RUN_CMD) rshell --port $(PORT)

all: sync reboot

build-image:
	docker build -t $(DOCKER_IMAGE) .

sync: .require-PROJECT
	$(RSHELL) rsync --mirror $(DOCKER_WORKDIR)/$(PROJECT) /pyboard

reboot:
	$(RSHELL) repl "~ import machine ~ machine.reset()~"

.require-%:
	@ if [ "${${*}}" = "" ]; then echo "Environment variable $* not set"; exit 1; fi
