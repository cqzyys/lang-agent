import asyncio
from typing import Optional, Union

import nest_asyncio
from langchain_core.messages import AIMessage
from pydantic import Field, TypeAdapter

from lang_agent.util import parse_json

from ..core import BaseNodeData, BaseNodeParam
from .base_agent import BaseAgentNode

nest_asyncio.apply()

__all__ = ["ReuseAgentNode", "ReuseAgentNodeParam"]


class ReuseAgentNodeData(BaseNodeData):
    data: Optional[dict] = Field(None, description="Agent数据")


class ReuseAgentNodeParam(BaseNodeParam):
    data: Optional[ReuseAgentNodeData] = Field(default=None, description="节点数据")


class ReuseAgentNode(BaseAgentNode):
    type = "reuse_agent"

    def __init__(self, param: Union[ReuseAgentNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(ReuseAgentNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        asyncio.run(self.compile(param))

    async def compile(self, param: ReuseAgentNodeParam):
        from lang_agent.graph.engine import GraphEngine

        data = parse_json(param.data.data)
        graph_engine = GraphEngine(data)
        await graph_engine.compile()
        self.agent = graph_engine.graph

    def invoke(self, state: dict):
        try:
            response = self.agent.invoke(state)
            if "messages" in response and len(response["messages"]) > 0:
                last_message = AIMessage(
                    content=response["messages"][-1].content, name=self.name
                )
            else:
                last_message = AIMessage(content="返回消息错误", name=self.name)
            return {"messages": [last_message]}
        except Exception as e:
            return {"messages": [AIMessage(content=f"Error: {str(e)}", name=self.name)]}

    async def ainvoke(self, state: dict):
        try:
            response = await self.agent.ainvoke(state)
            if "messages" in response and len(response["messages"]) > 0:
                last_message = AIMessage(
                    content=response["messages"][-1].content, name=self.name
                )
            else:
                last_message = AIMessage(content="返回消息错误", name=self.name)
            return {"messages": [last_message]}
        except Exception as e:
            return {"messages": [AIMessage(content=f"Error: {str(e)}", name=self.name)]}
