"""
测试增强版可视化工具的所有功能
验证坐标系统、拖拽功能、柱状图等
"""

import requests
import json
import time
import threading
from pathlib import Path

class EnhancedVisualizationTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_server_connection(self):
        """测试服务器连接"""
        try:
            response = requests.get(self.base_url, timeout=5)
            success = response.status_code == 200
            self.log_test("服务器连接", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("服务器连接", False, str(e))
            return False
    
    def test_api_endpoints(self):
        """测试API端点"""
        endpoints = [
            ('/api/status', 'GET'),
            ('/api/start_monitoring', 'POST'),
            ('/api/stop_monitoring', 'POST'),
            ('/api/set_frequency', 'POST')
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    data = {'frequency': 15} if 'frequency' in endpoint else {}
                    response = requests.post(f"{self.base_url}{endpoint}", 
                                           json=data, timeout=5)
                
                success = response.status_code == 200
                self.log_test(f"API {endpoint}", success, 
                            f"{method} {response.status_code}")
            except Exception as e:
                self.log_test(f"API {endpoint}", False, str(e))
    
    def test_template_files(self):
        """测试模板文件"""
        templates_dir = Path('templates')
        required_files = [
            'index_enhanced.html',
            'index.html'
        ]
        
        for file_name in required_files:
            file_path = templates_dir / file_name
            exists = file_path.exists()
            self.log_test(f"模板文件 {file_name}", exists)
            
            if exists:
                # 检查文件内容
                try:
                    content = file_path.read_text(encoding='utf-8')
                    has_coordinates = 'TM1: (350, 50)' in content or 'top: 50px' in content
                    has_draggable = 'draggable-module' in content
                    has_charts = 'barChart' in content or 'Chart.js' in content
                    
                    self.log_test(f"  坐标系统", has_coordinates)
                    self.log_test(f"  拖拽功能", has_draggable)
                    self.log_test(f"  图表功能", has_charts)
                except Exception as e:
                    self.log_test(f"  文件读取", False, str(e))
    
    def test_data_format(self):
        """测试数据格式"""
        try:
            # 测试历史数据加载
            test_data = {
                'filename': 'test_data.json',
                'data': {
                    'episodes': [1, 2, 3, 4, 5],
                    'rewards': [100, 150, 200, 250, 300],
                    'losses': [0.5, 0.4, 0.3, 0.2, 0.1],
                    'success_rates': [60, 70, 80, 85, 90],
                    'efficiency': [50, 60, 70, 75, 80]
                }
            }
            
            response = requests.post(f"{self.base_url}/api/load_data", 
                                   json=test_data, timeout=5)
            
            success = response.status_code == 200
            if success:
                result = response.json()
                success = result.get('status') == 'success'
                message = f"加载了 {result.get('records', 0)} 条记录"
            else:
                message = f"HTTP {response.status_code}"
            
            self.log_test("数据格式验证", success, message)
        except Exception as e:
            self.log_test("数据格式验证", False, str(e))
    
    def test_coordinate_system(self):
        """测试坐标系统"""
        # 检查CSS中的坐标定义
        try:
            template_path = Path('templates/index_enhanced.html')
            if template_path.exists():
                content = template_path.read_text(encoding='utf-8')
                
                # 检查TM模块坐标
                tm1_coords = 'top: 50px' in content and 'left: 290px' in content
                tm2_coords = 'top: 150px' in content and 'left: 275px' in content  
                tm3_coords = 'top: 400px' in content and 'left: 275px' in content
                
                self.log_test("TM1坐标 (350,50)", tm1_coords)
                self.log_test("TM2坐标 (350,200)", tm2_coords)
                self.log_test("TM3坐标 (350,450)", tm3_coords)
                
                # 检查正八边形
                octagon_clip = 'clip-path: polygon' in content
                self.log_test("正八边形样式", octagon_clip)
                
                # 检查腔室圆形
                chamber_circle = 'border-radius: 50%' in content
                self.log_test("圆形腔室", chamber_circle)
                
            else:
                self.log_test("坐标系统检查", False, "模板文件不存在")
        except Exception as e:
            self.log_test("坐标系统检查", False, str(e))
    
    def test_enhanced_features(self):
        """测试增强功能"""
        try:
            template_path = Path('templates/index_enhanced.html')
            if template_path.exists():
                content = template_path.read_text(encoding='utf-8')
                
                # 检查科技感配色
                gradient_bg = 'linear-gradient' in content and '#0a0e27' in content
                self.log_test("科技感配色", gradient_bg)
                
                # 检查拖拽功能
                drag_events = 'mousedown' in content and 'dragging' in content
                self.log_test("拖拽事件处理", drag_events)
                
                # 检查柱状图
                bar_chart = 'barChart' in content and "type: 'bar'" in content
                self.log_test("柱状图功能", bar_chart)
                
                # 检查连接线
                connection_lines = 'connection-line' in content
                self.log_test("TM连接线", connection_lines)
                
                # 检查180度机械臂
                arm_180 = '+ 180' in content and 'robot-arm' in content
                self.log_test("180度机械臂", arm_180)
                
            else:
                self.log_test("增强功能检查", False, "模板文件不存在")
        except Exception as e:
            self.log_test("增强功能检查", False, str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始测试增强版可视化工具")
        print("=" * 50)
        
        # 基础连接测试
        print("\n📡 基础连接测试:")
        if not self.test_server_connection():
            print("⚠️  服务器未运行，跳过API测试")
            print("请先运行: python start_enhanced_visualization.py")
        else:
            print("\n🔌 API端点测试:")
            self.test_api_endpoints()
            
            print("\n📊 数据功能测试:")
            self.test_data_format()
        
        # 文件和功能测试
        print("\n📁 模板文件测试:")
        self.test_template_files()
        
        print("\n📍 坐标系统测试:")
        self.test_coordinate_system()
        
        print("\n✨ 增强功能测试:")
        self.test_enhanced_features()
        
        # 汇总结果
        print("\n" + "=" * 50)
        print("📋 测试结果汇总:")
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ 通过: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed < total:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n🎯 功能验证:")
        feature_checks = [
            ("严格坐标系统", any("坐标" in r['test'] and r['success'] for r in self.test_results)),
            ("可拖拽模块", any("拖拽" in r['test'] and r['success'] for r in self.test_results)),
            ("柱状图展示", any("柱状图" in r['test'] and r['success'] for r in self.test_results)),
            ("科技感配色", any("配色" in r['test'] and r['success'] for r in self.test_results)),
            ("180度机械臂", any("机械臂" in r['test'] and r['success'] for r in self.test_results))
        ]
        
        for feature, status in feature_checks:
            icon = "✅" if status else "❌"
            print(f"   {icon} {feature}")

def main():
    """主函数"""
    tester = EnhancedVisualizationTester()
    tester.run_all_tests()
    
    print("\n🚀 测试完成!")
    print("如需启动可视化工具，请运行:")
    print("   python start_enhanced_visualization.py")

if __name__ == "__main__":
    main()
