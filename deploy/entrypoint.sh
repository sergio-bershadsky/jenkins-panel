#!/bin/bash

if [ -z "$DEBUG" ]; then
    gunicorn jenkins_panel.app:app -b 0.0.0.0:80
else
    if [ "$USE_WDB" != "0" ]; then
        wdb.server.py &
    fi
    python -m jenkins_panel.run
fi