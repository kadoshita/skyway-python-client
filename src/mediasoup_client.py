from pymediasoup import Device
from pymediasoup import AiortcHandler


class MediasoupClient:
    def __init__(
        self, sfu_api_client, bot_id, broadcaster_transport_id, transport_id
    ) -> None:
        self._sfu_api_client = sfu_api_client
        self._bot_id = bot_id
        self._broadcaster_transport_id = broadcaster_transport_id
        self._transport_id = transport_id
        self._device = Device(handlerFactory=AiortcHandler.createFactory())
        self._send_transport = None
        self._receive_transport = None
        self._producer = None
        pass

    async def load(self, rtp_capabilities):
        await self._device.load(rtp_capabilities)

    async def create_send_transport(self, broadcaster_transport_options):
        self._send_transport = self._device.createSendTransport(
            id=broadcaster_transport_options["id"],
            iceParameters=broadcaster_transport_options["iceParameters"],
            iceCandidates=broadcaster_transport_options["iceCandidates"],
            dtlsParameters=broadcaster_transport_options["dtlsParameters"],
            sctpParameters=broadcaster_transport_options["sctpParameters"],
        )

        @self._send_transport.on("connect")
        async def on_connect(dtls_parameters):
            print("send_transport connect")
            await self._sfu_api_client.connect(
                self._broadcaster_transport_id, dtls_parameters.dict(exclude_none=True)
            )

        @self._send_transport.on("produce")
        async def on_produce(kind, rtp_parameters, app_data):
            producer = await self._sfu_api_client.create_producer(
                self._bot_id,
                self._broadcaster_transport_id,
                self._transport_id,
                {
                    "kind": kind,
                    "rtpParameters": rtp_parameters.dict(exclude_none=True),
                    "appData": app_data,
                },
            )
            return producer["producerId"]

    async def create_recv_transport(self, transport_id, transport_options):
        self._receive_transport = self._device.createRecvTransport(
            id=transport_id,
            iceParameters=transport_options["iceParameters"],
            iceCandidates=transport_options["iceCandidates"],
            dtlsParameters=transport_options["dtlsParameters"],
            sctpParameters=transport_options["sctpParameters"],
        )

        @self._receive_transport.on("connect")
        async def on_connect(dtls_parameters):
            await self._sfu_api_client.connect(
                transport_id, dtls_parameters.dict(exclude_none=True)
            )

    async def produce(self, video_track):
        self._producer = await self._send_transport.produce(
            track=video_track,
            stopTracks=False,
            appData={},
        )
