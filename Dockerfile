FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /auvk6_bot

# Устанавливаем зависимости системы (по минимуму)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Сначала requirements (оптимизация кеша)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной проект
COPY . .

COPY .env.prod .env

# Запуск бота
CMD ["python", "main.py"]
