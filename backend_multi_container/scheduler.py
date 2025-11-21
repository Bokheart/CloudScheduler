from collections import deque

def calculate_metrics(tasks):
    for task in tasks:
        task['ct'] = task['finish']
        task['tat'] = task['ct'] - task['arrival']
        task['wt'] = task['tat'] - task['burst']

    total_burst = sum([task['burst'] for task in tasks])
    last_finish = max([task['finish'] for task in tasks])
    cpu_util = total_burst / last_finish if last_finish > 0 else 0

    return tasks, cpu_util

# -------------------------------
# FCFS
def fcfs(tasks):
    tasks = sorted(tasks, key=lambda x: x['arrival'])
    current_time = 0
    timeline = []
    for task in tasks:
        task['start'] = max(current_time, task['arrival'])
        task['finish'] = task['start'] + task['burst']
        current_time = task['finish']
        timeline.append({'id': task['id'], 'start': task['start'], 'finish': task['finish'], 'burst': task['burst']})
    tasks, cpu_util = calculate_metrics(tasks)
    return {'tasks': tasks, 'cpu_utilization': cpu_util, 'timeline': timeline}

# -------------------------------
# SJF
def sjf(tasks):
    tasks = sorted(tasks, key=lambda x: (x['arrival'], x['burst']))
    n = len(tasks)
    completed = [False]*n
    current_time = 0
    timeline = []
    for _ in range(n):
        available = [i for i in range(n) if tasks[i]['arrival'] <= current_time and not completed[i]]
        if not available:
            current_time = min([tasks[i]['arrival'] for i in range(n) if not completed[i]])
            available = [i for i in range(n) if tasks[i]['arrival'] <= current_time and not completed[i]]
        idx = min(available, key=lambda i: tasks[i]['burst'])
        task = tasks[idx]
        task['start'] = max(current_time, task['arrival'])
        task['finish'] = task['start'] + task['burst']
        current_time = task['finish']
        completed[idx] = True
        timeline.append({'id': task['id'], 'start': task['start'], 'finish': task['finish'], 'burst': task['burst']})
    tasks, cpu_util = calculate_metrics(tasks)
    return {'tasks': tasks, 'cpu_utilization': cpu_util, 'timeline': timeline}

# -------------------------------
# SRTF
def srtf(tasks):
    n = len(tasks)
    remaining = [task['burst'] for task in tasks]
    start_times = [-1]*n
    finish_times = [0]*n
    current_time = 0
    timeline = []
    completed = 0
    while completed < n:
        available = [i for i in range(n) if tasks[i]['arrival'] <= current_time and remaining[i] > 0]
        if not available:
            current_time += 1
            continue
        idx = min(available, key=lambda i: remaining[i])
        if start_times[idx] == -1:
            start_times[idx] = current_time
        remaining[idx] -= 1
        current_time += 1
        if remaining[idx] == 0:
            finish_times[idx] = current_time
            completed += 1
            timeline.append({'id': tasks[idx]['id'], 'start': start_times[idx], 'finish': finish_times[idx], 'burst': tasks[idx]['burst']})
    for i in range(n):
        tasks[i]['start'] = start_times[i]
        tasks[i]['finish'] = finish_times[i]
    tasks, cpu_util = calculate_metrics(tasks)
    return {'tasks': tasks, 'cpu_utilization': cpu_util, 'timeline': timeline}

# -------------------------------
# RR
def rr(tasks, quantum=1):
    n = len(tasks)
    remaining = [task['burst'] for task in tasks]
    start_times = [-1]*n
    finish_times = [0]*n
    current_time = 0
    timeline = []
    queue = deque()
    arrived = [False]*n
    while sum(remaining) > 0:
        for i in range(n):
            if tasks[i]['arrival'] <= current_time and not arrived[i] and remaining[i] > 0:
                queue.append(i)
                arrived[i] = True
        if not queue:
            current_time += 1
            continue
        idx = queue.popleft()
        if start_times[idx] == -1:
            start_times[idx] = current_time
        run_time = min(quantum, remaining[idx])
        current_time += run_time
        remaining[idx] -= run_time
        if remaining[idx] == 0:
            finish_times[idx] = current_time
            timeline.append({'id': tasks[idx]['id'], 'start': start_times[idx], 'finish': finish_times[idx], 'burst': tasks[idx]['burst']})
        else:
            for i in range(n):
                if tasks[i]['arrival'] <= current_time and not arrived[i] and remaining[i] > 0:
                    queue.append(i)
                    arrived[i] = True
            queue.append(idx)
    for i in range(n):
        tasks[i]['start'] = start_times[i]
        tasks[i]['finish'] = finish_times[i]
    tasks, cpu_util = calculate_metrics(tasks)
    return {'tasks': tasks, 'cpu_utilization': cpu_util, 'timeline': timeline}

# -------------------------------
# Priority
def priority(tasks):
    n = len(tasks)
    tasks = sorted(tasks, key=lambda x: x['arrival'])
    completed = [False]*n
    current_time = 0
    timeline = []
    for _ in range(n):
        available = [i for i in range(n) if tasks[i]['arrival'] <= current_time and not completed[i]]
        if not available:
            current_time = min([tasks[i]['arrival'] for i in range(n) if not completed[i]])
            available = [i for i in range(n) if tasks[i]['arrival'] <= current_time and not completed[i]]
        idx = min(available, key=lambda i: tasks[i]['priority'])
        task = tasks[idx]
        task['start'] = max(current_time, task['arrival'])
        task['finish'] = task['start'] + task['burst']
        current_time = task['finish']
        completed[idx] = True
        timeline.append({'id': task['id'], 'start': task['start'], 'finish': task['finish'], 'burst': task['burst'], 'priority': task['priority']})
    tasks, cpu_util = calculate_metrics(tasks)
    return {'tasks': tasks, 'cpu_utilization': cpu_util, 'timeline': timeline}
