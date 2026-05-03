import os
import sys

from cryptography.fernet import Fernet


class SecretHandler:
	def __init__(self):
		self.file_path = sys.path[0]+"\\sensitive\\"

		if os.path.exists(self.file_path+"secret.key"):
			with open(self.file_path+"secret.key", "rb") as f:
				self.key = f.read()
		else:
			self.key = Fernet.generate_key()
			with open(self.file_path+"secret.key", "wb") as f:
				f.write(self.key)

	def write(self, name:str, data: bytes):
		fernet = Fernet(self.key)
		with open(self.file_path+f"{name}.secret", "wb") as f:
			f.write(fernet.encrypt(data))

	def read(self, name:str) -> str:
		fernet = Fernet(self.key)
		with open(self.file_path+f"{name}.secret", "rb") as f:
			encrypted = f.read()
		return str(fernet.decrypt(encrypted), "utf-8")

	def secret_exists(self, name:str):
		return os.path.exists(self.file_path+f"{name}.secret")