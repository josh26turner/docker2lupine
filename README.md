# docker2lupine: build specialised Lupines from Docker Images

> A fork of Lupine: **[Source](https://github.com/hckuo/Lupine-Linux)**, **[Paper](https://dl.acm.org/doi/10.1145/3342195.3387526)**

Automatically build specialised Lupine unikernels from Docker images.

## Dependencies

* [Firecracker](https://github.com/firecracker-microvm/firecracker)
* Python 3
* Linux host with KVM
* Make + GCC

### Benchmark Dependencies

* [memtier_benchmark](https://github.com/RedisLabs/memtier_benchmark)
* [pgbench](https://www.postgresql.org/docs/10/pgbench.html)
* [redis-benchmark](https://redis.io/topics/benchmarks)
* [ab](https://httpd.apache.org/docs/2.4/programs/ab.html)

## Usage

Setup the Python environment how you would normally using the Pipfile, install the dev dependencies if you wish to run the benchmarks.

### Build a Lupine Manifest

The first step to building your Lupine unikernel is building a manifest, for best results use an Alpine based Docker image.

Running `scripts/host/build_manifest.py` will build a manifest from a given Docker image and populates `manifestout/` with a manifest and tarball of the rootfs.

```shell
$ python scripts/host/build_manifest.py --help 

usage: build_manifest.py [-h] [--output OUTPUT] [--skip_fs_dump] [--no_kml] [--envs ENVS [ENVS ...]] [--cmd CMD] [--init INIT [INIT ...]] docker_image [docker_tag]

positional arguments:
  docker_image
  docker_tag

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT
  --skip_fs_dump        just remake the manifest
  --no_kml              disable KML in the Lupine image
  --envs ENVS [ENVS ...]
                        environment variables to add to the manifest
  --cmd CMD             comma seperated list of args to append to the command

Run from the Lupine root directory
```

For example:

```shell
$ python scripts/host/build_manifest.py nginx alpine --output nginx
```

Will create `nginx.json` and `nginx.tar` in manifestout.

### Building a Lupine Image

From the manifest you can build a Lupine image, a kernel build and `ext4` filesystem in `kernelbuild/` and `rootfsbuild`.

```sh
$ python scripts/host/build_image.py --help                        
usage: build_image.py [-h] [--name NAME] [--kernel] [--filesystem] manifest

positional arguments:
  manifest

optional arguments:
  -h, --help    show this help message and exit
  --kernel      build the kernel
  --filesystem  create the filesystem

Run from the Lupine root directory
```

For example:

```shell
$ python scripts/host/build_image.py manifestout/nginx.json
```

Will build `kernelbuild/nginx` as a vmlinux and `rootfsbuild/nginx.ext4`.

### Running the Lupine Image

Images are run in Firecracker with a Python handler script.

```sh
$ python scripts/host/host.py --help                       
usage: host.py [-h] [--ip IP] [--port PORT] [--strace] lupine

positional arguments:
  lupine                Built image to run

optional arguments:
  -h, --help            show this help message and exit
  --ip IP, -a IP
  --port PORT, -p PORT
  --strace, -s          debug to build minimal manifest

Run from Lupine root directory
```

For example:

```sh
$ python scripts/host/host.py nginx
```

Will start the NGINX webserver on 192.168.100.2.

When you want to shut down webserver, hit enter in the Python output.

#### Specialising the Image

Run you image with `--strace` to perform a trace of the application that will reduce the manifest. The manifest is expected to be in `manifestout/<APP_NAME>.json`

For example:

```sh
$ python scripts/host/host.py nginx --strace
```

A which point, use the application as you would normally and when you are finished hit enter in the Python output.

This will build a specialised manifest that can be used to rebuild the image, for example:

```shell
$ python scripts/host/build_image.py manifestout/nginx.json
```
