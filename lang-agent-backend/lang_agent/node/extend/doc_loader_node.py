import base64
import os
import shutil
from pathlib import Path
from typing import Optional, Union

from langchain_community.document_loaders.base import BaseLoader
from langchain_core.messages import AIMessage
from pydantic import Field, TypeAdapter
from xid import XID

from ..core import BaseNode, BaseNodeData, BaseNodeParam

__all__ = ["DocLoaderNode", "DocLoaderNodeParam"]

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()


class DocLoaderNodeData(BaseNodeData):
    file_name: str = Field(..., description="文件名")
    file_content: str = Field(..., description="文件内容")


class DocLoaderNodeParam(BaseNodeParam):
    data: Optional[DocLoaderNodeData] = Field(default=None, description="节点数据")


class DocLoaderNode(BaseNode):
    type = "doc_loader"

    def __init__(self, param: Union[DocLoaderNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(DocLoaderNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.file_name = param.data.file_name
        self.file_content = param.data.file_content
        self.file_type = self.file_name.split(".")[-1].lower()
        self.file_path = PROJECT_ROOT / "tmp" / XID().string() / self.file_name

    def invoke(self, state: dict):
        os.makedirs(self.file_path.parent, exist_ok=True)
        _, encoded = self.file_content.split(";base64,", 1)
        file_data = base64.b64decode(encoded)
        with open(self.file_path, "wb") as f:
            f.write(file_data)
        match self.file_type:
            case "pdf":
                from langchain_community.document_loaders import PyPDFLoader

                loader = PyPDFLoader(self.file_path)
            case "txt":
                from langchain.document_loaders import TextLoader

                loader = TextLoader(self.file_path, encoding="utf-8")
            case "docx" | "md":
                from langchain_unstructured import UnstructuredLoader

                loader = UnstructuredLoader(self.file_path)
            case _:
                raise ValueError("Unsupported File Type")
        return self.load(loader)

    def load(self, loader: BaseLoader):
        content = "\n".join([page.page_content for page in loader.load()])
        shutil.rmtree(self.file_path.parent)
        return {"messages": [AIMessage(content=content, name=self.name)]}

    async def ainvoke(self, state: dict):
        return self.invoke(state)
