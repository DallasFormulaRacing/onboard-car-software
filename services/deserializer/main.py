#!/usr/bin/env python3
import argparse
import glob
import os
import time
import cantools
import can
import redis


def main():
    p = argparse.ArgumentParser(
        description="Listen on a CAN interface and decode messages using DBC files."
    )
    p.add_argument("interface", help="CAN interface name (e.g. can0 or vcan0)")
    args = p.parse_args()

    # Load all DBC files from directory
    dbc_dir = os.environ.get("DBC_DIR", "../../dbc-files")
    dbc_files = glob.glob(os.path.join(dbc_dir, "*.dbc"))

    db = cantools.database.Database()
    for dbc_file in dbc_files:
        db.add_dbc_file(dbc_file)
        print(f"Loaded DBC file: {dbc_file}")

    if not dbc_files:
        print(f"Warning: No DBC files found in {dbc_dir}")

    # FIXME: is interface=socketcan always right..?
    bus = can.interface.Bus(channel=args.interface, interface="socketcan")
    print(f"Listening on {args.interface}, loaded {len(dbc_files)} DBC file(s) from {dbc_dir}")

    # Connect to the Redis server via localhost (because this container is in host network mode)
    # REDIS_PORT is exposed by docker-compose, default 6379
    redis_port = int(os.environ.get("REDIS_PORT", "6379"))
    r = redis.Redis(decode_responses=True, host="localhost", port=redis_port)
    print(f"Connected to Redis on localhost:{redis_port}")

    while True:
        # NOTE: Consider swapping recv() for Listener
        msg = bus.recv(timeout=None)

        # decoded = db.decode_message(msg.arbitration_id, msg.data)
        try:
            database_message = db.get_message_by_frame_id(
                msg.arbitration_id, msg.is_extended_id
            )
        except KeyError:
            print(f"Unknown message with ID {msg.arbitration_id} (extended={msg.is_extended_id})")
            continue


        sensor_name = database_message.name
        sensor_id = msg.arbitration_id
        decoded = database_message.decode_simple(msg.data)

        fields = {
            "timestamp": time.time(),
            "sensor_id": sensor_id,
            "sensor_name": sensor_name,
        }

        # merge decoded signals into the stream entry
        for k, v in decoded.items():
            fields[k] = str(v) # Convert values to strings for Redis

        r.xadd(name="decoded-can", fields=fields)

        # print(f"{sensor_name=}")

        # for k, v in decoded.items():
        #     print(f"\t{k=} {v=}")


if __name__ == "__main__":
    main()
