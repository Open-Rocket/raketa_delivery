FROM python:3.11.12

RUN apt-get update && apt-get install -y gcc musl-dev python3-dev libffi-dev libssl-dev cargo ffmpeg flac

WORKDIR /raketa

COPY . /raketa

RUN pip install --no-cache-dir uv

RUN uv pip install --system --no-cache --requirements requirements.txt --verbose

EXPOSE 80

ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH=/raketa/src

RUN chmod +x src/models/create_db.py

CMD ["sh", "-c", "python -m src.models.create_db && python run.py"]