# Mini Redis from scratch in Python

import time


class KeyValueStore:

    def __init__(self):
        self.data = {}
        self.expiry = {}

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

        # Check if key has an expiry
        if key in self.expiry:

            # Has the key expired?
            if time.time() >= self.expiry[key]:

                # Delete expired key
                del self.data[key]
                del self.expiry[key]

                return None

        return self.data.get(key)

    # DELETE key
    def del_value(self, key):

        if key in self.data:
            del self.data[key]

            # Also remove expiry information
            self.expiry.pop(key, None)

            return "OK"

        return "Key not found"

    # EXISTS key
    def exists(self, key):

        # Calling get_value() also checks expiration
        return self.get_value(key) is not None

    # TTL key
    def ttl(self, key):

        # Key doesn't exist
        if key not in self.data:
            return -2

        # Key exists but has no expiry
        if key not in self.expiry:
            return -1

        remaining = self.expiry[key] - time.time()

        # Key has expired
        if remaining <= 0:
            del self.data[key]
            del self.expiry[key]
            return -2

        return int(remaining)


store = KeyValueStore()

# store.set("name", "Ahmad")
# print(store.get_value("name"))


store.set("session", "abc123", ttl=10)
print(store.get_value("session"))

print(store.ttl("session"))
