#!/usr/bin/env python3
import os
import sys
import time
import logging
import netifaces
import importlib
import threading
import subprocess
import socketserver
import Jetson.GPIO as GPIO
from find_device import get_cpu_serial_number

os.system('sudo busybox devmem 0x0243d010 w 0x005')

led_pin = 24 
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)

path = os.path.split(os.path.realpath(__file__))[0]
log_file_path = "%s/wifi.log"%path
if not os.path.exists(log_file_path):
    os.system('touch %s'%log_file_path)
config_file_name = "wifi_conf.py"
internal_config_file_dir_path = "/etc/wifi"
external_config_file_dir_path = path
internal_config_file_path = os.path.join(internal_config_file_dir_path, config_file_name)
external_config_file_path = os.path.join(external_config_file_dir_path, config_file_name)
led_on_time = 100
led_off_time = 100

logger = logging.getLogger("WiFi tool")
logger.setLevel(logging.DEBUG)
log_handler = logging.FileHandler(log_file_path)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

def update_globals(module):
    if module in sys.modules:
        mdl = importlib.reload(sys.modules[module])
    else:
        mdl = importlib.import_module(module)
    if "__all" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    globals().update({k: getattr(mdl, k) for k in names})

def led_thread():
    global led_on_time
    global led_off_time
    
    local_led_on_time = 0
    local_led_off_time = 0

    count = 0
    cycle_time = 0
    while True:
        if local_led_on_time != led_on_time or local_led_off_time != led_off_time:
            local_led_on_time = led_on_time
            local_led_off_time = led_off_time
            cycle_time = local_led_on_time + local_led_off_time
            count = 0
        if count < local_led_on_time:
            GPIO.output(led_pin, 0)
            count += 1
        elif count < cycle_time:
            GPIO.output(led_pin, 1)
            count += 1
        else:
            count = 0

        time.sleep(0.01)

if __name__ == "__main__":
    ap_prefix = 'HW-'
    sn = get_cpu_serial_number()   #get cpu serial number
    WIFI_MODE = 1  #1 means AP mode, 2 means Client Mode, 3 means AP mode with eth0 internet share '
    WIFI_AP_SSID = ''.join([ap_prefix, sn[0:8]])
    WIFI_STA_SSID = "ssid"
    WIFI_AP_PASSWORD = "hiwonder"
    WIFI_STA_PASSWORD = "12345678"
    WIFI_AP_GATEWAY = "192.168.149.1"
    WIFI_CHANNEL = 36
    WIFI_FREQ_BAND = 'a' #5G
    WIFI_TIMEOUT = 15
    WIFI_LED = True
    ip = WIFI_AP_GATEWAY

    ### read config file
    if os.path.exists(config_file_name):
        update_globals(os.path.splitext(config_file_name)[0])
    if os.path.exists(internal_config_file_path):
        sys.path.insert(0, internal_config_file_dir_path)
        update_globals(os.path.splitext(config_file_name)[0])
    if os.path.exists(external_config_file_path):
        sys.path.insert(1, external_config_file_dir_path)
        update_globals(os.path.splitext(config_file_name)[0])
   
    def get_connect():
        try:
            result = subprocess.run(['nmcli', '-t', 'con', 'show', '--active'], stdout=subprocess.PIPE)
            active_conns = result.stdout.decode().split('\n')
            for conn in active_conns:
                if conn:
                    conn_details = conn.split(':')
                    if 'wireless' in conn_details[2]:
                        wifi = conn_details[0]
                        return wifi
        except:
            pass

    def disconnect():
        try:
            wifi = get_connect()
            if wifi:
                # 断开连接
                os.system('nmcli connection down %s'%wifi)
        except:
            pass

    def is_connected_to_normal_wifi(ap_ssid_prefix="HW-"):
        try:
            cmd = "nmcli -t -f ACTIVE,SSID dev wifi | grep '^yes' | cut -d: -f2"
            ssid = subprocess.check_output(cmd, shell=True).decode().strip()
            if ssid and not ssid.startswith(ap_ssid_prefix):
                return True, ssid
        except:
            pass
        return False, ""

    def wait_nm_autoconnect(timeout=30):
        print("waiting NetworkManager autoconnect...")
        for i in range(timeout):
            ok, ssid = is_connected_to_normal_wifi()
            if ok:
               print("autoconnected:", ssid)
               logger.info("autoconnected: " + ssid)
               return True
            time.sleep(1)
        return False 

    def WIFI_MGR():
        global WIFI_AP_SSID
        global WIFI_AP_PASSWORD
        global led_on_time
        global led_off_time

        # 先等系统自动连已保存 WiFi
        led_on_time = 5
        led_off_time = 5

        if wait_nm_autoconnect(30):
            led_on_time = 100
            led_off_time = 0
            return -1

        # 自动连接失败，开 AP
        print("autoconnect failed, create AP")
        logger.error("autoconnect failed, create AP")

        led_on_time = 50
        led_off_time = 50

        if type(WIFI_AP_PASSWORD) != str:
            WIFI_AP_PASSWORD = "hiwonder"
        if len(WIFI_AP_PASSWORD) < 8:
            WIFI_AP_PASSWORD = "hiwonder"
        if type(WIFI_AP_SSID) != str:
            WIFI_AP_SSID = ''.join([ap_prefix, sn[0:8]])

        # 只删除同名 AP，不要清空全部网络
        os.system('nmcli connection down "%s" >/dev/null 2>&1' % WIFI_AP_SSID)
        os.system('nmcli connection delete "%s" >/dev/null 2>&1' % WIFI_AP_SSID)
 
        os.system('nmcli con add type wifi ifname wlan0 con-name "{0}" autoconnect no ssid "{0}"'.format(WIFI_AP_SSID))
        os.system('nmcli con modify "{0}" 802-11-wireless.mode ap ipv4.method shared ipv4.addresses {1}/24'.format(WIFI_AP_SSID, WIFI_AP_GATEWAY))
        os.system('nmcli con modify "{0}" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "{1}"'.format(WIFI_AP_SSID, WIFI_AP_PASSWORD))
        os.system('nmcli con up "{0}"'.format(WIFI_AP_SSID))

        timeout = 0
        while True:
           timeout += 1
           wifi = get_connect()
           if wifi == WIFI_AP_SSID:
               print("Create AP:", WIFI_AP_SSID)
               logger.info(WIFI_AP_SSID)
               return -1
           if timeout == 20:
               os.system('systemctl restart NetworkManager')
           if timeout > 20:
               return 0
           time.sleep(1)
    if WIFI_LED == True:
        threading.Thread(target = led_thread).start()
    while True:
        try:
            ret = WIFI_MGR()
        except BaseException as e:
            print('error', e)
        if ret == -1:
            sys.exit(0)
        WIFI_MODE = 1  
