# Dockerfile for FastAPI app

# Usa una imagen base con Python
FROM python:latest

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install -r requirements.txt  # Asegúrate de tener un requirements.txt con las dependencias de FastAPI

# Expone el puerto 8000
EXPOSE 8000

# Comando para iniciar el servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
