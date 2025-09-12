import traceback
from typing import Optional, Union

from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from ..core import BaseNode, BaseNodeData, BaseNodeParam


logger = get_logger(__name__)

__all__ = ["CounterNode", "CounterNodeParam"]


class CounterNodeData(BaseNodeData):
    state_field: str = Field(..., description="状态字段")


class CounterNodeParam(BaseNodeParam):
    data: Optional[CounterNodeData] = Field(default=None, description="节点数据")


class CounterNode(BaseNode):
    type = "counter"

    def __init__(self, param: Union[CounterNodeParam, dict], **kwargs):
        adapter = TypeAdapter(CounterNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.state_field = param.data.state_field

    def invoke(self, state: dict):
        try:
            count = state.get(self.state_field, 1)
            return {self.state_field: count + 1}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e

    async def ainvoke(self, state: dict):
        return self.invoke(state)
