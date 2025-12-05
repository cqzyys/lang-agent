from typing import Optional, Union
from pydantic import Field, TypeAdapter
from langchain_core.messages import AIMessage

from lang_agent.util import run_command,CommandResult
from ..core import BaseNode, BaseNodeData, BaseNodeParam


class CommandNodeData(BaseNodeData):
    command: str = Field(..., description="执行命令")
    cwd: Optional[str] = Field(None, description="命令执行目录")
    message_show: Optional[bool] = Field(default=True, description="是否显示消息")


class CommandNodeParam(BaseNodeParam):
    data: Optional[CommandNodeData] = Field(default=None, description="Node Data")


class CommandNode(BaseNode):
    type = "command"

    def __init__(self, param: Union[CommandNodeParam, dict], **kwargs):
        adapter = TypeAdapter(CommandNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.command = param.data.command
        self.cwd = param.data.cwd
        self.message_show = param.data.message_show

    async def ainvoke(self, state: dict):
        comannd_result: CommandResult = run_command(command=self.command,cwd=self.cwd)
        if comannd_result.success:
            content = comannd_result.data
            return {"messages": [
                AIMessage(
                    content=content,
                    name=self.name,
                    message_show=self.message_show
                )
            ]}
        raise Exception(comannd_result.error)
