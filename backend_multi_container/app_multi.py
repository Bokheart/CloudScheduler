from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(
    __name__,
    static_folder="build",  # 指向前端 build 文件夹
    static_url_path="/"     # 让所有静态资源都能访问
)

# -------- 模拟算法示例 --------
def simulate_algorithm(algorithm, tasks, quantum=1):
    # 简单示例，真实你可以用你原来的算法逻辑
    timeline = []
    cpu_utilization = 100
    for t in tasks:
        start = 0
        finish = t["burst"]
        timeline.append({
            "id": t["id"],
            "start": start,
            "finish": finish
        })
        t["start"] = start
        t["finish"] = finish
        t["tat"] = finish - start
        t["wt"] = start
    return {"tasks": tasks, "timeline": timeline, "cpu_utilization": cpu_utilization}

# -------- API --------
@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json()
    algorithm = data.get("algorithm")
    tasks = data.get("tasks", [])
    quantum = data.get("quantum", 1)

    result = simulate_algorithm(algorithm, tasks, quantum)
    return jsonify(result)

# -------- 前端页面 --------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
