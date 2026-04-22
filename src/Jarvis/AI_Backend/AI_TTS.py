import numpy as np
from piper.voice import PiperVoice
import sounddevice as sd
import os


class TextToSpeech:
	def __init__(self):
		self.voice = PiperVoice.load(
			os.path.join(os.path.dirname(__file__), '../voice/jarvis-high.onnx'),
			use_cuda=True
		)
		self.listening = False

	def talk(self, text:str):
		stream = sd.OutputStream(samplerate=self.voice.config.sample_rate, channels=1, dtype='int16')
		stream.start()
		self.listening = True
		for audio_bytes in self.voice.synthesize(text):
			int_data = np.frombuffer(audio_bytes.audio_int16_bytes, dtype=np.int16)
			stream.write(int_data)
			if not self.listening:
				break
		stream.stop()
		stream.close()

	def end_talk(self):
		self.listening = False