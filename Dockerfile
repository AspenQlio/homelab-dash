# Stage 1: Build React Frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Python/FastAPI
FROM python:3.11-slim
WORKDIR /app
# Instalar dependencias de Docker para que python-docker funcione
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*
# Instalar dependencias de Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copiar Backend y Frontend compilado
COPY backend/ ./backend/
COPY --from=builder /app/dist ./dist
# Exponer puerto
EXPOSE 8000
# Levantar servidor
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
