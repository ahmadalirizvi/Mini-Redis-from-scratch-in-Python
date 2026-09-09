"""
Command parser for Mini Redis.

Converts raw text commands received over the socket into calls
against a KeyValueStore instance, and formats the results back
into plain text responses.

Note: AUTH, SUBSCRIBE, and PUBLISH are handled directly in
server.py rather than here, since they involve per-connection
and cross-connection state (auth status, subscriber lists) that
this module — and the KeyValueStore it wraps — has no access to.
"""

from typing import Optional
from storage import KeyValueStore


def require_args(parts: list[str], count: int, usage: str) -> Optional[str]:
    """
    Validate that a command has exactly `count` tokens.

    Returns an error string if validation fails, or None if the
    command has the correct number of arguments.
    """
    if len(parts) != count:
        return f"ERR usage: {usage}"
    return None


def handle_command(store: KeyValueStore, message: str) -> str:
    """
    Parse a raw command string and execute it against the store.

    Returns a plain-text response suitable for sending back to
    the client over the socket.
    """
    parts = message.split()

    if not parts:
        return "ERR empty command"

    cmd = parts[0].upper()

    # ---- Strings ----

    if cmd == "SET":
        if len(parts) == 3:
            key, value = parts[1], parts[2]
            return store.set(key, value)
        elif len(parts) == 5 and parts[3].upper() == "EX":
            key, value = parts[1], parts[2]
            try:
                ttl = int(parts[4])
            except ValueError:
                return "ERR invalid TTL value"
            return store.set(key, value, ttl=ttl)
        else:
            return "ERR usage: SET key value [EX seconds]"

    elif cmd == "GET":
        if err := require_args(parts, 2, "GET key"):
            return err
        result = store.get_value(parts[1])
        return result if result is not None else "(nil)"

    elif cmd == "DELETE":
        if err := require_args(parts, 2, "DELETE key"):
            return err
        return store.del_value(parts[1])

    elif cmd == "EXISTS":
        if err := require_args(parts, 2, "EXISTS key"):
            return err
        return str(store.exists(parts[1]))

    elif cmd == "TTL":
        if err := require_args(parts, 2, "TTL key"):
            return err
        return str(store.ttl(parts[1]))

    elif cmd == "INCR":
        if err := require_args(parts, 2, "INCR key"):
            return err
        return str(store.incr(parts[1]))

    # ---- Lists ----

    elif cmd == "LPUSH":
        if err := require_args(parts, 3, "LPUSH key value"):
            return err
        return store.lpush(parts[1], parts[2])

    elif cmd == "RPUSH":
        if err := require_args(parts, 3, "RPUSH key value"):
            return err
        return store.rpush(parts[1], parts[2])

    elif cmd == "LRANGE":
        if err := require_args(parts, 2, "LRANGE key"):
            return err
        result = store.lrange(parts[1])
        return " ".join(result) if isinstance(result, list) else result

    elif cmd == "LPOP":
        if err := require_args(parts, 2, "LPOP key"):
            return err
        result = store.lpop(parts[1])
        return result if result is not None else "(nil)"

    elif cmd == "LLEN":
        if err := require_args(parts, 2, "LLEN key"):
            return err
        return str(store.llen(parts[1]))

    # ---- Sets ----

    elif cmd == "SADD":
        if err := require_args(parts, 3, "SADD key value"):
            return err
        return store.sadd(parts[1], parts[2])

    elif cmd == "SMEMBERS":
        if err := require_args(parts, 2, "SMEMBERS key"):
            return err
        result = store.smembers(parts[1])
        return " ".join(result) if isinstance(result, list) else result

    elif cmd == "SREM":
        if err := require_args(parts, 3, "SREM key value"):
            return err
        return store.srem(parts[1], parts[2])

    # ---- Hashes ----

    elif cmd == "HSET":
        if err := require_args(parts, 4, "HSET key field value"):
            return err
        return store.hset(parts[1], parts[2], parts[3])

    elif cmd == "HGET":
        if err := require_args(parts, 3, "HGET key field"):
            return err
        result = store.hget(parts[1], parts[2])
        return result if result is not None else "(nil)"

    elif cmd == "HGETALL":
        if err := require_args(parts, 2, "HGETALL key"):
            return err
        result = store.hgetall(parts[1])
        if not isinstance(result, dict):
            return result
        return " ".join(f"{k} {v}" for k, v in result.items())

    # ---- Sorted Sets ----

    elif cmd == "ZADD":
        if err := require_args(parts, 4, "ZADD key score member"):
            return err
        return store.zadd(parts[1], parts[2], parts[3])

    elif cmd == "ZRANGE":
        if err := require_args(parts, 2, "ZRANGE key"):
            return err
        result = store.zrange(parts[1])
        return " ".join(result) if isinstance(result, list) else result

    elif cmd == "ZSCORE":
        if err := require_args(parts, 3, "ZSCORE key member"):
            return err
        result = store.zscore(parts[1], parts[2])
        return str(result) if result is not None else "(nil)"

    # ---- Rate Limiting ----

    elif cmd == "RATE_LIMIT":
        if err := require_args(parts, 4, "RATE_LIMIT key max_requests window_seconds"):
            return err
        return store.rate_limit(parts[1], parts[2], parts[3])

    else:
        return f"ERR unknown command '{cmd}'"