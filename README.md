# DRL-d: Deep Reinforcement Learning for Semiconductor Manufacturing

[![CI](https://github.com/yourusername/DRL-d/workflows/CI/badge.svg)](https://github.com/yourusername/DRL-d/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个基于深度强化学习的半导体制造调度优化系统，专注于晶圆制造过程中的智能调度和资源优化。

## 🚀 特性

- **多智能体强化学习**: 支持多个智能体协同工作
- **实时可视化**: 提供Web界面和桌面GUI工具
- **灵活配置**: 支持多种设备和工艺配置
- **性能分析**: 内置训练过程分析和可视化工具
- **模块化设计**: 易于扩展和定制

## 📁 项目结构

```
DRL-d/
├── src/                    # 源代码
│   ├── agents/            # 智能体模块
│   ├── environment/       # 环境模块
│   ├── training/          # 训练模块
│   ├── utils/             # 工具模块
│   └── config/            # 配置模块
├── data/                  # 数据文件
│   ├── checkpoints/       # 训练检查点
│   └── output/            # 输出结果
├── web/                   # Web界面
│   ├── templates/         # HTML模板
│   └── static/            # 静态资源
├── scripts/               # 脚本文件
├── examples/              # 示例代码
├── tests/                 # 测试文件
├── docs/                  # 文档
└── .github/               # GitHub配置
```

## 🛠️ 安装

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/DRL-d.git
cd DRL-d
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -e .
```

或安装开发版本：
```bash
pip install -e .[dev]
```

## 🎯 快速开始

### 1. 基础训练

```bash
# 运行基础训练
python src/main.py

# 或使用命令行工具
drl-d-train
```

### 2. 可视化分析

```bash
# 启动Web可视化界面
python web/web_visualization_server.py

# 或使用桌面GUI工具
python examples/rl_visualization_tool.py
```

### 3. 训练分析

```bash
# 分析训练结果
python scripts/analyze_training.py

# 或使用命令行工具
drl-d-analyze
```

## 📊 功能模块

### 智能体 (Agents)
- `BaseAgent`: 基础智能体类
- `WaferAgent`: 晶圆处理智能体
- `ChamberAgent`: 腔室管理智能体
- `RobotAgent`: 机械臂控制智能体

### 环境 (Environment)
- `FabEnvironment`: 制造环境模拟
- `Chamber`: 腔室模型
- `RobotArm`: 机械臂模型
- `Wafer`: 晶圆模型

### 训练 (Training)
- `MultiAgentTrainer`: 多智能体训练器
- 支持分布式训练
- 自动检查点保存

### 可视化 (Visualization)
- Web界面实时监控
- 训练曲线可视化
- 性能指标分析
- 交互式数据探索

## 🔧 配置

主要配置文件位于 `src/config/` 目录：

- `equipment_config.py`: 设备配置
- `process_config.py`: 工艺配置  
- `task_config.py`: 任务配置

## 📈 性能指标

系统支持多种性能指标：

- **奖励函数**: 训练过程中的累积奖励
- **成功率**: 任务完成成功率
- **处理时间**: 平均处理时间
- **资源利用率**: 设备利用效率

## 🧪 测试

运行测试：
```bash
pytest tests/
```

运行覆盖率测试：
```bash
pytest --cov=src tests/
```

## 📚 文档

详细文档请查看 `docs/` 目录：

- [可视化指南](docs/RL_VISUALIZATION_GUIDE.md)
- [分析说明](docs/ANALYSIS_README.md)
- [Web界面说明](docs/VISUALIZATION_README.md)

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和研究人员。

## 📞 联系

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/yourusername/DRL-d/issues)
- 邮箱: naura_ic_warriors@163.com

---


⭐ 如果这个项目对您有帮助，请给我们一个星标！
