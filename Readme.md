### Описание проекта

1. [Selenium](https://github.com/repen/csbet_selenium)
2. [Парсер](https://github.com/repen/csbetParser)
3. [Сайт](https://github.com/repen/csbetSite)


Установка

### Команды

1. клонировать репо ```git clone https://github.com/repen/csbetSite.git```
2. Билд контейнера ```docker build -t csbet:latest```
3. Запуск контейнера ```docker run --name csgowebapp --rm -d -v csbet:/home/app/data -p 8010:5000 csbet:latest```