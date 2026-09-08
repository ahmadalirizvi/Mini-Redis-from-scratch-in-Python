from storage import KeyValueStore

def test_set_and_get():
    store = KeyValueStore(filepath="test_data.json")
    store.set("foo", "bar")
    assert store.get_value("foo") == "bar"

def test_delete():
    store = KeyValueStore(filepath="test_data.json")
    store.set("foo", "bar")
    store.del_value("foo")
    assert store.get_value("foo") is None