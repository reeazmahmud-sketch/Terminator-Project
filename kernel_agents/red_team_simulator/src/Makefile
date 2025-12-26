obj-m += dk_hider.o

PWD := $(CURDIR)

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

# Test Command
# Loads the module to hide process '1234'
test:
	sudo insmod dk_hider.ko target_pid="1234"
	ls /proc/ | grep 1234 || echo "Process 1234 Hidden!"
	sudo rmmod dk_hider
