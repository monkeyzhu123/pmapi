FROM pmapi
ADD . /data/
WORKDIR /data/
RUN pip install -r requirements.txt
ENTRYPOINT /bin/bash start_gunicorn.sh
EXPOSE 5001