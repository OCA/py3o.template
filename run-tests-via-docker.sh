#!/bin/bash
# Run tests using a Docker image, same as the CI (see .drone.yml).

TESTDIR="py3o-tox" # Directory within the container we mount into.

docker run --name py3o.template-tests --rm -it \
    -v "$PWD:/$TESTDIR" \
    python:3 \
    sh -c "cd $TESTDIR && pip install tox && tox"
