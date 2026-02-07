import json
import os
from pyrogram.client import Client
from pyrogram.raw.functions.channels import GetForumTopics
from pyrogram.raw.functions.messages import ReadDiscussion
from pyrogram.raw.types import ForumTopic, InputPeerChannel, InputChannel
from logger import Logger


async def clean_topics(app: Client):
    Logger.log("Starting topic cleaner...")

    # Load spammy topics
    if not os.path.exists("spammy_topics.json"):
        Logger.log("spammy_topics.json not found.", Logger.LogLevel.WARNING)
        return

    with open("spammy_topics.json", "r") as f:
        try:
            spammy_topics_config = json.load(f)
        except json.JSONDecodeError:
            Logger.log("Invalid JSON in spammy_topics.json", Logger.LogLevel.ERROR)
            return

    # No need for 'with app:' block here if we run this via app.run(clean_topics(app))
    # as app.run() handles the context.
    # However, if we pass the coroutine to app.run(), app.run() will start it.
    
    for chat_id_str, topic_ids in spammy_topics_config.items():
        try:
            chat_id = int(chat_id_str)
        except ValueError:
            Logger.log(f"Invalid chat_id: {chat_id_str}", Logger.LogLevel.WARNING)
            continue

        Logger.log(f"Checking chat {chat_id}...", Logger.LogLevel.DEBUG)

        try:
            peer = await app.resolve_peer(chat_id)
            if not peer:
                Logger.log(f"Could not resolve peer for {chat_id}", Logger.LogLevel.ERROR)
                continue

            input_channel = peer
            if isinstance(peer, InputPeerChannel):
                input_channel = InputChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)

            # Fetch topics
            topics_result = await app.invoke(
                GetForumTopics(
                    channel=input_channel,
                    offset_date=0,
                    offset_id=0,
                    offset_topic=0,
                    limit=100
                )
            )

            for topic in topics_result.topics:
                if isinstance(topic, ForumTopic):
                    if topic.id in topic_ids:
                        Logger.log(f"Found bad topic {topic.id} ({topic.title})", Logger.LogLevel.DEBUG)
                        if topic.unread_count > 0:
                            Logger.log(f"  Marking as read (unread: {topic.unread_count})")
                            await app.invoke(
                                ReadDiscussion(
                                    peer=peer,
                                    msg_id=topic.id,
                                    read_max_id=topic.top_message
                                )
                            )
                        else:
                            Logger.log("  Already read.", Logger.LogLevel.DEBUG)

        except Exception as e:
            Logger.log(f"Error processing chat {chat_id}: {e}", Logger.LogLevel.ERROR)

    Logger.log("Topic cleaner finished.")

