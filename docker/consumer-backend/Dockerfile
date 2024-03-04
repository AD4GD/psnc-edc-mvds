ARG BUILDER_IMAGE
FROM ${BUILDER_IMAGE}

WORKDIR /app
COPY . /app
COPY src/consumer-backend-py /app

RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN useradd -ms /bin/bash admin
RUN chown -R admin:admin /app
RUN chmod 755 /app
USER admin

CMD ["python", "app.py"]
