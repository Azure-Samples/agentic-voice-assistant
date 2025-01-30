
import os
import requests

SEND_EMAIL_LOGIC_APP_URL = os.getenv("SEND_EMAIL_LOGIC_APP_URL")
async def send_email(params):
    try:
        res = requests.post(SEND_EMAIL_LOGIC_APP_URL, json=params)
        res.raise_for_status()
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"
    

assistant_agent = {
	"id": "Assistant_Executive_Assistant",
	"name": "Executive Assistant",
	"description": """Call this if:
		- You need send an email
        - You need to recap the conversation.""",
	"system_message": """
	You are an executive assistant that helps with administartive tasks.
 	Interaction goes over voice, so it's *super* important that answers are as short as possible. Use professional language.
	
	Your tasks are - on the request by the user:
	- Provide a summary of the conversation in a structured format.
	- Send an email to the specified user using the "send_email" tool.
 
	NOTES:
	- Every time you are about to send an email, make sure to confirm all the details with the user.
 """,
	"tools": [
  		{
			"name": "send_email",
			"description": "Send an email to the specified user.",
			"parameters": {
				"type": "object",
				"properties": {
					"to": {"type": "string", "description": "The recipient's email address."},
					"subject": {"type": "string", "description": "The subject of the email."},
					"body": {"type": "string", "description": "The body of the email."},
				},
			},
			"returns": send_email,
		}
	],
}