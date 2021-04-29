#!/bin/bash -e
itr=1000

stat() {
    awk '{x+=$0;y+=$0^2}END{print x/NR, sqrt(y/NR-(x/NR)^2)}'
}

run_bench() {
    for i in `seq $itr`; do
        ab -n 100 $1/index.html 2>/dev/null | grep 'Requests per second' | sed 's/  */ /g' | cut -d' ' -f 4
    done | stat
}

echo "platform: mean variance"
echo "measured in requests per second, higher better"

echo -n 'lupine: '
run_bench 192.168.100.2

echo -n 'docker: '
run_bench 172.17.0.2