"""
可视化工具
用于分析和展示调度结果
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json
from typing import Dict, List
import pandas as pd

class ScheduleVisualizer:
    """调度结果可视化器"""
    
    def __init__(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_gantt_chart(self, move_list: List[Dict], save_path: str = None):
        """绘制甘特图"""
        # 按模块分组
        modules = {}
        for move in move_list:
            module = move['ModuleName']
            if module not in modules:
                modules[module] = []
            modules[module].append(move)
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 颜色映射
        colors = plt.cm.Set3(np.linspace(0, 1, len(modules)))
        module_colors = dict(zip(modules.keys(), colors))
        
        y_pos = 0
        y_labels = []
        
        for module, moves in modules.items():
            for move in moves:
                start_time = move['StartTime']
                duration = move['EndTime'] - move['StartTime']
                
                # 根据动作类型选择颜色深度
                alpha = 0.7 if move['MoveType'] in [1, 2] else 0.5  # 取放动作更深
                
                rect = patches.Rectangle(
                    (start_time, y_pos), duration, 0.8,
                    facecolor=module_colors[module], alpha=alpha,
                    edgecolor='black', linewidth=0.5
                )
                ax.add_patch(rect)
                
                # 添加文本标签
                if duration > 5:  # 只在较长的操作上显示文本
                    ax.text(start_time + duration/2, y_pos + 0.4, 
                           f"{move['MatID']}", 
                           ha='center', va='center', fontsize=8)
            
            y_labels.append(module)
            y_pos += 1
        
        ax.set_xlim(0, max(move['EndTime'] for move in move_list))
        ax.set_ylim(-0.5, len(modules) - 0.5)
        ax.set_yticks(range(len(modules)))
        ax.set_yticklabels(y_labels)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('设备模块')
        ax.set_title('晶圆调度甘特图')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_wafer_flow(self, move_list: List[Dict], wafer_id: str, save_path: str = None):
        """绘制单个晶圆的流程图"""
        wafer_moves = [move for move in move_list if move['MatID'] == wafer_id]
        
        if not wafer_moves:
            print(f"未找到晶圆 {wafer_id} 的移动记录")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        times = [move['StartTime'] for move in wafer_moves]
        modules = [move['ModuleName'] for move in wafer_moves]
        
        # 创建模块到y坐标的映射
        unique_modules = list(set(modules))
        module_y = {module: i for i, module in enumerate(unique_modules)}
        
        y_coords = [module_y[module] for module in modules]
        
        # 绘制路径
        ax.plot(times, y_coords, 'o-', linewidth=2, markersize=8)
        
        # 添加标签
        for i, (time, module, move) in enumerate(zip(times, modules, wafer_moves)):
            move_type = {1: '取', 2: '放', 3: '移动', 4: '开门', 5: '关门', 
                        6: '抽气', 7: '充气', 8: '处理', 9: '清洁'}
            label = move_type.get(move['MoveType'], '未知')
            ax.annotate(f"{label}\n{time:.1f}s", 
                       (time, module_y[module]), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, ha='left')
        
        ax.set_yticks(range(len(unique_modules)))
        ax.set_yticklabels(unique_modules)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('设备模块')
        ax.set_title(f'晶圆 {wafer_id} 的处理流程')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_utilization(self, move_list: List[Dict], save_path: str = None):
        """绘制设备利用率"""
        # 计算每个模块的利用率
        modules = {}
        total_time = max(move['EndTime'] for move in move_list)
        
        for move in move_list:
            module = move['ModuleName']
            if module not in modules:
                modules[module] = 0
            
            # 只计算处理时间
            if move['MoveType'] == 8:  # 处理动作
                modules[module] += move['EndTime'] - move['StartTime']
        
        # 计算利用率
        utilization = {module: time/total_time*100 for module, time in modules.items()}
        
        # 绘制柱状图
        fig, ax = plt.subplots(figsize=(12, 6))
        
        modules_list = list(utilization.keys())
        util_values = list(utilization.values())
        
        bars = ax.bar(modules_list, util_values)
        
        # 添加数值标签
        for bar, value in zip(bars, util_values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{value:.1f}%', ha='center', va='bottom')
        
        ax.set_ylabel('利用率 (%)')
        ax.set_xlabel('设备模块')
        ax.set_title('设备利用率分析')
        ax.set_ylim(0, max(util_values) * 1.2)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return utilization
    
    def analyze_results(self, result_file: str):
        """分析调度结果"""
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        move_list = data['MoveList']
        total_time = data.get('TotalTime', max(move['EndTime'] for move in move_list))
        
        print(f"=== 调度结果分析 ===")
        print(f"总完工时间: {total_time:.2f} 秒")
        print(f"总移动数量: {len(move_list)}")
        
        # 统计各类动作
        move_types = {}
        for move in move_list:
            move_type = move['MoveType']
            move_types[move_type] = move_types.get(move_type, 0) + 1
        
        type_names = {1: '取晶圆', 2: '放晶圆', 3: '移动', 4: '开门', 5: '关门',
                     6: '抽气', 7: '充气', 8: '处理', 9: '清洁'}
        
        print("\n动作类型统计:")
        for move_type, count in move_types.items():
            name = type_names.get(move_type, f'类型{move_type}')
            print(f"  {name}: {count}")
        
        # 计算设备利用率
        utilization = self.plot_utilization(move_list)
        avg_utilization = np.mean(list(utilization.values()))
        print(f"\n平均设备利用率: {avg_utilization:.2f}%")
        
        # 绘制甘特图
        self.plot_gantt_chart(move_list)
        
        return {
            'total_time': total_time,
            'move_count': len(move_list),
            'move_types': move_types,
            'utilization': utilization,
            'avg_utilization': avg_utilization
        }

def compare_results(result_files: List[str], labels: List[str] = None):
    """比较多个调度结果"""
    if labels is None:
        labels = [f"结果{i+1}" for i in range(len(result_files))]
    
    results = []
    for file in result_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        results.append(data)
    
    # 比较完工时间
    times = [data.get('TotalTime', max(move['EndTime'] for move in data['MoveList'])) 
             for data in results]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, times)
    
    # 添加数值标签
    for bar, time in zip(bars, times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times)*0.01,
                f'{time:.1f}s', ha='center', va='bottom')
    
    plt.ylabel('完工时间 (秒)')
    plt.title('调度结果比较')
    plt.tight_layout()
    plt.show()
    
    # 打印详细比较
    print("=== 结果比较 ===")
    for label, time in zip(labels, times):
        print(f"{label}: {time:.2f}秒")
    
    best_idx = np.argmin(times)
    print(f"\n最佳结果: {labels[best_idx]} ({times[best_idx]:.2f}秒)")