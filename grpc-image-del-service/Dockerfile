# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalar las dependencias desde el archivo requirements.txt
RUN pip install -r requirements.txt

# Instalar grpcio-tools para poder compilar el archivo .proto
RUN pip install grpcio-tools

# Generar los archivos Python a partir del archivo .proto
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. image_service.proto

# Exponer el puerto que usa tu microservicio
EXPOSE 5014

# Copy the .env file
COPY .env /app/

# Comando para ejecutar el microservicio
CMD ["python", "server.py"]
