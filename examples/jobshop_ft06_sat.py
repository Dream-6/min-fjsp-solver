# https://developers.google.com/optimization/scheduling/job_shop
# https://github.com/google/or-tools/tree/stable/examples/python

import collections
from ortools.sat.python import cp_model

# 定义数据
jobs_data = [
    [(0, 3), (1, 2), (2, 2)],    # job0
    [(0, 2), (2, 1), (1, 4)],     # job1
    [(1, 4), (2, 3)]              # job2
]
machines_count = 1+ max(task[0] for job in jobs_data for task in job) #
all_machines = range(machines_count)

# horizon设置为所有任务的总时间长度
horizon = sum(task[1] for job in jobs_data for task in job)

# 建模
model = cp_model.CpModel() 

# 定义变量
# 我没太理解这里，是创建了什么的元组？不熟悉下面这个nametuple
task_type = collections.namedtuple("task_type", "start end interval")
assigned_task_type = collections.namedtuple(
    "assigned_task_type", "start job index duration"
)
# print(task_type)
# print(assigned_task_type)

# 创建任务时间间隔，并添加给对应的机器
all_tasks = {}
machine_to_intervals = collections.defaultdict(list)

for job_id, job in enumerate(jobs_data):
    for task_id, task in enumerate(job):
        machine = task[0]
        duration = task[1]
        suffix = "_%i_%i" % (job_id, task_id) 
        start_var = model.NewIntVar(0, horizon, "start" + suffix) # 开始时间是整数
        end_var = model.NewIntVar(0, horizon, "end" + suffix) # 结束时间也是整数
        interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                            "interval" + suffix) # 区间变量：任务的开始时间，持续时间，结束时间
        all_tasks[job_id, task_id] = task_type(
            start=start_var, end=end_var, interval=interval_var
        )
        machine_to_intervals[machine].append(interval_var)


# 定义约束
# print(all_tasks)

# (job_id, task_id)的持续时间，在同一台机器上时，不重叠
for machine in all_machines:
    model.add_no_overlap(machine_to_intervals[machine])

# 同1个job的多个task的时序约束
for job_id, job in enumerate(jobs_data):
    for task_id in range(len(job) - 1):
        model.add(
            all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end
        )

# 目标函数
obj_var = model.new_int_var(0, horizon, "makespan")
model.add_max_equality(
    obj_var,
    [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(jobs_data)],
) # obj_var >= max(所有job的最后一个task的结束时间)
model.minimize(obj_var)

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
                    start=solver.value(all_tasks[job_id, task_id].start),
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
else:
    print("No solution found.")