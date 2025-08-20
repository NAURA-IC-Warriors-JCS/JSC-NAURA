import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import os
from datetime import datetime
import pandas as pd

class RLAnalyzer:
    """强化学习训练结果分析器"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints", output_dir: str = "analysis"):
        self.checkpoint_dir = checkpoint_dir
        self.output_dir = output_dir
        self.ensure_output_dir()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_checkpoint_data(self, task: str) -> Dict:
        """加载检查点数据"""
        task_dir = os.path.join(self.checkpoint_dir, f"task_{task}")
        if not os.path.exists(task_dir):
            print(f"警告: 任务 {task} 的检查点目录不存在")
            return {}
        
        checkpoints = []
        for file in sorted(os.listdir(task_dir)):
            if file.endswith('.json'):
                with open(os.path.join(task_dir, file), 'r') as f:
                    data = json.load(f)
                    checkpoints.append(data)
        
        return checkpoints
    
    def extract_training_metrics(self, checkpoints: List[Dict]) -> Dict:
        """提取训练指标"""
        episodes = []
        rewards = []
        losses = []
        success_rates = []
        completion_times = []
        
        for checkpoint in checkpoints:
            episodes.append(checkpoint.get('episode', 0))
            rewards.append(checkpoint.get('total_reward', 0))
            losses.append(checkpoint.get('loss', 0))
            success_rates.append(checkpoint.get('success_rate', 0))
            completion_times.append(checkpoint.get('completion_time', 0))
        
        return {
            'episodes': episodes,
            'rewards': rewards,
            'losses': losses,
            'success_rates': success_rates,
            'completion_times': completion_times
        }
    
    def plot_training_curves(self, task: str, metrics: Dict):
        """绘制训练曲线"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'任务 {task.upper()} 训练曲线分析', fontsize=16, fontweight='bold')
        
        # 奖励曲线
        axes[0, 0].plot(metrics['episodes'], metrics['rewards'], 'b-', linewidth=2)
        axes[0, 0].set_title('累积奖励变化')
        axes[0, 0].set_xlabel('训练轮次')
        axes[0, 0].set_ylabel('累积奖励')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 损失曲线
        axes[0, 1].plot(metrics['episodes'], metrics['losses'], 'r-', linewidth=2)
        axes[0, 1].set_title('损失函数变化')
        axes[0, 1].set_xlabel('训练轮次')
        axes[0, 1].set_ylabel('损失值')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 成功率曲线
        axes[1, 0].plot(metrics['episodes'], metrics['success_rates'], 'g-', linewidth=2)
        axes[1, 0].set_title('任务成功率')
        axes[1, 0].set_xlabel('训练轮次')
        axes[1, 0].set_ylabel('成功率 (%)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 完成时间曲线
        axes[1, 1].plot(metrics['episodes'], metrics['completion_times'], 'm-', linewidth=2)
        axes[1, 1].set_title('任务完成时间')
        axes[1, 1].set_xlabel('训练轮次')
        axes[1, 1].set_ylabel('完成时间 (秒)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'training_curves_task_{task}.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_performance_comparison(self, all_tasks_metrics: Dict):
        """绘制多任务性能对比"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('多任务性能对比分析', fontsize=16, fontweight='bold')
        
        colors = ['blue', 'red', 'green', 'orange']
        
        for i, (task, metrics) in enumerate(all_tasks_metrics.items()):
            color = colors[i % len(colors)]
            
            # 最终奖励对比
            if metrics['rewards']:
                axes[0, 0].bar(task.upper(), metrics['rewards'][-1], color=color, alpha=0.7)
            
            # 最终成功率对比
            if metrics['success_rates']:
                axes[0, 1].bar(task.upper(), metrics['success_rates'][-1], color=color, alpha=0.7)
            
            # 训练收敛速度（达到80%成功率的轮次）
            convergence_episode = self.find_convergence_point(metrics['success_rates'], 
                                                            metrics['episodes'], threshold=80)
            if convergence_episode:
                axes[1, 0].bar(task.upper(), convergence_episode, color=color, alpha=0.7)
            
            # 平均完成时间
            if metrics['completion_times']:
                avg_time = np.mean(metrics['completion_times'][-10:])  # 最后10次的平均值
                axes[1, 1].bar(task.upper(), avg_time, color=color, alpha=0.7)
        
        axes[0, 0].set_title('最终累积奖励')
        axes[0, 0].set_ylabel('奖励值')
        
        axes[0, 1].set_title('最终成功率')
        axes[0, 1].set_ylabel('成功率 (%)')
        
        axes[1, 0].set_title('收敛速度 (达到80%成功率)')
        axes[1, 0].set_ylabel('训练轮次')
        
        axes[1, 1].set_title('平均完成时间')
        axes[1, 1].set_ylabel('时间 (秒)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'performance_comparison.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def find_convergence_point(self, success_rates: List[float], episodes: List[int], 
                              threshold: float = 80) -> Optional[int]:
        """找到收敛点（成功率达到阈值的轮次）"""
        for i, rate in enumerate(success_rates):
            if rate >= threshold:
                return episodes[i]
        return None
    
    def create_dynamic_fab_visualization(self, task: str, checkpoints: List[Dict]):
        """创建动态晶圆厂可视化"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_title(f'任务 {task.upper()} 动态物理模型', fontsize=14, fontweight='bold')
        
        # 绘制设备布局
        chambers = [Rectangle((1, 1), 1.5, 1, facecolor='lightblue', edgecolor='black'),
                   Rectangle((1, 3), 1.5, 1, facecolor='lightgreen', edgecolor='black'),
                   Rectangle((1, 5), 1.5, 1, facecolor='lightcoral', edgecolor='black')]
        
        robot_arm = Circle((5, 4), 0.3, facecolor='orange', edgecolor='black')
        
        for chamber in chambers:
            ax.add_patch(chamber)
        ax.add_patch(robot_arm)
        
        # 添加标签
        ax.text(1.75, 1.5, 'Chamber 1', ha='center', va='center', fontweight='bold')
        ax.text(1.75, 3.5, 'Chamber 2', ha='center', va='center', fontweight='bold')
        ax.text(1.75, 5.5, 'Chamber 3', ha='center', va='center', fontweight='bold')
        ax.text(5, 3.5, 'Robot', ha='center', va='center', fontweight='bold')
        
        # 动态显示训练进度
        progress_text = ax.text(7, 7, '', fontsize=12, fontweight='bold')
        reward_text = ax.text(7, 6.5, '', fontsize=10)
        success_text = ax.text(7, 6, '', fontsize=10)
        
        def animate(frame):
            if frame < len(checkpoints):
                checkpoint = checkpoints[frame]
                episode = checkpoint.get('episode', 0)
                reward = checkpoint.get('total_reward', 0)
                success_rate = checkpoint.get('success_rate', 0)
                
                progress_text.set_text(f'训练轮次: {episode}')
                reward_text.set_text(f'累积奖励: {reward:.2f}')
                success_text.set_text(f'成功率: {success_rate:.1f}%')
                
                # 根据性能调整颜色
                if success_rate > 80:
                    robot_arm.set_facecolor('green')
                elif success_rate > 50:
                    robot_arm.set_facecolor('yellow')
                else:
                    robot_arm.set_facecolor('red')
        
        anim = animation.FuncAnimation(fig, animate, frames=len(checkpoints), 
                                     interval=200, repeat=True)
        
        plt.savefig(os.path.join(self.output_dir, f'dynamic_model_task_{task}.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        return anim
    
    def generate_statistical_report(self, all_tasks_metrics: Dict):
        """生成统计报告"""
        report = []
        report.append("=" * 60)
        report.append("强化学习训练统计报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for task, metrics in all_tasks_metrics.items():
            report.append(f"任务 {task.upper()} 统计:")
            report.append("-" * 30)
            
            if metrics['rewards']:
                report.append(f"  最终奖励: {metrics['rewards'][-1]:.2f}")
                report.append(f"  平均奖励: {np.mean(metrics['rewards']):.2f}")
                report.append(f"  奖励标准差: {np.std(metrics['rewards']):.2f}")
            
            if metrics['success_rates']:
                report.append(f"  最终成功率: {metrics['success_rates'][-1]:.1f}%")
                report.append(f"  平均成功率: {np.mean(metrics['success_rates']):.1f}%")
            
            if metrics['completion_times']:
                report.append(f"  平均完成时间: {np.mean(metrics['completion_times']):.2f}秒")
                report.append(f"  最短完成时间: {min(metrics['completion_times']):.2f}秒")
            
            convergence = self.find_convergence_point(metrics['success_rates'], 
                                                    metrics['episodes'])
            if convergence:
                report.append(f"  收敛轮次 (80%成功率): {convergence}")
            
            report.append("")
        
        # 保存报告
        with open(os.path.join(self.output_dir, 'training_report.txt'), 'w', 
                 encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print('\n'.join(report))
    
    def analyze_all_tasks(self, tasks: List[str] = ['a', 'b', 'c', 'd']):
        """分析所有任务"""
        all_tasks_metrics = {}
        
        for task in tasks:
            print(f"分析任务 {task.upper()}...")
            checkpoints = self.load_checkpoint_data(task)
            
            if not checkpoints:
                print(f"任务 {task} 没有找到检查点数据，跳过...")
                continue
            
            metrics = self.extract_training_metrics(checkpoints)
            all_tasks_metrics[task] = metrics
            
            # 绘制单个任务的训练曲线
            self.plot_training_curves(task, metrics)
            
            # 创建动态可视化
            self.create_dynamic_fab_visualization(task, checkpoints)
        
        if all_tasks_metrics:
            # 绘制多任务对比
            self.plot_performance_comparison(all_tasks_metrics)
            
            # 生成统计报告
            self.generate_statistical_report(all_tasks_metrics)
        
        print(f"分析完成！结果保存在 {self.output_dir} 目录中")

def main():
    """主函数"""
    analyzer = RLAnalyzer()
    
    # 分析所有任务
    analyzer.analyze_all_tasks(['a', 'b', 'd'])  # 根据实际存在的任务调整
    
    print("强化学习分析完成！")
    print("生成的文件包括:")
    print("- 各任务训练曲线图")
    print("- 多任务性能对比图")
    print("- 动态物理模型可视化")
    print("- 详细统计报告")

if __name__ == "__main__":
    main()