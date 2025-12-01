import asyncio
import contextlib
import os
import subprocess
import re
from collections.abc import Awaitable
from typing import Any, Callable, List, Optional, Set

import nest_asyncio

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

nest_asyncio.apply()

def parse_args(content: str, state: dict):
    """
    解析提示词，使用state中对应的值替换掉提示词中的变量
    """
    if not state:
        return {}
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
    """
    解析文本内容，使用state中对应的值替换掉文本内容中的变量
    """
    if not state:
        return content
    keys: List[str] = re.findall(r"{{(.+?)}}", content)
    messages: List[BaseMessage] = list(reversed(state["messages"]))
    for key in keys:
        if key.startswith("messages['") and key.endswith("']"):
            node_name = re.findall(r"\['(.+?)'\]", key)
            for message in messages:
                if message.name and message.name == node_name[0]:
                    content = content.replace(f"{{{{{key}}}}}", message.content)
                    break
        else:
            content = content.replace(f"{{{{{key}}}}}", str(state[key]))
    return content

def sync_wrapper(coro: Callable[..., Awaitable[Any]]):
    """
    将一个协程函数包装为一个同步函数。
    
    Args:
        coro (Callable[..., Awaitable[Any]]): 协程函数
        
    Returns:
        Callable[..., Any]: 同步函数
    """
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))

    return wrapper

def async_run(coro):
    """
    异步运行一个协程。
    
    Args:
        coro (Awaitable): 协程对象
        
    Returns:
        Any: 协程的返回值
    """
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

class CommandResult(BaseModel):
    success: bool = Field(default=False, description="命令执行成功与否")
    data: Optional[str] = Field(None, description="命令执行成功时的输出")
    error: Optional[str] = Field(None, description="命令执行失败时的错误信息")

@contextlib.contextmanager
def working_directory(cwd:os.PathLike):
    """上下文管理器，用于临时切换工作目录"""
    prev_cwd = os.getcwd()
    os.chdir(cwd)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

def run_command(command:str, cwd:os.PathLike = None) -> CommandResult:
    """
    运行命令，并返回命令执行结果。
    
    Args:
        command (str): 要运行的命令
        cwd (os.PathLike, optional): 运行命令的目录。默认为None，表示使用当前目录。
        
    Returns:
        CommandResult: 命令执行结果
    """
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'

    with working_directory(cwd) if cwd else contextlib.nullcontext():
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            check=False,
            encoding='utf-8',
            errors='ignore',
            env=env
        )
    if result.returncode == 0:
        return CommandResult(
            success=True,
            data=result.stdout,
        )
    return CommandResult(
        success=False,
        error=result.stderr,
    )
