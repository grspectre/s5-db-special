# Базовый образ
FROM python:3.12-slim

# Устанавливаем зависимости системы (по необходимости)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем только requirements.txt для кэширования слоёв
COPY app/requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY app/ .

# Открываем порт (по желанию, для наглядности)
EXPOSE 8000

# Команда запуска (пример с gunicorn)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]