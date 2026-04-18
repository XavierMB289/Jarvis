import queue
import threading

import numpy as np
import pyaudio
from faster_whisper import WhisperModel


#It doesn't like when I import LogWindow Here
#win: LogWindow
class SpeechToText:
	def __init__(self, win):
		self.window = win
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 16000
		self.CHUNK = 1024
		self.SEGMENT_SECONDS = 10
		self.MODEL_SIZE = "base"

		self.audio_queue = queue.Queue()

		self.model = WhisperModel(self.MODEL_SIZE, device="cpu", compute_type="int8")

		self.running = True

		self.audio = pyaudio.PyAudio()
		self.stream = self.audio.open(
			format=self.FORMAT,
			channels=self.CHANNELS,
			rate=self.RATE,
			input=True,
			frames_per_buffer=self.CHUNK,
			stream_callback=self.__audio_callback
		)
		self.stream.start_stream()

		self.worker_thread = threading.Thread(target=self.worker, daemon=True)
		self.worker_thread.start()

	def __audio_callback(self, in_data, frame_count, time_info, status):
		self.audio_queue.put(in_data)
		return None, pyaudio.paContinue

	def worker(self):
		buffer = b""
		target_bytes = int(self.RATE * self.SEGMENT_SECONDS * 2)

		while self.running:
			self.window.show_recording_start()
			while len(buffer) < target_bytes:
				try:
					data = self.audio_queue.get(timeout=1.0)
					buffer += data
				except queue.Empty:
					continue
			self.window.show_recording_stop()
			segment_bytes = buffer[:target_bytes]
			buffer = buffer[target_bytes:]

			audio_np = np.frombuffer(segment_bytes, dtype=np.int16).astype(np.float32) / 32768.0

			segments, info = self.model.transcribe(
				audio_np,
				language="en",
				task="transcribe",
				vad_filter=True
			)

			text = " ".join(seg.text.strip() for seg in segments).strip()
			if text:
				self.window.user_write(text)

	def stop(self):
		self.running = False
		self.stream.stop_stream()
		self.stream.close()
		self.audio.terminate()