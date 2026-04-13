from __future__ import annotations

import os
from threading import Thread
import pywhisper
import pyaudio
import math
import wave
import tempfile
from AI_Call import AIConnect

class SpeechToText:
	def __init__(self):
		self.thread = None
		#Model Variables
		self.model = pywhisper.load_model("base.en")
		self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete_on_close=False)
		self.running = True
		#Audio Variables
		self.audio_threshold = 1000
		self.sample_rate = 16000
		self.bits_per_sample = 16
		self.chunk_size = 1024
		self.audio_format = pyaudio.paInt16
		self.channels = 1
		#Flag for determining if the audio can be read or not
		self.flag = False

	def start(self):
		self.thread = Thread(target=self._talk, name="STT_Microphone_Input")
		self.thread.start()

	def stop(self):
		self.running = False
		self.thread.join()

	def _detect_input(self, data) -> bool:
		if not data:
			return False
		rms = math.sqrt(sum([x ** 2 for x in data]) / len(data))
		return rms > self.audio_threshold

	def _talk(self):
		while self.running:
			if self.flag: continue

			self._setup_audio()

			chunks_checked = 0
			data = []
			while self._detect_input(data) and chunks_checked > 5:
				data = self.stream.read(self.chunk_size)
				chunks_checked += 1

			self.flag = True

	def _setup_audio(self):
		self.wav_file = wave.open(f=self.temp_file.file, mode="wb")
		self.wav_file.setnchannels(self.channels)
		self.wav_file.setsampwidth(self.bits_per_sample // 8)
		self.wav_file.setframerate(self.sample_rate)

		def callback(in_data, frame_count, time_info, status):
			self.wav_file.writeframes(in_data)
			return None, pyaudio.paContinue

		self.audio = pyaudio.PyAudio()

		self.stream = self.audio.open(
			format=self.audio_format,
			channels=self.channels,
			rate=self.sample_rate,
			input=True,
			frames_per_buffer=self.chunk_size,
			stream_callback=callback
		)

	def read_audio(self):
		if not self.flag: return None
		#Stopping All Sources so we can read the file
		self.stream.stop_stream()
		self.stream.close()
		self.audio.terminate()
		self.wav_file.close()
		self.temp_file.close()
		#Reading/Transcribing the file
		result = pywhisper.transcribe(model=self.model, audio=self.temp_file.name)
		#Removing the file
		os.remove(self.temp_file.name)
		#Creating a new temp_file
		self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete_on_close=False)
		self.flag = False
		return result["text"].strip()

	def is_running(self) -> bool:
		return self.running