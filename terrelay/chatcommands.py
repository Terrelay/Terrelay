from terrelay.tconnection import TClientConnection, TRelayServer, prepstr
# this file re-creates the chat netmodule's commands, so that i dont have to pass them through to the server to get them.

async def EmoteCommand(srv,cl,msg:str):
    await srv.broadcastChat(cl,message="*"+cl.name+" "+msg,color=b"\x94\x4a\x00")

async def PlayingCommand(srv,cl,msg:str):
    msg = "Currently on the network: "+",".join([x.name for x in srv.conns])
    msg += "\nOn the same server as you: "+",".join([x.name for x in srv.conns if cl.cur_server == x.cur_server])
    await cl.sendchat(msg)

async def RollCommand(srv,cl,msg:str):
    from random import randint
    await srv.broadcastChat(cl,message=cl.name+" has rolled a "+str(randint(0,100))+".",sendall=False)

async def SayCommand(srv,cl,msg:str)
    print(msg)
    if msg[0] != "/":
        await srv.broadcastChat(cl,author=cl,message=msg)
    else:
        await cl.prcon.writepkt(b"\x52\x01\x00"+prepstr("Say")+prepstr(msg)) # hacks!

async def PartyCommand(srv,cl,msg:str):
    await cl.prcon.writepkt(b"\x52\x01\x00"+prepstr("Party")+prepstr(msg)) # hacks!

chatcommands = {
    "Emote": EmoteCommand,
    "Roll": RollCommand,
    "Say": SayCommand,
    "Party": PartyCommand,
    "Playing": PlayingCommand
}