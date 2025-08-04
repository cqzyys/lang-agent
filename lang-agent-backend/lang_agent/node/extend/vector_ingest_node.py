from typing import Optional, Union

from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from lang_agent.util import complete_content

from ..core import BaseNode, BaseNodeData, BaseNodeParam
from .vector_store_provider import VectorStoreConfig, VectorStoreProvider

logger = get_logger(__name__)

__all__ = ["VectorIngestNode", "VectorIngestNodeParam"]


class VectorIngestNodeData(BaseNodeData, VectorStoreConfig):
    content: str = Field(..., description="文本内容")


class VectorIngestNodeParam(BaseNodeParam):
    data: Optional[VectorIngestNodeData] = Field(default=None, description="节点数据")


class VectorIngestNode(BaseNode):
    type = "vector_ingest"

    def __init__(self, param: Union[VectorIngestNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(VectorIngestNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.content: str = param.data.content
        self.vs: VectorStore = VectorStoreProvider.init(param.data)
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n","\n","."," ","。"],
            chunk_size=1024,
            chunk_overlap=50,
        )

    def invoke(self, state: dict):
        content = complete_content(self.content, state)
        texts = self.text_splitter.split_text(content)
        self.vs.add_texts(texts)

    async def ainvoke(self, state: dict):
        self.invoke(state)
