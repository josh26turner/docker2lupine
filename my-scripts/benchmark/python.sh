#!/bin/bash -e
source scripts/run-helper.sh
itr=50

run_lupine() {
    CONFIG=$1
    KERNEL=./kernelbuild/$1/vmlinux
    shift
    echo -n "lupine: "
    for i in `seq $itr`; do
        sudo firectl --kernel $KERNEL \
                --tap-device=tap100/AA:FC:00:00:00:01 \
                --root-drive=rootfsbuild/python-bench.ext2 \
                --kernel-opts="console=ttyS0 noapic  panic=-1 pci=off nomodules rw init=/init"
    done 2>&1 | grep "res:" | cut -d: -f2 | stat
}

run_bare(){
    echo -n "bare: "
    for i in `seq $itr`; do
        python docker/bench.py
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
run_bare
