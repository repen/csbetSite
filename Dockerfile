#https://habr.com/ru/post/353234/
#docker build -t csbet:latest .
#docker run --name csgowebapp --rm -d -v csbet:/home/app/data -p 8010:5000 csbet:latest
#docker run --name csgowebapp --rm -v csbet:/home/app/data -p 8010:5000 -v /home/repente/prog/python/kwork/webapp/cssbet/app:/home/app --mount type=volume,source=datadb,destination=/home/app/db,readonly csgoweb:latest

FROM python:3.6-alpine

ENV path /home

WORKDIR ${path}

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
#RUN venv/bin/pip install gunicorn


COPY boot.sh ./
COPY app ${path}/app
RUN chmod 755 boot.sh

ENV FLASK_APP main.py
ENV APP_PATH ${path}/app
ENV DB_DIR ${path}/app/db

#CMD tail -f /dev/null
ENTRYPOINT ["./boot.sh"]
