#!/bin/bash -e
rep=1000000
itr=5
types="null read write"

stat() {
    awk '{x+=$0;y+=$0^2}END{print x/NR, sqrt(y/NR-(x/NR)^2)}'
}


run_test() {
    CONFIG=$1
    KERNEL=./kernelbuild/$1/vmlinux
    shift
    BIN=$@
    echo "$CONFIG $BIN"
    for t in $types; do 
        echo -n "   $t: "
        for i in `seq $itr`; do
            sudo firectl --kernel $KERNEL \
                    --tap-device=tap100/AA:FC:00:00:00:01 \
                    --root-drive=rootfsbuild/lat_syscall-latest.ext2 \
                    --kernel-opts="console=ttyS0 noapic  panic=-1 pci=off nomodules rw init=$BIN -N $rep $t"
        done 2>&1 | grep "res:" | cut -d: -f2 | stat
    done
}

run_test lupine-djw-nokml /libc.so /lat_syscall
run_test lupine-djw-kml /libc.so /lat_syscall
run_test lupine-djw-kml /lat_syscall-static
run_test lat_syscall-latest /init
