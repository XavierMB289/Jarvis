import datetime
import os
import tkinter as tk
from tkinter import filedialog

from src.Jarvis.AI_Backend.AI_Handler import AIHandler


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
		# AIHandler Setup
		self.aihandler = AIHandler(self)
		#Menu Bar Setup
		self._create_menu()
		#Window Closing Setup
		def on_closing():
			self.aihandler.stop()
			self.destroy()
		self.protocol("WM_DELETE_WINDOW", on_closing)
		#Starting Main Tkinters Loop
		self.mainloop()

	#Creates the menubar for the window
	def _create_menu(self):
		self.menubar = tk.Menu(self)
		self.config(menu=self.menubar)
		#File Menu
		file_menu = tk.Menu(self.menubar, tearoff=False)
		self.menubar.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label="New Project", command=self.aihandler.soft_reset)
		file_menu.add_command(label="Save Project", command=self.aihandler.save_proj)
		file_menu.add_command(label="Load Project", command=self.aihandler.load_proj)
		file_menu.add_separator()
		file_menu.add_command(label="FULL RESET", command=self.aihandler.hard_reset)
		file_menu.add_separator()
		file_menu.add_command(label="Clear Log", command=self.clear_log)
		file_menu.add_command(label="Save Log", command=self._save_log)
		file_menu.add_separator()
		file_menu.add_command(label="REMOVE LAST", command=self.aihandler.remove_last)
		file_menu.add_command(label="Advanced Entry", command=self.aihandler.adv_entry)
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
	def system_write(self, message: str, append_newline=False): self.append_log((os.linesep if append_newline else "")+"[SYSTEM]: "+message, "red")
	def ai_write(self, message: str): self.append_log("[JARVIS]: " + message, "#87CEEB")
	def user_write(self, message: str):
		self.last_index = self.text_log.index("end -1 lines")
		self.append_log("[USER-TTS]: "+message, "black")
		self.ai_write(self.aihandler.think(message))

	#Clears the current log
	def clear_log(self):
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

	#OPTIONS HANDLERS
	def _show_settings(self):
		return

	#Recording Handlers
	def show_recording_start(self):
		self.menubar.entryconfig("Recording...", state=tk.NORMAL)
	def show_recording_stop(self):
		self.menubar.entryconfig("Recording...", state=tk.DISABLED)