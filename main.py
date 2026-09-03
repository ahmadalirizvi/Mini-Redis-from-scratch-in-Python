# Mini Redis from scratch in Python

data = {}

data["name"] = "Ahmad"
print(data["name"])

class key_value_store:
    def __init__(self):
        self.data = {}
        
        
    def set(key, value):
        data[key] = value
        return "OK"
    
    def get_value(key):
        if key in data:
            return data[key]
        return None
    

    def del_value(key):
        if key in data:
            del data[key]
            return "OK"
        return "Key not found"
    
    def exists(key):
        return key in data
    

set("name", "Ahmad")
set("age", 21)

