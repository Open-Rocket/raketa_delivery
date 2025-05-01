FROM python:3.11.12

RUN apt-get update && apt-get install -y \
    gcc musl-dev python3-dev libffi-dev libssl-dev \
    cargo ffmpeg flac git

RUN pip install --no-cache-dir uv

WORKDIR /raketa_delivery

COPY . /raketa_delivery

RUN uv pip install --system --verbose .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/raketa_delivery/src

RUN chmod +x src/models/create_db.py

CMD ["sh", "-c", "python -m src.models.create_db && python ./run.py"]