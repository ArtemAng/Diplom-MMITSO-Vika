FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Установка cron
RUN apt-get update && apt-get -y install cron

# Копирование файла crontab
COPY crontab /etc/cron.d/app-cron
RUN chmod 0644 /etc/cron.d/app-cron
RUN crontab /etc/cron.d/app-cron

# Создание файла для логов
RUN touch /var/log/cron.log

COPY . .

# Запуск cron и Django
CMD service cron start && python manage.py runserver 0.0.0.0:8000
