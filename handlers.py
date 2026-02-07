import json
import os
from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.handlers.message_handler import MessageHandler
from pyrogram.raw.functions.messages import ReadDiscussion
from logger import Logger


async def handleUnreads(client: Client, message: Message):
    if not message.chat or not message.message_thread_id:
        return

    config_file = "bad_topics.json"
    if not os.path.exists(config_file):
        return
        
    try:
        with open(config_file, "r") as f:
            bad_topics = json.load(f)
    except Exception:
        return

    chat_id = str(message.chat.id)
    
    # Check if chat is in config
    if chat_id not in bad_topics:
        return
        
    topic_id = message.message_thread_id
    
    # Check if this specific topic is monitored
    target_topics = bad_topics[chat_id]
    
    # target_topics is a list of ints. topic_id is int.
    if topic_id in target_topics:
        Logger.log(
            f"Auto-reading message in {message.chat.title} (Topic: {topic_id})", 
            Logger.LogLevel.DEBUG
        )
        try:
            peer = await client.resolve_peer(message.chat.id)
            await client.invoke(
                ReadDiscussion(
                    peer=peer,
                    msg_id=topic_id,
                    read_max_id=message.id
                )
            )
        except Exception as e:
            Logger.log(f"Failed to mark as read: {e}", Logger.LogLevel.ERROR)


handlerFunctions = [handleUnreads]
handlersList: list[MessageHandler] = []
for handlerFunction in handlerFunctions:
    handler = MessageHandler(handlerFunction)
    handlersList.append(handler)
