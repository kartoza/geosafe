#!/usr/bin/env bash

# Run this from travis

# docker-geosafe dir
cd ${TRAVIS_BUILD_DIR}/../docker-geosafe/deployment

# run unittests worker
make geosafe-unittests-worker
make geosafe-test
