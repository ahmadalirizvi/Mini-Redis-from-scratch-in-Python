from storage import KeyValueStore
from parser import handle_command


def make_store(tmp_path):
    return KeyValueStore(filepath=str(tmp_path / "test_data.json"))


def test_set_command(tmp_path):
    store = make_store(tmp_path)
    result = handle_command(store, "SET name Ahmad")
    assert result == "OK"
    assert store.get_value("name") == "Ahmad"


def test_get_command_nil(tmp_path):
    store = make_store(tmp_path)
    result = handle_command(store, "GET nope")
    assert result == "(nil)"


def test_unknown_command(tmp_path):
    store = make_store(tmp_path)
    result = handle_command(store, "FOO bar")
    assert "ERR" in result


def test_set_wrong_args(tmp_path):
    store = make_store(tmp_path)
    result = handle_command(store, "SET onlykey")
    assert "ERR" in result
    