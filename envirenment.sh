#/bin/bash

yum install libxml2* python-devel libxslt-devel -y
cd /root/pmapi
pip  install -r requirements.txt
chmod +x gunicorn;
./gunicorn restart
