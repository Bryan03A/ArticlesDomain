# Usa una imagen base de Ruby
FROM ruby:3.3.7-slim

# Instalar dependencias necesarias para Ruby y PostgreSQL
RUN apt-get update -qq && apt-get install -y build-essential libpq-dev

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copiar los archivos del proyecto
COPY Gemfile Gemfile.lock ./

# Instalar las dependencias de Ruby
RUN bundle install

# Copiar todo el código fuente al contenedor
COPY . .

# Copy the .env file
COPY .env /app/

# Exponer el puerto en el que Sinatra escuchará
EXPOSE 5012

# Definir el comando para iniciar la aplicación
CMD ["ruby", "app.rb"]