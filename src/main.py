import logging
import settings
import jwt
import asyncio
import websockets
import uuid
import time
from rtc_api_client import RtcApiClient
from sfu_api_client import SfuApiClient
from mediasoup_client import MediasoupClient
from aiortc.contrib.media import MediaPlayer, MediaRelay

logging.getLogger().setLevel(logging.INFO)

if not settings.SECRET_KEY:
    raise ValueError("SKYWAY_SECRET_KEY environment variable is not set")

token = jwt.encode(
    {
        "jti": str(uuid.uuid4()),
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "version": 3,
        "scope": {
            "appId": settings.APP_ID,
            "rooms": [
                {
                    "id": "*",
                    "methods": [],
                    "member": {"id": "*", "methods": ["publish"]},
                }
            ],
        },
    },
    settings.SECRET_KEY,
    algorithm="HS256",
)


async def main():
    async with websockets.connect(
        "wss://rtc-api.skyway.ntt.com:443/ws", subprotocols=[token]
    ) as websocket:
        rtc_api_client = RtcApiClient(websocket, token, settings.APP_ID)
        sfu_api_client = SfuApiClient(token, settings.APP_ID)
        channel_id = input("channel_id: ")

        channel = await rtc_api_client.get_channel(channel_id)
        print(channel)

        member = await rtc_api_client.join_channel(channel_id)
        print(member)
        member_id = member["result"]["memberId"]

        await asyncio.sleep(1)

        player = MediaPlayer(
            "default:none",
            format="avfoundation",
            options={"framerate": "30", "video_size": "1280x720"},
        )
        relay = MediaRelay()
        video_track = relay.subscribe(player.video)

        publication = await rtc_api_client.publish_stream(channel_id, member_id)
        print(publication)
        publication_id = publication["result"]["id"]

        bot = await sfu_api_client.create_bot(channel_id)
        print(bot)
        bot_id = bot["id"]

        forwarding = await sfu_api_client.start_forwarding(
            member_id, publication_id, bot_id, "Video", 1
        )

        if "broadcasterTransportId" not in forwarding:
            raise Exception("broadcasterTransportId is not found")

        if "forwardingId" not in forwarding:
            raise Exception("forwardingId is not found")

        mediasoup_client = MediasoupClient(
            sfu_api_client,
            bot_id,
            forwarding["broadcasterTransportId"],
            forwarding["forwardingId"],
        )

        if "rtpCapabilities" in forwarding:
            await mediasoup_client.load(forwarding["rtpCapabilities"])

        if "broadcasterTransportOptions" in forwarding:
            await mediasoup_client.create_send_transport(
                forwarding["broadcasterTransportOptions"]
            )

        async def on_stream_subscribed_callback(data):
            while True:
                await asyncio.sleep(1)
                response = await sfu_api_client.confirm_subscription(
                    forwarding["forwardingId"],
                    data["params"]["data"]["subscription"]["id"],
                    forwarding["identifierKey"],
                )
                if (
                    "message" in response
                    and response["message"] == "IdentifierKey is invalid"
                ):
                    continue
                else:
                    break

        await rtc_api_client.on_stream_subscribed(on_stream_subscribed_callback)

        await mediasoup_client.produce(video_track)

        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
