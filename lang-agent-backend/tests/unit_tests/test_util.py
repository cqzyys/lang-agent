from langchain_core.messages import HumanMessage

from lang_agent.util import (
    async_run,
    complete_content,
    convert_str_to_type,
    error_to_str,
    parse_args,
    parse_json,
    parse_type,
    sync_wrapper,
    run_command,
)


def test_parse_type():
    assert parse_type("str") == str
    assert parse_type("int") == int
    assert parse_type("float") == float
    assert parse_type("bool") == bool
    assert parse_type("list") == list


def test_convert_str_to_type():
    assert convert_str_to_type("123", "int") == 123
    assert convert_str_to_type("true", "bool") is True
    assert convert_str_to_type("[1, 2]", "list") == [1, 2]
    assert convert_str_to_type("1.23", "float") == 1.23


def test_parse_args():
    content = "Hello {{name}}, you have {{count}} messages."
    state = {
        "name": "Alice",
        "count": 5,
        "messages": [HumanMessage(content="Hi there", name="User")],
    }
    args = parse_args(content, state)
    assert args["name"] == "Alice"
    assert args["count"] == 5


def test_complete_content():
    content = "Hello {{name}}, you have {{count}} messages."
    state = {
        "name": "Alice",
        "count": 5,
        "messages": [HumanMessage(content="Hi there", name="User")],
    }
    result = complete_content(content, state)
    assert result == "Hello Alice, you have 5 messages."


def test_sync_wrapper():
    @sync_wrapper
    async def dummy_coro():
        return "success"

    result = dummy_coro()
    assert result == "success"


def test_async_run():
    async def dummy_coro():
        return "success"

    result = async_run(dummy_coro())
    assert result == "success"


def test_parse_json():
    assert parse_json('{"key": "value"}') == {"key": "value"}
    assert parse_json("invalid json") == "invalid json"


def test_error_to_str():
    class MockHTTPException(Exception):
        detail = "Not Found"

    he = MockHTTPException()
    assert error_to_str(he) == "Not Found"

def test_run_command():
    result = run_command("echo Hello World")
    assert result.success
    assert result.data.strip().strip("'\"") == "Hello World"
    assert result.error is None
