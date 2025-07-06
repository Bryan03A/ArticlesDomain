require 'jwt'
require 'net/http'
require 'uri'
require 'json'
require 'sinatra'
require 'mongo'
require 'pg'
require 'logger'
require 'dotenv/load'
require 'active_record'
require_relative 'price_calculator' # Requerir el archivo price_calculator.rba
require 'rack/cors'

#use Rack::Cors do
#  allow do
#    origins 'http://3.212.132.24:8080' # Agrega aquí los dominios permitidos
#    resource '*',
#      headers: :any,
#      methods: [:get, :post, :put, :delete, :options],
#      credentials: true # Permitir credenciales (cookies, headers de autenticación) 2
#  end
#end

# Configuración de la conexión a MongoDB
client = Mongo::Client.new(ENV['MONGO_URI'])
db = client.database
models_collection = db[:models]

# Setup database connection using ActiveRecord
ActiveRecord::Base.establish_connection(
  ENV['POSTGRES_URI'] + '?prepared_statements=false'
)

# Define the 'custom' table if it does not exist
class Custom < ActiveRecord::Base
  validates :model_id, :user_id, :created_by, :cost_initial, :cost_final, :state, presence: true
  after_initialize :set_default_state

  private

  def set_default_state
    self.state ||= 'required'
  end
end

# Verificar si la tabla 'customs' existe, si no, crearla y agregar la columna 'state' si no existe
conn = ActiveRecord::Base.connection.raw_connection
conn.exec <<-SQL
  CREATE TABLE IF NOT EXISTS customs (
    id SERIAL PRIMARY KEY,
    model_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_by TEXT NOT NULL,
    custom_params JSONB NOT NULL,
    cost_initial DECIMAL NOT NULL,
    cost_final DECIMAL NOT NULL,
    state TEXT NOT NULL DEFAULT 'required',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Verificar si la columna 'state' existe, si no, agregarla
  DO $$ 
  BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customs' AND column_name='state') THEN
      ALTER TABLE customs ADD COLUMN state TEXT NOT NULL DEFAULT 'required';
    END IF;
  END $$;
SQL

# Ruta para obtener los modelos del catálogo desde MongoDB
get '/models' do
  models = models_collection.find.map { |model| model }
  models.to_json
end

# Function to verify the token with the auth-service
def verify_token(token)
  uri = URI.parse("http://3.224.44.87/auth/profile")
  req = Net::HTTP::Get.new(uri)
  req['Authorization'] = "Bearer #{token}"

  res = Net::HTTP.start(uri.hostname, uri.port) { |http| http.request(req) }
  if res.code.to_i == 200
    user_info = JSON.parse(res.body)
    return user_info['username'], user_info['email'], user_info['user_id']
  else
    raise 'Invalid or expired token'
  end
end

post '/customize-model' do
  begin
    # Get the token from the header
    token = request.env["HTTP_AUTHORIZATION"]&.split(" ")&.last
    raise 'Token missing' unless token

    # Verify the token with auth-service
    username, email, user_id = verify_token(token)
    puts "✅ Usuario autenticado: ID=#{user_id}" # Log del ID del usuario

    # Obtener los datos del modelo y parámetros personalizados
    data = JSON.parse(request.body.read)
    model_id = data['model_id']
    custom_params = data['custom_params']

    # Obtener el modelo desde MongoDB usando el model_id
    model = models_collection.find(_id: BSON::ObjectId(model_id)).first
    return status 404 if model.nil?

    # Obtener el precio del modelo desde MongoDB
    price = model['price'].to_f
    puts "Precio inicial del modelo: #{price}"

    # Obtener el campo 'created_by' del modelo (nombre del usuario que lo creó)
    created_by = model['created_by']
    puts "Modelo creado por: #{created_by}"

    # Usar la clase PriceCalculator para calcular el precio final
    cost_final = PriceCalculator.calculate(price, custom_params)
    puts "Precio final calculado: #{cost_final}"

    # Guardar la personalización en la base de datos
    custom_model = Custom.create(
      model_id: model_id,
      user_id: user_id,
      created_by: created_by,  # Añadir el 'created_by' aquí
      custom_params: custom_params.to_json,
      cost_initial: price,
      cost_final: cost_final
    )

    # Ahora, hacer la solicitud POST a order-status-service para crear la orden
    uri = URI.parse("http://3.224.44.87/order-status/orders/")
    http = Net::HTTP.new(uri.host, uri.port)

    # Parámetros para la orden
    order_data = {
      order_id: custom_model.id,  # El ID de custom se envía como order_id
      requester_id: user_id.to_s,      # El user_id de custom se envía como requester_id
      created_by: custom_model.created_by      # El created_by de custom se envía como creator_id
    }

    # Configurar la solicitud
    request = Net::HTTP::Post.new(uri.path, { 'Content-Type' => 'application/json' })
    request.body = order_data.to_json

    # Enviar la solicitud
    response = http.request(request)

    if response.code.to_i == 200
      puts "Orden creada correctamente en order-status-service"
    else
      puts "Error al crear orden en order-status-service: #{response.body}"
    end

    status 200
    { message: 'Model customized and saved successfully', custom_model: custom_model }.to_json
  rescue => e
    status 400
    { message: e.message }.to_json
  end
end

# Endpoint to list all customized models for a user
get '/customize-models' do
  begin
    # Get the token from the header
    token = request.env["HTTP_AUTHORIZATION"]&.split(" ")&.last
    raise 'Token missing' unless token

    # Verify the token with auth-service
    username, email, user_id = verify_token(token)

    # Fetch all custom models for the user
    custom_models = Custom.where(user_id: user_id)

    status 200
    custom_models.to_json
  rescue => e
    status 400
    { message: e.message }.to_json
  end
end

# Endpoint to get a customized model by ID
get '/customize-model/:id' do
  begin
    # Obtener el token del encabezado
    token = request.env["HTTP_AUTHORIZATION"]&.split(" ")&.last
    raise 'Token missing' unless token

    # Verificar el token con el servicio de autenticación
    username, email, user_id = verify_token(token)

    # Buscar el modelo personalizado por ID
    custom_model = Custom.find_by(id: params[:id])
    raise 'Custom model not found' unless custom_model

    # Verificar si el custom_model pertenece al usuario por user_id
    if custom_model.user_id == user_id
      # Si coincide con user_id, continuar con la respuesta
      status 200
      {
        custom_model: custom_model,
        original_model: models_collection.find(_id: BSON::ObjectId(custom_model.model_id)).first
      }.to_json
    else
      # Si no coincide con user_id, verificar con username y la columna 'created_by'
      if custom_model.created_by == username
        # Si el username coincide con 'created_by', continuar con la respuesta
        status 200
        {
          custom_model: custom_model,
          original_model: models_collection.find(_id: BSON::ObjectId(custom_model.model_id)).first
        }.to_json
      else
        # Si no coincide ni por user_id ni por username, lanzar Unauthorized
        raise 'Unauthorized'
      end
    end
  rescue => e
    status 400
    { message: e.message }.to_json
  end
end

# Endpoint para actualizar el estado de un modelo personalizado a 'paid'
put '/customize-model/:id/state' do
  begin
    # Obtener el token del encabezado
    token = request.env["HTTP_AUTHORIZATION"]&.split(" ")&.last
    puts "Token recibido: #{token.inspect}"
    raise 'Token missing' unless token

    # Verificar el token con el servicio de autenticación
    username, email, user_id = verify_token(token)
    puts "Token verificado - Username: #{username}, Email: #{email}, User ID: #{user_id}"

    # Buscar el modelo personalizado por ID
    custom_model = Custom.find_by(id: params[:id])
    puts "Modelo encontrado: #{custom_model.inspect}"
    raise 'Custom model not found' unless custom_model

    # Verificar si el custom_model pertenece al usuario por user_id
    if custom_model.user_id == user_id || custom_model.created_by == username
      custom_model.update(state: 'paid')
      puts "Estado actualizado a 'paid'"

      status 200
      return { message: 'Estado actualizado a "paid"', custom_model: custom_model }.to_json
    else
      raise 'Unauthorized'
    end
  rescue => e
    puts "Error: #{e.message}"
    status 400
    return { message: e.message }.to_json
  end
end

set :port, 5007
set :bind, '0.0.0.0'