#!/bin/bash -e
source scripts/run-helper.sh
itr=10

run_lupine() {
    CONFIG=$1
    KERNEL=./kernelbuild/$1/vmlinux
    shift
    echo -n "lupine: "
    for i in `seq $itr`; do
        firectl --kernel $KERNEL \
                --root-drive=rootfsbuild/python-bench.ext2 \
                --kernel-opts="console=ttyS0 noapic  panic=-1 pci=off nomodules rw init=/init"
    done 2>&1 | grep "res:" | cut -d: -f2 | stat
}

run_native(){
    echo -n "native: "
    for i in `seq $itr`; do
        python3.9 docker/bench.py
    done 2>&1 | grep "res:" | cut -d: -f2 | stat
}

run_docker(){
    echo -n "docker: "
    for i in `seq $itr`; do
        docker run --rm python:bench
    done 2>&1 | grep "res:" | cut -d: -f2 | stat
}

run_docker
run_lupine python-bench
run_native
