import os
import dashscope
from openai import OpenAI

###Chinese
api_key = ''
base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
dashscope.api_key = api_key

###English
llm_api_key = '' 
llm_base_url = 'https://api.openai.com/v1'
os.environ["OPENAI_API_KEY"] = llm_api_key
vllm_api_key = ''
vllm_base_url = 'https://openrouter.ai/api/v1'
