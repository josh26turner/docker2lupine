#!/bin/bash -e
itr=10

stat() {
    awk '{x+=$0;y+=$0^2}END{print x/NR, sqrt(y/NR-(x/NR)^2)}'
}

run_bench() {
    for i in `seq $itr`; do
        memtier_benchmark --protocol=memcache_text --server=$1 --port=11211 -t 1 2>/dev/null | grep Totals | sed 's/  */ /g' | cut -d' ' -f2
    done | stat
}

echo "platform: mean variance"
echo "measured in operations per second, higher better"

echo -n "docker: "
run_bench 172.17.0.2

echo -n "lupine: "
run_bench 192.168.100.2