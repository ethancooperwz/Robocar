#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/03/05
import os
import time
from config import *
from speech import awake
from speech import speech

wakeup_audio_path = './resources/audio/en/wakeup.wav'
start_audio_path = './resources/audio/en/start_audio.wav'
no_voice_audio_path = './resources/audio/en/no_voice.wav'

port = '/dev/ttyUSB0'
kws = awake.WonderEchoPro(port)
# kws = awake.CircleMic(port)

asr = speech.RealTimeOpenAIASR()
asr.update_session(model='whisper-1')
tts = speech.RealTimeOpenAITTS()
client = speech.OpenAIAPI(llm_api_key, llm_base_url)

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
                    response = client.llm(asr_result, model='gpt-4o-mini')
                    print('llm response:', response)
                    tts.tts(response)
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
