import os, sys

import requests
import json
import JSON_File as jfile


messages = []
API_KEY: str

def setup():
	global messages, API_KEY
	messages = jfile.load(os.path.join(os.path.dirname(__file__), 'projects/PROJECT_BASELINE.proj'))
	args = sys.argv
	for i in range(len(args)):
		if args[i].startswith('--api-key'):
			API_KEY = args[i+1]

def call() -> dict:
	global messages, API_KEY
	return requests.post(
		url="https://openrouter.ai/api/v1/chat/completions",
		headers={
			"Authorization": "Bearer "+API_KEY,
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