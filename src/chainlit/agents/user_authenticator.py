import os
from pydub import AudioSegment
from pydub.silence import split_on_silence  # added import
from io import BytesIO
from openai import AzureOpenAI  
from azure.identity import DefaultAzureCredential, get_bearer_token_provider  
import azure.cognitiveservices.speech as speechsdk

def get_audio_speech(params):
	# Assume pcm_data is a BytesIO object containing raw PCM data
	audio_buffer = BytesIO(params["last_audio_speech"])  # some_pcm_bytes should be raw PCM audio
	# Define PCM parameters (Azure OpenAI RealtTime config)
	sample_width = 2  # 2 bytes per sample (16-bit PCM)
	frame_rate = 24000  # Sample rate in Hz
	channels = 1  # Mono audio (use 2 for stereo)
	# Load PCM data into pydub
	audio = AudioSegment.from_raw(audio_buffer, sample_width=sample_width, frame_rate=frame_rate, channels=channels)
	audio = audio.set_frame_rate(16000)
	# Extract the last spoken segment after silence
	segments = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)
	last_segment = segments[-1] if segments else audio
	# Export the last spoken segment to wav for transcription using file conversion
	filename = f"output_{params['session_id']}.wav"
	last_segment.export(filename, format="wav")
	return filename


async def authenticate_user(params):
	# Get the audio speech
	filename = get_audio_speech(params)
	# Transcribe the audio file
	transcript = from_file(filename)
	# Print the transcript
	print(f"Transcript:  {transcript}")
	# Delete the file after use
	os.remove(filename)
	return validate_user_openai(transcript)


def validate_user_openai(transcript: str):
	# Get the Azure OpenAI Service endpoint and api version from environment variables
	endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  
	deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")  
	api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")             
	# Initialize Azure OpenAI Service client with Entra ID authentication
	token_provider = get_bearer_token_provider(  
		DefaultAzureCredential(),  
		"https://cognitiveservices.azure.com/.default"  
	)  
	# Initialize Azure OpenAI Service client with key-based authentication    
	client = AzureOpenAI(  
		azure_endpoint=endpoint,  
    	azure_ad_token_provider=token_provider,  
		api_version=api_version,
	)		
	#Prepare the chat prompt 
	chat_prompt = [
		{
			"role": "system",
			"content": [
				{
					"type": "text",
					"text": """ 
					You are a user authenticator that helps users authenticate and validate their identity.
					Interaction goes over voice, so it's *super* important that answers are as short as possible. Use professional language.
					Your tasks are:
					- Detect if the user mention his/her pin in the transcript.
					- If the user mention his/her pin (6789), validate the user.
					- If the user mention any other number, do not validate the user.
					- If the user mention do not mention any number, ask the user to repeat the pin.
					You need to reply with a single line of text in the following format:
					- User is validated.
					- User is not validated.
					- Ask the user to provide the pin.
					"""	
				}
			]
		},
		{
			"role": "user",
			"content": [
				{
					"type": "text",
					"text": transcript
				}
			]
		}
	] 		
	# Include speech result if speech is enabled  
	messages = chat_prompt  	
	# Generate the completion  
	completion = client.chat.completions.create(  
		model=deployment,
		messages=messages,
		max_tokens=100,  
		temperature=0.0,  
		top_p=0.95,  
		frequency_penalty=0,  
		presence_penalty=0,
		stop=None,  
		stream=False
	)
	return completion.choices[0].message.content

def from_file(filename: str):
	# Transcribe the audio file
	credential = DefaultAzureCredential()
	aad_token = credential.get_token("https://cognitiveservices.azure.com/")
	region = os.environ.get("SPEECH_SERVICE_REGION")	
	# You need to include the "aad#" prefix and the "#" (hash) separator between resource ID and Microsoft Entra access token.
	authorization_token = "aad#" + os.environ.get("SPEECH_SERVICE_RESOURCE_ID") + "#" + aad_token.token
	speech_config = speechsdk.SpeechConfig(auth_token=authorization_token, region=region)
	audio_config = speechsdk.AudioConfig(filename=filename)
	speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config, language=os.getenv("SPEECH_LANGUAGE"))
	print(f"Transcript start")
	speech_recognition_result = speech_recognizer.recognize_once_async().get()
	print(speech_recognition_result.text)
	return speech_recognition_result.text


user_authenticator = {
	"id": "Assistant_User_Authenticator",
	"name": "User Authenticator",
	"description": """Call this if:
		- You need to authenticate the user and validate their identity.
  """,
	"system_message": """
    You are a user authenticator that helps users authenticate and validate their identity.
 	Interaction goes over voice, so it's *super* important that answers are as short as possible. Use professional language.
	
	Your tasks are:
	- Authenticate the user and validate their identity using the "authenticate_user" tool.
    
 """,
	"tools": [
		{
			"name": "authenticate_user",
			"description": "Authenticate the user and validate their identity.",
			"parameters": {
				"type": "object",
				"properties": {
				},
			},
			"returns": authenticate_user,
		},
	],
}