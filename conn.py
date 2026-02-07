from pyrogram.client import Client


class Connection:
    def __init__(self, api_hash: str, api_id: int):
        self.api_hash = api_hash
        self.api_id = api_id

    def connect(self):
        return Client("my_account", api_id=self.api_id, api_hash=self.api_hash)
