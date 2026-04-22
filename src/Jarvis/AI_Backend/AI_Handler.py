#TODO: Add functions that follow NEXT_STEPS.txt
import json

import easygui

from src.Jarvis import Window
from src.Jarvis.JSON_File import JFile
from src.Jarvis.AI_Backend.AI_Call import AIConnect
from src.Jarvis.AI_Backend.AI_STT import SpeechToText
from src.Jarvis.AI_Backend.AI_TTS import TextToSpeech


class AIHandler:

	def __init__(self, win):
		self.window: Window.LogWindow = win
		# SpeechToText Setup
		self.stt = SpeechToText(self.window)
		# AI Connect Setup
		self.ai_connect = AIConnect()
		# TextToSpeech Setup
		self.tts = TextToSpeech()
	def stop(self):
		self.tts.end_talk()
		self.stt.stop()
	def think(self, message: str) -> str:
		self.ai_connect.add_user_input(message)
		response = self.ai_connect.call()
		json_obj: dict = json.loads(response.get("content"))
		self.ai_connect.add_ai_input(response.get("content"), response.get("reasoning_details"))
		self.tts.talk(json_obj.get("text"))

		#TODO: Filehandling here

		return json_obj.get("text")


	#Soft Reset for New Project Menu Button
	def soft_reset(self):
		self.window.clear_log()
		self.ai_connect.soft_reset_messages()
		self.window.system_write("Soft Reset Complete")
	#Save Project
	def save_proj(self):
		proj_name = easygui.enterbox("Project Name: ")
		JFile(f'projects/{proj_name}.proj').save(self.ai_connect.get_messages())
		self.window.system_write(f"Project saved at {proj_name}!")
	#Load Project
	def load_proj(self):
		proj_name = easygui.enterbox("Project Name: ")
		self.window.clear_log()
		self.ai_connect.set_messages(JFile(f'projects/{proj_name}.proj').load())
		self.window.system_write(f"Project {proj_name} loaded!")
	#Hard Reset for Full Reset Button
	def hard_reset(self):
		self.window.clear_log()
		self.ai_connect.hard_reset_messages()
		self.window.system_write("HARD RESET COMPLETE")
	#Remove Last
	def remove_last(self):
		self.window.text_log.configure(state="normal")
		self.window.text_log.delete(self.window.last_index, "end")
		self.ai_connect.remove_last_set()
		self.window.system_write("ITEMS REMOVED FROM RECORD", True)
	#Advanced Entry
	def adv_entry(self):
		self.stt.stop()
		entry = easygui.enterbox("Advanced Entry: ")
		self.window.ai_write(self.think(entry))
		self.stt = SpeechToText(self.window)