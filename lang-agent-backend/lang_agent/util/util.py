import asyncio
import json
import re
from collections.abc import Awaitable
from typing import Any, Callable, List, Set

import nest_asyncio
from langchain_core.messages import BaseMessage

nest_asyncio.apply()

type_map = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
}


def parse_type(content: str):
    return type_map[content]


def convert_str_to_type(value: str, target_type: str):
    if parse_type(target_type) is str:
        return value
    if parse_type(target_type) is int:
        return int(value)
    if parse_type(target_type) is float:
        return float(value)
    if parse_type(target_type) is bool:
        if value in ["true", "True"]:
            return True
        if value in ["false", "False"]:
            return False
        raise ValueError("错误的bool值")
    if parse_type(target_type) is list or target_type is dict:
        return json.loads(value)
    raise ValueError(f"不支持的类型: {target_type}")


def parse_args(content: str, state: dict):
    args = {}
    key_set: Set[str] = set(re.findall(r"{{(.+?)}}", content))
    messages: List[BaseMessage] = state["messages"]
    for key in key_set:
        # 如果key是messages['xxxx']这种形式，那么取messages列表里面对应的content
        if key.startswith("messages['") and key.endswith("']"):
            node_name = re.findall(r"\['(.+?)'\]", key)
            for message in messages:
                if message.name == node_name[0]:
                    args[key] = message.content
        else:
            args[key] = state[key]
    return args


def complete_content(content: str, state: dict) -> str:
    keys: List[str] = re.findall(r"{{(.+?)}}", content)
    messages: List[BaseMessage] = state["messages"]
    for key in keys:
        if key.startswith("messages['") and key.endswith("']"):
            node_name = re.findall(r"\['(.+?)'\]", key)
            for message in messages:
                if message.name == node_name[0]:
                    content = content.replace(f"{{{{{key}}}}}", message.content)
        else:
            content = content.replace(f"{{{{{key}}}}}", str(state[key]))
    return content


def sync_wrapper(coro: Callable[..., Awaitable[Any]]):
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))

    return wrapper


def async_run(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    return loop.run_until_complete(coro)


def parse_json(content: any):
    try:
        if isinstance(content, str):
            if content.startswith("{") and content.endswith("}"):
                return json.loads(content)
            if content.startswith("[") and content.endswith("]"):
                return json.loads(content)
        return content
    except json.JSONDecodeError:
        return content


def error_to_str(error):
    match type(error).__name__:
        case "ValidationError":
            error_messages = [f"{err['loc']}: {err['msg']}" for err in error.errors()]
            return "\n".join(error_messages)
        case "HTTPException" | "IntegrityError" | "DatabaseError":
            return getattr(error, "detail", str(error))
        case "ExceptionGroup":
            exceptions = error.exceptions
            error_messages = []
            for e in exceptions:
                error_messages.append(error_to_str(e))
            return "\n".join(error_messages)
        case _ if hasattr(error, "detail"):
            return str(error.detail)
        case _:
            return f"{type(error).__name__}: {str(error)}"
