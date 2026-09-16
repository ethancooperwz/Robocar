#!/usr/bin/env python3
# encoding: utf-8
# @data:2023/03/11
# @author:aiden
# 无人驾驶车道线提取(extraction of lane markings for autonomous driving)
import os
import cv2
import math
import queue
import threading
import numpy as np
import sdk.common as common
from cv_bridge import CvBridge

bridge = CvBridge()

lab_data = common.get_yaml_data("/home/ubuntu/software/lab_tool/lab_config.yaml")

class LaneDetector(object):
    def __init__(self, color):
        # 车道线颜色(lane color)
        self.target_color = color
        # 车道线识别的区域(the recognized area of lane)
        if os.environ['DEPTH_CAMERA_TYPE'] == 'Dabai':
            self.rois = ((338, 360, 0, 320, 0.7), (292, 315, 0, 320, 0.2), (248, 270, 0, 320, 0.1))
        else:
            self.rois = ((450, 480, 0, 320, 0.7), (390, 480, 0, 320, 0.2), (330, 480, 0, 320, 0.1))
        self.weight_sum = 1.0

    def set_roi(self, roi):
        self.rois = roi

    @staticmethod
    def get_area_max_contour(contours, threshold=100):
        '''
        (retrieve the contour corresponding to the largest area)
        :param contours:
        :param threshold:
        :return:
        '''
        contour_area = zip(contours, tuple(map(lambda c: math.fabs(cv2.contourArea(c)), contours)))
        contour_area = tuple(filter(lambda c_a: c_a[1] > threshold, contour_area))
        if len(contour_area) > 0:
            max_c_a = max(contour_area, key=lambda c_a: c_a[1])
            return max_c_a
        return None
    
    def add_horizontal_line(self, image):
        #   |____  --->   |————   ---> ——
        h, w = image.shape[:2]
        roi_w_min = int(w/2)
        roi_w_max = w
        roi_h_min = 0
        roi_h_max = h
        roi = image[roi_h_min:roi_h_max, roi_w_min:roi_w_max]  # 截取右半边(capture the right half)
        flip_binary = cv2.flip(roi, 0)  # 上下翻转(flip vertically)
        max_y = cv2.minMaxLoc(flip_binary)[-1][1]  # 提取最上，最左数值为255的点坐标(extract coordinates of points with the highest and leftmost values of 255)

        return h - max_y

    def add_vertical_line_far(self, image):
        h, w = image.shape[:2]
        roi_w_min = int(w/8)
        roi_w_max = int(w/2)
        roi_h_min = 0
        roi_h_max = h
        roi = image[roi_h_min:roi_h_max, roi_w_min:roi_w_max]
        flip_binary = cv2.flip(roi, -1)  # 图像左右上下翻转(flip the image horizontally and vertically)
        #cv2.imshow('1', flip_binary)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(ret)
        # minVal：最小值(the minimum value)
        # maxVal：最大值(the maximal value)
        # minLoc：最小值的位置(the position of minimum value)
        # maxLoc：最大值的位置(the position of the maximal value)
        # 遍历的顺序，先行再列，行从左到右，列从上到下(the traversal order is row-major, iterating through rows from left to right and columns from top to bottom)
        (x_0, y_0) = cv2.minMaxLoc(flip_binary)[-1]  # 提取最上，最左数值为255的点坐标(extract coordinates of points with the highest and leftmost values of 255)
        y_center = y_0 + 55
        roi = flip_binary[y_center:, :]
        (x_1, y_1) = cv2.minMaxLoc(roi)[-1]
        down_p = (roi_w_max - x_1, roi_h_max - (y_1 + y_center))
        
        y_center = y_0 + 65
        roi = flip_binary[y_center:, :]
        (x_2, y_2) = cv2.minMaxLoc(roi)[-1]
        up_p = (roi_w_max - x_2, roi_h_max - (y_2 + y_center))

        up_point = (0, 0)
        down_point = (0, 0)
        if up_p[1] - down_p[1] != 0 and up_p[0] - down_p[0] != 0:
            up_point = (int(-down_p[1]/((up_p[1] - down_p[1])/(up_p[0] - down_p[0])) + down_p[0]), 0)
            down_point = (int((h - down_p[1])/((up_p[1] - down_p[1])/(up_p[0] - down_p[0])) + down_p[0]), h)

        return up_point, down_point

    def add_vertical_line_near(self, image):
        # ——|         |——        |
        #   |   --->  |     --->
        h, w = image.shape[:2]
        roi_w_min = 0
        roi_w_max = int(w/2)
        roi_h_min = int(h/2)
        roi_h_max = h
        roi = image[roi_h_min:roi_h_max, roi_w_min:roi_w_max]
        flip_binary = cv2.flip(roi, -1)  # 图像左右上下翻转(flip the image horizontally and vertically)
        #cv2.imshow('1', flip_binary)
        (x_0, y_0) = cv2.minMaxLoc(flip_binary)[-1]  # 提取最上，最左数值为255的点坐标(extract coordinates of points with the highest and leftmost values of 255)
        down_p = (roi_w_max - x_0, roi_h_max - y_0)

        (x_1, y_1) = cv2.minMaxLoc(roi)[-1]
        y_center = int((roi_h_max - roi_h_min - y_1 + y_0)/2)
        roi = flip_binary[y_center:, :] 
        (x, y) = cv2.minMaxLoc(roi)[-1]
        up_p = (roi_w_max - x, roi_h_max - (y + y_center))

        up_point = (0, 0)
        down_point = (0, 0)
        if up_p[1] - down_p[1] != 0 and up_p[0] - down_p[0] != 0:
            up_point = (int(-down_p[1]/((up_p[1] - down_p[1])/(up_p[0] - down_p[0])) + down_p[0]), 0)
            down_point = down_p

        return up_point, down_point, y_center

    def get_binary(self, image):
        # 通过lab空间识别颜色(recognize color through lab space)
        img_lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)  # rgb转lab(convert rgb to lab)
        img_blur = cv2.GaussianBlur(img_lab, (3, 3), 3)  # 高斯模糊去噪(Gaussian blur for noise reduction)
        mask = cv2.inRange(img_blur, tuple(lab_data['lab']['Stereo'][self.target_color]['min']), tuple(lab_data['lab']['Stereo'][self.target_color]['max']))  # 二值化(binarization)
        eroded = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  # 腐蚀(corrosion)
        dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  # 膨胀(dilation)

        return dilated

    def __call__(self, image, result_image):
        # 按比重提取线中心(extracting line centers based on weight)
        centroid_sum = 0
        h, w = image.shape[:2]
        max_center_x = -1
        center_x = []
        for roi in self.rois:
            blob = image[roi[0]:roi[1], roi[2]:roi[3]]  # 截取roi(crop roi)
            contours = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)[-2]  # 找轮廓(find contour)
            max_contour_area = self.get_area_max_contour(contours, 30)  # 获取最大面积对应轮廓(retrieve the contour with the largest area)
            if max_contour_area is not None:
                rect = cv2.minAreaRect(max_contour_area[0])  # 最小外接矩形(the minimum bounding rectangle)
                box = np.intp(cv2.boxPoints(rect))  # 四个角(four corners)
                for j in range(4):
                    box[j, 1] = box[j, 1] + roi[0]
                cv2.drawContours(result_image, [box], -1, (255, 255, 0), 2)  # 画出四个点组成的矩形(draw a rectangle formed by four points)

                # 获取矩形对角点(retrieve the diagonal points of the rectangle)
                pt1_x, pt1_y = box[0, 0], box[0, 1]
                pt3_x, pt3_y = box[2, 0], box[2, 1]
                # 线的中心点(the center point of line)
                line_center_x, line_center_y = (pt1_x + pt3_x) / 2, (pt1_y + pt3_y) / 2

                cv2.circle(result_image, (int(line_center_x), int(line_center_y)), 5, (0, 0, 255), -1)  # 画出中心点(draw center point)
                center_x.append(line_center_x)
            else:
                center_x.append(-1)
        for i in range(len(center_x)):
            if center_x[i] != -1:
                if center_x[i] > max_center_x:
                    max_center_x = center_x[i]
                centroid_sum += center_x[i] * self.rois[i][-1]
        if centroid_sum == 0:
            return result_image, None, max_center_x
        center_pos = centroid_sum / self.weight_sum  # 按比重计算中心点(calculate the centroid based on weight)
        angle = math.degrees(-math.atan((center_pos - (w / 2.0)) / (h / 2.0)))
        
        return result_image, angle, max_center_x

image_queue = queue.Queue(2)
def image_callback(ros_image):
    cv_image = bridge.imgmsg_to_cv2(ros_image, "bgr8")
    bgr_image = np.array(cv_image, dtype=np.uint8)
    if image_queue.full():
        # 如果队列已满，丢弃最旧的图像(if the queue is full, discard the oldest image)
        image_queue.get()
        # 将图像放入队列(put the image into the queue)
    image_queue.put(bgr_image)

def main():
    running = True
    while running:
        try:
            image = image_queue.get(block=True, timeout=1)
        except queue.Empty:
            if not running:
                break
            else:
                continue
        binary_image = lane_detect.get_binary(image)
        cv2.imshow('binary', binary_image)
        img = image.copy()
        y = lane_detect.add_horizontal_line(binary_image)
        roi = [(0, y), (640, y), (640, 0), (0, 0)]
        cv2.fillPoly(binary_image, [np.array(roi)], [0, 0, 0])  # 将上面填充为黑色，防干扰(fill the area above with black to prevent interference)
        min_x = cv2.minMaxLoc(binary_image)[-1][0]
        cv2.line(img, (min_x, y), (640, y), (255, 255, 255), 50)  # 画虚拟线来驱使转弯(draw dashed lines to guide the turn)
        result_image, angle, x = lane_detect(binary_image, image.copy()) 
        '''
        up, down = lane_detect.add_vertical_line_far(binary_image)
        #up, down, center = lane_detect.add_vertical_line_near(binary_image)
        cv2.line(img, up, down, (255, 255, 255), 10)
        '''
        cv2.imshow('image', img)
        key = cv2.waitKey(1)
        if key == ord('q') or key == 27:  # 按q或者esc退出(press Q or ESC to exit)
            break

    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    import rclpy
    from sensor_msgs.msg import Image
    rclpy.init()
    node = rclpy.create_node('lane_detect')
    lane_detect = LaneDetector('yellow')
    node.create_subscription(Image, '/depth_cam/rgb/image_raw', image_callback, 1)
    threading.Thread(target=main, daemon=True).start()
    rclpy.spin(node)




