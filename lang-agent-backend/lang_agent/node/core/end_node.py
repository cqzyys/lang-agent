from typing import Union

from pydantic import TypeAdapter
from langchain_core.messages import AIMessage, BaseMessage

from .base import BaseNode, BaseNodeParam

__all__ = ["EndNode", "EndNodeParam"]


class EndNodeParam(BaseNodeParam):
    pass


class EndNode(BaseNode):
    type = "end"

    def __init__(self, param: Union[EndNodeParam, dict], **kwargs):
        adapter = TypeAdapter(EndNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)

    def invoke(self, state: dict):
        subgraph = self.kwargs.get("subgraph",False)
        agent_name = self.kwargs.get("agent_name")
        messages: list[BaseMessage] = state.get("messages")
        # 如果是子图，则在子图结束后补充一个以子图名为name的消息
        if subgraph:
            message = AIMessage(content=messages[-1].content,name=agent_name)
            messages.append(message)
        return state

    async def ainvoke(self, state: dict):
        return self.invoke(state)
