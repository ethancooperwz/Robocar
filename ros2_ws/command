#关闭所有ros节点
~/.stop_ros.sh

#编译
cd ~/ros2_ws && ~/.build.sh
#colcon build --event-handlers  console_direct+  --cmake-args  -DCMAKE_BUILD_TYPE=Release --symlink-install
#单独编译某个包
colcon build --event-handlers  console_direct+  --cmake-args  -DCMAKE_BUILD_TYPE=Release --symlink-install --packages-select xxx

#######calibration#######
#角速度校准(mecanum, tank)
ros2 launch calibration angular_calib.launch.py

#线速度校准(mecanum, tank)
ros2 launch calibration linear_calib.launch.py

#imu校准
ros2 launch ros_robot_controller ros_robot_controller.launch.py
ros2 run imu_calib do_calib --ros-args -r imu:=/ros_robot_controller/imu_raw --param output_file:=/home/ubuntu/ros2_ws/src/calibration/config/imu_calib.yaml

#查看imu校准效果
ros2 launch peripherals imu_view.launch.py

#深度摄像头点云可视化(Dabai)
#深度摄像头RGB图像可视化(Dabai)
ros2 launch peripherals depth_camera.launch.py
rviz2

#单目摄像头可视化
ros2 launch peripherals usb_cam.launch.py
rviz2

#雷达数据可视化
ros2 launch peripherals lidar_view.launch.py

#######app#######
#雷达功能
ros2 launch app lidar_node.launch.py debug:=true
#雷达避障
ros2 service call /lidar_app/enter std_srvs/srv/Trigger {}
ros2 service call /lidar_app/set_running interfaces/srv/SetInt64 "{data: 1}"

#雷达跟随
ros2 service call /lidar_app/enter std_srvs/srv/Trigger {}
ros2 service call /lidar_app/set_running interfaces/srv/SetInt64 "{data: 2}"

#雷达警卫
ros2 service call /lidar_app/enter std_srvs/srv/Trigger {}
ros2 service call /lidar_app/set_running interfaces/srv/SetInt64 "{data: 3}"

#巡线
ros2 launch app line_following_node.launch.py debug:=true
ros2 service call /line_following/enter std_srvs/srv/Trigger {}
#鼠标左键点击画面取色
ros2 service call /line_following/set_running std_srvs/srv/SetBool "{data: True}"

#目标跟踪
ros2 launch app object_tracking_node.launch.py debug:=true
ros2 service call /object_tracking/enter std_srvs/srv/Trigger {}
#鼠标左键点击画面取色
ros2 service call /object_tracking/set_running std_srvs/srv/SetBool "{data: True}"

#ar
ros2 launch app ar_app_node.launch.py debug:=true
ros2 service call /ar_app/enter std_srvs/srv/Trigger {}
ros2 service call /ar_app/set_model interfaces/srv/SetString "{data: \"bicycle\"}"

#hand_gesture
ros2 launch app hand_gesture_node.launch.py debug:=true
ros2 service call /hand_gesture/enter std_srvs/srv/Trigger {}
ros2 service call /hand_gesture/set_running std_srvs/srv/SetBool "{data: True}"

#######example#######
#二维码生成
cd ~/ros2_ws/src/example/example/qrcode && python3 qrcode_creater.py
#####################
ros2 launch peripherals depth_camera.launch.py

#二维码检测
cd ~/ros2_ws/src/example/example/qrcode && python3 qrcode_detecter.py

#人脸检测
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 face_detect.py

#人脸网格
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 face_mesh.py

#手关键点检测
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 hand.py

#肢体关键点检测
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 pose.py

#背景分割
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 self_segmentation.py

#整体检测
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 holistic.py

#3D物体检测
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 objectron.py

#指尖轨迹
cd ~/ros2_ws/src/example/example/mediapipe_example && python3 hand_gesture.py

#颜色识别
cd ~/ros2_ws/src/example/example/color_detect && python3 color_detect_demo.py
#####################
#垃圾分类
ros2 launch example garbage_classification.launch.py debug:=true

#肢体姿态控制
ros2 launch example body_control.launch.py

#肢体姿态融合RGB控制
ros2 launch example body_and_rgb_control.launch.py

#人体跟踪(Dabai)
ros2 launch example body_track.launch.py

#跌倒检测
ros2 launch example fall_down_detect.launch.py

#颜色分捡
ros2 launch example color_sorting_node.launch.py debug:=true

#颜色追踪
ros2 launch example color_track_node.launch.py

#手势控制
ros2 launch example hand_gesture_control_node.launch.py

#手部跟踪
ros2 launch example hand_track_node.launch.py

#指尖控制
ros2 launch example finger_control.launch.py

#指尖轨迹
ros2 launch example hand_trajectory_node.launch.py

#巡线清障(mecanum, tank)
ros2 launch example line_follow_clean_node.launch.py debug:=true

#颜色夹取
ros2 launch example automatic_pick.launch.py debug:=true
#开启夹取
ros2 service call /automatic_pick/pick std_srvs/srv/Trigger {}
#开启放置
ros2 service call /automatic_pick/place std_srvs/srv/Trigger {}

#导航搬运
ros2 launch example navigation_transport.launch.py map:=map_01

#过独木桥(深度相机)(mecanum, tank)(Dabai)
ros2 launch example cross_bridge.launch.py debug:=true

#三维夹取(深度相机)(Dabai)
ros2 launch example object_classification.launch.py

#防跌落(深度相机)(mecanum, tank)(Dabai)
ros2 launch example prevent_falling.launch.py debug:=true

#跟踪夹取(深度相机)(Dabai)
ros2 launch example track_and_grab.launch.py

#物体跟踪(深度相机)(mecanum, tank)(Dabai)
ros2 launch example track_object.launch.py

#语音控制跟踪夹取(深度相机)(Dabai)
ros2 launch example vc_track_and_grab.launch.py

#语音控制三维夹取(深度相机)(Dabai)
ros2 launch example vc_object_classification.launch.py

#无人驾驶
ros2 launch example self_driving.launch.py
#######slam#######
#2D建图
ros2 launch slam slam.launch.py

#rviz查看建图效果
ros2 launch slam rviz_slam.launch.py

#键盘控制(可选)
ros2 launch peripherals teleop_key_control.launch.py

#保存地图
#/home/ubuntu/ros2_ws/src/slam/maps/map_01.yaml
cd ~/ros2_ws/src/slam/maps && ros2 run nav2_map_server map_saver_cli -f "map_01" --ros-args -p map_subscribe_transient_local:=true

#cd ~/ros2_ws/src/slam/maps && ros2 run nav2_map_server map_saver_cli -f "保存名称" --ros-args -p map_subscribe_transient_local:=true -r __ns:=/robot_1

#3D建图(Dabai)
ros2 launch slam rtabmap_slam.launch.py

#rviz查看建图效果
ros2 launch slam rviz_rtabmap.launch.py

#键盘控制(可选)
ros2 launch peripherals teleop_key_control.launch.py

#######navigation#######
#2D导航
##rviz发布导航目标
ros2 launch navigation rviz_navigation.launch.py
ros2 launch navigation navigation.launch.py map:=地图名称

#3D导航(Dabai)
ros2 launch navigation rtabmap_navigation.launch.py

#rviz发布导航目标
ros2 launch navigation rviz_rtabmap_navigation.launch.py

#######simulations#######
#urdf可视化
ros2 launch jetrover_description display.launch.py

#######xf_mic_asr_offline#######
#语音控制机械臂
ros2 launch xf_mic_asr_offline voice_control_arm.launch.py

#语音控制颜色识别
ros2 launch xf_mic_asr_offline voice_control_color_detect.launch.py

#语音控制颜色分类
ros2 launch xf_mic_asr_offline voice_control_color_sorting.launch.py

#语音控制颜色跟踪
ros2 launch xf_mic_asr_offline voice_control_color_track.launch.py

#语音控制移动
ros2 launch xf_mic_asr_offline voice_control_move.launch.py

#语音控制垃圾分类
ros2 launch xf_mic_asr_offline voice_control_garbage_classification.launch.py

#语音控制导航
ros2 launch xf_mic_asr_offline voice_control_navigation.launch.py map:='地图名称'

#语音控制导航搬运
ros2 launch xf_mic_asr_offline voice_control_navigation_transport.launch.py map:='地图名称'

########software
ros2 launch peripherals depth_camera.launch.py

#lab_tool
python3 ~/software/lab_tool/main.py

#collect_picture
python3 ~/software/collect_picture/main.py

#servo_tool
python3 ~/software/servo_tool/main.py

#######large_models_examples#######
#前后左右，横向移动，然后漂移
ros2 launch large_models_examples llm_control_move.launch.py

#追踪红色物体
#ros2 topic pub --once /vocal_detect/asr_result std_msgs/msg/String '{data: "追踪红色物体"}'
ros2 launch large_models_examples llm_color_track.launch.py

#沿着黑线走，遇到障碍就停下
ros2 launch large_models_examples llm_visual_patrol.launch.py

#描述下你看到了什么
ros2 launch large_models_examples vllm_with_camera.launch.py

#跟着前面穿白色衣服的人
ros2 launch large_models_examples vllm_track.launch.py

#去前台看看大门有没有关，然后回来告诉我
ros2 launch large_models_examples vllm_navigation.launch.py map:=map_01

ros2 launch large_models_examples automatic_transport.launch.py debug:=pick/debug:=place

#我在客厅，将厨房的早晨拿给我
ros2 launch large_models_examples vllm_transport_dietitianl.launch.py map:=map_01
