ARG BUILDER_IMAGE
FROM ${BUILDER_IMAGE}

WORKDIR /app
COPY ./docker/consumer-backend/* /app
COPY src/consumer-backend-py /app

RUN mkdir -p /app/data && chmod -R 777 /app/data
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "app.py"]
