using JSON
using Statistics

# Simple logistic regression for delay prediction
function haversine_distance(lat1, lon1, lat2, lon2)
    R = 6371.0  # Earth radius in km
    lat1_rad, lon1_rad = deg2rad(lat1), deg2rad(lon1)
    lat2_rad, lon2_rad = deg2rad(lat2), deg2rad(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat/2)^2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)^2
    c = 2 * asin(sqrt(a))
    return R * c
end

function predict_delay_probability(delivery_data, weather_risk, traffic_risk)
    # Extract features
    origin_lat = delivery_data["origin_lat"]
    origin_lon = delivery_data["origin_lon"]
    dest_lat = delivery_data["dest_lat"]
    dest_lon = delivery_data["dest_lon"]
    current_lat = delivery_data["current_lat"]
    current_lon = delivery_data["current_lon"]
    
    # Calculate distances
    total_distance = haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    remaining_distance = haversine_distance(current_lat, current_lon, dest_lat, dest_lon)
    
    # Calculate features
    percent_complete = total_distance > 0 ? (total_distance - remaining_distance) / total_distance * 100 : 0
    
    # Time features
    current_time = time()
    elapsed_time = current_time - delivery_data["timestamp"]
    time_until_expected = delivery_data["expected_delivery_date"] - current_time
    
    # Normalize features
    norm_weather = (weather_risk - 1) / 4  # Scale 1-5 to 0-1
    norm_traffic = (traffic_risk - 1) / 4
    norm_percent = percent_complete / 100
    norm_remaining = min(remaining_distance / 3000, 1.0)  # Cap at 3000km
    norm_time_pressure = time_until_expected < 0 ? 1.0 : max(0, 1 - time_until_expected / (7 * 24 * 3600))
    
    # Load trained weights
    local w_weather, w_traffic, w_remaining, w_time_pressure, w_percent, bias
    try
        model_params = JSON.parsefile("trained_model.json")
        weights = model_params["weights"]
        w_weather = weights[1]
        w_traffic = weights[2]
        w_remaining = weights[3]
        w_time_pressure = weights[4]
        w_percent = weights[5]
        bias = model_params["bias"]
    catch
        # Fallback to default weights if model file not found
        w_weather = 0.35
        w_traffic = 0.30
        w_remaining = 0.20
        w_time_pressure = 0.40
        w_percent = -0.25
        bias = -0.5
    end
    
    # Logistic regression
    z = bias + w_weather * norm_weather + w_traffic * norm_traffic + 
        w_remaining * norm_remaining + w_time_pressure * norm_time_pressure + 
        w_percent * norm_percent
    
    # Sigmoid function
    probability = 1 / (1 + exp(-z))
    
    return round(probability * 100, digits=1)
end

function main()
    # Read input from stdin (JSON)
    input_json = readline()
    data = JSON.parse(input_json)
    
    delivery_data = data["delivery"]
    weather_risk = get(data, "weather_risk", 2)
    traffic_risk = get(data, "traffic_risk", 2)
    
    probability = predict_delay_probability(delivery_data, weather_risk, traffic_risk)
    
    # Output result
    println(probability)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
