"""
腔室智能体
负责决策腔室的开关门、清洁等操作
"""

import numpy as np
import random
from typing import List, Dict, Any
from .base_agent import BaseAgent

class ChamberAgent(BaseAgent):
    """腔室智能体"""
    
    def __init__(self, chamber):
        super().__init__(f"chamber_{chamber.chamber_name}", "chamber")
        self.chamber = chamber
        self.state_dim = 15
        self.action_dim = 6  # 空闲、开门、关门、开始处理、开始清洁、等待
        
        # Q表
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
    
    def get_state(self, environment) -> np.ndarray:
        """获取腔室状态"""
        state = self.chamber.get_state_vector(environment.current_time)
        
        # 添加环境信息
        env_info = np.zeros(5)
        
        # 等待进入的晶圆数量
        waiting_for_chamber = 0
        for wafer in environment.wafers:
            if (not wafer.is_completed() and 
                wafer.can_enter_chamber(self.chamber.chamber_id)):
                waiting_for_chamber += 1
        env_info[0] = waiting_for_chamber
        
        # 当前时间
        env_info[1] = environment.current_time % 1000  # 归一化
        
        # 合并状态
        full_state = np.concatenate([state, env_info])
        return full_state[:self.state_dim]
    
    def get_action_space(self) -> List[int]:
        """获取动作空间"""
        return list(range(self.action_dim))
    
    def get_valid_actions(self, environment) -> List[int]:
        """获取有效动作"""
        valid_actions = []
        
        if self.chamber.status == 'idle':
            valid_actions.append(0)  # 保持空闲
            
            # 如果有晶圆等待且门关闭，可以开门
            if (not self.chamber.door_open and 
                any(w.current_location == self.chamber.chamber_name 
                    for w in environment.wafers)):
                valid_actions.append(1)  # 开门
            
            # 如果需要清洁
            if self.chamber.needs_cleaning:
                valid_actions.append(4)  # 开始清洁
        
        elif self.chamber.status == 'door_opening':
            valid_actions.append(5)  # 等待门开完成
        
        elif self.chamber.status == 'door_closing':
            valid_actions.append(5)  # 等待门关完成
        
        elif self.chamber.door_open and self.chamber.current_wafer:
            valid_actions.append(2)  # 关门
            valid_actions.append(3)  # 开始处理
        
        elif self.chamber.status in ['processing', 'cleaning']:
            valid_actions.append(5)  # 等待完成
        
        if not valid_actions:
            valid_actions.append(0)  # 默认空闲
        
        return valid_actions
    
    def select_action(self, state: np.ndarray, valid_actions: List[int] = None) -> int:
        """选择动作"""
        if valid_actions is None:
            valid_actions = self.get_action_space()
        
        state_key = tuple(state.astype(int))
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim)
        
        # epsilon-greedy
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        else:
            q_values = self.q_table[state_key]
            valid_q_values = [(action, q_values[action]) for action in valid_actions]
            return max(valid_q_values, key=lambda x: x[1])[0]
    
    def update_policy(self, state: np.ndarray, action: int, reward: float,
                     next_state: np.ndarray, done: bool):
        """更新Q表"""
        state_key = tuple(state.astype(int))
        next_state_key = tuple(next_state.astype(int))
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_dim)
        
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
        
        # 成功处理晶圆的奖励
        if action_result.get('wafer_processed', False):
            reward += 15.0
        
        # 及时清洁的奖励
        if action_result.get('cleaning_completed', False):
            reward += 8.0
        
        # 高效利用率奖励
        utilization = action_result.get('utilization', 0)
        reward += utilization * 5.0
        
        # 空闲时间惩罚
        idle_time = action_result.get('idle_time', 0)
        if idle_time > 10:  # 空闲超过10秒
            reward -= idle_time * 0.05
        
        # 门操作效率
        if action_result.get('door_operation_efficient', False):
            reward += 2.0
        
        # 违反操作规则的惩罚
        if action_result.get('invalid_operation', False):
            reward -= 10.0
        
        return reward
    
    def get_action_description(self, action: int) -> str:
        """获取动作描述"""
        actions = {
            0: "保持空闲",
            1: "开门",
            2: "关门", 
            3: "开始处理",
            4: "开始清洁",
            5: "等待操作完成"
        }
        return actions.get(action, "未知动作")