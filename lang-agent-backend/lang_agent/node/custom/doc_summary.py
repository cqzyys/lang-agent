import asyncio
import traceback
import base64
import os
import shutil
from typing import Optional, Union
from pathlib import Path

from xid import XID
from pydantic import BaseModel, Field, TypeAdapter
import aiofiles

from langgraph.types import interrupt

from lang_agent.logger import get_logger
from ..core import BaseNode, BaseNodeData, BaseNodeParam

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
logger = get_logger(__name__)


class FileData(BaseModel):
    file_name: str = Field(..., description="文件名")
    file_content: str = Field(..., description="文件内容")

class DocSummaryNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")


class DocSummaryNodeParam(BaseNodeParam):
    data: Optional[DocSummaryNodeData] = Field(default=None, description="Node Data")


class DocSummaryNode(BaseNode):
    type = "doc_summary"

    def __init__(self, param: Union[DocSummaryNodeParam, dict], **kwargs):
        adapter = TypeAdapter(DocSummaryNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words
        self.dir_path = PROJECT_ROOT / "tmp" / XID().string()
        os.makedirs(self.dir_path, exist_ok=True)

    async def ainvoke(self, state: dict):
        try:
            resume_state: dict = interrupt({
                "type": "doc_loader",
                "message": self.guiding_words
            })
            files: list[FileData] = resume_state.get("files", [])
            for file in files:
                _, encoded = file["file_content"].split(";base64,", 1)
                file_data = base64.b64decode(encoded)
                file_path = self.dir_path / file["file_name"]
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(file_data)
                file_type: str = file.file_name.split(".")[-1].lower()
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
