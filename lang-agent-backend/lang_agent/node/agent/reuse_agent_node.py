import traceback
import asyncio
from typing import Optional, Union

import nest_asyncio
from pydantic import Field, TypeAdapter

from lang_agent.logger import get_logger
from lang_agent.util import parse_json

from ..core import BaseNodeData, BaseNodeParam
from .base_agent import BaseAgentNode

nest_asyncio.apply()

__all__ = ["ReuseAgentNode", "ReuseAgentNodeParam"]

logger = get_logger(__name__)


class ReuseAgentNodeData(BaseNodeData):
    data: Optional[str] = Field(None, description="Agent数据")


class ReuseAgentNodeParam(BaseNodeParam):
    data: Optional[ReuseAgentNodeData] = Field(default=None, description="节点数据")


class ReuseAgentNode(BaseAgentNode):
    type = "reuse_agent"

    def __init__(self, param: Union[ReuseAgentNodeParam, dict], **kwargs):
        adapter = TypeAdapter(ReuseAgentNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        asyncio.run(self.compile(param))

    async def compile(self, param: ReuseAgentNodeParam):
        try:
            from lang_agent.graph.engine import GraphEngine
            data = parse_json(param.data.data)
            self.engine = GraphEngine(
                agent_data = data,
                subgraph = True,
                agent_name = self.name
            )
            await self.engine.compile()
            self.agent = self.engine.graph
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
