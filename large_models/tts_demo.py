#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
import os
from config import *
from speech import speech

speech.set_volume(80)
tts = speech.RealTimeTTS()
# tts = speech.RealTimeTTS(samplerate=16000, channels=1, device=0)

model = 'sambert-zhinan-v1'
# save_path = ''
# tts.tts('准备就绪', model=model, save_path=os.path.join(save_path, 'start_audio.wav'), play=True)
# tts.tts('我在', model=model, save_path=os.path.join(save_path, 'wakeup.wav'), play=True)
# tts.tts('我还在学习中', model=model, save_path=os.path.join(save_path, 'error.wav', play=True)
# tts.tts('小幻没有听清楚，请再说一遍', model=model, save_path=os.path.join(save_path, 'no_voice.wav', play=True)
# tts.tts('我记住了', model=model, save_path=os.path.join(save_path, 'record_finish.wav', play=True)
# tts.tts('开始追踪', model=model, save_path=os.path.join(save_path, 'start_track.wav', play=True)
# tts.tts('获取目标失败', model=model, save_path=os.path.join(save_path, 'track_fail.wav', play=True)
tts.tts('你好，请问有什么可以帮到您')
# 此处以sambert-zhiming-v1例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
# tts.tts('你好，请问有什么可以帮到您', model='cosyvoice-v1', voice='longcheng', block=True)
# tts.tts('你好，请问有什么可以帮到您', model='cosyvoice-v2', voice='longcheng_v2', block=True)
# tts.tts('你好，请问有什么可以帮到您', model='sambert-zhiming-v1', save_path='./resources/audio/tts_audio.wav', play=False)

