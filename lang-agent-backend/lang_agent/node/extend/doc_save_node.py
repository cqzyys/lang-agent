import traceback
from typing import Optional, Union
from pydantic import Field, TypeAdapter

from lang_agent.util.util import complete_content
from lang_agent.logger import get_logger
from ..core import BaseNode, BaseNodeData, BaseNodeParam


logger = get_logger(__name__)

class DocSaveNodeData(BaseNodeData):
    content: str = Field(..., description="文档内容")
    save_path: str = Field(..., description="文档存储路径")


class DocSaveNodeParam(BaseNodeParam):
    data: Optional[DocSaveNodeData] = Field(default=None, description="Node Data")


class DocSaveNode(BaseNode):
    type = "doc_save"

    def __init__(self, param: Union[DocSaveNodeParam, dict], **kwargs):
        adapter = TypeAdapter(DocSaveNodeParam)
        param = adapter.validate_python(param)
        self.content = param.data.content
        self.save_path = param.data.save_path
        super().__init__(param, **kwargs)

    def invoke(self, state: dict):
        try:
            content = complete_content(self.content, state)
            with open(self.save_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
    async def ainvoke(self, state: dict):
        self.invoke(state)
        return state
