#!/bin/bash
set -e
touch /tmp/log/gunicorn.log
touch /tmp/log/gunicorn.err
touch /tmp/log/access.log

# Start Gunicorn processes
echo Starting Gunicorn...
exec gunicorn app:app \
        --bind 0.0.0.0:5000 \
        --workers 4 \
        --log-level=info \
        --log-file=/tmp/log/gunicorn.log \
        --access-logfile=/tmp/log/access.log \
        "$@"
echo Gunicorn is running...