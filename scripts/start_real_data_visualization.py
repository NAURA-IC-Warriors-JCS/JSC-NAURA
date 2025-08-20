#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动真实数据可视化服务器
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖项"""
    required_packages = ['flask', 'flask-socketio', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("依赖包安装完成")
        except subprocess.CalledProcessError as e:
            print(f"安装依赖包失败: {e}")
            return False
    
    return True

def check_data_files():
    """检查训练数据文件"""
    checkpoints_dir = "checkpoints"
    if not os.path.exists(checkpoints_dir):
        print(f"警告: 未找到 {checkpoints_dir} 目录")
        return False
    
    tasks = []
    for item in os.listdir(checkpoints_dir):
        task_dir = os.path.join(checkpoints_dir, item)
        if os.path.isdir(task_dir):
            checkpoint_files = [f for f in os.listdir(task_dir) if f.startswith('checkpoint_') and f.endswith('.json')]
            if checkpoint_files:
                tasks.append(item)
    
    if tasks:
        print(f"发现训练数据: {', '.join(tasks)}")
        return True
    else:
        print("警告: 未找到有效的训练数据文件")
        return False

def main():
    print("=" * 60)
    print("强化学习真实数据可视化服务器启动器")
    print("=" * 60)
    
    # 检查依赖项
    print("1. 检查依赖项...")
    if not check_dependencies():
        print("依赖项检查失败，退出")
        return
    
    # 检查数据文件
    print("2. 检查训练数据...")
    has_data = check_data_files()
    if not has_data:
        print("将使用模拟数据运行")
    
    # 检查必要文件
    print("3. 检查必要文件...")
    required_files = [
        'web_visualization_server_real_data.py',
        'utils/real_data_loader.py',
        'templates/index_complete.html',
        'static/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"缺少必要文件: {', '.join(missing_files)}")
        print("请确保所有文件都已正确创建")
        return
    
    print("4. 启动服务器...")
    print("=" * 60)
    
    try:
        # 启动服务器
        subprocess.run([sys.executable, 'web_visualization_server_real_data.py'])
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器失败: {e}")

if __name__ == '__main__':
    main()