FROM python:3.11-slim

WORKDIR /auvk6_bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Порт для Render
EXPOSE 8080

CMD ["python", "main.py"]
