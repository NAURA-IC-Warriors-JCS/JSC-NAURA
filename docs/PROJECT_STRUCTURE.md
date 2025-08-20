# 项目结构说明

## 📁 DRL-d 项目结构

```
DRL-d/
├── 📄 README.md                    # 项目主文档
├── 📄 LICENSE                      # MIT许可证
├── 📄 CONTRIBUTING.md              # 贡献指南
├── 📄 requirements.txt             # Python依赖
├── 📄 setup.py                     # 安装配置
├── 📄 .gitignore                   # Git忽略文件
│
├── 📂 src/                         # 源代码目录
│   ├── 📄 __init__.py             # 包初始化
│   ├── 📄 main.py                 # 主程序入口
│   ├── 📄 train_rl.py             # 训练脚本
│   ├── 📄 train_rl_fixed.py       # 修复版训练脚本
│   │
│   ├── 📂 agents/                  # 智能体模块
│   │   ├── 📄 base_agent.py       # 基础智能体
│   │   ├── 📄 wafer_agent.py      # 晶圆智能体
│   │   ├── 📄 chamber_agent.py    # 腔室智能体
│   │   └── 📄 robot_agent.py      # 机械臂智能体
│   │
│   ├── 📂 environment/             # 环境模块
│   │   ├── 📄 fab_environment.py  # 制造环境
│   │   ├── 📄 chamber.py          # 腔室模型
│   │   ├── 📄 robot_arm.py        # 机械臂模型
│   │   └── 📄 wafer.py            # 晶圆模型
│   │
│   ├── 📂 training/                # 训练模块
│   │   ├── 📄 multi_agent_trainer.py        # 多智能体训练器
│   │   └── 📄 multi_agent_trainer_fixed.py  # 修复版训练器
│   │
│   ├── 📂 utils/                   # 工具模块
│   │   ├── 📄 rl_analyzer.py      # 强化学习分析器
│   │   ├── 📄 physics_model.py    # 物理模型
│   │   ├── 📄 real_data_loader.py # 真实数据加载器
│   │   ├── 📄 visualization.py    # 可视化工具
│   │   └── 📄 validator.py        # 验证器
│   │
│   └── 📂 config/                  # 配置模块
│       ├── 📄 equipment_config.py # 设备配置
│       ├── 📄 process_config.py   # 工艺配置
│       └── 📄 task_config.py      # 任务配置
│
├── 📂 data/                        # 数据目录
│   ├── 📂 checkpoints/             # 训练检查点
│   │   ├── 📂 task_a/             # 任务A检查点
│   │   ├── 📂 task_b/             # 任务B检查点
│   │   └── 📂 task_d/             # 任务D检查点
│   ├── 📂 output/                  # 输出结果
│   └── 📂 analysis/                # 分析结果
│
├── 📂 web/                         # Web界面
│   ├── 📄 *.html                  # HTML模板
│   └── 📄 app.js                  # JavaScript文件
│
├── 📂 scripts/                     # 脚本文件
│   ├── 📄 analyze_training.py     # 训练分析脚本
│   ├── 📄 generate_reward_plots.py # 奖励图表生成
│   ├── 📄 run_analysis.py         # 运行分析
│   ├── 📄 web_visualization_*.py  # Web可视化服务器
│   └── 📄 ...                     # 其他脚本
│
├── 📂 examples/                    # 示例代码
│   ├── 📄 rl_visualization_tool.py # 可视化工具示例
│   └── 📄 ...                     # 其他示例
│
├── 📂 tests/                       # 测试文件
│   ├── 📄 __init__.py             # 测试包初始化
│   ├── 📄 test_basic.py           # 基础测试
│   └── 📄 ...                     # 其他测试
│
├── 📂 docs/                        # 文档目录
│   ├── 📄 ANALYSIS_README.md      # 分析文档
│   ├── 📄 VISUALIZATION_README.md # 可视化文档
│   └── 📄 PROJECT_STRUCTURE.md    # 项目结构说明
│
└── 📂 .github/                     # GitHub配置
    └── 📂 workflows/               # CI/CD工作流
        └── 📄 ci.yml              # 持续集成配置
```

## 🎯 主要模块说明

### 源代码 (src/)
- **agents/**: 包含各种智能体的实现
- **environment/**: 制造环境和设备模型
- **training/**: 训练算法和流程
- **utils/**: 通用工具和辅助函数
- **config/**: 配置文件和参数设置

### 数据 (data/)
- **checkpoints/**: 训练过程中保存的模型检查点
- **output/**: 训练结果和生成的图表
- **analysis/**: 分析结果和报告

### Web界面 (web/)
- HTML模板和静态资源
- 实时监控和可视化界面

### 脚本 (scripts/)
- 各种实用脚本和工具
- 训练、分析、可视化脚本

### 示例 (examples/)
- 使用示例和演示代码
- 可视化工具和测试程序

### 测试 (tests/)
- 单元测试和集成测试
- 确保代码质量和功能正确性

### 文档 (docs/)
- 详细的使用说明和API文档
- 项目架构和设计文档

## 🚀 快速开始

1. **安装依赖**:
   ```bash
   pip install -e .
   ```

2. **运行训练**:
   ```bash
   python src/main.py
   ```

3. **启动可视化**:
   ```bash
   python scripts/web_visualization_server.py
   ```

4. **运行测试**:
   ```bash
   pytest tests/
   ```

## 📝 开发指南

- 新功能开发请在相应的模块目录下添加文件
- 测试文件请放在 `tests/` 目录下
- 文档更新请修改 `docs/` 目录下的相关文件
- 脚本工具请放在 `scripts/` 目录下

## 🔧 配置说明

主要配置文件位于 `src/config/` 目录：
- `equipment_config.py`: 设备参数配置
- `process_config.py`: 工艺流程配置
- `task_config.py`: 任务和调度配置