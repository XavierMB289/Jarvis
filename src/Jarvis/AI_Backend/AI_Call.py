import json
import sys
import threading

from openai import OpenAI

from src.Jarvis.AI_Backend import AI_TTS, Call_Data
from src.Jarvis.sensitive import Secret_Handler


class AIConnect:
	def __init__(self):
		self.client = None
		self.debug = False
		self.secret = Secret_Handler.SecretHandler()
		args = sys.argv
		for i in range(len(args)):
			key = args[i]
			if key.startswith('--debug'):
				self.debug = True
		self.client = OpenAI(api_key=self.secret.read("openai-key"))
		self.call_handler = Call_Data.CallHandler()
		self.input_list: list = []
		self.tts = AI_TTS.TextToSpeech()

	def call(self, user_input: str) -> str:
		"""
		Calls the AI and runs the functions given by the AI.
		All functions are in the Call_Handler.
		:param user_input: Command given to the AI by the user
		:return: Response from the AI representing everything that was completed.
		"""
		self.input_list.append({"role": "user", "content": user_input})
		response = self.client.responses.create(
			model="gpt-5.4-mini",
			tools=self.call_handler.get_tools(),
			input=self.input_list
		)
		self.input_list += response.output

		for item in response.output:
			if item.type == "function_call":
				loaded_json = json.loads(item.arguments)
				data = None
				match item.name:
					case "create_file":
						file_name = loaded_json["file_name"]
						file_path = loaded_json["file_path"]
						file_data = loaded_json["file_data"]
						data = self.call_handler.create_file(file_name, file_path, file_data)
					case "read_file":
						file_name = loaded_json["file_name"]
						file_path = loaded_json["file_path"]
						data = self.call_handler.read_file(file_name, file_path)
					case "delete_file":
						file_name = loaded_json["file_name"]
						file_path = loaded_json["file_path"]
						data = self.call_handler.delete_file(file_name, file_path)
					case "create_connections":
						message = loaded_json["message"]
						data = self.call_handler.create_connections(message)
					case "send_file":
						file_name = loaded_json["file_name"]
						file_path = loaded_json["file_path"]
						email = loaded_json["email"]
						data = self.call_handler.send_file(file_name, file_path, email)
					case "send_email":
						subject = loaded_json["subject"]
						message = loaded_json["message"]
						email = loaded_json["email"]
						data = self.call_handler.send_email(subject, message, email)
					case "text_user":
						message = loaded_json["message"]
						number = loaded_json["phone_number"]
						carrier = loaded_json["carrier"]
						data = self.call_handler.text_user(message, number, carrier)
					case "create_project":
						name = loaded_json["project_name"]
						data = self.call_handler.create_project(name)
					case "open_project":
						name = loaded_json["project_name"]
						data = self.call_handler.open_project(name)
				if data is not None:
					self.input_list.append({
						"type": "function_call_output",
						"call_id": item.call_id,
						"output": data
					})
		if self.debug:
			print("Created Input List:")
			print(self.input_list)
		response = self.client.responses.create(
			model="gpt-5.4-mini",
			instructions="Respond with a summary of everything done.",
			tools=self.call_handler.get_tools(),
			input=self.input_list
		)
		self.tts.talk(response.output_text)
		return response.output_text