"""
测试修复后的训练系统
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fixed_wafer_agent():
    """测试修复后的晶圆智能体"""
    print("=== 测试修复后的晶圆智能体 ===")
    
    try:
        from environment.fab_environment import FabEnvironment
        from agents.wafer_agent_fixed import WaferAgent
        
        env = FabEnvironment('a')
        wafer = env.wafers[0]
        agent = WaferAgent(wafer)
        
        # 测试状态获取
        state = agent.get_state(env)
        print(f"✅ 状态获取成功: 维度={len(state)}, 类型={type(state[0])}")
        
        # 测试动作选择
        valid_actions = agent.get_valid_actions(env)
        action = agent.select_action(state, valid_actions)
        print(f"✅ 动作选择成功: 有效动作={valid_actions}, 选择={action}")
        
        # 测试策略更新
        next_state = agent.get_state(env)
        agent.update_policy(state, action, 1.0, next_state, False)
        print(f"✅ 策略更新成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_fixed_trainer():
    """测试修复后的训练器"""
    print("\n=== 测试修复后的训练器 ===")
    
    try:
        from training.multi_agent_trainer_fixed import MultiAgentTrainer
        
        # 小规模测试配置
        config = {
            'episodes': 3,
            'max_steps_per_episode': 50,
            'learning_rate': 0.1,
            'epsilon_start': 0.5,
            'epsilon_end': 0.1,
            'epsilon_decay': 0.9,
            'save_interval': 2,
            'log_interval': 1
        }
        
        trainer = MultiAgentTrainer('a', config)
        print(f"✅ 训练器创建成功")
        
        # 运行几个训练回合
        for episode in range(2):
            result = trainer.train_episode()
            print(f"✅ 回合 {episode}: 奖励={result['episode_reward']:.2f}, "
                  f"完成={result['completed_wafers']}/{len(trainer.env.wafers)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quick_training():
    """测试快速训练"""
    print("\n=== 测试快速训练 ===")
    
    try:
        import subprocess
        
        # 运行修复后的训练脚本
        command = "python train_rl_fixed.py --task a --episodes 5 --max_steps 100"
        print(f"执行命令: {command}")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 快速训练成功")
            if result.stdout:
                print("输出:")
                print(result.stdout[-500:])  # 只显示最后500字符
            return True
        else:
            print("❌ 快速训练失败")
            if result.stderr:
                print("错误:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_output_files():
    """检查输出文件"""
    print("\n=== 检查输出文件 ===")
    
    if not os.path.exists('output'):
        print("❌ 输出目录不存在")
        return False
    
    json_files = [f for f in os.listdir('output') if f.endswith('.json')]
    
    if not json_files:
        print("❌ 未找到JSON结果文件")
        return False
    
    print(f"✅ 找到 {len(json_files)} 个结果文件:")
    
    for file in json_files:
        filepath = os.path.join('output', file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            move_count = len(data.get('MoveList', []))
            total_time = data.get('TotalTime', 0)
            
            print(f"  - {file}: {move_count} 个移动, 总时间 {total_time:.2f}s")
            
            # 验证数据格式
            if 'MoveList' in data and isinstance(data['MoveList'], list):
                print(f"    ✅ 格式正确")
            else:
                print(f"    ❌ 格式错误")
                
        except Exception as e:
            print(f"  - {file}: ❌ 读取失败 ({e})")
    
    return True

def main():
    """主测试函数"""
    print("开始测试修复后的训练系统...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建必要目录
    os.makedirs('output', exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)
    
    tests = [
        ("晶圆智能体", test_fixed_wafer_agent),
        ("训练器", test_fixed_trainer),
        ("快速训练", test_quick_training),
        ("输出文件", check_output_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"测试: {test_name}")
        print(f"{'='*50}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ 测试 {test_name} 出现异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print(f"\n{'='*50}")
    print("测试总结")
    print(f"{'='*50}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总体结果: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过! 系统修复成功!")
        print("\n可以使用以下命令运行完整训练:")
        print("python train_rl_fixed.py --task a --episodes 200")
        print("python train_rl_fixed.py --task b --episodes 200")
    else:
        print("⚠️  部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()