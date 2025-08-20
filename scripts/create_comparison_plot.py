#!/usr/bin/env python3
"""
创建所有任务的奖励函数对比图
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_all_tasks_data():
    """加载所有任务的数据"""
    tasks = ['task_a', 'task_b', 'task_d']
    all_data = {}
    
    for task in tasks:
        print(f"加载 {task} 数据...")
        checkpoints_dir = f"checkpoints/{task}"
        
        if not os.path.exists(checkpoints_dir):
            continue
        
        files = [f for f in os.listdir(checkpoints_dir) if f.endswith('.json')]
        files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        
        episodes = []
        avg_rewards = []
        best_rewards = []
        all_rewards = []
        
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
                    all_rewards.extend(rewards)
                    
            except Exception as e:
                print(f"加载 {task}/{file} 失败: {e}")
                continue
        
        if episodes:
            all_data[task] = {
                'episodes': episodes,
                'avg_rewards': avg_rewards,
                'best_rewards': best_rewards,
                'all_rewards': all_rewards
            }
            print(f"✓ {task}: {len(episodes)} 个数据点")
        else:
            print(f"✗ {task}: 无可用数据")
    
    return all_data

def create_comparison_plot(all_data, output_dir):
    """创建对比图"""
    if not all_data:
        print("没有可用数据")
        return None
    
    # 创建大图表
    fig = plt.figure(figsize=(20, 16))
    
    # 设置颜色和标签
    colors = {'task_a': '#1f77b4', 'task_b': '#ff7f0e', 'task_d': '#2ca02c'}
    labels = {'task_a': 'Task A (装载腔室)', 'task_b': 'Task B (处理腔室)', 'task_d': 'Task D (完整流程)'}
    
    # 1. 平均奖励对比 (左上)
    ax1 = plt.subplot(2, 3, 1)
    for task, data in all_data.items():
        episodes = data['episodes']
        avg_rewards = data['avg_rewards']
        color = colors[task]
        label = labels[task]
        
        ax1.plot(episodes, avg_rewards, color=color, linewidth=2.5, label=label, alpha=0.8)
        
        # 添加数值标注
        if episodes:
            final_reward = avg_rewards[-1]
            ax1.annotate(f'{final_reward:.0f}', 
                        xy=(episodes[-1], final_reward),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7),
                        fontsize=10, color='white', fontweight='bold')
    
    ax1.set_title('平均奖励对比', fontsize=14, fontweight='bold')
    ax1.set_xlabel('训练轮次')
    ax1.set_ylabel('平均奖励值')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. 最佳奖励对比 (右上)
    ax2 = plt.subplot(2, 3, 2)
    for task, data in all_data.items():
        episodes = data['episodes']
        best_rewards = data['best_rewards']
        color = colors[task]
        label = labels[task]
        
        ax2.plot(episodes, best_rewards, color=color, linewidth=2.5, label=label, alpha=0.8)
        
        # 添加数值标注
        if episodes:
            final_best = best_rewards[-1]
            ax2.annotate(f'{final_best:.0f}', 
                        xy=(episodes[-1], final_best),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7),
                        fontsize=10, color='white', fontweight='bold')
    
    ax2.set_title('最佳奖励对比', fontsize=14, fontweight='bold')
    ax2.set_xlabel('训练轮次')
    ax2.set_ylabel('最佳奖励值')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. 奖励分布对比 (中上)
    ax3 = plt.subplot(2, 3, 3)
    for task, data in all_data.items():
        all_rewards = data['all_rewards']
        color = colors[task]
        label = labels[task]
        
        ax3.hist(all_rewards, bins=40, alpha=0.6, color=color, label=label, 
                density=True, edgecolor='black', linewidth=0.5)
    
    ax3.set_title('奖励分布对比', fontsize=14, fontweight='bold')
    ax3.set_xlabel('奖励值')
    ax3.set_ylabel('密度')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 训练效果统计表 (左下)
    ax4 = plt.subplot(2, 3, 4)
    ax4.axis('off')
    
    # 创建统计表格
    table_data = []
    headers = ['任务', '最终平均奖励', '最终最佳奖励', '训练轮次', '奖励标准差']
    
    for task, data in all_data.items():
        task_label = labels[task]
        final_avg = data['avg_rewards'][-1] if data['avg_rewards'] else 0
        final_best = data['best_rewards'][-1] if data['best_rewards'] else 0
        total_episodes = data['episodes'][-1] if data['episodes'] else 0
        reward_std = np.std(data['avg_rewards']) if data['avg_rewards'] else 0
        
        table_data.append([
            task_label,
            f'{final_avg:.1f}',
            f'{final_best:.1f}',
            f'{total_episodes}',
            f'{reward_std:.1f}'
        ])
    
    # 绘制表格
    table = ax4.table(cellText=table_data, colLabels=headers, 
                     cellLoc='center', loc='center',
                     colWidths=[0.25, 0.2, 0.2, 0.15, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # 设置表格样式
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i, task in enumerate(['task_a', 'task_b', 'task_d']):
        color = colors[task]
        for j in range(len(headers)):
            table[(i+1, j)].set_facecolor(color)
            table[(i+1, j)].set_alpha(0.3)
    
    ax4.set_title('训练效果统计', fontsize=14, fontweight='bold', pad=20)
    
    # 5. 训练收敛性分析 (中下)
    ax5 = plt.subplot(2, 3, 5)
    
    for task, data in all_data.items():
        avg_rewards = data['avg_rewards']
        episodes = data['episodes']
        color = colors[task]
        label = labels[task]
        
        if len(avg_rewards) > 5:
            # 计算滚动标准差
            window_size = min(5, len(avg_rewards) // 2)
            rolling_std = []
            rolling_episodes = []
            
            for i in range(window_size, len(avg_rewards)):
                window_data = avg_rewards[i-window_size:i]
                rolling_std.append(np.std(window_data))
                rolling_episodes.append(episodes[i])
            
            ax5.plot(rolling_episodes, rolling_std, color=color, linewidth=2, 
                    label=label, alpha=0.8)
    
    ax5.set_title('训练稳定性对比', fontsize=14, fontweight='bold')
    ax5.set_xlabel('训练轮次')
    ax5.set_ylabel('奖励标准差')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # 6. 性能提升分析 (右下)
    ax6 = plt.subplot(2, 3, 6)
    
    improvement_data = []
    task_names = []
    
    for task, data in all_data.items():
        avg_rewards = data['avg_rewards']
        if len(avg_rewards) >= 2:
            initial_reward = np.mean(avg_rewards[:3]) if len(avg_rewards) >= 3 else avg_rewards[0]
            final_reward = np.mean(avg_rewards[-3:]) if len(avg_rewards) >= 3 else avg_rewards[-1]
            improvement = ((final_reward - initial_reward) / initial_reward) * 100
            
            improvement_data.append(improvement)
            task_names.append(labels[task])
    
    if improvement_data:
        bars = ax6.bar(task_names, improvement_data, 
                      color=[colors[task] for task in all_data.keys()], 
                      alpha=0.7, edgecolor='black')
        
        # 添加数值标注
        for bar, value in zip(bars, improvement_data):
            height = bar.get_height()
            ax6.annotate(f'{value:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
    
    ax6.set_title('性能提升对比', fontsize=14, fontweight='bold')
    ax6.set_ylabel('提升百分比 (%)')
    ax6.grid(True, alpha=0.3, axis='y')
    ax6.tick_params(axis='x', rotation=45)
    
    # 总标题
    fig.suptitle('强化学习训练过程奖励函数综合分析', fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    
    # 保存图表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reward_training_comparison_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    try:
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ 对比图已保存: {filepath}")
        plt.close()
        return filepath
    except Exception as e:
        print(f"✗ 保存对比图失败: {e}")
        plt.close()
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("生成奖励函数训练对比图")
    print("=" * 60)
    
    # 确保输出目录存在
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 加载所有任务数据
    all_data = load_all_tasks_data()
    
    if all_data:
        # 创建对比图
        filepath = create_comparison_plot(all_data, output_dir)
        
        if filepath:
            print("\n" + "=" * 60)
            print("对比图生成完成！")
            print(f"文件位置: {os.path.abspath(filepath)}")
            print("=" * 60)
        else:
            print("对比图生成失败")
    else:
        print("没有找到可用的训练数据")

if __name__ == "__main__":
    main()