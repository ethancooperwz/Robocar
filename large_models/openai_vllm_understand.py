#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
import cv2
import base64
from config import *
from speech import speech

client = speech.OpenAIAPI(llm_api_key, llm_base_url)

image = cv2.imread('./resources/pictures/test_image_understand.jpeg')

# _, buffer = cv2.imencode('.jpg', image)
# params = {"model": 'gpt-4o-mini',
          # "messages": [
            # {
                # "role": "user",
                # "content": [
                    # {
                        # "type": "text",
                        # "text": "Describe the image"
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

print(client.vllm('Describe the image', image, prompt='', model='gpt-4o-mini'))
while True:
    try:
        cv2.imshow('image', image)
        key = cv2.waitKey(1)
        if key != -1:
            break
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
