#!/usr/bin/env python3
"""
测试真实数据可视化工具
"""

import sys
import os
import traceback

def test_imports():
    """测试所有必要的导入"""
    try:
        import tkinter as tk
        print("✓ tkinter 导入成功")
        
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        print("✓ matplotlib 导入成功")
        
        import numpy as np
        print("✓ numpy 导入成功")
        
        import json
        print("✓ json 导入成功")
        
        import glob
        print("✓ glob 导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_data_availability():
    """测试数据文件是否存在"""
    checkpoints_dir = "checkpoints"
    if not os.path.exists(checkpoints_dir):
        print(f"✗ checkpoints 目录不存在: {checkpoints_dir}")
        return False
    
    tasks = ['task_a', 'task_b', 'task_d']
    available_tasks = []
    
    for task in tasks:
        task_dir = os.path.join(checkpoints_dir, task)
        if os.path.exists(task_dir):
            json_files = [f for f in os.listdir(task_dir) if f.endswith('.json')]
            if json_files:
                available_tasks.append(task)
                print(f"✓ {task}: 发现 {len(json_files)} 个数据文件")
            else:
                print(f"✗ {task}: 目录存在但无数据文件")
        else:
            print(f"✗ {task}: 目录不存在")
    
    if available_tasks:
        print(f"✓ 总共发现 {len(available_tasks)} 个可用任务: {available_tasks}")
        return True
    else:
        print("✗ 没有发现可用的训练数据")
        return False

def test_tool_creation():
    """测试工具类创建"""
    try:
        from rl_visualization_tool_real_data import RealDataRLVisualizationTool
        
        # 创建工具实例（不启动GUI）
        app = RealDataRLVisualizationTool()
        print(f"✓ 工具创建成功")
        print(f"✓ 发现可用任务: {app.available_tasks}")
        
        # 测试数据加载
        if app.available_tasks:
            try:
                app.load_latest_data()
                print("✓ 数据加载成功")
            except Exception as e:
                print(f"⚠ 数据加载警告: {e}")
        
        # 销毁窗口（避免GUI显示）
        app.root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ 工具创建失败: {e}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("真实数据可视化工具测试")
    print("=" * 60)
    
    # 测试导入
    print("\n1. 测试模块导入...")
    if not test_imports():
        print("模块导入失败，请检查依赖安装")
        return False
    
    # 测试数据可用性
    print("\n2. 测试数据可用性...")
    if not test_data_availability():
        print("数据文件不可用，请先运行训练生成数据")
        return False
    
    # 测试工具创建
    print("\n3. 测试工具创建...")
    if not test_tool_creation():
        print("工具创建失败")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！工具可以正常使用")
    print("运行命令: python rl_visualization_tool_real_data.py")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)