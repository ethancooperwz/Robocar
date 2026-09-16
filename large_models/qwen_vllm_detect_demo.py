#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
import cv2
from config import *
from speech import speech

PROMPT = '''
As an image expert, your ability is to accurately locate the target in the pictures sent by users and output the final results according to the "output format".
**1. Understand the picture
I will give you a picture, please identify the total number of objects in the picture.
**2. Object positioning - position
Detect the position of each object, based on your knowledge and memory, see the appearance of the object, and identify the specific name of each object. Please output all objects without missing any
**output format (please only output the following content, do not say any extra words)
{
    "object1": [name1, xmin, ymin, xmax, ymax],
    "object2": [name2, xmin, ymin, xmax, ymax],
}

**Example
Output:
{
    "object1": ["person", 100, 290, 466, 670],
    "object2": ["car", 201, 640, 350, 800],
}
'''

client = speech.OpenAIAPI(vllm_api_key, vllm_base_url)
image = cv2.imread('./resources/pictures/detect.jpg')
vllm_result = client.vllm('', image, prompt=PROMPT, model='qwen/qwen2.5-vl-72b-instruct:free')
print(vllm_result)
vllm_result = eval(vllm_result[vllm_result.find('{'):vllm_result.find('}') + 1])
h, w = image.shape[:2]
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
