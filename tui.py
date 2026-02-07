import json
import os
from pyrogram.client import Client
from pyrogram.raw.functions.channels import GetForumTopics
from pyrogram.raw.types import ForumTopic, InputChannel, InputPeerChannel
from pyrogram.types import Chat
from logger import Logger

async def configure_tui(app: Client):
    Logger.log("Starting configuration TUI...")

    # Load existing config
    config_file = "data/spammy_topics.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            try:
                msg_config = json.load(f)
            except json.JSONDecodeError:
                msg_config = {}
    else:
        msg_config = {}

    Logger.log("Fetching dialogs (forums only)...")
    dialogs: list[Chat] = []
    
    # get_dialogs returns an async generator yielding Dialog objects
    from pyrogram.enums import ChatType
    from pyrogram.errors import BadRequest
    
    async for dialog in app.get_dialogs():
        chat = dialog.chat
        
        # Check if chat is a forum.
        # Try safe check first
        is_forum = getattr(chat, "is_forum", False)
        
        if is_forum:
            dialogs.append(chat)
        elif chat.type == ChatType.SUPERGROUP:
            # Fallback for Pyrogram versions where is_forum is not exposed in Chat
            # We list all supergroups. Users can ignore non-forums.
            dialogs.append(chat)
    
    if not dialogs:
        Logger.log("No forum chats found.", Logger.LogLevel.WARNING)
        return

    while True:
        try:
            Logger.log("Available Forums (and Supergroups):")
            for i, d in enumerate(dialogs):
                print(f"{i + 1}. {d.title} (ID: {d.id})")
            print("0. Exit")
            
            choice = input("\nSelect a chat number: ").strip()
            if not choice.isdigit():
                print("Invalid input. Please enter a number.")
                continue
            
            idx = int(choice)
            if idx == 0:
                break
            if idx < 1 or idx > len(dialogs):
                print("Invalid selection.")
                continue
                
            selected_chat = dialogs[idx - 1]
        except (ValueError, IndexError):
            print("Invalid selection.")
            continue

        Logger.log(f"Fetching topics for {selected_chat.title}...")
        
        try:
            peer = await app.resolve_peer(selected_chat.id)
            input_channel = peer
            if isinstance(peer, InputPeerChannel):
                input_channel = InputChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)

            # Fetch topics (limit 100 for TUI simplicity)
            topics_result = await app.invoke(
                GetForumTopics(
                    channel=input_channel,
                    offset_date=0,
                    offset_id=0,
                    offset_topic=0,
                    limit=100
                )
            )
            
            topics: list[ForumTopic] = []
            if hasattr(topics_result, 'topics'):
                for t in topics_result.topics:
                    if isinstance(t, ForumTopic):
                        topics.append(t)
            
            if not topics:
                Logger.log("No topics found in this chat.", Logger.LogLevel.WARNING)
                continue

            existing_ids = set(msg_config.get(str(selected_chat.id), []))
            
            while True:
                # Use print for menu items to avoid cluttering with log prefixes
                print(f"\nTopics in {selected_chat.title}:")
                # Map simple index to topic
                topic_map = {}
                
                for i, t in enumerate(topics):
                    status = "[x]" if t.id in existing_ids else "[ ]"
                    print(f"{i + 1}. {status} {t.title} (ID: {t.id})")
                    topic_map[i + 1] = t
                
                print("\nEnter topic numbers to toggle (separated by space), 'a' for all, 'n' for none, or 'q' to go back.")
                cmd = input("Command: ").strip().lower()
                
                if cmd == 'q':
                    break
                
                if cmd == 'a':
                    for t in topics:
                        existing_ids.add(t.id)
                elif cmd == 'n':
                    existing_ids.clear()
                else:
                    parts = cmd.split()
                    for part in parts:
                        if part.isdigit():
                            t_idx = int(part)
                            if t_idx in topic_map:
                                t = topic_map[t_idx]
                                if t.id in existing_ids:
                                    existing_ids.remove(t.id)
                                else:
                                    existing_ids.add(t.id)
                        else:
                            Logger.log(f"Skipping invalid input: {part}", Logger.LogLevel.WARNING)

                # Save immediately
                msg_config[str(selected_chat.id)] = list(existing_ids)
                with open(config_file, "w") as f:
                    json.dump(msg_config, f, indent=4)
                Logger.log("Configuration saved.")

        except BadRequest as e:
            if "CHANNEL_FORUM_MISSING" in str(e):
                Logger.log(f"Error: '{selected_chat.title}' is not a Forum (Topics are not enabled).", Logger.LogLevel.ERROR)
            else:
                 Logger.log(f"Telegram BadRequest: {e}", Logger.LogLevel.ERROR)
        except Exception as e:
            Logger.log(f"Error accessing chat {selected_chat.title}: {e}", Logger.LogLevel.ERROR)
            import traceback
            traceback.print_exc()
            
    Logger.log("Configuration finished.")


