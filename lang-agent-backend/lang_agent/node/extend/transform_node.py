from typing import Optional, Union

from langchain_core.messages import AIMessage
from pydantic import Field, TypeAdapter

from lang_agent.util import convert_str_to_type

from ..core import BaseNode, BaseNodeData, BaseNodeParam

__all__ = ["TransformNode", "TransformNodeParam"]


class TransformNodeData(BaseNodeData):
    state_field: str = Field(..., description="状态字段")


class TransformNodeParam(BaseNodeParam):
    data: Optional[TransformNodeData] = Field(default=None, description="节点数据")


class TransformNode(BaseNode):
    type = "transform"

    def __init__(self, param: Union[TransformNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(TransformNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.state_field = param.data.state_field

    def invoke(self, state: dict):
        content = state["messages"][-1].content
        if not self.state_field or self.state_field == "messages":
            return {"messages": [AIMessage(content=content, name=self.name)]}
        filed_type: str = self.state_schema.get(self.state_field)
        return {self.state_field: convert_str_to_type(content, filed_type)}

    async def ainvoke(self, state: dict):
        return self.invoke(state)
