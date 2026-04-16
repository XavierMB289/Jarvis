from __future__ import annotations

import os
import pywhisper
import pyaudio
import wave
import tempfile
from pywhisper import Whisper


class SpeechToText:
	def __init__(self):
		self.model = pywhisper.load_model("base.en")
		self.__reset_file()

		self.wav_file = None
		self.audio = pyaudio.PyAudio()
		self.stream = None

	def __reset_file(self):
		self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete_on_close=False)

	def talk(self):
		sample_rate = 16000
		bits_per_sample = 16
		chunk_size = 1024
		audio_format = pyaudio.paInt16
		channels = 1

		self.wav_file = wave.open(f=self.temp_file.file, mode="wb")
		self.wav_file.setnchannels(channels)
		self.wav_file.setsampwidth(bits_per_sample // 8)
		self.wav_file.setframerate(sample_rate)

		def callback(in_data, frame_count, time_info, status):
			self.wav_file.writeframes(in_data)
			return None, pyaudio.paContinue

		self.stream = self.audio.open(
			format=audio_format,
			channels=channels,
			rate=sample_rate,
			input=True,
			frames_per_buffer=chunk_size,
			stream_callback=callback
		)

	def end_talk(self):
		self.stream.stop_stream()
		self.stream.close()
		self.wav_file.close()

		self.temp_file.close()

		result = self.model.transcribe(audio=self.temp_file.name, fp16=False)

		os.remove(self.temp_file.name)
		self.__reset_file()
		return result["text"].strip()