FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents agents/
COPY api api/
COPY config config/
COPY memory memory/
COPY logs logs/
COPY main.py .

EXPOSE 8080

CMD ["python", "-m", "api.server"]