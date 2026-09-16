#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
import cv2
from config import *
from speech import speech

client = speech.OpenAIAPI(api_key, base_url)

image = cv2.imread('./resources/pictures/ocr.jpeg')
print(client.vllm('识别图中的文字', image, prompt='', model='qwen-vl-max-latest'))
while True:
    try:
        cv2.imshow('image', image)
        key = cv2.waitKey(1)
        if key != -1:
            break
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
