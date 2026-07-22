FROM python:3.12-slim

# curl para el healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

# BD SQLite y archivos subidos viven en volúmenes
VOLUME ["/app/instance", "/app/uploads"]

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD curl -fs http://localhost:5001/login > /dev/null || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
