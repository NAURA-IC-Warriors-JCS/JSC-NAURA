"""
启动增强版强化学习可视化工具
包含严格坐标系统、可拖拽模块、柱状图展示
"""

import subprocess
import sys
import time
import webbrowser
import threading
import os
from pathlib import Path

def check_and_install_dependencies():
    """检查并安装依赖包"""
    required_packages = [
        'flask',
        'flask-socketio', 
        'numpy',
        'eventlet'  # 添加eventlet以提高性能
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'flask-socketio':
                import flask_socketio
            elif package == 'eventlet':
                import eventlet
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"🔧 安装缺少的依赖包: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
                return False
        print("🎉 所有依赖包安装完成!")
    
    return True

def check_templates():
    """检查模板文件"""
    templates_dir = Path('templates')
    if not templates_dir.exists():
        print("❌ templates 目录不存在")
        return False
    
    enhanced_template = templates_dir / 'index_enhanced.html'
    if not enhanced_template.exists():
        print("❌ index_enhanced.html 模板不存在")
        return False
    
    print("✅ 模板文件检查通过")
    return True

def open_browser_delayed():
    """延迟打开浏览器"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 浏览器已打开: http://localhost:5000")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:5000")

def main():
    """主函数"""
    print("🚀 强化学习可视化工具 - 增强版启动器")
    print("=" * 60)
    
    # 检查依赖
    print("🔍 检查依赖包...")
    if not check_and_install_dependencies():
        print("❌ 依赖包安装失败，请手动安装")
        return
    
    # 检查模板
    print("🔍 检查模板文件...")
    if not check_templates():
        print("❌ 模板文件检查失败")
        return
    
    # 检查服务器文件
    server_file = 'web_visualization_server_fixed.py'
    if not os.path.exists(server_file):
        print(f"❌ 服务器文件不存在: {server_file}")
        return
    
    print("✅ 所有检查通过!")
    print("\n🎯 功能特色:")
    print("   📍 严格坐标系统 - TM1(350,50), TM2(350,200), TM3(350,450)")
    print("   🖱️  可拖拽模块 - 所有TM和腔室模块支持鼠标拖拽")
    print("   📊 柱状图展示 - 实时数据柱状图和折线图")
    print("   🎨 科技感配色 - 深蓝渐变背景，霓虹色彩")
    print("   🔄 180度机械臂 - TM2与TM3固定180度角差")
    print("   ⚡ 高频刷新 - 支持1-60Hz数据更新")
    
    print("\n🌐 启动Web服务器...")
    
    try:
        # 启动浏览器线程
        browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
        browser_thread.start()
        
        # 启动服务器
        subprocess.run([sys.executable, server_file])
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断，服务器已停止")
    except FileNotFoundError:
        print(f"❌ 找不到Python解释器或服务器文件")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n🔧 故障排除:")
        print("1. 检查Python版本 >= 3.7")
        print("2. 检查端口5000是否被占用")
        print("3. 检查防火墙设置")
        print("4. 尝试手动运行: python web_visualization_server_fixed.py")

if __name__ == "__main__":
    main()