#!/usr/bin/env python3
import os, time
import Jetson.GPIO as GPIO
from ros_robot_controller.ros_robot_controller_sdk import Board
key1_pin = 25 # wifi切换回ap
key2_pin = 4  # 关机

def reset_wifi():
    os.system("sudo rm /etc/wifi/* -rf > /dev/null 2>&1")
    os.system("sudo systemctl restart wifi.service > /dev/null 2>&1")

if __name__ == "__main__":
    board = Board()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(key1_pin, GPIO.IN)
    GPIO.setup(key2_pin, GPIO.IN)

    key1_pressed = False
    key2_pressed = False
    count = 0
    while True:
        if GPIO.input(key1_pin) == GPIO.LOW:
            time.sleep(0.05)
            if GPIO.input(key1_pin) == GPIO.LOW:
                count += 1
                if count == 2 and not key1_pressed:
                    count = 0
                    board.set_buzzer(1900, 0.2, 0.01, 1)
                    key1_pressed = True
                    print('reset_wifi')
                    reset_wifi()
            else:
                count = 0
                key1_pressed = False
                continue
            
        elif GPIO.input(key2_pin) == GPIO.LOW:
            time.sleep(0.05)
            if GPIO.input(key2_pin) == GPIO.LOW:
                count += 1
                if count == 30 and not key2_pressed:
                    count = 0
                    board.set_buzzer(2500, 0.5, 0.01, 1)
                    key2_pressed = True
                    print('sudo halt')
                    os.system('sudo halt')
            else:
                count = 0
                key1_pressed = False
                continue
        else:
            key1_pressed = False
            key2_pressed = False
            count = 0
            time.sleep(0.05)

        
