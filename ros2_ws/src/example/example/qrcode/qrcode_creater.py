#!/usr/bin/env python3
# encoding: utf-8
import os
import cv2
import qrcode
import numpy as np

def create_qrcode(data, file_name):
    '''
    version：值为1~40的整数，控制二维码的大小（最小值是1，是个12×12的矩阵）。(an integer value ranging from 1 to 40, controlling the size of the QR code (minimum value is 1, resulting in a 12x12 matrix))
             如果想让程序自动确定，将值设置为 None 并使用 fit 参数即可。(if you want the program to automatically determine, set the value to None and use the fit parameter)
    error_correction：控制二维码的错误纠正功能。可取值下列4个常量。(control the error correction capability of the QR code. It can take one of the following four constants)
    　　ERROR_CORRECT_L：大约7%或更少的错误能被纠正。(approximately 7% or fewer errors can be corrected)
    　　ERROR_CORRECT_M（默认）：大约15%或更少的错误能被纠正。(approximately 15% or fewer errors can be corrected)
    　　ROR_CORRECT_H：大约30%或更少的错误能被纠正。(approximately 30% or fewer errors can be corrected)
    box_size：控制二维码中每个小格子包含的像素数。(control the number of pixels contained in each small square of the QR code)
    border：控制边框（二维码与图片边界的距离）包含的格子数（默认为4，是相关标准规定的最小值）(control the number of squares contained in the border (the distance between the QR code and the image boundary). The default is 4, which is the minimum value according to relevant standards)
    '''
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,
        border=4)
    # 添加数据(add data)
    qr.add_data(data)
    # 填充数据(fill data)
    qr.make(fit=True)
    # 生成图片(generate image)
    img = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255))
    opencv_img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    while True:
        cv2.imshow('img', opencv_img)
        k = cv2.waitKey(1)
        if k != -1:
            break
    cv2.imwrite(file_name, opencv_img)
    print('save', data, file_name)

if __name__ == '__main__':
    file_path = os.getcwd()
    out_img = file_path + '/myQRcode.jpg'
    qrcode_text = input("Please enter：")
    create_qrcode(qrcode_text, out_img)
