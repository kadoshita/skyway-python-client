import asyncio
import uuid
import json
import time
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


def print_json(message):
    data = json.loads(message)
    formatted_data = json.dumps(data, indent=2)
    print(highlight(formatted_data, JsonLexer(), TerminalFormatter()))
    return data


class RtcApiClient:
    def __init__(self, socket, token, app_id):
        self.socket = socket
        self.token = token
        self.app_id = app_id
        self.events = {}
        asyncio.Task(self.__message_handler())

    async def __message_handler(self):
        while True:
            message = await self.socket.recv()
            data = print_json(message)
            if "id" in data:
                id = data["id"]
                if id in self.events:
                    self.events[id](data)

    async def __send_update_member_ttl(self, channel_id, member_id):
        await self.socket.send(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "updateMemberTtl",
                    "params": {
                        "appId": self.app_id,
                        "channelId": channel_id,
                        "memberId": member_id,
                        "ttlSec": int(time.time()) + 30,
                        "authToken": self.token,
                    },
                    "id": str(uuid.uuid4()),
                }
            )
        )
        print("send_update_member_ttl")

    async def __update_member_ttl(self, channel_id, member_id):
        await self.__send_update_member_ttl(channel_id, member_id)
        while True:
            await asyncio.sleep(20)
            await self.__send_update_member_ttl(channel_id, member_id)

    async def get_channel(self, channel_id):
        future = asyncio.Future()
        id = str(uuid.uuid4())
        print(f"get_channel: {id}")
        await self.socket.send(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "getChannel",
                    "params": {
                        "id": channel_id,
                        "appId": self.app_id,
                        "authToken": self.token,
                    },
                    "id": id,
                }
            )
        )

        def callback(data):
            future.set_result(data)

        self.events[id] = callback

        await future
        del self.events[id]
        return future.result()

    async def join_channel(self, channel_id):
        future = asyncio.Future()
        id = str(uuid.uuid4())
        print(f"join_channel: {id}")
        await self.socket.send(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "addMember",
                    "params": {
                        "channelId": channel_id,
                        "name": f"skyway-python-client-{str(uuid.uuid4())}",
                        "appId": self.app_id,
                        "ttlSec": int(time.time()) + 30,
                        "authToken": self.token,
                        "subtype": "Person",
                        "type": "Person",
                    },
                    "id": id,
                }
            )
        )

        def callback(data):
            if "result" in data:
                member_id = data["result"]["memberId"]
                asyncio.Task(self.__update_member_ttl(channel_id, member_id))
            future.set_result(data)

        self.events[id] = callback

        await future
        del self.events[id]
        return future.result()

    async def publish_stream(self, channel_id, publisher_id):
        future = asyncio.Future()
        id = str(uuid.uuid4())
        print(f"publish_stream: {id}")
        await self.socket.send(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "publishStream",
                    "params": {
                        "channelId": channel_id,
                        "publisherId": publisher_id,
                        "contentType": "Video",
                        "codecCapabilities": [{"mimeType": "video/vp8"}],
                        "appId": self.app_id,
                        "authToken": self.token,
                    },
                    "id": id,
                }
            )
        )

        def callback(data):
            future.set_result(data)

        self.events[id] = callback

        await future
        del self.events[id]
        return future.result()
