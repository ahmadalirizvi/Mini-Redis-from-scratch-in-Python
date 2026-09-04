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
        
    


store = KeyValueStore()

# store.set("name", "Ahmad")
# print(store.get_value("name"))


store.set("session", "abc123", ttl=10)
print(store.get_value("session"))

print(store.ttl("session"))

print("In memory:", store.data, store.expiry)

with open(store.filepath) as f:
    print("On disk:", f.read())