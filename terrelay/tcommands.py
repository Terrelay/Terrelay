from terrelay.tconnection import TerrariaConnection, TClientConnection, TRelayServer, prepstr
async def handle(msg, cl:TClientConnection, srv:TRelayServer):
    cmd = msg.split(" ")[0][1:]
    args = msg.split(" ")[1:]

    print("Command: "+msg)

    if cmd in commands:
        return await commands[cmd]['func'](cl,srv,args)
    return False

commands = {}

def reg_command(name=None,helpstr="",hidden=False):
    def command(func):
        commands[name or func.__name__] = {"func":func,"help":helpstr,"hidden":hidden}
        return func
    return command