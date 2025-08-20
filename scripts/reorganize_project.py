#!/usr/bin/env python3
"""
重新整理项目结构，符合GitHub标准
"""

import os
import shutil
from pathlib import Path

def create_github_structure():
    """创建标准的GitHub项目结构"""
    
    # 定义新的目录结构
    directories = [
        'src',
        'src/agents',
        'src/environment', 
        'src/training',
        'src/utils',
        'src/config',
        'data',
        'data/checkpoints',
        'data/output',
        'docs',
        'examples',
        'tests',
        'scripts',
        'web',
        'web/templates',
        'web/static',
        '.github',
        '.github/workflows'
    ]
    
    # 创建目录
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    # 移动文件到新结构
    file_moves = [
        # 源代码文件
        ('agents/', 'src/agents/'),
        ('environment/', 'src/environment/'),
        ('training/', 'src/training/'),
        ('utils/', 'src/utils/'),
        ('config/', 'src/config/'),
        
        # 数据文件
        ('checkpoints/', 'data/checkpoints/'),
        ('output/', 'data/output/'),
        ('analysis/', 'data/analysis/'),
        
        # Web文件
        ('templates/', 'web/templates/'),
        ('static/', 'web/static/'),
        
        # 主要脚本
        ('main.py', 'src/main.py'),
        ('train_rl.py', 'src/train_rl.py'),
        ('train_rl_fixed.py', 'src/train_rl_fixed.py'),
    ]
    
    # 执行文件移动
    for src, dst in file_moves:
        if os.path.exists(src):
            try:
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.move(src, dst)
                else:
                    shutil.move(src, dst)
                print(f"✓ 移动: {src} -> {dst}")
            except Exception as e:
                print(f"✗ 移动失败: {src} -> {dst}, 错误: {e}")
    
    # 移动脚本文件到scripts目录
    script_files = [
        'run_all_tasks.py',
        'run_analysis.py', 
        'run_visualization.py',
        'quick_analysis.py',
        'analyze_training.py',
        'generate_reward_plots.py',
        'simple_reward_plot.py',
        'actual_training_with_plots.py',
        'train_with_live_plotting.py',
        'test_system.py',
        'test_fixed_training.py',
        'test_matplotlib.py',
        'install_analysis_deps.py'
    ]
    
    for script in script_files:
        if os.path.exists(script):
            try:
                shutil.move(script, f'scripts/{script}')
                print(f"✓ 移动脚本: {script} -> scripts/{script}")
            except Exception as e:
                print(f"✗ 移动脚本失败: {script}, 错误: {e}")
    
    # 移动Web相关文件
    web_files = [
        'web_visualization_server.py',
        'web_visualization_server_fixed.py', 
        'web_visualization_server_final.py',
        'web_visualization_server_real_data.py',
        'web_visualization_server_optimized.py',
        'web_visualization_1800x900.py',
        'start_web_server.py',
        'start_enhanced_visualization.py',
        'start_real_data_visualization.py',
        'start_rl_visualization.py'
    ]
    
    for web_file in web_files:
        if os.path.exists(web_file):
            try:
                shutil.move(web_file, f'web/{web_file}')
                print(f"✓ 移动Web文件: {web_file} -> web/{web_file}")
            except Exception as e:
                print(f"✗ 移动Web文件失败: {web_file}, 错误: {e}")
    
    # 移动可视化工具到examples
    viz_files = [
        'rl_visualization_tool.py',
        'rl_visualization_tool_real_data.py',
        'test_real_data_tool.py',
        'test_enhanced_features.py',
        'test_web_visualization.py',
        'test_visualization.py'
    ]
    
    for viz_file in viz_files:
        if os.path.exists(viz_file):
            try:
                shutil.move(viz_file, f'examples/{viz_file}')
                print(f"✓ 移动示例: {viz_file} -> examples/{viz_file}")
            except Exception as e:
                print(f"✗ 移动示例失败: {viz_file}, 错误: {e}")
    
    # 移动文档文件
    doc_files = [
        'README.md',
        'ANALYSIS_README.md', 
        'RL_VISUALIZATION_GUIDE.md',
        'VISUALIZATION_README.md'
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file) and doc_file != 'README.md':
            try:
                shutil.move(doc_file, f'docs/{doc_file}')
                print(f"✓ 移动文档: {doc_file} -> docs/{doc_file}")
            except Exception as e:
                print(f"✗ 移动文档失败: {doc_file}, 错误: {e}")

if __name__ == "__main__":
    print("🔄 开始重新整理项目结构...")
    create_github_structure()
    print("✅ 项目结构整理完成！")