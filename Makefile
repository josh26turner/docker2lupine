build-env-image:
	cd docker && \
		docker build . -t linuxbuild:latest -f build-env.Dockerfile

patch-linux:
	cd linux && \
		git apply ../kml_4.0_001.diff

unpatch-linux:
	pushd linux && \
	git reset --hard HEAD && \
	git clean -fd && \
	popd

patch-musl:
	pushd musl && \
	git apply ../musl_kml.patch | exit 0 && \
	popd

unpatch-musl:
	pushd musl && \
	git reset --hard HEAD && \
	git clean -fd && \
	popd

musl-kml: patch-musl
	pushd musl && \
	./configure --prefix=$(PWD)/musl/musl-kml && \
	make install && \
	popd && \
	make -C linux ARCH=x86 INSTALL_HDR_PATH=../musl/musl-kml/ headers_install

build-linux:
	docker run -it -v "$(PWD)/linux":/linux-volume --rm linuxbuild:latest	\
		bash -c "make -j8 -C /linux-volume"

clean:
	rm -rf straceout/* firecrackerout/* init/build/* kernelbuild/* rootfsbuild/* manifestout/*

benchmark-docker:
	cd docker && \
	docker build . -t redis:lupine -f redis.Dockerfile && \
	docker build . -t node:bench -f node.Dockerfile && \
	docker build . -t python:bench -f python.Dockerfile
