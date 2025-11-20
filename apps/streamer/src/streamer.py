from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Tuple

from .buffer import PreRollBuffer
from .activity import ActivityConfig, is_active
from .redis_reader import RedisReader
from .config import Config


class ProducerProtocol:
    """
    Minimal protocol that Eshi's EventHubProducer should implement.
    """
    def send(self, records: List[Dict[str, Any]], partition_key: str) -> None:
        raise NotImplementedError


class FakeProducer(ProducerProtocol):
    """
    Temporary stand-in for development. Just prints what would be sent.
    """
    def send(self, records: List[Dict[str, Any]], partition_key: str) -> None:
        print(f"[FakeProducer] Sending {len(records)} records "
              f"for session {partition_key}")


class Streamer:
    def __init__(self, cfg: Config, producer: ProducerProtocol | None = None) -> None:
        self._cfg = cfg
        self._reader = RedisReader(
            redis_url=cfg.redis_url,
            stream_key=cfg.redis_stream_key,
            group=cfg.redis_consumer_group,
            consumer_name=cfg.redis_consumer_name,
        )
        self._buffer = PreRollBuffer(cfg.pre_roll_seconds)
        self._activity_cfg = ActivityConfig(
            speed_field=cfg.speed_field,
            rpm_field=cfg.rpm_field,
            min_speed=cfg.min_speed,
        )
        self._producer: ProducerProtocol = producer or FakeProducer()

        # Session + state
        self._session_id = self._new_session_id()
        self._state: str = "IDLE"          # other states: "ACTIVE", "STOP_PENDING"
        self._stop_deadline: float | None = None

    def _new_session_id(self) -> str:
        return f"{self._cfg.pi_id}-{int(time.time())}-{uuid.uuid4().hex[:8]}"

    def _send_event(self, event_type: str) -> None:
        """
        Sends a lightweight control event (drive:start / drive:stop).
        """
        now_ms = int(time.time() * 1000)
        record = {
            "type": event_type,
            "session": self._session_id,
            "ts_ms": now_ms,
            "pi_id": self._cfg.pi_id,
        }
        self._producer.send([record], partition_key=self._session_id)

    def _handle_batch(
        self,
        entries: List[Tuple[str, Dict[str, Any]]],
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Process a batch from Redis and decide what to send.

        Returns:
          - list of Redis IDs to ACK
          - list of frames to send to the producer (excluding control events)
        """
        ids_to_ack: List[str] = []
        outgoing: List[Dict[str, Any]] = []

        for entry_id, frame in entries:
            ids_to_ack.append(entry_id)

            ts_ms = int(frame.get(self._cfg.timestamp_field, frame.get("ts_ms")))
            self._buffer.push(ts_ms, frame)

            active = is_active(frame, self._activity_cfg)

            if self._state == "IDLE":
                if active:
                    # Car just woke up → new session, start event + pre-roll
                    self._session_id = self._new_session_id()
                    self._state = "ACTIVE"
                    self._stop_deadline = None
                    self._send_event("drive:start")
                    # Flush pre-roll frames first
                    outgoing.extend(self._buffer.drain())
                    outgoing.append(frame)
                # if inactive while IDLE, just keep buffering (for potential future start)

            elif self._state == "ACTIVE":
                outgoing.append(frame)
                if not active:
                    # Start grace timer
                    self._state = "STOP_PENDING"
                    self._stop_deadline = time.time() + self._cfg.inactive_grace_seconds

            elif self._state == "STOP_PENDING":
                if active:
                    # Car woke up again within grace period → cancel stop
                    self._state = "ACTIVE"
                    self._stop_deadline = None
                else:
                    # Still inactive; timer check happens in run() loop
                    pass

        return ids_to_ack, outgoing

    def run(self) -> None:
        """
        Main loop. Reads from Redis, applies activity + pre-roll logic,
        sends data via producer, and ACKs on success.
        """
        self._reader.ensure_group()
        print("[Streamer] Starting main loop in state IDLE")

        try:
            while True:
                batch = self._reader.read_batch()
                now = time.time()

                # Handle grace timer if in STOP_PENDING
                if self._state == "STOP_PENDING" and self._stop_deadline is not None:
                    if now >= self._stop_deadline:
                        self._send_event("drive:stop")
                        self._state = "IDLE"
                        self._stop_deadline = None

                if not batch:
                    # No new frames; small sleep to avoid busy loop
                    time.sleep(0.1)
                    continue

                ids_to_ack, outgoing = self._handle_batch(batch)

                if outgoing:
                    # Send frames; if this raises, we do NOT ack
                    self._producer.send(outgoing, partition_key=self._session_id)

                # If we reached here, send succeeded; now we can ACK the Redis entries
                self._reader.ack(ids_to_ack)

        except KeyboardInterrupt:
            print("[Streamer] Caught KeyboardInterrupt, shutting down gracefully")
            # If we were active, send a stop event on shutdown
            if self._state in ("ACTIVE", "STOP_PENDING"):
                self._send_event("drive:stop")
