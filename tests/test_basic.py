#!/usr/bin/env python3
"""
基础测试模块
"""

import pytest
import sys
import os

def test_python_version():
    """测试Python版本"""
    assert sys.version_info >= (3, 8)

def test_project_structure():
    """测试项目结构"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    # 检查主要目录
    expected_dirs = [
        'src',
        'data', 
        'tests',
        'scripts',
        'web',
        'examples',
        'docs'
    ]
    
    for dir_name in expected_dirs:
        dir_path = os.path.join(project_root, dir_name)
        assert os.path.exists(dir_path), f"Directory {dir_name} should exist"

def test_requirements_file():
    """测试requirements.txt文件存在"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    requirements_path = os.path.join(project_root, 'requirements.txt')
    assert os.path.exists(requirements_path), "requirements.txt should exist"