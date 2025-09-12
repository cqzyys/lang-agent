import traceback
from typing import Optional, Union

from langchain_core.messages import HumanMessage
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from .base import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["InputNode", "InputNodeParam"]


class InputNodeData(BaseNodeData):
    state_field: str = Field(..., description="状态字段")


class InputNodeParam(BaseNodeParam):
    data: Optional[InputNodeData] = Field(default=None, description="节点数据")


class InputNode(BaseNode):
    type = "user_input"

    def __init__(self, param: Union[InputNodeParam, dict], **kwargs):
        adapter = TypeAdapter(InputNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.state_field = param.data.state_field

    def invoke(self, state: dict):
        try:
            if self.state_field == "messages":
                message: HumanMessage = state["messages"][-1]
                message.name = self.name
                return state
            return {self.state_field: state[self.state_field]}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e

    async def ainvoke(self, state: dict):
        return self.invoke(state)
