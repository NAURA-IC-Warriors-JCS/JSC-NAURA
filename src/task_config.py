"""
任务配置文件
定义所有晶圆任务分配
"""

# 任务a: 75片晶圆全部执行工艺A
TASK_A = []
for lot in range(1, 4):  # 1.x, 2.x, 3.x
    for wafer in range(1, 26):  # x.1 到 x.25
        TASK_A.append({
            'wafer_id': f"{lot}.{wafer}",
            'process_type': 'A',
            'lot_id': lot,
            'wafer_num': wafer
        })

# 任务b: 75片晶圆全部执行工艺B
TASK_B = []
for lot in range(1, 4):
    for wafer in range(1, 26):
        TASK_B.append({
            'wafer_id': f"{lot}.{wafer}",
            'process_type': 'B',
            'lot_id': lot,
            'wafer_num': wafer
        })

# 任务c: 第1批工艺C，第2、3批工艺D
TASK_C = []
# 第1批: 工艺C
for wafer in range(1, 26):
    TASK_C.append({
        'wafer_id': f"1.{wafer}",
        'process_type': 'C',
        'lot_id': 1,
        'wafer_num': wafer
    })
# 第2、3批: 工艺D
for lot in range(2, 4):
    for wafer in range(1, 26):
        TASK_C.append({
            'wafer_id': f"{lot}.{wafer}",
            'process_type': 'D',
            'lot_id': lot,
            'wafer_num': wafer
        })

# 任务d: 复杂工艺分配
TASK_D = []
# 1.1-1.10: 工艺E
for wafer in range(1, 11):
    TASK_D.append({
        'wafer_id': f"1.{wafer}",
        'process_type': 'E',
        'lot_id': 1,
        'wafer_num': wafer
    })
# 1.11-1.25: 工艺F
for wafer in range(11, 26):
    TASK_D.append({
        'wafer_id': f"1.{wafer}",
        'process_type': 'F',
        'lot_id': 1,
        'wafer_num': wafer
    })
# 2.1-2.5: 工艺G
for wafer in range(1, 6):
    TASK_D.append({
        'wafer_id': f"2.{wafer}",
        'process_type': 'G',
        'lot_id': 2,
        'wafer_num': wafer
    })
# 2.6-2.15: 工艺H
for wafer in range(6, 16):
    TASK_D.append({
        'wafer_id': f"2.{wafer}",
        'process_type': 'H',
        'lot_id': 2,
        'wafer_num': wafer
    })
# 2.16-2.25: 工艺I
for wafer in range(16, 26):
    TASK_D.append({
        'wafer_id': f"2.{wafer}",
        'process_type': 'I',
        'lot_id': 2,
        'wafer_num': wafer
    })
# 3.1-3.15: 工艺J
for wafer in range(1, 16):
    TASK_D.append({
        'wafer_id': f"3.{wafer}",
        'process_type': 'J',
        'lot_id': 3,
        'wafer_num': wafer
    })
# 3.16-3.25: 工艺K
for wafer in range(16, 26):
    TASK_D.append({
        'wafer_id': f"3.{wafer}",
        'process_type': 'K',
        'lot_id': 3,
        'wafer_num': wafer
    })

# 任务字典
TASKS = {
    'a': TASK_A,
    'b': TASK_B,
    'c': TASK_C,
    'd': TASK_D
}

def get_task_wafers(task_name):
    """获取指定任务的晶圆列表"""
    return TASKS.get(task_name.lower(), [])

def get_wafer_process_route(wafer_info):
    """获取晶圆的工艺路径"""
    from .process_config import PROCESS_ROUTES
    return PROCESS_ROUTES.get(wafer_info['process_type'], [])