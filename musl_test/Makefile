all: hello hello-static

MUSL_DIR=$(PWD)/musl/
MUSL_INSTALL_DIR=$(MUSL_DIR)/musl-kml
MUSL_GCC=$(MUSL_INSTALL_DIR)/bin/musl-gcc

hello: libc.so hello.c
	$(MUSL_GCC) hello.c -o hello

hello-static: libc.so hello.c
	$(MUSL_GCC) -static hello.c -o hello-static

.PHONY: always
libc.so: always
ifneq ($(shell test -e $(MUSL_GCC) && echo -n yes),yes)
	make -C ../ musl-kml
endif
ifneq ($(shell test -e ./libc.so && echo -n yes),yes)
	cp $(MUSL_DIR)/lib/libc.so ./
endif

docker: Dockerfile hello libc.so
	docker build -t musl_test .

image: docker
	(cd .. && scripts/image2rootfs.sh musl_test latest ext2)

clean:
	rm -f hello libc.so
