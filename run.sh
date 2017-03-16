pip install -r requirements.txt
cp logrotate_gunicorn /etc/logrotate.d/
cp gunicorn /etc/init.d/gunicorn;chmod +x /etc/init.d/gunicorn
/etc/init.d/gunicorn start
