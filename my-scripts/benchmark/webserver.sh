#!/bin/bash -e

SCRIPT_DIR=$(dirname $0)/

benchmark_webserver(){
    APP_NAME=$1
    DOCKER_IM=$(sed 's/-/:/g' <<< $APP_NAME)
    echo $APP_NAME

    LOG_DIR='benchlogs/'
    mkdir -p $LOG_DIR

    run_bench() {
        TYPE=$1
        HOST=$2
        IP=$3

        if [[ $TYPE == "conn" ]]; then
            ab -n 100000 $IP/index.html > $LOG_DIR$APP_NAME-$HOST-$TYPE.log 2>&1
        elif [[ $TYPE == "sess" ]]; then
            ab -k -n 100000 $IP/index.html > $LOG_DIR$APP_NAME-$HOST-$TYPE.log 2>&1
        fi
    }

    run_lupine() {
        TYPE=$1

        python $SCRIPT_DIR/host/host.py $APP_NAME

        while ! grep -q "APP START" firecrackerout/$APP_NAME.log; do
            sleep 1
        done

        sleep 5

        run_bench $TYPE lupine 192.168.100.2

        sudo kill -KILL `pgrep -x firecracker`
    }

    run_docker() {
        TYPE=$1

        CONTAINER_ID=$(docker run --rm -d $DOCKER_IM)

        CONTAINER_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID)

        sleep 5

        run_bench $TYPE docker $CONTAINER_IP

        docker stop $CONTAINER_ID
    }

    python $SCRIPT_DIR/build/build_image.py manifestout/$APP_NAME.json --filesystem > /dev/null 2>&1
    run_lupine conn
    python $SCRIPT_DIR/build/build_image.py manifestout/$APP_NAME.json --filesystem > /dev/null 2>&1
    run_lupine sess

    run_docker conn
    run_docker sess
}

benchmark_webserver nginx-alpine
benchmark_webserver httpd-alpine