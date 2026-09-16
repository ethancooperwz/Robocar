#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
from config import *
from speech import speech

client = speech.OpenAIAPI(llm_api_key, llm_base_url)

# streaming
# params = {"model": 'gpt-4o-mini', 
          # "messages": [
            # {
                # "role": "user",
                # "content": 'Write a 50-word article about changing life with technology'
            # },
          # ],
          # "stream": True}
# stream = client.llm_origin(params)
# for event in stream:
    # print(event.choices[0].delta.content)

# web search
# params = {"model": 'gpt-4o-search-preview', 
          # "web_search_options": {}, 
          # "messages": [
            # {
                # "role": "user",
                # "content": 'What was a positive news story from today?'
            # },
          # ],
          # }
# completion  = client.llm_origin(params)
# print(completion.choices[0].message.content)

print(client.llm('Write a 50-word article about changing life with technology', prompt='', model='gpt-4o-mini')) # https://platform.openai.com/docs/models
