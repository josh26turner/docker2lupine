#!/bin/bash -e
itr=30

APP=python
DOCKER_IM=python
DOCKER_TAG=bench
LOG_FILE=benchlogs/performance/$APP-lower.csv
SCRIPT_DIR=$(dirname $0)/../..
BENCH_DIR=$(dirname $0)

run_lupine() {
    for i in `seq $itr`; do
        firectl --kernel kernelbuild/$APP \
                --root-drive=rootfsbuild/$APP.ext4 \
                --kernel-opts="console=ttyS0 noapic  panic=-1 pci=off nomodules rw init=/init"
    done 2>&1 | grep "res:" | cut -d: -f2 | python $SCRIPT_DIR/benchmark/stat.py >> $LOG_FILE
}

optimise_lupine() {
    sleep 2

    while ! grep "res:" firecrackerout/$APP.log > /dev/null 2>&1; do
        sleep 1
    done

    echo ""
}

run_docker() {
    for i in `seq $itr`; do
        docker run --rm --cpus 1 python:bench
    done 2>&1 | grep "res:" | cut -d: -f2 | python $SCRIPT_DIR/benchmark/stat.py >> $LOG_FILE
}

echo "platform,mean,std" > $LOG_FILE

echo "Benching docker"
echo -n "docker," >> $LOG_FILE
run_docker

echo "Building lupine"
python $SCRIPT_DIR/build/build_manifest.py $DOCKER_IM $DOCKER_TAG --output $APP --init ENTROPY_GEN PROC_FS SYS_FS TMP_FS > /dev/null 2>&1
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json > /dev/null 2>&1

echo "Benching unoptimised lupine"
echo -n "lupine-unopt," >> $LOG_FILE
run_lupine

echo "Optimising lupine"
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json --filesystem > /dev/null 2>&1
python $SCRIPT_DIR/host/host.py $APP --strace --no_net > /dev/null 2>&1

echo "Benching optimised lupine"
echo -n "lupine-opt," >> $LOG_FILE
run_lupine
