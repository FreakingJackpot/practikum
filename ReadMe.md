Инструкция по запуску:

1) Установить python3.8
2) pip install requirements.txt (requirements под linux)
3) Установить postgreSQL (последнюю на данный момент версию)
4) Создать .env файл в корне проекта и вписать в него
   DATABASE_NAME,DATABASE_USER,DATABASE_PASSWORD,DATABASE_HOST,DATABASE_PORT,DEBUG
5) ./manage.py migrate
6) ./manage.py runserver