"""
主运行脚本
执行指定任务的晶圆调度仿真
"""

import argparse
import os
from datetime import datetime
from environment.fab_environment import FabEnvironment

def main():
    parser = argparse.ArgumentParser(description='半导体晶圆调度仿真')
    parser.add_argument('--task', type=str, choices=['a', 'b', 'c', 'd'], 
                       required=True, help='要执行的任务 (a, b, c, d)')
    parser.add_argument('--output_dir', type=str, default='output',
                       help='输出目录')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 创建环境
    print(f"开始执行任务 {args.task.upper()}")
    env = FabEnvironment(args.task)
    
    print(f"初始化完成:")
    print(f"- 晶圆数量: {len(env.wafers)}")
    print(f"- 腔室数量: {len(env.chambers)}")
    print(f"- 机械臂数量: {len(env.robot_arms)}")
    
    # 运行仿真
    print("开始仿真...")
    start_time = datetime.now()
    
    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(args.output_dir, f"task_{args.task}_{timestamp}.json")
    
    # 保存结果
    env.save_results(output_file)
    
    end_time = datetime.now()
    simulation_time = (end_time - start_time).total_seconds()
    
    print(f"仿真完成，耗时: {simulation_time:.2f}秒")
    print(f"结果文件: {output_file}")

if __name__ == "__main__":
    main()