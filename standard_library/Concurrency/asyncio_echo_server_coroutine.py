import asyncio
import logging
import sys

SERVER_ADDRESS = ("localhost", 10000)
logging.basicConfig(
    level=logging.DEBUG, format="%(name)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger("main")
event_loop = asyncio.get_event_loop()


async def echo(reader, writer):
    address = writer.get_extra_info("peername")
    log = logging.getLogger("Echo_{}_{}".format(*address))
    log.debug("connection accepted")
    while True:
        data = await reader.read(128)
        if data:
            log.debug(f"received {data!r}")
            writer.write(data)
            await writer.drain()
            log.debug(f"sent {data!r}")
        else:
            log.debug("closing")
            writer.close()
            return


factory = asyncio.start_server(echo, *SERVER_ADDRESS)
server = event_loop.run_until_complete(factory)
log.debug(f"starting up on {SERVER_ADDRESS[0]} port {SERVER_ADDRESS[1]}")
try:
    event_loop.run_forever()
finally:
    log.debug("closing server")
    server.close()
    event_loop.run_until_complete(server.wait_closed())
    log.debug("closing event loop")
    event_loop.close()
