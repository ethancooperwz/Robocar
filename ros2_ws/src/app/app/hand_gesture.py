#!/usr/bin/env python3
# encoding: utf-8
# @data:2022/11/19
# @author:aiden
# 手势控制(hand gesture control)
import os
import cv2
import math
import time
import rclpy
import threading
import numpy as np
from rclpy.node import Node
from app.common import Heart
from geometry_msgs.msg import Twist
from interfaces.msg import Points
from std_srvs.srv import SetBool, Trigger
from rclpy.executors import MultiThreadedExecutor
from servo_controller_msgs.msg import ServosPosition
from rclpy.callback_groups import ReentrantCallbackGroup
from servo_controller.bus_servo_control import set_servo_position
from ros_robot_controller_msgs.msg import MotorsState, MotorState

class HandGestureControlNode(Node):
    def __init__(self, name):
        rclpy.init()
        super().__init__(name)
        self.name = name
        self.image = None
        self.image_sub = None
        self.running = True
        self.last_point = [0, 0]
        self.linear_speed = 0.3
        self.angular_speed = 2
        self.th = None
        self.thread_running = True
        self.machine_type = os.environ.get('MACHINE_TYPE')
        self.mecanum_pub = self.create_publisher(Twist, '/controller/cmd_vel', 1)  # 底盘控制(chassis control)

        timer_cb_group = ReentrantCallbackGroup()
        self.create_service(Trigger, '~/enter', self.enter_srv_callback, callback_group=timer_cb_group)  # 进入玩法(enter the game)
        self.create_service(Trigger, '~/exit', self.exit_srv_callback, callback_group=timer_cb_group)  # 退出玩法(exit the game)
        self.create_service(SetBool, '~/set_running', self.set_running_srv_callback)  # 开启玩法(start the game)
        self.joints_pub = self.create_publisher(ServosPosition, 'servo_controller', 1)
        Heart(self, self.name + '/heartbeat', 5, lambda _: self.exit_srv_callback(request=Trigger.Request(), response=Trigger.Response()))  # 心跳包(heartbeat package)
        self.motor_pub = self.create_publisher(MotorsState, '/ros_robot_controller/set_motor', 1)
        self.joints_pub = self.create_publisher(ServosPosition, 'servo_controller', 1)
        self.mecanum_pub.publish(Twist())

        self.set_hand_trajectory_enter_client = self.create_client(Trigger, '/hand_trajectory/enter', callback_group=timer_cb_group)
        self.set_hand_trajectory_exit_client = self.create_client(Trigger, '/hand_trajectory/exit', callback_group=timer_cb_group)
        self.set_hand_trajectory_stop_client = self.create_client(Trigger, '/hand_trajectory/stop', callback_group=timer_cb_group)
        self.set_hand_trajectory_start_client = self.create_client(Trigger, '/hand_trajectory/start', callback_group=timer_cb_group)
        self.set_hand_trajectory_start_client.wait_for_service()
        self.set_hand_trajectory_stop_client.wait_for_service()
        self.set_hand_trajectory_enter_client.wait_for_service()
        self.set_hand_trajectory_exit_client.wait_for_service()
        self.create_service(Trigger, '~/init_finish', self.get_node_state)
        self.get_logger().info('\033[1;32m%s\033[0m' % 'start')
        # self.enter_srv_callback(request=Trigger.Request(), response=Trigger.Response())
        # self.set_running_srv_callback(request=SetBool.Request(data=True), response=SetBool.Response())

    def get_node_state(self, request, response):
        response.success = True
        return response

    def send_request(self, client, msg):
        future = client.call_async(msg)
        while rclpy.ok():
            if future.done() and future.result():
                return future.result()

    def enter_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "hand gesture control enter")
        set_servo_position(self.joints_pub, 1.5, ((10, 300), (5, 500), (4, 600), (3, 0), (2, 750), (1, 500)))
        self.mecanum_pub.publish(Twist())
        
        self.send_request(self.set_hand_trajectory_enter_client, Trigger.Request())
        if self.image_sub is None:
            self.image_sub = self.create_subscription(Points, '/hand_trajectory/points', self.get_hand_points_callback, 1)
        self.thread_running = False
        
        response.success = True
        response.message = "enter"
        return response

    def exit_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "hand gesture control exit")
        self.mecanum_pub.publish(Twist())
        self.thread_running = False
        self.send_request(self.set_hand_trajectory_exit_client, Trigger.Request())
        
        try:
            if self.image_sub is not None:
                self.destroy_subscription(self.image_sub)
                self.image_sub = None
        except Exception as e:
            self.get_logger().error(str(e))
        response.success = True
        response.message = "exit"
        return response
   
    def set_running_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "set_running")
        
        if request.data:
            self.thread_running = True
            self.send_request(self.set_hand_trajectory_start_client, Trigger.Request())
        else:
            self.thread_running = False
            self.send_request(self.set_hand_trajectory_stop_client, Trigger.Request())
        self.mecanum_pub.publish(Twist())
        
        response.success = True
        response.message = "set_running"
        return response

    def move_action(self, *args):
        status = 0
        t_start = time.time()
        while self.thread_running:
            current_time = time.time()
            if status == 0 and t_start < current_time:
                status = 1
                if self.machine_type == 'JetRover_Acker':
                    twist = args[0]
                    if twist.angular.z == 0:
                        self.mecanum_pub.publish(twist)
                        t_start = current_time + args[1]/50.0/self.linear_speed
                    elif args[0].angular.z == 1:
                        set_servo_position(self.joints_pub, 0.1, ((9, 650), ))
                        time.sleep(0.2)
                        motor1 = MotorState()
                        motor1.id = 2
                        motor1.rps = 0.1
                        motor2 = MotorState()
                        motor2.id = 4
                        motor2.rps = -1.0
                        
                        msg = MotorsState()
                        msg.data = [motor1, motor2] 
                        self.motor_pub.publish(msg)
                        t_start = current_time + 1.5
                    elif args[0].angular.z == -1:
                        set_servo_position(self.joints_pub, 0.1, ((9, 350), ))
                        time.sleep(0.2)
                        motor1 = MotorState()
                        motor1.id = 2
                        motor1.rps = 1.0
                        motor2 = MotorState()
                        motor2.id = 4
                        motor2.rps = -0.1
                        msg = MotorsState()
                        msg.data = [motor1, motor2] 
                        self.motor_pub.publish(msg)
                        t_start = current_time + 1
                else:
                    twist = args[0]
                    self.mecanum_pub.publish(twist)
                    if self.machine_type == 'JetRover_Mecanum':
                        t_start = current_time + args[1]/50.0/self.linear_speed
                    elif self.machine_type == 'JetRover_Tank':
                        if twist.angular.z == 0:
                            t_start = current_time + args[1]/50.0/self.linear_speed
                        else:
                            t_start = current_time + 2*math.pi/self.angular_speed
            elif status == 1 and t_start < current_time:
                status = 0
                break
            time.sleep(0.01)
        
        if self.machine_type == 'JetRover_Acker':
            set_servo_position(self.joints_pub, 0.1, ((9, 500), ))
            motor1 = MotorState()
            motor1.id = 2
            motor1.rps = 0.0
            motor2 = MotorState()
            motor2.id = 4
            motor2.rps = 0.0
            msg = MotorsState()
            msg.data = [motor1, motor2] 
            self.motor_pub.publish(msg)
        self.mecanum_pub.publish(Twist())

    def get_hand_points_callback(self, msg):
        points = []
        left_and_right = [0]
        up_and_down = [0]
        if len(msg.points) >= 5:
            for i in msg.points:
                if int(i.x) - self.last_point[0] > 0:
                    left_and_right.append(1)
                else:
                    left_and_right.append(-1)
                if int(i.y) - self.last_point[1] > 0:
                    up_and_down.append(1)
                else:
                    up_and_down.append(-1)
                points.extend([(int(i.x), int(i.y))])
                self.last_point = [int(i.x), int(i.y)]
            line = cv2.fitLine(np.array(points), cv2.DIST_L2, 0, 0.01, 0.01)
            angle = int(abs(math.degrees(math.acos(line[0][0]))))
            twist = Twist()
            # self.get_logger().info('\033[1;32mangle: %s\033[0m' % str(angle))
            if 0 <= angle < 30:
                if sum(left_and_right) > 0:
                    if self.machine_type == 'JetRover_Mecanum':
                        twist.linear.y = float(self.linear_speed)
                    elif self.machine_type == 'JetRover_Tank':
                        twist.angular.z = float(self.angular_speed)
                    elif self.machine_type == 'JetRover_Acker':
                        twist.angular.z = 1.0
                else:
                    if self.machine_type == 'JetRover_Mecanum':
                        twist.linear.y = float(-self.linear_speed)
                    elif self.machine_type == 'JetRover_Tank':
                        twist.angular.z = float(-self.angular_speed)
                    elif self.machine_type == 'JetRover_Acker':
                        twist.angular.z = -1.0
            elif 60 < angle <= 90:
                if sum(up_and_down) > 0:
                    twist.linear.x = float(self.linear_speed)
                else:
                    twist.linear.x = float(-self.linear_speed)
            if self.th is None:
                self.th = threading.Thread(target=self.move_action, args=(twist, len(points)))
                self.th.start()
            else:
                if not self.th.is_alive():
                    self.th = threading.Thread(target=self.move_action, args=(twist, len(points)))
                    self.th.start()
                else:
                    self.thread_running = False
                    time.sleep(0.1)

def main():
    node = HandGestureControlNode('hand_gesture')
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
 
if __name__ == "__main__":
    main()
    
