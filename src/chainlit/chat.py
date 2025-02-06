import chainlit as cl
from uuid import uuid4
from chainlit.logger import logger

from realtime2 import RealtimeClient
    
from agents.root import root_assistant
from agents.sop_agent import sop_agent
from agents.lab_agent import lab_agent
from agents.assistant_agent import assistant_agent
from agents.web_search_agent import web_search_agent

async def setup_openai_realtime():
    """Instantiate and configure the OpenAI Realtime Client"""
             
    openai_realtime = RealtimeClient(system_prompt = "")
    cl.user_session.set("track_id", str(uuid4()))
    async def handle_conversation_updated(event):
        item = event.get("item")
        delta = event.get("delta")
        """Currently used to stream audio back to the client."""
        if event:
            # print(f"Event {event}")
            if "input_audio_transcription" in item["type"]:
                msg = cl.Message(content=delta["transcript"], author="user")
                msg.type = "user_message"
                await msg.send()
        if delta:
            # Only one of the following will be populated for any given event
            if 'audio' in delta:
                audio = delta['audio']  # Int16Array, audio added
                await cl.context.emitter.send_audio_chunk(cl.OutputAudioChunk(mimeType="pcm16", data=audio, track=cl.user_session.get("track_id")))
            if 'transcript' in delta:
                transcript = delta['transcript']  # string, transcript added
                pass
            if 'arguments' in delta:
                arguments = delta['arguments']  # string, function arguments added
                pass
            
    async def handle_item_completed(item):
        """Used to populate the chat context with transcription once an item is completed."""
        if item["item"]["type"] == "message":
                
            content = item["item"]["content"][0]
            
            if item["item"]["content"][0]["type"] == "input_audio":
                logger.info(f"----------------------------------------")
                logger.info(f"Here to be transcription")
                
            if content["type"] == "audio":
                await cl.Message(content=content["transcript"]).send()
    
    async def handle_conversation_interrupt(event):
        """Used to cancel the client previous audio playback."""
        cl.user_session.set("track_id", str(uuid4()))
        # NOTE this will only work starting from version 2.0.0
        await cl.context.emitter.send_audio_interrupt()
        
    async def handle_error(event):
        logger.error(event)
        
    
    openai_realtime.on('conversation.updated', handle_conversation_updated)
    openai_realtime.on('conversation.item.completed', handle_item_completed)
    openai_realtime.on('conversation.interrupted', handle_conversation_interrupt)
    openai_realtime.on('error', handle_error)
    
    cl.user_session.set("openai_realtime", openai_realtime)
    
    # Agents must be registered before the root agent
    openai_realtime.assistant.register_agent(web_search_agent)
    openai_realtime.assistant.register_agent(sop_agent)
    openai_realtime.assistant.register_agent(lab_agent)
    openai_realtime.assistant.register_agent(assistant_agent)
    # This method must be called last, as it will ensure every agent knows each other plus the path to the root agent
    openai_realtime.assistant.register_root_agent(root_assistant)
    

@cl.on_chat_start
async def start():
    # res = await cl.AskUserMessage(content="What is your name?", timeout=30).send()
    await setup_openai_realtime()

@cl.on_message
async def on_message(message: cl.Message):
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime and openai_realtime.is_connected():
        await openai_realtime.send_user_message_content([{ "type": 'input_text', "text": message.content}])
    else:
        await cl.Message(content="Please activate voice mode before sending messages!").send()

@cl.on_audio_start
async def on_audio_start():
    try:
        openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
        # TODO: might want to recreate items to restore context
        # openai_realtime.create_conversation_item(item)
        await openai_realtime.connect()
        logger.info("Connected to OpenAI realtime")
        return True
    except Exception as e:
        await cl.ErrorMessage(content=f"Failed to connect to OpenAI realtime: {e}").send()
        return False

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime:            
        if openai_realtime.is_connected():
            await openai_realtime.append_input_audio(chunk.data)
        else:
            logger.info("RealtimeClient is not connected")

@cl.on_audio_end
@cl.on_chat_end
@cl.on_stop
async def on_end():
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime and openai_realtime.is_connected():
        await openai_realtime.disconnect()