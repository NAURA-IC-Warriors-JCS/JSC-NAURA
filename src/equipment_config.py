"""
设备配置文件
定义所有设备的物理参数和时间参数
"""

# 设备映射
EQUIPMENT_MAPPING = {
    'LLA': 11, 'LLB': 12, 'LLC': 13, 'LLD': 14,
    'PM1': 1, 'PM2': 2, 'PM3': 3, 'PM4': 4, 'PM5': 5,
    'PM6': 6, 'PM7': 7, 'PM8': 8, 'PM9': 9, 'PM10': 10
}

# 反向映射
EQUIPMENT_ID_TO_NAME = {v: k for k, v in EQUIPMENT_MAPPING.items()}

# TM1参数
TM1_PARAMS = {
    'pick_time': 4.0,
    'place_time': 4.0,
    'move_time': 1.0
}

# TM2/TM3参数
TM23_PARAMS = {
    'pick_time_single': 5.0,
    'pick_time_double': 15.0,
    'place_time_single': 7.0,
    'place_time_double': 15.0,
    'move_time_adjacent': 0.5,
    'move_time_full_circle': 4.0
}

# LoadLock参数
LOADLOCK_PARAMS = {
    'LLA': {'pump_time': 15.0, 'vent_time': 20.0},
    'LLB': {'pump_time': 15.0, 'vent_time': 20.0},
    'LLC': {'fixed_vacuum': True},
    'LLD': {'fixed_vacuum': True}
}

# 门操作时间
DOOR_PARAMS = {
    'open_time': 1.0,
    'close_time': 1.0
}

# 清洁参数
CLEAN_PARAMS = {
    'idle_threshold': 80.0,
    'idle_clean_time': 30.0,
    'process_switch_clean_time': 200.0,
    'wafer_count_threshold': 13,
    'wafer_count_clean_time': 300.0
}

# TM2布局 (正八边形)
TM2_LAYOUT = {
    'LLA': 0,    # 0度
    'PM7': 1,    # 45度
    'PM8': 2,    # 90度
    'PM9': 3,    # 135度
    'LLD': 4,    # 180度
    'PM10': 5,   # 225度
    'LLC': 6,    # 270度
    'LLB': 7     # 315度
}

# TM3布局 (正八边形)
TM3_LAYOUT = {
    'LLC': 0,    # 0度
    'PM1': 1,    # 45度
    'PM2': 2,    # 90度
    'PM3': 3,    # 135度
    'LLD': 4,    # 180度
    'PM6': 5,    # 225度
    'PM5': 6,    # 270度
    'PM4': 7     # 315度
}

# 移动类型定义
MOVE_TYPES = {
    'PICK': 1,
    'PLACE': 2,
    'TRANS': 3,
    'PREPARE': 4,
    'COMPLETE': 5,
    'PUMP': 6,
    'VENT': 7,
    'PROCESS': 8,
    'CLEAN': 9
}