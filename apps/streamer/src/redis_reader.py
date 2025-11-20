from __future__ import annotations

from typing import Any, Dict, List, Tuple

import json
import time

import redis

class RedisReader:
    """
    Reads telemetry frames from a Redis Stream using consumer groups.

    Assumptions:
      - Stream key is configurable (env → Config).
      - Entries are either:
          1) a "payload" field containing JSON, OR
          2) a set of fields directly representing the frame.
    """

    def __init__(
        self,
        redis_url: str,
        stream_key: str,
        group: str,
        consumer_name: str,
    ) -> None:
        self._r = redis.Redis.from_url(redis_url, decode_responses=True)
        self._key = stream_key
        self._group = group
        self._consumer = consumer_name

    def ensure_group(self) -> None:
        """
        Create the consumer group if it doesn't exist yet.
        Safe to call on every startup.
        """
        try:
            self._r.xgroup_create(self._key, self._group, id="$", mkstream=True)
        except redis.ResponseError as e:
            # BUSYGROUP means the group already exists.
            if "BUSYGROUP" not in str(e):
                raise

    def _normalize_entry(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """
        Convert raw Redis fields to a Python dict representing a frame.

        This is the place you'll tweak if the Deserializer changes how it
        writes to Redis.
        """
        # Case 1: JSON-encoded payload
        if "payload" in fields:
            try:
                return json.loads(fields["payload"])
            except json.JSONDecodeError:
                # Fall back to returning raw fields if payload is bad
                pass

        # Case 2: direct fields (all strings)
        # You can add conversions here if you want, but keep it generic for now.
        return dict(fields)

    def read_batch(
        self,
        count: int = 100,
        block_ms: int = 2000,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Read up to `count` new entries from the stream.

        Returns a list of (entry_id, frame_dict).
        """
        resp = self._r.xreadgroup(
            groupname=self._group,
            consumername=self._consumer,
            streams={self._key: ">"},
            count=count,
            block=block_ms,
        )

        if not resp:
            return []

        # resp is like: [(stream_key, [(id, fields), (id, fields), ...])]
        _, entries = resp[0]
        result: List[Tuple[str, Dict[str, Any]]] = []

        now_ms = int(time.time() * 1000)
        for entry_id, fields in entries:
            frame = self._normalize_entry(fields)
            # If we don't have a timestamp yet, downstream can fill it
            frame.setdefault("ts_ms", now_ms)
            result.append((entry_id, frame))

        return result

    def ack(self, ids: List[str]) -> None:
        """Mark the given stream entries as processed."""
        if not ids:
            return
        self._r.xack(self._key, self._group, *ids)
