#/bin/bash -e

APP=mariadb
DOCKER_IM=yobasystems/alpine-mariadb
DOCKER_TAG=latest
LOG_FILE=benchlogs/$APP-lower.csv
SCRIPT_DIR=$(dirname $0)/../..
BENCH_DIR=$(dirname $0)
MARIA_PASS=pass

run_docker() {
    CONTAINER_ID=$(docker run --cpus 1 --rm -d -e MYSQL_ROOT_PASSWORD=$MARIA_PASS $DOCKER_IM:$DOCKER_TAG)
    CONTAINER_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID)

    sleep 5

    python $BENCH_DIR/$APP.py $CONTAINER_IP >> $LOG_FILE

    docker stop $CONTAINER_ID > /dev/null
}

run_lupine_tests() {
    sleep 2

    while ! grep 'port: 3306  MariaDB Server' firecrackerout/$APP.log > /dev/null 2>&1; do
        sleep 1
    done

    if [ "opt" = "$1" ]; then
        python $BENCH_DIR/$APP.py 192.168.100.2 1
    else
        python $BENCH_DIR/$APP.py 192.168.100.2 >> $LOG_FILE
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
python $SCRIPT_DIR/build/build_manifest.py $DOCKER_IM $DOCKER_TAG --no_kml --output $APP --envs MYSQL_ROOT_PASSWORD=$MARIA_PASS > /dev/null 2>&1
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