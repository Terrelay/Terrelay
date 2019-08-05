from typing import List
import asyncio
import struct
import os
import importlib
import inspect
import traceback
from settings import default_hub

def prepstr(s:str)->bytes:
    stlen = len(s)
    lenbytes = b""
    while stlen>=128:
        cb = (stlen&0x7f)|0x80
        lenbytes += cb.to_bytes(1,byteorder="little")
        stlen>>=7
    lenbytes += stlen.to_bytes(1,byteorder="little")
    return lenbytes+bytes(s,"utf-8")

def parsestr(pkt):
    curb = pkt[0]
    i=slen=l=0
    lenbytes = []
    while curb&0x80 == 0x80:
        i+=1
        lenbytes.append(curb & 0x7F)
        curb = pkt[i]
    lenbytes.append(curb & 0x7F)
    for x in lenbytes:
        slen+=x<<7*l
        l+=1
    s = pkt[i+1:i+1+slen]
    return (i+1+len(s),s.decode("utf-8"))

class TPlugin:
    async def on_plugin_load(self,srv):
        pass
    async def on_plugin_unload(self,srv):
        pass
    async def on_chat_message(self,srv,cl,msg:str,emote:bool):
        pass
    async def on_connection(self,srv,cl):
        pass
    async def on_server_join(self,srv,cl,server:str):
        pass
    async def on_server_leave(self,srv,cl,server:str):
        pass
    async def on_disconnect(self,srv,cl):
        pass

def get_plugins(d="plugins")->List[TPlugin]:
    plugins = []
    for x in os.scandir(d):
        if x.is_dir():
            plugins += get_plugins(d+os.sep+x.name)
        else:
            if x.name[-3:] == ".py":
                pl = importlib.import_module(d.replace(os.sep,".")+"."+x.name[:-3])
                importlib.reload(pl)
                for y in dir(pl):
                    yv = getattr(pl,y) 
                    if inspect.isclass(yv) and issubclass(yv,TPlugin) and yv is not TPlugin:
                        plugins.append(yv)
    return plugins

class TRelayServer:
    def __init__(self,listen_addr,loop=None):
        self.host = listen_addr[0]
        self.port = listen_addr[1]
        self.conns = []
        self.plugins = []
        self.loop = loop or asyncio.get_event_loop()

    async def start(self):
        self.server = await asyncio.start_server(self.handle_terr,self.host,self.port,loop=self.loop)
        print("Server Started")

    async def handle_terr(self,inp,out):
        cl = TClientConnection(inp,out,self)
        await cl.set_server(default_hub)
        self.conns.append(cl)
        self.loop.create_task(cl.listen())

    async def close(self):
        await self.unload_plugins()
        self.server.close()

    async def broadcastChat(self,src,author=None,message:str="",color:bytes=None,sendall=True):
        srvpkt = allpkt = b"\x52\x01\x00"
        allpkt += b"\xff\x00"
        if author is not None:
            srvpkt += author.prmyslot.to_bytes(1,byteorder="little") + b"\x00" + prepstr(message)
            allpkt += prepstr("<"+author.name+"> "+message)
        else:
            srvpkt += b"\xff\x00" + prepstr(message)
            allpkt += prepstr(message)
        
        if color is None:
            srvpkt += b"\xff\xff\xff"
            allpkt += b"\xff\xff\xff"
        else:
            srvpkt += color
            allpkt += color
            
        if src is not None:
            await self.broadcastPacket(srvpkt,lambda u:src.cur_server == u.cur_server)
            if sendall:
              await self.broadcastPacket(allpkt,lambda u:src.cur_server != u.cur_server)
        else:
            await self.broadcastPacket(allpkt)
    
    async def broadcastPacket(self,pkt:bytes,cond = None):
        for x in self.conns:
            if cond is None or cond(x): 
                await x.writepkt(pkt)

    async def handle_chat(self,client,chatcommand,message):
        from terrelay.chatcommands import chatcommands
        if chatcommand == "Say" and message[0] == "-":
            if await self.handle_command(client,message):
                return
        if chatcommand in chatcommands:
            if chatcommand in ["Say","Emote"]:
                for plugin in self.plugins:
                    try:
                        await plugin.on_chat_message(self, client, message, emote=(chatcommand=="Emote"))
                    except:
                        print("Plugin Error on chat message:"+type(plugin).__name__)
                        traceback.print_exc()
            await chatcommands[chatcommand](self, client, message)

    async def handle_command(self,client,msg):
        from terrelay import tcommands
        success = await tcommands.handle(msg,client,self)
        return success

    async def load_plugins(self):
        plugins = get_plugins()
        for plugin in plugins:
            try:
                await self.register_plugin(plugin)
            except:
                print("error occured when loading "+type(plugin).__name__)
                traceback.print_exc()

    async def unload_plugins(self):
        for plugin in self.plugins:
            try:
                await plugin.on_plugin_unload(self)
            except:
                print("error occured when unloading "+type(plugin).__name__)
                traceback.print_exc()
        self.plugins = []

    async def register_plugin(self,plugin:TPlugin):
        print("Registered plugin ["+plugin.__name__+"]")
        plinstance = plugin()
        self.plugins.append(plinstance)
        await plinstance.on_plugin_load(self)

class TerrariaConnection:
    def __init__(self, rdr, wrtr):
        self.reader,self.writer = rdr,wrtr

    async def close(self):
        self.writer.close()

    async def writepkt(self, d:bytes): 
        if self.writer.transport.is_closing():
            raise ConnectionResetError()
        dl = (len(d)+2).to_bytes(2,byteorder="little")
        self.writer.write(dl+d)

    async def readpkt(self)->bytes:
        if self.writer.transport.is_closing():
            raise ConnectionResetError()
        i = await self.reader.readexactly(2)
        i = int.from_bytes(i,byteorder="little")-2
        return await self.reader.readexactly(i)



    async def sendchat(self, msg:str, color:bytes=b"\xff\xff\xff"):
        await self.writepkt(b"\x52\x01\x00\xff\x00"+prepstr(msg)+color)

    async def listen(self):
        while True:
            try:
                pkt = await self.readpkt()
                await self.handle_pkt(pkt)
            except asyncio.IncompleteReadError:
                await self.close()
                break
            except ConnectionResetError:
                await self.close()
                break
            except: # no other exception matters.
                traceback.print_exc()
                continue

    async def handle_pkt(self,pkt):
        pass

class TClientConnection(TerrariaConnection):

    def __init__(self,rdr,wrtr,srv:TRelayServer):
        self.initpkts = []
        self.seen_npc_ids = []
        self.seen_item_ids = []
        self.ingame = False
        self.prspawnpos = []
        self.prmyslot = 0
        self.respawn_on_world = False
        self.cur_server = None
        self.server = srv
        self.name = ""
        self.pos = [0,0]
        self.partycolor = None
        TerrariaConnection.__init__(self,rdr,wrtr)

    async def init_proxy(self,dest):
        self.prcon = TProxyConnection(dest,self.handle_pr_pkt)
        await self.prcon.connect()
        asyncio.get_event_loop().create_task(self.prcon.listen())
        self.cur_server = dest

    async def set_server(self,dst):
        if self.ingame: # we are in a server already, 
            if self.cur_server == dst: # if we're setting to the current server, just respawn.
                self.respawn()
                await self.sendchat("You're already connected to this server!",b"\xff\x22\x22")
                return
            
            if self.prcon is not None:
                oldprcon = self.prcon
                await oldprcon.close() 
                
            await self.purge_data()
            self.seen_npc_ids=[]
            self.seen_item_ids=[]
            
            await self.init_proxy(dst)

            for x in self.initpkts:
                await self.prcon.writepkt(x)

            self.respawn_on_world = True
            await self.sendchat("Server changed.",b"\x22\xff\xff")
        else: # this is the first server we're connecting to. no need to purge anything
            await self.init_proxy(dst)

    async def listen(self):
        await TerrariaConnection.listen(self)

    async def purge_data(self):
        for x in self.seen_npc_ids:
            await self.writepkt(b"\x17"+x+b"\x00"*40)
        for x in self.seen_item_ids:
            await self.writepkt(b"\x15"+x+b"\x00"*22)

    async def respawn(self):
        """ teleports the player to the spawn of the server they are currently connected to, does not ressurect or kill or revive or anything else, just a teleport """
        await self.writepkt(b"\x0c"+bytes(self.prmyslot)+b"\x00"*8)

    async def close(self):
        await self.prcon.close()
        await TerrariaConnection.close(self)

    async def handle_pr_pkt(self,pkt):
        if pkt[0] == 0x17:
            self.seen_npc_ids.append(pkt[1:2])
        elif pkt[0] == 0x15:
            self.seen_item_ids.append(pkt[1:2])
        elif pkt[0] == 0x07:
            self.prspawnpos = pkt[16:24]
            if self.respawn_on_world:
                await self.respawn()
        elif pkt[0] == 0x03:
            self.prmyslot = pkt[1]

        if self.ingame and pkt[0] in [0x25]:
            return

        await self.writepkt(pkt)

    async def handle_pkt(self,pkt):
        if pkt[0] in [0x01,0x26,0x04,0x10,0x2a,0x32,0x05,0x06,0x08,0x0c]:
            self.initpkts.append(pkt)

        if pkt[0] == 0x0c and self.respawn_on_world:
            await self.respawn()
            self.respawn_on_world = False
        if pkt[0] == 0x0d:
            self.pos = [pkt[5:9],pkt[9:13]]
        
        if not self.ingame and pkt[0] == 0x0c:
            await self.sendchat("Welcome! This server uses TERRPROXY.\nType -help for a list of commands.",b"\x00\xff\xff")
            self.ingame = True
        if pkt[0] == 0x52: # load netmodule
            u1,u2 = pkt[1:3]
            tl,t = parsestr(pkt[3:])
            try:
                _,msg = parsestr(pkt[3+tl:])
            except:
                msg = ""
            if u1==0x01 and u2==0x00: # chat netmodule
                await self.server.handle_chat(self,t,msg)
                return
        elif pkt[0] == 0x04:
            nlen = int.from_bytes(pkt[4:5],byteorder="big")
            self.name = pkt[5:5+nlen].decode("utf-8")
        # elif pkt[0] == 0x2d:
        #     p,t = pkt[0:1]
        #     if p == self.prmyslot:
        #         self.partycolor = ["\x"][t]

        await self.prcon.writepkt(pkt)

class TProxyConnection(TerrariaConnection):
    def __init__(self, dest, on_pkt):
        self.dest = dest
        self.on_pkt = on_pkt
        TerrariaConnection.__init__(self,None,None)

    async def connect(self):
        self.reader,self.writer = await asyncio.open_connection(self.dest[0],self.dest[1])

    async def handle_pkt(self,pkt):
        if self.on_pkt is not None:
            await self.on_pkt(pkt)
