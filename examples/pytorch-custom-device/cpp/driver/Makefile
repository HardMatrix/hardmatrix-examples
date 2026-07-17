MODULE := tensor
KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

obj-m += $(MODULE).o
$(MODULE)-y := src/hal.o

.PHONY: all check clean load unload logs

all: check
	$(MAKE) -C $(KDIR) M=$(PWD) modules

check:
	@test -d "$(KDIR)" || { \
		echo "Kernel headers not found at $(KDIR)"; \
		echo "Install headers for kernel $(shell uname -r)"; \
		exit 1; \
	}

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

load: all
	sudo insmod $(MODULE).ko mock=1 debug=1 device_mode=0666

unload:
	-sudo rmmod $(MODULE)

logs:
	dmesg | tail -n 200
