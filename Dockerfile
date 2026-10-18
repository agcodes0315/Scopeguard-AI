FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

COPY frontend ./frontend

RUN mkdir -p /app/data

EXPOSE 10000

CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
