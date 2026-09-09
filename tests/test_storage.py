from storage import KeyValueStore
import time


def make_store(tmp_path):
    return KeyValueStore(filepath=str(tmp_path / "test_data.json"))


def test_set_and_get(tmp_path):
    store = make_store(tmp_path)
    store.set("foo", "bar")
    assert store.get_value("foo") == "bar"


def test_get_missing_key_returns_none(tmp_path):
    store = make_store(tmp_path)
    assert store.get_value("nope") is None


def test_delete(tmp_path):
    store = make_store(tmp_path)
    store.set("foo", "bar")
    result = store.del_value("foo")
    assert result == "OK"
    assert store.get_value("foo") is None


def test_delete_missing_key(tmp_path):
    store = make_store(tmp_path)
    assert store.del_value("nope") == "Key not found"


def test_exists(tmp_path):
    store = make_store(tmp_path)
    assert store.exists("foo") is False
    store.set("foo", "bar")
    assert store.exists("foo") is True