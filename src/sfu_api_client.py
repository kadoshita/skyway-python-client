import json
import aiohttp
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

API_URL = "https://sfu.skyway.ntt.com/v3"

def print_json(data):
    formatted_data = json.dumps(data, indent=2)
    print(highlight(formatted_data, JsonLexer(), TerminalFormatter()))


class SfuApiClient:
    def __init__(self, token, app_id) -> None:
        self.session = aiohttp.ClientSession()
        self.token = token
        self.app_id = app_id

    async def create_bot(self, channel_id):
        async with self.session.post(
            API_URL + "/bots",
            json={"appId": self.app_id, "channelId": channel_id},
            headers={
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
            },
        ) as response:
            data = await response.json()
            print_json(data)
            return data

    async def start_forwarding(
        self,
        publisher_id,
        publication_id,
        bot_id,
        content_type,
        max_subscribers,
    ):
        async with self.session.post(
            API_URL + "/bots/" + bot_id + "/forwardings",
            json={
                "publicationId": publication_id,
                "maxSubscribers": max_subscribers,
                "contentType": content_type,
                "publisherId": publisher_id,
            },
            headers={
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
            },
        ) as response:
            data = await response.json()
            print_json(data)
            return data

    async def connect(self, transport_id, dtls_parameters):
        pass

    async def create_producer(self, transport_id, producer_options):
        pass