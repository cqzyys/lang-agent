import traceback
from typing import Optional, Union
from pathlib import Path

from pydantic import Field, TypeAdapter
from langchain_core.messages import AIMessage

from lang_agent.util.util import complete_content
from lang_agent.logger import get_logger
from ..core import BaseNode, BaseNodeData, BaseNodeParam


logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
DIR_PATH = PROJECT_ROOT / "tmp/download"

class DocDowloadNodeData(BaseNodeData):
    content: str = Field(..., description="文档内容")
    message_show: Optional[bool] = Field(default=True, description="是否显示消息")


class DocDowloadNodeParam(BaseNodeParam):
    data: Optional[DocDowloadNodeData] = Field(default=None, description="Node Data")


class DocDowloadNode(BaseNode):
    type = "doc_dowload"

    def __init__(self, param: Union[DocDowloadNodeParam, dict], **kwargs):
        adapter = TypeAdapter(DocDowloadNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.content = param.data.content
        self.message_show = param.data.message_show


    async def ainvoke(self, state: dict):
        try:
            content = complete_content(self.content, state)
            file_name = f"{self.name}.md"
            file_path = DIR_PATH / file_name
            DIR_PATH.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            message = AIMessage(
                content = f"📥 [{self.name}](http://127.0.0.1:8810/api/v1/file/download/{file_name})",
                name = self.name,
                message_show = self.message_show,
            )
            return {"messages": message}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
