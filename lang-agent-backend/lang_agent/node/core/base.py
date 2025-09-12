from abc import ABC, abstractmethod
from typing import Optional, Union

from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field, TypeAdapter

__all__ = ["BaseNode", "BaseNodeParam", "BaseNodeData"]


class BaseNodeData(BaseModel):
    name: str = Field(..., description="节点名称")


class BaseNodeParam(BaseModel):
    id: str = Field(..., description="节点ID")
    data: Optional[BaseNodeData] = Field(None, description="节点数据")


class BaseNode(ABC):
    type: str = "base"
    category: str = "node"

    def __init__(self, param: Union[BaseNodeParam, dict], **kwargs):
        adapter = TypeAdapter(BaseNodeParam)
        param = adapter.validate_python(param)
        self.id = param.id
        self.name = param.data.name
        self.kwargs = kwargs

    @abstractmethod
    def invoke(self, state: MessagesState):
        """
        Subclass needs to implement methods
        """

    @abstractmethod
    async def ainvoke(self, state: MessagesState):
        """
        Subclass needs to implement methods
        """
