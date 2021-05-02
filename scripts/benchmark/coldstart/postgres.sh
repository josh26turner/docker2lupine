#!/bin/bash -e
itr=50

APP=postgres
DOCKER_IM=postgres
DOCKER_TAG=alpine
LOG_FILE=benchlogs/coldstart/$APP.csv
SCRIPT_DIR=$(dirname $0)/../..
BENCH_DIR=$(dirname $0)
PORT=5432
INIT_DONE='database system is ready to accept connections'
POST_PASS=pass

run_lupine() {
    for i in `seq $itr`; do
        python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json --filesystem > /dev/null 2>&1
        start=`date +%s.%N`

        python $SCRIPT_DIR/host/host.py $APP > /dev/null 2>&1 &
        
        while ! timeout 0.01 nc -z 192.168.100.2 $PORT > /dev/null 2>&1; do
            :
        done
        end=`date +%s.%N`

        echo "$end-$start" | bc

        sudo kill -KILL `pgrep -x firecracker`

        wait_for_lupine_stop

        sleep 1
    done | python $SCRIPT_DIR/benchmark/stat.py >> $LOG_FILE
}

run_docker() {
    for i in `seq $itr`; do
        start=`date +%s.%N`

        CONTAINER_ID=$(docker run --cpus 1 --rm -d -e POSTGRES_PASSWORD=$POST_PASS $DOCKER_IM:$DOCKER_TAG)
        CONTAINER_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID)
        
        while ! timeout 0.01 nc -z $CONTAINER_IP $PORT > /dev/null 2>&1; do
            :
        done

        end=`date +%s.%N`

        echo "$end-$start" | bc

        docker kill $CONTAINER_ID > /dev/null
    done | python $SCRIPT_DIR/benchmark/stat.py >> $LOG_FILE
}

opt_lupine_test() {
    sleep 2

    while ! grep "$INIT_DONE" firecrackerout/$APP.log > /dev/null 2>&1; do
        sleep 1
    done

    sleep 2

    PGPASSWORD=$POST_PASS pgbench -i -U postgres -h 192.168.100.2 > /dev/null 2>&1

    echo ""
}

wait_for_lupine_stop() {
    while ! grep 'stopVMM' firecrackerout/$APP.log > /dev/null 2>&1; do
        sleep 1
    done
}


opt_lupine() {
    opt_lupine_test | python $SCRIPT_DIR/host/host.py $APP --strace > /dev/null 2>&1
    wait_for_lupine_stop
}

echo "platform,mean,std" > $LOG_FILE

echo "Benching docker"
echo -n "docker," >> $LOG_FILE
run_docker

echo "Building lupine"
python $SCRIPT_DIR/build/build_manifest.py $DOCKER_IM $DOCKER_TAG --output $APP --envs POSTGRES_PASSWORD=$POST_PASS > /dev/null 2>&1
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json > /dev/null 2>&1

echo "Benching unoptimised lupine"
echo -n "lupine-unopt," >> $LOG_FILE
run_lupine

echo "Optimising lupine"
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json --filesystem > /dev/null 2>&1
opt_lupine
echo "Rebuilding lupine"
python $SCRIPT_DIR/build/build_image.py manifestout/$APP.json > /dev/null 2>&1

echo "Benching optimised lupine"
echo -n "lupine-opt," >> $LOG_FILE
run_lupine