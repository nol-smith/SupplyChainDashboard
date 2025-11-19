import subprocess
import json
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    R = 6371.0
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def predict_delay(delivery, weather_risk=2, traffic_risk=2):
    """Predict delay probability using Julia ML model"""
    try:
        import os
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        julia_script = os.path.join(script_dir, 'ml_model.jl')
        
        # Prepare data for Julia
        data = {
            "delivery": delivery,
            "weather_risk": weather_risk,
            "traffic_risk": traffic_risk
        }
        
        # Call Julia script
        result = subprocess.run(
            ['julia', julia_script],
            input=json.dumps(data),
            capture_output=True,
            text=True,
            timeout=5,
            cwd=script_dir
        )
        
        if result.returncode == 0:
            return float(result.stdout.strip())
        else:
            return None
    except Exception as e:
        print(f"ML prediction error: {e}")
        return None
