FROM python:3.11-slim

WORKDIR /app

# Node.js for Trust Wallet Agent Kit CLI (@trustwallet/cli)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g @trustwallet/cli@0.19.1 \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents agents/
COPY api api/
COPY config config/
COPY memory memory/
COPY logs logs/
COPY scripts scripts/
COPY main.py .
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["./docker-entrypoint.sh"]