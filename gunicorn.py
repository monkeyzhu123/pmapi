# /bin/env python

bind = '0.0.0.0:5001'
backlog = 2048
workers = 3
worker_class = 'gevent'
worker_connections = 1000
timeout = 10
keepalive = 1
daemon = True
errorlog = '/var/log/gunicorn_error.log'
pidfile = '/tmp/gunicorn.pid'
loglevel = 'debug'
accesslog = '/var/log/gunicorn.log'
