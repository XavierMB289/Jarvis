import datetime
import os
import tkinter as tk
from tkinter import filedialog

import easygui

from AI_Call import AIConnect
from JSON_File import JFile
#from AI_STT import SpeechToText
from AI_TTS import TextToSpeech
from NEW_STT import SpeechToText


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
		self.last_index = None
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
		#Window Closing Setup
		def on_closing():
			self.tts.end_talk()
			self.stt.stop()
			self.destroy()
		self.protocol("WM_DELETE_WINDOW", on_closing)
		# SpeechToText Setup
		self.stt = SpeechToText(self)
		#Starting Main Tkinters Loop
		self.mainloop()

	#Creates the menubar for the window
	def _create_menu(self):
		self.menubar = tk.Menu(self)
		self.config(menu=self.menubar)
		#File Menu
		file_menu = tk.Menu(self.menubar, tearoff=False)
		self.menubar.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label="New Project", command=self._new_proj)
		file_menu.add_command(label="Save Project", command=self._save_proj)
		file_menu.add_command(label="Load Project", command=self._load_proj)
		file_menu.add_separator()
		file_menu.add_command(label="FULL RESET", command=self._full_reset)
		file_menu.add_separator()
		file_menu.add_command(label="Clear Log", command=self._clear_log)
		file_menu.add_command(label="Save Log", command=self._save_log)
		file_menu.add_command(label="REMOVE LAST", command=self._remove_last)
		# Init Options Variables
		self._autoscroll = tk.BooleanVar(value=True)
		# Options Menu
		options_menu = tk.Menu(self.menubar, tearoff=False)
		self.menubar.add_cascade(label="Options", menu=options_menu)
		options_menu.add_checkbutton(
			label="Auto-scroll",
			onvalue=True,
			offvalue=False,
			variable=self._autoscroll
		)
		options_menu.add_separator()
		options_menu.add_command(label="Settings...", command=self._show_settings)
		#Recording Notifier
		recording_notifier = tk.Menu(self.menubar, tearoff=False)
		self.menubar.add_cascade(label="Recording...", menu=recording_notifier, state="disabled")

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
	def system_write(self, message: str, append_newline=False):
		self.append_log((os.linesep if append_newline else "")+"[SYSTEM]: "+message, "red")
	def user_write(self, message: str):
		self.last_index = self.text_log.index("end -1 lines")
		self.append_log("[USER-TTS]: "+message, "black")
		self.ai_connect.add_user_input(message)
		response = self.ai_connect.call()
		self.ai_write(self.ai_connect.add_ai_input(response))
	def ai_write(self, message: str):
		self.append_log("[JARVIS]: "+message, "#87CEEB")

	#Adding User Input, Calling AI_Connect, adding AI Input
	def add_inputs(self, user_input: str):
		self.user_write(user_input)
		self.ai_connect.add_user_input(user_input)
		response = self.ai_connect.call()
		self.ai_connect.add_ai_input(response)
		self.ai_write(response.get("content"))

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

	def _remove_last(self):
		self.ai_connect.remove_last_set()
		self.text_log.configure(state="normal")
		self.text_log.delete(self.last_index, tk.END)
		self.system_write("ITEMS REMOVED FROM RECORD", True)

	#OPTIONS HANDLERS
	def _show_settings(self):
		return

	#Recording Handlers
	def show_recording_start(self):
		self.menubar.entryconfig("Recording...", state=tk.NORMAL)
	def show_recording_stop(self):
		self.menubar.entryconfig("Recording...", state=tk.DISABLED)