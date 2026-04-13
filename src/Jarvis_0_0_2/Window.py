import datetime
import tkinter as tk
from threading import Thread
from tkinter import filedialog

import easygui

from AI_Call import AIConnect
from JSON_File import JFile
from AI_STT import SpeechToText
from AI_TTS import TextToSpeech


class LogWindow(tk.Tk):
	#Initializes Variables used in LogWindow
	def __init__(self):
		#Initializing the Window
		super().__init__()
		self.title("Jarvis Log")
		self.geometry("600x400")
		#Layout
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		#"Console log"
		self.text_log = tk.Text(
			self,
			wrap='word',
			font=('Consolas', 10),
			bg='#696969',
			fg='#222222',
			state='disabled'
		)
		self.text_log.grid(column=0, row=0, sticky="nsew")
		#Scroll Bar
		self.scrollbar = tk.Scrollbar(
			self,
			orient='vertical',
			command=self.text_log.yview
		)
		self.scrollbar.grid(column=1, row=0, sticky="ns")
		self.text_log.configure(yscrollcommand=self.scrollbar.set)
		#Menu Bar Setup
		self._create_menu()
		#AI Connect Setup
		self.ai_connect = AIConnect()
		#TextToSpeech Setup
		self.tts = TextToSpeech()
		#SpeechToText Setup
		self.stt = SpeechToText()
		self.stt.start()
		#Window Closing Setup
		def on_closing():
			self.tts.end_talk()
			self.stt.stop()
			self.destroy()
		self.protocol("WM_DELETE_WINDOW", on_closing)
		def window_check():
			while self.stt.is_running():
				data = self.stt.read_audio()
				if not data is None:
					ai_output = self.ai_connect.add_ai_input(data)
					self.ai_write(ai_output)
					self.tts.talk(ai_output)

		self.thread = Thread(target=window_check, name="STT_Check_For_Window")
		self.thread.start()
		#Starting Main Tkinters Loop
		self.mainloop()

	#Creates the menubar for the window
	def _create_menu(self):
		menubar = tk.Menu(self)
		self.config(menu=menubar)
		#File Menu
		file_menu = tk.Menu(menubar, tearoff=False)
		menubar.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label="New Project", command=self._new_proj)
		file_menu.add_command(label="Save Project", command=self._save_proj)
		file_menu.add_command(label="Load Project", command=self._load_proj)
		file_menu.add_separator()
		file_menu.add_command(label="FULL RESET", command=self._full_reset)
		file_menu.add_separator()
		file_menu.add_command(label="Clear Log", command=self._clear_log)
		file_menu.add_command(label="Save Log", command=self._save_log)
		# Init Options Variables
		self._autoscroll = tk.BooleanVar(value=True)
		# Options Menu
		options_menu = tk.Menu(menubar, tearoff=False)
		menubar.add_cascade(label="Options", menu=options_menu)
		options_menu.add_checkbutton(
			label="Auto-scroll",
			onvalue=True,
			offvalue=False,
			variable=self._autoscroll
		)
		options_menu.add_separator()
		options_menu.add_command(label="Settings...", command=self._show_settings)

	#LOGGING HELPERS
	#Adds text to the end of the log
	def append_log(self, message: str, color: str):
		# Create the tag if we've never used this color before
		if color not in self.text_log.tag_names():
			self.text_log.tag_configure(color, foreground=color)
		# Output Text to output_text
		self.text_log.configure(state='normal')
		self.text_log.insert(tk.END, message + "\n", color)
		self.text_log.configure(state='disabled')
		if self._autoscroll.get():
			self.text_log.see(tk.END)

	#Default options for quick use
	def system_write(self, message: str): self.append_log("[SYSTEM]: "+message, "red")
	def ai_write(self, message: str): self.append_log("[JARVIS]: "+message, "#87CEEB")
	def user_write(self, message: str): self.append_log("[USER-TTS]"+message, "black")

	#Clears the current log
	def _clear_log(self):
		self.text_log.configure(state='normal')
		self.text_log.delete(1.0, tk.END)
		self.text_log.configure(state='disabled')

	#Attempts to save the log to a specified filepath
	def _save_log(self):
		self.system_write(f"Attempting to save log at {str(datetime.datetime.now())}.")
		content = self.text_log.get("1.0", tk.END).rstrip()
		if not content:
			self.system_write("Log is empty - nothing to save.")
			return
		filepath = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
			title="Save Log As..."
		)
		if filepath:
			try:
				with open(filepath, "w", encoding="utf-8") as f:
					f.write(content)
					self.system_write(f"Log saved at {filepath}")
			except Exception as e:
				self.system_write(f"Failed to save file:\n{e}")


	#FILE HANDLERS
	def _new_proj(self):
		self._clear_log()
		self.ai_connect.soft_reset_messages()

	def _save_proj(self):
		proj_name = easygui.enterbox("Project Name: ")
		JFile(f'projects/{proj_name}.proj').save(self.ai_connect.get_messages())
		self.system_write(f"Project saved at {proj_name}!")

	def _load_proj(self):
		proj_name = easygui.enterbox("Project Name: ")
		self.ai_connect.set_messages(JFile(f'projects/{proj_name}.proj').load())
		self._clear_log()
		self.system_write(f"Project {proj_name} loaded!")

	def _full_reset(self):
		self.ai_connect.hard_reset_messages()
		self._clear_log()
		self.system_write("FULL RESET COMPLETE")

	#OPTIONS HANDLERS
	def _show_settings(self):
		return