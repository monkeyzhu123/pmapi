#!/bin/bash
set -e
touch /tmp/gunicorn.log
touch /tmp/gunicorn.err
touch /tmp/access.log

# Start Gunicorn processes
echo Starting Gunicorn...
exec gunicorn app:app \
        --bind 0.0.0.0:5001 \
        --workers 4 \
        --log-level=info \
        --log-file=/tmp/gunicorn.log \
        --access-logfile=/tmp/access.log \
        "$@"
echo Gunicorn is running...