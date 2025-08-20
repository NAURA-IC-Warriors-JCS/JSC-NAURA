"""
半导体制造环境主类
整合所有智能体和环境逻辑
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

from .wafer import Wafer
from .chamber import Chamber, LoadLock
from .robot_arm import TM1Arm, TM2Arm, TM3Arm
from config.equipment_config import EQUIPMENT_MAPPING, EQUIPMENT_ID_TO_NAME, MOVE_TYPES
from config.task_config import get_task_wafers
from config.process_config import get_process_time

class FabEnvironment:
    """半导体制造环境"""
    
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.current_time = 0.0
        self.move_counter = 0
        
        # 初始化所有智能体
        self.wafers = self._initialize_wafers()
        self.chambers = self._initialize_chambers()
        self.robot_arms = self._initialize_robot_arms()
        
        # 输出记录
        self.move_list = []
        
        # 约束检查
        self.constraint_violations = []
        
    def _initialize_wafers(self) -> List[Wafer]:
        """初始化晶圆智能体"""
        wafer_configs = get_task_wafers(self.task_name)
        wafers = []
        
        for config in wafer_configs:
            wafer = Wafer(
                wafer_id=config['wafer_id'],
                process_type=config['process_type'],
                lot_id=config['lot_id'],
                wafer_num=config['wafer_num']
            )
            wafers.append(wafer)
        
        return wafers
    
    def _initialize_chambers(self) -> Dict[str, Chamber]:
        """初始化腔室智能体"""
        chambers = {}
        
        # 初始化PM腔室
        for i in range(1, 11):
            chamber_name = f"PM{i}"
            chambers[chamber_name] = Chamber(i, chamber_name)
        
        # 初始化LoadLock
        for ll_name in ['LLA', 'LLB', 'LLC', 'LLD']:
            chamber_id = EQUIPMENT_MAPPING[ll_name]
            chambers[ll_name] = LoadLock(chamber_id, ll_name)
        
        return chambers
    
    def _initialize_robot_arms(self) -> Dict[str, object]:
        """初始化机械臂智能体"""
        arms = {}
        
        # TM1单臂
        arms['TM1'] = TM1Arm()
        
        # TM2双臂
        arms['TM2_R1'] = TM2Arm(1)
        arms['TM2_R2'] = TM2Arm(2)
        
        # TM3双臂
        arms['TM3_R1'] = TM3Arm(1)
        arms['TM3_R2'] = TM3Arm(2)
        
        return arms
    
    def get_available_chambers_for_wafer(self, wafer: Wafer) -> List[Chamber]:
        """获取晶圆可用的腔室列表"""
        available = []
        flexible_options = wafer.get_flexible_chamber_options()
        
        for chamber_id in flexible_options:
            chamber_name = EQUIPMENT_ID_TO_NAME.get(chamber_id)
            if chamber_name and chamber_name in self.chambers:
                chamber = self.chambers[chamber_name]
                if chamber.can_accept_wafer(wafer):
                    available.append(chamber)
        
        return available
    
    def check_overtaking_constraint(self, wafer: Wafer, target_chamber: Chamber) -> bool:
        """检查超片约束：同一PM、同工艺步，不允许大编号晶圆先于小编号进入"""
        if not target_chamber.chamber_name.startswith('PM'):
            return True  # 非PM腔室不检查
        
        current_target = wafer.get_current_target_chamber()
        
        # 检查同批次中编号更小的晶圆
        for other_wafer in self.wafers:
            if (other_wafer.lot_id == wafer.lot_id and 
                other_wafer.wafer_num < wafer.wafer_num and
                other_wafer.process_type == wafer.process_type and
                other_wafer.get_current_target_chamber() == current_target and
                other_wafer.current_step == wafer.current_step and
                other_wafer.status != 'completed'):
                
                # 如果小编号晶圆还未进入相同步骤的腔室，则大编号不能进入
                if other_wafer.current_location != target_chamber.chamber_name:
                    return False
        
        return True
    
    def execute_wafer_move(self, wafer: Wafer, target_chamber: Chamber, 
                          robot_arm: object) -> List[Dict]:
        """执行晶圆移动操作"""
        moves = []
        
        # 检查约束
        if not self.check_overtaking_constraint(wafer, target_chamber):
            self.constraint_violations.append({
                'type': 'overtaking',
                'wafer_id': wafer.wafer_id,
                'chamber': target_chamber.chamber_name,
                'time': self.current_time
            })
            return moves
        
        # 1. 机械臂移动到晶圆位置
        if wafer.current_location and wafer.current_location != robot_arm.arm_id:
            # 计算移动时间和位置
            move_time = 1.0  # 简化计算
            moves.append({
                'StartTime': self.current_time,
                'EndTime': self.current_time + move_time,
                'MoveID': self.move_counter,
                'MoveType': MOVE_TYPES['TRANS'],
                'ModuleName': robot_arm.arm_id,
                'MatID': wafer.wafer_id,
                'SlotID': 1
            })
            self.move_counter += 1
            self.current_time += move_time
        
        # 2. 开门
        if hasattr(target_chamber, 'door_open') and not target_chamber.door_open:
            target_chamber.open_door(self.current_time)
            door_time = 1.0
            moves.append({
                'StartTime': self.current_time,
                'EndTime': self.current_time + door_time,
                'MoveID': self.move_counter,
                'MoveType': MOVE_TYPES['PREPARE'],
                'ModuleName': target_chamber.chamber_name,
                'MatID': wafer.wafer_id,
                'SlotID': 1
            })
            self.move_counter += 1
            self.current_time += door_time
        
        # 3. 取晶圆
        robot_arm.start_pick(wafer, self.current_time)
        pick_time = robot_arm.action_end_time - robot_arm.action_start_time
        moves.append({
            'StartTime': self.current_time,
            'EndTime': self.current_time + pick_time,
            'MoveID': self.move_counter,
            'MoveType': MOVE_TYPES['PICK'],
            'ModuleName': robot_arm.arm_id,
            'MatID': wafer.wafer_id,
            'SlotID': 1
        })
        self.move_counter += 1
        self.current_time += pick_time
        robot_arm.finish_pick(wafer, self.current_time)
        
        # 4. 移动到目标腔室
        move_time = 1.0  # 简化计算
        moves.append({
            'StartTime': self.current_time,
            'EndTime': self.current_time + move_time,
            'MoveID': self.move_counter,
            'MoveType': MOVE_TYPES['TRANS'],
            'ModuleName': robot_arm.arm_id,
            'MatID': wafer.wafer_id,
            'SlotID': 1
        })
        self.move_counter += 1
        self.current_time += move_time
        
        # 5. 放晶圆
        robot_arm.start_place(self.current_time)
        place_time = robot_arm.action_end_time - robot_arm.action_start_time
        moves.append({
            'StartTime': self.current_time,
            'EndTime': self.current_time + place_time,
            'MoveID': self.move_counter,
            'MoveType': MOVE_TYPES['PLACE'],
            'ModuleName': robot_arm.arm_id,
            'MatID': wafer.wafer_id,
            'SlotID': 1
        })
        self.move_counter += 1
        self.current_time += place_time
        robot_arm.finish_place(target_chamber, self.current_time)
        
        # 6. 关门
        if hasattr(target_chamber, 'door_open') and target_chamber.door_open:
            target_chamber.close_door(self.current_time)
            door_time = 1.0
            moves.append({
                'StartTime': self.current_time,
                'EndTime': self.current_time + door_time,
                'MoveID': self.move_counter,
                'MoveType': MOVE_TYPES['COMPLETE'],
                'ModuleName': target_chamber.chamber_name,
                'MatID': wafer.wafer_id,
                'SlotID': 1
            })
            self.move_counter += 1
            self.current_time += door_time
        
        # 7. 开始处理
        process_time = get_process_time(wafer.process_type, target_chamber.chamber_id)
        if process_time > 0:
            target_chamber.start_processing(wafer, self.current_time, process_time)
            moves.append({
                'StartTime': self.current_time,
                'EndTime': self.current_time + process_time,
                'MoveID': self.move_counter,
                'MoveType': MOVE_TYPES['PROCESS'],
                'ModuleName': target_chamber.chamber_name,
                'MatID': wafer.wafer_id,
                'SlotID': 1
            })
            self.move_counter += 1
            self.current_time += process_time
            
            # 完成处理
            target_chamber.finish_processing(self.current_time)
            wafer.advance_step()
        
        return moves
    
    def step(self) -> bool:
        """环境步进，返回是否所有晶圆完成"""
        # 简化的调度逻辑：按顺序处理晶圆
        for wafer in self.wafers:
            if not wafer.is_completed():
                available_chambers = self.get_available_chambers_for_wafer(wafer)
                if available_chambers:
                    # 选择第一个可用腔室
                    target_chamber = available_chambers[0]
                    # 选择第一个可用机械臂
                    available_arm = None
                    for arm in self.robot_arms.values():
                        if arm.can_perform_action():
                            available_arm = arm
                            break
                    
                    if available_arm:
                        moves = self.execute_wafer_move(wafer, target_chamber, available_arm)
                        self.move_list.extend(moves)
                        break
        
        # 检查是否所有晶圆完成
        return all(wafer.is_completed() for wafer in self.wafers)
    
    def run_simulation(self) -> Dict:
        """运行完整仿真"""
        max_steps = 10000  # 防止无限循环
        step_count = 0
        
        while step_count < max_steps:
            all_completed = self.step()
            step_count += 1
            
            if all_completed:
                break
        
        # 设置完成时间
        for wafer in self.wafers:
            if wafer.is_completed():
                wafer.completion_time = self.current_time
        
        return {
            'MoveList': self.move_list,
            'TotalTime': self.current_time,
            'CompletedWafers': len([w for w in self.wafers if w.is_completed()]),
            'TotalWafers': len(self.wafers),
            'ConstraintViolations': self.constraint_violations
        }
    
    def save_results(self, filename: str):
        """保存结果到JSON文件"""
        result = self.run_simulation()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"结果已保存到 {filename}")
        print(f"总完工时间: {result['TotalTime']:.2f}秒")
        print(f"完成晶圆数: {result['CompletedWafers']}/{result['TotalWafers']}")