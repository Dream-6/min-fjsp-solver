# min-fjsp-solver

一个最小化的柔性作业车间调度问题（FJSP, Flexible Job-shop Scheduling Problem）求解与对比项目。

用同一个问题、同一批标准算例，对比三类方法的解质量与求解时间：

1. **贪心基线**（Greedy）—— 最简单的构造式方法，作为对照组
2. **手写元启发式**（禁忌搜索 / 大邻域搜索）—— 展示启发式设计能力
3. **精确求解**（Google OR-Tools CP-SAT）—— 工业界主流的约束规划求解器

## 项目目标

- 掌握 CP-SAT 的工业级建模方法（变量 → 约束 → 目标 → 求解参数）
- 手写并调优现代元启发式算法
- 建立"算法在标准算例上可量化对比"的实验习惯
- （Q3 扩展）Web 可视化：上传算例，交互式展示排程甘特图

## 项目进度

- [x] 建仓，环境搭建（Python 3.12 / VS Code / Git）
- [ ] 跑通 OR-Tools 官方 job-shop 示例
- [ ] 贪心基线求解器
- [ ] CP-SAT 求解器（JSP 版）
- [ ] 升级为 FJSP（机器分配决策变量）
- [ ] 禁忌搜索 / LNS 启发式
- [ ] Brandimarte Mk 算例集跑分对比
- [ ] Web 甘特图可视化

## 目录结构（规划）

```
min-fjsp-solver/
├── README.md              # 本文件
├── data/                  # 标准算例（Taillard JSP / Brandimarte Mk FJSP）
├── solvers/               # 求解器实现
│   ├── greedy.py
│   ├── heuristic.py
│   └── cpsat.py
├── experiments/           # 实验脚本与结果
│   ├── run_experiments.py
│   └── results.md
└── web/                   # （后期）可视化前端
```

## 运行方式（随进度更新）

```bash
pip install ortools
python hello_ortools.py
```

## 算例与评价标准

- **JSP**：Taillard 算例集（已知最好解，用于计算 gap）
- **FJSP**：Brandimarte Mk01-Mk10 算例集
- 指标：解的质量（相对已知最好解的 gap %）、求解耗时、随问题规模的扩展性

---
*个人学习项目，用于调度优化方向的系统性训练。进度按周更新。*
