#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
import cv2
import base64
from config import *
from speech import speech

client = speech.OpenAIAPI(api_key, base_url)

image = cv2.imread('./resources/pictures/test_image_understand.jpeg')

# _, buffer = cv2.imencode('.jpg', image)
# params = {"model": 'qwen-vl-max-latest',
          # "messages": [
            # {
                # "role": "user",
                # "content": [
                    # {
                        # "type": "text",
                        # "text": "图片里内容是什么?"
                    # },
                    # {
                        # "type": "image_url",
                        # "image_url": {
                            # "url": 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8'),
                            # "detail": "high"
                        # }
                    # }
                # ]
            # },
            # ],
          # "stream": True}
# stream = client.vllm_origin(params)
# for event in stream:
    # print(event.choices[0].delta.content)

# qwen-vl-max-latest is used here as an example. Feel free to substitute it with another model name based on your needs. Refer to the model list for available options. (此处以qwen-vl-max-latest例，可按需更换模型名称。模型列表)：https://help.aliyun.com/zh/model-studio/getting-started/models
print(client.vllm('图片里内容是什么?', image, prompt='', model='qwen-vl-max-latest'))
while True:
    try:
        cv2.imshow('image', image)
        key = cv2.waitKey(1)
        if key != -1:
            break
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
