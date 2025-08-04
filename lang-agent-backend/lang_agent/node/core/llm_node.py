from typing import Optional, Union

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field, TypeAdapter

from lang_agent.setting.manager import resource_manager
from lang_agent.util import parse_args

from .base import BaseNode, BaseNodeData, BaseNodeParam

__all__ = ["LLMNode", "LLMNodeParam"]


class LLMNodeData(BaseNodeData):
    model: str = Field(..., description="模型名称")
    system_prompt: Optional[str] = Field(default="", description="系统提示词")
    user_prompt: Optional[str] = Field(default="", description="用户提示词")


class LLMNodeParam(BaseNodeParam):
    data: Optional[LLMNodeData] = Field(default=None, description="节点数据")


class LLMNode(BaseNode):
    type = "llm"

    def __init__(self, param: Union[LLMNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(LLMNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.model: BaseLanguageModel = resource_manager.models["llm"][param.data.model]
        self.system_prompt = param.data.system_prompt
        self.user_prompt = param.data.user_prompt

    def invoke(self, state: dict):
        template = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", self.user_prompt),
            ],
            template_format="mustache",
        )
        chain = template | self.model
        args = parse_args(self.system_prompt + self.user_prompt, state)
        message: BaseMessage = chain.invoke(args)
        message.name = self.name
        return {"messages": [message]}

    async def ainvoke(self, state: dict):
        template = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", self.user_prompt),
            ],
            template_format="mustache",
        )
        chain = template | self.model
        args = parse_args(self.system_prompt + self.user_prompt, state)
        message: BaseMessage = await chain.ainvoke(args)
        message.name = self.name
        return {"messages": [message]}
