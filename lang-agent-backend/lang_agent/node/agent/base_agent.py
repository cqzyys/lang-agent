from langgraph.graph.state import CompiledStateGraph

from lang_agent.node import BaseNode

__all__ = ["BaseAgentNode"]


class BaseAgentNode(BaseNode):
    type: str = "agent"
    category: str = "agent"
    agent: CompiledStateGraph

    def __init__(self, param: dict, state_schema: dict):
        super().__init__(param, state_schema)

    def invoke(self, state: dict):
        return self.agent.invoke(state)

    async def ainvoke(self, state: dict):
        return await self.agent.ainvoke(state)
