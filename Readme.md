### Описание проекта

Каккойто проект....

### Зависимости

**Docker**

### Команды


1. клонировать репо ```git clone```
2. Билд контейнера ```docker build -t csbet:latest```
3. Запуск контейнера ```docker run --name csgowebapp --rm -d -v csbet:/home/app/data -p 8010:5000 csbet:latest```