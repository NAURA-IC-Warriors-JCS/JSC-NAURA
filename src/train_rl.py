"""
强化学习训练主脚本
"""

import argparse
import os
from datetime import datetime
from training.multi_agent_trainer import MultiAgentTrainer

def main():
    parser = argparse.ArgumentParser(description='多智能体强化学习训练')
    parser.add_argument('--task', type=str, choices=['a', 'b', 'c', 'd'], 
                       required=True, help='要训练的任务 (a, b, c, d)')
    parser.add_argument('--episodes', type=int, default=1000,
                       help='训练回合数')
    parser.add_argument('--output_dir', type=str, default='output',
                       help='输出目录')
    parser.add_argument('--learning_rate', type=float, default=0.1,
                       help='学习率')
    parser.add_argument('--epsilon_start', type=float, default=0.9,
                       help='初始探索率')
    parser.add_argument('--epsilon_end', type=float, default=0.01,
                       help='最终探索率')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 训练配置
    config = {
        'episodes': args.episodes,
        'max_steps_per_episode': 5000,
        'learning_rate': args.learning_rate,
        'epsilon_start': args.epsilon_start,
        'epsilon_end': args.epsilon_end,
        'epsilon_decay': 0.995,
        'save_interval': 100,
        'log_interval': 10
    }
    
    print(f"开始强化学习训练 - 任务 {args.task.upper()}")
    print(f"配置: {config}")
    
    # 创建训练器
    trainer = MultiAgentTrainer(args.task, config)
    
    # 开始训练
    start_time = datetime.now()
    
    try:
        results = trainer.train()
        
        # 保存结果
        output_file = trainer.save_final_results(args.output_dir)
        
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        print(f"\n训练完成!")
        print(f"训练时间: {training_time:.2f}秒")
        print(f"最佳完工时间: {results['best_time']:.2f}秒")
        print(f"结果文件: {output_file}")
        
    except KeyboardInterrupt:
        print("\n训练被用户中断")
        # 保存当前结果
        trainer.save_final_results(args.output_dir)
    
    except Exception as e:
        print(f"\n训练过程中出现错误: {e}")
        # 尝试保存当前结果
        try:
            trainer.save_final_results(args.output_dir)
        except:
            pass

if __name__ == "__main__":
    main()