using Random
using JSON

Random.seed!(42)

# Generate synthetic training data
function generate_training_data(n_samples=500)
    data = []
    
    for i in 1:n_samples
        # Random delivery parameters
        total_distance = rand(500:3000)  # km
        percent_complete = rand(0:100)
        remaining_distance = total_distance * (1 - percent_complete/100)
        
        # Time features
        elapsed_days = rand(0:10)
        expected_days = rand(1:7)
        time_until_expected = (expected_days - elapsed_days) * 24 * 3600
        
        # Risk factors
        weather_risk = rand(1:5)
        traffic_risk = rand(1:5)
        
        # Determine if delayed (ground truth)
        # Logic: High risk factors + low progress + time pressure = delay
        delay_score = 0.0
        
        # Weather and traffic contribute heavily
        delay_score += (weather_risk - 1) / 4 * 0.35
        delay_score += (traffic_risk - 1) / 4 * 0.30
        
        # Remaining distance matters
        delay_score += min(remaining_distance / 3000, 1.0) * 0.20
        
        # Time pressure is critical
        if time_until_expected < 0
            delay_score += 0.40
        else
            delay_score += (1 - time_until_expected / (7 * 24 * 3600)) * 0.40
        end
        
        # Progress helps
        delay_score -= (percent_complete / 100) * 0.25
        
        # Add some randomness
        delay_score += randn() * 0.1
        
        # Convert to binary label (delayed or not)
        is_delayed = delay_score > 0.5 ? 1 : 0
        
        push!(data, Dict(
            "total_distance" => total_distance,
            "remaining_distance" => remaining_distance,
            "percent_complete" => percent_complete,
            "elapsed_days" => elapsed_days,
            "expected_days" => expected_days,
            "time_until_expected" => time_until_expected,
            "weather_risk" => weather_risk,
            "traffic_risk" => traffic_risk,
            "is_delayed" => is_delayed,
            "delay_score" => delay_score
        ))
    end
    
    return data
end

# Generate and save training data
training_data = generate_training_data(500)

# Save to JSON
open("training_data.json", "w") do f
    JSON.print(f, training_data, 2)
end

# Print statistics
delayed_count = sum(d["is_delayed"] for d in training_data)
println("Generated $(length(training_data)) training samples")
println("Delayed: $delayed_count ($(round(delayed_count/length(training_data)*100, digits=1))%)")
println("On-time: $(length(training_data) - delayed_count) ($(round((length(training_data)-delayed_count)/length(training_data)*100, digits=1))%)")
println("Saved to training_data.json")
