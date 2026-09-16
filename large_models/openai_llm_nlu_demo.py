#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2025/02/28
from config import *
from speech import speech

client = speech.OpenAIAPI(llm_api_key, llm_base_url)

print(client.llm('Artificial intelligence (AI) is a branch of computer science that aims to create systems that can simulate human intelligent behavior. The application range of AI is very wide, including natural language processing, image recognition, machine learning, autonomous driving, and intelligent recommendation systems. In recent years, the rise of deep learning has greatly promoted the development of artificial intelligence. Deep learning is a type of machine learning that processes and analyzes data by simulating the working method of neurons in the human brain. Using large amounts of data, deep learning models can recognize patterns, classify, and perform excellent performance in complex tasks. Although artificial intelligence has made significant progress in many fields, it still faces some challenges. For example, how to ensure the transparency and fairness of decision-making in AI systems, and how to deal with the impact of AI on the job market are urgent issues to be solved. With the continuous advancement of technology, the potential of artificial intelligence will continue to be tapped, bringing more innovation and changes to society. However, ensuring the safety and controllability of AI will be the key to future development. Summarize the above text in concise language', prompt='', model='gpt-4o-mini'))
