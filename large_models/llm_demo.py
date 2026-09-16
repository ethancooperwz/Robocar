#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
from config import *
from speech import speech

client = speech.OpenAIAPI(api_key, base_url)

# Additional parameters can be provided in the following way(更多参数采用以下方式进行输入)
# Streaming output(流式输出)
# params = {"model": 'qwen-max', 
          # "messages": [
            # {
                # "role": "user",
                # "content": '以科技改变生活写一段50字的中文文案'
            # },
          # ],
          # "stream": True}
# stream = client.llm_origin(params)
# for event in stream:
    # print(event.choices[0].delta.content)

# networked search(联网搜索)
# params = {"model": 'qwen-max', 
          # "messages": [
            # {
                # "role": "user",
                # "content": '深圳天气'
            # },
          # ],
          # "extra_body": {
          # "enable_search": True
          # }
        # }
# completion = client.llm_origin(params)
# print(completion.choices[0].message.content.strip())

print(client.llm('以科技改变生活写一段50字的中文文案', prompt='', model='qwen-max')) # Here, qwen-max is used as an example. You can replace it with another model name as needed(此处以qwen-max为例，可按需更换模型名称。模型列表)：https://help.aliyun.com/zh/model-studio/getting-started/models
