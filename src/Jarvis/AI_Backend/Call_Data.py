import mimetypes
import os

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CallHandler:
	def __init__(self):
		#AI Tool Creation
		self.tools = [
			{
				"type": "function",
				"name": "create_file",
				"description": "Create a file at the given path. Can also be used to overwrite the contents of a file.",
				"parameters": {
					"type": "object",
					"properties": {
						"file_name": {
							"type": "string",
							"description": "The name of the file including the file extension"
						},
						"file_path": {
							"type": "string",
							"description": "The relative path of the file to create"
						},
						"file_data": {
							"type": "string",
							"description": "The contents of the file"
						}
					},
					"required": ["file_name", "file_path", "file_data"]
				}
			},
			{
				"type": "function",
				"name": "read_file",
				"description": "Reads the contents of a file at the given path and returns them",
				"parameters": {
					"type": "object",
					"properties": {
						"file_name": {
							"type": "string",
							"description": "The name of the file including the file extension"
						},
						"file_path": {
							"type": "string",
							"description": "The relative path of the file to read"
						}
					},
					"required": ["file_name", "file_path"]
				}
			},
			{
				"type": "function",
				"name": "delete_file",
				"description": "Delete a file at the given path",
				"parameters": {
					"type": "object",
					"properties": {
						"file_name": {
							"type": "string",
							"description": "The name of the file including the file extension"
						},
						"file_path": {
							"type": "string",
							"description": "The relative path of the file to delete"
						}
					},
					"required": ["file_name", "file_path"]
				}
			},
			{
				"type": "function",
				"name": "create_connections",
				"description": "Prompt the user to create the given connections in order to send texts or emails",
				"parameters": {
					"type": "object",
					"properties": {
						"message": {
							"type": "string",
							"description": "A connection successful message"
						}
					},
					"required": ["message"]
				}
			},
			{
				"type": "function",
				"name": "send_file",
				"description": "Send a file from the given path through email.",
				"parameters": {
					"type": "object",
					"properties": {
						"file_name": {
							"type": "string",
							"description": "The name of the file including the file extension"
						},
						"file_path": {
							"type": "string",
							"description": "The relative path of the file to send"
						},
						"email": {
							"type": "string",
							"description": "The e-mail address to send the file to"
						}
					},
					"required": ["file_name", "file_path"]
				}
			},
			{
				"type": "function",
				"name": "send_email",
				"description": "Send an email to the given email address",
				"parameters": {
					"type": "object",
					"properties": {
						"subject":{
							"type": "string",
							"description": "The subject of the email"
						},
						"message": {
							"type": "string",
							"description": "The message to send"
						},
						"email": {
							"type": "string",
							"description": "The e-mail address to send the message to"
						}
					},
					"required": ["subject", "message"]
				}
			},
			{
				"type": "function",
				"name": "text_user",
				"description": "Send the user a text",
				"parameters": {
					"type": "object",
					"properties": {
						"message": {
							"type": "string",
							"description": "The message to tell the user"
						},
						"phone_number":{
							"type": "string",
							"description": "The phone number of the user"
						},
						"carrier":{
							"type": "string",
							"description": "The phone carrier of the user"
						}
					},
					"required": ["message", "phone_number", "carrier"]
				}
			},
			{
				"type": "function",
				"name": "create_project",
				"description": "Creates a new directory to contain any new files created until a new project is opened",
				"parameters": {
					"type": "object",
					"properties": {
						"project_name": {
							"type": "string",
							"description": "The name of the project"
						}
					}
				}
			},
			{
				"type": "function",
				"name": "open_project",
				"description": "Opens a project folder",
				"parameters": {
					"type": "object",
					"properties": {
						"project_name": {
							"type": "string",
							"description": "The name of the project"
						}
					}
				}
			}
		]
		#Google Credentials Variable
		self.creds = None
		self.service = None

	def __get_user_email(self) -> str:
		"""
		Gets the user's e-mail address
		:return: A string containing the e-mail address
		"""
		return self.service.users().getProfile(userId="me").execute().get('emailAddress')

	@staticmethod
	def create_file(file_name: str, file_path: str, file_data: str):
		"""
		Create a file using the given file name and file path
		:param file_name: Name of the file
		:param file_path: Relative path of the file
		:param file_data: Content of the file
		"""
		with open(file_path+file_name, "w") as file:
			file.write(file_data)
		return f"File {file_name} has been created."

	@staticmethod
	def read_file(file_name: str, file_path: str) -> str:
		"""
		Read a file from the given path
		:param file_name: Name of the file
		:param file_path: Relative path of the file
		:return: The contents of the file (using file.read())
		"""
		ret = ""
		with open(file_path+file_name, "r") as file:
			ret = file.read()
		return ret

	@staticmethod
	def delete_file(file_name: str, file_path: str):
		"""
		Delete a file from the given path
		:param file_name: File Name with the extension
		:param file_path: Relative path of the file
		"""
		if os.path.exists(file_path+file_name):
			os.remove(file_path+file_name)
		return f"File {file_path+file_name} was deleted."

	def create_connections(self, message: str):
		"""
		Creates the GMAIL connection needed to send emails/texts
		:param message: A "test" message
		"""
		if not self.creds or not self.creds.valid:
			self.creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				"sensitive/credentials.json",
				["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/userinfo.email"]
			)
			self.creds = flow.run_local_server(port=0)
		self.service = build("gmail", "v1", credentials=self.creds)
		self.send_email("JARVIS TEST EMAIL", message)
		return "Connection to email services established successfully"

	def send_file(self, file_name: str, file_path: str, email: str = None) -> str:
		"""
		Send a file from the given path through email.
		:param file_name: The name of the file including the file extension
		:param file_path: The relative path of the file to send
		:param email: The email address to send the message to. If None (or not provided), the user is assumed
		"""
		if self.creds is None: return "You must create connections before sending a file"
		try:
			userEmail = self.__get_user_email()
			#Email Setup
			mime_message = EmailMessage()
			mime_message['To'] = email if email is not None else userEmail
			mime_message['From'] = userEmail
			mime_message['Subject'] = "FILE FROM JARVIS"
			mime_message.set_content("Please see attached file")
			#File attachments
			type_subtype, _ = mimetypes.guess_type(file_name)
			maintype, subtype = type_subtype.split("/")
			with open(file_path+file_name, "rb") as file:
				attachment_data = file.read()
			mime_message.add_attachment(attachment_data, maintype=maintype, subtype=subtype, filename=file_name)
			#Encoding & Sending
			encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
			create_draft_request_body = {"message": {"raw": encoded_message}}
			draft = (
				self.service.users().messages().create(userId="me", body=create_draft_request_body).execute()
			)
		except HttpError as error:
			print(f"An error occurred: {error}")

		return "File Sent Successfully"

	def send_email(self, subject:str, message: str, email: str = None) -> str:
		"""
		Creates an email and sends it to the given email or the user
		:param subject: The subject of the email
		:param message: The body of the email. Can use HTML formatting
		:param email: Email address to send the message to. If None (or not provided), the user is assumed
		"""
		if self.creds is None: return "You must create connections before sending an email"
		try:
			userEmail = self.__get_user_email()
			msg = EmailMessage()
			msg.set_content(message)
			msg['To'] = email if email is not None else userEmail
			msg['From'] = userEmail
			msg['Subject'] = subject
			encoded_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
			create_message = {"message": {"raw": encoded_msg}}
			draft = (
				self.service.users().messages().send(userId="me", body=create_message).execute()
			)
		except HttpError as error:
			print(f"An error occurred: {error}")

		return "Email Sent Successfully"

	def text_user(self, message: str, phone_number: str, carrier: str) -> str:
		"""
		Sends a text message to the given phone number
		:param message: Message to send
		:param phone_number: Phone number to send the message to (XXX-XXX-XXXX)
		:param carrier: Phone carrier. All lowercase. Alphabet only.
		"""
		if self.creds is None: return "You must create connections before sending a text"
		CARRIERS = {
			"att": "@mms.att.net",
			"tmobile": "@tmomail.net",
			"verizon": "@vtext.com",
			"sprint": "@messaging.sprintpcs.com"
		}
		if not carrier in CARRIERS: raise Exception("Invalid Carrier specified: "+carrier)
		self.send_email("JARVIS", message, phone_number+CARRIERS[carrier])

		return "Text Sent Successfully"

	def create_project(self, project_name: str) -> str:
		"""Creates a new project"""
		if not os.path.exists(f"../projects/{project_name}/"):
			os.makedirs(f"../projects/{project_name}/")
			return f"Project Created at ../projects/{project_name}/"
		return f"Project Exists at ../projects/{project_name}/"

	def open_project(self, project_name: str) -> str:
		"""Opens a given project"""
		if os.path.exists(f"../projects/{project_name}/"):
			return f"Use ../projects/{project_name}/ as the start of any needed relative file paths from now on"
		return f"Project Not Found at ../projects/{project_name}/"

	def get_tools(self):
		return self.tools