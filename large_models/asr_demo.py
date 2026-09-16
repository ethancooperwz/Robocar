#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/03/05
from config import *
from speech import speech

# all param
# asr = speech.RealTimeASR(rate=16000, channel=1, device=0)

asr = speech.RealTimeASR()

print(asr.asr())
# The paraformer-realtime-v2 model is used here as an example. You may substitute it with another model from the list below, based on your requirements.(此处以paraformer-realtime-v2例，可按需更换模型名称。模型列表)：https://help.aliyun.com/zh/model-studio/getting-started/models
# print(asr.asr(model='paraformer-realtime-v2', save_path='./resources/audio/test_recording.wav', semantic_punctuation_enabled=False, max_sentence_silence=1500))
