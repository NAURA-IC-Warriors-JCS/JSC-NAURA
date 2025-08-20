#!/usr/bin/env python3
"""
简化版奖励函数训练图生成器
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_task_data(task_name):
    """加载任务数据"""
    print(f"正在加载 {task_name} 数据...")
    checkpoints_dir = f"checkpoints/{task_name}"
    
    if not os.path.exists(checkpoints_dir):
        print(f"目录不存在: {checkpoints_dir}")
        return None, None, None
    
    files = [f for f in os.listdir(checkpoints_dir) if f.endswith('.json')]
    files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    episodes = []
    avg_rewards = []
    best_rewards = []
    
    for file in files:
        try:
            with open(os.path.join(checkpoints_dir, file), 'r') as f:
                data = json.load(f)
            
            episode = data.get('episode', 0)
            rewards = data.get('episode_rewards', [])
            
            if rewards:
                episodes.append(episode)
                avg_rewards.append(np.mean(rewards))
                best_rewards.append(np.max(rewards))
                
        except Exception as e:
            print(f"加载文件 {file} 失败: {e}")
            continue
    
    print(f"成功加载 {len(episodes)} 个数据点")
    return episodes, avg_rewards, best_rewards

def create_reward_plot(task_name, episodes, avg_rewards, best_rewards, output_dir):
    """创建奖励函数训练图"""
    if not episodes:
        print(f"任务 {task_name} 没有可用数据")
        return None
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'{task_name.upper()} 训练过程奖励函数分析', fontsize=16, fontweight='bold')
    
    # 1. 奖励曲线
    ax1.plot(episodes, avg_rewards, 'b-', linewidth=2, label='平均奖励', alpha=0.8)
    ax1.plot(episodes, best_rewards, 'r-', linewidth=2, label='最佳奖励', alpha=0.8)
    
    # 添加数值标注
    if episodes:
        final_avg = avg_rewards[-1]
        final_best = best_rewards[-1]
        ax1.text(0.02, 0.98, f'最终平均奖励: {final_avg:.1f}\n最终最佳奖励: {final_best:.1f}', 
                transform=ax1.transAxes, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    ax1.set_title('奖励函数训练曲线')
    ax1.set_xlabel('训练轮次')
    ax1.set_ylabel('奖励值')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. 奖励改善趋势
    if len(avg_rewards) > 1:
        improvement = np.diff(avg_rewards)
        ax2.plot(episodes[1:], improvement, 'g-', linewidth=2, alpha=0.7)
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax2.set_title('奖励改善趋势')
        ax2.set_xlabel('训练轮次')
        ax2.set_ylabel('奖励变化')
        ax2.grid(True, alpha=0.3)
        
        # 显示改善统计
        positive_improvements = np.sum(improvement > 0)
        total_improvements = len(improvement)
        improvement_rate = positive_improvements / total_improvements * 100
        ax2.text(0.02, 0.98, f'改善率: {improvement_rate:.1f}%', 
                transform=ax2.transAxes, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    
    # 3. 奖励统计分析
    ax3.hist(avg_rewards, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.axvline(np.mean(avg_rewards), color='red', linestyle='--', linewidth=2, 
               label=f'均值: {np.mean(avg_rewards):.1f}')
    ax3.axvline(np.median(avg_rewards), color='green', linestyle='--', linewidth=2, 
               label=f'中位数: {np.median(avg_rewards):.1f}')
    ax3.set_title('平均奖励分布')
    ax3.set_xlabel('奖励值')
    ax3.set_ylabel('频次')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 训练稳定性
    if len(avg_rewards) > 5:
        window_size = min(5, len(avg_rewards) // 2)
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
        
        # 显示稳定性指标
        final_std = rolling_std[-1] if rolling_std else 0
        ax4.text(0.02, 0.98, f'最终标准差: {final_std:.1f}\n(越小越稳定)', 
                transform=ax4.transAxes, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
    
    plt.tight_layout()
    
    # 保存图表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reward_training_{task_name}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    try:
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {filepath}")
        plt.close()
        return filepath
    except Exception as e:
        print(f"✗ 保存失败: {e}")
        plt.close()
        return None

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
    generated_files = []
    
    # 为每个任务生成图表
    for task in tasks:
        print(f"\n处理任务: {task}")
        episodes, avg_rewards, best_rewards = load_task_data(task)
        
        if episodes:
            filepath = create_reward_plot(task, episodes, avg_rewards, best_rewards, output_dir)
            if filepath:
                generated_files.append(filepath)
        else:
            print(f"✗ {task} 没有可用数据")
    
    print("\n" + "=" * 60)
    if generated_files:
        print("图表生成完成！")
        print(f"输出目录: {os.path.abspath(output_dir)}")
        print("生成的文件:")
        for file in generated_files:
            print(f"  - {os.path.basename(file)}")
    else:
        print("没有生成任何图表")
    print("=" * 60)

if __name__ == "__main__":
    main()