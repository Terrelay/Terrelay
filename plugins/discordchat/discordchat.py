from __future__ import annotations
from terrelay.tconnection import TPlugin, TClientConnection, TRelayServer
from plugins.discordchat.creds import clienttkn
import asyncio
import discord

class DiscordClient(discord.Client):
    def __init__(self,plg):
        discord.Client.__init__(self)
        self.plg = plg
    async def on_ready(self):
        print('Logged on as', self.user)
    async def on_message(self,message):
        await self.plg.on_discord_message(message)

class DiscordChat(TPlugin):
    async def on_discord_message(self,message):
        if message.channel.id != 599404562926796800:
            return
        if message.author == self.discord.user:
            return
        if len(message.content) == 0:
            return
        tmsg = "[Discord] "+message.author.name+": "+message.content[:200]
        await self.srv.broadcastChat(None,message=tmsg,color=b"\x5e\xa2\xe6")

    async def on_plugin_load(self,srv:TRelayServer):
        print("Loaded DiscordChat")
        self.discord = DiscordClient(self)
        self.srv = srv
        asyncio.create_task(self.discord.start(clienttkn))

    async def on_plugin_unload(self,srv:TRelayServer):
        await self.discord.logout()

    async def on_chat_message(self,srv:TRelayServer,cl:TClientConnection,msg:str,emote:bool):
        await self.discord.get_channel(599404562926796800).send(("*"+cl.name+" "+msg+"*" if emote else "<"+cl.name+"> "+msg))

    async def on_connection(self,srv:TRelayServer,cl:TClientConnection):
        pass
    async def on_server_join(self,srv:TRelayServer,cl:TClientConnection,server:str):
        pass
    async def on_server_leave(self,srv:TRelayServer,cl:TClientConnection,server:str):
        pass
    async def on_disconnect(self,srv:TRelayServer,cl:TClientConnection):
        pass