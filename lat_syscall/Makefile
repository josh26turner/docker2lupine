all: lat_syscall lat_syscall-static

MUSL_DIR=../musl/musl-kml/
MUSL_GCC=$(MUSL_DIR)/bin/musl-gcc

libc:
ifneq ($(shell test -e $(MUSL_GCC) && echo -n yes),yes)
	make -C ../ musl-kml
endif
ifneq ($(shell test -e ./libc.so && echo -n yes),yes)
	cp $(MUSL_DIR)/lib/libc.so ./
endif

lat_syscall-static: libc lat_syscall.c Makefile
	$(MUSL_GCC) -g -o $@ -static lat_syscall.c lib_timing.c

lat_syscall: libc lat_syscall.c Makefile
	$(MUSL_GCC) -o $@ lat_syscall.c lib_timing.c

docker: Dockerfile lat_syscall lat_syscall-static
	docker build -t lat_syscall .

image: docker
	(cd .. && ./my-scripts/build/image2rootfs.sh lat_syscall latest ext2)

clean:
	rm -f lat_syscall lat_syscall-static
