import traceback
import base64
import os
import shutil
from pathlib import Path
from typing import Optional, Union

from langchain_community.document_loaders.base import BaseLoader
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field, TypeAdapter
from xid import XID

from lang_agent.logger import get_logger
from ..core import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["DocLoaderNode", "DocLoaderNodeParam"]

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

class FileData(BaseModel):
    file_name: str = Field(..., description="文件名")
    file_content: str = Field(..., description="文件内容")

class DocLoaderNodeData(BaseNodeData):
    files: list[FileData] = Field(..., description="文件列表")


class DocLoaderNodeParam(BaseNodeParam):
    data: Optional[DocLoaderNodeData] = Field(default=None, description="节点数据")


class DocLoaderNode(BaseNode):
    type = "doc_loader"

    def __init__(self, param: Union[DocLoaderNodeParam, dict], **kwargs):
        adapter = TypeAdapter(DocLoaderNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.files = param.data.files
        self.dir_path = PROJECT_ROOT / "tmp" / XID().string()
        os.makedirs(self.dir_path, exist_ok=True)

    def invoke(self, state: dict):
        try:
            contents: list[str] = []
            for file in self.files:
                _, encoded = file.file_content.split(";base64,", 1)
                file_data = base64.b64decode(encoded)
                file_path = self.dir_path / file.file_name
                with open(file_path, "wb") as f:
                    f.write(file_data)
                file_type = file.file_name.split(".")[-1].lower()
                match file_type:
                    case "pdf":
                        from langchain_community.document_loaders import PyPDFLoader
                        loader = PyPDFLoader(file_path)
                    case "txt":
                        from langchain_community.document_loaders import TextLoader
                        loader = TextLoader(file_path, encoding="utf-8")
                    case "docx" | "md":
                        from langchain_unstructured import UnstructuredLoader
                        loader = UnstructuredLoader(file_path)
                    case _:
                        raise ValueError("Unsupported File Type")
                contents.append(self.load(loader))
            shutil.rmtree(self.dir_path)
            return {"messages": [
                AIMessage(content="\n\n".join(contents), name=self.name)
            ]}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e

    def load(self, loader: BaseLoader):
        content = "\n".join([page.page_content for page in loader.load()])
        return content

    async def ainvoke(self, state: dict):
        return self.invoke(state)
