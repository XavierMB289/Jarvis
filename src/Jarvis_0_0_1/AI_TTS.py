import numpy as np
from piper.voice import PiperVoice
import sounddevice as sd
import os

#Variable Declaration
voice:PiperVoice

#Setup voice variable with jarvis voice
def setup():
	global voice
	temp_file = os.path.join(os.path.dirname(__file__), 'voice/jarvis-high.onnx')
	voice = PiperVoice.load(temp_file, use_cuda=True)

#TTS output
def talk(text:str):
	global voice
	stream = sd.OutputStream(samplerate=voice.config.sample_rate, channels=1, dtype='int16')
	stream.start()
	for audio_bytes in voice.synthesize(text):
		int_data = np.frombuffer(audio_bytes.audio_int16_bytes, dtype=np.int16)
		stream.write(int_data)
	stream.stop()
	stream.close()