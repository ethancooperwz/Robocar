#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/03/5
import os
import time
import action_demo
from config import *
from speech import awake
from speech import speech

PROMPT = '''
# 角色
你是一款智能陪伴机器人，专注机器人动作规划，解析人类指令并以幽默方式描述即将展开的行动序列，为交互增添无限趣味。
## 技能
### 指令解析与创意演绎
- **智能解码**：瞬间领悟用户指令的核心意图。
- **灵动编排**：依据解析成果，精心构建一系列连贯且富有逻辑性的动作指令序列。
- **妙语生花**：为每个动作序列编织一句精炼（5至20字）、风趣且变化无穷的反馈信息，让交流过程妙趣横生。
## 技术规格
- **严格遵循JSON格式，在输出前要去掉开头的```json和结尾的```，以`{`开头，以`}`结尾，你只需要回答一个列表即可，不要回答任何中文。
- **结构要求**：
  - `"action"`键下承载一个按执行顺序排列的函数名称字符串数组，当找不到对应动作函数时action输出[]。
  - `"response"`键则配以精心构思的简短回复，完美贴合上述字数与风格要求。
- **特殊处理**：对于特定函数`track`，其参数需精确包裹于双引号中。
## 所有动作函数
- 前进一步：forward()
- 后退一步：back()
- 向左转动一步：turn_left()
- 向右转动一步：turn_right()
- 追踪不同颜色的物体：track('red')
## 示例
### 任务示例：先前进两步，然后向左转，最后再后退一步。
### 期望回应：{'action':['forward()', 'forward()', 'turn_left()', 'back()'], 'response':'收到，马上执行'}
### 任务示例：先活动活动筋骨，然后跟踪红色的球。
### 期望回应：{'action':['twist()', “track('red')”], 'response':'这可难不到我'}
'''
print(PROMPT)

wakeup_audio_path = './resources/audio/wakeup.wav'
start_audio_path = './resources/audio/start_audio.wav'
no_voice_audio_path = './resources/audio/no_voice.wav'
error_audio_path = './resources/audio/error.wav'

port = '/dev/ttyUSB0'
kws = awake.WonderEchoPro(port)
# kws = awake.CircleMic(port)

asr = speech.RealTimeASR()
tts = speech.RealTimeTTS()
client = speech.OpenAIAPI(api_key, base_url)

try:  # If a fan is present, it's recommended to turn it off before detection to reduce interference(如果有风扇，检测前推荐关掉减少干扰)
    os.system('pinctrl FAN_PWM op dh')
except:
    pass

speech.set_volume(80)
speech.play_audio(start_audio_path)
print('start...')

def main():
    kws.start()
    while True:
        try:
            if kws.wakeup(): # Wake word detected (检测到唤醒词)
                speech.play_audio(wakeup_audio_path)  # Play wake-up audio(唤醒播放)
                asr_result = asr.asr() # Start voice recognition(开启录音识别)
                print('asr_result:', asr_result)
                if asr_result:
                    # Send the input question to the agent, and process the response to extract actions and reply(输入问题给智能体，对返回的回答进行处理，提取出对应的行为和回答)
                    action_list, response = None, None
                    result = client.llm(asr_result, prompt=PROMPT)
                    print('llm_result:', result)
                    if 'action' in result: # If an action is included in the response, extract and process it(如果有对应的行为返回那么就提取处理)
                        result = eval(result[result.find('{'):result.find('}')+1])
                        if 'action' in result:
                            action_list = result['action']
                        if 'response' in result:
                            response = result['response']
                    else: # No associated action, only reply(没有对应的行为，只回答)
                        response = result
                    print('agent_result:', action_list, response)
                    tts.tts(response)
                    if response is not None:
                        if action_list is not None:
                            for a in action_list:
                                eval(f'action_demo.{a}')
                    else:
                        speech.play_audio(error_audio_path)
                else:
                    speech.play_audio(no_voice_audio_path)
            time.sleep(0.02)
        except KeyboardInterrupt:
            kws.exit() 
            try:
                os.system('pinctrl FAN_PWM a0')
            except:
                pass
            break
        except BaseException as e:
            print(e)

if __name__ == '__main__':
    main()
