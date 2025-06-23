# Usamos la imagen base de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo requirements.txt que contiene las dependencias
COPY requirements.txt /app/

# Instalamos las dependencias desde el requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la aplicación al contenedor
COPY . /app/

# Exponemos el puerto 5009 para que sea accesible desde fuera del contenedor
EXPOSE 5009

# Copy the .env file
COPY .env /app/

# Comando para ejecutar el microservicio Flask
CMD ["python", "server.py"]