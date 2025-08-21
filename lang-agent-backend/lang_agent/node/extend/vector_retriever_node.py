from typing import Optional, Union

from langchain_core.messages import AIMessage
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from lang_agent.util import complete_content
from lang_agent.setting import resource_manager

from ..core import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["VectorRetrieverNode", "VectorRetrieverNodeParam"]


class VectorRetrieverNodeData(BaseNodeData):
    vs_name: str = Field(..., description="向量库名称")
    keywords: str = Field(..., description="关键字")


class VectorRetrieverNodeParam(BaseNodeParam):
    data: Optional[VectorRetrieverNodeData] = Field(default=None, description="节点数据")


class VectorRetrieverNode(BaseNode):
    type = "vector_retriever"

    def __init__(
        self,
        param: Union[VectorRetrieverNodeParam, dict],
        state_schema: dict
    ):
        adapter = TypeAdapter(VectorRetrieverNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.vs_name: str = param.data.vs_name
        self.keywords: str = param.data.keywords
        self.vs: VectorStore = resource_manager.vectorstore_map[self.vs_name]

    def invoke(self, state: dict):
        keywords = complete_content(self.keywords, state)
        docs: list[Document] = self.vs.similarity_search(keywords)
        content = "\n".join([doc.page_content for doc in docs])
        return {"messages": [AIMessage(content=content, name=self.name)]}

    async def ainvoke(self, state: dict):
        return self.invoke(state)
