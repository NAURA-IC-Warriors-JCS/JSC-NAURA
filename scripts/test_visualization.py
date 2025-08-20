"""
可视化工具测试脚本
验证所有功能是否正常工作
"""

import os
import sys
import json
import time
import numpy as np
import subprocess
import threading
from datetime import datetime

def test_dependencies():
    """测试依赖包"""
    print("🔍 测试依赖包...")
    
    required_packages = [
        'matplotlib', 'numpy', 'seaborn', 'pandas',
        'flask', 'flask_socketio', 'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'flask_socketio':
                import flask_socketio
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 缺失")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: python run_visualization.py --install")
        return False
    
    print("✅ 所有依赖包检查通过")
    return True

def create_test_data():
    """创建测试数据"""
    print("📊 创建测试数据...")
    
    # 创建测试目录
    os.makedirs('test_data', exist_ok=True)
    
    # 生成测试训练数据
    training_history = []
    for i in range(500):
        episode_data = {
            'episode': i,
            'reward': 120 + i * 0.8 + np.sin(i * 0.05) * 15 + np.random.normal(0, 8),
            'loss': max(0.1, 60 - i * 0.12 + np.random.exponential(2)),
            'success_rate': min(100, max(0, 40 + i * 0.15 + np.random.normal(0, 6))),
            'efficiency': max(0, 18 + i * 0.04 + np.random.gamma(2, 1)),
            'completion_time': max(5, 80 - i * 0.1 + np.random.lognormal(0, 0.3))
        }
        training_history.append(episode_data)
    
    test_data = {
        'training_history': training_history,
        'metadata': {
            'task': 'test_task',
            'algorithm': 'PPO',
            'total_episodes': len(training_history),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'test_mode': True
        }
    }
    
    # 保存测试数据
    test_file = 'test_data/test_training_data.json'
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 测试数据已保存: {test_file}")
    return test_file

def test_desktop_version():
    """测试桌面版"""
    print("🖥️  测试桌面版...")
    
    try:
        # 导入桌面版模块
        from rl_visualization_tool import RLVisualizationTool
        
        # 创建实例但不运行GUI
        app = RLVisualizationTool()
        
        # 测试数据加载功能
        test_file = create_test_data()
        app.load_training_data(test_file)
        
        print("✅ 桌面版基础功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 桌面版测试失败: {e}")
        return False

def test_web_server():
    """测试Web服务器"""
    print("🌐 测试Web服务器...")
    
    try:
        # 导入Web服务器模块
        from web_visualization_server import WebRLVisualizer
        
        # 创建可视化器实例
        visualizer = WebRLVisualizer()
        
        # 测试数据生成
        visualizer.simulate_real_time_data()
        
        # 检查数据是否正确生成
        if len(visualizer.training_data['episodes']) > 0:
            print("✅ Web服务器数据生成测试通过")
        else:
            print("❌ Web服务器数据生成失败")
            return False
        
        # 测试物理模型数据
        if 'robot_arm_angle' in visualizer.physics_data:
            print("✅ 物理模型数据测试通过")
        else:
            print("❌ 物理模型数据测试失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web服务器测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("📁 测试文件结构...")
    
    required_files = [
        'rl_visualization_tool.py',
        'web_visualization_server.py', 
        'run_visualization.py',
        'templates/index.html',
        'VISUALIZATION_README.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - 缺失")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 文件结构检查通过")
    return True

def test_data_format():
    """测试数据格式"""
    print("📋 测试数据格式...")
    
    # 测试现有的检查点数据
    checkpoint_dirs = ['checkpoints/task_a', 'checkpoints/task_b', 'checkpoints/task_d']
    
    valid_data_found = False
    
    for checkpoint_dir in checkpoint_dirs:
        if os.path.exists(checkpoint_dir):
            files = [f for f in os.listdir(checkpoint_dir) if f.endswith('.json')]
            if files:
                try:
                    with open(os.path.join(checkpoint_dir, files[0]), 'r') as f:
                        data = json.load(f)
                    print(f"  ✅ {checkpoint_dir} - 数据格式正确")
                    valid_data_found = True
                except Exception as e:
                    print(f"  ❌ {checkpoint_dir} - 数据格式错误: {e}")
    
    if not valid_data_found:
        print("  ⚠️  未找到有效的检查点数据，将使用测试数据")
    
    return True

def run_quick_demo():
    """运行快速演示"""
    print("🎬 运行快速演示...")
    
    try:
        # 启动Web服务器演示
        print("启动Web服务器演示 (5秒)...")
        
        def demo_server():
            from web_visualization_server import WebRLVisualizer
            visualizer = WebRLVisualizer()
            
            # 生成一些演示数据
            for i in range(10):
                visualizer.simulate_real_time_data()
                time.sleep(0.1)
            
            print(f"  生成了 {len(visualizer.training_data['episodes'])} 个数据点")
        
        demo_thread = threading.Thread(target=demo_server)
        demo_thread.start()
        demo_thread.join(timeout=5)
        
        print("✅ 快速演示完成")
        return True
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 强化学习可视化工具测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("依赖包检查", test_dependencies),
        ("文件结构检查", test_file_structure), 
        ("数据格式检查", test_data_format),
        ("桌面版测试", test_desktop_version),
        ("Web服务器测试", test_web_server),
        ("快速演示", run_quick_demo)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔄 {test_name}...")
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            test_results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！可视化工具已准备就绪")
        print("\n🚀 启动建议:")
        print("  - Web版: python run_visualization.py --mode web")
        print("  - 桌面版: python run_visualization.py --mode desktop")
        print("  - 或直接运行: start_visualization.bat")
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查相关问题")
        
        if not test_results[0][1]:  # 依赖包检查失败
            print("  建议先运行: python run_visualization.py --install")

if __name__ == "__main__":
    main()