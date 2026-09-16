#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/03/05
import os
import time
from config import *
from speech import awake
from speech import speech

wakeup_audio_path = './resources/audio/wakeup.wav'
start_audio_path = './resources/audio/start_audio.wav'
no_voice_audio_path = './resources/audio/no_voice.wav'

port = '/dev/ttyUSB0'
kws = awake.WonderEchoPro(port)
# kws = awake.CircleMic(port)

asr = speech.RealTimeASR()
tts = speech.RealTimeTTS()
client = speech.OpenAIAPI(api_key, base_url)

try:
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
                    # Send the recognition result to the agent for a response(将识别结果传给智能体让他来回答)
                    params = {"model": 'qwen-max', 
                      "messages": [
                        {
                            "role": "user",
                            "content": asr_result
                        },
                      ],
                      "extra_body": {
                      "enable_search": True
                      }
                    }
                    response = client.llm_origin(params).choices[0].message.content.strip()
                    print('llm response:', response)
                    tts.tts(response)
                else:
                    speech.play_audio(no_voice_audio_path)
            else:
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
