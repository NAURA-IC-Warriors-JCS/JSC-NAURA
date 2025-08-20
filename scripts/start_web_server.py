"""
简化的Web服务器启动脚本
确保可视化工具能正常运行
"""

import sys
import os

def check_dependencies():
    """检查必要的依赖"""
    try:
        import flask
        import flask_socketio
        import numpy
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install flask flask-socketio numpy")
        return False

def start_server():
    """启动Web服务器"""
    if not check_dependencies():
        return False
    
    try:
        print("🚀 启动强化学习可视化Web服务器...")
        print("📊 访问地址: http://localhost:5000")
        print("⚡ 支持实时数据刷新频率: 1-60 Hz")
        print("🏭 TM1-TM2-TM3物理模型可视化")
        print("=" * 50)
        
        # 导入并启动服务器
        from web_visualization_server import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_server()