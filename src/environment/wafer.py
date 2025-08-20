"""
晶圆类定义
每个晶圆作为一个智能体
"""

import numpy as np
from typing import List, Dict, Optional
from config.process_config import PROCESS_ROUTES, get_process_time, get_flexible_options

class Wafer:
    """晶圆智能体类"""
    
    def __init__(self, wafer_id: str, process_type: str, lot_id: int, wafer_num: int):
        self.wafer_id = wafer_id
        self.process_type = process_type
        self.lot_id = lot_id
        self.wafer_num = wafer_num
        
        # 工艺路径
        self.process_route = PROCESS_ROUTES.get(process_type, [])
        self.current_step = 0
        self.completed_steps = []
        
        # 状态信息
        self.current_location = None  # 当前位置
        self.status = 'waiting'  # waiting, processing, moving, completed
        self.start_time = 0.0
        self.completion_time = None
        
        # 历史记录
        self.move_history = []
        self.processing_history = []
        
    def get_current_target_chamber(self) -> Optional[int]:
        """获取当前目标腔室"""
        if self.current_step < len(self.process_route):
            return self.process_route[self.current_step]
        return None
    
    def get_next_target_chamber(self) -> Optional[int]:
        """获取下一个目标腔室"""
        if self.current_step + 1 < len(self.process_route):
            return self.process_route[self.current_step + 1]
        return None
    
    def get_flexible_chamber_options(self) -> List[int]:
        """获取当前步骤的柔性腔室选项"""
        current_chamber = self.get_current_target_chamber()
        if current_chamber is not None:
            return get_flexible_options(self.process_type, current_chamber)
        return []
    
    def get_processing_time(self, chamber_id: int) -> float:
        """获取在指定腔室的处理时间"""
        return get_process_time(self.process_type, chamber_id)
    
    def advance_step(self):
        """推进到下一个工艺步骤"""
        if self.current_step < len(self.process_route):
            self.completed_steps.append(self.process_route[self.current_step])
            self.current_step += 1
    
    def is_completed(self) -> bool:
        """检查是否完成所有工艺步骤"""
        return self.current_step >= len(self.process_route)
    
    def can_enter_chamber(self, chamber_id: int) -> bool:
        """检查是否可以进入指定腔室"""
        flexible_options = self.get_flexible_chamber_options()
        return chamber_id in flexible_options
    
    def get_state_vector(self) -> np.ndarray:
        """获取状态向量用于强化学习"""
        state = np.zeros(20)  # 状态向量维度
        
        # 基本信息
        state[0] = self.lot_id
        state[1] = self.wafer_num
        state[2] = self.current_step
        state[3] = len(self.process_route)
        
        # 当前目标腔室
        current_target = self.get_current_target_chamber()
        if current_target is not None:
            state[4] = current_target
        
        # 下一个目标腔室
        next_target = self.get_next_target_chamber()
        if next_target is not None:
            state[5] = next_target
        
        # 状态编码
        status_encoding = {
            'waiting': 1, 'processing': 2, 'moving': 3, 'completed': 4
        }
        state[6] = status_encoding.get(self.status, 0)
        
        # 当前位置
        if self.current_location is not None:
            state[7] = self.current_location
        
        # 完成进度
        state[8] = self.current_step / len(self.process_route) if self.process_route else 1.0
        
        # 柔性选项数量
        state[9] = len(self.get_flexible_chamber_options())
        
        return state
    
    def get_reward(self, action_result: Dict) -> float:
        """计算奖励函数"""
        reward = 0.0
        
        # 基础奖励：按工艺路径行走
        if action_result.get('follows_process_route', False):
            reward += 10.0
        
        # 完成步骤奖励
        if action_result.get('step_completed', False):
            reward += 5.0
        
        # 完成全部工艺奖励
        if self.is_completed():
            reward += 50.0
        
        # 时间惩罚
        if action_result.get('waiting_time', 0) > 0:
            reward -= action_result['waiting_time'] * 0.1
        
        # 违反约束惩罚
        if action_result.get('constraint_violation', False):
            reward -= 20.0
        
        return reward
    
    def __str__(self):
        return f"Wafer({self.wafer_id}, {self.process_type}, step={self.current_step}/{len(self.process_route)})"
    
    def __repr__(self):
        return self.__str__()