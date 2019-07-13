from terrelay.tconnection import TerrariaConnection, TClientConnection, TRelayServer
async def handle(msg, cl:TClientConnection, srv:TRelayServer):
    cmd = msg.split(" ")[0][1:]
    args = msg.split(" ")[1:]

    print("Command: "+msg)

    if cmd in commands:
        return await commands[cmd]['func'](cl,srv,args)

    return False

    # if cmd == "help":
    #     await self.sendchat("Available commands:\n-quit <message> - Kick yourself with the message provided")
    # elif cmd == "quit":
    #     await self.writepkt(b"\x02"+self.prepstr(msg[len(cmd)+1:],2))
    # elif cmd == "debug":
    # else:
    #     await self.sendchat("That is not a valid command!",b"\xff\x33\x33")

commands = {}

def prepstr(s:str,llen:int)->bytes:
    stlen = len(s)
    return stlen.to_bytes(llen,byteorder="big")+bytes(s,"utf-8")

def reg_command(name=None,helpstr="",hidden=False):
    def command(func):
        commands[name or func.__name__] = {"func":func,"help":helpstr,"hidden":hidden}
        return func
    return command

@reg_command(helpstr="help - Show this text.")
async def help(cl:TerrariaConnection,srv:TRelayServer,args:str):
    m = "Available commands:"
    for x in commands:
        if commands[x]['hidden']:
            continue
        m += "\n"+(commands[x]['help'] or x)
    await cl.sendchat(m)
    return True

@reg_command(helpstr="help - Show this text.")
async def reload(cl:TerrariaConnection,srv:TRelayServer,args:str):
    await srv.unload_plugins()
    await srv.load_plugins()
    return True

@reg_command(helpstr="quit <message> - Kicks you with the provided message")
async def quit(cl:TerrariaConnection,srv:TRelayServer,args:str):
    await cl.writepkt(b"\x02"+prepstr(" ".join(args),2))
    return True

@reg_command(helpstr=None)
async def serv1(cl:TerrariaConnection,srv:TRelayServer,args:str):
    await cl.set_server(("10.1.0.199",7777))
    return True

@reg_command(helpstr=None)
async def serv2(cl:TerrariaConnection,srv:TRelayServer,args:str):
    await cl.set_server(("10.1.0.199",7778))
    return True

@reg_command(helpstr=None)
async def rsp(cl:TerrariaConnection,srv:TRelayServer,args:str):
    await cl.respawn()
    return True

@reg_command(helpstr=None,hidden=True)
async def test(cl:TerrariaConnection,srv:TRelayServer,args:str):
    return True