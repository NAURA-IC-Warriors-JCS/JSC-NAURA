"""
机械臂智能体类定义
包括TM1、TM2、TM3的所有机械臂
"""

import numpy as np
from typing import Optional, List, Dict, Tuple
from config.equipment_config import TM1_PARAMS, TM23_PARAMS, TM2_LAYOUT, TM3_LAYOUT

class RobotArm:
    """机械臂智能体基类"""
    
    def __init__(self, arm_id: str, arm_type: str):
        self.arm_id = arm_id
        self.arm_type = arm_type  # TM1, TM2, TM3
        
        # 状态信息
        self.current_position = 0  # 当前位置
        self.status = 'idle'  # idle, moving, picking, placing
        self.holding_wafer = None
        
        # 时间信息
        self.action_start_time = 0.0
        self.action_end_time = 0.0
        
        # 历史记录
        self.move_history = []
        
    def can_perform_action(self) -> bool:
        """检查是否可以执行动作"""
        return self.status == 'idle'
    
    def calculate_move_time(self, from_pos: int, to_pos: int) -> float:
        """计算移动时间"""
        if self.arm_type == 'TM1':
            return TM1_PARAMS['move_time']
        else:
            # TM2/TM3 八边形布局
            positions = 8
            distance = min(abs(to_pos - from_pos), positions - abs(to_pos - from_pos))
            return distance * TM23_PARAMS['move_time_adjacent']
    
    def start_move(self, target_position: int, current_time: float):
        """开始移动"""
        move_time = self.calculate_move_time(self.current_position, target_position)
        self.status = 'moving'
        self.action_start_time = current_time
        self.action_end_time = current_time + move_time
        
        # 记录移动历史
        self.move_history.append({
            'from_pos': self.current_position,
            'to_pos': target_position,
            'start_time': current_time,
            'end_time': self.action_end_time,
            'action_type': 'move'
        })
    
    def finish_move(self, target_position: int, current_time: float):
        """完成移动"""
        self.current_position = target_position
        self.status = 'idle'
    
    def start_pick(self, wafer, current_time: float):
        """开始取晶圆"""
        if self.arm_type == 'TM1':
            pick_time = TM1_PARAMS['pick_time']
        else:
            pick_time = TM23_PARAMS['pick_time_single']
        
        self.status = 'picking'
        self.action_start_time = current_time
        self.action_end_time = current_time + pick_time
        
        # 记录历史
        self.move_history.append({
            'wafer_id': wafer.wafer_id,
            'start_time': current_time,
            'end_time': self.action_end_time,
            'action_type': 'pick',
            'position': self.current_position
        })
    
    def finish_pick(self, wafer, current_time: float):
        """完成取晶圆"""
        self.holding_wafer = wafer
        self.status = 'idle'
        wafer.current_location = f"{self.arm_id}"
        wafer.status = 'moving'
    
    def start_place(self, current_time: float):
        """开始放晶圆"""
        if self.arm_type == 'TM1':
            place_time = TM1_PARAMS['place_time']
        else:
            place_time = TM23_PARAMS['place_time_single']
        
        self.status = 'placing'
        self.action_start_time = current_time
        self.action_end_time = current_time + place_time
        
        # 记录历史
        if self.holding_wafer:
            self.move_history.append({
                'wafer_id': self.holding_wafer.wafer_id,
                'start_time': current_time,
                'end_time': self.action_end_time,
                'action_type': 'place',
                'position': self.current_position
            })
    
    def finish_place(self, target_chamber, current_time: float):
        """完成放晶圆"""
        if self.holding_wafer:
            self.holding_wafer.current_location = target_chamber.chamber_name
            self.holding_wafer.status = 'waiting'
            self.holding_wafer = None
        self.status = 'idle'
    
    def is_action_complete(self, current_time: float) -> bool:
        """检查当前动作是否完成"""
        return current_time >= self.action_end_time
    
    def get_remaining_time(self, current_time: float) -> float:
        """获取剩余动作时间"""
        if self.status != 'idle':
            return max(0, self.action_end_time - current_time)
        return 0.0
    
    def get_state_vector(self, current_time: float) -> np.ndarray:
        """获取状态向量"""
        state = np.zeros(12)
        
        state[0] = self.current_position
        state[1] = 1 if self.holding_wafer else 0
        
        # 状态编码
        status_encoding = {
            'idle': 1, 'moving': 2, 'picking': 3, 'placing': 4
        }
        state[2] = status_encoding.get(self.status, 0)
        
        # 时间信息
        state[3] = self.get_remaining_time(current_time)
        
        # 持有晶圆信息
        if self.holding_wafer:
            state[4] = self.holding_wafer.lot_id
            state[5] = self.holding_wafer.wafer_num
            state[6] = self.holding_wafer.current_step
        
        return state
    
    def __str__(self):
        return f"RobotArm({self.arm_id}, pos={self.current_position}, {self.status})"


class TM1Arm(RobotArm):
    """TM1单臂机械手"""
    
    def __init__(self):
        super().__init__('TM1', 'TM1')
        self.accessible_chambers = ['LoadPort1', 'LoadPort2', 'LoadPort3', 'LLA']


class TM2Arm(RobotArm):
    """TM2双臂机械手"""
    
    def __init__(self, arm_index: int):
        super().__init__(f'TM2_R{arm_index}', 'TM2')
        self.arm_index = arm_index
        self.layout = TM2_LAYOUT
        self.accessible_chambers = list(TM2_LAYOUT.keys())
        
        # 双臂特殊功能
        self.can_hold_two_wafers = True
        self.second_wafer = None
    
    def get_chamber_position(self, chamber_name: str) -> Optional[int]:
        """获取腔室在八边形中的位置"""
        return self.layout.get(chamber_name)
    
    def get_chamber_at_position(self, position: int) -> Optional[str]:
        """获取指定位置的腔室名称"""
        for chamber, pos in self.layout.items():
            if pos == position:
                return chamber
        return None
    
    def start_double_pick(self, wafer1, wafer2, current_time: float):
        """开始双晶圆取操作"""
        pick_time = TM23_PARAMS['pick_time_double']
        self.status = 'picking'
        self.action_start_time = current_time
        self.action_end_time = current_time + pick_time
        
        # 记录历史
        self.move_history.append({
            'wafer_ids': [wafer1.wafer_id, wafer2.wafer_id],
            'start_time': current_time,
            'end_time': self.action_end_time,
            'action_type': 'double_pick',
            'position': self.current_position
        })
    
    def finish_double_pick(self, wafer1, wafer2, current_time: float):
        """完成双晶圆取操作"""
        self.holding_wafer = wafer1
        self.second_wafer = wafer2
        self.status = 'idle'
        
        wafer1.current_location = f"{self.arm_id}_1"
        wafer2.current_location = f"{self.arm_id}_2"
        wafer1.status = 'moving'
        wafer2.status = 'moving'
    
    def start_double_place(self, current_time: float):
        """开始双晶圆放操作"""
        place_time = TM23_PARAMS['place_time_double']
        self.status = 'placing'
        self.action_start_time = current_time
        self.action_end_time = current_time + place_time
        
        # 记录历史
        wafer_ids = []
        if self.holding_wafer:
            wafer_ids.append(self.holding_wafer.wafer_id)
        if self.second_wafer:
            wafer_ids.append(self.second_wafer.wafer_id)
        
        self.move_history.append({
            'wafer_ids': wafer_ids,
            'start_time': current_time,
            'end_time': self.action_end_time,
            'action_type': 'double_place',
            'position': self.current_position
        })
    
    def finish_double_place(self, target_chamber1, target_chamber2, current_time: float):
        """完成双晶圆放操作"""
        if self.holding_wafer:
            self.holding_wafer.current_location = target_chamber1.chamber_name
            self.holding_wafer.status = 'waiting'
            self.holding_wafer = None
        
        if self.second_wafer:
            self.second_wafer.current_location = target_chamber2.chamber_name
            self.second_wafer.status = 'waiting'
            self.second_wafer = None
        
        self.status = 'idle'


class TM3Arm(RobotArm):
    """TM3双臂机械手"""
    
    def __init__(self, arm_index: int):
        super().__init__(f'TM3_R{arm_index}', 'TM3')
        self.arm_index = arm_index
        self.layout = TM3_LAYOUT
        self.accessible_chambers = list(TM3_LAYOUT.keys())
        
        # 双臂特殊功能
        self.can_hold_two_wafers = True
        self.second_wafer = None
    
    def get_chamber_position(self, chamber_name: str) -> Optional[int]:
        """获取腔室在八边形中的位置"""
        return self.layout.get(chamber_name)
    
    def get_chamber_at_position(self, position: int) -> Optional[str]:
        """获取指定位置的腔室名称"""
        for chamber, pos in self.layout.items():
            if pos == position:
                return chamber
        return None
    
    # 双臂操作方法与TM2Arm相同
    def start_double_pick(self, wafer1, wafer2, current_time: float):
        """开始双晶圆取操作"""
        pick_time = TM23_PARAMS['pick_time_double']
        self.status = 'picking'
        self.action_start_time = current_time
        self.action_end_time = current_time + pick_time
    
    def finish_double_pick(self, wafer1, wafer2, current_time: float):
        """完成双晶圆取操作"""
        self.holding_wafer = wafer1
        self.second_wafer = wafer2
        self.status = 'idle'
        
        wafer1.current_location = f"{self.arm_id}_1"
        wafer2.current_location = f"{self.arm_id}_2"
        wafer1.status = 'moving'
        wafer2.status = 'moving'