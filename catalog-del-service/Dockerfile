# Usa una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copiar el archivo de requerimientos
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente al contenedor
COPY . .

# Exponer el puerto donde la aplicación escuchará
EXPOSE 5011

# Copy the .env file
COPY .env /app/

# Definir el comando de inicio del contenedor
CMD ["python", "app.py"]

# Configuración para producción
ENV FLASK_ENV=production