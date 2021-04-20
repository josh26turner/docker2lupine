all: reseed

reseed: reseed.c Makefile
	../musl/musl-kml/bin/musl-gcc -mrdrnd -static -o $@ $<

install: reseed
	cp reseed $(out)

clean:
	rm -f reseed
