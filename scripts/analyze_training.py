#!/usr/bin/env python3
"""
强化学习训练结果分析脚本
用于分析通过 train_rl_fixed.py 训练的结果
"""

import argparse
import sys
import os
from utils.rl_analyzer import RLAnalyzer

def main():
    parser = argparse.ArgumentParser(description='分析强化学习训练结果')
    parser.add_argument('--tasks', nargs='+', default=['a', 'b', 'c', 'd'],
                       help='要分析的任务列表 (默认: a b c d)')
    parser.add_argument('--checkpoint-dir', default='checkpoints',
                       help='检查点目录 (默认: checkpoints)')
    parser.add_argument('--output-dir', default='analysis',
                       help='输出目录 (默认: analysis)')
    parser.add_argument('--single-task', type=str,
                       help='只分析单个任务')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = RLAnalyzer(checkpoint_dir=args.checkpoint_dir, 
                         output_dir=args.output_dir)
    
    if args.single_task:
        # 分析单个任务
        print(f"分析任务 {args.single_task.upper()}...")
        checkpoints = analyzer.load_checkpoint_data(args.single_task)
        
        if not checkpoints:
            print(f"错误: 任务 {args.single_task} 没有找到检查点数据")
            sys.exit(1)
        
        metrics = analyzer.extract_training_metrics(checkpoints)
        analyzer.plot_training_curves(args.single_task, metrics)
        analyzer.create_dynamic_fab_visualization(args.single_task, checkpoints)
        
        # 生成单任务报告
        analyzer.generate_statistical_report({args.single_task: metrics})
        
    else:
        # 分析所有指定任务
        analyzer.analyze_all_tasks(args.tasks)
    
    print(f"\n分析完成！结果保存在 '{args.output_dir}' 目录中")

if __name__ == "__main__":
    main()