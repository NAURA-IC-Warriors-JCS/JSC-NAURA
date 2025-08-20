#!/usr/bin/env python3
"""
生成训练过程中奖励函数训练图
保存到output文件夹中
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_training_data(task_name):
    """加载指定任务的训练数据"""
    checkpoints_dir = f"checkpoints/{task_name}"
    if not os.path.exists(checkpoints_dir):
        return None
    
    # 获取所有checkpoint文件
    checkpoint_files = [f for f in os.listdir(checkpoints_dir) if f.endswith('.json')]
    checkpoint_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    episodes = []
    all_rewards = []
    avg_rewards = []
    best_rewards = []
    episode_times = []
    
    for file in checkpoint_files:
        file_path = os.path.join(checkpoints_dir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            episode = data.get('episode', 0)
            rewards = data.get('episode_rewards', [])
            times = data.get('episode_times', [])
            
            if rewards:
                episodes.append(episode)
                all_rewards.extend(rewards)
                avg_rewards.append(np.mean(rewards))
                best_rewards.append(np.max(rewards))
                episode_times.extend(times)
                
        except Exception as e:
            print(f"加载文件 {file} 失败: {e}")
            continue
    
    return {
        'episodes': episodes,
        'all_rewards': all_rewards,
        'avg_rewards': avg_rewards,
        'best_rewards': best_rewards,
        'episode_times': episode_times
    }

def calculate_success_rate(episode_times, threshold_percentile=25):
    """基于处理时间计算成功率"""
    if not episode_times:
        return []
    
    # 使用时间的25%分位数作为成功阈值
    threshold = np.percentile(episode_times, threshold_percentile)
    success_rate = (np.array(episode_times) <= threshold).astype(float) * 100
    return success_rate

def smooth_data(data, window_size=10):
    """数据平滑处理"""
    if len(data) < window_size:
        return data
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def create_reward_training_plot(task_name, data, output_dir):
    """创建奖励函数训练图"""
    if not data or not data['episodes']:
        print(f"任务 {task_name} 没有可用数据")
        return
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'{task_name.upper()} 训练过程奖励函数分析', fontsize=16, fontweight='bold')
    
    episodes = data['episodes']
    avg_rewards = data['avg_rewards']
    best_rewards = data['best_rewards']
    all_rewards = data['all_rewards']
    episode_times = data['episode_times']
    
    # 1. 平均奖励和最佳奖励曲线
    ax1.plot(episodes, avg_rewards, 'b-', linewidth=2, label='平均奖励', alpha=0.8)
    ax1.plot(episodes, best_rewards, 'r-', linewidth=2, label='最佳奖励', alpha=0.8)
    
    # 添加平滑曲线
    if len(avg_rewards) > 5:
        smooth_avg = smooth_data(avg_rewards, min(10, len(avg_rewards)//3))
        smooth_episodes = episodes[len(episodes)-len(smooth_avg):]
        ax1.plot(smooth_episodes, smooth_avg, 'darkblue', linewidth=3, 
                label='平均奖励(平滑)', alpha=0.9)
    
    ax1.set_title('奖励函数训练曲线')
    ax1.set_xlabel('训练轮次')
    ax1.set_ylabel('奖励值')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 在图上显示数值
    if len(episodes) > 0:
        # 显示最终值
        final_avg = avg_rewards[-1]
        final_best = best_rewards[-1]
        ax1.text(0.02, 0.98, f'最终平均奖励: {final_avg:.1f}\n最终最佳奖励: {final_best:.1f}', 
                transform=ax1.transAxes, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # 2. 奖励分布直方图
    ax2.hist(all_rewards, bins=50, alpha=0.7, color='skyblue', edgecolor='black', density=True)
    ax2.axvline(np.mean(all_rewards), color='red', linestyle='--', linewidth=2, label=f'均值: {np.mean(all_rewards):.1f}')
    ax2.axvline(np.median(all_rewards), color='green', linestyle='--', linewidth=2, label=f'中位数: {np.median(all_rewards):.1f}')
    ax2.set_title('奖励值分布')
    ax2.set_xlabel('奖励值')
    ax2.set_ylabel('密度')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 成功率和效率分析
    if episode_times:
        # 计算成功率（基于处理时间）
        success_rates = []
        efficiency_rates = []
        
        # 按checkpoint分组计算
        times_per_checkpoint = len(episode_times) // len(episodes) if episodes else 1
        
        for i in range(len(episodes)):
            start_idx = i * times_per_checkpoint
            end_idx = min((i + 1) * times_per_checkpoint, len(episode_times))
            
            if start_idx < len(episode_times):
                checkpoint_times = episode_times[start_idx:end_idx]
                
                # 成功率：处理时间低于中位数的比例
                median_time = np.median(episode_times)
                success_rate = (np.array(checkpoint_times) <= median_time).mean() * 100
                success_rates.append(success_rate)
                
                # 效率：晶圆/小时
                avg_time_hours = np.mean(checkpoint_times) / 3600
                efficiency = 1 / avg_time_hours if avg_time_hours > 0 else 0
                efficiency_rates.append(efficiency)
        
        # 绘制成功率（右侧纵坐标）
        ax3_twin = ax3.twinx()
        
        # 奖励曲线（左侧纵坐标）
        line1 = ax3.plot(episodes, avg_rewards, 'b-', linewidth=2, label='平均奖励')
        ax3.set_xlabel('训练轮次')
        ax3.set_ylabel('奖励值', color='b')
        ax3.tick_params(axis='y', labelcolor='b')
        
        # 成功率曲线（右侧纵坐标）
        if len(success_rates) == len(episodes):
            line2 = ax3_twin.plot(episodes, success_rates, 'r-', linewidth=2, label='成功率')
            ax3_twin.set_ylabel('成功率 (%)', color='r')
            ax3_twin.tick_params(axis='y', labelcolor='r')
            ax3_twin.set_ylim(0, 100)
            
            # 在图上显示数值
            if success_rates:
                final_success = success_rates[-1]
                ax3_twin.text(0.02, 0.98, f'最终成功率: {final_success:.1f}%', 
                            transform=ax3_twin.transAxes, verticalalignment='top',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
        
        ax3.set_title('奖励与成功率对比')
        ax3.grid(True, alpha=0.3)
        
        # 添加图例
        lines1, labels1 = ax3.get_legend_handles_labels()
        lines2, labels2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(lines1 + lines2, labels1 + labels2, loc='center right')
    
    # 4. 训练稳定性分析
    if len(avg_rewards) > 10:
        # 计算奖励的变异系数
        reward_std = np.std(avg_rewards)
        reward_mean = np.mean(avg_rewards)
        cv = reward_std / reward_mean if reward_mean != 0 else 0
        
        # 绘制奖励的滚动标准差
        window_size = min(10, len(avg_rewards) // 3)
        rolling_std = []
        rolling_episodes = []
        
        for i in range(window_size, len(avg_rewards)):
            window_data = avg_rewards[i-window_size:i]
            rolling_std.append(np.std(window_data))
            rolling_episodes.append(episodes[i])
        
        ax4.plot(rolling_episodes, rolling_std, 'purple', linewidth=2, label='滚动标准差')
        ax4.set_title('训练稳定性分析')
        ax4.set_xlabel('训练轮次')
        ax4.set_ylabel('奖励标准差')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        # 显示变异系数
        ax4.text(0.02, 0.98, f'变异系数: {cv:.3f}\n(越小越稳定)', 
                transform=ax4.transAxes, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
    
    plt.tight_layout()
    
    # 保存图表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reward_training_plot_{task_name}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"已保存: {filepath}")
    
    plt.close()
    
    return filepath

def create_combined_comparison_plot(all_data, output_dir):
    """创建所有任务的对比图"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('所有任务奖励函数训练对比', fontsize=16, fontweight='bold')
    
    colors = {'task_a': 'blue', 'task_b': 'red', 'task_d': 'green'}
    task_names = {'task_a': 'Task A (装载)', 'task_b': 'Task B (处理)', 'task_d': 'Task D (完整)'}
    
    # 1. 平均奖励对比
    for task_name, data in all_data.items():
        if data and data['episodes']:
            episodes = data['episodes']
            avg_rewards = data['avg_rewards']
            color = colors.get(task_name, 'black')
            label = task_names.get(task_name, task_name)
            
            ax1.plot(episodes, avg_rewards, color=color, linewidth=2, label=label, alpha=0.8)
            
            # 添加平滑曲线
            if len(avg_rewards) > 5:
                smooth_avg = smooth_data(avg_rewards, min(10, len(avg_rewards)//3))
                smooth_episodes = episodes[len(episodes)-len(smooth_avg):]
                ax1.plot(smooth_episodes, smooth_avg, color=color, linewidth=3, 
                        alpha=0.6, linestyle='--')
    
    ax1.set_title('平均奖励对比')
    ax1.set_xlabel('训练轮次')
    ax1.set_ylabel('平均奖励值')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. 最佳奖励对比
    for task_name, data in all_data.items():
        if data and data['episodes']:
            episodes = data['episodes']
            best_rewards = data['best_rewards']
            color = colors.get(task_name, 'black')
            label = task_names.get(task_name, task_name)
            
            ax2.plot(episodes, best_rewards, color=color, linewidth=2, label=label, alpha=0.8)
    
    ax2.set_title('最佳奖励对比')
    ax2.set_xlabel('训练轮次')
    ax2.set_ylabel('最佳奖励值')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. 奖励分布对比
    for task_name, data in all_data.items():
        if data and data['all_rewards']:
            color = colors.get(task_name, 'black')
            label = task_names.get(task_name, task_name)
            
            ax3.hist(data['all_rewards'], bins=30, alpha=0.5, color=color, 
                    label=label, density=True, edgecolor='black')
    
    ax3.set_title('奖励分布对比')
    ax3.set_xlabel('奖励值')
    ax3.set_ylabel('密度')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 训练效果总结
    ax4.axis('off')
    summary_text = "训练效果总结:\n\n"
    
    for task_name, data in all_data.items():
        if data and data['avg_rewards']:
            task_label = task_names.get(task_name, task_name)
            final_avg = data['avg_rewards'][-1]
            final_best = data['best_rewards'][-1]
            total_episodes = data['episodes'][-1] if data['episodes'] else 0
            
            summary_text += f"{task_label}:\n"
            summary_text += f"  最终平均奖励: {final_avg:.1f}\n"
            summary_text += f"  最终最佳奖励: {final_best:.1f}\n"
            summary_text += f"  训练轮次: {total_episodes}\n\n"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=12,
            verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
            facecolor="lightblue", alpha=0.8))
    
    plt.tight_layout()
    
    # 保存对比图
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reward_training_comparison_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"已保存对比图: {filepath}")
    
    plt.close()
    
    return filepath

def main():
    """主函数"""
    print("=" * 60)
    print("生成训练过程奖励函数训练图")
    print("=" * 60)
    
    # 确保输出目录存在
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    # 支持的任务
    tasks = ['task_a', 'task_b', 'task_d']
    all_data = {}
    
    # 为每个任务生成图表
    for task in tasks:
        print(f"\n处理任务: {task}")
        data = load_training_data(task)
        
        if data:
            all_data[task] = data
            filepath = create_reward_training_plot(task, data, output_dir)
            print(f"✓ {task} 图表已生成")
        else:
            print(f"✗ {task} 没有可用数据")
    
    # 生成对比图
    if all_data:
        print(f"\n生成对比图...")
        comparison_filepath = create_combined_comparison_plot(all_data, output_dir)
        print("✓ 对比图已生成")
    
    print("\n" + "=" * 60)
    print("所有图表生成完成！")
    print(f"输出目录: {os.path.abspath(output_dir)}")
    print("=" * 60)

if __name__ == "__main__":
    main()