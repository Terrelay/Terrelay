#from __future__ import annotations
from terrelay.tconnection import TPlugin, TClientConnection, TRelayServer, prepstr
from terrelay.tcommands import reg_command, commands
from settings import default_hub

@reg_command(helpstr="help - Show this text.")
async def help(cl:TClientConnection,srv:TRelayServer,args):
    await cl.sendchat("Available commands:",color=b"\xff\xff\x00")
    for x in commands:
        if commands[x]['hidden']:
            continue
        await cl.sendchat(commands[x]['help'] or x,color=b"\xff\xff\x00")
    return True

@reg_command(helpstr="reload - Reloads all server plugins.")
async def reload(cl:TClientConnection,srv:TRelayServer,args):
    await srv.unload_plugins()
    await srv.load_plugins()
    return True

@reg_command(helpstr="quit <message> - Kicks you with the provided message")
async def quit(cl:TClientConnection,srv:TRelayServer,args):
    await cl.writepkt(b"\x02"+prepstr(" ".join(args)))
    return True

@reg_command(helpstr=None)
async def hub(cl:TClientConnection,srv:TRelayServer,args):
    await cl.set_server(default_hub)
    return True

@reg_command(helpstr=None)
async def rsp(cl:TClientConnection,srv:TRelayServer,args):
    await cl.respawn()
    return True

@reg_command(helpstr=None,hidden=True)
async def test(cl:TClientConnection,srv:TRelayServer,args):
    return True
