from __future__ import annotations
from terrelay.tconnection import TClientConnection, TRelayServer, prepstr
# this file re-creates the chat netmodule's commands, so that i dont have to pass them through to the server to get them.

async def EmoteCommand(srv:TRelayServer,cl:TClientConnection,msg:str):
    await srv.broadcastChat(cl,message="*"+cl.name+" "+msg,color=b"\x94\x4a\x00")

async def PlayingCommand(srv:TRelayServer,cl:TClientConnection,msg:str):
    msg = "Currently on the network: "+",".join([x.name for x in srv.conns])
    msg += "\nOn the same server as you: "+",".join([x.name for x in srv.conns if cl.cur_server == x.cur_server])
    await cl.sendchat(msg)

async def RollCommand(srv:TRelayServer,cl:TClientConnection,msg:str):
    from random import randint
    await srv.broadcastChat(cl,message=cl.name+" has rolled a "+str(randint(0,100))+".",sendall=False)

async def SayCommand(srv:TRelayServer,cl:TClientConnection,msg:str):
    await srv.broadcastChat(cl,author=cl,message=msg)

async def PartyCommand(srv:TRelayServer,cl:TClientConnection,msg:str):
    await cl.prcon.writepkt(b"\x52\x01\x00"+prepstr("Party")+prepstr(msg)) # hacks!

chatcommands = {
    "Emote": EmoteCommand,
    "Roll": RollCommand,
    "Say": SayCommand,
    "Party": PartyCommand,
    "Playing": PlayingCommand
}