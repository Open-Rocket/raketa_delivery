FROM python:3.11.12

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc musl-dev python3-dev libffi-dev libssl-dev \
    cargo ffmpeg flac git

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Рабочая директория
WORKDIR /raketa_delivery

# Копируем проект
COPY . /raketa_delivery

# Устанавливаем зависимости через uv из pyproject.toml
RUN uv pip install --system --verbose

# Настройки
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/raketa_delivery/src

# Делаем файлы исполняемыми
RUN chmod +x src/models/create_db.py

RUN pkill -f "python run.py" || true 

# Запуск
CMD ["python", "-m", "src.models.create_db && ./run.py"]
