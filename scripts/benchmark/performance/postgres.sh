#!/bin/bash -e
itr=1000

stat() {
    awk '{x+=$0;y+=$0^2}END{print x/NR, sqrt(y/NR-(x/NR)^2)}'
}

run_bench() {
    PGPASSWORD=pass pgbench -i -U postgres -h $1 > /dev/null 2>&1
    for i in `seq $itr`; do
        PGPASSWORD=pass pgbench -U postgres -h $1 2> /dev/null | grep excluding | cut -d= -f 2 | cut -d\( -f 1 | sed 's/ //g'
    done | stat
}

echo "platform: mean variance"
echo "measured in transactions per second, higher better"

echo -n "docker: "
run_bench 172.17.0.2

echo -n "lupine: "
run_bench 192.168.100.2