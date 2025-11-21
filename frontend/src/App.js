import { useState } from "react";
import axios from "axios";

export default function SchedulerForm() {
  const [tasks, setTasks] = useState([{ id: 1, at: "", bt: "", priority: "" }]);
  const [algorithm, setAlgorithm] = useState("FCFS");
  const [quantum, setQuantum] = useState(1);
  const [result, setResult] = useState(null);

  const addTask = () => {
    setTasks([...tasks, { id: Date.now(), at: "", bt: "", priority: "" }]);
  };

  const removeTask = (id) => {
    setTasks(tasks.filter((task) => task.id !== id));
  };

  const handleChange = (id, field, value) => {
    setTasks(
      tasks.map((task) => (task.id === id ? { ...task, [field]: value } : task))
    );
  };

  const runSimulation = async () => {
    try {
     const formattedTasks = tasks.map((t, index) => ({
  id: index + 1,
  arrival: parseInt(t.at) || 0,
  burst: parseInt(t.bt) || 0,
  priority: parseInt(t.priority) || 0
}));


      const response = await axios.post("http://localhost:5001/simulate", {
        algorithm: algorithm.toLowerCase(),
        tasks: formattedTasks,
        quantum: parseInt(quantum)
      });

      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert("请求后端失败，请确认 Flask 已启动并且端口正确");
    }
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      {/* 算法选择 */}
      <div className="mb-4">
        <label className="mr-2 font-bold">Select Algorithm:</label>
        <select
          value={algorithm}
          onChange={(e) => setAlgorithm(e.target.value)}
          className="border p-1 rounded"
        >
          <option value="FCFS">FCFS</option>
          <option value="SJF">SJF</option>
          <option value="SRTF">SRTF</option>
          <option value="RR">RR</option>
          <option value="Priority">Priority</option>
        </select>
      </div>

      {/* RR 时间片 */}
      {algorithm === "RR" && (
        <div className="mb-4">
          <label className="mr-2 font-bold">Time Quantum:</label>
          <input
            type="number"
            value={quantum}
            onChange={(e) => setQuantum(e.target.value)}
            className="border p-1 w-20 rounded"
          />
        </div>
      )}

      {/* 任务输入 */}
      {tasks.map((task, index) => (
        <div
          key={task.id}
          className="flex items-center gap-2 mb-2 border p-2 rounded"
        >
          <span>Task {index + 1}:</span>
          <input
            type="number"
            placeholder="AT"
            value={task.at}
            onChange={(e) => handleChange(task.id, "at", e.target.value)}
            className="border p-1 w-16 rounded"
          />
          <input
            type="number"
            placeholder="BT"
            value={task.bt}
            onChange={(e) => handleChange(task.id, "bt", e.target.value)}
            className="border p-1 w-16 rounded"
          />
          {algorithm === "Priority" && (
            <input
              type="number"
              placeholder="Priority"
              value={task.priority}
              onChange={(e) =>
                handleChange(task.id, "priority", e.target.value)
              }
              className="border p-1 w-16 rounded"
            />
          )}
          <button
            onClick={() => removeTask(task.id)}
            className="bg-red-500 text-white px-2 py-1 rounded"
          >
            Delete
          </button>
        </div>
      ))}

      <div className="flex gap-2 mt-2">
        <button
          onClick={addTask}
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          Add Task
        </button>
        <button
          onClick={runSimulation}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Run Simulation
        </button>
      </div>

      {/* 结果展示 */}
      {result && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h3 className="font-bold mb-2 text-lg">
            CPU Utilization: {result.cpu_utilization}
          </h3>

          <h4 className="font-bold mb-1">Task Results:</h4>
          <table className="border-collapse border border-black w-full text-left mb-4">
            <thead>
              <tr>
                <th className="border px-1">ID</th>
                <th className="border px-1">Start</th>
                <th className="border px-1">Finish</th>
                <th className="border px-1">TAT</th>
                <th className="border px-1">WT</th>
              </tr>
            </thead>
            <tbody>
              {result.tasks.map((t) => (
                <tr key={t.id}>
                  <td className="border px-1">{t.id}</td>
                  <td className="border px-1">{t.start}</td>
                  <td className="border px-1">{t.finish}</td>
                  <td className="border px-1">{t.tat}</td>
                  <td className="border px-1">{t.wt}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* 彩色甘特图 */}
          <h4 className="font-bold mb-2">Gantt Chart:</h4>
          <div style={{ overflowX: "auto", border: "1px solid #ccc", padding: "8px", borderRadius: "6px", background: "#fff" }}>
            {/* 甘特图条 */}
            <div style={{ display: "flex", height: "60px", alignItems: "flex-end" }}>
              {result.timeline.map((t, idx) => {
                const colors = ["#1E3A8A", "#10B981", "#8B5CF6", "#FBBF24", "#EF4444", "#EC4899", "#6366F1", "#14B8A6"];
                return (
                  <div
                    key={idx}
                    style={{
                      width: `${(t.finish - t.start) * 30}px`,
                      height: "3rem",
                      backgroundColor: colors[idx % colors.length],
                      color: "#fff",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      borderTopLeftRadius: "4px",
                      borderTopRightRadius: "4px",
                      marginRight: "2px",
                      position: "relative",
                    }}
                  >
                    <span style={{ position: "absolute", top: "-18px", fontSize: "12px", fontWeight: "bold" }}>
                      T{t.id}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* 时间刻度 */}
            <div style={{ display: "flex", marginTop: "4px", fontSize: "12px" }}>
              {result.timeline.map((t, idx) => (
                <div
                  key={idx}
                  style={{
                    width: `${(t.finish - t.start) * 30}px`,
                    position: "relative",
                    textAlign: "left"
                  }}
                >
                  <span>{t.start}</span>
                  {idx === result.timeline.length - 1 && (
                    <span style={{ position: "absolute", right: 0 }}>{t.finish}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

