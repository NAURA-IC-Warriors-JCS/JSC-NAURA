"""
多智能体强化学习训练器
协调所有智能体的训练过程
"""

import numpy as np
import json
import os
from typing import Dict, List, Any
from datetime import datetime

from agents.wafer_agent import WaferAgent
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
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'episodes': 1000,
            'max_steps_per_episode': 5000,
            'learning_rate': 0.1,
            'epsilon_start': 0.9,
            'epsilon_end': 0.01,
            'epsilon_decay': 0.995,
            'save_interval': 100,
            'log_interval': 10
        }
    
    def _create_wafer_agents(self) -> Dict[str, WaferAgent]:
        """创建晶圆智能体"""
        agents = {}
        for wafer in self.env.wafers:
            agent = WaferAgent(wafer)
            agent.epsilon = self.config['epsilon_start']
            agents[wafer.wafer_id] = agent
        return agents
    
    def _create_chamber_agents(self) -> Dict[str, ChamberAgent]:
        """创建腔室智能体"""
        agents = {}
        for chamber_name, chamber in self.env.chambers.items():
            agent = ChamberAgent(chamber)
            agent.epsilon = self.config['epsilon_start']
            agents[chamber_name] = agent
        return agents
    
    def _create_robot_agents(self) -> Dict[str, RobotAgent]:
        """创建机械臂智能体"""
        agents = {}
        for arm_name, arm in self.env.robot_arms.items():
            agent = RobotAgent(arm)
            agent.epsilon = self.config['epsilon_start']
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
        
        while step_count < self.config['max_steps_per_episode']:
            # 检查是否所有晶圆完成
            if all(wafer.is_completed() for wafer in self.env.wafers):
                break
            
            # 获取所有智能体的状态和动作
            states = {}
            actions = {}
            
            # 晶圆智能体决策
            for wafer_id, agent in self.wafer_agents.items():
                if not agent.wafer.is_completed():
                    state = agent.get_state(self.env)
                    valid_actions = agent.get_valid_actions(self.env)
                    action = agent.select_action(state, valid_actions)
                    
                    states[wafer_id] = state
                    actions[wafer_id] = action
            
            # 腔室智能体决策
            for chamber_name, agent in self.chamber_agents.items():
                state = agent.get_state(self.env)
                valid_actions = agent.get_valid_actions(self.env)
                action = agent.select_action(state, valid_actions)
                
                states[chamber_name] = state
                actions[chamber_name] = action
            
            # 机械臂智能体决策
            for arm_name, agent in self.robot_agents.items():
                state = agent.get_state(self.env)
                valid_actions = agent.get_valid_actions(self.env)
                action = agent.select_action(state, valid_actions)
                
                states[arm_name] = state
                actions[arm_name] = action
            
            # 执行动作并获取奖励
            rewards = self._execute_actions_and_get_rewards(actions)
            
            # 获取下一状态
            next_states = {}
            for wafer_id, agent in self.wafer_agents.items():
                if not agent.wafer.is_completed():
                    next_states[wafer_id] = agent.get_state(self.env)
            
            for chamber_name, agent in self.chamber_agents.items():
                next_states[chamber_name] = agent.get_state(self.env)
            
            for arm_name, agent in self.robot_agents.items():
                next_states[arm_name] = agent.get_state(self.env)
            
            # 更新智能体策略
            done = all(wafer.is_completed() for wafer in self.env.wafers)
            
            for wafer_id, agent in self.wafer_agents.items():
                if wafer_id in states and wafer_id in next_states:
                    agent.update_policy(
                        states[wafer_id], actions[wafer_id], rewards.get(wafer_id, 0),
                        next_states[wafer_id], done
                    )
            
            for chamber_name, agent in self.chamber_agents.items():
                if chamber_name in states and chamber_name in next_states:
                    agent.update_policy(
                        states[chamber_name], actions[chamber_name], rewards.get(chamber_name, 0),
                        next_states[chamber_name], done
                    )
            
            for arm_name, agent in self.robot_agents.items():
                if arm_name in states and arm_name in next_states:
                    agent.update_policy(
                        states[arm_name], actions[arm_name], rewards.get(arm_name, 0),
                        next_states[arm_name], done
                    )
            
            episode_reward += sum(rewards.values())
            step_count += 1
            
            # 推进环境
            self.env.step()
        
        # 更新探索率
        self._update_epsilon()
        
        return {
            'episode_reward': episode_reward,
            'completion_time': self.env.current_time,
            'completed_wafers': len([w for w in self.env.wafers if w.is_completed()]),
            'total_steps': step_count
        }
    
    def _execute_actions_and_get_rewards(self, actions: Dict) -> Dict[str, float]:
        """执行动作并计算奖励"""
        rewards = {}
        
        # 简化的动作执行和奖励计算
        for agent_id, action in actions.items():
            if agent_id in self.wafer_agents:
                # 晶圆智能体奖励
                agent = self.wafer_agents[agent_id]
                action_result = self._simulate_wafer_action(agent, action)
                rewards[agent_id] = agent.calculate_reward(self.env, action_result)
                
            elif agent_id in self.chamber_agents:
                # 腔室智能体奖励
                agent = self.chamber_agents[agent_id]
                action_result = self._simulate_chamber_action(agent, action)
                rewards[agent_id] = agent.calculate_reward(self.env, action_result)
                
            elif agent_id in self.robot_agents:
                # 机械臂智能体奖励
                agent = self.robot_agents[agent_id]
                action_result = self._simulate_robot_action(agent, action)
                rewards[agent_id] = agent.calculate_reward(self.env, action_result)
        
        return rewards
    
    def _simulate_wafer_action(self, agent: WaferAgent, action: int) -> Dict:
        """模拟晶圆动作"""
        result = {
            'follows_process_route': False,
            'step_completed': False,
            'chamber_available': False,
            'waiting_time': 0,
            'constraint_violation': False,
            'flexible_choice': False
        }
        
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
                    result['step_completed'] = True
        
        return result
    
    def _simulate_chamber_action(self, agent: ChamberAgent, action: int) -> Dict:
        """模拟腔室动作"""
        result = {
            'wafer_processed': False,
            'cleaning_completed': False,
            'utilization': 0.0,
            'idle_time': 0,
            'door_operation_efficient': False,
            'invalid_operation': False
        }
        
        if action == 3:  # 开始处理
            if agent.chamber.current_wafer:
                result['wafer_processed'] = True
                result['utilization'] = 0.8
        elif action == 4:  # 开始清洁
            if agent.chamber.needs_cleaning:
                result['cleaning_completed'] = True
        elif action == 0:  # 空闲
            result['idle_time'] = 1
        
        return result
    
    def _simulate_robot_action(self, agent: RobotAgent, action: int) -> Dict:
        """模拟机械臂动作"""
        return agent.execute_action(action, self.env, self.env.current_time)
    
    def _update_epsilon(self):
        """更新所有智能体的探索率"""
        for agent in list(self.wafer_agents.values()) + \
                     list(self.chamber_agents.values()) + \
                     list(self.robot_agents.values()):
            agent.update_epsilon()
    
    def train(self) -> Dict:
        """执行完整训练"""
        print(f"开始训练任务 {self.task_name.upper()}")
        print(f"智能体数量: 晶圆={len(self.wafer_agents)}, 腔室={len(self.chamber_agents)}, 机械臂={len(self.robot_agents)}")
        
        for episode in range(self.config['episodes']):
            episode_result = self.train_episode()
            
            self.episode_rewards.append(episode_result['episode_reward'])
            self.episode_times.append(episode_result['completion_time'])
            
            # 记录最佳结果
            if episode_result['completion_time'] < self.best_time:
                self.best_time = episode_result['completion_time']
                self.best_solution = self.env.move_list.copy()
            
            # 日志输出
            if episode % self.config['log_interval'] == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_time = np.mean(self.episode_times[-10:])
                print(f"Episode {episode}: 平均奖励={avg_reward:.2f}, 平均时间={avg_time:.2f}, 最佳时间={self.best_time:.2f}")
            
            # 保存检查点
            if episode % self.config['save_interval'] == 0:
                self.save_checkpoint(episode)
        
        return {
            'best_time': self.best_time,
            'best_solution': self.best_solution,
            'episode_rewards': self.episode_rewards,
            'episode_times': self.episode_times
        }
    
    def save_checkpoint(self, episode: int):
        """保存训练检查点"""
        checkpoint_dir = f"checkpoints/task_{self.task_name}"
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint = {
            'episode': episode,
            'best_time': self.best_time,
            'best_solution': self.best_solution,
            'episode_rewards': self.episode_rewards,
            'episode_times': self.episode_times,
            'config': self.config
        }
        
        filename = os.path.join(checkpoint_dir, f"checkpoint_{episode}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    def save_final_results(self, output_dir: str = "output"):
        """保存最终结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"rl_result_task_{self.task_name}_{timestamp}.json")
        
        result = {
            'MoveList': self.best_solution or [],
            'TotalTime': self.best_time,
            'TrainingStats': {
                'episodes': len(self.episode_rewards),
                'final_avg_reward': np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0,
                'final_avg_time': np.mean(self.episode_times[-100:]) if self.episode_times else 0,
                'best_time': self.best_time
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"最终结果已保存到 {filename}")
        return filename