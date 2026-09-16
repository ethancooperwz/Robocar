#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/04/08
from config import *
from speech import speech

# all param
# asr = speech.RealTimeOpenAIASR(rate=16000, channel=1, device=0)

asr = speech.RealTimeOpenAIASR()
# whisper-1 fast than gpt-4o-transcribe 
asr.update_session(model='whisper-1', language='en', threshold=0.2, prefix_padding_ms=300, silence_duration_ms=800)

print('start talking...')
print(asr.asr())
# print(asr.asr(save_path='./resources/audio/test_recording.wav'))
