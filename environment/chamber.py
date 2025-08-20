"""
腔室智能体类定义
包括PM、LoadLock等所有处理腔室
"""

import numpy as np
from typing import Optional, List, Dict
from config.equipment_config import CLEAN_PARAMS, LOADLOCK_PARAMS, DOOR_PARAMS

class Chamber:
    """腔室智能体基类"""
    
    def __init__(self, chamber_id: int, chamber_name: str):
        self.chamber_id = chamber_id
        self.chamber_name = chamber_name
        
        # 状态信息
        self.is_occupied = False
        self.current_wafer = None
        self.status = 'idle'  # idle, processing, cleaning, door_opening, door_closing
        
        # 时间信息
        self.last_activity_time = 0.0
        self.process_start_time = 0.0
        self.process_end_time = 0.0
        
        # 清洁信息
        self.wafer_count = 0
        self.last_process_type = None
        self.needs_cleaning = False
        
        # 门状态
        self.door_open = False
        
        # 历史记录
        self.processing_history = []
        
    def can_accept_wafer(self, wafer) -> bool:
        """检查是否可以接受晶圆"""
        return not self.is_occupied and self.status == 'idle'
    
    def start_processing(self, wafer, current_time: float, process_time: float):
        """开始处理晶圆"""
        self.is_occupied = True
        self.current_wafer = wafer
        self.status = 'processing'
        self.process_start_time = current_time
        self.process_end_time = current_time + process_time
        self.last_activity_time = current_time
        
        # 更新晶圆计数
        self.wafer_count += 1
        
        # 记录历史
        self.processing_history.append({
            'wafer_id': wafer.wafer_id,
            'start_time': current_time,
            'end_time': self.process_end_time,
            'process_type': wafer.process_type
        })
    
    def finish_processing(self, current_time: float):
        """完成处理"""
        if self.current_wafer:
            self.last_process_type = self.current_wafer.process_type
        
        self.is_occupied = False
        self.current_wafer = None
        self.status = 'idle'
        self.last_activity_time = current_time
        
        # 检查是否需要清洁
        self.check_cleaning_requirements(current_time)
    
    def check_cleaning_requirements(self, current_time: float):
        """检查清洁需求"""
        # 晶圆计数清洁
        if self.wafer_count >= CLEAN_PARAMS['wafer_count_threshold']:
            self.needs_cleaning = True
            return
        
        # 空闲时间清洁
        idle_time = current_time - self.last_activity_time
        if idle_time >= CLEAN_PARAMS['idle_threshold']:
            self.needs_cleaning = True
            return
    
    def start_cleaning(self, current_time: float, clean_type: str = 'idle'):
        """开始清洁"""
        self.status = 'cleaning'
        self.needs_cleaning = False
        
        if clean_type == 'idle':
            clean_time = CLEAN_PARAMS['idle_clean_time']
        elif clean_type == 'process_switch':
            clean_time = CLEAN_PARAMS['process_switch_clean_time']
        elif clean_type == 'wafer_count':
            clean_time = CLEAN_PARAMS['wafer_count_clean_time']
            self.wafer_count = 0  # 重置计数
        else:
            clean_time = CLEAN_PARAMS['idle_clean_time']
        
        self.process_start_time = current_time
        self.process_end_time = current_time + clean_time
    
    def finish_cleaning(self, current_time: float):
        """完成清洁"""
        self.status = 'idle'
        self.last_activity_time = current_time
    
    def open_door(self, current_time: float):
        """开门"""
        if not self.door_open:
            self.status = 'door_opening'
            self.process_start_time = current_time
            self.process_end_time = current_time + DOOR_PARAMS['open_time']
    
    def close_door(self, current_time: float):
        """关门"""
        if self.door_open:
            self.status = 'door_closing'
            self.process_start_time = current_time
            self.process_end_time = current_time + DOOR_PARAMS['close_time']
    
    def finish_door_operation(self, current_time: float):
        """完成门操作"""
        if self.status == 'door_opening':
            self.door_open = True
        elif self.status == 'door_closing':
            self.door_open = False
        
        self.status = 'idle'
        self.last_activity_time = current_time
    
    def is_process_complete(self, current_time: float) -> bool:
        """检查当前操作是否完成"""
        return current_time >= self.process_end_time
    
    def get_remaining_time(self, current_time: float) -> float:
        """获取剩余处理时间"""
        if self.status in ['processing', 'cleaning', 'door_opening', 'door_closing']:
            return max(0, self.process_end_time - current_time)
        return 0.0
    
    def get_state_vector(self, current_time: float) -> np.ndarray:
        """获取状态向量"""
        state = np.zeros(15)
        
        state[0] = self.chamber_id
        state[1] = 1 if self.is_occupied else 0
        state[2] = 1 if self.door_open else 0
        state[3] = 1 if self.needs_cleaning else 0
        state[4] = self.wafer_count
        
        # 状态编码
        status_encoding = {
            'idle': 1, 'processing': 2, 'cleaning': 3,
            'door_opening': 4, 'door_closing': 5
        }
        state[5] = status_encoding.get(self.status, 0)
        
        # 时间信息
        state[6] = current_time - self.last_activity_time  # 空闲时间
        state[7] = self.get_remaining_time(current_time)   # 剩余时间
        
        return state
    
    def __str__(self):
        return f"Chamber({self.chamber_name}, {self.status}, occupied={self.is_occupied})"


class LoadLock(Chamber):
    """LoadLock特殊腔室类"""
    
    def __init__(self, chamber_id: int, chamber_name: str):
        super().__init__(chamber_id, chamber_name)
        self.is_vacuum = chamber_name in ['LLC', 'LLD']  # 固定真空
        self.can_pump_vent = chamber_name in ['LLA', 'LLB']  # 可抽充气
        
        if self.can_pump_vent:
            self.pump_time = LOADLOCK_PARAMS[chamber_name]['pump_time']
            self.vent_time = LOADLOCK_PARAMS[chamber_name]['vent_time']
    
    def start_pump(self, current_time: float):
        """开始抽气"""
        if self.can_pump_vent and not self.is_vacuum:
            self.status = 'pumping'
            self.process_start_time = current_time
            self.process_end_time = current_time + self.pump_time
    
    def start_vent(self, current_time: float):
        """开始充气"""
        if self.can_pump_vent and self.is_vacuum:
            self.status = 'venting'
            self.process_start_time = current_time
            self.process_end_time = current_time + self.vent_time
    
    def finish_pump_vent(self, current_time: float):
        """完成抽充气"""
        if self.status == 'pumping':
            self.is_vacuum = True
        elif self.status == 'venting':
            self.is_vacuum = False
        
        self.status = 'idle'
        self.last_activity_time = current_time