#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
import cv2
from config import *
from speech import speech

PROMPT = '''
你作为图像专家，你的能力是将用户发来的图片进行目标检测精准定位，并按「输出格式」进行最后结果的输出。。
## 1.理解图片
我会给你一张图片，请识别图片中一共有哪些物体。
## 2.物体定位 - position
检测到每一个物体的位置，根据你的知识和记忆，看清这个物体的样子，识别每个物体的具体名称。**请输出全部的物体不要遗漏**
## 输出格式（请仅输出以下内容，不要说任何多余的话）
{
 "object1": [name, xmin, ymin, xmax, ymax],
 "object2": [name, xmin, ymin, xmax, ymax],
}
'''

client = speech.OpenAIAPI(api_key, base_url)
image = cv2.imread('./resources/pictures/detect.jpg')
vllm_result = client.vllm('', image, prompt=PROMPT, model='qwen-vl-max-latest')
vllm_result = eval(vllm_result[vllm_result.find('{'):vllm_result.find('}') + 1])
print(vllm_result)
for i in vllm_result:
    position = vllm_result[i]
    p1 = [position[1], position[2]]
    p2 = [position[3], position[4]]
    cv2.rectangle(image, p1, p2, (0, 255, 0), 2, 1)
while True:
    try:
        cv2.imshow('image', image)
        key = cv2.waitKey(1)
        if key != -1:
            break
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break

