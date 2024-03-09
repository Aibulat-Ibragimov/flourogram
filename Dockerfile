# Используем базовый образ Python
FROM python:3.8

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем все файлы из текущего каталога в контейнер
COPY . .

# Определяем переменные окружения
ENV FLASK_APP=app.py

# Открываем порт, на котором будет работать Flask приложение
EXPOSE 5000

# Команда для запуска Flask приложения
CMD ["flask", "run", "--host=0.0.0.0"]
