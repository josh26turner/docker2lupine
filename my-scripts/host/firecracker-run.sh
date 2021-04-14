#!/bin/bash

sudo firectl \
    --kernel kernelbuild/$1/vmlinux \
    --root-drive=rootfsbuild/$1.ext2 \
    --ncpus=1 --memory=8192 -d \
    --tap-device=tap100/AA:FC:00:00:00:12 \
    --kernel-opts="console=ttyS0 panic=1 reboot=k pci=off ipv6.disable=1 init=$2"