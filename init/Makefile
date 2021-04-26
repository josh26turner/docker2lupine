MUSL_DIR=../musl/musl-kml/
MUSL_GCC=$(MUSL_DIR)/bin/musl-gcc

all: init

libc:
ifneq ($(shell test -e $(MUSL_GCC) && echo -n yes),yes)
	make -C ../ musl-kml
endif

init: libc
	@mkdir -p $(out)
	$(MUSL_GCC) -g -o $(out)/init -mrdrnd -static init.c reseed.c socket_client.c
