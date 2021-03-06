#!/bin/bash

kernel=$1
rootfs=$2
init=$3

sudo firectl \
    --kernel $1 \
    --root-drive=$2 \
    --vmm-log-fifo=firelog --ncpus=1 --memory=8192 -d \
    --tap-device=tap100/AA:FC:00:00:00:12 \
    --kernel-opts="console=ttyS0 panic=1 init=$3"