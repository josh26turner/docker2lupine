all: reseed

reseed: reseed.c Makefile
	../musl/musl-kml/bin/musl-gcc -mrdrnd -static -o $@ $<

install: reseed
	cp reseed ../my-scripts/guest/reseed

clean:
	rm -f reseed
