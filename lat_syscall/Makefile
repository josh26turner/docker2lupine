all: lat_syscall lat_syscall-static

MUSL_GCC=../../musl/musl-kml/bin/musl-gcc #TODO: setup musl submodule

lat_syscall-static: lat_syscall.c Makefile
	$(MUSL_GCC) -g -o $@ -static lat_syscall.c lib_timing.c

lat_syscall: lat_syscall.c Makefile
	$(MUSL_GCC) -o $@ lat_syscall.c lib_timing.c

docker: Dockerfile lat_syscall lat_syscall-static
	docker build -t lat_syscall .

image: docker
	(cd .. && ./my-scripts/build/image2rootfs.sh lat_syscall latest ext2)

clean:
	rm -f lat_syscall lat_syscall-static
