obj-m += ai_agent.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
	rm -rf keys/

# Security Target
sign: all
	chmod +x sign_module.sh
	./sign_module.sh ai_agent.ko

test:
	sudo dmesg -C
	# Try loading (will fail if Secure Boot enabled and not signed/enrolled)
	sudo insmod ai_agent.ko
	sudo dmesg