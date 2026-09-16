#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
from config import *
from speech import speech

client = speech.OpenAIAPI(api_key, base_url)

messages = [{"role": "user", "content": '好烦'}]
assistant_output = client.llm_multi_turn(messages, model='qwen-plus')
print(assistant_output)

messages.append({"role": "assistant", "content": assistant_output})

messages.append({"role": "user", "content": '哈哈'})
assistant_output = client.llm_multi_turn(messages, model='qwen-max')
print(assistant_output)
