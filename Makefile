PORT := /dev/ttyUSB0
RSHELL := .venv/bin/rshell

all: sync reboot

sync: .require-PROJECT
	$(RSHELL) --port $(PORT) rsync --mirror ./$(PROJECT) /pyboard

reboot:
	$(RSHELL) --port $(PORT) repl "~ import machine ~ machine.reset()~"

.require-%:
	@ if [ "${${*}}" = "" ]; then echo "Environment variable $* not set"; exit 1; fi
