from dataclasses import dataclass
from typing import Mapping, Any

@dataclass
class ActivityConfig:
    speed_field: str
    rpm_field: str
    min_speed: float

def is_active(
    frame: Mapping[str, Any],
    cfg: ActivityConfig
) -> bool:
    """
    Returns True if the car is considered "active" based on speed or RPM.
    All values come in as strings from Redis; convert cautiously.
    """
    def _to_float(v: Any) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    speed = _to_float(frame.get(cfg.speed_field, 0.0))
    rpm = _to_float(frame.get(cfg.rpm_field, 0.0))

    return (speed > cfg.min_speed) or (rpm > 0.0)
