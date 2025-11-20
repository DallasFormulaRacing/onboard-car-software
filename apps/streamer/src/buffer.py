from collections import deque
from typing import Deque, Tuple, Dict, Any

class PreRollBuffer:
    """
    Maintains a rolling window of frames by timestamp (ms).
    Used to send the last N seconds of data when the car becomes active.
    """
    def __init__(self, window_seconds: float) -> None:
        self.window_ms = int(window_seconds * 1000)
        self._buf: Deque[Tuple[int, Dict[str, Any]]] = deque()

    def push(self, ts_ms: int, frame: Dict[str, Any]) -> None:
        self._buf.append((ts_ms, frame))
        cutoff = ts_ms - self.window_ms
        # Trim everything older than the window
        while self._buf and self._buf[0][0] < cutoff:
            self._buf.popleft()

    def drain(self) -> list[Dict[str, Any]]:
        """Return all buffered frames and clear the buffer."""
        items = [f for (_ts, f) in self._buf]
        self._buf.clear()
        return items
