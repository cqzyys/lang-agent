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
from lang_agent.util.convert import objs_to_models
from ..core import BaseNode, BaseNodeData, BaseNodeParam

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
logger = get_logger(__name__)


try:
    import patoolib
    PATOOL_AVAILABLE = True
except ImportError:
    PATOOL_AVAILABLE = False
    logger.warning(
        "patool module not installed. Please install it with `poetry add patool`."
    )

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

    async def ainvoke(self, state: dict):
        try:
            resume_state: dict = interrupt({
                "type": "doc_loader",
                "message": self.guiding_words
            })
            files: list[FileData] = objs_to_models(
                resume_state.get("files", []),FileData
            )
            tmp_dir_path = PROJECT_ROOT / "tmp" / XID().string()
            tmp_extract_path = tmp_dir_path / "extracted"
            os.makedirs(tmp_dir_path, exist_ok=True)
            os.makedirs(tmp_extract_path, exist_ok=True)
            for file in files:
                _, encoded = file.file_content.split(";base64,", 1)
                file_data = base64.b64decode(encoded)
                tmp_file_path = tmp_dir_path / file.file_name
                async with aiofiles.open(tmp_file_path, "wb") as f:
                    await f.write(file_data)
                file_name: str = file.file_name.split(".")[0]
                file_extension: str = file.file_name.split(".")[1].lower()
                compressed_extensions = {'zip', 'rar'}
                if file_extension in compressed_extensions:
                    if self._extract_archive(tmp_file_path,tmp_extract_path):
                        dir_path = tmp_extract_path / file_name
                        #读取dir_path下的所有文件
                        for f in dir_path.iterdir():
                            logger.info("file: %s",f.name)
                    else:
                        logger.warning("Failed to extract %s",file.file_name)
            return state
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e


    def _extract_archive(self, file_path: Path, extract_path: Path) -> bool:
        if not PATOOL_AVAILABLE:
            logger.warning("patool not available, cannot extract archives")
            return False
        try:
            patoolib.extract_archive(
                str(file_path),
                outdir=str(extract_path),
                interactive=False
            )
            return True
        except Exception as e:
            logger.error("Failed to extract %s: %s",file_path,e)
            return False
