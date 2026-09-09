"""
Core storage engine for Mini Redis.

KeyValueStore is an in-memory key-value store with:
- Basic string operations (SET/GET/DELETE/EXISTS)
- TTL-based expiration (lazy expiration on access)
- JSON-based persistence to disk, with batched (dirty-flag) writes
- List, Set, Hash, and Sorted Set data structures
- Basic counter/rate-limiting support

Persistence note: writes don't hit disk immediately. Mutating methods
set self._dirty = True; a background thread (see server.py) calls
flush() periodically to actually save. This trades a small durability
window (writes since the last flush can be lost on crash) for much
higher write throughput — see Phase 12 benchmark results in README.md.
"""

import time
import json
import os
from typing import Any, Optional, Union

from config import DEFAULT_DB_PATH


class KeyValueStore:
    def __init__(self, filepath: Optional[str] = None) -> None:
        """Create a store, loading any existing data from filepath."""
        self.filepath = filepath or DEFAULT_DB_PATH
        self.data: dict[str, Any] = {}
        self.expiry: dict[str, float] = {}
        self._dirty: bool = False
        self.load()

    # ---- Strings ----

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> str:
        """Store value under key. If ttl (seconds) is given, key expires after ttl."""
        self.data[key] = value

        if ttl is not None:
            self.expiry[key] = time.time() + ttl
        else:
            # Remove old expiry if the key already existed
            self.expiry.pop(key, None)

        self._dirty = True
        return "OK"

    def get_value(self, key: str) -> Optional[Any]:
        """Return the value for key, or None if missing or expired."""
        if key in self.expiry:
            if time.time() >= self.expiry[key]:
                del self.data[key]
                del self.expiry[key]
                self._dirty = True
                return None

        return self.data.get(key)

    def del_value(self, key: str) -> str:
        """Delete key and any associated TTL. Returns 'OK' or 'Key not found'."""
        if key in self.data:
            del self.data[key]
            self.expiry.pop(key, None)
            self._dirty = True
            return "OK"

        return "Key not found"

    def exists(self, key: str) -> bool:
        """Return True if key exists and has not expired."""
        # Calling get_value() also checks expiration
        return self.get_value(key) is not None

    def ttl(self, key: str) -> int:
        """
        Return remaining seconds until key expires.

        Returns:
            -1 if the key exists but has no expiration
            -2 if the key does not exist or has already expired
            Otherwise, seconds remaining (rounded down)
        """
        if key not in self.data:
            return -2

        if key not in self.expiry:
            return -1

        remaining = self.expiry[key] - time.time()

        if remaining <= 0:
            del self.data[key]
            del self.expiry[key]
            self._dirty = True
            return -2

        return int(remaining)

    def incr(self, key: str) -> Union[int, float, str]:
        """Increment a numeric counter at key by 1, creating it at 0 if missing."""
        current = self.data.get(key, 0)

        if not isinstance(current, (int, float)):
            return "ERR value is not an integer"

        current += 1
        self.data[key] = current
        self._dirty = True
        return current

    # ---- Persistence ----

    def save(self) -> None:
        """Write the current data and expiry state to disk as JSON."""
        dir_path = os.path.dirname(self.filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Sets aren't JSON-serializable, so tag and convert them to lists
        serializable_data = {}
        for key, value in self.data.items():
            if isinstance(value, set):
                serializable_data[key] = {"__type__": "set", "values": list(value)}
            else:
                serializable_data[key] = value

        with open(self.filepath, "w") as f:
            json.dump({"data": serializable_data, "expiry": self.expiry}, f)

    def flush(self) -> None:
        """Save to disk only if there are unsaved changes."""
        if self._dirty:
            self.save()
            self._dirty = False

    def load(self) -> None:
        """Load data and expiry state from disk, if the file exists and is valid."""
        if not os.path.exists(self.filepath):
            return

        if os.path.getsize(self.filepath) == 0:
            return

        try:
            with open(self.filepath, "r") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            # Corrupt or partially-written file — start fresh
            return

        raw_data = content.get("data", {})
        self.expiry = content.get("expiry", {})

        # Convert tagged sets back from their list form
        self.data = {}
        for key, value in raw_data.items():
            if isinstance(value, dict) and value.get("__type__") == "set":
                self.data[key] = set(value["values"])
            else:
                self.data[key] = value

    # ---- Lists ----

    def lpush(self, key: str, value: str) -> str:
        """Insert value at the head of the list at key, creating it if needed."""
        if key not in self.data:
            self.data[key] = []

        if not isinstance(self.data[key], list):
            return "ERR wrong type for key"

        self.data[key].insert(0, value)
        self._dirty = True
        return "OK"

    def rpush(self, key: str, value: str) -> str:
        """Insert value at the tail of the list at key, creating it if needed."""
        if key not in self.data:
            self.data[key] = []

        if not isinstance(self.data[key], list):
            return "ERR wrong type for key"

        self.data[key].append(value)
        self._dirty = True
        return "OK"

    def lrange(self, key: str) -> Union[list[str], str]:
        """Return the full list stored at key."""
        value = self.data.get(key)

        if value is None:
            return []

        if not isinstance(value, list):
            return "ERR wrong type for key"

        return value

    def lpop(self, key: str) -> Optional[str]:
        """Remove and return the head of the list at key. Deletes key if list empties."""
        value = self.data.get(key)

        if value is None:
            return None

        if not isinstance(value, list):
            return "ERR wrong type for key"

        if not value:
            return None

        popped = value.pop(0)

        if not value:
            del self.data[key]

        self._dirty = True
        return popped

    def llen(self, key: str) -> int:
        """Return the length of the list at key, or 0 if missing."""
        value = self.data.get(key)

        if value is None:
            return 0

        if not isinstance(value, list):
            return "ERR wrong type for key"

        return len(value)

    # ---- Sets ----

    def sadd(self, key: str, value: str) -> str:
        """Add value to the set at key, creating it if needed. No-op on duplicates."""
        if key not in self.data:
            self.data[key] = set()

        if not isinstance(self.data[key], set):
            return "ERR wrong type for key"

        self.data[key].add(value)
        self._dirty = True
        return "OK"

    def smembers(self, key: str) -> Union[list[str], str]:
        """Return all members of the set at key."""
        value = self.data.get(key)

        if value is None:
            return []

        if not isinstance(value, set):
            return "ERR wrong type for key"

        return list(value)

    def srem(self, key: str, value: str) -> str:
        """Remove value from the set at key. Deletes key if set empties."""
        value_set = self.data.get(key)

        if value_set is None:
            return "OK"

        if not isinstance(value_set, set):
            return "ERR wrong type for key"

        value_set.discard(value)

        if not value_set:
            del self.data[key]

        self._dirty = True
        return "OK"

    # ---- Hashes ----

    def hset(self, key: str, field: str, value: str) -> str:
        """Set field to value within the hash at key, creating it if needed."""
        if key not in self.data:
            self.data[key] = {}

        if not isinstance(self.data[key], dict):
            return "ERR wrong type for key"

        self.data[key][field] = value
        self._dirty = True
        return "OK"

    def hget(self, key: str, field: str) -> Optional[str]:
        """Return the value of field within the hash at key."""
        value = self.data.get(key)

        if value is None:
            return None

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        return value.get(field)

    def hgetall(self, key: str) -> Union[dict[str, str], str]:
        """Return all field-value pairs in the hash at key."""
        value = self.data.get(key)

        if value is None:
            return {}

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        return value

    # ---- Sorted Sets ----

    def zadd(self, key: str, score: str, member: str) -> str:
        """Add member with score to the sorted set at key, creating it if needed."""
        if key not in self.data:
            self.data[key] = {}

        if not isinstance(self.data[key], dict):
            return "ERR wrong type for key"

        try:
            score_value = float(score)
        except ValueError:
            return "ERR score must be a number"

        self.data[key][member] = score_value
        self._dirty = True
        return "OK"

    def zrange(self, key: str) -> Union[list[str], str]:
        """Return members of the sorted set at key, ordered by score ascending."""
        value = self.data.get(key)

        if value is None:
            return []

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        sorted_members = sorted(value.items(), key=lambda item: item[1])
        return [member for member, score in sorted_members]

    def zscore(self, key: str, member: str) -> Optional[float]:
        """Return the score of member within the sorted set at key."""
        value = self.data.get(key)

        if value is None:
            return None

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        return value.get(member)

    # ---- Rate Limiting ----

    def rate_limit(self, key: str, max_requests: str, window_seconds: str) -> str:
        """
        Fixed-window rate limiter: allow up to max_requests within window_seconds.

        Returns "ALLOWED" or "REJECTED". The window fully resets once
        window_seconds has elapsed since the first request in that window.
        """
        try:
            max_requests_int = int(max_requests)
            window_seconds_int = int(window_seconds)
        except ValueError:
            return "ERR max_requests and window_seconds must be integers"

        if key not in self.data:
            self.data[key] = 1
            self.expiry[key] = time.time() + window_seconds_int
            self._dirty = True
            return "ALLOWED"

        if key in self.expiry and time.time() >= self.expiry[key]:
            self.data[key] = 1
            self.expiry[key] = time.time() + window_seconds_int
            self._dirty = True
            return "ALLOWED"

        self.data[key] += 1
        self._dirty = True

        if self.data[key] > max_requests_int:
            return "REJECTED"

        return "ALLOWED"