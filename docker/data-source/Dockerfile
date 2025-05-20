ARG BUILDER_IMAGE
FROM ${BUILDER_IMAGE}

WORKDIR /app
COPY ./docker/data-source/* /app
COPY src/data-source /app

RUN mkdir /app/data && chmod -R 777 /app/data
RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "app.py"]