
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
	git apply ../musl_kml_from_6ad514e.patch | exit 0 && \
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
	popd

build-linux:
	docker run -it -v "$(PWD)/linux":/linux-volume --rm linuxbuild:latest	\
		bash -c "make -j8 -C /linux-volume"
