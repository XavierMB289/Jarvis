import tkinter as tk
import AI_STT as stt
import AI_Call as call
import AI_TTS as tts
import threading

root: tk.Tk
output_text: tk.Text
btn_style = {
	'font': ('Segoe UI', 10),
	'width': 12,
	'pady': 6
}
tts_thread: threading.Thread = None

def write_output(message: str, color: str = "black"):
	global output_text
	#Create the tag if we've never used this color before
	if color not in output_text.tag_names():
		output_text.tag_configure(color, foreground=color)
	#Output Text to output_text
	output_text.configure(state='normal')
	output_text.insert(tk.END, message+"\n", color)
	output_text.see(tk.END)
	output_text.configure(state='disabled')

def setup():
	global root, output_text, btn_style, tts_thread
	#Window
	root = tk.Tk()
	root.title("Jarvis")
	root.geometry("600x500")
	#Frames
	left_frame = tk.Frame(root)
	left_frame.pack(side="left", fill='both', expand=True)
	right_frame = tk.Frame(root, width=200)
	right_frame.pack(side='right', fill='y')
	right_frame.pack_propagate(False)
	#Text Output (left side)
	output_text = tk.Text(
		left_frame,
		wrap='word',
		font=('Consolas', 10),
		bg='#f8f8f8',
		fg='#222222',
		state='disabled'
	)
	output_text.pack(side='left', fill='both', expand=True)
	#Text Output Scrollbar
	v_scroll = tk.Scrollbar(left_frame, orient='vertical', command=output_text.yview)
	v_scroll.pack(side='right', fill='y')
	output_text.configure(yscrollcommand=v_scroll.set)
	#TTS Button
	def tts_on_press(event):
		stt.talk()
	def tts_on_release(event):
		global tts_thread
		if tts_thread is None or not tts_thread.is_alive():
			tts_thread = threading.Thread(target=tts_background_process, name="TTS_Background_Process")
			tts_thread.start()
	def tts_background_process():
		global tts_thread
		user_input = stt.end_talk()
		write_output("[USER-TTS]: "+user_input)
		call.add_user_input(user_input)
		response = call.call()
		content = response.get("content")
		write_output("[AI]: "+content, "#87CEEB")
		call.add_ai_input(response)
		tts.talk(content)
		#Join the current backgrounded thread
		#HAS TO BE THE FINAL STEP
		tts_thread.join()

	tts_btn = tk.Button(right_frame, text="TTS", **btn_style)
	tts_btn.pack(pady=(10,5))
	tts_btn.bind("<ButtonPress-1>", tts_on_press)
	tts_btn.bind("<ButtonRelease-1>", tts_on_release)
	#New Button
	def new_cmd():
		return
	new_btn = tk.Button(right_frame, text="NEW", command=new_cmd, **btn_style)
	new_btn.pack(pady=5)
	#Reset Button
	def full_reset():
		return
	reset_btn = tk.Button(right_frame, text="FULL RESET", command=full_reset, **btn_style)
	reset_btn.pack(pady=5)
	#STT Setup
	stt.setup()
	#TTS Setup
	tts.setup()

def start():
	global root
	root.mainloop()