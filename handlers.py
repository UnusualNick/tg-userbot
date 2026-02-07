import os
import json
from typing import Any, Optional, cast, List

from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler, EditedMessageHandler
from pyrogram.raw.functions.messages import ReadDiscussion

from logger import Logger


async def handleUnreads(client: Client, message: Message):
    # Log everything to debug "missing" messages
    # Use generic generic logging to catch cases where .chat might be weird (though unlikely)
    try:
        chat_title = message.chat.title if message.chat else "No Chat"
        chat_id = message.chat.id if message.chat else "No ID"
        Logger.log(
            f"INCOMING: {chat_title} ({chat_id}) | Msg: {message.id} | Type: {message.service if message.service else 'Text'}", 
            Logger.LogLevel.DEBUG
        )
    except Exception as e:
         Logger.log(f"Logger Error: {e}", Logger.LogLevel.ERROR)

    chat = message.chat
    if not chat:
        return

    # Check config FIRST before deciding to return
    config_file = "data/spammy_topics.json"
    if not os.path.exists(config_file):
        return

    try:
        with open(config_file, "r") as f:
            spammy_topics = json.load(f)
    except Exception as e:
        Logger.log(f"Error loading config: {e}", Logger.LogLevel.ERROR)
        return

    chat_id = str(chat.id)
    if chat_id not in spammy_topics:
        # Not a monitored chat, ignore
        # Logger.log(f"Ignoring chat {chat_id} (not in valid list)", Logger.LogLevel.DEBUG)
        return

    target_topics = spammy_topics[chat_id]

    # --- SIMPLIFIED LOGIC: BLIND FIRE ---
    # Iterate through ALL monitored topics for this chat and read them all.
    # This ensures that any activity triggers a cleanup of all "spammy" topics.
    
    if not target_topics:
        return

    Logger.log(f"Activity in {chat.title} - Cleaning {len(target_topics)} topics...", Logger.LogLevel.INFO)
    
    try:
        peer = cast(Any, await client.resolve_peer(chat.id))
        
        for topic_id in target_topics:
            try:
                # We use the incoming message ID as the read_max_id.
                # Since message IDs are global and increasing in a Supergroup, 
                # passing a high ID (like the current one) should mark everything before it as read.
                await client.invoke(
                        ReadDiscussion(
                            peer=peer, 
                            msg_id=topic_id, 
                            read_max_id=message.id
                        )
                    )
            except Exception as e:
                 # Be quiet about individual failures (e.g. topic deleted) but log generic error
                 Logger.log(f"Failed to clear Topic {topic_id}: {e}", Logger.LogLevel.DEBUG)
                 
    except Exception as e:
         Logger.log(f"Error resolving peer or clearing topics: {e}", Logger.LogLevel.ERROR)

    return

handlersList: List[MessageHandler] = [
    MessageHandler(handleUnreads),
    EditedMessageHandler(handleUnreads) 
]
