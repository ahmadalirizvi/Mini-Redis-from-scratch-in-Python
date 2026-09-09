from storage import KeyValueStore


def test_data_survives_restart(tmp_path):
    filepath = str(tmp_path / "test_data.json")

    store1 = KeyValueStore(filepath=filepath)
    store1.set("name", "Ahmad")
    store1.flush()   # force save since writes are now batched

    store2 = KeyValueStore(filepath=filepath)  # simulates a fresh restart
    assert store2.get_value("name") == "Ahmad"


def test_load_handles_missing_file(tmp_path):
    filepath = str(tmp_path / "does_not_exist.json")
    store = KeyValueStore(filepath=filepath)
    assert store.data == {}


def test_load_handles_empty_file(tmp_path):
    filepath = tmp_path / "empty.json"
    filepath.write_text("")
    store = KeyValueStore(filepath=str(filepath))
    assert store.data == {}