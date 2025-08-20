#!/usr/bin/env python3
"""
实际强化学习训练并生成奖励函数图表
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
from environment.fab_environment import FabEnvironment
from agents.wafer_agent_fixed import WaferAgent
from training.multi_agent_trainer_fixed import MultiAgentTrainer
from config import task_config

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class RealTimeTrainingPlotter:
    def __init__(self, task_name, output_dir="output"):
        self.task_name = task_name
        self.output_dir = output_dir
        self.training_data = {
            'episodes': [],
            'episode_rewards': [],
            'avg_rewards': [],
            'best_rewards': [],
            'episode_times': [],
            'losses': []
        }
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def add_episode_data(self, episode, reward, episode_time, loss=None):
        """添加单次训练数据"""
        self.training_data['episodes'].append(episode)
        self.training_data['episode_rewards'].append(reward)
        self.training_data['episode_times'].append(episode_time)
        
        # 计算移动平均奖励
        window_size = min(10, len(self.training_data['episode_rewards']))
        recent_rewards = self.training_data['episode_rewards'][-window_size:]
        avg_reward = np.mean(recent_rewards)
        self.training_data['avg_rewards'].append(avg_reward)
        
        # 更新最佳奖励
        if not self.training_data['best_rewards']:
            self.training_data['best_rewards'].append(reward)
        else:
            best_so_far = max(self.training_data['best_rewards'][-1], reward)
            self.training_data['best_rewards'].append(best_so_far)
        
        if loss is not None:
            self.training_data['losses'].append(loss)
    
    def create_training_plot(self, save_final=False):
        """创建训练过程图表"""
        if not self.training_data['episodes']:
            return None
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        suffix = "最终" if save_final else "实时"
        fig.suptitle(f'{self.task_name.upper()} {suffix}训练过程奖励函数分析', fontsize=16, fontweight='bold')
        
        episodes = self.training_data['episodes']
        episode_rewards = self.training_data['episode_rewards']
        avg_rewards = self.training_data['avg_rewards']
        best_rewards = self.training_data['best_rewards']
        episode_times = self.training_data['episode_times']
        
        # 1. 奖励曲线（左侧纵坐标）和成功率（右侧纵坐标）
        ax1_twin = ax1.twinx()
        
        # 奖励曲线
        line1 = ax1.plot(episodes, episode_rewards, 'lightblue', alpha=0.6, linewidth=1, label='单次奖励')
        line2 = ax1.plot(episodes, avg_rewards, 'b-', linewidth=2.5, label='平均奖励')
        line3 = ax1.plot(episodes, best_rewards, 'r-', linewidth=2.5, label='最佳奖励')
        
        # 成功率（基于处理时间）
        if len(episode_times) > 10:
            # 计算成功率：处理时间低于中位数的比例
            median_time = np.median(episode_times)
            success_rates = []
            window_size = 10
            
            for i in range(len(episode_times)):
                start_idx = max(0, i - window_size + 1)
                window_times = episode_times[start_idx:i+1]
                success_rate = (np.array(window_times) <= median_time).mean() * 100
                success_rates.append(success_rate)
            
            line4 = ax1_twin.plot(episodes, success_rates, 'g-', linewidth=2, label='成功率')
            ax1_twin.set_ylabel('成功率 (%)', color='g')
            ax1_twin.tick_params(axis='y', labelcolor='g')
            ax1_twin.set_ylim(0, 100)
        
        # 添加数值标注
        if episodes:
            current_avg = avg_rewards[-1]
            current_best = best_rewards[-1]
            current_episode = episodes[-1]
            success_rate_final = success_rates[-1] if 'success_rates' in locals() and success_rates else 0
            
            ax1.text(0.02, 0.98, f'当前轮次: {current_episode}\n平均奖励: {current_avg:.1f}\n最佳奖励: {current_best:.1f}\n成功率: {success_rate_final:.1f}%', 
                    transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        ax1.set_title('奖励函数训练曲线与成功率')
        ax1.set_xlabel('训练轮次')
        ax1.set_ylabel('奖励值', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1.grid(True, alpha=0.3)
        
        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')
        
        # 2. 处理效率分析
        if episode_times:
            # 计算效率：晶圆/小时
            efficiency_rates = []
            for time_sec in episode_times:
                time_hours = time_sec / 3600
                efficiency = 1 / time_hours if time_hours > 0 else 0
                efficiency_rates.append(efficiency)
            
            ax2.plot(episodes, efficiency_rates, 'brown', linewidth=2, alpha=0.8, label='处理效率')
            
            # 添加移动平均
            if len(efficiency_rates) > 10:
                window = min(20, len(efficiency_rates) // 4)
                eff_avg = np.convolve(efficiency_rates, np.ones(window)/window, mode='valid')
                ax2.plot(episodes[window-1:], eff_avg, 'darkred', linewidth=3, label='效率移动平均')
            
            ax2.set_title('处理效率分析')
            ax2.set_xlabel('训练轮次')
            ax2.set_ylabel('晶圆/小时')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            # 显示效率统计
            if efficiency_rates:
                final_efficiency = efficiency_rates[-1]
                avg_efficiency = np.mean(efficiency_rates)
                ax2.text(0.02, 0.98, f'当前效率: {final_efficiency:.2f}\n平均效率: {avg_efficiency:.2f}', 
                        transform=ax2.transAxes, verticalalignment='top',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
        
        # 3. 奖励分布分析
        if len(episode_rewards) > 10:
            ax3.hist(episode_rewards, bins=30, alpha=0.7, color='skyblue', edgecolor='black', density=True)
            ax3.axvline(np.mean(episode_rewards), color='red', linestyle='--', linewidth=2, 
                       label=f'均值: {np.mean(episode_rewards):.1f}')
            ax3.axvline(np.median(episode_rewards), color='green', linestyle='--', linewidth=2, 
                       label=f'中位数: {np.median(episode_rewards):.1f}')
            
            # 显示分布统计
            std_reward = np.std(episode_rewards)
            ax3.text(0.02, 0.98, f'标准差: {std_reward:.1f}\n变异系数: {std_reward/np.mean(episode_rewards):.3f}', 
                    transform=ax3.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
            
            ax3.set_title('奖励分布分析')
            ax3.set_xlabel('奖励值')
            ax3.set_ylabel('密度')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. 训练统计和进度
        ax4.axis('off')
        
        if episodes:
            total_episodes = len(episodes)
            initial_avg = avg_rewards[0] if avg_rewards else 0
            current_avg = avg_rewards[-1] if avg_rewards else 0
            improvement_pct = ((current_avg - initial_avg) / initial_avg * 100) if initial_avg != 0 else 0
            
            # 计算训练稳定性
            recent_rewards = avg_rewards[-20:] if len(avg_rewards) >= 20 else avg_rewards
            stability = np.std(recent_rewards) if len(recent_rewards) > 1 else 0
            
            # 计算平均处理时间
            avg_time = np.mean(episode_times) if episode_times else 0
            min_time = min(episode_times) if episode_times else 0
            
            stats_text = f"""实际训练统计信息:

总训练轮次: {total_episodes}
初始平均奖励: {initial_avg:.1f}
当前平均奖励: {current_avg:.1f}
性能提升: {improvement_pct:.1f}%

最佳奖励: {max(best_rewards) if best_rewards else 0:.1f}
最低奖励: {min(episode_rewards) if episode_rewards else 0:.1f}
奖励标准差: {np.std(episode_rewards) if episode_rewards else 0:.1f}

平均处理时间: {avg_time:.1f}秒
最短处理时间: {min_time:.1f}秒
近期稳定性: {stability:.1f}

训练任务: {self.task_name}
训练状态: {'已完成' if save_final else '进行中'}"""
            
            ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, fontsize=11,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor="lightblue", alpha=0.8))
        
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix_name = "final" if save_final else "live"
        filename = f"actual_training_{self.task_name}_{suffix_name}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ {'最终' if save_final else '实时'}训练图表已保存: {filepath}")
            return filepath
        except Exception as e:
            print(f"✗ 保存训练图表失败: {e}")
            plt.close()
            return None

def run_actual_training(task_name, episodes=100):
    """运行实际的强化学习训练"""
    print(f"开始实际训练任务: {task_name}")
    print(f"目标训练轮次: {episodes}")
    print("=" * 60)
    
    try:
        # 获取任务配置
        if task_name not in TASK_CONFIGS:
            print(f"错误: 未找到任务配置 {task_name}")
            return None
        
        task_config = TASK_CONFIGS[task_name]
        
        # 创建环境
        env = FabEnvironment(task_config)
        
        # 创建智能体
        state_size = env.get_state_size()
        action_size = env.get_action_size()
        agent = WaferAgent(state_size, action_size)
        
        # 创建训练器
        trainer = MultiAgentTrainer([agent], env)
        
        # 创建绘图器
        plotter = RealTimeTrainingPlotter(task_name)
        
        print(f"环境状态空间大小: {state_size}")
        print(f"环境动作空间大小: {action_size}")
        print("开始训练...")
        
        # 训练循环
        for episode in range(1, episodes + 1):
            start_time = time.time()
            
            # 重置环境
            state = env.reset()
            total_reward = 0
            done = False
            step_count = 0
            
            # 单次训练循环
            while not done and step_count < 1000:  # 限制最大步数
                # 选择动作
                action = agent.act(state)
                
                # 执行动作
                next_state, reward, done, info = env.step(action)
                
                # 存储经验
                agent.remember(state, action, reward, next_state, done)
                
                # 更新状态和奖励
                state = next_state
                total_reward += reward
                step_count += 1
                
                # 训练智能体
                if len(agent.memory) > 32:
                    loss = agent.replay(32)
                else:
                    loss = 0
            
            # 计算训练时间
            episode_time = time.time() - start_time
            
            # 添加训练数据
            plotter.add_episode_data(episode, total_reward, episode_time, loss)
            
            # 每10轮输出进度和生成图表
            if episode % 10 == 0 or episode == episodes:
                avg_reward = plotter.training_data['avg_rewards'][-1]
                best_reward = plotter.training_data['best_rewards'][-1]
                
                print(f"轮次 {episode:4d}: 奖励={total_reward:8.1f}, 平均={avg_reward:8.1f}, 最佳={best_reward:8.1f}, 时间={episode_time:.2f}s")
                
                # 生成实时图表
                plotter.create_training_plot(save_final=False)
            
            # 更新探索率
            if hasattr(agent, 'epsilon') and agent.epsilon > agent.epsilon_min:
                agent.epsilon *= agent.epsilon_decay
        
        # 生成最终图表
        final_plot = plotter.create_training_plot(save_final=True)
        
        print("=" * 60)
        print(f"✓ 任务 {task_name} 实际训练完成！")
        print(f"最终平均奖励: {plotter.training_data['avg_rewards'][-1]:.1f}")
        print(f"最终最佳奖励: {plotter.training_data['best_rewards'][-1]:.1f}")
        if plotter.training_data['avg_rewards']:
            improvement = ((plotter.training_data['avg_rewards'][-1] - plotter.training_data['avg_rewards'][0]) / plotter.training_data['avg_rewards'][0] * 100)
            print(f"总体提升: {improvement:.1f}%")
        print("=" * 60)
        
        return plotter.training_data
        
    except Exception as e:
        print(f"训练过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数 - 运行实际训练"""
    print("=" * 60)
    print("开始实际强化学习训练并生成奖励函数图表")
    print("=" * 60)
    
    # 可用的训练任务
    available_tasks = ['task_a', 'task_b', 'task_d']
    
    # 为每个任务运行实际训练
    all_results = {}
    
    for task_name in available_tasks:
        print(f"\n{'='*20} 开始训练 {task_name.upper()} {'='*20}")
        
        # 运行实际训练（较少轮次用于演示）
        results = run_actual_training(task_name, episodes=50)
        
        if results:
            all_results[task_name] = results
            print(f"✓ {task_name} 训练完成")
        else:
            print(f"✗ {task_name} 训练失败")
        
        print(f"{'='*20} 完成训练 {task_name.upper()} {'='*20}\n")
    
    print("\n" + "=" * 60)
    if all_results:
        print("所有实际训练任务完成！")
        print("生成的图表文件保存在 output/ 文件夹中")
        
        # 显示结果摘要
        print("\n训练结果摘要:")
        for task_name, data in all_results.items():
            if data['avg_rewards']:
                final_avg = data['avg_rewards'][-1]
                final_best = data['best_rewards'][-1]
                print(f"  {task_name}: 平均奖励={final_avg:.1f}, 最佳奖励={final_best:.1f}")
    else:
        print("没有成功完成任何训练任务")
    print("=" * 60)

if __name__ == "__main__":
    main()