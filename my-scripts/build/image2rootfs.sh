#!/bin/bash
# Usage: ./image2rootfs.sh app tag fs

dir="$(dirname `realpath $0`)"
guestdir=$dir/../guest

die() { echo "$*" 1>&2 ; exit 1; }

app=$1 tag=$2
fs=${3:-ext2}
echo $app $tag

container_id=$(docker create $app:$tag || die "run container failed.")
if [ "$container_id" == "" ]; then
    die "empty container id."
fi

app=$dir/../../rootfsbuild/$(echo $app | tr '/' '-'):$tag
docker export $container_id > $app.tar || die "failed to create tar."
trap "rm $app.tar" EXIT
docker rm $container_id;
mnt=$(mktemp -d)
dd if=/dev/zero of=$app.$fs bs=1 count=0 seek=20G
yes | mkfs."$fs" "$app.$fs"
sudo mount "$app.$fs" $mnt
sudo tar -xvf $app.tar -C $mnt > /dev/null

# install devices
sudo mknod -m 666 $mnt/dev/null c 1 3
sudo mknod -m 666 $mnt/dev/zero c 1 5
sudo mknod -m 666 $mnt/dev/ptmx c 5 2
sudo mknod -m 666 $mnt/dev/tty c 5 0
sudo mknod -m 444 $mnt/dev/random c 1 8
sudo mknod -m 444 $mnt/dev/urandom c 1 9
sudo mknod -m 660 $mnt/dev/mem c 1 1

# install network setup script
sudo cp $guestdir/busybox-x86_64 $mnt
sudo cp $guestdir/guest* $mnt

# install musl libc
sudo mkdir -p $mnt/trusted
sudo cp $guestdir/libc.so $mnt/trusted/libc.so

sudo umount $mnt
rmdir $mnt
