#docker build -t csbet_site:latest .
#docker run --name csbetsite --rm -d -v betscsgo:/site/data -p 8030:5000 csbet_site:latest
#docker run --name csbetsite --rm -v betscsgo:/site/data -p 8030:5000 csbet_site:latest

FROM python:3.6-alpine

ENV path /site

COPY app ${path}
WORKDIR ${path}

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV EXTERNAL_WORK true
ENV BASE_DIR ${path}
ENV DATA_DIR ${path}/data

#CMD tail -f /dev/null
CMD python main.py
