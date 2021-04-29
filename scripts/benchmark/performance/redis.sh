#/bin/bash -e

SCRIPT_DIR=$(dirname $0)/

APP_NAME='redis-lupine'
DOCKER_IM=$(sed 's/-/:/g' <<< $APP_NAME)
echo $APP_NAME

LOG_DIR='benchlogs/'
mkdir -p $LOG_DIR

run_bench() {
    HOST=$1
    IP=$2

    redis-benchmark --csv -h $IP -t get,set > $LOG_DIR$APP_NAME-$HOST.log 2>&1
}

run_lupine() {
    python $SCRIPT_DIR/host/host.py $APP_NAME

    while ! grep -q "APP START" firecrackerout/$APP_NAME.log; do
        sleep 1
    done

    sleep 2

    run_bench lupine 192.168.100.2

    sudo kill -KILL `pgrep -x firecracker`
}

run_docker() {
    CONTAINER_ID=$(docker run --rm -d $DOCKER_IM)

    CONTAINER_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID)

    sleep 2

    run_bench docker $CONTAINER_IP

    docker stop $CONTAINER_ID
}


if [ ! -f kernelbuild/$APP_NAME ]; then
    pushd docker
    docker build . -t redis:lupine -f redis.Dockerfile
    popd

    python $SCRIPT_DIR/build/build_manifest.py redis lupine --app_conf configs/apps/redis.config
    python $SCRIPT_DIR/build/build_image.py manifestout/$APP_NAME.json > /dev/null 2>&1
else
    python $SCRIPT_DIR/build/build_image.py manifestout/$APP_NAME.json --filesystem > /dev/null 2>&1
fi

run_lupine
run_docker