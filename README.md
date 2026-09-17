# Robocar

基于Ubuntu和ROS 2 Humble的 Robocar无人小车项目，包含底盘控制、机械臂、外设驱动、SLAM建图、导航、视觉示例和WiFi管理等功能。

## 系统环境

- Ubuntu 22.04
- ROS 2 Humble
- 默认终端：Zsh
- 小车用户：`ubuntu`
- ROS 2工作空间：`/home/ubuntu/ros2_ws`

> 本项目依赖小车原有的系统环境、硬件驱动和ROS 2依赖，仅克隆仓库不一定能在普通电脑上直接运行。

## 目录结构

| 目录 | 说明 |
|---|---|
| `ros2_ws/` | ROS 2 主工作空间 |
| `ros2_ws/src/bringup/` | 整车启动脚本 |
| `ros2_ws/src/driver/` | 底盘、舵机等硬件驱动 |
| `ros2_ws/src/peripherals/` | 相机、控制器等外设 |
| `ros2_ws/src/slam/` | SLAM 建图 |
| `ros2_ws/src/navigation/` | 自动导航 |
| `ros2_ws/src/example/` | 功能示例 |
| `software/` | 标定、舵机和上位机工具 |
| `large_models/` | 大模型相关程序 |
| `wifi_manager/` | WiFi 自动连接和 AP 热点管理 |

## 加载ROS 2环境

Robocar默认使用 Zsh。

```zsh
zsh
source /opt/ros/humble/setup.zsh
source /home/ubuntu/ros2_ws/install/setup.zsh
```

如果已经通过 `.zshrc` 自动加载ROS环境，可以直接使用ROS 2命令。

## 检查系统状态

查看正在运行的ROS 2节点：

```zsh
ros2 node list
```

查看全部话题：

```zsh
ros2 topic list
```

查看机械臂和舵机相关话题：

```zsh
ros2 topic list | grep -E 'joint_states|servo_states|servo_controller'
```

查看一次关节状态：

```zsh
ros2 topic echo /joint_states --once
```

## 启动Robocar

启动整车基础节点：

```zsh
ros2 launch bringup bringup.launch.py
```

启动SLAM建图：

```zsh
bash /home/ubuntu/ros2_ws/src/bringup/scripts/slam.sh
```

启动导航：

```zsh
bash /home/ubuntu/ros2_ws/src/bringup/scripts/navigation.sh
```

## WiFi管理

WiFi管理程序位于：

```text
/home/ubuntu/wifi_manager/wifi.py
```

配置文件位于：

```text
/etc/wifi/wifi_conf.py
```

当前开机通信连接逻辑：
1. NetworkManager自动尝试连接曾经保存过的WiFi。
2. 屏幕连接过的新WiFi会由NetworkManager保存。
3. 如果规定时间内没有连接成功，小车会创建`HW-xxxxxxxx`AP热点。
4. AP默认密码由 `wifi_conf.py`中的`WIFI_AP_PASSWORD`设置。

检查当前连接：

```zsh
nmcli -t -f ACTIVE,SSID dev wifi
```

查看所有已保存网络：

```zsh
nmcli connection show
```

检查WiFi服务：

```zsh
systemctl status wifi.service --no-pager
```

查看WiFi日志：

```zsh
tail -n 30 /home/ubuntu/wifi_manager/wifi.log
```

重启WiFi服务：

```zsh
sudo systemctl restart wifi.service
```

## 编译ROS 2工作空间

需要重新编译时：

```zsh
cd /home/ubuntu/ros2_ws
source /opt/ros/humble/setup.zsh
colcon build --symlink-install
source install/setup.zsh
```

## Git 使用注意事项

以下内容未提交到GitHub：

- Python 虚拟环境，例如 `.venv/`
- ROS 2 的 `build/`、`install/`、`log/`
- 模型权重，例如 `.pt`、`.onnx`、`.engine`
- 运行日志和缓存
- 大型第三方依赖

提交前建议检查：

```zsh
git status
git diff
```

## 更新记录

- 2026-09-17：WiFi改为自动连接已保存网络，连接失败后回退到AP热点。
