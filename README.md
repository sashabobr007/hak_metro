К финалу будет Docker🐳 и инструкция по запуску.
Вот же он.

Соберите образ Docker:

```
   docker build -t metro .
```
Запустите контейнер Docker:

```
   docker run -d --name metro -p 8000:8000 metro
```

Скрипты бызы данных postgresql лежат в файле postgresq.txt 