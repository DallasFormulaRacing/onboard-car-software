"""
Small helper to push fake CAN-like telemetry into a Redis Stream so you can
test the Streamer without the C++ deserializer being ready.
"""

import time
import random
import redis
import json
import os

STREAM_KEY = os.getenv("REDIS_STREAM_KEY", "can:frames")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def main():
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    print(f"[fake-data] Writing to stream '{STREAM_KEY}' at {REDIS_URL}")

    ts = int(time.time() * 1000)
    speed = 0.0
    rpm = 0.0

    try:
        while True:
            ts += 200  # 5 Hz
            # Simple pattern: ramp speed + rpm up, then down
            phase = (ts // 10000) % 4

            if phase == 0:
                # Idle
                speed = 0.0
                rpm = 0.0
            elif phase == 1:
                # Accelerating
                speed = min(speed + 0.5, 30.0)
                rpm = min(rpm + 200, 4000)
            elif phase == 2:
                # Cruising
                speed = 30.0
                rpm = 3500.0
            else:
                # Braking
                speed = max(speed - 0.8, 0.0)
                rpm = max(rpm - 300, 0.0)

            frame = {
                "ts_ms": ts,
                "vehicle_speed": speed,
                "rpm": rpm,
                "can_id": 0x123,
                "raw_data": "01ABEF",
            }

            # Option A: direct fields:
            # r.xadd(STREAM_KEY, frame)

            # Option B: JSON payload field (matches your _normalize_entry logic):
            r.xadd(STREAM_KEY, {"payload": json.dumps(frame)})

            print(f"[fake-data] XADD speed={speed:.1f} rpm={rpm:.0f}")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("[fake-data] Stopping.")


if __name__ == "__main__":
    main()
