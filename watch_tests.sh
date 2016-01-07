#!/usr/bin/env bash

command="docker-compose run --rm --entrypoint django-admin \
    service-jenkins-panel test"

watchmedo shell-command --recursive -p "*.py;*tests/*.xml" \
    -c "$command" --interval=30 --drop ./