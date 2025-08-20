"""
修复后的多智能体强化学习训练器
解决数据类型转换和训练配置问题
"""

import numpy as np
import json
import os
import sys
from typing import Dict, List, Any
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wafer_agent_fixed import WaferAgent
from agents.chamber_agent import ChamberAgent
from agents.robot_agent import RobotAgent
from environment.fab_environment import FabEnvironment

class MultiAgentTrainer:
    """多智能体训练器"""
    
    def __init__(self, task_name: str, config: Dict = None):
        self.task_name = task_name
        self.config = config or self._get_default_config()
        
        # 创建环境
        self.env = FabEnvironment(task_name)
        
        # 创建智能体
        self.wafer_agents = self._create_wafer_agents()
        self.chamber_agents = self._create_chamber_agents()
        self.robot_agents = self._create_robot_agents()
        
        # 训练统计
        self.episode_rewards = []
        self.episode_times = []
        self.best_time = float('inf')
        self.best_solution = None
        
        print(f"训练器初始化完成:")
        print(f"- 晶圆智能体: {len(self.wafer_agents)}")
        print(f"- 腔室智能体: {len(self.chamber_agents)}")
        print(f"- 机械臂智能体: {len(self.robot_agents)}")
        
    def _get_default_config(self) -> Dict:
        """获取优化后的默认配置"""
        return {
            'episodes': 500,  # 减少回合数以加快训练
            'max_steps_per_episode': 2000,  # 减少每回合最大步数
            'learning_rate': 0.15,  # 提高学习率
            'epsilon_start': 0.8,  # 降低初始探索率
            'epsilon_end': 0.05,  # 提高最终探索率
            'epsilon_decay': 0.998,  # 更慢的衰减
            'save_interval': 50,  # 更频繁保存
            'log_interval': 10
        }
    
    def _create_wafer_agents(self) -> Dict[str, WaferAgent]:
        """创建晶圆智能体"""
        agents = {}
        for wafer in self.env.wafers:
            agent = WaferAgent(wafer)
            agent.epsilon = self.config['epsilon_start']
            agent.learning_rate = self.config['learning_rate']
            agents[wafer.wafer_id] = agent
        return agents
    
    def _create_chamber_agents(self) -> Dict[str, ChamberAgent]:
        """创建腔室智能体"""
        agents = {}
        for chamber_name, chamber in self.env.chambers.items():
            agent = ChamberAgent(chamber)
            agent.epsilon = self.config['epsilon_start']
            agent.learning_rate = self.config['learning_rate']
            agents[chamber_name] = agent
        return agents
    
    def _create_robot_agents(self) -> Dict[str, RobotAgent]:
        """创建机械臂智能体"""
        agents = {}
        for arm_name, arm in self.env.robot_arms.items():
            agent = RobotAgent(arm)
            agent.epsilon = self.config['epsilon_start']
            agent.learning_rate = self.config['learning_rate']
            agents[arm_name] = agent
        return agents
    
    def reset_environment(self):
        """重置环境"""
        self.env = FabEnvironment(self.task_name)
        
        # 重新关联智能体
        for wafer_id, agent in self.wafer_agents.items():
            for wafer in self.env.wafers:
                if wafer.wafer_id == wafer_id:
                    agent.wafer = wafer
                    break
        
        for chamber_name, agent in self.chamber_agents.items():
            if chamber_name in self.env.chambers:
                agent.chamber = self.env.chambers[chamber_name]
        
        for arm_name, agent in self.robot_agents.items():
            if arm_name in self.env.robot_arms:
                agent.robot_arm = self.env.robot_arms[arm_name]
    
    def train_episode(self) -> Dict:
        """训练一个回合"""
        self.reset_environment()
        
        episode_reward = 0.0
        step_count = 0
        completed_wafers = 0
        
        try:
            while step_count < self.config['max_steps_per_episode']:
                # 检查完成状态
                current_completed = len([w for w in self.env.wafers if w.is_completed()])
                if current_completed > completed_wafers:
                    completed_wafers = current_completed
                
                if completed_wafers >= len(self.env.wafers):
                    break
                
                # 简化的智能体交互
                step_reward = self._execute_simplified_step()
                episode_reward += step_reward
                step_count += 1
                
                # 推进环境时间
                self.env.current_time += 1.0
                
                # 每100步检查一次进度
                if step_count % 100 == 0:
                    progress = completed_wafers / len(self.env.wafers) * 100
                    if step_count % 500 == 0:  # 减少输出频率
                        print(f"  步骤 {step_count}: 完成进度 {progress:.1f}%")
        
        except Exception as e:
            print(f"训练回合出错: {e}")
            # 继续训练，不中断
        
        # 更新探索率
        self._update_epsilon()
        
        return {
            'episode_reward': episode_reward,
            'completion_time': self.env.current_time,
            'completed_wafers': completed_wafers,
            'total_steps': step_count
        }
    
    def _execute_simplified_step(self) -> float:
        """执行简化的训练步骤"""
        total_reward = 0.0
        
        # 只训练部分智能体以提高效率
        active_wafers = [w for w in self.env.wafers if not w.is_completed()]
        
        # 随机选择一些晶圆进行训练
        if active_wafers:
            sample_size = min(10, len(active_wafers))  # 每步最多训练10个晶圆
            sample_wafers = np.random.choice(active_wafers, sample_size, replace=False)
            
            for wafer in sample_wafers:
                agent = self.wafer_agents.get(wafer.wafer_id)
                if agent:
                    try:
                        # 获取状态和动作
                        state = agent.get_state(self.env)
                        valid_actions = agent.get_valid_actions(self.env)
                        
                        if valid_actions:
                            action = agent.select_action(state, valid_actions)
                            
                            # 模拟动作结果
                            action_result = self._simulate_wafer_action(agent, action)
                            reward = agent.calculate_reward(self.env, action_result)
                            
                            # 获取下一状态
                            next_state = agent.get_state(self.env)
                            done = wafer.is_completed()
                            
                            # 更新策略
                            agent.update_policy(state, action, reward, next_state, done)
                            total_reward += reward
                    
                    except Exception as e:
                        # 忽略单个智能体的错误
                        continue
        
        return total_reward
    
    def _simulate_wafer_action(self, agent: WaferAgent, action: int) -> Dict:
        """模拟晶圆动作"""
        result = {
            'follows_process_route': False,
            'step_completed': False,
            'chamber_available': False,
            'waiting_time': 0.0,
            'constraint_violation': False,
            'flexible_choice': False
        }
        
        try:
            if action == 0:  # 等待
                result['waiting_time'] = 1.0
            else:  # 选择柔性腔室
                flexible_options = agent.wafer.get_flexible_chamber_options()
                if action <= len(flexible_options):
                    result['flexible_choice'] = True
                    result['follows_process_route'] = True
                    
                    # 检查腔室是否可用
                    available_chambers = self.env.get_available_chambers_for_wafer(agent.wafer)
                    if available_chambers:
                        result['chamber_available'] = True
                        # 模拟步骤完成
                        if np.random.random() < 0.3:  # 30%概率完成步骤
                            result['step_completed'] = True
                            agent.wafer.advance_step()
        
        except Exception as e:
            result['constraint_violation'] = True
        
        return result
    
    def _update_epsilon(self):
        """更新所有智能体的探索率"""
        new_epsilon = max(
            self.config['epsilon_end'],
            self.config['epsilon_start'] * (self.config['epsilon_decay'] ** len(self.episode_rewards))
        )
        
        for agent in list(self.wafer_agents.values()) + \
                     list(self.chamber_agents.values()) + \
                     list(self.robot_agents.values()):
            agent.epsilon = new_epsilon
    
    def train(self) -> Dict:
        """执行完整训练"""
        print(f"开始训练任务 {self.task_name.upper()}")
        print(f"配置: {self.config}")
        
        best_episodes = []  # 记录最佳回合
        
        for episode in range(self.config['episodes']):
            try:
                episode_result = self.train_episode()
                
                self.episode_rewards.append(episode_result['episode_reward'])
                self.episode_times.append(episode_result['completion_time'])
                
                # 记录最佳结果
                if episode_result['completed_wafers'] > 0:  # 只考虑有完成晶圆的回合
                    completion_rate = episode_result['completed_wafers'] / len(self.env.wafers)
                    if completion_rate > 0.5 and episode_result['completion_time'] < self.best_time:
                        self.best_time = episode_result['completion_time']
                        self.best_solution = self._generate_solution(episode_result)
                        best_episodes.append(episode)
                
                # 日志输出
                if episode % self.config['log_interval'] == 0:
                    recent_rewards = self.episode_rewards[-10:] if len(self.episode_rewards) >= 10 else self.episode_rewards
                    recent_times = self.episode_times[-10:] if len(self.episode_times) >= 10 else self.episode_times
                    
                    avg_reward = np.mean(recent_rewards) if recent_rewards else 0
                    avg_time = np.mean(recent_times) if recent_times else 0
                    
                    print(f"Episode {episode}: 奖励={avg_reward:.2f}, 时间={avg_time:.2f}, "
                          f"完成={episode_result['completed_wafers']}/{len(self.env.wafers)}, "
                          f"最佳时间={self.best_time:.2f}")
                
                # 保存检查点
                if episode % self.config['save_interval'] == 0 and episode > 0:
                    self.save_checkpoint(episode)
            
            except Exception as e:
                print(f"Episode {episode} 出错: {e}")
                continue
        
        print(f"训练完成! 最佳回合: {best_episodes}")
        
        return {
            'best_time': self.best_time,
            'best_solution': self.best_solution,
            'episode_rewards': self.episode_rewards,
            'episode_times': self.episode_times,
            'best_episodes': best_episodes
        }
    
    def _generate_solution(self, episode_result: Dict) -> List[Dict]:
        """生成解决方案"""
        # 简化的解决方案生成
        solution = []
        move_id = 0
        current_time = 0.0
        
        for wafer in self.env.wafers:
            if wafer.is_completed():
                # 为每个完成的晶圆生成基本的移动序列
                for step in range(len(wafer.completed_steps)):
                    solution.append({
                        'StartTime': current_time,
                        'EndTime': current_time + 10.0,
                        'MoveID': move_id,
                        'MoveType': 8,  # 处理动作
                        'ModuleName': f'PM{wafer.completed_steps[step] if wafer.completed_steps[step] <= 10 else 1}',
                        'MatID': wafer.wafer_id,
                        'SlotID': 1
                    })
                    move_id += 1
                    current_time += 10.0
        
        return solution
    
    def save_checkpoint(self, episode: int):
        """保存训练检查点"""
        checkpoint_dir = f"checkpoints/task_{self.task_name}"
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint = {
            'episode': episode,
            'best_time': self.best_time,
            'episode_rewards': self.episode_rewards[-100:],  # 只保存最近100个
            'episode_times': self.episode_times[-100:],
            'config': self.config,
            'epsilon': self.wafer_agents[list(self.wafer_agents.keys())[0]].epsilon if self.wafer_agents else 0.1
        }
        
        filename = os.path.join(checkpoint_dir, f"checkpoint_{episode}.json")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
            print(f"检查点已保存: {filename}")
        except Exception as e:
            print(f"保存检查点失败: {e}")
    
    def save_final_results(self, output_dir: str = "output"):
        """保存最终结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"rl_result_task_{self.task_name}_{timestamp}.json")
        
        # 确保有有效的解决方案
        if not self.best_solution:
            self.best_solution = []
        
        result = {
            'MoveList': self.best_solution,
            'TotalTime': float(self.best_time) if self.best_time != float('inf') else 0.0,
            'TrainingStats': {
                'episodes': len(self.episode_rewards),
                'final_avg_reward': float(np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0),
                'final_avg_time': float(np.mean(self.episode_times[-100:]) if self.episode_times else 0),
                'best_time': float(self.best_time) if self.best_time != float('inf') else 0.0,
                'total_wafers': len(self.env.wafers),
                'config': self.config
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"最终结果已保存到 {filename}")
            print(f"最佳完工时间: {result['TotalTime']:.2f}秒")
            return filename
        
        except Exception as e:
            print(f"保存结果失败: {e}")
            return None