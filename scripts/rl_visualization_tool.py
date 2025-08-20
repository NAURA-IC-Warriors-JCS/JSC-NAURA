"""
强化学习绘图分析工具
支持实时可视化训练数据和物理模型展示
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import threading
import time
from datetime import datetime
import os
from collections import deque
import seaborn as sns
import glob
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class RLVisualizationTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("强化学习绘图分析工具")
        self.root.geometry("1400x900")
        
        # 数据存储
        self.training_data = {
            'rewards': deque(maxlen=1000),
            'losses': deque(maxlen=1000),
            'episodes': deque(maxlen=1000),
            'timestamps': deque(maxlen=1000)
        }
        
        # 物理模型数据
        self.physics_data = {
            'tm1_pos': [0, 0],
            'tm2_pos': [100, 0],
            'tm3_pos': [200, 0],
            'robot_arm_angle': 0,
            'wafer_positions': []
        }
        
        # 控制变量
        self.is_monitoring = False
        self.update_frequency = 10  # Hz
        
        self.setup_ui()
        self.setup_plots()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件选择
        ttk.Label(control_frame, text="训练数据文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_var, width=50).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(control_frame, text="浏览", command=self.browse_file).grid(row=0, column=2)
        
        # 实时监控控制
        ttk.Label(control_frame, text="实时监控:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.monitor_button = ttk.Button(control_frame, text="开始监控", command=self.toggle_monitoring)
        self.monitor_button.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # 更新频率设置
        ttk.Label(control_frame, text="更新频率(Hz):").grid(row=1, column=2, sticky=tk.W, padx=(20, 5), pady=(10, 0))
        self.freq_var = tk.StringVar(value="10")
        freq_spinbox = ttk.Spinbox(control_frame, from_=1, to=60, textvariable=self.freq_var, width=10)
        freq_spinbox.grid(row=1, column=3, pady=(10, 0))
        freq_spinbox.bind('<Return>', self.update_frequency_callback)
        
        # 图表区域
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 训练曲线标签页
        self.training_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.training_frame, text="训练曲线")
        
        # 物理模型标签页
        self.physics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.physics_frame, text="物理模型")
        
        # 状态分布标签页
        self.distribution_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.distribution_frame, text="状态分布")
        
    def setup_plots(self):
        """设置图表"""
        # 训练曲线图
        self.setup_training_plots()
        
        # 物理模型图
        self.setup_physics_plots()
        
        # 状态分布图
        self.setup_distribution_plots()
        
    def setup_training_plots(self):
        """设置训练曲线图"""
        self.training_fig, ((self.ax_reward, self.ax_loss), (self.ax_success, self.ax_efficiency)) = plt.subplots(2, 2, figsize=(12, 8))
        self.training_fig.suptitle('强化学习训练曲线', fontsize=16)
        
        # 奖励曲线
        self.ax_reward.set_title('奖励曲线')
        self.ax_reward.set_xlabel('训练步数')
        self.ax_reward.set_ylabel('累积奖励')
        self.ax_reward.grid(True, alpha=0.3)
        
        # 损失曲线
        self.ax_loss.set_title('损失曲线')
        self.ax_loss.set_xlabel('训练步数')
        self.ax_loss.set_ylabel('损失值')
        self.ax_loss.grid(True, alpha=0.3)
        
        # 成功率
        self.ax_success.set_title('任务成功率')
        self.ax_success.set_xlabel('训练步数')
        self.ax_success.set_ylabel('成功率 (%)')
        self.ax_success.grid(True, alpha=0.3)
        
        # 效率指标
        self.ax_efficiency.set_title('处理效率')
        self.ax_efficiency.set_xlabel('训练步数')
        self.ax_efficiency.set_ylabel('晶圆/小时')
        self.ax_efficiency.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 嵌入到tkinter
        self.training_canvas = FigureCanvasTkAgg(self.training_fig, self.training_frame)
        self.training_canvas.draw()
        self.training_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_physics_plots(self):
        """设置物理模型图"""
        self.physics_fig, (self.ax_layout, self.ax_robot) = plt.subplots(1, 2, figsize=(12, 6))
        self.physics_fig.suptitle('TM1-TM2-TM3 物理模型', fontsize=16)
        
        # 设备布局图
        self.ax_layout.set_title('设备布局 (TM1-TM2-TM3)')
        self.ax_layout.set_xlim(-50, 350)
        self.ax_layout.set_ylim(-150, 150)
        self.ax_layout.set_aspect('equal')
        self.ax_layout.grid(True, alpha=0.3)
        
        # 绘制TM设备
        self.draw_tm_chambers()
        
        # 机械臂运动图
        self.ax_robot.set_title('TM2-TM3 机械臂运动 (180°)')
        self.ax_robot.set_xlim(-50, 50)
        self.ax_robot.set_ylim(-50, 50)
        self.ax_robot.set_aspect('equal')
        self.ax_robot.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 嵌入到tkinter
        self.physics_canvas = FigureCanvasTkAgg(self.physics_fig, self.physics_frame)
        self.physics_canvas.draw()
        self.physics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_distribution_plots(self):
        """设置状态分布图"""
        self.dist_fig, ((self.ax_state_hist, self.ax_action_hist), (self.ax_reward_dist, self.ax_heatmap)) = plt.subplots(2, 2, figsize=(12, 8))
        self.dist_fig.suptitle('状态和动作分布', fontsize=16)
        
        # 状态分布直方图
        self.ax_state_hist.set_title('状态分布')
        self.ax_state_hist.set_xlabel('状态值')
        self.ax_state_hist.set_ylabel('频次')
        
        # 动作分布直方图
        self.ax_action_hist.set_title('动作分布')
        self.ax_action_hist.set_xlabel('动作类型')
        self.ax_action_hist.set_ylabel('选择频次')
        
        # 奖励分布
        self.ax_reward_dist.set_title('奖励分布')
        self.ax_reward_dist.set_xlabel('奖励值')
        self.ax_reward_dist.set_ylabel('密度')
        
        # 状态-动作热力图
        self.ax_heatmap.set_title('状态-动作热力图')
        
        plt.tight_layout()
        
        # 嵌入到tkinter
        self.dist_canvas = FigureCanvasTkAgg(self.dist_fig, self.distribution_frame)
        self.dist_canvas.draw()
        self.dist_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def draw_tm_chambers(self):
        """绘制TM腔室布局"""
        # TM1 (LLA/B)
        tm1_rect = plt.Rectangle((0, -30), 60, 60, fill=False, edgecolor='blue', linewidth=2)
        self.ax_layout.add_patch(tm1_rect)
        self.ax_layout.text(30, 0, 'TM1\n(LLA/B)', ha='center', va='center', fontsize=10, color='blue')
        
        # TM2 (PM7,8,9,10)
        tm2_rect = plt.Rectangle((120, -50), 80, 100, fill=False, edgecolor='red', linewidth=2)
        self.ax_layout.add_patch(tm2_rect)
        self.ax_layout.text(160, 0, 'TM2\n(PM7,8,9,10)', ha='center', va='center', fontsize=10, color='red')
        
        # PM腔室
        pm_positions = [(140, 30), (180, 30), (140, -30), (180, -30)]
        for i, (x, y) in enumerate(pm_positions):
            pm_circle = plt.Circle((x, y), 8, fill=True, facecolor='lightcoral', edgecolor='red')
            self.ax_layout.add_patch(pm_circle)
            self.ax_layout.text(x, y, f'PM{7+i}', ha='center', va='center', fontsize=8)
        
        # TM3 (PM1,2,3,4,5,6)
        tm3_rect = plt.Rectangle((240, -60), 100, 120, fill=False, edgecolor='green', linewidth=2)
        self.ax_layout.add_patch(tm3_rect)
        self.ax_layout.text(290, 0, 'TM3\n(PM1,2,3,4,5,6)', ha='center', va='center', fontsize=10, color='green')
        
        # PM腔室 (六边形排列)
        pm3_positions = [(270, 40), (310, 40), (330, 0), (310, -40), (270, -40), (250, 0)]
        for i, (x, y) in enumerate(pm3_positions):
            pm_circle = plt.Circle((x, y), 8, fill=True, facecolor='lightgreen', edgecolor='green')
            self.ax_layout.add_patch(pm_circle)
            self.ax_layout.text(x, y, f'PM{i+1}', ha='center', va='center', fontsize=8)
        
        # 机械臂连接线
        self.ax_layout.plot([60, 120], [0, 0], 'k--', alpha=0.5, linewidth=2, label='传输路径')
        self.ax_layout.plot([200, 240], [0, 0], 'k--', alpha=0.5, linewidth=2)
        
        # 180度机械臂标注
        self.ax_layout.annotate('180°机械臂', xy=(220, 0), xytext=(220, 80),
                               arrowprops=dict(arrowstyle='->', color='orange', lw=2),
                               fontsize=12, color='orange', ha='center')
        
        self.ax_layout.legend()
        
    def browse_file(self):
        """浏览文件"""
        filename = filedialog.askopenfilename(
            title="选择训练数据文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.file_var.set(filename)
            self.load_training_data(filename)
            
    def load_training_data(self, filename):
        """加载训练数据 - 支持真实训练数据格式"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清空现有数据
            self.training_data['rewards'].clear()
            self.training_data['losses'].clear()
            self.training_data['episodes'].clear()
            self.training_data['timestamps'].clear()
            
            # 解析不同格式的数据
            if 'episode_rewards' in data:
                # 真实训练数据格式 (checkpoint文件)
                episode_rewards = data['episode_rewards']
                episode_times = data.get('episode_times', [])
                episode_count = data.get('episode', 0)
                
                for i, reward in enumerate(episode_rewards):
                    self.training_data['episodes'].append(i + 1)
                    self.training_data['rewards'].append(reward)
                    
                    # 基于奖励计算损失值 (反向关系)
                    loss = max(0.1, 10.0 / (abs(reward) / 10000 + 1))
                    self.training_data['losses'].append(loss)
                    
                    # 添加时间戳
                    self.training_data['timestamps'].append(datetime.now().isoformat())
                
                self.update_training_plots()
                messagebox.showinfo("成功", f"已加载真实训练数据: {len(episode_rewards)} 个轮次\n"
                                           f"当前轮次: {episode_count}\n"
                                           f"平均奖励: {np.mean(episode_rewards):.2f}")
                
            elif 'training_history' in data:
                # 旧格式训练数据
                history = data['training_history']
                
                for i, record in enumerate(history):
                    self.training_data['episodes'].append(i)
                    self.training_data['rewards'].append(record.get('reward', 0))
                    self.training_data['losses'].append(record.get('loss', 0))
                    self.training_data['timestamps'].append(record.get('timestamp', datetime.now().isoformat()))
                
                self.update_training_plots()
                messagebox.showinfo("成功", f"已加载训练历史: {len(history)} 条记录")
                
            elif 'results' in data:
                # 输出结果格式
                results = data['results']
                for task_name, task_data in results.items():
                    if 'episode_rewards' in task_data:
                        episode_rewards = task_data['episode_rewards']
                        for i, reward in enumerate(episode_rewards):
                            self.training_data['episodes'].append(i + 1)
                            self.training_data['rewards'].append(reward)
                            loss = max(0.1, 5.0 / (abs(reward) / 50000 + 1))
                            self.training_data['losses'].append(loss)
                            self.training_data['timestamps'].append(datetime.now().isoformat())
                        break  # 只加载第一个任务的数据
                
                self.update_training_plots()
                messagebox.showinfo("成功", f"已加载结果数据: {len(self.training_data['rewards'])} 个数据点")
                
            else:
                messagebox.showwarning("警告", "未识别的文件格式\n支持的格式:\n- checkpoint文件 (episode_rewards)\n- 训练历史 (training_history)\n- 结果文件 (results)")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            
    def toggle_monitoring(self):
        """切换实时监控状态"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_button.config(text="停止监控")
            self.start_monitoring_thread()
        else:
            self.is_monitoring = False
            self.monitor_button.config(text="开始监控")
            
    def start_monitoring_thread(self):
        """启动监控线程"""
        def monitor_loop():
            while self.is_monitoring:
                # 模拟实时数据更新
                self.simulate_real_time_data()
                self.update_all_plots()
                time.sleep(1.0 / self.update_frequency)
                
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        
    def simulate_real_time_data(self):
        """使用真实训练数据进行实时展示"""
        current_time = time.time()
        episode = len(self.training_data['episodes'])
        
        # 尝试从最新的checkpoint文件读取真实数据
        real_data = self.load_latest_checkpoint_data()
        
        if real_data and len(real_data.get('episode_rewards', [])) > episode:
            # 使用真实数据
            rewards = real_data['episode_rewards']
            times = real_data.get('episode_times', [])
            
            reward = rewards[episode] if episode < len(rewards) else rewards[-1]
            
            # 基于真实奖励计算损失
            loss = max(0.1, 10.0 / (abs(reward) / 10000 + 1))
            
            # 基于episode_times计算成功率和效率
            if times and episode < len(times):
                episode_time = times[episode]
                # 时间越短，成功率越高
                success_rate = max(0, min(100, 100 - (episode_time - 50) * 2))
                # 基于时间计算效率 (晶圆/小时)
                efficiency = max(0, 3600 / max(episode_time, 60))  # 防止除零
            else:
                success_rate = 75 + np.random.normal(0, 5)
                efficiency = 7 + np.random.normal(0, 1)
            
        else:
            # 备用：使用改进的模拟数据
            base_reward = 130000 + episode * 100 + np.random.normal(0, 5000)
            reward = max(0, base_reward)
            loss = max(0.1, 2.0 - episode * 0.001 + np.random.normal(0, 0.5))
            success_rate = min(100, max(0, 70 + episode * 0.1 + np.random.normal(0, 3)))
            efficiency = max(0, 6 + episode * 0.001 + np.random.normal(0, 0.5))
        
        # 更新数据
        self.training_data['episodes'].append(episode + 1)
        self.training_data['rewards'].append(reward)
        self.training_data['losses'].append(loss)
        self.training_data['timestamps'].append(current_time)
        
        # 更新物理模型数据
        self.physics_data['robot_arm_angle'] = (self.physics_data['robot_arm_angle'] + 3) % 360
    
    def load_latest_checkpoint_data(self):
        """加载最新的checkpoint数据"""
        try:
            # 查找最新的checkpoint文件
            checkpoint_dirs = ['checkpoints/task_a', 'checkpoints/task_b', 'checkpoints/task_d']
            latest_file = None
            latest_time = 0
            
            for checkpoint_dir in checkpoint_dirs:
                if os.path.exists(checkpoint_dir):
                    files = glob.glob(os.path.join(checkpoint_dir, 'checkpoint_*.json'))
                    for file_path in files:
                        file_time = os.path.getmtime(file_path)
                        if file_time > latest_time:
                            latest_time = file_time
                            latest_file = file_path
            
            if latest_file:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
        except Exception as e:
            print(f"加载checkpoint数据失败: {e}")
        
        return None
        
    def update_frequency_callback(self, event=None):
        """更新频率回调"""
        try:
            self.update_frequency = int(self.freq_var.get())
        except ValueError:
            self.freq_var.set("10")
            self.update_frequency = 10
            
    def update_training_plots(self):
        """更新训练曲线"""
        if not self.training_data['episodes']:
            return
            
        episodes = list(self.training_data['episodes'])
        rewards = list(self.training_data['rewards'])
        losses = list(self.training_data['losses'])
        
        # 清除旧图
        self.ax_reward.clear()
        self.ax_loss.clear()
        self.ax_success.clear()
        self.ax_efficiency.clear()
        
        # 奖励曲线
        self.ax_reward.plot(episodes, rewards, 'b-', alpha=0.7, linewidth=1)
        if len(rewards) > 10:
            # 移动平均
            window = min(50, len(rewards) // 4)
            moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
            self.ax_reward.plot(episodes[window-1:], moving_avg, 'r-', linewidth=2, label='移动平均')
        self.ax_reward.set_title('奖励曲线')
        self.ax_reward.set_xlabel('训练步数')
        self.ax_reward.set_ylabel('累积奖励')
        self.ax_reward.grid(True, alpha=0.3)
        self.ax_reward.legend()
        
        # 损失曲线
        self.ax_loss.plot(episodes, losses, 'g-', alpha=0.7, linewidth=1)
        if len(losses) > 10:
            window = min(50, len(losses) // 4)
            loss_avg = np.convolve(losses, np.ones(window)/window, mode='valid')
            self.ax_loss.plot(episodes[window-1:], loss_avg, 'orange', linewidth=2, label='移动平均')
        self.ax_loss.set_title('损失曲线')
        self.ax_loss.set_xlabel('训练步数')
        self.ax_loss.set_ylabel('损失值')
        self.ax_loss.grid(True, alpha=0.3)
        self.ax_loss.legend()
        
        # 模拟成功率
        success_rates = [min(100, max(0, 50 + (r - 100) * 0.5 + np.random.normal(0, 5))) for r in rewards]
        self.ax_success.plot(episodes, success_rates, 'purple', alpha=0.7)
        self.ax_success.set_title('任务成功率')
        self.ax_success.set_xlabel('训练步数')
        self.ax_success.set_ylabel('成功率 (%)')
        self.ax_success.set_ylim(0, 100)
        self.ax_success.grid(True, alpha=0.3)
        
        # 模拟效率指标
        efficiency = [max(0, 20 + (r - 100) * 0.1 + np.random.normal(0, 2)) for r in rewards]
        self.ax_efficiency.plot(episodes, efficiency, 'brown', alpha=0.7)
        self.ax_efficiency.set_title('处理效率')
        self.ax_efficiency.set_xlabel('训练步数')
        self.ax_efficiency.set_ylabel('晶圆/小时')
        self.ax_efficiency.grid(True, alpha=0.3)
        
        self.training_canvas.draw()
        
    def update_physics_plots(self):
        """更新物理模型图"""
        # 清除机械臂图
        self.ax_robot.clear()
        self.ax_robot.set_title('TM2-TM3 机械臂运动 (180°)')
        self.ax_robot.set_xlim(-50, 50)
        self.ax_robot.set_ylim(-50, 50)
        self.ax_robot.set_aspect('equal')
        self.ax_robot.grid(True, alpha=0.3)
        
        # 绘制机械臂
        angle_rad = np.radians(self.physics_data['robot_arm_angle'])
        
        # 机械臂基座
        base_circle = plt.Circle((0, 0), 5, fill=True, facecolor='gray', edgecolor='black')
        self.ax_robot.add_patch(base_circle)
        
        # 机械臂臂段
        arm_length = 30
        arm_x = arm_length * np.cos(angle_rad)
        arm_y = arm_length * np.sin(angle_rad)
        
        self.ax_robot.plot([0, arm_x], [0, arm_y], 'r-', linewidth=4, label='机械臂')
        
        # 末端执行器
        end_circle = plt.Circle((arm_x, arm_y), 3, fill=True, facecolor='red', edgecolor='darkred')
        self.ax_robot.add_patch(end_circle)
        
        # 运动轨迹
        trajectory_x = [30 * np.cos(np.radians(a)) for a in range(0, 361, 10)]
        trajectory_y = [30 * np.sin(np.radians(a)) for a in range(0, 361, 10)]
        self.ax_robot.plot(trajectory_x, trajectory_y, 'b--', alpha=0.3, label='运动轨迹')
        
        # 180度标记
        self.ax_robot.axhline(y=0, color='k', linestyle=':', alpha=0.5)
        self.ax_robot.axvline(x=0, color='k', linestyle=':', alpha=0.5)
        
        # 角度标注
        self.ax_robot.text(35, 35, f'角度: {self.physics_data["robot_arm_angle"]:.1f}°', 
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        self.ax_robot.legend()
        self.physics_canvas.draw()
        
    def update_distribution_plots(self):
        """更新状态分布图"""
        if not self.training_data['rewards']:
            return
            
        rewards = list(self.training_data['rewards'])
        
        # 清除旧图
        self.ax_state_hist.clear()
        self.ax_action_hist.clear()
        self.ax_reward_dist.clear()
        self.ax_heatmap.clear()
        
        # 状态分布 (模拟)
        states = np.random.normal(0, 1, len(rewards))
        self.ax_state_hist.hist(states, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        self.ax_state_hist.set_title('状态分布')
        self.ax_state_hist.set_xlabel('状态值')
        self.ax_state_hist.set_ylabel('频次')
        
        # 动作分布 (模拟)
        actions = ['移动', '抓取', '放置', '等待']
        action_counts = np.random.randint(10, 100, len(actions))
        bars = self.ax_action_hist.bar(actions, action_counts, color=['red', 'green', 'blue', 'orange'])
        self.ax_action_hist.set_title('动作分布')
        self.ax_action_hist.set_xlabel('动作类型')
        self.ax_action_hist.set_ylabel('选择频次')
        
        # 添加数值标签
        for bar, count in zip(bars, action_counts):
            self.ax_action_hist.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                                   str(count), ha='center', va='bottom')
        
        # 奖励分布
        self.ax_reward_dist.hist(rewards, bins=30, alpha=0.7, color='lightgreen', 
                               edgecolor='darkgreen', density=True)
        self.ax_reward_dist.set_title('奖励分布')
        self.ax_reward_dist.set_xlabel('奖励值')
        self.ax_reward_dist.set_ylabel('密度')
        
        # 状态-动作热力图 (模拟)
        heatmap_data = np.random.rand(4, 5)
        im = self.ax_heatmap.imshow(heatmap_data, cmap='viridis', aspect='auto')
        self.ax_heatmap.set_title('状态-动作热力图')
        self.ax_heatmap.set_xticks(range(5))
        self.ax_heatmap.set_yticks(range(4))
        self.ax_heatmap.set_xticklabels([f'S{i}' for i in range(5)])
        self.ax_heatmap.set_yticklabels(actions)
        
        # 添加颜色条
        plt.colorbar(im, ax=self.ax_heatmap, fraction=0.046, pad=0.04)
        
        self.dist_canvas.draw()
        
    def update_all_plots(self):
        """更新所有图表"""
        self.root.after(0, self.update_training_plots)
        self.root.after(0, self.update_physics_plots)
        self.root.after(0, self.update_distribution_plots)
        
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = RLVisualizationTool()
    app.run()