FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]