import threading

from src.Jarvis import Window
from src.Jarvis.AI_Backend import AI_STT, AI_Call


class ThreadedAIHandler:
	def __init__(self, win: Window.LogWindow):
		self.window = win
		self.stt = AI_STT.SpeechToText()
		self.call = AI_Call.AIConnect()
		self.running = True
		self.thread = threading.Thread(target=self.run)
		self.thread.start()
	def run(self):
		while self.running:
			user_input = self.stt.listen()
			self.window.user_write(user_input)
			response = self.call.call(user_input)
			self.window.ai_write(response)