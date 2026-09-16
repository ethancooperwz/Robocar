import threading, os, time
from ros_robot_controller_sdk import Board
from bus_servo_control import BusServoControl
from action_group_controller import ActionGroupController

board = Board()
# board.enable_reception()

agc = ActionGroupController(board)
bsc = BusServoControl(board)

def getServoPulse(servo_id):
    data = bsc.getBusServoPulse(servo_id)
    if data is not None:
        return data[0]
    else:
        return None

def getServoDeviation(servo_id):
    data = bsc.getBusServoDeviation(servo_id)
    if data is not None:
        return data[0]
    else:
        return None

def setServoPulse(servo_id, pulse, use_time):
    bsc.setBusServoPulse(servo_id, pulse, use_time)

def setServoDeviation(servo_id ,dev):
    bsc.setBusServoDeviation(servo_id, dev)
    
def saveServoDeviation(servo_id):
    bsc.saveBusServoDeviation(servo_id)

def unloadServo(servo_id):
    bsc.unloadBusServo(servo_id)

def runActionGroup(num):
    threading.Thread(target=agc.runAction, args=(num, )).start()    

def stopActionGroup():    
    agc.stop_action_group()

def enable_reception(enable=True):
    res = os.popen('ros2 topic info /ros_robot_controller/enable_reception').read()
    if enable:
        board.enable_reception(not enable)
        if 'Subscription' in res: 
            time.sleep(1)
            threading.Thread(target=os.system, args=("ros2 topic pub --once /ros_robot_controller/enable_reception std_msgs/Bool \"data: true\"",), daemon=True).start()
            time.sleep(2)
    else:
        if 'Subscription' in res: 
            threading.Thread(target=os.system, args=("ros2 topic pub --once /ros_robot_controller/enable_reception std_msgs/Bool \"data: false\"",), daemon=True).start()
            time.sleep(4)
        board.enable_reception(not enable)
        time.sleep(1)

