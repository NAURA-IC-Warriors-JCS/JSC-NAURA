"""
系统测试脚本
测试各个组件的功能
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from environment.fab_environment import FabEnvironment
from training.multi_agent_trainer import MultiAgentTrainer
from utils.validator import validate_result_file
from utils.visualization import ScheduleVisualizer

def test_environment():
    """测试环境基本功能"""
    print("=== 测试环境基本功能 ===")
    
    for task in ['a', 'b', 'c', 'd']:
        print(f"\n测试任务 {task.upper()}:")
        
        try:
            env = FabEnvironment(task)
            print(f"  ✅ 环境创建成功")
            print(f"  - 晶圆数量: {len(env.wafers)}")
            print(f"  - 腔室数量: {len(env.chambers)}")
            print(f"  - 机械臂数量: {len(env.robot_arms)}")
            
            # 检查晶圆工艺路径
            process_types = set(wafer.process_type for wafer in env.wafers)
            print(f"  - 工艺类型: {process_types}")
            
        except Exception as e:
            print(f"  ❌ 环境创建失败: {e}")

def test_simple_simulation():
    """测试简单仿真"""
    print("\n=== 测试简单仿真 ===")
    
    try:
        env = FabEnvironment('a')
        
        # 运行几步仿真
        for step in range(5):
            all_done = env.step()
            if all_done:
                break
        
        print(f"  ✅ 仿真运行成功")
        print(f"  - 当前时间: {env.current_time:.2f}秒")
        print(f"  - 移动记录数: {len(env.move_list)}")
        
        # 检查晶圆状态
        completed = sum(1 for wafer in env.wafers if wafer.is_completed())
        print(f"  - 完成晶圆数: {completed}/{len(env.wafers)}")
        
    except Exception as e:
        print(f"  ❌ 仿真运行失败: {e}")

def test_agents():
    """测试智能体功能"""
    print("\n=== 测试智能体功能 ===")
    
    try:
        env = FabEnvironment('a')
        
        # 测试晶圆智能体
        from agents.wafer_agent import WaferAgent
        wafer_agent = WaferAgent(env.wafers[0])
        state = wafer_agent.get_state(env)
        actions = wafer_agent.get_valid_actions(env)
        action = wafer_agent.select_action(state, actions)
        
        print(f"  ✅ 晶圆智能体测试成功")
        print(f"  - 状态维度: {len(state)}")
        print(f"  - 有效动作: {actions}")
        print(f"  - 选择动作: {action}")
        
        # 测试腔室智能体
        from agents.chamber_agent import ChamberAgent
        chamber_agent = ChamberAgent(list(env.chambers.values())[0])
        state = chamber_agent.get_state(env)
        actions = chamber_agent.get_valid_actions(env)
        
        print(f"  ✅ 腔室智能体测试成功")
        print(f"  - 状态维度: {len(state)}")
        print(f"  - 有效动作: {actions}")
        
        # 测试机械臂智能体
        from agents.robot_agent import RobotAgent
        robot_agent = RobotAgent(list(env.robot_arms.values())[0])
        state = robot_agent.get_state(env)
        actions = robot_agent.get_valid_actions(env)
        
        print(f"  ✅ 机械臂智能体测试成功")
        print(f"  - 状态维度: {len(state)}")
        print(f"  - 有效动作: {actions}")
        
    except Exception as e:
        print(f"  ❌ 智能体测试失败: {e}")

def test_training():
    """测试训练功能"""
    print("\n=== 测试训练功能 ===")
    
    try:
        # 创建小规模训练配置
        config = {
            'episodes': 5,
            'max_steps_per_episode': 100,
            'learning_rate': 0.1,
            'epsilon_start': 0.5,
            'epsilon_end': 0.1,
            'epsilon_decay': 0.9,
            'save_interval': 2,
            'log_interval': 1
        }
        
        trainer = MultiAgentTrainer('a', config)
        
        # 运行几个训练回合
        for episode in range(2):
            result = trainer.train_episode()
            print(f"  回合 {episode}: 奖励={result['episode_reward']:.2f}, "
                  f"时间={result['completion_time']:.2f}, "
                  f"完成={result['completed_wafers']}/{len(trainer.env.wafers)}")
        
        print(f"  ✅ 训练功能测试成功")
        
    except Exception as e:
        print(f"  ❌ 训练功能测试失败: {e}")

def test_validation():
    """测试验证功能"""
    print("\n=== 测试验证功能 ===")
    
    try:
        # 创建测试数据
        test_moves = [
            {
                "StartTime": 0.0,
                "EndTime": 1.0,
                "MoveID": 0,
                "MoveType": 4,
                "ModuleName": "PM1",
                "MatID": "1.1",
                "SlotID": 1
            },
            {
                "StartTime": 1.0,
                "EndTime": 5.0,
                "MoveID": 1,
                "MoveType": 1,
                "ModuleName": "TM2_R1",
                "MatID": "1.1",
                "SlotID": 1
            }
        ]
        
        from utils.validator import ConstraintValidator
        validator = ConstraintValidator()
        result = validator.validate_schedule(test_moves)
        
        print(f"  ✅ 验证功能测试成功")
        print(f"  - 验证结果: {'通过' if result['valid'] else '失败'}")
        print(f"  - 违反数量: {result['violation_count']}")
        
    except Exception as e:
        print(f"  ❌ 验证功能测试失败: {e}")

def run_quick_demo():
    """运行快速演示"""
    print("\n=== 运行快速演示 ===")
    
    try:
        # 创建输出目录
        os.makedirs('output', exist_ok=True)
        
        # 运行简单仿真
        env = FabEnvironment('a')
        result = env.run_simulation()
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/demo_result_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 演示完成")
        print(f"  - 结果文件: {filename}")
        print(f"  - 总时间: {result['TotalTime']:.2f}秒")
        print(f"  - 完成晶圆: {result['CompletedWafers']}/{result['TotalWafers']}")
        
        # 验证结果
        validation_result = validate_result_file(filename)
        print(f"  - 约束验证: {'通过' if validation_result['valid'] else '失败'}")
        
        return filename
        
    except Exception as e:
        print(f"  ❌ 演示运行失败: {e}")
        return None

def main():
    """主测试函数"""
    print("开始系统测试...")
    
    # 运行所有测试
    test_environment()
    test_simple_simulation()
    test_agents()
    test_training()
    test_validation()
    
    # 运行演示
    demo_file = run_quick_demo()
    
    print("\n=== 测试总结 ===")
    print("所有基本功能测试完成")
    
    if demo_file:
        print(f"演示结果文件: {demo_file}")
        print("\n可以使用以下命令运行完整仿真:")
        print("python main.py --task a")
        print("\n可以使用以下命令运行强化学习训练:")
        print("python train_rl.py --task a --episodes 100")

if __name__ == "__main__":
    main()
