#!/bin/bash -e
itr=10

stat() {
    awk '{x+=$0;y+=$0^2}END{print x/NR, sqrt(y/NR-(x/NR)^2)}'
}

run_lupine() {
    echo -n "lupine: "
    for i in `seq $itr`; do
        firectl --kernel kernelbuild/python-bench \
                --root-drive=rootfsbuild/python-bench.ext2 \
                --kernel-opts="console=ttyS0 noapic  panic=-1 pci=off nomodules rw init=/init"
    done 2>&1 | grep "res:" | cut -d: -f2 | stat
}

run_docker(){
    echo -n "docker: "
    for i in `seq $itr`; do
        docker run --rm python:bench
    done 2>&1 | grep "res:" | cut -d: -f2 | stat
}

echo 'platform: mean variance'
echo 'measured in seconds, lower better'
run_docker
run_lupine
