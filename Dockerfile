# --- 1. Build Frontend ---
FROM node:20 AS frontend

WORKDIR /frontend
COPY frontend/ .
RUN npm install
RUN npm run build

# --- 2. Build Backend ---
FROM python:3.11-slim

WORKDIR /app

# Copy backend and built frontend
COPY backend/ ./backend
COPY --from=frontend /frontend/dist ./frontend/dist
COPY requirements.txt .
COPY start.sh .

RUN pip install -r requirements.txt
RUN chmod +x start.sh

CMD ["./start.sh"]    