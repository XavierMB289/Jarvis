from __future__ import annotations

import os
import pywhisper
import pyaudio
import wave
import tempfile
from pywhisper import Whisper

#Variable Declarations
model:Whisper
temp_file: tempfile._TemporaryFileWrapper[bytes]
wav_file: wave.Wave_read
audio: pyaudio.PyAudio
stream: pyaudio.Stream

def setup():
	global model, temp_file
	model = pywhisper.load_model("base.en")
	temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete_on_close=False)

def talk():
	global model, temp_file, wav_file, audio, stream
	sample_rate = 16000
	bits_per_sample = 16
	chunk_size = 1024
	audio_format = pyaudio.paInt16
	channels = 1

	wav_file = wave.open(f=temp_file.file, mode="wb")
	wav_file.setnchannels(channels)
	wav_file.setsampwidth(bits_per_sample // 8)
	wav_file.setframerate(sample_rate)

	def callback(in_data, frame_count, time_info, status):
		wav_file.writeframes(in_data)
		return None, pyaudio.paContinue

	audio = pyaudio.PyAudio()

	stream = audio.open(
		format=audio_format,
		channels=channels,
		rate=sample_rate,
		input=True,
		frames_per_buffer=chunk_size,
		stream_callback=callback
	)

def end_talk() -> str:
	global stream, audio, wav_file, temp_file
	stream.stop_stream()
	stream.close()
	audio.terminate()

	wav_file.close()

	temp_file.close()
	result = model.transcribe(audio=temp_file.name, fp16=False)

	os.remove(temp_file.name)
	temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete_on_close=False)

	return result["text"].strip()