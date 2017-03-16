'run.sh' is deploy flask app in current dir.
1 install app dependence packages use:
    pip install -r requirements.txt
2 copy init script and log rotate config file to system dir
    cp logrotate_gunicorn /etc/logrotate.d/
    cp gunicorn /etc/init.d/gunicorn
3 start flask app
    /etc/init.d/gunicorn start

