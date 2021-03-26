#!/bin/sh

procfs() {
    echo "Mounting procfs"
    mount -t proc proc /proc
}

net_setup() {
    echo "Network setup"
    ./busybox-x86_64 ip addr add 192.168.100.2/24 dev eth0
    ./busybox-x86_64 ip addr add 127.0.0.1/24 dev lo
    ./busybox-x86_64 ip link set eth0 up
    ./busybox-x86_64 ip link set lo up
    ./busybox-x86_64 ip route add default via 192.168.100.1 dev eth0

    echo "nameserver 192.168.100.1" > /etc/resolv.conf
}

entropy_gen() {
    echo "Sleeping"
    sleep 1
}

. ./env.sh

if [ "$PROC_FS" = "1" ]; then
    procfs
fi

if [ "$NET_SETUP" = "1" ]; then
    net_setup
fi

if [ "$ENTROPY_GEN" = "1" ]; then
    entropy_gen
fi

cd $WORKING_DIR

eval "$CMD"