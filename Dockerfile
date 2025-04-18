# Use Python base image
FROM python:3.11-slim

WORKDIR /app

COPY backend ./backend
COPY frontend/dist ./frontend/dist
COPY requirements.txt ./
COPY start.sh .

RUN pip install -r requirements.txt
RUN chmod +x start.sh

CMD ["./start.sh"]
