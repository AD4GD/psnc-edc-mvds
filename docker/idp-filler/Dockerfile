FROM python:3.11-slim

WORKDIR /home/app

COPY . ./

RUN apt update && \
	# apk add --no-cache bash curl jq openssl && \
	pip install --no-cache-dir -r /home/app/requirements.txt

# Default entrypoint runs Python app; compose can override if needed
ENTRYPOINT ["python", "/home/app/app.py"]
