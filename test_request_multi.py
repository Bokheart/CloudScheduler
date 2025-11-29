# test_request_multi.py
import requests

# function to get tasks from user
def get_tasks_input(algorithm):
    num_tasks = int(input("Enter number of tasks: "))
    tasks = []
    for i in range(num_tasks):
        burst = int(input(f"Task {i+1} burst time: "))
        arrival = int(input(f"Task {i+1} arrival time: "))
        task = {"id": i+1, "burst": burst, "arrival": arrival}
        # only ask priority if algorithm is Priority
        if algorithm == "priority":
            priority_val = int(input(f"Task {i+1} priority (lower number = higher priority): "))
            task["priority"] = priority_val
        tasks.append(task)
    return tasks

# function to print results in table and timeline
def print_results(data, algorithm):
    print("\n=== Simulation Results ===\n")
    print(f"CPU Utilization: {data.get('cpu_utilization',0):.2f}\n")

    # define headers and column widths
    headers = ["Task", "AT", "BT"]
    if algorithm == "priority":
        headers.append("PR")
    headers += ["CT", "TAT", "WT"]

    # calculate max width for each column (for centering)
    columns = {h: max(len(h), 5) for h in headers}

    # print header
    header_line = "  ".join(f"{h:^{columns[h]}}" for h in headers)
    print(header_line)
    print("-" * len(header_line))

    # print each task
    for t in data.get("tasks", []):
        values = [
            f"{str(t['id']):^{columns['Task']}}",
            f"{str(t['arrival']):^{columns['AT']}}",
            f"{str(t['burst']):^{columns['BT']}}"
        ]
        if algorithm == "priority":
            values.append(f"{str(t.get('priority',0)):^{columns['PR']}}")
        values += [
            f"{str(t['ct']):^{columns['CT']}}",
            f"{str(t['tat']):^{columns['TAT']}}",
            f"{str(t['wt']):^{columns['WT']}}"
        ]
        print("  ".join(values))

    # print timeline
    print("\nTimeline:")
    for t in data.get("timeline", []):
        print(f"Task {t['id']}: Start={t['start']} -> Finish={t['finish']}, Burst={t['burst']}")

    print("\n" + "="*60 + "\n")

def main():
    print("Select scheduling algorithm:")
    print("1. FCFS")
    print("2. SJF")
    print("3. SRTF")
    print("4. RR")
    print("5. Priority")
    choice = input("Enter choice (1-5): ")

    algo_map = {
        "1": "fcfs",
        "2": "sjf",
        "3": "srtf",
        "4": "rr",
        "5": "priority"
    }

    algorithm = algo_map.get(choice, "fcfs")

    # ask for RR time quantum if needed
    quantum = 1
    if algorithm == "rr":
        quantum = int(input("Enter time quantum for RR: "))

    # get tasks info from user
    tasks = get_tasks_input(algorithm)

    # prepare payload to send to backend
    payload = {
        "algorithm": algorithm,
        "tasks": tasks,
        "quantum": quantum
    }

    try:
        response = requests.post("http://127.0.0.1:5000/simulate", json=payload)
        data = response.json()
        if "error" in data:
            print("Error from backend:", data["error"])
        else:
            print_results(data, algorithm)
    except Exception as e:
        print("Error connecting to backend:", e)

if __name__ == "__main__":
    main()
