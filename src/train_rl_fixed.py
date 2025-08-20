"""
修复后的强化学习训练主脚本
解决数据类型转换和配置问题
"""

import argparse
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from training.multi_agent_trainer_fixed import MultiAgentTrainer

def main():
    parser = argparse.ArgumentParser(description='修复后的多智能体强化学习训练')
    parser.add_argument('--task', type=str, choices=['a', 'b', 'c', 'd'], 
                       required=True, help='要训练的任务 (a, b, c, d)')
    parser.add_argument('--episodes', type=int, default=200,
                       help='训练回合数 (默认200)')
    parser.add_argument('--output_dir', type=str, default='output',
                       help='输出目录')
    parser.add_argument('--learning_rate', type=float, default=0.15,
                       help='学习率 (默认0.15)')
    parser.add_argument('--epsilon_start', type=float, default=0.8,
                       help='初始探索率 (默认0.8)')
    parser.add_argument('--max_steps', type=int, default=1500,
                       help='每回合最大步数 (默认1500)')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)
    
    # 优化后的训练配置
    config = {
        'episodes': args.episodes,
        'max_steps_per_episode': args.max_steps,
        'learning_rate': args.learning_rate,
        'epsilon_start': args.epsilon_start,
        'epsilon_end': 0.05,
        'epsilon_decay': 0.998,
        'save_interval': max(10, args.episodes // 10),  # 动态调整保存间隔
        'log_interval': max(5, args.episodes // 20)     # 动态调整日志间隔
    }
    
    print("="*60)
    print(f"开始强化学习训练 - 任务 {args.task.upper()}")
    print("="*60)
    print(f"训练配置:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print("="*60)
    
    # 创建训练器
    try:
        trainer = MultiAgentTrainer(args.task, config)
        print("✅ 训练器创建成功")
    except Exception as e:
        print(f"❌ 训练器创建失败: {e}")
        return
    
    # 开始训练
    start_time = datetime.now()
    
    try:
        print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        results = trainer.train()
        
        # 保存结果
        output_file = trainer.save_final_results(args.output_dir)
        
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print("训练完成!")
        print("="*60)
        print(f"训练时间: {training_time:.2f}秒")
        print(f"最佳完工时间: {results['best_time']:.2f}秒")
        print(f"训练回合数: {len(results['episode_rewards'])}")
        
        if results['episode_rewards']:
            final_avg_reward = sum(results['episode_rewards'][-10:]) / min(10, len(results['episode_rewards']))
            print(f"最终平均奖励: {final_avg_reward:.2f}")
        
        if output_file:
            print(f"结果文件: {output_file}")
        
        # 训练统计
        if 'best_episodes' in results and results['best_episodes']:
            print(f"最佳回合: {results['best_episodes']}")
        
    except KeyboardInterrupt:
        print("\n训练被用户中断")
        try:
            trainer.save_final_results(args.output_dir)
            print("已保存当前训练结果")
        except:
            print("保存结果失败")
    
    except Exception as e:
        print(f"\n训练过程中出现错误: {e}")
        print("尝试保存当前结果...")
        try:
            trainer.save_final_results(args.output_dir)
            print("已保存当前训练结果")
        except:
            print("保存结果失败")

if __name__ == "__main__":
    main()