#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
import cv2
from config import *
from speech import speech

client = speech.OpenAIAPI(llm_api_key, llm_base_url)

image = cv2.imread('./resources/pictures/hello_world.jpg')
print(client.vllm('Recognize text in images, do not answer anything else', image, prompt='', model='gpt-4o-mini'))
while True:
    try:
        cv2.imshow('image', image)
        key = cv2.waitKey(1)
        if key != -1:
            break
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
