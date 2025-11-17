import traceback
from typing import Optional, Union
from pydantic import Field, TypeAdapter

from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from lang_agent.logger import get_logger
from .base import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["InputNode", "InputNodeParam"]


class InputNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")
    state_field: str = Field(..., description="状态字段")


class InputNodeParam(BaseNodeParam):
    data: Optional[InputNodeData] = Field(default=None, description="节点数据")


class InputNode(BaseNode):
    type = "user_input"

    def __init__(self, param: Union[InputNodeParam, dict], **kwargs):
        adapter = TypeAdapter(InputNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words
        self.state_field = param.data.state_field

    async def ainvoke(self, state: dict):
        resume_state: dict = interrupt({
            "type": "user_input",
            "message": self.guiding_words
        })
        try:
            if self.state_field == "messages":
                message: HumanMessage = HumanMessage(
                    content=resume_state.get("messages",""),
                    name=self.name
                )
                return {"messages": [message]}
            return {self.state_field: resume_state[self.state_field]}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
