import ssl
import sys

import speech_recognition as sr
import src.Jarvis.sensitive.Secret_Handler as s


class SpeechToText:
	def __init__(self):
		self.r = sr.Recognizer()
		self.secret = s.SecretHandler()
		#Bypassing SSL Verification
		ssl._create_default_https_context = ssl._create_unverified_context
		#Grabbing Debug
		self.debug = False
		args = sys.argv
		for i in range(len(args)):
			key = args[i]
			if key.startswith('--debug'):
				self.debug = True
	def listen(self) -> str:
		mic = sr.Microphone()
		with mic as source:
			self.r.adjust_for_ambient_noise(source)
			if self.debug: print("Say something!")
			audio = self.r.listen(source)

		return self.r.recognize_houndify(audio_data=audio, client_id=self.secret.read("houndify-id"), client_key=self.secret.read("houndify-key"))[0]
