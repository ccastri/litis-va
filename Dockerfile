# # Build Stage
# FROM python:latest AS builder

# WORKDIR /app

# COPY ./requirements.txt .

# # Install dependencies
# RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Production Stage
FROM python:latest

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY . /app
# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

# Comando para iniciar el servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", '--reload']
