#!/usr/bin/env python3
# encoding: utf-8
# Date:2022/10/22
# Author:aiden
import os
import cv2
import sys
import time
import rclpy
import queue
import threading
import numpy as np
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from PyQt5.QtCore import pyqtSignal, QSettings, QTimer
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QShortcut, QFileDialog, QMessageBox, QFileDialog, QDesktopWidget
if __name__ == '__main__':
    import ui
else:
    from collect_picture import ui

class CameraNode(Node):  
    def __init__(self, name):
        rclpy.init()
        super().__init__(name)
        self.subscription = None
        self.bridge = CvBridge()
        self.image_queue = queue.Queue(maxsize=2)

    def create_sub(self, topic):
        self.subscription = self.create_subscription(Image, topic, self.image_callback, 1)

    def destroy_sub(self):
        if self.subscription is not None:
            self.destroy_subscription(self.subscription)

    def image_callback(self, ros_image):
        cv_image = self.bridge.imgmsg_to_cv2(ros_image, "rgb8")
        rgb_image = np.array(cv_image, dtype=np.uint8)
        if self.image_queue.full():
            # 如果队列已满，丢弃最旧的图像
            self.image_queue.get()
        # 将图像放入队列
        self.image_queue.put(rgb_image)

    def shutdown(self):
        rclpy.shutdown()

class MainWindow(QWidget, ui.Ui_Form):
    clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.camera_node = None
        self.set_window_position()
        self.image_prefix = 'image'
        self.number = 0
        self.save_image_name = None
        self.image_number = 0
        self.save_path = ''
        self.picture = None
        self.pictures_list = []
        self.exist_number = 0
        self.display_size = (640, 480)
        self.camera_type = os.environ['DEPTH_CAMERA_TYPE']
        self.pushButton_save.pressed.connect(lambda: self.button_clicked('save'))
        self.pushButton_delete.pressed.connect(lambda: self.button_clicked('delete'))
        self.pushButton_select.pressed.connect(lambda: self.button_clicked('select'))
        self.pushButton_exit.pressed.connect(lambda: self.button_clicked('exit'))

        self.shortcut_save = QShortcut(QKeySequence('space'), self)
        self.shortcut_save.activated.connect(self.pushButton_save.click)
        self.shortcut_delete = QShortcut(QKeySequence('d'), self)
        self.shortcut_delete.activated.connect(self.pushButton_delete.click)
        self.shortcut_quit = QShortcut(QKeySequence('q'), self)
        self.shortcut_quit.activated.connect(self.pushButton_exit.click)
        
        config_path = os.path.split(os.path.realpath(__file__))[0]
        self.setting = QSettings(os.path.join(config_path, 'config.ini'), QSettings.IniFormat)
        
        self.lineEdit_width.setText(self.setting.value('width'))
        self.lineEdit_height.setText(self.setting.value('height'))
        self.lineEdit_path.setText(self.setting.value('save_path'))
        self.save_size = (self.setting.value('width'), self.setting.value('height'))
        
        self.get_exist_image()

        self.radioButton_zn.toggled.connect(lambda: self.language(self.radioButton_zn))
        self.radioButton_en.toggled.connect(lambda: self.language(self.radioButton_en))        
        
        try:
            if os.environ['ASR_LANGUAGE'] == 'Chinese':
                self.radioButton_zn.setChecked(True)
            else:
                self.radioButton_en.setChecked(True)
        except:
            self.radioButton_zn.setChecked(True)

        self.camera = 'depth_cam'
        threading.Thread(target=self.ros_node, daemon=True).start()
        time.sleep(1)
        self._timer = QTimer()
        self._timer.timeout.connect(self.show_image)
        self._timer.start(30)
        if self.camera_type == 'usb_cam':
            self.change_camera()
        self.pushButton_camera_change.setEnabled(False)

    def ros_node(self):
        self.camera_node = CameraNode('collect_picture_node')
        self.camera_node.create_sub('/%s/rgb/image_raw'%self.camera) 
        rclpy.spin(self.camera_node)
        self.camera_node.destroy_node()

    def set_window_position(self):
        # 窗口居中
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def change_camera(self):
        self.camera_node.destroy_sub()
        if self.pushButton_camera_change.text() == '深度相机' or self.pushButton_camera_change.text() == 'Stereo':
            self.current_camera = 'Mono'
            if self.pushButton_camera_change.text() == '深度相机':
                self.pushButton_camera_change.setText('单目相机')
            else:
                self.pushButton_camera_change.setText('Mono')
            self.camera = 'depth_cam'
            self.camera_node.create_sub('/%s/rgb/image_raw'%self.camera)
        else:
            self.current_camera = 'Stereo'
            if self.pushButton_camera_change.text() == '单目相机':
                self.pushButton_camera_change.setText('深度相机')
            else:
                self.pushButton_camera_change.setText('Stereo')
            self.camera = 'depth_cam'
            self.camera_node.create_sub('/%s/rgb/image_raw'%self.camera)

    def language(self, name):
        if name.text() == "中文":
            self.label_camera.setText("摄像头画面")
            self.label_resolution.setText("图片分辨率")
            self.label_width.setText("宽")
            self.label_height.setText("高")
            self.label_save_path.setText("保存路径")
            self.pushButton_save.setText("保存\n(space)")
            self.pushButton_delete.setText("删除\n(d)")
            self.pushButton_select.setText("选择")
            self.pushButton_exit.setText("退出")
            if self.pushButton_camera_change.text() == 'Mono':
                self.pushButton_camera_change.setText('单目相机')
            if self.pushButton_camera_change.text() == 'Stereo':
                self.pushButton_camera_change.setText('深度相机')
        elif name.text() == "English":
            self.label_camera.setText("Camera View")
            self.label_resolution.setText("Resolution")
            self.label_width.setText("Width")
            self.label_height.setText("Height")
            self.label_save_path.setText("Save path")
            self.pushButton_save.setText("Save\n(space)")
            self.pushButton_delete.setText("Delete\n(d)")
            self.pushButton_select.setText("Select")
            self.pushButton_exit.setText("Quit")
            if self.pushButton_camera_change.text() == '单目相机':
                self.pushButton_camera_change.setText('Mono')
            if self.pushButton_camera_change.text() == '深度相机':
                self.pushButton_camera_change.setText('Stereo')

    # 弹窗提示函数
    def message_from(self, string):
        try:
            QMessageBox.about(self, '', string)
        except:
            pass
    
    # 弹窗提示函数
    def message_delect(self, string):
        messageBox = QMessageBox()
        messageBox.setWindowTitle(' ')
        messageBox.setText(string)
        messageBox.addButton(QPushButton('OK'), QMessageBox.YesRole)
        messageBox.addButton(QPushButton('Cancel'), QMessageBox.NoRole)
        return messageBox.exec_()

    # 窗口退出
    def closeEvent(self, e):    
        result = QMessageBox.question(self,
                                    "Prompt box",
                                    "quit?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if result == QMessageBox.Yes:
            # 退出前先把节点退出
            self.camera_node.shutdown()
            QWidget.closeEvent(self, e)
            sys.exit()
        else:
            e.ignore()

    def get_exist_image(self):
        self.save_path = self.lineEdit_path.text()
        jpg_path = os.path.join(self.save_path, 'JPEGImages')
        if os.path.exists(self.save_path):
            if os.path.exists(jpg_path):
                self.pictures_list = []
                self.image_number = 0
                for i in os.listdir(os.path.join(self.save_path, 'JPEGImages')):
                    if self.image_prefix == i.split('_' + i.split('_')[-1])[0] and i[-3:] == 'jpg':
                        self.pictures_list.append(i)
                self.exist_number = len(self.pictures_list)

    def button_clicked(self, name):
        if name == 'save':
            width = self.lineEdit_width.text()
            height = self.lineEdit_height.text()
            if width.isdigit() and height.isdigit():
                width = abs(int(width))
                height = abs(int(height))
                self.save_size = (width, height)
                self.setting.setValue('width', width)
                self.setting.setValue('height', height)
                self.save_path = self.lineEdit_path.text()
                if self.save_path != '' and self.picture is not None:
                    jpg_path = os.path.join(self.save_path, 'JPEGImages')
                    ann_path = os.path.join(self.save_path, 'Annotations')
                    image_path = os.path.join(self.save_path, 'ImageSets')

                    if not os.path.exists(self.save_path):
                        os.makedirs(self.save_path)
                    
                    if not os.path.exists(jpg_path):
                        os.makedirs(jpg_path)
                    if not os.path.exists(ann_path):
                        os.makedirs(ann_path)
                    if not os.path.exists(image_path):
                        os.makedirs(image_path)
                    
                    self.setting.setValue('save_path', self.save_path)
                    self.image_number += 1
                    self.number = 0
                    image_resize = cv2.resize(self.picture, self.save_size, interpolation=cv2.INTER_NEAREST)

                    while True:
                        self.number += 1
                        save_name = '{}_{}.jpg'.format(self.image_prefix, str(self.number))
                        if save_name not in self.pictures_list:
                            self.pictures_list.append(save_name)
                            self.save_image_name = save_name
                            cv2.imwrite(os.path.join(self.save_path, 'JPEGImages', save_name), cv2.cvtColor(image_resize, cv2.COLOR_RGB2BGR))
                            break
                elif self.save_path == '':
                    self.message_from('choose path first')
                else:
                    self.message_from('no picture')
            else:
                self.message_from('wrong resolution')
        elif name == 'delete':
            if self.image_number > 0:
                delete_file = self.pictures_list[-1]
                os.system('sudo rm ' + os.path.join(self.save_path, 'JPEGImages', delete_file))
                self.image_number -= 1
                del self.pictures_list[-1]
                self.message_from('delete ' + delete_file)
            else:
                self.message_from('no picture')
        elif name =='select':
                file_path = QFileDialog.getExistingDirectory(None, "select directory", '')
                self.lineEdit_path.setText(file_path)
                self.get_exist_image()
        elif name == 'exit':
            self.camera_node.shutdown()
            sys.exit(0)

    # 摄像头画面界面显示
    def show_image(self):
        try:
            image = self.camera_node.image_queue.get(block=True)
            image_resize = cv2.resize(image, self.display_size)
            self.picture = image_resize.copy()
            cv2.putText(image_resize, 'save number: ' + str(self.image_number), (19, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (32, 32, 32), 4, cv2.LINE_AA)
            cv2.putText(image_resize, 'save number: ' + str(self.image_number), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (240, 240, 240), 1, cv2.LINE_AA)
            cv2.putText(image_resize, 'existing: ' + str(self.exist_number + self.image_number), (19, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (32, 32, 32), 4, cv2.LINE_AA)
            cv2.putText(image_resize, 'existing: ' + str(self.exist_number + self.image_number), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (240, 240, 240), 1, cv2.LINE_AA)
            
            frame_rgb = image_resize
            qimage = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
            qpix = QPixmap.fromImage(qimage)           
            self.label_display.setPixmap(qpix)
        except BaseException as e:
            print(e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myshow = MainWindow()
    myshow.show()
    sys.exit(app.exec_())
