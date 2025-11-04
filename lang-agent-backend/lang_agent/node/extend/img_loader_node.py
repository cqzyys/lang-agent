import traceback
from pathlib import Path
from typing import Optional, Union
from pydantic import BaseModel, Field, TypeAdapter

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from lang_agent.logger import get_logger
from lang_agent.util import obj_to_model
from ..core import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["ImgLoaderNode", "ImgLoaderNodeParam"]

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

class FileData(BaseModel):
    file_name: str = Field(..., description="文件名")
    file_content: str = Field(..., description="文件内容")

class ImgLoaderNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")

class ImgLoaderNodeParam(BaseNodeParam):
    data: Optional[ImgLoaderNodeData] = Field(default=None, description="节点数据")


class ImgLoaderNode(BaseNode):
    type = "img_loader"

    def __init__(self, param: Union[ImgLoaderNodeParam, dict], **kwargs):
        adapter = TypeAdapter(ImgLoaderNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words

    async def ainvoke(self, state: dict):
        try:
            resume_state: dict = interrupt({
                "type": "doc_loader",
                "message": self.guiding_words
            })
            image:FileData = obj_to_model(resume_state.get("files", [])[0],FileData)
            encode_data = image.file_content
            return {"messages": [
                AIMessage(content=encode_data, name=self.name)
            ]}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
