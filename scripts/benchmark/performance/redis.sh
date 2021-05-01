#/bin/bash -e
itr=20

APP=redis
DOCKER_IM=redis
DOCKER_TAG=lupine
LOG_FILE=benchlogs/$APP-higher.csv
SCRIPT_DIR=$(dirname $0)/../..
BENCH_DIR=$(dirname $0)

run_bench() {
    for i in `seq $itr`; do
        redis-benchmark --csv -h $1 -t get,set | grep "SET\|GET" | cut -d',' -f2 | sed 's/"//g'
    done | python $SCRIPT_DIR/benchmark/stat.py >> $LOG_FILE
}

run_docker() {
    CONTAINER_ID=$(docker run --cpus 1 --rm -d $DOCKER_IM:$DOCKER_TAG)
    CONTAINER_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID)

    sleep 5

    run_bench $CONTAINER_IP

    docker stop $CONTAINER_ID > /dev/null
}

run_lupine_tests() {
    sleep 2

    while ! grep 'Ready to accept connections' firecrackerout/$APP.log > /dev/null 2>&1; do
        sleep 1
    done

    sleep 2

    if [ "opt" = "$1" ]; then
        redis-benchmark --csv -h $1 -t get,set >/dev/null 2>&1
    else
        run_bench 192.168.100.2 >> $LOG_FILE
    fi

    echo ""
}

wait_for_lupine_stop() {
    while ! grep 'stopVMM' firecrackerout/$APP.log > /dev/null 2>&1; do
        sleep 1
    done
}

run_lupine() {
    run_lupine_tests $1 | python $SCRIPT_DIR/host/host.py $APP $2 > /dev/null 2>&1
    wait_for_lupine_stop
}

echo "platform,mean,std" > $LOG_FILE

echo "Benching docker"
echo -n "docker," >> $LOG_FILE
run_docker

echo "Building lupine"
python $SCRIPT_DIR/build/build_manifest.py $DOCKER_IM $DOCKER_TAG --output $APP > /dev/null 2>&1
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json > /dev/null 2>&1

echo "Benching unoptimised lupine"
echo -n "lupine-unopt," >> $LOG_FILE
run_lupine

echo "Optimising lupine"
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json --filesystem > /dev/null 2>&1
run_lupine opt --strace
echo "Rebuilding lupine"
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json > /dev/null 2>&1

echo "Benching optimised lupine"
echo -n "lupine-opt," >> $LOG_FILE
run_lupine