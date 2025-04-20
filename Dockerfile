# --- 1. Build Frontend ---
FROM node:20 AS frontend

WORKDIR /frontend
COPY frontend/ ./
RUN npm install
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN REACT_APP_API_URL=$REACT_APP_API_URL npm run build


# --- 2. Build Spring Boot Backend ---
FROM eclipse-temurin:21 AS backend-build

WORKDIR /app

# Copy backend source
COPY backend/ ./backend
COPY --from=frontend /frontend/build ./backend/src/main/resources/static

# Build Spring Boot JAR
WORKDIR /app/backend
RUN chmod +x ./gradlew
RUN ./gradlew build --no-daemon

# --- 3. Final Image ---
FROM eclipse-temurin:21-jre

WORKDIR /app

# Copy the built JAR from the build container
COPY --from=backend-build /app/backend/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]