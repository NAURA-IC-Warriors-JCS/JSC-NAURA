"""
修复后的晶圆智能体
解决数据类型转换问题
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
    
    def _clean_state(self, state: np.ndarray) -> np.ndarray:
        """清理状态数据，确保数值类型"""
        # 处理NaN和无穷值
        state_clean = np.nan_to_num(state, nan=0.0, posinf=999.0, neginf=-999.0)
        # 确保是浮点数类型
        return state_clean.astype(np.float32)
    
    def _state_to_key(self, state: np.ndarray) -> tuple:
        """将状态转换为可哈希的键"""
        state_clean = self._clean_state(state)
        # 量化状态以减少状态空间
        state_quantized = np.round(state_clean * 10).astype(int)  # 保留一位小数
        return tuple(state_quantized)
    
    def get_state(self, environment) -> np.ndarray:
        """获取晶圆状态"""
        state = np.zeros(self.state_dim, dtype=np.float32)
        
        # 基本信息
        state[0] = float(self.wafer.lot_id)
        state[1] = float(self.wafer.wafer_num)
        state[2] = float(self.wafer.current_step)
        state[3] = float(len(self.wafer.process_route))
        
        # 当前目标腔室
        current_target = self.wafer.get_current_target_chamber()
        if current_target is not None:
            state[4] = float(current_target)
        
        # 下一个目标腔室
        next_target = self.wafer.get_next_target_chamber()
        if next_target is not None:
            state[5] = float(next_target)
        
        # 状态编码
        status_encoding = {
            'waiting': 1.0, 'processing': 2.0, 'moving': 3.0, 'completed': 4.0
        }
        state[6] = status_encoding.get(self.wafer.status, 0.0)
        
        # 当前位置编码
        if self.wafer.current_location is not None:
            # 将位置名称转换为数字编码
            location_encoding = self._encode_location(self.wafer.current_location)
            state[7] = float(location_encoding)
        
        # 完成进度
        if self.wafer.process_route:
            state[8] = float(self.wafer.current_step) / float(len(self.wafer.process_route))
        else:
            state[8] = 1.0
        
        # 柔性选项数量
        state[9] = float(len(self.wafer.get_flexible_chamber_options()))
        
        # 环境信息
        available_chambers = environment.get_available_chambers_for_wafer(self.wafer)
        state[10] = float(len(available_chambers))
        
        # 当前时间（归一化）
        state[11] = float(environment.current_time % 1000) / 1000.0
        
        # 等待的晶圆数量
        waiting_wafers = sum(1 for w in environment.wafers 
                           if w.status == 'waiting' and not w.is_completed())
        state[12] = float(waiting_wafers)
        
        return self._clean_state(state)
    
    def _encode_location(self, location: str) -> int:
        """将位置名称编码为数字"""
        location_map = {
            'LoadPort1': 1, 'LoadPort2': 2, 'LoadPort3': 3,
            'LLA': 11, 'LLB': 12, 'LLC': 13, 'LLD': 14,
            'PM1': 21, 'PM2': 22, 'PM3': 23, 'PM4': 24, 'PM5': 25,
            'PM6': 26, 'PM7': 27, 'PM8': 28, 'PM9': 29, 'PM10': 30,
            'TM1': 31, 'TM2_R1': 32, 'TM2_R2': 33, 'TM3_R1': 34, 'TM3_R2': 35
        }
        return location_map.get(location, 0)
    
    def get_action_space(self) -> List[int]:
        """获取动作空间"""
        return list(range(self.action_dim))
    
    def get_valid_actions(self, environment) -> List[int]:
        """获取有效动作"""
        valid_actions = [0]  # 总是可以等待
        
        if self.wafer.is_completed():
            return [0]  # 已完成的晶圆只能等待
        
        # 获取柔性腔室选项
        flexible_options = self.wafer.get_flexible_chamber_options()
        available_chambers = environment.get_available_chambers_for_wafer(self.wafer)
        
        # 检查每个柔性选项是否可用
        for i, chamber_id in enumerate(flexible_options[:4]):  # 最多4个选项
            # 根据chamber_id找到对应的腔室名称
            chamber_name = None
            if chamber_id <= 10:
                chamber_name = f"PM{chamber_id}"
            else:
                chamber_map = {11: 'LLA', 12: 'LLB', 13: 'LLC', 14: 'LLD'}
                chamber_name = chamber_map.get(chamber_id)
            
            if chamber_name and any(c.chamber_name == chamber_name for c in available_chambers):
                valid_actions.append(i + 1)
        
        return valid_actions
    
    def select_action(self, state: np.ndarray, valid_actions: List[int] = None) -> int:
        """选择动作 (epsilon-greedy)"""
        if valid_actions is None:
            valid_actions = self.get_action_space()
        
        if not valid_actions:
            return 0  # 默认等待
        
        state_key = self._state_to_key(state)
        
        # 初始化Q值
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim, dtype=np.float32)
        
        # epsilon-greedy策略
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        else:
            # 选择Q值最高的有效动作
            q_values = self.q_table[state_key]
            valid_q_values = [(action, q_values[action]) for action in valid_actions]
            if valid_q_values:
                return max(valid_q_values, key=lambda x: x[1])[0]
            else:
                return valid_actions[0]
    
    def update_policy(self, state: np.ndarray, action: int, reward: float,
                     next_state: np.ndarray, done: bool):
        """更新Q表"""
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # 初始化Q值
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim, dtype=np.float32)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_dim, dtype=np.float32)
        
        # 确保action在有效范围内
        if action >= self.action_dim:
            action = 0
        
        # Q-learning更新
        current_q = float(self.q_table[state_key][action])
        next_max_q = float(np.max(self.q_table[next_state_key])) if not done else 0.0
        
        new_q = current_q + self.learning_rate * (
            float(reward) + self.discount_factor * next_max_q - current_q
        )
        
        self.q_table[state_key][action] = new_q
        self.total_reward += float(reward)
    
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
            reward -= float(waiting_time) * 0.1
        
        # 违反约束的严重惩罚
        if action_result.get('constraint_violation', False):
            reward -= 50.0
        
        # 柔性腔室选择奖励
        if action_result.get('flexible_choice', False):
            reward += 3.0
        
        return float(reward)
    
    def get_action_description(self, action: int) -> str:
        """获取动作描述"""
        if action == 0:
            return "等待"
        else:
            return f"选择柔性腔室选项{action}"