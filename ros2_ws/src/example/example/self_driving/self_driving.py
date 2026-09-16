#!/usr/bin/env python3
# encoding: utf-8
# @data:2023/03/28
# @author:aiden
# 无人驾驶(autonomous driving)
import os
import cv2
import math
import time
import queue
import rclpy
import threading
import numpy as np
import sdk.pid as pid
from rclpy.node import Node
import sdk.common as common
# from app.common import Heart
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from interfaces.msg import ObjectsInfo
from std_srvs.srv import SetBool, Trigger
from sdk.common import colors, plot_one_box
from example.self_driving import lane_detect
from rclpy.executors import MultiThreadedExecutor
from servo_controller_msgs.msg import ServosPosition
from rclpy.callback_groups import ReentrantCallbackGroup
from servo_controller.bus_servo_control import set_servo_position

class SelfDrivingNode(Node):
    def __init__(self, name):
        rclpy.init()
        super().__init__(name, allow_undeclared_parameters=True, automatically_declare_parameters_from_overrides=True)
        self.name = name
        self.is_running = True
        self.pid = pid.PID(0.01, 0.0, 0.0)
        self.param_init()

        self.image_queue = queue.Queue(maxsize=2)
        self.classes = ['go', 'right', 'park', 'red', 'green', 'crosswalk']
        self.display = True
        self.bridge = CvBridge()
        self.lock = threading.RLock()
        self.colors = common.Colors()
        # signal.signal(signal.SIGINT, self.shutdown)
        self.machine_type = os.environ.get('MACHINE_TYPE')
        self.lane_detect = lane_detect.LaneDetector("yellow")

        self.mecanum_pub = self.create_publisher(Twist, '/controller/cmd_vel', 1)
        self.joints_pub = self.create_publisher(ServosPosition, '/servo_controller', 1) # 舵机控制(servo control)
        self.result_publisher = self.create_publisher(Image, '~/image_result', 1)

        self.create_service(Trigger, '~/enter', self.enter_srv_callback) # 进入玩法(enter game)
        self.create_service(Trigger, '~/exit', self.exit_srv_callback) # 退出玩法(exit game)
        self.create_service(SetBool, '~/set_running', self.set_running_srv_callback)
        # self.heart = Heart(self.name + '/heartbeat', 5, lambda _: self.exit_srv_callback(None))
        timer_cb_group = ReentrantCallbackGroup()
        self.client = self.create_client(Trigger, '/controller_manager/init_finish')
        self.client.wait_for_service()
        self.client = self.create_client(Trigger, '/yolov5/init_finish')
        self.client.wait_for_service()
        self.start_yolov5_client = self.create_client(Trigger, '/yolov5/start', callback_group=timer_cb_group)
        self.start_yolov5_client.wait_for_service()
        self.stop_yolov5_client = self.create_client(Trigger, '/yolov5/stop', callback_group=timer_cb_group)
        self.stop_yolov5_client.wait_for_service()

        self.timer = self.create_timer(0.0, self.init_process, callback_group=timer_cb_group)

    def init_process(self):
        self.timer.cancel()

        self.mecanum_pub.publish(Twist())
        if not self.get_parameter('only_line_follow').value:
            self.send_request(self.start_yolov5_client, Trigger.Request())
        if self.machine_type != 'JetRover_Tank':
            set_servo_position(self.joints_pub, 1, ((10, 500), (5, 500), (4, 250), (3, 0), (2, 750), (1, 500)))  # 初始姿态
        else:
            set_servo_position(self.joints_pub, 1, ((10, 500), (5, 500), (4, 230), (3, 0), (2, 750), (1, 500)))  # 初始姿态
        time.sleep(1)
        
        if 1:#self.get_parameter('start').value:
            self.display = True
            self.enter_srv_callback(Trigger.Request(), Trigger.Response())
            request = SetBool.Request()
            request.data = True
            self.set_running_srv_callback(request, SetBool.Response())

        #self.park_action() 
        threading.Thread(target=self.main, daemon=True).start()
        self.create_service(Trigger, '~/init_finish', self.get_node_state)
        self.get_logger().info('\033[1;32m%s\033[0m' % 'start')

    def param_init(self):
        self.start = False
        self.enter = False

        self.have_turn_right = False
        self.detect_turn_right = False
        self.detect_far_lane = False
        self.park_x = -1  # 停车标识的x像素坐标(the x-coordinate of the parking sign pixel)

        self.start_turn_time_stamp = 0
        self.count_turn = 0
        self.start_turn = False  # 开始转弯(begin turning)

        self.count_right = 0
        self.count_right_miss = 0
        self.turn_right = False  # 右转标志(right turn sign)

        self.last_park_detect = False
        self.count_park = 0
        self.stop = False  # 停下标识(the stop sign)
        self.start_park = False  # 开始泊车标识(star parking sign)

        self.count_crosswalk = 0
        self.crosswalk_distance = 0  # 离斑马线距离(the distance from the zebra crossing)
        self.crosswalk_length = 0.1 + 0.3  # 斑马线长度 + 车长(the length of the zebra crossing plus the length of the car)

        self.start_slow_down = False  # 减速标识(deceleration sign)
        self.normal_speed = 0.15  # 正常前进速度(normal forward speed)
        self.slow_down_speed = 0.1  # 减速行驶的速度(speed for decelerated driving)

        self.traffic_signs_status = None  # 记录红绿灯状态(record the status of the traffic light)
        self.red_loss_count = 0

        self.object_sub = None
        self.image_sub = None
        self.objects_info = []

    def get_node_state(self, request, response):
        response.success = True
        return response

    def send_request(self, client, msg):
        future = client.call_async(msg)
        while rclpy.ok():
            if future.done() and future.result():
                return future.result()

    def enter_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "self driving enter")
        with self.lock:
            self.start = False
            camera = 'depth_cam'#self.get_parameter('depth_camera_name').value
            self.create_subscription(Image, '/%s/rgb/image_raw' % camera, self.image_callback, 1)
            self.create_subscription(ObjectsInfo, '/yolov5/object_detect', self.get_object_callback, 1)
            self.mecanum_pub.publish(Twist())
            self.enter = True
        response.success = True
        response.message = "enter"
        return response

    def exit_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "self driving exit")
        with self.lock:
            try:
                if self.image_sub is not None:
                    self.image_sub.unregister()
                if self.object_sub is not None:
                    self.object_sub.unregister()
            except Exception as e:
                self.get_logger().info('\033[1;32m%s\033[0m' % str(e))
            self.mecanum_pub.publish(Twist())
        self.param_init()
        response.success = True
        response.message = "exit"
        return response

    def set_running_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "set_running")
        with self.lock:
            self.start = request.data
            if not self.start:
                self.mecanum_pub.publish(Twist())
        response.success = True
        response.message = "set_running"
        return response

    def shutdown(self, signum, frame):  # ctrl+c关闭处理(press Ctrl+C to terminate the process)
        self.is_running = False

    def image_callback(self, ros_image):  # 目标检查回调(target inspection callback)
        cv_image = self.bridge.imgmsg_to_cv2(ros_image, "rgb8")
        rgb_image = np.array(cv_image, dtype=np.uint8)
        if self.image_queue.full():
            # 如果队列已满，丢弃最旧的图像(if the queue is full, discard the oldest image)
            self.image_queue.get()
        # 将图像放入队列(put the image to the queue)
        self.image_queue.put(rgb_image)
    
    # 泊车处理(parking process)
    def park_action(self):
        if self.machine_type == 'JetRover_Mecanum': 
            twist = Twist()
            twist.linear.y = -0.2
            self.mecanum_pub.publish(twist)
            time.sleep(0.38/0.2)
        elif self.machine_type == 'JetRover_Acker':
            twist = Twist()
            twist.linear.x = 0.15
            twist.angular.z = twist.linear.x*math.tan(-0.6)/0.213
            self.mecanum_pub.publish(twist)
            time.sleep(3)

            twist = Twist()
            twist.linear.x = 0.15
            twist.angular.z = -twist.linear.x*math.tan(-0.6)/0.213
            self.mecanum_pub.publish(twist)
            time.sleep(2)

            twist = Twist()
            twist.linear.x = -0.15
            twist.angular.z = twist.linear.x*math.tan(-0.6)/0.213
            self.mecanum_pub.publish(twist)
            time.sleep(1.5)

            set_servo_position(self.joints_pub, 0.1, ((9, 500), ))
        else:
            twist = Twist()
            twist.angular.z = -1
            self.mecanum_pub.publish(twist)
            time.sleep(1.5)
            self.mecanum_pub.publish(Twist())
            twist = Twist()
            twist.linear.x = 0.2
            self.mecanum_pub.publish(twist)
            time.sleep(0.65/0.2)
            self.mecanum_pub.publish(Twist())
            twist = Twist()
            twist.angular.z = 1
            self.mecanum_pub.publish(twist)
            time.sleep(1.5)
        self.mecanum_pub.publish(Twist())

    def main(self):
        while self.is_running:
            time_start = time.time()
            try:
                image = self.image_queue.get(block=True, timeout=1)
            except queue.Empty:
                if not self.is_running:
                    break
                else:
                    continue
            result_image = image.copy()
            if self.start:
                h, w = image.shape[:2]

                # 获取车道线的二值化图(obtain the binary image of the lane lines)
                binary_image = self.lane_detect.get_binary(image)
                # 检测到斑马线,开启减速标志(zebra crossing detected, activate deceleration sign)
                if 450 < self.crosswalk_distance and not self.start_slow_down:  # 只有足够近时才开始减速(only start decelerating when close enough)
                    self.count_crosswalk += 1
                    if self.count_crosswalk == 3:  # 多次判断，防止误检测(multiple checks to prevent false detection)
                        self.count_crosswalk = 0
                        self.start_slow_down = True  # 减速标识(deceleration sign)
                        self.count_slow_down = time.time()  # 减速固定时间(decelerate for a fixed duration)
                else:  # 需要连续检测，否则重置(continuous detection required, otherwise reset)
                    self.count_crosswalk = 0

                twist = Twist()
                # 减速行驶处理(deceleration driving processing)
                if self.start_slow_down:
                    if self.traffic_signs_status is not None:
                        # 通过面积判断离灯灯远近，如果太近那么即使是红灯也不会停(use area to determine the distance from the traffic light. If too close, even if it's a red light, the vehicle won't stop)
                        area = abs(self.traffic_signs_status.box[0] - self.traffic_signs_status.box[2])*abs(self.traffic_signs_status.box[1] - self.traffic_signs_status.box[3])
                        if self.traffic_signs_status.class_name == 'red' and area < 1000:  # 如果遇到红灯就停车(if encountering a red light, stop the vehicle)
                            self.mecanum_pub.publish(Twist())
                            self.stop = True
                        elif self.traffic_signs_status.class_name == 'green':  # 遇到绿灯，速度放缓(if encountering a green light, reduce speed)
                            twist.linear.x = self.slow_down_speed
                            self.stop = False
                    if not self.stop:  # 其他非停止的情况速度放缓， 同时计时，时间=斑马线的长度/行驶速度(in other non-stop situations, slow down speed, and at the same time, measure time, where time equals the length of the zebra crossing divided by the driving speed)
                        twist.linear.x = self.slow_down_speed
                        if time.time() - self.count_slow_down > self.crosswalk_length/twist.linear.x:
                            self.start_slow_down = False
                else:
                    twist.linear.x = self.normal_speed  # 直走正常速度(straight ahead at normal speed)

                # 检测到 停车标识+斑马线 就减速, 让识别稳定(decelerate upon detecting a stop sign + zebra crossing to stabilize recognition)
                if 0 < self.park_x and 135 < self.crosswalk_distance:
                    twist.linear.x = self.slow_down_speed
                    if self.machine_type != 'JetRover_Acker':
                        if not self.start_park and 255 < self.crosswalk_distance:  # 离斑马线足够近时就开启停车(activate stop when close enough to the zebra crossing)
                            self.mecanum_pub.publish(Twist())
                            self.start_park = True
                            self.stop = True
                            threading.Thread(target=self.park_action).start()  
                    elif self.machine_type == 'JetRover_Acker':
                        if not self.start_park and 176 < self.crosswalk_distance:  # 离斑马线足够近时就开启停车(when close enough to the zebra crossing, initiate stopping)
                            self.mecanum_pub.publish(Twist())
                            self.start_park = True
                            self.stop = True
                            threading.Thread(target=self.park_action).start()                       
                
                # 右转及停车补线策略(right turn and stop line filling strategy)
                if self.turn_right:
                    y = self.lane_detect.add_horizontal_line(binary_image)
                    if 0 < y < 300:
                        roi = [(0, y), (w, y), (w, 0), (0, 0)]
                        cv2.fillPoly(binary_image, [np.array(roi)], [0, 0, 0])  # 将上面填充为黑色，防干扰(fill the above area with black to prevent interference)
                        min_x = cv2.minMaxLoc(binary_image)[-1][0]
                        cv2.line(binary_image, (min_x, y), (w, y), (255, 255, 255), 40)  # 画虚拟线来驱使转弯(draw virtual lines to guide the turn)
                elif 0 < self.park_x and not self.start_turn:  # 检测到停车标识需要填补线，使其保持直走(if a stop sign is detected, fill in the lines to keep the vehicle going straight)
                    if not self.detect_far_lane:
                        up, down, center = self.lane_detect.add_vertical_line_near(binary_image)
                        binary_image[:, :] = 0  # 全置黑，防止干扰(set all to black to prevent interference)
                        if 50 < center < 80:  # 当将要看不到车道线时切换到识别较远车道线(switch to recognizing farther lane lines when lane lines are about to become invisible)
                            self.detect_far_lane = True
                    else:
                        up, down = self.lane_detect.add_vertical_line_far(binary_image)
                        binary_image[:, :] = 0
                    if up != down:
                        cv2.line(binary_image, up, down, (255, 255, 255), 20)  # 手动画车道线(manually draw lane lines)

                result_image, lane_angle, lane_x = self.lane_detect(binary_image, image.copy())  # 在处理后的图上提取车道线中心(extract lane center from processed image with lane lines)
                # cv2.imshow('image', image)
                # 巡线处理(line following processing)
                if lane_x >= 0 and not self.stop:
                    if lane_x > 150:  # 转弯(turning)
                        if self.turn_right:  # 如果是检测到右转标识的转弯(if it's a right turn sign detected, initiate the turn)
                            self.count_right_miss += 1
                            if self.count_right_miss >= 50:
                                self.count_right_miss = 0
                                self.turn_right = False
                        self.count_turn += 1
                        if self.count_turn > 5 and not self.start_turn:  # 稳定转弯(steady turn)
                            self.start_turn = True
                            self.count_turn = 0
                            self.start_turn_time_stamp = time.time()
                        if self.machine_type != 'JetRover_Acker': 
                            twist.angular.z = -0.45  # 转弯速度(turning speed)
                        else:
                            twist.angular.z = twist.linear.x*math.tan(-0.6)/0.213  # 转弯速度(turning speed)
                    else:  # 直道由pid计算转弯修正(PID calculates turn correction for straight road)
                        self.count_turn = 0
                        if time.time() - self.start_turn_time_stamp > 3 and self.start_turn:
                            self.start_turn = False
                        if not self.start_turn:
                            self.pid.SetPoint = 100  # 在车道中间时线的坐标(the coordinates of the line when in the middle of the lane)
                            self.pid.update(lane_x)
                            if self.machine_type != 'JetRover_Acker':
                                twist.angular.z = common.set_range(self.pid.output, -0.8, 0.8)
                            else:
                                twist.angular.z = twist.linear.x*math.tan(common.set_range(self.pid.output, -0.1, 0.1))/0.213
                        else:
                            if self.machine_type == 'JetRover_Acker':
                                twist.angular.z = 0.15*math.tan(-0.6)/0.213  # 转弯速度(turning speed)
                    self.mecanum_pub.publish(twist)
                else:
                    self.pid.clear()

                # 绘制识别的物体，由于物体检测的速度小于线检测的速度，所以绘制的框会有所偏离(draw recognized objects. Due to the slower speed of object detection compared to line detection, the drawn boxes may deviate slightly)
                if self.objects_info != []:
                    for i in self.objects_info:
                        box = i.box
                        class_name = i.class_name
                        cls_conf = i.score
                        cls_id = self.classes.index(class_name)
                        color = colors(cls_id, True)
                        plot_one_box(
                            box,
                            result_image,
                            color=color,
                            label="{}:{:.2f}".format(class_name, cls_conf),
                        )
            else:
                time.sleep(0.01)

            bgr_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
            if self.display:
                cv2.imshow('result', bgr_image)
                key = cv2.waitKey(1)
                if key == ord('q') or key == 27:  # 按q或者esc退出(press q or esc to exit)
                    self.is_running = False
            self.result_publisher.publish(self.bridge.cv2_to_imgmsg(bgr_image, "bgr8"))
            time_d = 0.03 - (time.time() - time_start)
            if time_d > 0:
                time.sleep(time_d)
        self.mecanum_pub.publish(Twist())
        rclpy.shutdown()

    # 获取目标检测结果(get target detected result)
    def get_object_callback(self, msg):
        self.objects_info = msg.objects
        if self.objects_info == []:  # 没有识别到时重置变量(reset variables when no detection is made)
            self.traffic_signs_status = None
            self.crosswalk_distance = 0
        else:
            min_distance = 0
            for i in self.objects_info:
                class_name = i.class_name
                center = (int((i.box[0] + i.box[2])/2), int((i.box[1] + i.box[3])/2))
                
                if class_name == 'crosswalk':  
                    if center[1] > min_distance:  # 获取最近的人行道y轴像素坐标(retrieve the closest pedestrian crossing y-axis pixel coordinate)
                        min_distance = center[1]
                elif class_name == 'right':  # 获取右转标识(retrieve the right turn sign)
                    self.count_right += 1
                    self.count_right_miss = 0
                    if self.count_right >= 10:  # 检测到多次就将右转标志至真(if detected multiple times, set the right turn sign to true)
                        self.turn_right = True
                        self.count_right = 0
                elif class_name == 'park':  # 获取停车标识中心坐标(retrieve the center coordinates of the stop sign)
                    self.park_x = center[0]
                elif class_name == 'red' or class_name == 'green':  # 获取红绿灯状态(get the state of traffic light)
                    self.traffic_signs_status = i
        
            self.crosswalk_distance = min_distance

def main():
    node = SelfDrivingNode('self_driving')
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
 
if __name__ == "__main__":
    main()

