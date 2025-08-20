#!/usr/bin/env python3
"""
测试matplotlib是否能正常生成图片
"""

import os
import numpy as np
import matplotlib
print(f"Matplotlib版本: {matplotlib.__version__}")
print(f"当前后端: {matplotlib.get_backend()}")

# 强制使用Agg后端
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def test_simple_plot():
    """测试简单图表生成"""
    print("测试简单图表生成...")
    
    # 创建简单数据
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    # 创建图表
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
    plt.title('测试图表')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    
    # 确保输出目录存在
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存图表
    filepath = os.path.join(output_dir, "test_plot.png")
    try:
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ 测试图表已保存: {filepath}")
        return True
    except Exception as e:
        print(f"✗ 保存失败: {e}")
        plt.close()
        return False

def test_reward_plot():
    """测试奖励图表生成"""
    print("测试奖励图表生成...")
    
    # 模拟奖励数据
    episodes = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500]
    rewards = [120000, 125000, 128000, 130000, 131000, 132000, 133000, 132500, 133500]
    
    # 创建图表
    plt.figure(figsize=(10, 6))
    plt.plot(episodes, rewards, 'b-', linewidth=2, marker='o', label='平均奖励')
    plt.title('奖励函数训练曲线测试')
    plt.xlabel('训练轮次')
    plt.ylabel('奖励值')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 添加数值标注
    final_reward = rewards[-1]
    plt.text(0.02, 0.98, f'最终奖励: {final_reward:.0f}', 
            transform=plt.gca().transAxes, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # 保存图表
    filepath = os.path.join("output", "test_reward_plot.png")
    try:
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ 奖励测试图表已保存: {filepath}")
        return True
    except Exception as e:
        print(f"✗ 保存失败: {e}")
        plt.close()
        return False

def main():
    print("=" * 50)
    print("Matplotlib 测试")
    print("=" * 50)
    
    success1 = test_simple_plot()
    success2 = test_reward_plot()
    
    if success1 and success2:
        print("\n✓ 所有测试通过！matplotlib工作正常")
    else:
        print("\n✗ 测试失败，matplotlib可能有问题")
    
    print("=" * 50)

if __name__ == "__main__":
    main()