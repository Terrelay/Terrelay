from __future__ import annotations
from terrelay.tconnection import TPlugin, TClientConnection, TRelayServer, prepstr
from terrelay.tcommands import reg_command, commands

@reg_command(helpstr="give <itemid> - Spawns an item with that id at your feet.")
async def give(cl:TClientConnection,srv:TRelayServer,args):
    try:
        itemid = int(args[0])
        quantity = 1
        prefix = 0
        try:
            quantity = int(args[1])
        except:
            pass
        try:
            prefix = int(args[2])
        except:
            pass
        # await cl.prcon.writepkt(b"\x15\x90\x01"+cl.pos[0]+cl.pos[1]+b"\x00"*8+b"\xff\x7f\x00\x01\xf1\x02")

        await cl.writepkt(b"\x15\x7f\x00"+cl.pos[0]+cl.pos[1]+b"\x00"*8+quantity.to_bytes(2,byteorder="little")+prefix.to_bytes(1,byteorder="little")+b"\x00"+itemid.to_bytes(2,byteorder="little"))
        # await cl.writepkt(b"\x58\x7f\x00\x02\xff\xff")
        await cl.writepkt(b"\x16\x7f\x00"+cl.prmyslot.to_bytes(1,byteorder="little"))
    except:
        await cl.sendchat("Usage: give <itemid>")
        pass
    return True

@reg_command(helpstr="heal - Heals you back to full.")
async def heal(cl:TClientConnection,srv:TRelayServer,args):
    await cl.writepkt(b"\x42\x00\xff\x7f")
    for x in range(5):
        await cl.writepkt(b"\x15"+(128+x).to_bytes(2,byteorder="little")+cl.pos[0]+cl.pos[1]+b"\x00"*8+b"\x01\x00\x00\x00\xb8\x00")
        await cl.writepkt(b"\x16"+(128+x).to_bytes(2,byteorder="little")+cl.prmyslot.to_bytes(1,byteorder="little"))
    return True

godmodes = []
import asyncio
@reg_command(helpstr="godmode - Heals you to full health and mana 3 times per second.")
async def godmode(cl:TClientConnection,srv:TRelayServer,args):
    async def myloop():
        while cl in godmodes:
            try:
                await cl.writepkt(b"\x42\x00\xff\x7f")
                for x in range(5):
                    await cl.writepkt(b"\x15"+(128+x).to_bytes(2,byteorder="little")+cl.pos[0]+cl.pos[1]+b"\x00"*8+b"\x01\x00\x00\x00\xb8\x00")
                    await cl.writepkt(b"\x16"+(128+x).to_bytes(2,byteorder="little")+cl.prmyslot.to_bytes(1,byteorder="little"))
                await asyncio.sleep(0.3)
            except:
                godmodes.remove(cl)
    if cl in godmodes:
        godmodes.remove(cl)
    else:
        godmodes.append(cl)
    asyncio.create_task(myloop())
    return True