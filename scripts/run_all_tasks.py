"""
批量运行所有任务的脚本
"""

import subprocess
import os
import sys
from datetime import datetime

def run_command(command, description):
    """运行命令并处理输出"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} 完成")
        else:
            print(f"❌ {description} 失败 (返回码: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False

def main():
    """主函数"""
    print("半导体晶圆调度系统 - 批量任务执行")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建输出目录
    os.makedirs('output', exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)
    
    tasks = ['a', 'b', 'c', 'd']
    success_count = 0
    
    # 1. 运行系统测试
    print("\n" + "="*60)
    print("第一步: 系统测试")
    print("="*60)
    
    if run_command("python test_system.py", "系统功能测试"):
        print("✅ 系统测试通过，继续执行任务")
    else:
        print("❌ 系统测试失败，请检查环境配置")
        return
    
    # 2. 运行基础仿真
    print("\n" + "="*60)
    print("第二步: 基础仿真调度")
    print("="*60)
    
    for task in tasks:
        print(f"\n--- 任务 {task.upper()} 基础仿真 ---")
        command = f"python main.py --task {task}"
        if run_command(command, f"任务{task.upper()}基础仿真"):
            success_count += 1
    
    print(f"\n基础仿真完成: {success_count}/{len(tasks)} 个任务成功")
    
    # 3. 运行强化学习训练 (可选)
    print("\n" + "="*60)
    print("第三步: 强化学习训练 (可选)")
    print("="*60)
    
    user_input = input("是否运行强化学习训练? (y/n): ").lower().strip()
    
    if user_input == 'y':
        rl_success = 0
        episodes = input("请输入训练回合数 (默认100): ").strip()
        if not episodes:
            episodes = "100"
        
        for task in tasks:
            print(f"\n--- 任务 {task.upper()} 强化学习训练 ---")
            command = f"python train_rl.py --task {task} --episodes {episodes}"
            if run_command(command, f"任务{task.upper()}强化学习训练"):
                rl_success += 1
        
        print(f"\n强化学习训练完成: {rl_success}/{len(tasks)} 个任务成功")
    else:
        print("跳过强化学习训练")
    
    # 4. 结果分析
    print("\n" + "="*60)
    print("第四步: 结果分析")
    print("="*60)
    
    output_files = []
    for file in os.listdir('output'):
        if file.endswith('.json'):
            output_files.append(os.path.join('output', file))
    
    if output_files:
        print(f"找到 {len(output_files)} 个结果文件:")
        for file in output_files:
            print(f"  - {file}")
        
        # 运行结果验证
        print("\n验证结果文件...")
        for file in output_files[:4]:  # 只验证前4个文件
            command = f"python -c \"from utils.validator import validate_result_file; validate_result_file('{file}')\""
            run_command(command, f"验证 {os.path.basename(file)}")
    else:
        print("未找到结果文件")
    
    # 5. 总结
    print("\n" + "="*60)
    print("执行总结")
    print("="*60)
    
    end_time = datetime.now()
    print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"基础仿真成功: {success_count}/{len(tasks)}")
    
    if output_files:
        print(f"生成结果文件: {len(output_files)} 个")
        print("结果文件位置: output/ 目录")
    
    print("\n可用的后续操作:")
    print("1. 查看结果可视化:")
    print("   python -c \"from utils.visualization import ScheduleVisualizer; v=ScheduleVisualizer(); v.analyze_results('output/your_file.json')\"")
    print("2. 比较多个结果:")
    print("   python -c \"from utils.visualization import compare_results; compare_results(['file1.json', 'file2.json'])\"")
    print("3. 单独运行任务:")
    print("   python main.py --task a")
    print("4. 强化学习训练:")
    print("   python train_rl.py --task a --episodes 500")

if __name__ == "__main__":
    main()