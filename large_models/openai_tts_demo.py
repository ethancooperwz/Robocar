#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/04/08
from config import *
from speech import speech  

tts = speech.RealTimeOpenAITTS()
tts.tts("Hello, Can I help you?") # https://platform.openai.com/docs/guides/text-to-speech
tts.tts("Hello, Can I help you?", model="tts-1", voice="onyx", speed=1.0, instructions='Speak in a cheerful and positive tone.')
tts.save_audio("Hello, Can I help you?", model="gpt-4o-mini-tts", voice="onyx", speed=1.0, instructions='Speak in a cheerful and positive tone.', audio_format='wav', save_path="./resources/audio/tts_audio.wav")

# tts.save_audio("I'm here", model="tts-1-hd", voice="onyx", speed=0.7, audio_format='wav', save_path="./resources/audio/en/wakeup.wav")
# tts.save_audio("I'm ready", model="tts-1-hd", voice="onyx", speed=0.9, audio_format='wav', save_path="./resources/audio/en/start_audio.wav")
# tts.save_audio("Sorry, would you please repeat again", model="tts-1-hd", voice="onyx", audio_format='wav', save_path="./resources/audio/en/no_voice.wav")
# tts.save_audio("Sorry, I can't do that", model="tts-1-hd", voice="onyx", audio_format='wav', save_path="./resources/audio/en/error.wav")
# tts.save_audio("OK, Start tracking", model="tts-1-hd", voice="onyx", audio_format='wav', save_path="./resources/audio/en/start_track.wav")
# tts.save_audio("Failed to get target", model="tts-1-hd", voice="onyx", audio_format='wav', save_path="./resources/audio/en/track_fail.wav")
# tts.save_audio("Already remembered", model="tts-1-hd", voice="onyx", audio_format='wav', save_path="./resources/audio/en/record_finish.wav")
