#!/usr/bin/env python3
"""
快速分析脚本 - 一键运行所有分析
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"执行命令: {command}")
    print()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 执行成功!")
            if result.stdout:
                print("输出:")
                print(result.stdout)
        else:
            print("❌ 执行失败!")
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False

def main():
    print("🎯 强化学习训练结果快速分析工具")
    print("=" * 60)
    
    # 检查必要文件
    required_files = [
        'utils/rl_analyzer.py',
        'utils/physics_model.py',
        'run_analysis.py',
        'checkpoints'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n请确保所有文件都存在后再运行。")
        return
    
    print("✅ 所有必要文件检查通过")
    
    # 检查训练数据
    tasks_with_data = []
    for task in ['a', 'b', 'c', 'd']:
        task_dir = f"checkpoints/task_{task}"
        if os.path.exists(task_dir) and os.listdir(task_dir):
            tasks_with_data.append(task)
    
    if not tasks_with_data:
        print("❌ 没有找到任何训练数据!")
        print("请先运行训练脚本生成数据:")
        print("python train_rl_fixed.py --task a --episodes 2000")
        return
    
    print(f"📊 找到训练数据的任务: {tasks_with_data}")
    
    # 运行分析
    tasks_str = ' '.join(tasks_with_data)
    
    # 1. 运行完整分析
    success = run_command(
        f"python run_analysis.py --mode all --tasks {tasks_str}",
        "运行完整分析 (训练曲线 + 物理仿真 + 综合报告)"
    )
    
    if success:
        print("\n🎉 分析完成!")
        print("\n📁 生成的文件:")
        
        analysis_dir = "analysis"
        if os.path.exists(analysis_dir):
            for file in os.listdir(analysis_dir):
                file_path = os.path.join(analysis_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   📄 {file} ({size} bytes)")
        
        print(f"\n📂 所有结果保存在: {os.path.abspath(analysis_dir)}/")
        
        # 提供额外选项
        print("\n🔧 额外分析选项:")
        print("python run_analysis.py --mode analysis  # 仅训练分析")
        print("python run_analysis.py --mode physics   # 仅物理仿真")
        print("python run_analysis.py --mode report    # 仅生成报告")
        print("python analyze_training.py --single-task a  # 单任务分析")
        
    else:
        print("\n❌ 分析失败，请检查错误信息")

if __name__ == "__main__":
    main()