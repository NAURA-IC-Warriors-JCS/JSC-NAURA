"""
智能体基类
定义所有智能体的通用接口
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple

class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state_dim = 0
        self.action_dim = 0
        
        # 学习参数
        self.learning_rate = 0.001
        self.epsilon = 0.1  # 探索率
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # 经验回放
        self.memory = []
        self.memory_size = 10000
        
        # 奖励记录
        self.episode_rewards = []
        self.total_reward = 0.0
    
    @abstractmethod
    def get_state(self, environment) -> np.ndarray:
        """获取当前状态"""
        pass
    
    @abstractmethod
    def get_action_space(self) -> List[int]:
        """获取动作空间"""
        pass
    
    @abstractmethod
    def select_action(self, state: np.ndarray, valid_actions: List[int] = None) -> int:
        """选择动作"""
        pass
    
    @abstractmethod
    def update_policy(self, state: np.ndarray, action: int, reward: float, 
                     next_state: np.ndarray, done: bool):
        """更新策略"""
        pass
    
    def add_experience(self, state: np.ndarray, action: int, reward: float,
                      next_state: np.ndarray, done: bool):
        """添加经验到回放缓冲区"""
        experience = (state, action, reward, next_state, done)
        
        if len(self.memory) >= self.memory_size:
            self.memory.pop(0)
        
        self.memory.append(experience)
    
    def update_epsilon(self):
        """更新探索率"""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def reset_episode(self):
        """重置回合"""
        self.episode_rewards.append(self.total_reward)
        self.total_reward = 0.0
    
    def get_average_reward(self, last_n: int = 100) -> float:
        """获取最近N个回合的平均奖励"""
        if not self.episode_rewards:
            return 0.0
        
        recent_rewards = self.episode_rewards[-last_n:]
        return np.mean(recent_rewards)