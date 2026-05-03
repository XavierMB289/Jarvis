import sys
import threading

import src.Jarvis.AI_Backend.AI_STT as AI_STT
import src.Jarvis.AI_Backend.AI_Call as AI_Call
from src.Jarvis import Window


class ThreadedAIHandler:
	def __init__(self, win: Window.LogWindow):
		self.debug = False
		args = sys.argv
		for i in range(len(args)):
			key = args[i]
			if key.startswith('--debug'):
				self.debug = True
		self.window = win
		if self.debug: print("Starting STT")
		self.stt = AI_STT.SpeechToText()
		if self.debug: print("Starting Connection")
		self.call = AI_Call.AIConnect()
		self.running = True
		if self.debug: print("Starting Thread")
		self.thread = threading.Thread(target=self.run)
		self.thread.start()
	def run(self):
		while self.running:
			user_input = self.stt.listen()
			self.window.user_write(user_input)
			response = self.call.call(user_input)
			self.window.ai_write(response)
	def stop(self):
		self.running = False