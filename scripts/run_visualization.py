"""
启动强化学习可视化工具
支持桌面版和Web版两种模式
"""

import sys
import os
import argparse
import subprocess
import threading
import time

def run_desktop_version():
    """运行桌面版可视化工具"""
    print("启动桌面版强化学习可视化工具...")
    try:
        import tkinter
        from rl_visualization_tool import RLVisualizationTool
        
        app = RLVisualizationTool()
        app.run()
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install matplotlib tkinter numpy seaborn")
        return False
    except Exception as e:
        print(f"启动桌面版失败: {e}")
        return False
    
    return True

def run_web_version():
    """运行Web版可视化工具"""
    print("启动Web版强化学习可视化工具...")
    try:
        # 检查依赖
        import flask
        import flask_socketio
        
        # 启动Web服务器
        from web_visualization_server import app, socketio
        
        print("=" * 60)
        print("🚀 强化学习Web可视化工具已启动!")
        print("📊 访问地址: http://localhost:5000")
        print("⚡ 支持实时数据刷新频率: 1-60 Hz")
        print("🏭 包含TM1-TM2-TM3物理模型可视化")
        print("=" * 60)
        
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install flask flask-socketio")
        return False
    except Exception as e:
        print(f"启动Web版失败: {e}")
        return False
    
    return True

def install_dependencies():
    """安装必要的依赖"""
    print("安装可视化工具依赖...")
    
    dependencies = [
        "matplotlib",
        "numpy", 
        "seaborn",
        "flask",
        "flask-socketio",
        "pandas"
    ]
    
    for dep in dependencies:
        try:
            print(f"安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError:
            print(f"安装 {dep} 失败")
            return False
    
    print("依赖安装完成!")
    return True

def create_sample_data():
    """创建示例数据文件"""
    import json
    import numpy as np
    
    print("创建示例训练数据...")
    
    # 生成示例训练历史数据
    training_history = []
    for i in range(1000):
        episode_data = {
            'episode': i,
            'reward': 100 + i * 0.5 + np.random.normal(0, 10),
            'loss': max(0.1, 50 - i * 0.05 + np.random.normal(0, 2)),
            'success_rate': min(100, max(0, 50 + i * 0.1 + np.random.normal(0, 5))),
            'efficiency': max(0, 20 + i * 0.02 + np.random.normal(0, 1)),
            'completion_time': max(10, 100 - i * 0.08 + np.random.normal(0, 3))
        }
        training_history.append(episode_data)
    
    sample_data = {
        'training_history': training_history,
        'metadata': {
            'task': 'sample',
            'algorithm': 'PPO',
            'total_episodes': len(training_history),
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    # 保存示例数据
    os.makedirs('sample_data', exist_ok=True)
    with open('sample_data/training_data_sample.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print("示例数据已保存到: sample_data/training_data_sample.json")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='强化学习可视化工具')
    parser.add_argument('--mode', choices=['desktop', 'web', 'both'], default='web',
                       help='运行模式: desktop(桌面版), web(Web版), both(同时运行)')
    parser.add_argument('--install', action='store_true', help='安装依赖包')
    parser.add_argument('--sample', action='store_true', help='创建示例数据')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 强化学习绘图分析工具")
    print("📊 支持实时可视化训练数据")
    print("🏭 TM1-TM2-TM3物理模型展示")
    print("⚡ 数据刷新频率可达60Hz")
    print("=" * 60)
    
    # 安装依赖
    if args.install:
        if not install_dependencies():
            return
    
    # 创建示例数据
    if args.sample:
        create_sample_data()
        return
    
    # 运行可视化工具
    if args.mode == 'desktop':
        run_desktop_version()
    elif args.mode == 'web':
        run_web_version()
    elif args.mode == 'both':
        # 在单独线程中运行Web版
        web_thread = threading.Thread(target=run_web_version, daemon=True)
        web_thread.start()
        
        # 等待一下让Web服务器启动
        time.sleep(2)
        
        # 运行桌面版
        run_desktop_version()

if __name__ == "__main__":
    main()
