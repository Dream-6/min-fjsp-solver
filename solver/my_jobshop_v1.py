import collections
from ortools.sat.python import cp_model
import matplotlib.pyplot as plt

jobs_data = [
    [(0, 4), (1, 6), (2, 2)],    # job0
    [(0, 2), (2, 4), (1, 4)],     # job1
    [(1, 4), (2, 2), (0, 1)]              # job2
]

machines_count = 1+ max(task[0] for job in jobs_data for task in job) #
all_machines = range(machines_count)

# horizon设置为所有任务的总时间长度
horizon = sum(task[1] for job in jobs_data for task in job)

# 建模
model = cp_model.CpModel() 

# 变量
task_type = collections.namedtuple("task_type", "start end interval")
assigned_task_type = collections.namedtuple("assigend_task_type", "start job index duration")

# 任务分配的变量
all_jobs = {}
machine_to_intervals = collections.defaultdict(list)

for job_id, job in enumerate(jobs_data):
    for task_id, task in enumerate(job):
        machine = task[0]
        duration = task[1]
        start_var = model.new_int_var(0 , horizon, f"start_{job_id}_{task_id}")
        end_var = model.new_int_var(0 , horizon, f"end_{job_id}_{task_id}")
        interval_var = model.new_interval_var(start_var, duration, end_var, f"interval_{job_id}_{task_id}")
        all_jobs[job_id, task_id] = task_type(start=start_var, end=end_var, interval=interval_var)
        machine_to_intervals[machine].append(interval_var)

# 约束条件
for machine in all_machines:
    model.add_no_overlap(machine_to_intervals[machine])

for job_id, job in enumerate(jobs_data):
    for task_id in range(len(job) - 1):
        model.add(all_jobs[job_id, task_id + 1].start >= all_jobs[job_id, task_id].end)

# 目标函数
ojb_var = model.new_int_var(0, horizon, "makespan")
model.add_max_equality(ojb_var, [all_jobs[job_id, len(job) - 1].end for job_id, job in enumerate(jobs_data)])
model.minimize(ojb_var)

# 调用求解器
# 日志参数必须在 solve() 之前设置（求解器启动时读取，求解完再设就来不及了）
solver = cp_model.CpSolver()
solver.parameters.log_search_progress = True
status = solver.solve(model)

# 展示结果
print(status)
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution:")
    assigned_jobs = collections.defaultdict(list)
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            assigned_jobs[machine].append(
                assigned_task_type(
                    start=solver.value(all_jobs[job_id, task_id].start),
                    job=job_id,
                    index=task_id,
                    duration=task[1],
                )
            )

    # 打印每台机器的任务安排
    output = ""
    for machine in all_machines:
        # Sort by starting time.
        assigned_jobs[machine].sort()
        sol_line_tasks = "Machine " + str(machine) + ": "
        sol_line = "           "

        for assigned_task in assigned_jobs[machine]:
            name = f"job_{assigned_task.job}_task_{assigned_task.index}"
            # add spaces to output to align columns.
            sol_line_tasks += f"{name:15}"

            start = assigned_task.start
            duration = assigned_task.duration
            sol_tmp = f"[{start},{start + duration}]"
            # add spaces to output to align columns.
            sol_line += f"{sol_tmp:15}"

        sol_line += "\n"
        sol_line_tasks += "\n"
        output += sol_line_tasks
        output += sol_line

    # Finally print the solution found.
    print(f"Optimal Schedule Length: {solver.objective_value}")
    print(output)
    print("\nStatistics")
    print(f"  - conflicts: {solver.num_conflicts}")
    print(f"  - branches : {solver.num_branches}")
    print(f"  - wall time: {solver.wall_time}s")

    # ============ 甘特图绘制 ============
    # 思路：每台机器一行（y 坐标 = 机器编号），横轴是时间，色块表示该机器上的每个任务。
    # 颜色按 job 区分：同一 job 的所有工序用同一种颜色，方便追踪"这个 job 走过了哪几台机器"。
    colors = plt.cm.tab10.colors  # matplotlib 自带的 10 种高对比度颜色

    fig, ax = plt.subplots(figsize=(10, 4))
    for machine in all_machines:
        assigned_jobs[machine].sort()  # 按开始时间排序，色块才能从左到右排列
        for assigned_task in assigned_jobs[machine]:
            start = assigned_task.start
            duration = assigned_task.duration
            job_id = assigned_task.job
            # broken_barh 画一条横在指定 y 位置的色块：
            #   [(start, duration)]  → 色块的 (x 起点, 长度)
            #   (machine - 0.4, 0.8) → (y 起点, 高度)，让色块居中落在 y=machine 这一行
            ax.broken_barh(
                [(start, duration)],
                (machine - 0.4, 0.8),
                facecolors=colors[job_id % len(colors)],
                edgecolors="black",
            )
            # 在色块中央标上 "j{job编号}t{工序编号}"，方便识别
            ax.text(
                start + duration / 2,
                machine,
                f"j{job_id}t{assigned_task.index}",
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

    # 设置坐标轴
    ax.set_yticks(range(machines_count))
    ax.set_yticklabels([f"Machine {m}" for m in all_machines])
    ax.set_xlabel("Time")
    ax.set_title(f"Job-Shop Schedule (makespan = {solver.objective_value})")
    ax.set_xlim(0, solver.objective_value + 1)
    ax.grid(axis="x", linestyle="--", alpha=0.6)

    # 保存图片并显示
    plt.tight_layout()
    # plt.savefig("gantt.png", dpi=150)
    # print("\n甘特图已保存为 gantt.png")
    plt.show()
else:
    print("No solution found.")