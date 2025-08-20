import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from typing import Dict, List, Tuple
import json

class WaferPhysicsModel:
    """晶圆物理模型"""
    
    def __init__(self, wafer_radius: float = 0.15):
        self.wafer_radius = wafer_radius
        self.temperature = 25.0  # 初始温度 (°C)
        self.pressure = 1.0      # 初始压力 (atm)
        self.position = np.array([0.0, 0.0])  # 位置 (x, y)
        self.velocity = np.array([0.0, 0.0])  # 速度 (m/s)
        self.acceleration = np.array([0.0, 0.0])  # 加速度 (m/s²)
        
    def update_physics(self, dt: float, force: np.ndarray):
        """更新物理状态"""
        # 牛顿第二定律: F = ma
        mass = 0.1  # 晶圆质量 (kg)
        self.acceleration = force / mass
        
        # 更新速度和位置
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        
        # 添加阻尼
        damping = 0.95
        self.velocity *= damping
    
    def update_thermal(self, target_temp: float, dt: float):
        """更新热力学状态"""
        # 简单的热传导模型
        thermal_conductivity = 0.1
        temp_diff = target_temp - self.temperature
        self.temperature += thermal_conductivity * temp_diff * dt

class ChamberPhysicsModel:
    """腔室物理模型"""
    
    def __init__(self, chamber_id: int, position: Tuple[float, float]):
        self.chamber_id = chamber_id
        self.position = np.array(position)
        self.temperature = 25.0
        self.pressure = 1.0
        self.is_occupied = False
        self.process_time = 0.0
        self.target_temp = 25.0
        
    def start_process(self, process_temp: float, process_time: float):
        """开始工艺过程"""
        self.target_temp = process_temp
        self.process_time = process_time
        self.is_occupied = True
    
    def update(self, dt: float):
        """更新腔室状态"""
        if self.is_occupied:
            # 温度控制
            temp_diff = self.target_temp - self.temperature
            heating_rate = 10.0  # °C/s
            self.temperature += np.sign(temp_diff) * min(abs(temp_diff), heating_rate * dt)
            
            # 工艺时间倒计时
            self.process_time -= dt
            if self.process_time <= 0:
                self.is_occupied = False
                self.target_temp = 25.0

class RobotArmPhysicsModel:
    """机械臂物理模型"""
    
    def __init__(self, base_position: Tuple[float, float]):
        self.base_position = np.array(base_position)
        self.arm_length = 2.0
        self.joint_angle = 0.0  # 关节角度 (弧度)
        self.angular_velocity = 0.0  # 角速度 (rad/s)
        self.target_angle = 0.0
        self.is_carrying_wafer = False
        
    def get_end_effector_position(self) -> np.ndarray:
        """获取末端执行器位置"""
        x = self.base_position[0] + self.arm_length * np.cos(self.joint_angle)
        y = self.base_position[1] + self.arm_length * np.sin(self.joint_angle)
        return np.array([x, y])
    
    def move_to_target(self, target_position: np.ndarray, dt: float):
        """移动到目标位置"""
        # 计算目标角度
        relative_pos = target_position - self.base_position
        self.target_angle = np.arctan2(relative_pos[1], relative_pos[0])
        
        # PID控制器
        angle_error = self.target_angle - self.joint_angle
        # 处理角度环绕
        while angle_error > np.pi:
            angle_error -= 2 * np.pi
        while angle_error < -np.pi:
            angle_error += 2 * np.pi
        
        # 简单P控制
        kp = 5.0
        target_angular_velocity = kp * angle_error
        
        # 角速度限制
        max_angular_velocity = 2.0  # rad/s
        target_angular_velocity = np.clip(target_angular_velocity, 
                                        -max_angular_velocity, max_angular_velocity)
        
        # 更新角速度和角度
        self.angular_velocity = target_angular_velocity
        self.joint_angle += self.angular_velocity * dt

class FabPhysicsSimulator:
    """晶圆厂物理仿真器"""
    
    def __init__(self):
        self.wafers = []
        self.chambers = [
            ChamberPhysicsModel(0, (1.0, 1.5)),
            ChamberPhysicsModel(1, (1.0, 3.5)),
            ChamberPhysicsModel(2, (1.0, 5.5))
        ]
        self.robot = RobotArmPhysicsModel((5.0, 3.5))
        self.time = 0.0
        self.dt = 0.1  # 时间步长
        
    def add_wafer(self, wafer_id: int):
        """添加晶圆"""
        wafer = WaferPhysicsModel()
        wafer.wafer_id = wafer_id
        wafer.position = np.array([8.0, 3.5])  # 初始位置
        self.wafers.append(wafer)
    
    def update(self):
        """更新仿真状态"""
        # 更新腔室
        for chamber in self.chambers:
            chamber.update(self.dt)
        
        # 更新机械臂
        if self.wafers and not self.robot.is_carrying_wafer:
            # 移动到晶圆位置
            target_wafer = self.wafers[0]
            self.robot.move_to_target(target_wafer.position, self.dt)
        
        # 更新晶圆物理
        for wafer in self.wafers:
            # 如果被机械臂抓取，跟随机械臂运动
            if self.robot.is_carrying_wafer:
                wafer.position = self.robot.get_end_effector_position()
            else:
                # 重力作用
                gravity_force = np.array([0.0, -9.8 * 0.1])  # 简化重力
                wafer.update_physics(self.dt, gravity_force)
        
        self.time += self.dt
    
    def visualize_realtime(self, training_data: List[Dict] = None):
        """实时可视化"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(-1, 10)
        ax.set_ylim(0, 7)
        ax.set_aspect('equal')
        ax.set_title('晶圆厂物理仿真', fontsize=14, fontweight='bold')
        
        # 绘制静态元素
        chamber_patches = []
        for i, chamber in enumerate(self.chambers):
            color = 'lightcoral' if chamber.is_occupied else 'lightblue'
            patch = FancyBboxPatch((chamber.position[0]-0.5, chamber.position[1]-0.5),
                                 1.0, 1.0, boxstyle="round,pad=0.1",
                                 facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(patch)
            chamber_patches.append(patch)
            
            # 添加温度显示
            ax.text(chamber.position[0], chamber.position[1]+0.7, 
                   f'Chamber {i+1}', ha='center', fontweight='bold')
        
        # 机械臂基座
        base_circle = Circle(self.robot.base_position, 0.2, 
                           facecolor='orange', edgecolor='black', linewidth=2)
        ax.add_patch(base_circle)
        
        # 机械臂
        arm_line, = ax.plot([], [], 'k-', linewidth=4)
        end_effector = Circle((0, 0), 0.1, facecolor='red', edgecolor='black')
        ax.add_patch(end_effector)
        
        # 晶圆
        wafer_circles = []
        for wafer in self.wafers:
            circle = Circle(wafer.position, wafer.wafer_radius, 
                          facecolor='silver', edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            wafer_circles.append(circle)
        
        # 信息显示
        info_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                          verticalalignment='top', fontsize=10,
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        def animate(frame):
            self.update()
            
            # 更新机械臂
            end_pos = self.robot.get_end_effector_position()
            arm_line.set_data([self.robot.base_position[0], end_pos[0]],
                            [self.robot.base_position[1], end_pos[1]])
            end_effector.center = end_pos
            
            # 更新晶圆位置
            for i, wafer in enumerate(self.wafers):
                if i < len(wafer_circles):
                    wafer_circles[i].center = wafer.position
            
            # 更新腔室颜色
            for i, chamber in enumerate(self.chambers):
                if i < len(chamber_patches):
                    color = 'lightcoral' if chamber.is_occupied else 'lightblue'
                    chamber_patches[i].set_facecolor(color)
            
            # 更新信息显示
            info = f"仿真时间: {self.time:.1f}s\n"
            info += f"机械臂角度: {np.degrees(self.robot.joint_angle):.1f}°\n"
            for i, chamber in enumerate(self.chambers):
                info += f"腔室{i+1}: {chamber.temperature:.1f}°C "
                info += f"{'占用' if chamber.is_occupied else '空闲'}\n"
            
            info_text.set_text(info)
        
        # 创建动画
        anim = animation.FuncAnimation(fig, animate, interval=100, blit=False)
        plt.tight_layout()
        plt.show()
        
        return anim

def main():
    """演示物理仿真"""
    simulator = FabPhysicsSimulator()
    
    # 添加一些晶圆
    for i in range(2):
        simulator.add_wafer(i)
    
    # 启动一些工艺过程
    simulator.chambers[0].start_process(200.0, 5.0)
    simulator.chambers[1].start_process(150.0, 3.0)
    
    # 开始可视化
    anim = simulator.visualize_realtime()
    
    print("物理仿真演示完成！")

if __name__ == "__main__":
    main()