"""
强化学习可视化工具启动脚本
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖包"""
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
        for package in missing_packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("依赖包安装完成!")

def start_visualization():
    """启动可视化工具"""
    print("🚀 启动强化学习可视化分析工具...")
    print("=" * 50)
    
    # 检查依赖
    check_dependencies()
    
    # 启动Web服务器
    try:
        print("📡 启动Web服务器...")
        print("🌐 访问地址: http://localhost:5000")
        print("⏹️  按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 延迟打开浏览器
        import threading
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动服务器
        subprocess.run([sys.executable, 'web_visualization_server.py'])
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查端口5000是否被占用")

if __name__ == "__main__":
    start_visualization()