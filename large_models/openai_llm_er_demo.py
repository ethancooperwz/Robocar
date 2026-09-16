#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
from config import *
from speech import speech

client = speech.OpenAIAPI(llm_api_key, llm_base_url)

messages = [{"role": "user", "content": 'So sad'}]
assistant_output = client.llm_multi_turn(messages, model='gpt-4o-mini')
print(assistant_output)

messages.append({"role": "assistant", "content": assistant_output})

messages.append({"role": "user", "content": 'Ha ha'})
assistant_output = client.llm_multi_turn(messages, model='gpt-4o-mini')
print(assistant_output)
