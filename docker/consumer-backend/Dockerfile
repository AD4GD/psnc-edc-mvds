ARG BUILDER_IMAGE
FROM ${BUILDER_IMAGE}

WORKDIR /app
RUN chmod -R 777 /app
RUN chmod -R 777 /var/cache

COPY . /app
COPY src/consumer-backend-py /app

RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "app.py"]
