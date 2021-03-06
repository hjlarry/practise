import redis
import logging
import json

import sys

sys.path.append("/code")

import config
import bootstrap
from domain import commands


r = redis.Redis(**config.get_redis_host_and_port())


def main():
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")

    for m in pubsub.listen():
        handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(m, bus):
    logging.debug("handling msg %s", m)
    data = json.loads(m["data"])
    cmd = commands.ChangeBatchQuantity(ref=data["batchref"], qty=data["qty"])
    bus.handle(cmd)


if __name__ == "__main__":
    main()
