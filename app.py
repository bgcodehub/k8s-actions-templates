from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)

# Simulated space weather data
def get_space_weather():
    return {
        "aurora_visibility": random.choice(["High", "Medium", "Low"]),
        "solar_activity": random.uniform(50, 150),  # Simulated solar flux (in SFU)
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC")
    }

@app.route('/')
def index():
    weather_data = get_space_weather()
    return render_template('index.html', weather=weather_data)

@app.route('/health')
def health():
    """Health check endpoint for Kubernetes liveness probe"""
    return jsonify({"status": "healthy", "time": time.time()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)