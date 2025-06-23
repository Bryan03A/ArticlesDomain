# price_calculator.rb

class PriceCalculator
  def self.calculate(price, custom_params)
    cost_final = price # El precio inicial es el precio del modelo

    custom_params.each do |key, value|
      # Ajuste por calidad del filamento
      if key == 'filament_quality'
        case value
        when 'Low'
          cost_final += 0
        when 'Medium'
          cost_final += 5.0
        when 'High'
          cost_final += 10.0
        end
      end

      # Ajuste por color
      if key == 'color'
        case value
        when 'Red'
          cost_final += 0
        when 'Gold'
          cost_final += 5.0
        when 'Blue'
          cost_final += 3.0
        end
      end

      # Ajuste por tamaño
      if key == 'size'
        case value
        when 'Small'
          cost_final += 0
        when 'Medium'
          cost_final += 5.0
        when 'Large'
          cost_final += 8.0
        end
      end

      # Ajuste por complejidad de la forma
      if key == 'shape_complexity'
        case value
        when 'Low'
          cost_final += 0
        when 'Medium'
          cost_final += 6.0
        when 'High'
          cost_final += 12.0
        end
      end

      # Ajuste por tipo de material
      if key == 'material_type'
        case value
        when 'Standard'
          cost_final += 0
        when 'Premium'
          cost_final += 15.0
        when 'Luxury'
          cost_final += 25.0
        end
      end
    end

    return cost_final
  end
end