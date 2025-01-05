FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Копируем только requirements.txt перед установкой зависимостей
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Теперь копируем весь код (кеширование останется эффективным)
COPY . /app

# Открываем порт для вебхука (совпадает с конфигурацией nginx)
EXPOSE 8000

# Запускаем бота
CMD ["python", "app/main.py"]
