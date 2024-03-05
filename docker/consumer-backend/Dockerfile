ARG BUILDER_IMAGE
FROM ${BUILDER_IMAGE}

RUN useradd --create-home -s /bin/bash pipelines_user

WORKDIR /app
RUN chmod 777 /app
COPY . /app
COPY src/consumer-backend-py /app

RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /app/requirements.txt


CMD ["python", "app.py"]
