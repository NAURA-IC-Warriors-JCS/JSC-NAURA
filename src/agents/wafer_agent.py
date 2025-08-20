"""
晶圆智能体
负责决策晶圆的工艺路径选择和等待策略
"""

import numpy as np
import random
from typing import List, Dict, Any
from .base_agent import BaseAgent

class WaferAgent(BaseAgent):
    """晶圆智能体"""
    
    def __init__(self, wafer):
        super().__init__(f"wafer_{wafer.wafer_id}", "wafer")
        self.wafer = wafer
        self.state_dim = 20
        self.action_dim = 5  # 等待、选择柔性腔室1-4
        
        # Q表 (简化的Q-learning)
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
    
    def get_state(self, environment) -> np.ndarray:
        """获取晶圆状态"""
        state = self.wafer.get_state_vector()
        
        # 添加环境信息
        env_state = np.zeros(10)
        
        # 可用腔室数量
        available_chambers = environment.get_available_chambers_for_wafer(self.wafer)
        env_state[0] = len(available_chambers)
        
        # 当前时间
        env_state[1] = environment.current_time
        
        # 等待的晶圆数量
        waiting_wafers = sum(1 for w in environment.wafers 
                           if w.status == 'waiting' and not w.is_completed())
        env_state[2] = waiting_wafers
        
        # 合并状态
        full_state = np.concatenate([state, env_state])
        return full_state[:self.state_dim]  # 截断到固定维度
    
    def get_action_space(self) -> List[int]:
        """获取动作空间"""
        return list(range(self.action_dim))
    
    def get_valid_actions(self, environment) -> List[int]:
        """获取有效动作"""
        valid_actions = [0]  # 总是可以等待
        
        # 获取柔性腔室选项
        flexible_options = self.wafer.get_flexible_chamber_options()
        available_chambers = environment.get_available_chambers_for_wafer(self.wafer)
        
        # 检查每个柔性选项是否可用
        for i, chamber_id in enumerate(flexible_options[:4]):  # 最多4个选项
            chamber_name = environment.chambers.get(f"PM{chamber_id}" if chamber_id <= 10 else 
                                                   {11: 'LLA', 12: 'LLB', 13: 'LLC', 14: 'LLD'}[chamber_id])
            if chamber_name and any(c.chamber_name == chamber_name for c in available_chambers):
                valid_actions.append(i + 1)
        
        return valid_actions
    
    def select_action(self, state: np.ndarray, valid_actions: List[int] = None) -> int:
        """选择动作 (epsilon-greedy)"""
        if valid_actions is None:
            valid_actions = self.get_action_space()
        
        # 确保状态是数值类型并处理NaN值
        state_clean = np.nan_to_num(state, nan=0.0, posinf=999.0, neginf=-999.0)
        state_key = tuple(np.round(state_clean, 2).astype(float))
        
        # 初始化Q值
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim)
        
        # epsilon-greedy策略
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        else:
            # 选择Q值最高的有效动作
            q_values = self.q_table[state_key]
            valid_q_values = [(action, q_values[action]) for action in valid_actions]
            return max(valid_q_values, key=lambda x: x[1])[0]
    
    def update_policy(self, state: np.ndarray, action: int, reward: float,
                     next_state: np.ndarray, done: bool):
        """更新Q表"""
        state_key = tuple(state.astype(int))
        next_state_key = tuple(next_state.astype(int))
        
        # 初始化Q值
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_dim)
        
        # Q-learning更新
        current_q = self.q_table[state_key][action]
        next_max_q = np.max(self.q_table[next_state_key]) if not done else 0
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * next_max_q - current_q
        )
        
        self.q_table[state_key][action] = new_q
        self.total_reward += reward
    
    def calculate_reward(self, environment, action_result: Dict) -> float:
        """计算奖励"""
        reward = 0.0
        
        # 基础奖励：遵循工艺路径
        if action_result.get('follows_process_route', False):
            reward += 20.0
        
        # 完成步骤奖励
        if action_result.get('step_completed', False):
            reward += 10.0
            
        # 完成全部工艺的大奖励
        if self.wafer.is_completed():
            reward += 100.0
        
        # 选择可用腔室的奖励
        if action_result.get('chamber_available', False):
            reward += 5.0
        
        # 等待时间惩罚
        waiting_time = action_result.get('waiting_time', 0)
        if waiting_time > 0:
            reward -= waiting_time * 0.1
        
        # 违反约束的严重惩罚
        if action_result.get('constraint_violation', False):
            reward -= 50.0
        
        # 柔性腔室选择奖励
        if action_result.get('flexible_choice', False):
            reward += 3.0
        
        return reward
    
    def get_action_description(self, action: int) -> str:
        """获取动作描述"""
        if action == 0:
            return "等待"
        else:
            return f"选择柔性腔室选项{action}"