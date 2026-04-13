import sys

import requests
import json
from JSON_File import JFile


class AIConnect:
	def __init__(self):
		args = sys.argv
		self.API_KEY = None
		for i in range(len(args)):
			if args[i].startswith('--api-key'):
				self.API_KEY = args[i + 1]
		if self.API_KEY is None:
			raise Exception('API_KEY not found! Add "--api-key <API_KEY>" when starting the program.')
		self.messages = JFile("projects/PROJECT_BASELINE.proj").load()
		print("AI_Call Loaded")

	def call(self) -> dict:
		return requests.post(
			url="https://openrouter.ai/api/v1/chat/completions",
			headers={
				"Authorization": "Bearer "+self.API_KEY,
				"Content-Type": "application/json"
			},
			data=json.dumps({
				"model": "nvidia/nemotron-3-super-120b-a12b:free",
				"messages": self.messages,
				"reasoning": {"enabled": True}
			})
		).json()['choices'][0]['message']

	def add_user_input(self, user_input: str):
		self.messages.append({"role": "user", "content": user_input})

	def add_ai_input(self, response: dict) -> str:
		self.messages.append({"role": "assistant", "content": response.get("content"), "reasoning_details": response.get("reasoning_details")})
		return response.get("content")

	def hard_reset_messages(self):
		self.messages = []

	def soft_reset_messages(self):
		self.messages = JFile("projects/PROJECT_BASELINE.proj").load()

	def get_messages(self) -> list[dict]:
		return self.messages

	def set_messages(self, msgs: list):
		self.messages = msgs