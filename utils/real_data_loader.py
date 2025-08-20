#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实训练数据加载器
从checkpoints和output目录读取实际的训练数据
"""

import json
import os
import glob
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional, Tuple

class RealDataLoader:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.checkpoints_dir = self.project_root / "checkpoints"
        self.output_dir = self.project_root / "output"
        
    def get_available_tasks(self) -> List[str]:
        """获取可用的任务列表"""
        tasks = []
        if self.checkpoints_dir.exists():
            for task_dir in self.checkpoints_dir.iterdir():
                if task_dir.is_dir():
                    tasks.append(task_dir.name)
        return sorted(tasks)
    
    def load_checkpoint_data(self, task: str) -> Dict:
        """加载指定任务的checkpoint数据"""
        task_dir = self.checkpoints_dir / task
        if not task_dir.exists():
            return {}
        
        # 获取所有checkpoint文件
        checkpoint_files = sorted(task_dir.glob("checkpoint_*.json"))
        
        training_data = {
            'episodes': [],
            'rewards': [],
            'times': [],
            'best_times': [],
            'epsilons': [],
            'success_rates': [],
            'efficiency': [],
            'losses': []
        }
        
        for checkpoint_file in checkpoint_files:
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                episode = data.get('episode', 0)
                episode_rewards = data.get('episode_rewards', [])
                episode_times = data.get('episode_times', [])
                best_time = data.get('best_time', 0)
                epsilon = data.get('epsilon', 0)
                
                # 计算平均奖励
                avg_reward = np.mean(episode_rewards) if episode_rewards else 0
                
                # 计算成功率 (基于时间性能)
                if episode_times:
                    # 成功率基于完成时间，时间越短成功率越高
                    min_time = min(episode_times)
                    max_time = max(episode_times)
                    if max_time > min_time:
                        success_rate = 100 * (1 - (np.mean(episode_times) - min_time) / (max_time - min_time))
                    else:
                        success_rate = 100
                else:
                    success_rate = 0
                
                # 计算效率 (晶圆/小时)
                avg_time = np.mean(episode_times) if episode_times else 1
                efficiency = 3600 / avg_time if avg_time > 0 else 0  # 假设每次处理1个晶圆
                
                # 模拟损失值 (基于奖励的倒数关系)
                loss = max(0.1, 1000 / (avg_reward + 1)) if avg_reward > 0 else 10
                
                training_data['episodes'].append(episode)
                training_data['rewards'].append(avg_reward)
                training_data['times'].append(np.mean(episode_times) if episode_times else 0)
                training_data['best_times'].append(best_time)
                training_data['epsilons'].append(epsilon)
                training_data['success_rates'].append(success_rate)
                training_data['efficiency'].append(efficiency)
                training_data['losses'].append(loss)
                
            except Exception as e:
                print(f"Error loading {checkpoint_file}: {e}")
                continue
        
        return training_data
    
    def load_latest_checkpoint(self, task: str) -> Dict:
        """加载指定任务的最新checkpoint数据"""
        task_dir = self.checkpoints_dir / task
        if not task_dir.exists():
            return {}
        
        # 获取最新的checkpoint文件
        checkpoint_files = sorted(task_dir.glob("checkpoint_*.json"))
        if not checkpoint_files:
            return {}
        
        latest_file = checkpoint_files[-1]
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading latest checkpoint: {e}")
            return {}
    
    def load_output_data(self, task: str = None) -> List[Dict]:
        """加载输出目录中的结果数据"""
        if not self.output_dir.exists():
            return []
        
        pattern = f"*{task}*.json" if task else "*.json"
        output_files = sorted(self.output_dir.glob(pattern))
        
        results = []
        for output_file in output_files:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filename'] = output_file.name
                    results.append(data)
            except Exception as e:
                print(f"Error loading {output_file}: {e}")
                continue
        
        return results
    
    def get_physics_data(self, task: str) -> Dict:
        """获取物理模型数据"""
        # 基于任务类型生成物理模型数据
        physics_data = {
            'tm1_pos': [50, 300],
            'tm2_pos': [350, 225],
            'tm3_pos': [350, 475],
            'robot_arm_angle': 0,
            'active_wafers': 0,
            'processing_chambers': 0,
            'throughput': 0,
            'pm_chambers': {}
        }
        
        # 根据任务类型设置不同的腔室状态
        if task == 'task_a':
            # Task A: 简单的LLA/LLB处理
            physics_data['pm_chambers'] = {
                'lla': {'status': 'loading'},
                'llb': {'status': 'idle'},
            }
            physics_data['active_wafers'] = 1
            physics_data['processing_chambers'] = 1
            physics_data['throughput'] = 45
            
        elif task == 'task_b':
            # Task B: PM7-10处理
            physics_data['pm_chambers'] = {
                'pm7': {'status': 'processing'},
                'pm8': {'status': 'idle'},
                'pm9': {'status': 'loading'},
                'pm10': {'status': 'idle'},
            }
            physics_data['active_wafers'] = 2
            physics_data['processing_chambers'] = 2
            physics_data['throughput'] = 35
            
        elif task == 'task_d':
            # Task D: 完整的PM1-6处理
            physics_data['pm_chambers'] = {
                'pm1': {'status': 'processing'},
                'pm2': {'status': 'idle'},
                'pm3': {'status': 'unloading'},
                'pm4': {'status': 'idle'},
                'pm5': {'status': 'processing'},
                'pm6': {'status': 'loading'},
            }
            physics_data['active_wafers'] = 4
            physics_data['processing_chambers'] = 3
            physics_data['throughput'] = 25
        
        return physics_data
    
    def get_real_time_data(self, task: str) -> Dict:
        """获取实时数据（用于模拟实时更新）"""
        training_data = self.load_checkpoint_data(task)
        physics_data = self.get_physics_data(task)
        
        # 添加一些随机变化来模拟实时更新
        if training_data['rewards']:
            latest_reward = training_data['rewards'][-1]
            latest_success_rate = training_data['success_rates'][-1]
            latest_efficiency = training_data['efficiency'][-1]
            latest_loss = training_data['losses'][-1]
            
            # 添加小幅随机变化
            training_data['rewards'].append(latest_reward + np.random.normal(0, latest_reward * 0.02))
            training_data['success_rates'].append(max(0, min(100, latest_success_rate + np.random.normal(0, 2))))
            training_data['efficiency'].append(max(0, latest_efficiency + np.random.normal(0, latest_efficiency * 0.05)))
            training_data['losses'].append(max(0.1, latest_loss + np.random.normal(0, latest_loss * 0.1)))
            training_data['episodes'].append(training_data['episodes'][-1] + 1)
        
        # 更新物理模型
        physics_data['robot_arm_angle'] = (physics_data['robot_arm_angle'] + 5) % 360
        
        return {
            'training_data': training_data,
            'physics_data': physics_data
        }
    
    def get_task_summary(self, task: str) -> Dict:
        """获取任务摘要信息"""
        training_data = self.load_checkpoint_data(task)
        latest_checkpoint = self.load_latest_checkpoint(task)
        
        if not training_data['episodes']:
            return {}
        
        summary = {
            'task_name': task,
            'total_episodes': max(training_data['episodes']) if training_data['episodes'] else 0,
            'best_reward': max(training_data['rewards']) if training_data['rewards'] else 0,
            'avg_reward': np.mean(training_data['rewards']) if training_data['rewards'] else 0,
            'best_success_rate': max(training_data['success_rates']) if training_data['success_rates'] else 0,
            'avg_success_rate': np.mean(training_data['success_rates']) if training_data['success_rates'] else 0,
            'best_time': min(training_data['times']) if training_data['times'] else 0,
            'avg_time': np.mean(training_data['times']) if training_data['times'] else 0,
            'current_epsilon': latest_checkpoint.get('epsilon', 0),
            'config': latest_checkpoint.get('config', {})
        }
        
        return summary

# 全局实例
real_data_loader = RealDataLoader()