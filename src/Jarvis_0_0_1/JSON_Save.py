import json
from pathlib import Path

def save(data, file_path: str):
	output_path = Path(file_path)

	with output_path.open("w", encoding="utf-8") as f:
		json.dump(
			data,
			f,
			indent="\t",
			sort_keys=True,
			ensure_ascii=False
		)

def load(file_path: str) -> str:
	path = Path(file_path)

	if not path.is_file():
		raise FileNotFoundError(f"No such file: {file_path}")

	with path.open("r", encoding="utf-8") as f:
		loaded = json.load(f)

	return json.dumps(loaded, indent="\t", ensure_ascii=False)