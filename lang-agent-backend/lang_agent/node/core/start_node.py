import traceback
from typing import Optional, Union

from langchain_core.messages import AIMessage
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from .base import BaseNode, BaseNodeData, BaseNodeParam

__all__ = ["StartNode", "StartNodeParam"]

logger = get_logger(__name__)

class StartNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")


class StartNodeParam(BaseNodeParam):
    data: Optional[StartNodeData] = Field(default=None, description="节点数据")


class StartNode(BaseNode):
    type = "start"

    def __init__(self, param: Union[StartNodeParam, dict], **kwargs):
        adapter = TypeAdapter(StartNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words

    async def ainvoke(self, state: dict):
        try:
            if self.guiding_words:
                state["messages"] = [
                    AIMessage(content=self.guiding_words, name=self.name)
                ]
            return state
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
