from storage import KeyValueStore
import time


def make_store(tmp_path):
    return KeyValueStore(filepath=str(tmp_path / "test_data.json"))


def test_ttl_no_expiry_set(tmp_path):
    store = make_store(tmp_path)
    store.set("foo", "bar")
    assert store.ttl("foo") == -1


def test_ttl_missing_key(tmp_path):
    store = make_store(tmp_path)
    assert store.ttl("nope") == -2


def test_ttl_counts_down(tmp_path):
    store = make_store(tmp_path)
    store.set("foo", "bar", ttl=10)
    remaining = store.ttl("foo")
    assert 0 < remaining <= 10


def test_key_expires_after_ttl(tmp_path):
    store = make_store(tmp_path)
    store.set("foo", "bar", ttl=1)
    assert store.get_value("foo") == "bar"
    time.sleep(1.1)
    assert store.get_value("foo") is None


def test_expired_key_removed_from_ttl_check(tmp_path):
    store = make_store(tmp_path)
    store.set("foo", "bar", ttl=1)
    time.sleep(1.1)
    assert store.ttl("foo") == -2