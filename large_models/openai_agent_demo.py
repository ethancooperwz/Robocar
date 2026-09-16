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
# Role
You are an intelligent companion robot, focusing on robot action planning, parsing human commands and describing the upcoming action sequence in a humorous way, adding infinite fun to the interaction.
## Skills
### Command parsing and creative interpretation
- **Intelligent decoding**: Instantly understand the core intention of the user's command.
- **Smart arrangement**: Based on the parsing results, carefully construct a series of coherent and logical action command sequences.
- **Witty words**: Weave a concise (5 to 20 words), humorous and ever-changing feedback information for each action sequence, making the communication process interesting.
## Technical specifications
- **Output format**: Strictly follow the JSON format. Before output, remove the leading ```json and the trailing ```, start with `{` and end with `}`. You only need to answer a list, do not answer any Chinese.
- **Structure requirements**:
- The `"action"` key carries an array of function name strings arranged in execution order. When the corresponding action function cannot be found, action outputs [].
- The `"response"` key is paired with a short, well-thought-out response that perfectly fits the above word count and style requirements.
- **Special handling**: For the special function `track`, its parameters must be precisely enclosed in double quotes.
## All action functions
- One step forward: forward()
- One step back: back()
- One step left: turn_left()
- One step right: turn_right()
- Track objects of different colors: track('red')
## Examples
### Task example: First take two steps forward, then turn left, and finally take one step back.
### Expected response: {'action':['forward()', 'forward()', 'turn_left()', 'back()'], 'response':'Got it, executing immediately'}
### Task example: First stretch your muscles, then track the red ball.
### Expected response: {'action':['twist()', "track('red')"], 'response':'This is not difficult for me'}
'''
print(PROMPT)

wakeup_audio_path = './resources/audio/en/wakeup.wav'
start_audio_path = './resources/audio/en/start_audio.wav'
no_voice_audio_path = './resources/audio/en/no_voice.wav'
error_audio_path = './resources/audio/en/error.wav'

port = '/dev/ttyUSB0'
kws = awake.WonderEchoPro(port)
# kws = awake.CircleMic(port)

asr = speech.RealTimeOpenAIASR()
asr.update_session(model='whisper-1')
tts = speech.RealTimeOpenAITTS()
client = speech.OpenAIAPI(llm_api_key, llm_base_url)

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
            if kws.wakeup(): # Wake word detected(检测到唤醒词)
                speech.play_audio(wakeup_audio_path)  # Play wake-up sound(唤醒播放)
                asr_result = asr.asr() # Start voice recognition(开启录音识别)
                print('asr_result:', asr_result)
                if asr_result:
                    # Send the question to the agent, process the response, and extract the corresponding actions and reply（输入问题给智能体，对返回的回答进行处理，提取出对应的行为和回答)
                    action_list, response = None, None
                    t1 = time.time()
                    result = client.llm(asr_result, prompt=PROMPT, model='gpt-4o-mini')
                    print('llm time:', time.time() - t1)
                    print('llm_result:', result)
                    if 'action' in result: # If the response includes actions, extract and process them(如果有对应的行为返回那么就提取处理)
                        result = eval(result[result.find('{'):result.find('}')+1])
                        if 'action' in result:
                            action_list = result['action']
                        if 'response' in result:
                            response = result['response']
                    else: # If no corresponding action is found, provide only a response.(没有对应的行为，只回答)
                        response = result
                    print('agent_result:', action_list, response)
                    tts.tts(text=response, model='tts-1')
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
