import os

import requests
import json
import JSON_File as jfile


messages = []

def setup():
	global messages
	messages = jfile.load(os.path.join(os.path.dirname(__file__), 'projects/PROJECT_BASELINE.proj'))

def call() -> dict:
	global messages
	return requests.post(
		url="https://openrouter.ai/api/v1/chat/completions",
		headers={
			"Authorization": "Bearer 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",
			"Content-Type": "application/json"
		},
		data=json.dumps({
			"model": "nvidia/nemotron-3-super-120b-a12b:free",
			"messages": messages,
			"reasoning": {"enabled": True}
		})
	).json()['choices'][0]['message']

def add_user_input(user_input:str):
	global messages
	messages.append({"role": "user", "content": user_input})

def add_ai_input(response):
	global messages
	messages.append({"role": "assistant", "content": response.get("content"), "reasoning_details": response.get("reasoning_details")})

def reset_messages():
	global messages
	messages = []

def get_messages() -> list:
	global messages
	return messages

def set_messages(msgs:list):
	global messages
	messages = msgs