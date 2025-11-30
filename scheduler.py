# scheduler.py

from collections import deque

# ======================================================
#   统一统计函数：WT、TAT、CPU 利用率
# ======================================================
def calculate_metrics(tasks):
    """
    输入：每个 task 具有 arrival、burst、start、finish
    输出：增加 CT / TAT / WT，并返回平均指标 + CPU 利用率
    """
    total_tat = 0
    total_wt = 0
    n = len(tasks)

    # 计算 CT, TAT, WT
    for task in tasks:
        task['ct'] = task['finish']
        task['tat'] = task['ct'] - task['arrival']
        task['wt'] = task['tat'] - task['burst']

        total_tat += task['tat']
        total_wt += task['wt']

    # CPU 利用率
    start_time = min([task['arrival'] for task in tasks])
    end_time = max([task['finish'] for task in tasks])
    total_burst = sum([task['burst'] for task in tasks])
    cpu_util = total_burst / (end_time - start_time) if end_time > start_time else 1

    return {
        'tasks': tasks,
        'avg_tat': round(total_tat / n, 2),
        'avg_wt': round(total_wt / n, 2),
        'cpu_utilization': round(cpu_util * 100, 2)  # 百分比
    }


# ======================================================
#   FCFS
# ======================================================
def fcfs(tasks):
    tasks = sorted(tasks, key=lambda x: x['arrival'])
    current_time = 0
    timeline = []

    for task in tasks:
        task['start'] = max(current_time, task['arrival'])
        task['finish'] = task['start'] + task['burst']
        current_time = task['finish']

        timeline.append({
            'id': task['id'],
            'start': task['start'],
            'finish': task['finish'],
            'burst': task['burst']
        })

    result = calculate_metrics(tasks)
    result['timeline'] = timeline
    return result


# ======================================================
#   SJF （非抢占）
# ======================================================
def sjf(tasks):
    tasks = sorted(tasks, key=lambda x: (x['arrival'], x['burst']))
    n = len(tasks)
    completed = [False] * n
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

        timeline.append({
            'id': task['id'],
            'start': task['start'],
            'finish': task['finish'],
            'burst': task['burst']
        })

    result = calculate_metrics(tasks)
    result['timeline'] = timeline
    return result


# ======================================================
#   SRTF（抢占式）
# ======================================================
def srtf(tasks):
    n = len(tasks)
    remaining = [task['burst'] for task in tasks]
    start_times = [-1] * n
    finish_times = [0] * n
    current_time = 0
    completed = 0
    timeline = []

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
            timeline.append({
                'id': tasks[idx]['id'],
                'start': start_times[idx],
                'finish': finish_times[idx],
                'burst': tasks[idx]['burst']
            })

    for i in range(n):
        tasks[i]['start'] = start_times[i]
        tasks[i]['finish'] = finish_times[i]

    result = calculate_metrics(tasks)
    result['timeline'] = timeline
    return result


# ======================================================
#   RR（Round Robin）
# ======================================================
def rr(tasks, quantum=1):
    n = len(tasks)
    remaining = [task['burst'] for task in tasks]
    start_times = [-1]*n
    finish_times = [0]*n

    current_time = 0
    queue = deque()
    arrived = [False]*n
    timeline = []

    while sum(remaining) > 0:
        # 检查新到达任务
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
        # 在 timeline 中记录每个切片
        timeline.append({
            'id': tasks[idx]['id'],
            'start': current_time,
            'finish': current_time + run_time,
            'burst': run_time
        })

        remaining[idx] -= run_time
        current_time += run_time

        # 检查新到达任务
        for i in range(n):
            if tasks[i]['arrival'] <= current_time and not arrived[i] and remaining[i] > 0:
                queue.append(i)
                arrived[i] = True

        if remaining[idx] > 0:
            queue.append(idx)
        else:
            finish_times[idx] = current_time

    for i in range(n):
        tasks[i]['start'] = start_times[i]
        tasks[i]['finish'] = finish_times[i]

    result = calculate_metrics(tasks)
    result['timeline'] = timeline
    return result


# ======================================================
#   Priority（非抢占）
# ======================================================
def priority(tasks):
    n = len(tasks)
    tasks = sorted(tasks, key=lambda x: x['arrival'])
    completed = [False] * n
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

        timeline.append({
            'id': task['id'],
            'start': task['start'],
            'finish': task['finish'],
            'burst': task['burst'],
            'priority': task['priority']
        })

    result = calculate_metrics(tasks)
    result['timeline'] = timeline
    return result
