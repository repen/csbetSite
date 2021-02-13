#docker build -t csbet_site:latest .
#docker run --name csbetsite -d -v betscsgo_tester:/site/data -p 8080:5000 csbet_site:latest
#docker run --name csbetsite -v betscsgo_tester:/site/data -p 8080:5000 csbet_site:latest

FROM python:3.8

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
