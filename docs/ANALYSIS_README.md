# 强化学习训练结果分析工具

本工具套件用于分析通过 `train_rl_fixed.py` 训练的强化学习结果，提供全面的性能评估、可视化和物理模型仿真。

## 🚀 快速开始

### 1. 安装依赖
```bash
python install_analysis_deps.py
```

### 2. 一键分析
```bash
python quick_analysis.py
```

## 📊 功能特性

### 训练曲线分析
- ✅ 累积奖励变化曲线
- ✅ 损失函数变化曲线  
- ✅ 任务成功率趋势
- ✅ 完成时间优化曲线

### 多任务性能对比
- ✅ 最终性能对比
- ✅ 收敛速度分析
- ✅ 学习效率评估
- ✅ 稳定性分析

### 动态物理模型
- ✅ 晶圆厂布局可视化
- ✅ 机械臂运动仿真
- ✅ 腔室状态监控
- ✅ 实时物理参数显示

### 统计报告
- ✅ 详细性能统计
- ✅ 收敛点分析
- ✅ 改进建议
- ✅ Markdown格式报告

## 🛠️ 使用方法

### 完整分析
```bash
# 分析所有任务 (a, b, d)
python run_analysis.py --mode all

# 分析指定任务
python run_analysis.py --mode all --tasks a b

# 指定输出目录
python run_analysis.py --mode all --output-dir my_analysis
```

### 分模块分析
```bash
# 仅训练曲线分析
python run_analysis.py --mode analysis

# 仅物理仿真
python run_analysis.py --mode physics

# 仅生成报告
python run_analysis.py --mode report
```

### 单任务详细分析
```bash
# 分析单个任务
python analyze_training.py --single-task a

# 自定义检查点目录
python analyze_training.py --single-task a --checkpoint-dir my_checkpoints
```

## 📁 输出文件说明

分析完成后，在 `analysis/` 目录下会生成以下文件：

### 图像文件
- `training_curves_task_a.png` - 任务A训练曲线
- `training_curves_task_b.png` - 任务B训练曲线  
- `training_curves_task_d.png` - 任务D训练曲线
- `performance_comparison.png` - 多任务性能对比
- `dynamic_model_task_*.png` - 动态物理模型截图

### 报告文件
- `training_report.txt` - 详细统计报告
- `comprehensive_report.md` - 综合分析报告

## 🔧 高级配置

### 自定义分析参数
```python
# 在 utils/rl_analyzer.py 中修改
class RLAnalyzer:
    def __init__(self, checkpoint_dir="checkpoints", output_dir="analysis"):
        # 自定义参数
        self.convergence_threshold = 80  # 收敛阈值
        self.smoothing_window = 10       # 平滑窗口
```

### 物理模型参数
```python
# 在 utils/physics_model.py 中修改
class WaferPhysicsModel:
    def __init__(self, wafer_radius=0.15):
        self.temperature = 25.0    # 初始温度
        self.pressure = 1.0        # 初始压力
        # 其他物理参数...
```

## 📈 分析指标说明

### 关键性能指标 (KPI)
1. **累积奖励**: 衡量智能体整体表现
2. **成功率**: 任务完成的成功百分比
3. **收敛轮次**: 达到稳定性能所需的训练轮次
4. **完成时间**: 任务执行效率指标

### 收敛判断标准
- 成功率达到80%以上
- 连续10个episode保持稳定
- 奖励方差小于阈值

## 🎯 使用场景

### 训练过程监控
```bash
# 训练完成后立即分析
python train_rl_fixed.py --task a --episodes 2000
python quick_analysis.py
```

### 超参数调优
```bash
# 对比不同超参数的训练结果
python run_analysis.py --checkpoint-dir checkpoints_lr001
python run_analysis.py --checkpoint-dir checkpoints_lr01 --output-dir analysis_lr01
```

### 论文图表生成
```bash
# 生成高质量图表用于论文
python run_analysis.py --mode analysis
# 图表保存在 analysis/ 目录，DPI=300
```

## 🐛 故障排除

### 常见问题

1. **没有找到训练数据**
   ```
   错误: 任务 a 没有找到检查点数据
   解决: 确保先运行 train_rl_fixed.py 生成训练数据
   ```

2. **依赖包缺失**
   ```
   ModuleNotFoundError: No module named 'matplotlib'
   解决: 运行 python install_analysis_deps.py
   ```

3. **内存不足**
   ```
   解决: 减少分析的episode数量或分批处理
   ```

### 调试模式
```bash
# 启用详细输出
python run_analysis.py --mode analysis --verbose

# 检查数据完整性
python -c "from utils.rl_analyzer import RLAnalyzer; RLAnalyzer().load_checkpoint_data('a')"
```

## 📚 扩展开发

### 添加新的分析指标
```python
# 在 RLAnalyzer 类中添加新方法
def analyze_custom_metric(self, checkpoints):
    # 自定义分析逻辑
    pass
```

### 自定义可视化
```python
# 在 physics_model.py 中扩展可视化
def custom_visualization(self):
    # 自定义可视化逻辑
    pass
```

## 📞 技术支持

如有问题，请检查：
1. Python版本 >= 3.7
2. 所有依赖包已正确安装
3. 训练数据文件完整性
4. 文件路径权限

---

**版本**: 1.0.0  
**更新日期**: 2025-01-19  
**兼容性**: Python 3.7+, Windows/Linux/macOS