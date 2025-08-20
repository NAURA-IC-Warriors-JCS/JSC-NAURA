"""
约束验证工具
验证调度结果是否满足所有约束条件
"""

from typing import List, Dict, Set
import json

class ConstraintValidator:
    """约束验证器"""
    
    def __init__(self):
        self.violations = []
    
    def validate_schedule(self, move_list: List[Dict]) -> Dict:
        """验证完整调度方案"""
        self.violations = []
        
        # 验证各类约束
        self._validate_resource_conflicts(move_list)
        self._validate_wafer_flow(move_list)
        self._validate_overtaking_constraint(move_list)
        self._validate_door_operations(move_list)
        self._validate_loadlock_operations(move_list)
        self._validate_time_consistency(move_list)
        
        return {
            'valid': len(self.violations) == 0,
            'violations': self.violations,
            'violation_count': len(self.violations)
        }
    
    def _validate_resource_conflicts(self, move_list: List[Dict]):
        """验证资源冲突"""
        # 检查同一时间同一设备的冲突
        time_slots = {}
        
        for move in move_list:
            module = move['ModuleName']
            start_time = move['StartTime']
            end_time = move['EndTime']
            
            # 检查时间重叠
            for t in range(int(start_time), int(end_time) + 1):
                key = (module, t)
                if key in time_slots:
                    self.violations.append({
                        'type': 'resource_conflict',
                        'module': module,
                        'time': t,
                        'moves': [time_slots[key], move['MoveID']],
                        'description': f"设备 {module} 在时间 {t} 存在资源冲突"
                    })
                else:
                    time_slots[key] = move['MoveID']
    
    def _validate_wafer_flow(self, move_list: List[Dict]):
        """验证晶圆流程"""
        wafer_states = {}  # wafer_id -> current_location
        
        for move in move_list:
            wafer_id = move['MatID']
            move_type = move['MoveType']
            module = move['ModuleName']
            
            if wafer_id not in wafer_states:
                wafer_states[wafer_id] = None
            
            # 验证取放逻辑
            if move_type == 1:  # 取晶圆
                if wafer_states[wafer_id] is None:
                    # 第一次取晶圆，应该从LoadPort开始
                    if not module.startswith('TM'):
                        self.violations.append({
                            'type': 'invalid_pick',
                            'wafer_id': wafer_id,
                            'module': module,
                            'description': f"晶圆 {wafer_id} 首次取操作应由机械臂执行"
                        })
                
            elif move_type == 2:  # 放晶圆
                if wafer_states[wafer_id] is None:
                    self.violations.append({
                        'type': 'invalid_place',
                        'wafer_id': wafer_id,
                        'module': module,
                        'description': f"晶圆 {wafer_id} 在未被取起时就被放置"
                    })
                
                wafer_states[wafer_id] = module
    
    def _validate_overtaking_constraint(self, move_list: List[Dict]):
        """验证超片约束"""
        # 按晶圆分组
        wafer_moves = {}
        for move in move_list:
            wafer_id = move['MatID']
            if wafer_id not in wafer_moves:
                wafer_moves[wafer_id] = []
            wafer_moves[wafer_id].append(move)
        
        # 检查同批次晶圆的处理顺序
        for wafer_id, moves in wafer_moves.items():
            try:
                lot_id, wafer_num = wafer_id.split('.')
                lot_id = int(lot_id)
                wafer_num = int(wafer_num)
                
                # 查找同批次的其他晶圆
                for other_wafer_id, other_moves in wafer_moves.items():
                    if other_wafer_id == wafer_id:
                        continue
                    
                    try:
                        other_lot_id, other_wafer_num = other_wafer_id.split('.')
                        other_lot_id = int(other_lot_id)
                        other_wafer_num = int(other_wafer_num)
                        
                        if (lot_id == other_lot_id and wafer_num > other_wafer_num):
                            # 检查是否存在超片
                            self._check_overtaking(wafer_id, moves, other_wafer_id, other_moves)
                    
                    except ValueError:
                        continue
            
            except ValueError:
                continue
    
    def _check_overtaking(self, wafer_id: str, moves: List[Dict], 
                         other_wafer_id: str, other_moves: List[Dict]):
        """检查两个晶圆之间的超片情况"""
        # 获取PM处理时间
        wafer_pm_times = []
        other_pm_times = []
        
        for move in moves:
            if move['MoveType'] == 8 and move['ModuleName'].startswith('PM'):
                wafer_pm_times.append((move['ModuleName'], move['StartTime']))
        
        for move in other_moves:
            if move['MoveType'] == 8 and move['ModuleName'].startswith('PM'):
                other_pm_times.append((move['ModuleName'], move['StartTime']))
        
        # 检查相同PM的处理顺序
        for pm, start_time in wafer_pm_times:
            for other_pm, other_start_time in other_pm_times:
                if pm == other_pm and start_time < other_start_time:
                    self.violations.append({
                        'type': 'overtaking_violation',
                        'wafer_id': wafer_id,
                        'other_wafer_id': other_wafer_id,
                        'module': pm,
                        'description': f"晶圆 {wafer_id} 在 {pm} 超越了 {other_wafer_id}"
                    })
    
    def _validate_door_operations(self, move_list: List[Dict]):
        """验证门操作"""
        door_states = {}  # module -> is_open
        
        for move in move_list:
            module = move['ModuleName']
            move_type = move['MoveType']
            
            if module not in door_states:
                door_states[module] = False  # 初始门关闭
            
            if move_type == 4:  # 开门
                if door_states[module]:
                    self.violations.append({
                        'type': 'door_already_open',
                        'module': module,
                        'time': move['StartTime'],
                        'description': f"设备 {module} 的门已经是开启状态"
                    })
                door_states[module] = True
                
            elif move_type == 5:  # 关门
                if not door_states[module]:
                    self.violations.append({
                        'type': 'door_already_closed',
                        'module': module,
                        'time': move['StartTime'],
                        'description': f"设备 {module} 的门已经是关闭状态"
                    })
                door_states[module] = False
    
    def _validate_loadlock_operations(self, move_list: List[Dict]):
        """验证LoadLock操作"""
        ll_states = {}  # module -> vacuum_state
        
        for move in move_list:
            module = move['ModuleName']
            move_type = move['MoveType']
            
            if module in ['LLA', 'LLB']:  # 可抽充气的LoadLock
                if module not in ll_states:
                    ll_states[module] = False  # 初始大气状态
                
                if move_type == 6:  # 抽气
                    if ll_states[module]:
                        self.violations.append({
                            'type': 'already_vacuum',
                            'module': module,
                            'time': move['StartTime'],
                            'description': f"LoadLock {module} 已经是真空状态"
                        })
                    ll_states[module] = True
                    
                elif move_type == 7:  # 充气
                    if not ll_states[module]:
                        self.violations.append({
                            'type': 'already_atmosphere',
                            'module': module,
                            'time': move['StartTime'],
                            'description': f"LoadLock {module} 已经是大气状态"
                        })
                    ll_states[module] = False
    
    def _validate_time_consistency(self, move_list: List[Dict]):
        """验证时间一致性"""
        for move in move_list:
            if move['StartTime'] >= move['EndTime']:
                self.violations.append({
                    'type': 'invalid_time',
                    'move_id': move['MoveID'],
                    'start_time': move['StartTime'],
                    'end_time': move['EndTime'],
                    'description': f"移动 {move['MoveID']} 的开始时间不早于结束时间"
                })
    
    def print_validation_report(self, validation_result: Dict):
        """打印验证报告"""
        print("=== 约束验证报告 ===")
        
        if validation_result['valid']:
            print("✅ 调度方案满足所有约束条件")
        else:
            print(f"❌ 发现 {validation_result['violation_count']} 个约束违反")
            
            # 按类型分组显示违反情况
            violation_types = {}
            for violation in validation_result['violations']:
                vtype = violation['type']
                if vtype not in violation_types:
                    violation_types[vtype] = []
                violation_types[vtype].append(violation)
            
            for vtype, violations in violation_types.items():
                print(f"\n{vtype} ({len(violations)} 个):")
                for violation in violations[:5]:  # 只显示前5个
                    print(f"  - {violation['description']}")
                if len(violations) > 5:
                    print(f"  ... 还有 {len(violations) - 5} 个类似违反")

def validate_result_file(filename: str):
    """验证结果文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    validator = ConstraintValidator()
    result = validator.validate_schedule(data['MoveList'])
    validator.print_validation_report(result)
    
    return result