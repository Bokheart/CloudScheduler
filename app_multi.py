# app_multi.py
# Simple cloud-ready Flask app for CloudScheduler
# Frontend is served from React build folder
# Backend handles scheduling algorithms and experiment generation

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sqlite3
import random
import ast
from datetime import datetime
from scheduler import fcfs, sjf, srtf, rr, priority

# ---------------------- Initialize Flask ----------------------
# static_folder points to React build
app = Flask(__name__, static_folder="build", static_url_path="/")
CORS(app)  # allow cross-origin requests

# ---------------------- Algorithms ----------------------
ALGORITHMS = {
    "fcfs": fcfs,
    "sjf": sjf,
    "srtf": srtf,
    "rr": rr,
    "priority": priority
}

algo_list = list(ALGORITHMS.keys())
current_algo_index = 0

# ---------------------- Initialize Database ----------------------
def init_db():
    """Create database table for storing experiment results"""
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input TEXT,
            algorithm TEXT,
            output TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ---------------------- Serve React Frontend ----------------------
@app.route('/')
def serve_frontend():
    """Serve React index.html"""
    return send_from_directory(app.static_folder, 'index.html')

# ---------------------- Show Experiment Records ----------------------
@app.route("/records")
def records():
    """Show experiment records in HTML"""
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("SELECT input, algorithm, output, created_at FROM test_results ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    grouped = {}
    for input_str, algo, output_str, created_at in rows:
        grouped.setdefault(algo, []).append((input_str, output_str, created_at))

    html_rows = ""
    for algo, experiments in grouped.items():
        html_rows += f"<h2>Algorithm: {algo} | {len(experiments)} Records</h2>"
        for input_str, output_str, created_at in experiments[:50]:
            try:
                tasks = ast.literal_eval(input_str)
            except:
                tasks = []

            task_rows = "".join(
                f"<tr><td>{t['id']}</td><td>{t['name']}</td><td>{t['arrival']}</td><td>{t['burst']}</td><td>{t['priority']}</td></tr>"
                for t in tasks
            )

            html_rows += f"""
            <h4>Experiment Time: {created_at}</h4>
            <table>
                <tr><th>ID</th><th>Name</th><th>Arrival</th><th>Burst</th><th>Priority</th></tr>
                {task_rows}
            </table>
            <pre>{output_str}</pre>
            <hr>
            """

    html = f"""
    <html>
    <head>
        <title>Random Task Scheduling Experiment Records</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            table {{ border-collapse: collapse; width: 80%; margin-bottom: 10px; }}
            th, td {{ border: 1px solid #ccc; padding: 6px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            hr {{ border: 1px dashed #ccc; margin: 20px 0; }}
            button {{ padding: 10px 20px; margin-bottom: 20px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>Random Task Scheduling Experiment Records</h1>
        <button onclick="generateNextAlgorithm()">Generate 50 Experiments for Current Algorithm (and Switch to Next)</button>
        <div id="experiments">
            {html_rows if html_rows else "<p>No experiment records yet</p>"}
        </div>

        <script>
            function generateNextAlgorithm() {{
                fetch('/generate_next')
                .then(response => response.json())
                .then(data => {{
                    alert(data.message);
                    let container = document.getElementById("experiments");

                    data.experiments.forEach(exp => {{
                        let tasksHtml = "<tr><th>ID</th><th>Name</th><th>Arrival</th><th>Burst</th><th>Priority</th></tr>";
                        exp.tasks.forEach(t => {{
                            tasksHtml += "<tr><td>" + t.id + "</td><td>" + t.name + "</td><td>" + t.arrival + "</td><td>" + t.burst + "</td><td>" + t.priority + "</td></tr>";
                        }});

                        let html = "<h2>Algorithm: " + data.algorithm + " | Experiment Time: " + exp.created_at + "</h2>" +
                                   "<table>" + tasksHtml + "</table>" +
                                   "<pre>" + JSON.stringify(exp.result, null, 2) + "</pre><hr>";

                        container.innerHTML = html + container.innerHTML;
                    }});
                }})
                .catch(err => alert('Generation failed: ' + err));
            }}
        </script>
    </body>
    </html>
    """
    return html

# ---------------------- Generate 50 Experiments API ----------------------
@app.route("/generate_next", methods=["GET"])
def generate_next():
    """Generate 50 random tasks for the current algorithm and save to DB"""
    global current_algo_index
    algo_name = algo_list[current_algo_index]
    experiments = []

    for _ in range(50):
        n_tasks = random.randint(5, 15)
        tasks = []
        for i in range(1, n_tasks + 1):
            tasks.append({
                "id": i,
                "name": f"P{i}",
                "arrival": random.randint(0, 5),
                "burst": random.randint(1, 10),
                "priority": random.randint(1, 5)
            })

        quantum = 2
        algo_func = ALGORITHMS[algo_name]

        if algo_name == "rr":
            result = algo_func(tasks, quantum)
        else:
            result = algo_func(tasks)

        conn = sqlite3.connect("results.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO test_results (input, algorithm, output) VALUES (?, ?, ?)",
            (str(tasks), algo_name, str(result))
        )
        conn.commit()
        conn.close()

        experiments.append({
            "tasks": tasks,
            "result": result,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Move to next algorithm for next call
    current_algo_index = (current_algo_index + 1) % len(algo_list)

    return jsonify({
        "status": "success",
        "algorithm": algo_name,
        "experiments": experiments,
        "message": f"Successfully generated 50 experiment records for algorithm {algo_name}"
    })

# ---------------------- Simulate Custom Task API ----------------------
@app.route("/simulate", methods=["POST"])
def simulate():
    """Simulate tasks from frontend and return result"""
    data = request.get_json()
    algo_name = data.get("algorithm")
    tasks = data.get("tasks", [])
    quantum = data.get("quantum", 2)

    if algo_name not in ALGORITHMS:
        return jsonify({"error": "Algorithm not supported"}), 400

    algo_func = ALGORITHMS[algo_name]

    try:
        if algo_name == "rr":
            result = algo_func(tasks, quantum)
        else:
            result = algo_func(tasks)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- Start Flask Server ----------------------
import os

if __name__ == "__main__":
    init_db()  
    port = int(os.environ.get("PORT", 5000))  # use PORT if provided, else 5000
    app.run(host="0.0.0.0", port=port)
