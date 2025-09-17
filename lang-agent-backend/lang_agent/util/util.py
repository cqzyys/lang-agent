import asyncio
import re
from collections.abc import Awaitable
from typing import Any, Callable, List, Set

import nest_asyncio
from langchain_core.messages import BaseMessage

nest_asyncio.apply()

def parse_args(content: str, state: dict):
    args = {}
    key_set: Set[str] = set(re.findall(r"{{(.+?)}}", content))
    messages: List[BaseMessage] = list(reversed(state["messages"]))
    remaining_keys = set(key_set)
    for key in key_set:
        if not remaining_keys:
            break
        # 如果key是messages['xxxx']这种形式，那么取messages列表里面对应的content
        if key.startswith("messages['") and key.endswith("']"):
            node_name = re.findall(r"\['(.+?)'\]", key)
            for message in messages:
                if message.name == node_name[0]:
                    args[key] = message.content
                    remaining_keys.discard(key)
                    break
        else:
            args[key] = state[key]
            remaining_keys.discard(key)
    return args

def complete_content(content: str, state: dict) -> str:
    keys: List[str] = re.findall(r"{{(.+?)}}", content)
    messages: List[BaseMessage] = list(reversed(state["messages"]))
    for key in keys:
        if key.startswith("messages['") and key.endswith("']"):
            node_name = re.findall(r"\['(.+?)'\]", key)
            for message in messages:
                if message.name and message.name == node_name[0]:
                    content = content.replace(f"{{{{{key}}}}}", message.content)
                    return content
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

def merge_json(a: dict, b: dict) -> dict:
    """
    深度合并两个JSON对象。
    规则：
    - a中存在的属性不会被b中的相同属性覆盖
    - a中不存在而b中存在的属性会添加到a中
    - 对于嵌套对象，同样遵循上述规则
    
    Args:
        a (dict): 主JSON对象，优先级更高
        b (dict): 次要JSON对象，提供补充属性
        
    Returns:
        dict: 合并后的JSON对象
    """
    result = a.copy()
    for key, value in b.items():
        if key not in result:
            result[key] = value
        elif isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json(result[key], value)
    return result
