FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "app.py"]
