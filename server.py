import asyncio
import struct
from terrelay.tconnection import TerrariaConnection, TClientConnection, TRelayServer, TPlugin
from settings import server_bind


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    relaysrv = TRelayServer(server_bind,loop=loop)

    async def wakeup():
        while True:
            await asyncio.sleep(1)

    loop.create_task(relaysrv.load_plugins())
    
    loop.create_task(wakeup())
    loop.create_task(relaysrv.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Recv SIGINT, closing")
        pass

    loop.run_until_complete(relaysrv.close())
    loop.close()