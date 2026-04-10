import requests
import json


messages = []

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