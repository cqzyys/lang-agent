import asyncio
import traceback
import base64
import os
import shutil
from pathlib import Path
from typing import Optional, Union
import aiofiles
from pydantic import BaseModel, Field, TypeAdapter
from xid import XID

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from lang_agent.logger import get_logger
from lang_agent.util import objs_to_models,aload_document
from ..core import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["DocLoaderNode", "DocLoaderNodeParam"]

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

class FileData(BaseModel):
    file_name: str = Field(..., description="文件名")
    file_content: str = Field(..., description="文件内容")

class DocLoaderNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")

class DocLoaderNodeParam(BaseNodeParam):
    data: Optional[DocLoaderNodeData] = Field(default=None, description="节点数据")


class DocLoaderNode(BaseNode):
    type = "doc_loader"

    def __init__(self, param: Union[DocLoaderNodeParam, dict], **kwargs):
        adapter = TypeAdapter(DocLoaderNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words

    async def ainvoke(self, state: dict):
        resume_state: dict = interrupt({
            "type": "file_upload",
            "message": self.guiding_words
        })
        try:
            files: list[FileData] = objs_to_models(
                resume_state.get("files", []),
                FileData
            )
            tmp_dir_path = PROJECT_ROOT / "tmp" / XID().string()
            os.makedirs(tmp_dir_path, exist_ok=True)
            contents: list[str] = []
            for file in files:
                _, encoded = file.file_content.split(";base64,", 1)
                file_data = base64.b64decode(encoded)
                file_path = tmp_dir_path / file.file_name
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(file_data)
                docs = await aload_document(str(file_path))
                contents.append(
                    "\n".join([page.page_content for page in docs])
                )
            await asyncio.get_event_loop().run_in_executor(
                None, shutil.rmtree, tmp_dir_path
            )
            return {"messages": [
                AIMessage(content="\n\n".join(contents), name=self.name)
            ]}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
