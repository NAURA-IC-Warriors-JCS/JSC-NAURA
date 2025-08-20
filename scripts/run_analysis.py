#!/usr/bin/env python3
"""
强化学习训练结果完整分析脚本
整合训练曲线分析、物理模型仿真和性能评估
"""

import argparse
import os
import sys
from utils.rl_analyzer import RLAnalyzer
from utils.physics_model import FabPhysicsSimulator
import matplotlib.pyplot as plt

def run_training_analysis(tasks, checkpoint_dir, output_dir):
    """运行训练分析"""
    print("=" * 50)
    print("开始强化学习训练分析...")
    print("=" * 50)
    
    analyzer = RLAnalyzer(checkpoint_dir=checkpoint_dir, output_dir=output_dir)
    analyzer.analyze_all_tasks(tasks)
    
    print(f"训练分析完成！结果保存在 '{output_dir}' 目录")

def run_physics_simulation():
    """运行物理仿真"""
    print("=" * 50)
    print("开始物理模型仿真...")
    print("=" * 50)
    
    simulator = FabPhysicsSimulator()
    
    # 添加晶圆
    for i in range(3):
        simulator.add_wafer(i)
    
    # 启动工艺过程
    simulator.chambers[0].start_process(200.0, 8.0)
    simulator.chambers[1].start_process(150.0, 6.0)
    simulator.chambers[2].start_process(300.0, 10.0)
    
    print("启动物理仿真可视化...")
    anim = simulator.visualize_realtime()
    
    print("物理仿真完成！")
    return anim

def generate_comprehensive_report(tasks, checkpoint_dir, output_dir):
    """生成综合报告"""
    print("=" * 50)
    print("生成综合分析报告...")
    print("=" * 50)
    
    analyzer = RLAnalyzer(checkpoint_dir=checkpoint_dir, output_dir=output_dir)
    
    # 收集所有任务数据
    all_data = {}
    for task in tasks:
        checkpoints = analyzer.load_checkpoint_data(task)
        if checkpoints:
            metrics = analyzer.extract_training_metrics(checkpoints)
            all_data[task] = {
                'checkpoints': checkpoints,
                'metrics': metrics
            }
    
    if not all_data:
        print("没有找到任何训练数据！")
        return
    
    # 生成详细报告
    report_path = os.path.join(output_dir, 'comprehensive_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 强化学习训练综合分析报告\n\n")
        f.write("## 概述\n\n")
        f.write(f"本报告分析了 {len(all_data)} 个任务的训练结果。\n\n")
        
        f.write("## 任务性能总结\n\n")
        f.write("| 任务 | 最终奖励 | 最终成功率 | 收敛轮次 | 平均完成时间 |\n")
        f.write("|------|----------|------------|----------|-------------|\n")
        
        for task, data in all_data.items():
            metrics = data['metrics']
            final_reward = metrics['rewards'][-1] if metrics['rewards'] else 0
            final_success = metrics['success_rates'][-1] if metrics['success_rates'] else 0
            convergence = analyzer.find_convergence_point(metrics['success_rates'], 
                                                        metrics['episodes'])
            avg_time = sum(metrics['completion_times'][-10:]) / 10 if len(metrics['completion_times']) >= 10 else 0
            
            f.write(f"| {task.upper()} | {final_reward:.2f} | {final_success:.1f}% | {convergence or 'N/A'} | {avg_time:.2f}s |\n")
        
        f.write("\n## 详细分析\n\n")
        for task, data in all_data.items():
            f.write(f"### 任务 {task.upper()}\n\n")
            metrics = data['metrics']
            
            if metrics['rewards']:
                f.write(f"- **训练轮次**: {len(metrics['episodes'])}\n")
                f.write(f"- **最终累积奖励**: {metrics['rewards'][-1]:.2f}\n")
                f.write(f"- **奖励改善**: {metrics['rewards'][-1] - metrics['rewards'][0]:.2f}\n")
                f.write(f"- **最终成功率**: {metrics['success_rates'][-1]:.1f}%\n")
                
                if metrics['completion_times']:
                    f.write(f"- **平均完成时间**: {sum(metrics['completion_times'])/len(metrics['completion_times']):.2f}s\n")
                
                convergence = analyzer.find_convergence_point(metrics['success_rates'], metrics['episodes'])
                if convergence:
                    f.write(f"- **收敛轮次** (80%成功率): {convergence}\n")
                
                f.write("\n")
        
        f.write("## 建议\n\n")
        f.write("基于分析结果，建议：\n\n")
        f.write("1. 对于收敛较慢的任务，考虑调整学习率或奖励函数\n")
        f.write("2. 对于成功率较低的任务，检查环境设置和动作空间\n")
        f.write("3. 继续训练表现良好但未完全收敛的任务\n")
        f.write("4. 考虑使用迁移学习在任务间共享知识\n\n")
    
    print(f"综合报告已保存到: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='完整的强化学习训练结果分析')
    parser.add_argument('--mode', choices=['analysis', 'physics', 'report', 'all'], 
                       default='all', help='运行模式')
    parser.add_argument('--tasks', nargs='+', default=['a', 'b', 'd'],
                       help='要分析的任务列表')
    parser.add_argument('--checkpoint-dir', default='checkpoints',
                       help='检查点目录')
    parser.add_argument('--output-dir', default='analysis',
                       help='输出目录')
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    print("强化学习训练结果分析工具")
    print(f"分析任务: {args.tasks}")
    print(f"检查点目录: {args.checkpoint_dir}")
    print(f"输出目录: {args.output_dir}")
    print()
    
    if args.mode in ['analysis', 'all']:
        run_training_analysis(args.tasks, args.checkpoint_dir, args.output_dir)
    
    if args.mode in ['physics', 'all']:
        run_physics_simulation()
    
    if args.mode in ['report', 'all']:
        generate_comprehensive_report(args.tasks, args.checkpoint_dir, args.output_dir)
    
    print("\n" + "=" * 50)
    print("所有分析完成！")
    print("=" * 50)
    print("\n生成的文件包括:")
    print("📊 训练曲线图 (training_curves_task_*.png)")
    print("📈 性能对比图 (performance_comparison.png)")
    print("🎬 动态物理模型 (dynamic_model_task_*.png)")
    print("📋 统计报告 (training_report.txt)")
    print("📄 综合报告 (comprehensive_report.md)")
    print(f"\n所有结果保存在: {args.output_dir}/")

if __name__ == "__main__":
    main()