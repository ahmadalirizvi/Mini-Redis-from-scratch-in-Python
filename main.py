# Mini Redis from scratch in Python

data = {}

# data["name"] = "Ahmad"
# print(data["name"])

class key_value_store:
    def __init__(self):
        self.data = {}
        
        
    def set(self, key, value):
        self.data[key] = value
        return "OK"
    
    def get_value(self, key):
        if key in self.data:
            return self.data[key]
        return None
    

    def del_value(self, key):
        if key in self.data:
            del self.data[key]
            return "OK"
        return "Key not found"
    
    def exists(self, key):
        return key in self.data
    

store = key_value_store()
store.set("name", "Ahmad")
store.set("age", 21)
print(store.get_value("name"))


