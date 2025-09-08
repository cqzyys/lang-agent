from typing import Optional, Union

from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from lang_agent.util import complete_content
from lang_agent.setting.manager import resource_manager

from ..core import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["VectorIngestNode", "VectorIngestNodeParam"]


class VectorIngestNodeData(BaseNodeData):
    vs_name: str = Field(..., description="向量库名称")
    content: str = Field(..., description="文档内容")
    description: str = Field(..., description="文档描述")


class VectorIngestNodeParam(BaseNodeParam):
    data: Optional[VectorIngestNodeData] = Field(default=None, description="节点数据")


class VectorIngestNode(BaseNode):
    type = "vector_ingest"

    def __init__(self, param: Union[VectorIngestNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(VectorIngestNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.vs_name: str = param.data.vs_name
        self.content: str = param.data.content
        self.description: str = param.data.description
        self.vs: VectorStore = resource_manager.vectorstore_map[self.vs_name]
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n","\n","."," ","。"],
            chunk_size=1024,
            chunk_overlap=50,
        )

    def invoke(self, state: dict):
        content = complete_content(self.content, state)
        texts = self.text_splitter.split_text(content)
        metadatas = [
            {
                "source": f"{self.description}_{i}"
            }
            for i in range(len(texts))
        ]
        self.vs.add_texts(texts=texts,metadatas=metadatas)

    async def ainvoke(self, state: dict):
        self.invoke(state)
