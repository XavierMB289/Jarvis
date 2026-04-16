import json
import os
from pathlib import Path


class JFile:
	def __init__(self, relative_file_path: str):
		self.file_path = Path(os.path.join(os.path.dirname(__file__), relative_file_path))

	def save(self, data):
		with self.file_path.open('w', encoding="utf-8") as f:
			json.dump(
				data,
				f,
				indent="\t",
				sort_keys=True,
				ensure_ascii=False
			)

	def load(self):
		if not self.file_path.is_file():
			raise FileNotFoundError(f"File not found: {self.file_path}.")

		with self.file_path.open('r', encoding="utf-8") as f:
			loaded = json.load(f)

		return loaded
