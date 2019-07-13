# TODO some proxy functionality, acting as a middleman between 2 servers 
#  (just fwd packets at first, including chat, but capture all SAY "/"s as commands)
#  See if we can switch between servers mid-game 
#   Crude idea: send completely new zone packets and send faux disconnect packets
#   Better version: see if any of the server-inits clear the client cache and fuck with that. 
#        Looks like when you send 0x25 midgame on a server with a password, the client goes 
#          back to loading screen, maybe this can be abused? Have not tested if it is a working
#          loading screen or not. Might be worth a shot to send 0x25 and all future packets
#          and then see if there's any single packet that causes a cache flush 
#          (assuming there is a cache....).
#  
# The best place to start the remote connection would most likely be when the client sends a x01,
#  since we can just forward it to the other server and forward that servers x03 back (or x25/x02)
#
# TODO figure out why the client keeps timing out (being a full proxy will most likely fix this)
# 


import asyncio
import struct
from terrelay.tconnection import TerrariaConnection, TClientConnection, TRelayServer


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    relaysrv = TRelayServer(("0.0.0.0",7777),loop=loop)

    async def wakeup():
        while True:
            await asyncio.sleep(1)
    loop.create_task(wakeup())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Recv SIGINT, closing")
        pass

    loop.run_until_complete(relaysrv.close())
    loop.close()