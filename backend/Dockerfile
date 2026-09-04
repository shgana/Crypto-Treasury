FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
ENV PORT=8000
CMD sh -c "python -m backend.seed && uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
