import settings
import jwt
import asyncio
import websockets
import uuid
import time
from rtc_api_client import RtcApiClient
from sfu_api_client import SfuApiClient

token = jwt.encode(
    {
        "jti": str(uuid.uuid4()),
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "scope": {
            "app": {
                "id": settings.APP_ID,
                "turn": True,
                "actions": ["read"],
                "channels": [
                    {
                        "id": "*",
                        "name": "*",
                        "actions": ["write"],
                        "members": [
                            {
                                "id": "*",
                                "name": "*",
                                "actions": ["write"],
                                "publication": {"actions": ["write"]},
                                "subscription": {"actions": ["write"]},
                            }
                        ],
                        "sfuBots": [
                            {
                                "actions": ["write"],
                                "forwardings": [{"actions": ["write"]}],
                            }
                        ],
                    }
                ],
            }
        },
    },
    settings.SECRET_KEY,
    algorithm="HS256",
)


async def main():
    async with websockets.connect(
        "wss://rtc-api.skyway.ntt.com:443/ws", subprotocols=[token]
    ) as websocket:
        rtcApiClient = RtcApiClient(websocket, token, settings.APP_ID)
        sfuApiClient = SfuApiClient(token, settings.APP_ID)
        channel_id = input("channel_id: ")

        channel = await rtcApiClient.get_channel(channel_id)
        print(channel)

        member = await rtcApiClient.join_channel(channel_id)
        print(member)
        member_id = member["result"]["memberId"]

        await asyncio.sleep(1)

        publication = await rtcApiClient.publish_stream(channel_id, member_id)
        print(publication)
        publication_id = publication["result"]["id"]

        bot = await sfuApiClient.create_bot(channel_id)
        print(bot)
        bot_id = bot["id"]

        forwarding = await sfuApiClient.start_forwarding(
            member_id, publication_id, bot_id, "Video", 1
        )
        print(forwarding)

        await asyncio.sleep(100)


if __name__ == "__main__":
    asyncio.run(main())
