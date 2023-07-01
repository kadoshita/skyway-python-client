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
} from "@skyway-sdk/core";
import { SfuBotMember, SfuBotPlugin } from "@skyway-sdk/sfu-bot";

const appId = process.env.SKYWAY_APP_ID ?? "";
const secretKey = process.env.SKYWAY_SECRET_KEY ?? "";

const token = new SkyWayAuthToken({
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
}).encode(secretKey);

(async () => {
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
    const terminateButton = <HTMLButtonElement>(
        document.getElementById("terminate-button")
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
                `${publication.id} published, ${publication.contentType}, ${publication.publisher.id}`
            );
        });
    };

    const context = await SkyWayContext.Create(token);
    const plugin = new SfuBotPlugin();
    context.registerPlugin(plugin);

    let channel: Channel;
    let me: LocalPerson;
    let publication: Publication<LocalVideoStream>;
    let bot: SfuBotMember;
    createChannelButton.addEventListener("click", async () => {
        channel = await SkyWayChannel.Create(context);
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
        publication = await me.publish(video);
        console.log(`${publication.id} published`);
    });

    createBotButton.addEventListener("click", async () => {
        bot = await plugin.createBot(channel);
        console.info(`Bot ID: ${bot.id}`);
    });

    forwardingMediaButton.addEventListener("click", async () => {
        const forwarding = await bot.startForwarding(publication, {
            maxSubscribers: 2,
        });
        console.log(`${forwarding.id} forwarding`);
    });

    terminateButton.addEventListener("click", async () => {
        await channel.close();
        await context.dispose();
    });
})();
