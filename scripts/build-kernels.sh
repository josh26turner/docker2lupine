#!/bin/bash
# this script is a wrapper to rebulid all kernels used in the paper
# base is an empty file for cleaner scripts
for app in base redis nginx; do
    ./scripts/build-with-configs.sh nopatch configs/lupine-djw-nokml.config \
        configs/apps/$app.config;
    ./scripts/build-with-configs.sh nopatch configs/lupine-djw-nokml-tiny.config \
        configs/apps/$app.config
    ./scripts/build-with-configs.sh configs/lupine-djw-kml.config \
        configs/apps/$app.config;
    ./scripts/build-with-configs.sh configs/lupine-djw-kml-tiny.config \
        configs/apps/$app.config
done
