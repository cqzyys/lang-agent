from typing import Optional, Union

from langchain_core.messages import AIMessage
from pydantic import Field, TypeAdapter

from .base import BaseNode, BaseNodeData, BaseNodeParam

__all__ = ["StartNode", "StartNodeParam"]


class StartNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")


class StartNodeParam(BaseNodeParam):
    data: Optional[StartNodeData] = Field(default=None, description="节点数据")


class StartNode(BaseNode):
    type = "start"

    def __init__(self, param: Union[StartNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(StartNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.guiding_words = param.data.guiding_words

    def invoke(self, state: dict):
        if self.guiding_words:
            state["messages"] = [AIMessage(content=self.guiding_words, name=self.name)]
        return state

    async def ainvoke(self, state: dict):
        return self.invoke(state)
