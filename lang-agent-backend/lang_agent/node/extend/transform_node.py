import traceback
from typing import Optional, Union

from langchain_core.messages import AIMessage
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from lang_agent.util import convert_str_to_type,complete_content
from ..core import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["TransformNode", "TransformNodeParam"]


class TransformNodeData(BaseNodeData):
    origin_state_field: Optional[str] = Field(default=None, description="来源状态变量")
    target_state_field: str = Field(..., description="目标状态变量")


class TransformNodeParam(BaseNodeParam):
    data: Optional[TransformNodeData] = Field(default=None, description="节点数据")


class TransformNode(BaseNode):
    type = "transform"

    def __init__(self, param: Union[TransformNodeParam, dict], **kwargs):
        adapter = TypeAdapter(TransformNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.origin_state_field = param.data.origin_state_field
        self.target_state_field = param.data.target_state_field


    def invoke(self, state: dict):
        try:
            if self.origin_state_field:
                content = complete_content(self.origin_state_field, state)
            else:
                content = state["messages"][-1].content
            if not self.target_state_field or self.target_state_field == "messages":
                return {"messages": [AIMessage(content=content, name=self.name)]}
            filed_type: str = self.kwargs.get("state_schema").get(
                self.target_state_field
            )
            return {self.target_state_field: convert_str_to_type(content, filed_type)}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e

    async def ainvoke(self, state: dict):
        return self.invoke(state)
