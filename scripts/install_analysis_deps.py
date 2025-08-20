#!/usr/bin/env python3
"""
安装分析工具所需的依赖包
"""

import subprocess
import sys

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔧 安装强化学习分析工具依赖包")
    print("=" * 50)
    
    # 必需的包
    required_packages = [
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0", 
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0"
    ]
    
    print("📦 需要安装的包:")
    for pkg in required_packages:
        print(f"   - {pkg}")
    
    print("\n🚀 开始安装...")
    
    success_count = 0
    for package in required_packages:
        print(f"\n安装 {package}...")
        if install_package(package):
            print(f"✅ {package} 安装成功")
            success_count += 1
        else:
            print(f"❌ {package} 安装失败")
    
    print(f"\n📊 安装结果: {success_count}/{len(required_packages)} 成功")
    
    if success_count == len(required_packages):
        print("🎉 所有依赖包安装完成!")
        print("\n现在可以运行分析工具:")
        print("python quick_analysis.py")
    else:
        print("⚠️  部分包安装失败，请手动安装或检查网络连接")
        print("\n手动安装命令:")
        for package in required_packages:
            print(f"pip install {package}")

if __name__ == "__main__":
    main()