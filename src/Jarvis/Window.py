import tkinter as tk


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

	def setup_stop(self, stopFun = None):
		# Window Closing Setup
		def on_closing():
			if stopFun is not None: stopFun()
			self.destroy()
		self.protocol("WM_DELETE_WINDOW", on_closing)

	def start_loop(self):
		# Starting Main Tkinters Loop
		self.mainloop()

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
		self.text_log.see(tk.END)

	#Default options for quick use
	def system_write(self, message: str): self.append_log("[SYSTEM]: "+message, "red")
	def ai_write(self, message: str): self.append_log("[JARVIS]: " + message, "#87CEEB")
	def user_write(self, message: str): self.append_log("[USER-TTS]: "+message, "black")