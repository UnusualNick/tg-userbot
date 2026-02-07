import os
import json
from typing import Any, Optional, cast, List

from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from pyrogram.raw.functions.messages import ReadDiscussion

from logger import Logger


async def handleUnreads(client: Client, message: Message):
    chat = message.chat
    if not chat:
        return

    # Check config FIRST before deciding to return
    config_file = "spammy_topics.json"
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
        return

    target_topics = spammy_topics[chat_id]

    # Now determine topic ID
    # We need to distinguish between:
    # A) A message/reply in a monitored topic (e.g. 56736).
    # B) A message/reply in the General topic (1).
    # C) A message/reply in a NON-monitored topic.
    
    detected_topic_id = None
    is_confirmed_general = False

    # 1. Trust Message Object (if available)
    if getattr(message, "topic", None):
        detected_topic_id = message.topic.id
    
    # 2. Use Link Parsing to strictly identify topic structure
    if detected_topic_id is None and message.link:
        try:
            parts = message.link.split("/")
            # Filter empty strings from split (e.g. initial /)
            parts = [p for p in parts if p]
            
            # Identify parts based on pattern
            # Private: t.me/c/CHAT/TOPIC/MSG (5 parts) or t.me/c/CHAT/MSG (4 parts)
            # Public: t.me/USER/TOPIC/MSG (3 parts) or t.me/USER/MSG (2 parts)
            
            if len(parts) >= 3 and parts[-3] == "c":
                # Private Link structure
                if parts[-2].isdigit() and parts[-1].isdigit():
                    # Check if there is a topic part before these? 
                    # t.me/c/CHAT/TOPIC/MSG -> parts[-2] is TOPIC.
                    # t.me/c/CHAT/MSG -> parts[-2] is CHAT.
                    # This is ambiguous without knowing if parts[-2] is the Chat ID.
                    
                    # We know the chat_id! (though it might be -100... vs positive in link)
                    # chat.id is usually -1001234567890. Link has 1234567890.
                    chat_id_link_format = str(chat.id).replace("-100", "")
                    
                    if parts[-2] == chat_id_link_format:
                        # .../c/CHAT/MSG -> This is Genera/No Topic
                        is_confirmed_general = True
                        detected_topic_id = 1
                    else:
                        # .../c/CHAT/TOPIC/MSG
                        detected_topic_id = int(parts[-2])
                        
            elif len(parts) >= 2:
                # Public Link structure: .../CHATNAME/MSG or .../CHATNAME/TOPIC/MSG
                # parts[-1] is MSG.
                # If parts[-2] is numeric, it is likely TOPIC.
                # If parts[-2] is string, it is likely CHATNAME.
                
                if parts[-2].isdigit():
                    detected_topic_id = int(parts[-2])
                else:
                    is_confirmed_general = True
                    detected_topic_id = 1
                    
        except (ValueError, IndexError):
            pass

    # 3. Use reply_to_top_message_id as a hint
    # If we detected a topic above, checking if it is in target_topics handles it.
    # If we didn't (or we think it's General), we check reply_to_top.
    
    top_id = cast(Optional[int], message.reply_to_top_message_id)
    
    # Final Decision Logic
    topic_to_process = None

    # Determine the "Effective Topic ID"
    # If we are in General (detected_topic_id is 1 or None), 
    # but there is a reply_to_top_message_id, that ID represents a specific thread.
    # Users likely want to manage that thread separately from "General".
    # So if top_id exists, we treat it as the effective topic.
    
    effective_id = None
    
    if is_confirmed_general or detected_topic_id == 1:
        if top_id:
             effective_id = top_id
        else:
             effective_id = 1
    elif detected_topic_id:
        effective_id = detected_topic_id
    elif top_id:
        # Fallback if detection failed completely but we have a top ID
        effective_id = top_id
    
    # Check if effective ID is monitored
    if effective_id and effective_id in target_topics:
        topic_to_process = effective_id
        
    if topic_to_process:
        Logger.log(
            f"Marking as read in {chat.title} (Topic: {topic_to_process})",
            Logger.LogLevel.INFO,
        )
        try:
            # If topic_id is 1 (General), ReadDiscussion might fail or be incorrect.
            # Use standard mark_chat_read behavior for ID 1 / None logic.
            if topic_to_process == 1:
                # Mark the whole chat/general topic as read up to this message
                await client.read_chat_history(chat.id, max_id=message.id)
            else:
                peer = cast(Any, await client.resolve_peer(chat.id))
                await client.invoke(
                    ReadDiscussion(
                        peer=peer, msg_id=topic_to_process, read_max_id=message.id
                    )
                )

        except Exception as e:
            Logger.log(f"Failed to mark as read: {e}", Logger.LogLevel.ERROR)
    else:
        # Debug unpicked messages to understand why they were skipped
         if 1 in target_topics and not is_confirmed_general and not topic_to_process:
             # This is the "False Positive Avoidance" case.
             # We skipped it because we weren't sure it was General.
             # Logger.log(f"SKIPPING ambiguous message {message.id}. Link: {message.link}. Top: {message.reply_to_top_message_id}", Logger.LogLevel.DEBUG)
             pass


# ---------- THIS is what main.py imports ----------

handlersList: List[MessageHandler] = [MessageHandler(handleUnreads)]
