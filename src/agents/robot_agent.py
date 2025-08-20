"""
机械臂智能体
负责决策机械臂的移动、取放晶圆等操作
"""

import numpy as np
import random
from typing import List, Dict, Any, Tuple
from .base_agent import BaseAgent

class RobotAgent(BaseAgent):
    """机械臂智能体"""
    
    def __init__(self, robot_arm):
        super().__init__(f"robot_{robot_arm.arm_id}", "robot")
        self.robot_arm = robot_arm
        self.state_dim = 18
        self.action_dim = 10  # 空闲、移动到位置0-7、取晶圆、放晶圆
        
        # Q表
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
    
    def get_state(self, environment) -> np.ndarray:
        """获取机械臂状态"""
        state = self.robot_arm.get_state_vector(environment.current_time)
        
        # 添加环境信息
        env_info = np.zeros(6)
        
        # 可取的晶圆数量
        pickable_wafers = 0
        for wafer in environment.wafers:
            if (wafer.status == 'waiting' and 
                wafer.current_location and
                not wafer.is_completed()):
                pickable_wafers += 1
        env_info[0] = pickable_wafers
        
        # 可放置的腔室数量
        available_chambers = 0
        for chamber in environment.chambers.values():
            if chamber.can_accept_wafer(None):  # 简化检查
                available_chambers += 1
        env_info[1] = available_chambers
        
        # 当前时间
        env_info[2] = environment.current_time % 1000
        
        # 合并状态
        full_state = np.concatenate([state, env_info])
        return full_state[:self.state_dim]
    
    def get_action_space(self) -> List[int]:
        """获取动作空间"""
        return list(range(self.action_dim))
    
    def get_valid_actions(self, environment) -> List[int]:
        """获取有效动作"""
        valid_actions = []
        
        if self.robot_arm.can_perform_action():
            valid_actions.append(0)  # 保持空闲
            
            # 移动动作 (位置0-7)
            if hasattr(self.robot_arm, 'layout'):  # TM2/TM3
                for pos in range(8):
                    if pos != self.robot_arm.current_position:
                        valid_actions.append(pos + 1)
            
            # 取晶圆动作
            if not self.robot_arm.holding_wafer:
                # 检查当前位置是否有可取的晶圆
                current_chamber = self._get_chamber_at_current_position(environment)
                if current_chamber and current_chamber.current_wafer:
                    valid_actions.append(8)  # 取晶圆
            
            # 放晶圆动作
            if self.robot_arm.holding_wafer:
                current_chamber = self._get_chamber_at_current_position(environment)
                if current_chamber and current_chamber.can_accept_wafer(self.robot_arm.holding_wafer):
                    valid_actions.append(9)  # 放晶圆
        
        if not valid_actions:
            valid_actions.append(0)  # 默认空闲
        
        return valid_actions
    
    def _get_chamber_at_current_position(self, environment):
        """获取当前位置的腔室"""
        if hasattr(self.robot_arm, 'layout'):
            chamber_name = self.robot_arm.get_chamber_at_position(self.robot_arm.current_position)
            if chamber_name:
                return environment.chambers.get(chamber_name)
        return None
    
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
        
        # 成功取放晶圆的奖励
        if action_result.get('pick_success', False):
            reward += 10.0
        if action_result.get('place_success', False):
            reward += 10.0
        
        # 移动效率奖励
        move_efficiency = action_result.get('move_efficiency', 0)
        reward += move_efficiency * 3.0
        
        # 减少空闲时间的奖励
        if action_result.get('productive_action', False):
            reward += 5.0
        
        # 协调性奖励（与其他机械臂配合）
        if action_result.get('coordination_bonus', False):
            reward += 8.0
        
        # 无效动作惩罚
        if action_result.get('invalid_action', False):
            reward -= 15.0
        
        # 碰撞或冲突惩罚
        if action_result.get('conflict', False):
            reward -= 20.0
        
        # 长时间空闲惩罚
        idle_time = action_result.get('idle_time', 0)
        if idle_time > 5:
            reward -= idle_time * 0.2
        
        return reward
    
    def get_action_description(self, action: int) -> str:
        """获取动作描述"""
        if action == 0:
            return "保持空闲"
        elif 1 <= action <= 8:
            return f"移动到位置{action-1}"
        elif action == 8:
            return "取晶圆"
        elif action == 9:
            return "放晶圆"
        else:
            return "未知动作"
    
    def execute_action(self, action: int, environment, current_time: float) -> Dict:
        """执行动作并返回结果"""
        result = {
            'success': False,
            'pick_success': False,
            'place_success': False,
            'move_efficiency': 0.0,
            'productive_action': False,
            'invalid_action': False,
            'conflict': False,
            'idle_time': 0.0
        }
        
        if action == 0:  # 空闲
            result['idle_time'] = 1.0
            result['success'] = True
            
        elif 1 <= action <= 8:  # 移动
            target_pos = action - 1
            if target_pos != self.robot_arm.current_position:
                move_time = self.robot_arm.calculate_move_time(
                    self.robot_arm.current_position, target_pos)
                self.robot_arm.start_move(target_pos, current_time)
                
                # 计算移动效率
                result['move_efficiency'] = 1.0 / (move_time + 0.1)
                result['productive_action'] = True
                result['success'] = True
            else:
                result['invalid_action'] = True
                
        elif action == 8:  # 取晶圆
            if not self.robot_arm.holding_wafer:
                chamber = self._get_chamber_at_current_position(environment)
                if chamber and chamber.current_wafer:
                    self.robot_arm.start_pick(chamber.current_wafer, current_time)
                    result['pick_success'] = True
                    result['productive_action'] = True
                    result['success'] = True
                else:
                    result['invalid_action'] = True
            else:
                result['invalid_action'] = True
                
        elif action == 9:  # 放晶圆
            if self.robot_arm.holding_wafer:
                chamber = self._get_chamber_at_current_position(environment)
                if chamber and chamber.can_accept_wafer(self.robot_arm.holding_wafer):
                    self.robot_arm.start_place(current_time)
                    result['place_success'] = True
                    result['productive_action'] = True
                    result['success'] = True
                else:
                    result['invalid_action'] = True
            else:
                result['invalid_action'] = True
        
        return result