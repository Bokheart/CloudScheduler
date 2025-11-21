from flask import Flask, request, jsonify
from flask_cors import CORS
from scheduler import fcfs, sjf, srtf, rr, priority
import os

app = Flask(__name__)
CORS(app)

ALGORITHMS = {
    "fcfs": fcfs,
    "sjf": sjf,
    "srtf": srtf,
    "rr": rr,
    "priority": priority
}

@app.route("/", methods=["GET"])
def home():
    return "Cloud Scheduler backend is running!"

@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        data = request.get_json()
        tasks = data.get("tasks", [])
        algo_name = data.get("algorithm", "fcfs")
        quantum = data.get("quantum", 1)

        if algo_name not in ALGORITHMS:
            return jsonify({"error": "Invalid algorithm"}), 400

        algo_func = ALGORITHMS[algo_name]
        result = algo_func(tasks, quantum) if algo_name == "rr" else algo_func(tasks)
        return jsonify(result)

    except Exception as e:
        print("Backend Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
