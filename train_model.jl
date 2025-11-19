using JSON
using Statistics
using LinearAlgebra

# Load training data
function load_training_data()
    data = JSON.parsefile("training_data.json")
    return data
end

# Normalize features
function normalize_features(data)
    X = zeros(length(data), 5)  # 5 features
    y = zeros(length(data))
    
    for (i, sample) in enumerate(data)
        # Normalize each feature to 0-1
        X[i, 1] = (sample["weather_risk"] - 1) / 4
        X[i, 2] = (sample["traffic_risk"] - 1) / 4
        X[i, 3] = min(sample["remaining_distance"] / 3000, 1.0)
        X[i, 4] = sample["time_until_expected"] < 0 ? 1.0 : max(0, 1 - sample["time_until_expected"] / (7 * 24 * 3600))
        X[i, 5] = sample["percent_complete"] / 100
        
        y[i] = sample["is_delayed"]
    end
    
    return X, y
end

# Sigmoid function
sigmoid(z) = 1 ./ (1 .+ exp.(-z))

# Logistic regression training using gradient descent
function train_logistic_regression(X, y; learning_rate=0.1, iterations=1000)
    n_samples, n_features = size(X)
    
    # Initialize weights and bias
    weights = zeros(n_features)
    bias = 0.0
    
    # Gradient descent
    for iter in 1:iterations
        # Forward pass
        z = X * weights .+ bias
        predictions = sigmoid(z)
        
        # Compute gradients
        dz = predictions - y
        dw = (1/n_samples) * X' * dz
        db = (1/n_samples) * sum(dz)
        
        # Update parameters
        weights -= learning_rate * dw
        bias -= learning_rate * db
        
        # Print loss every 100 iterations
        if iter % 100 == 0
            loss = -mean(y .* log.(predictions .+ 1e-10) .+ (1 .- y) .* log.(1 .- predictions .+ 1e-10))
            println("Iteration $iter: Loss = $(round(loss, digits=4))")
        end
    end
    
    return weights, bias
end

# Evaluate model
function evaluate_model(X, y, weights, bias)
    z = X * weights .+ bias
    predictions = sigmoid(z)
    predicted_labels = predictions .>= 0.5
    
    accuracy = mean(predicted_labels .== y)
    
    # Confusion matrix
    tp = sum((predicted_labels .== 1) .& (y .== 1))
    fp = sum((predicted_labels .== 1) .& (y .== 0))
    tn = sum((predicted_labels .== 0) .& (y .== 0))
    fn = sum((predicted_labels .== 0) .& (y .== 1))
    
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * (precision * recall) / (precision + recall)
    
    return accuracy, precision, recall, f1
end

# Main training script
function main()
    println("Loading training data...")
    data = load_training_data()
    println("Loaded $(length(data)) samples")
    
    println("\nNormalizing features...")
    X, y = normalize_features(data)
    
    println("\nTraining logistic regression model...")
    weights, bias = train_logistic_regression(X, y, learning_rate=0.1, iterations=1000)
    
    println("\nTrained weights:")
    println("  Weather Risk:     $(round(weights[1], digits=3))")
    println("  Traffic Risk:     $(round(weights[2], digits=3))")
    println("  Remaining Dist:   $(round(weights[3], digits=3))")
    println("  Time Pressure:    $(round(weights[4], digits=3))")
    println("  Percent Complete: $(round(weights[5], digits=3))")
    println("  Bias:             $(round(bias, digits=3))")
    
    println("\nEvaluating model...")
    accuracy, precision, recall, f1 = evaluate_model(X, y, weights, bias)
    
    println("\nModel Performance:")
    println("  Accuracy:  $(round(accuracy * 100, digits=2))%")
    println("  Precision: $(round(precision * 100, digits=2))%")
    println("  Recall:    $(round(recall * 100, digits=2))%")
    println("  F1 Score:  $(round(f1, digits=3))")
    
    # Save trained weights
    model_params = Dict(
        "weights" => weights,
        "bias" => bias,
        "accuracy" => accuracy,
        "precision" => precision,
        "recall" => recall,
        "f1" => f1
    )
    
    open("trained_model.json", "w") do f
        JSON.print(f, model_params, 2)
    end
    
    println("\nModel saved to trained_model.json")
end

main()
