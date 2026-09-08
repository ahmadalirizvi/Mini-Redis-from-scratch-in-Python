# Mini Redis from scratch in Python

import time
import json
import os

class KeyValueStore:

    def __init__(self, filepath="data/database.json"):
        self.filepath = filepath
        self.data = {}
        self.expiry = {}
        self.load()

    # SET key value [EX seconds]
    def set(self, key, value, ttl=None):
        self.data[key] = value

        if ttl is not None:
            self.expiry[key] = time.time() + ttl
        else:
            # Remove old expiry if the key already existed
            self.expiry.pop(key, None)

        return "OK"

    def get_value(self, key):
        if key in self.expiry:
            if time.time() >= self.expiry[key]:
                del self.data[key]
                del self.expiry[key]
                self.save()          # <-- add this
                return None
    
        return self.data.get(key)

    # DELETE key
    def del_value(self, key):

        if key in self.data:
            del self.data[key]

            # Also remove expiry information
            self.expiry.pop(key, None)
            self.save()

            return "OK"

        return "Key not found"

    # EXISTS key
    def exists(self, key):

        # Calling get_value() also checks expiration
        return self.get_value(key) is not None

    # TTL key
    def ttl(self, key):
        if key not in self.data:
            return -2

        if key not in self.expiry:
            return -1

        remaining = self.expiry[key] - time.time()

        if remaining <= 0:
            del self.data[key]
            del self.expiry[key]
            self.save()               # <-- add this
            return -2

        return int(remaining)
    
    # Save method
    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump({"data": self.data, "expiry": self.expiry}, f)
    
    # Load method   
    def load(self):
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

        self.data = content.get("data", {})
        self.expiry = content.get("expiry", {})
    
    # Call save() after every mutation
    
    def set(self, key, value, ttl=None):
        self.data[key] = value
        if ttl is not None:
            self.expiry[key] = time.time() + ttl
        else:
            self.expiry.pop(key, None)
        self.save()
        return "OK"
        
    # LPUSH key value
    def lpush(self, key, value):
        if key not in self.data:
            self.data[key] = []

        if not isinstance(self.data[key], list):
            return "ERR wrong type for key"

        self.data[key].insert(0, value)
        self.save()
        return "OK"

    # LRANGE key (returns the whole list for now)
    def lrange(self, key):
        value = self.data.get(key)

        if value is None:
            return []

        if not isinstance(value, list):
            return "ERR wrong type for key"

        return value
    
        # LPOP key
    def lpop(self, key):
        value = self.data.get(key)

        if value is None:
            return None

        if not isinstance(value, list):
            return "ERR wrong type for key"

        if not value:
            return None

        popped = value.pop(0)

        # Clean up empty lists so they don't linger as stale keys
        if not value:
            del self.data[key]

        self.save()
        return popped

    # LLEN key
    def llen(self, key):
        value = self.data.get(key)

        if value is None:
            return 0

        if not isinstance(value, list):
            return "ERR wrong type for key"

        return len(value)
        # HSET key field value
    def hset(self, key, field, value):
        if key not in self.data:
            self.data[key] = {}

        if not isinstance(self.data[key], dict):
            return "ERR wrong type for key"

        self.data[key][field] = value
        self.save()
        return "OK"

    # HGET key field
    def hget(self, key, field):
        value = self.data.get(key)

        if value is None:
            return None

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        return value.get(field)

    # HGETALL key
    def hgetall(self, key):
        value = self.data.get(key)

        if value is None:
            return {}

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        return value
    
        # ZADD key score member
    def zadd(self, key, score, member):
        if key not in self.data:
            self.data[key] = {}

        if not isinstance(self.data[key], dict):
            return "ERR wrong type for key"

        try:
            score = float(score)
        except ValueError:
            return "ERR score must be a number"

        self.data[key][member] = score
        self.save()
        return "OK"

    # ZRANGE key (returns members sorted by score, ascending)
    def zrange(self, key):
        value = self.data.get(key)

        if value is None:
            return []

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        # Sort members by their score
        sorted_members = sorted(value.items(), key=lambda item: item[1])
        return [member for member, score in sorted_members]

    # ZSCORE key member
    def zscore(self, key, member):
        value = self.data.get(key)

        if value is None:
            return None

        if not isinstance(value, dict):
            return "ERR wrong type for key"

        return value.get(member)
    
        # INCR key — increments a counter, creating it at 0 first if needed
    def incr(self, key):
        current = self.data.get(key, 0)

        if not isinstance(current, (int, float)):
            return "ERR value is not an integer"

        current += 1
        self.data[key] = current

        # Preserve existing TTL if the key already had one — incr shouldn't reset it
        self.save()
        return current
    
    # RATE_LIMIT key max_requests window_seconds
    def rate_limit(self, key, max_requests, window_seconds):
        try:
            max_requests = int(max_requests)
            window_seconds = int(window_seconds)
        except ValueError:
            return "ERR max_requests and window_seconds must be integers"

        # First request in a fresh window — set counter + TTL together
        if key not in self.data:
            self.data[key] = 1
            self.expiry[key] = time.time() + window_seconds
            self.save()
            return "ALLOWED"

        # Check if window has expired (reuse existing expiry logic)
        if key in self.expiry and time.time() >= self.expiry[key]:
            self.data[key] = 1
            self.expiry[key] = time.time() + window_seconds
            self.save()
            return "ALLOWED"

        # Still within window — increment and check
        self.data[key] += 1
        self.save()

        if self.data[key] > max_requests:
            return "REJECTED"

        return "ALLOWED"

        # RPUSH key value — push to the tail (for FIFO queue behavior)
    def rpush(self, key, value):
        if key not in self.data:
            self.data[key] = []

        if not isinstance(self.data[key], list):
            return "ERR wrong type for key"

        self.data[key].append(value)
        self.save()
        return "OK"

# store = KeyValueStore()

# # store.set("name", "Ahmad")
# # print(store.get_value("name"))


# store.set("session", "abc123", ttl=10)
# print(store.get_value("session"))

# print(store.ttl("session"))

# print("In memory:", store.data, store.expiry)

# with open(store.filepath) as f:
#     print("On disk:", f.read())