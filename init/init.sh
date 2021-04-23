#!/libc.so /bin/sh

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
    echo "127.0.0.1       localhost" > /etc/hosts
}

entropy_gen() {
    echo "Generating entropy"
    /reseed 2048
    /reseed 2048
    /reseed 2048
    /reseed 2048
}

tmpfs() {
    echo "Mounting tmpfs"
    mount -t tmpfs tmpfs /tmp
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

if [ "$TMP_FS" = "1" ]; then
    tmpfs
fi

cd $WORKING_DIR

echo "==============APP START=============="

if [ "$1" = "strace" ]; then
    shift

    eval strace -ff -o /$NAME $CMD $@ &

    RES=$(curl 192.168.100.1:8080 2>/dev/null)
    while [ "$RES" != "Stop" ]; do 
        RES=$(curl 192.168.100.1:8080 2> /dev/null)
        sleep 3
    done

    kill -KILL `pgrep strace`

    STRACE_FILES=/$NAME*

    for dump in $STRACE_FILES; do
        echo -n "$dump: "
        curl -F file_1=@$dump 192.168.100.1:8080 && echo
    done

    curl 192.168.100.1:8080/finish && echo
else
    exec $CMD
fi

echo "==============ALL CLOSE=============="