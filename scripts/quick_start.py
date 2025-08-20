"""
快速启动脚本
提供简单的交互式界面
"""

import os
import sys
import subprocess
from datetime import datetime

def print_banner():
    """打印横幅"""
    print("="*60)
    print("    半导体晶圆调度多智能体强化学习系统")
    print("    Semiconductor Wafer Scheduling with Multi-Agent RL")
    print("="*60)
    print()

def print_menu():
    """打印菜单"""
    print("请选择操作:")
    print("1. 运行系统测试")
    print("2. 运行基础仿真调度 (任务A)")
    print("3. 运行基础仿真调度 (任务B)")
    print("4. 运行基础仿真调度 (任务C)")
    print("5. 运行基础仿真调度 (任务D)")
    print("6. 运行强化学习训练 (任务A)")
    print("7. 运行强化学习训练 (任务B)")
    print("8. 运行强化学习训练 (任务C)")
    print("9. 运行强化学习训练 (任务D)")
    print("10. 批量运行所有任务")
    print("11. 分析结果文件")
    print("0. 退出")
    print()

def run_command_interactive(command, description):
    """交互式运行命令"""
    print(f"\n执行: {description}")
    print(f"命令: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ {description} 完成")
        else:
            print(f"❌ {description} 失败")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False

def get_result_files():
    """获取结果文件列表"""
    if not os.path.exists('output'):
        return []
    
    files = []
    for file in os.listdir('output'):
        if file.endswith('.json'):
            files.append(os.path.join('output', file))
    
    return sorted(files, key=os.path.getmtime, reverse=True)

def analyze_results():
    """分析结果"""
    files = get_result_files()
    
    if not files:
        print("未找到结果文件")
        return
    
    print("找到以下结果文件:")
    for i, file in enumerate(files[:10]):  # 只显示最新的10个
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        print(f"{i+1}. {os.path.basename(file)} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    try:
        choice = input("\n请选择要分析的文件编号 (1-{}): ".format(min(10, len(files))))
        idx = int(choice) - 1
        
        if 0 <= idx < len(files):
            selected_file = files[idx]
            print(f"\n分析文件: {selected_file}")
            
            # 验证文件
            command = f"python -c \"from utils.validator import validate_result_file; validate_result_file('{selected_file}')\""
            run_command_interactive(command, "约束验证")
            
            # 可视化分析
            command = f"python -c \"from utils.visualization import ScheduleVisualizer; v=ScheduleVisualizer(); v.analyze_results('{selected_file}')\""
            run_command_interactive(command, "结果可视化")
        else:
            print("无效的选择")
    
    except ValueError:
        print("请输入有效的数字")
    except KeyboardInterrupt:
        print("\n操作取消")

def main():
    """主函数"""
    # 创建必要目录
    os.makedirs('output', exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)
    
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("请输入选择 (0-11): ").strip()
            
            if choice == '0':
                print("退出系统")
                break
            
            elif choice == '1':
                run_command_interactive("python test_system.py", "系统测试")
            
            elif choice in ['2', '3', '4', '5']:
                task = chr(ord('a') + int(choice) - 2)  # 2->a, 3->b, 4->c, 5->d
                command = f"python main.py --task {task}"
                run_command_interactive(command, f"任务{task.upper()}基础仿真")
            
            elif choice in ['6', '7', '8', '9']:
                task = chr(ord('a') + int(choice) - 6)  # 6->a, 7->b, 8->c, 9->d
                episodes = input("请输入训练回合数 (默认100): ").strip()
                if not episodes:
                    episodes = "100"
                command = f"python train_rl.py --task {task} --episodes {episodes}"
                run_command_interactive(command, f"任务{task.upper()}强化学习训练")
            
            elif choice == '10':
                run_command_interactive("python run_all_tasks.py", "批量运行所有任务")
            
            elif choice == '11':
                analyze_results()
            
            else:
                print("无效的选择，请重新输入")
            
            if choice != '0':
                input("\n按回车键继续...")
        
        except KeyboardInterrupt:
            print("\n\n退出系统")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()