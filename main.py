from pyrogram.client import Client
from pyrogram.sync import idle
from handlers import handlersList
from cleaner import clean_topics
from tui import configure_tui
from args import parse_args
from logger import Logger


def main():
    args = parse_args()

    app = init()

    async def run_cleaner():
        async with app:
            await clean_topics(app)

    async def run_config():
        async with app:
            await configure_tui(app)

    if args.clean_topics:
        app.run(run_cleaner())
    elif args.configure:
        app.run(run_config())
    else:
        workload(app)


def workload(app: Client):
    async def run_bot():
        async with app:
            # await clean_topics(app)
            Logger.log("Userbot started and waiting for updates...", Logger.LogLevel.INFO)
            await idle()

    app.run(run_bot())


def init():
    from dotenv import load_dotenv
    import os
    from conn import Connection

    load_dotenv()
    api_hash = os.getenv("API_HASH") or "API_HASH not found in .env file"
    api_id = int(os.getenv("API_ID") or "API_ID not found in .env file")
    conn = Connection(api_hash, api_id)
    app = conn.connect()
    for handler in handlersList:
        app.add_handler(handler)
    return app


if __name__ == "__main__":
    main()
