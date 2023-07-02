import {
    SkyWayAuthToken,
    uuidV4,
    nowInSec,
    SkyWayContext,
    SkyWayChannel,
    Channel,
    LocalPerson,
    SkyWayStreamFactory,
    LocalVideoStream,
    Publication,
    AuthToken,
    RemoteVideoStream,
    Subscription,
} from "@skyway-sdk/core";
import { SfuBotMember, SfuBotPlugin } from "@skyway-sdk/sfu-bot";

const appId = process.env.SKYWAY_APP_ID ?? "";
const secretKey = process.env.SKYWAY_SECRET_KEY ?? "";

const tokenObject: AuthToken = {
    jti: uuidV4(),
    iat: nowInSec(),
    exp: nowInSec() + 60 * 60 * 24,
    scope: {
        app: {
            id: appId,
            turn: true,
            actions: ["read"],
            channels: [
                {
                    id: "*",
                    name: "*",
                    actions: ["write"],
                    members: [
                        {
                            id: "*",
                            name: "*",
                            actions: ["write"],
                            publication: {
                                actions: ["write"],
                            },
                            subscription: {
                                actions: ["write"],
                            },
                        },
                    ],
                    sfuBots: [
                        {
                            actions: ["write"],
                            forwardings: [
                                {
                                    actions: ["write"],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    },
};

(async () => {
    const startButton = <HTMLButtonElement>(
        document.getElementById("start-button")
    );
    const createChannelButton = <HTMLButtonElement>(
        document.getElementById("create-channel-button")
    );
    const channelIdText = <HTMLInputElement>(
        document.getElementById("channel-id-text")
    );
    const findChannelButton = <HTMLButtonElement>(
        document.getElementById("find-channel-button")
    );
    const joinChannelButton = <HTMLButtonElement>(
        document.getElementById("join-channel-button")
    );
    const publishMediaButton = <HTMLButtonElement>(
        document.getElementById("publish-media-button")
    );
    const createBotButton = <HTMLButtonElement>(
        document.getElementById("create-bot-button")
    );
    const botIdText = <HTMLInputElement>document.getElementById("bot-id-text");
    const deleteBotButton = <HTMLButtonElement>(
        document.getElementById("delete-bot-button")
    );
    const forwardingMediaButton = <HTMLButtonElement>(
        document.getElementById("forwarding-media-button")
    );
    const getAllPublicationsButton = <HTMLButtonElement>(
        document.getElementById("get-all-publications-button")
    );
    const publicationIdText = <HTMLInputElement>(
        document.getElementById("publication-id-text")
    );
    const subscribeMediaButton = <HTMLButtonElement>(
        document.getElementById("subscribe-media-button")
    );
    const subscribeHighButton = <HTMLButtonElement>(
        document.getElementById("subscribe-high-button")
    );
    const subscribeMidButton = <HTMLButtonElement>(
        document.getElementById("subscribe-mid-button")
    );
    const subscribeLowButton = <HTMLButtonElement>(
        document.getElementById("subscribe-low-button")
    );

    const terminateButton = <HTMLButtonElement>(
        document.getElementById("terminate-button")
    );
    const remoteVideo = <HTMLVideoElement>(
        document.getElementById("remote-video")
    );
    const channelNameText = <HTMLInputElement>(
        document.getElementById("channel-name-text")
    );
    const tokenChannelScopeText = <HTMLTextAreaElement>(
        document.getElementById("token-channel-scope-text")
    );
    tokenChannelScopeText.value = JSON.stringify(
        tokenObject.scope.app.channels,
        null,
        2
    );
    const updateTokenButton = <HTMLButtonElement>(
        document.getElementById("update-token-button")
    );

    const attachHandlers = (channel: Channel) => {
        channel.onMemberJoined.add(({ member }) => {
            console.info(`${member.id} joined, ${member.name}`);
        });
        channel.onMemberLeft.add(({ member }) => {
            console.info(`${member.id} left, ${member.name}`);
        });
        channel.onStreamPublished.add(({ publication }) => {
            console.info(
                `${publication.id} published, ${publication.contentType}, ${publication.publisher.type}`
            );
        });
    };

    let context: SkyWayContext;
    let plugin: SfuBotPlugin;
    startButton.addEventListener("click", async () => {
        const token = new SkyWayAuthToken({
            jti: uuidV4(),
            iat: nowInSec(),
            exp: nowInSec() + 60 * 60 * 24,
            scope: {
                app: {
                    id: appId,
                    turn: true,
                    actions: ["read"],
                    channels: JSON.parse(tokenChannelScopeText.value),
                },
            },
        }).encode(secretKey);

        context = await SkyWayContext.Create(token, {
            log: {
                level: "info",
                format: "string",
            },
        });
        plugin = new SfuBotPlugin();
        context.registerPlugin(plugin);
    });

    let channel: Channel;
    let me: LocalPerson;
    let publication: Publication<LocalVideoStream>;
    let bot: SfuBotMember;
    let subscription: {
        subscription: Subscription<RemoteVideoStream>;
        stream: RemoteVideoStream;
    };
    createChannelButton.addEventListener("click", async () => {
        channel = await SkyWayChannel.Create(
            context,
            channelNameText.value !== ""
                ? {
                      name: channelNameText.value,
                  }
                : undefined
        );
        console.info("channel", channel);
        channelIdText.value = channel.id;
        attachHandlers(channel);
    });
    findChannelButton.addEventListener("click", async () => {
        channel = await SkyWayChannel.Find(context, {
            id: channelIdText.value,
        });
        attachHandlers(channel);
    });
    joinChannelButton.addEventListener("click", async () => {
        me = await channel.join();
        console.info(`My ID: ${me.id}`);
    });

    publishMediaButton.addEventListener("click", async () => {
        const video = await SkyWayStreamFactory.createCameraVideoStream();
        publication = await me.publish(video, {
            encodings: [
                { scaleResolutionDownBy: 1, id: "high", maxBitrate: 1000000 },
                { scaleResolutionDownBy: 4, id: "mid", maxBitrate: 100000 },
                { scaleResolutionDownBy: 8, id: "low", maxBitrate: 10000 },
            ],
        });
        console.log(`${publication.id} published`);
    });

    createBotButton.addEventListener("click", async () => {
        bot = await plugin.createBot(channel);
        console.info(`Bot ID: ${bot.id}`);
        botIdText.value = bot.id;
    });

    deleteBotButton.addEventListener("click", async () => {
        await plugin.deleteBot(channel, botIdText.value);
    });

    forwardingMediaButton.addEventListener("click", async () => {
        const forwarding = await bot.startForwarding(publication, {
            maxSubscribers: 2,
        });
        console.log(`${forwarding.id} forwarding`);
    });

    getAllPublicationsButton.addEventListener("click", async () => {
        channel.publications.forEach((publication) => {
            console.log(
                `${publication.id} ${publication.contentType} ${publication.publisher.type}`
            );
        });
    });

    subscribeMediaButton.addEventListener("click", async () => {
        const publication = channel.publications.find(
            (publication) => publication.id === publicationIdText.value
        );
        if (!publication) {
            console.error("publication not found");
            return;
        }
        subscription = await me.subscribe<RemoteVideoStream>(publication, {
            preferredEncodingId: "mid",
        });
        console.log(`${subscription} subscribed`);
        const { stream } = subscription;
        if (stream.contentType === "video") {
            stream.attach(remoteVideo);
        }
    });

    subscribeHighButton.addEventListener("click", async () => {
        subscription.subscription.changePreferredEncoding("high");
    });

    subscribeMidButton.addEventListener("click", async () => {
        subscription.subscription.changePreferredEncoding("mid");
    });

    subscribeLowButton.addEventListener("click", async () => {
        subscription.subscription.changePreferredEncoding("low");
    });

    terminateButton.addEventListener("click", async () => {
        await channel.close();
        await context.dispose();
    });

    updateTokenButton.addEventListener("click", async () => {
        const token = new SkyWayAuthToken({
            jti: uuidV4(),
            iat: nowInSec(),
            exp: nowInSec() + 60 * 60 * 24,
            scope: {
                app: {
                    id: appId,
                    turn: true,
                    actions: ["read"],
                    channels: JSON.parse(tokenChannelScopeText.value),
                },
            },
        }).encode(secretKey);
        await context.updateAuthToken(token);
    });
})();
