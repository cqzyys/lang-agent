import traceback
from typing import Optional, Union

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from lang_agent.setting.manager import resource_manager
from lang_agent.util import parse_args,complete_content

from .base import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["VLMNode", "VLMNodeParam"]


class VLMNodeData(BaseNodeData):
    model: str = Field(..., description="模型名称")
    system_prompt: Optional[str] = Field(default="", description="系统提示词")
    user_prompt: Optional[str] = Field(default="", description="用户提示词")
    image_url: Optional[str] = Field(default="", description="图片URL")
    message_show: Optional[bool] = Field(default=True, description="是否显示消息")


class VLMNodeParam(BaseNodeParam):
    data: Optional[VLMNodeData] = Field(default=None, description="节点数据")


class VLMNode(BaseNode):
    type = "vlm"

    def __init__(self, param: Union[VLMNodeParam, dict], **kwargs):
        adapter = TypeAdapter(VLMNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.model: BaseLanguageModel = resource_manager.models["vlm"][param.data.model]
        self.system_prompt = param.data.system_prompt
        self.user_prompt = param.data.user_prompt
        self.image_url = param.data.image_url
        self.message_show = param.data.message_show

    async def ainvoke(self, state: dict):
        try:
            template = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(
                        content=[
                            {"type": "text", "text": self.user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": complete_content(self.image_url,state),
                                }
                            },
                        ]
                    )
                ],
                template_format="mustache",
            )
            chain = template | self.model
            args = parse_args(self.system_prompt + self.user_prompt, state)
            raw_message: BaseMessage = await chain.ainvoke(args)
            message: AIMessage = AIMessage(
                content = raw_message.content,
                name = self.name,
                message_show = self.message_show
            )
            return {"messages": [message]}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
