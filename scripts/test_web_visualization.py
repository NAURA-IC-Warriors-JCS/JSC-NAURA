"""
Web可视化工具功能测试
"""

import requests
import json
import time
import threading
from datetime import datetime

def test_server_connection():
    """测试服务器连接"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Web服务器连接正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    base_url = 'http://localhost:5000'
    
    # 测试启动监控
    try:
        response = requests.post(f'{base_url}/api/start_monitoring')
        if response.status_code == 200:
            print("✅ 启动监控API正常")
        else:
            print("❌ 启动监控API异常")
    except Exception as e:
        print(f"❌ 启动监控API测试失败: {e}")
    
    # 测试设置频率
    try:
        response = requests.post(f'{base_url}/api/set_frequency', 
                               json={'frequency': 20})
        if response.status_code == 200:
            print("✅ 设置频率API正常")
        else:
            print("❌ 设置频率API异常")
    except Exception as e:
        print(f"❌ 设置频率API测试失败: {e}")
    
    # 测试停止监控
    try:
        response = requests.post(f'{base_url}/api/stop_monitoring')
        if response.status_code == 200:
            print("✅ 停止监控API正常")
        else:
            print("❌ 停止监控API异常")
    except Exception as e:
        print(f"❌ 停止监控API测试失败: {e}")

def create_test_data():
    """创建测试数据"""
    import numpy as np
    
    training_history = []
    for i in range(100):
        episode_data = {
            'episode': i,
            'reward': 100 + i * 0.5 + np.random.normal(0, 10),
            'loss': max(0.1, 50 - i * 0.05 + np.random.normal(0, 2)),
            'success_rate': min(100, max(0, 50 + i * 0.1 + np.random.normal(0, 5))),
            'efficiency': max(0, 20 + i * 0.02 + np.random.normal(0, 1)),
            'completion_time': max(10, 100 - i * 0.08 + np.random.normal(0, 3))
        }
        training_history.append(episode_data)
    
    test_data = {
        'training_history': training_history,
        'metadata': {
            'task': 'web_test',
            'algorithm': 'PPO',
            'total_episodes': len(training_history),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    # 保存测试数据
    with open('test_web_data.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print("✅ 测试数据已创建: test_web_data.json")
    return 'test_web_data.json'

def test_data_loading():
    """测试数据加载功能"""
    test_file = create_test_data()
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        response = requests.post('http://localhost:5000/api/load_data',
                               json={'filename': test_file, 'data': data})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ 数据加载测试成功: {result.get('records', 0)} 条记录")
            else:
                print(f"❌ 数据加载失败: {result.get('message', '未知错误')}")
        else:
            print("❌ 数据加载API响应异常")
            
    except Exception as e:
        print(f"❌ 数据加载测试失败: {e}")

def run_comprehensive_test():
    """运行综合测试"""
    print("=" * 60)
    print("🧪 Web可视化工具综合测试")
    print("=" * 60)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    # 测试连接
    if not test_server_connection():
        print("❌ 服务器未启动，请先运行: python start_web_server.py")
        return
    
    # 测试API
    print("\n🔧 测试API端点...")
    test_api_endpoints()
    
    # 测试数据加载
    print("\n📊 测试数据加载...")
    test_data_loading()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("🌐 访问 http://localhost:5000 查看可视化界面")
    print("📱 建议使用Chrome或Edge浏览器获得最佳体验")
    print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_test()