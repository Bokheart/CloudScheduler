# app_multi.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from scheduler import fcfs, sjf, srtf, rr, priority

app = Flask(__name__)

# 允许来自 React 前端的跨域请求
from flask_cors import CORS

CORS(app)  # 允许所有跨域请求


ALGORITHMS = {
    "fcfs": fcfs,
    "sjf": sjf,
    "srtf": srtf,
    "rr": rr,
    "priority": priority
}

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
        if algo_name == "rr":
            result = algo_func(tasks, quantum)
        else:
            result = algo_func(tasks)

        return jsonify(result)

    except Exception as e:
        print("Backend Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 强制绑定 0.0.0.0 便于浏览器访问
   app.run(host="0.0.0.0", port=5001, debug=True)
