ARG BUILDER_IMAGE
FROM ${BUILDER_IMAGE}

RUN useradd --create-home -u 1000 -s /bin/bash admin
WORKDIR /app
RUN chmod 777 /app

COPY . /app
COPY src/consumer-backend-py /app

RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /app/requirements.txt

USER admin 

CMD ["python", "app.py"]
