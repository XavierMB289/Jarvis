import easygui
import src.Jarvis.Window as window
import src.Jarvis.sensitive.Secret_Handler as s

def main():
	secret = s.SecretHandler()
	if not secret.secret_exists("houndify-id"):
		secret.write("houndify-id", easygui.enterbox("Houndify ID:").encode("utf-8"))
		secret.write("houndify-key", easygui.enterbox("Houndify Key:").encode("utf-8"))
		secret.write("openai-key", easygui.enterbox("OpenAI Key:").encode("utf-8"))
	#win = window.LogWindow()
	#win.system_write("Jarvis V0.0.4")

main()