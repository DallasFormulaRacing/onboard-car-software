import os
import socket
from dataclasses import dataclass

@dataclass
class Config:
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    redis_stream_key: str = os.getenv("REDIS_STREAM_KEY", "can:frames")
    redis_consumer_group: str = os.getenv("REDIS_CONSUMER_GROUP", "streamer")
    redis_consumer_name: str = os.getenv(
        "REDIS_CONSUMER_NAME",
        f"streamer-{socket.gethostname()}"
    )

    # Activity / buffering
    pre_roll_seconds: float = float(os.getenv("PRE_ROLL_SECONDS", "5"))
    inactive_grace_seconds: float = float(os.getenv("INACTIVE_GRACE_SECONDS", "10"))
    min_speed: float = float(os.getenv("MIN_SPEED_MPS", "0.5"))
    speed_field: str = os.getenv("SPEED_FIELD", "vehicle_speed")
    rpm_field: str = os.getenv("RPM_FIELD", "rpm")
    timestamp_field: str = os.getenv("TS_FIELD", "ts_ms")  # fall back if absent

    # Session / partitioning
    pi_id: str = os.getenv("PI_ID", socket.gethostname())
