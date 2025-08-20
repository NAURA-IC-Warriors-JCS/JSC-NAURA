# 强化学习绘图分析工具

## 🚀 功能特性

### 核心功能
- **实时可视化训练数据** - 支持10Hz以上的高频数据刷新
- **完整训练过程展示** - 奖励曲线、损失函数、成功率、处理效率等关键指标
- **物理模型可视化** - 准确呈现TM1-TM2-TM3结构和180度机械臂运动
- **多种界面模式** - 桌面版GUI和Web版实时界面

### 物理模型特性
- **TM1 (LLA/B)** - 装载锁定腔室
- **TM2 (PM7-10)** - 处理模块7-10，包含LLC/D功能
- **TM3 (PM1-6)** - 处理模块1-6，六边形排列
- **180度机械臂** - TM2与TM3之间的机械臂运动可视化

## 📦 安装和启动

### 方法1: 使用启动脚本 (推荐)
```bash
# Windows
start_visualization.bat

# 或直接双击 start_visualization.bat 文件
```

### 方法2: 命令行启动
```bash
# 安装依赖
python run_visualization.py --install

# 创建示例数据
python run_visualization.py --sample

# 启动Web版 (推荐)
python run_visualization.py --mode web

# 启动桌面版
python run_visualization.py --mode desktop

# 同时启动两个版本
python run_visualization.py --mode both
```

## 🌐 Web版使用说明

### 访问地址
启动后访问: http://localhost:5000

### 主要功能
1. **实时监控控制**
   - 开始/停止监控按钮
   - 实时连接状态指示
   - 可调节更新频率 (1-60 Hz)

2. **训练曲线显示**
   - 累积奖励实时曲线
   - 损失函数变化趋势
   - 成功率统计
   - 处理效率监控

3. **物理模型可视化**
   - TM1-TM2-TM3设备布局
   - 180度机械臂实时运动
   - PM腔室状态监控
   - 实时角度显示

4. **数据管理**
   - 支持加载历史训练数据
   - JSON格式数据导入
   - 实时数据导出

### 数据格式要求
```json
{
  "training_history": [
    {
      "episode": 0,
      "reward": 100.5,
      "loss": 2.3,
      "success_rate": 85.2,
      "efficiency": 25.8,
      "completion_time": 45.2
    }
  ],
  "metadata": {
    "task": "task_name",
    "algorithm": "PPO",
    "total_episodes": 1000
  }
}
```

## 🖥️ 桌面版使用说明

### 主要界面
1. **控制面板**
   - 文件选择和加载
   - 实时监控开关
   - 更新频率设置

2. **多标签页显示**
   - 训练曲线标签页
   - 物理模型标签页  
   - 状态分布标签页

3. **图表功能**
   - 支持缩放和平移
   - 数据点悬停显示
   - 图表保存功能

## 📊 可视化内容详解

### 训练曲线分析
- **奖励曲线**: 显示累积奖励变化趋势和移动平均
- **损失曲线**: 监控模型训练损失的收敛情况
- **成功率**: 任务完成成功率的实时统计
- **处理效率**: 以晶圆/小时为单位的效率指标

### 物理模型展示
- **设备布局**: 精确的TM1-TM2-TM3空间布局
- **机械臂运动**: 180度旋转机械臂的实时动画
- **腔室状态**: PM1-PM10腔室的实时状态监控
- **传输路径**: 晶圆在设备间的传输路径可视化

### 状态分布分析
- **状态分布直方图**: 智能体状态的统计分布
- **动作分布**: 各类动作的选择频次统计
- **奖励分布**: 奖励值的概率密度分布
- **状态-动作热力图**: 状态与动作的关联性分析

## ⚙️ 高级配置

### 性能优化
- **更新频率**: 根据系统性能调整刷新频率
- **数据缓存**: 自动管理内存中的数据量
- **图表优化**: 禁用动画以提高性能

### 自定义设置
- **颜色主题**: 可自定义图表颜色方案
- **显示范围**: 调整图表的显示时间窗口
- **数据过滤**: 选择性显示特定类型的数据

## 🔧 技术架构

### Web版技术栈
- **后端**: Flask + Flask-SocketIO
- **前端**: HTML5 + Chart.js + Socket.IO
- **实时通信**: WebSocket协议
- **数据处理**: NumPy + JSON

### 桌面版技术栈
- **GUI框架**: Tkinter
- **图表库**: Matplotlib + Seaborn
- **数据处理**: Pandas + NumPy
- **动画**: Matplotlib Animation

## 📁 文件结构
```
DRL-d/
├── rl_visualization_tool.py      # 桌面版主程序
├── web_visualization_server.py   # Web版服务器
├── run_visualization.py          # 统一启动脚本
├── start_visualization.bat       # Windows启动脚本
├── templates/
│   └── index.html               # Web版前端界面
├── sample_data/                 # 示例数据目录
└── VISUALIZATION_README.md      # 本说明文档
```

## 🐛 常见问题

### Q: Web版无法访问？
A: 检查防火墙设置，确保5000端口未被占用

### Q: 图表显示异常？
A: 检查数据格式是否正确，确保JSON文件结构完整

### Q: 更新频率过低？
A: 降低数据量或调整缓存设置，检查系统性能

### Q: 依赖安装失败？
A: 使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`

## 📞 技术支持

如遇到问题，请检查：
1. Python版本 (推荐3.7+)
2. 依赖包完整性
3. 数据文件格式
4. 系统资源使用情况

## 🔄 更新日志

### v1.0.0
- 初始版本发布
- 支持Web版和桌面版
- 实现TM1-TM2-TM3物理模型
- 支持10Hz+高频数据刷新
- 完整的训练过程可视化

---

**开发团队**: CodeBuddy AI Assistant  
**更新时间**: 2025-08-19  
**版本**: v1.0.0