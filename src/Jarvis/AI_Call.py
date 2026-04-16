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
				self.API_KEY = str(args[i + 1])
				break
		if self.API_KEY is None:
			raise Exception('API_KEY not found! Add "--api-key <API_KEY>" when starting the program.')
		self.messages: list[dict] = JFile("projects/PROJECT_BASELINE.proj").load()

	#Makes the call
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

	#Adds the input to messages as though the user said it
	def add_user_input(self, user_input: str):
		self.messages.append({"role": "user", "content": user_input})

	#Adds the input to messages as though the AI said it
	def add_ai_input(self, response: dict) -> str:
		self.messages.append({"role": "assistant", "content": response.get("content"), "reasoning_details": response.get("reasoning_details")})
		return response.get("content")

	#Completely deletes all messages
	def hard_reset_messages(self):
		self.messages = []

	#Loads the PROJECT_BASELINE file
	def soft_reset_messages(self):
		self.messages = JFile("projects/PROJECT_BASELINE.proj").load()

	#Removes the last 2 messages (user input and AI output)
	def remove_last_set(self):
		del self.messages[-2:]

	#Gets All the messages currently
	def get_messages(self) -> list[dict]:
		return self.messages

	#Sets the messages
	def set_messages(self, msgs: list):
		self.messages = msgs