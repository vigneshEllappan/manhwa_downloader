# --- 1. Build Frontend ---
FROM node:20 AS frontend

WORKDIR /frontend
COPY frontend/ .
RUN npm install
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN REACT_APP_API_URL=$REACT_APP_API_URL npm run build


# --- 2. Build Backend ---
FROM python:3.11-slim

WORKDIR /app

# Copy backend and built frontend
COPY backend/ ./backend
COPY --from=frontend /frontend/build ./frontend/build
COPY requirements.txt .
COPY start.sh .
ENV FLASK_ENV=production
RUN pip install -r requirements.txt
RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]    