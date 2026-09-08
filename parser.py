def handle_command(store, message):
    parts = message.split()

    if not parts:
        return "ERR empty command"

    cmd = parts[0].upper()

    # SET key value
    # SET key value EX seconds
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

    # GET key
    elif cmd == "GET":
        if len(parts) != 2:
            return "ERR usage: GET key"

        key = parts[1]
        result = store.get_value(key)
        return result if result is not None else "(nil)"

    # DELETE key
    elif cmd == "DELETE":
        if len(parts) != 2:
            return "ERR usage: DELETE key"

        return store.del_value(parts[1])

    # EXISTS key
    elif cmd == "EXISTS":
        if len(parts) != 2:
            return "ERR usage: EXISTS key"

        return str(store.exists(parts[1]))

    
    elif cmd == "LPUSH":
        if len(parts) != 3:
            return "ERR usage: LPUSH key value"
        return store.lpush(parts[1], parts[2])

    elif cmd == "LRANGE":
        if len(parts) != 2:
            return "ERR usage: LRANGE key"
        result = store.lrange(parts[1])
        return " ".join(result) if isinstance(result, list) else result
    
    elif cmd == "LPUSH":
        if len(parts) != 3:
            return "ERR usage: LPUSH key value"
        return store.lpush(parts[1], parts[2])

    elif cmd == "LRANGE":
        if len(parts) != 2:
            return "ERR usage: LRANGE key"
        result = store.lrange(parts[1])
        return " ".join(result) if isinstance(result, list) else result

    elif cmd == "LPOP":
        if len(parts) != 2:
            return "ERR usage: LPOP key"
        result = store.lpop(parts[1])
        return result if result is not None else "(nil)"

    elif cmd == "LLEN":
        if len(parts) != 2:
            return "ERR usage: LLEN key"
        return str(store.llen(parts[1]))
    
    # TTL key
    elif cmd == "TTL":
        if len(parts) != 2:
            return "ERR usage: TTL key"
    
        return str(store.ttl(parts[1]))
    
    elif cmd == "HSET":
        if len(parts) != 4:
            return "ERR usage: HSET key field value"
        return store.hset(parts[1], parts[2], parts[3])

    elif cmd == "HGET":
        if len(parts) != 3:
            return "ERR usage: HGET key field"
        result = store.hget(parts[1], parts[2])
        return result if result is not None else "(nil)"

    elif cmd == "HGETALL":
        if len(parts) != 2:
            return "ERR usage: HGETALL key"
        result = store.hgetall(parts[1])
        if not isinstance(result, dict):
            return result
        return " ".join(f"{k} {v}" for k, v in result.items())
        
    else:
        return f"ERR unknown command '{cmd}'"