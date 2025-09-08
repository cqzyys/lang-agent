import asyncio
from typing import Optional, Union

import nest_asyncio
from langchain_core.messages import AIMessage
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

    def __init__(self, param: Union[ReuseAgentNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(ReuseAgentNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        asyncio.run(self.compile(param))

    async def compile(self, param: ReuseAgentNodeParam):
        from lang_agent.graph.engine import GraphEngine

        data = parse_json(param.data.data)
        self.engine = GraphEngine(data)
        await self.engine.compile()
        self.agent = self.engine.graph

    def invoke(self, state: dict):
        pass
        '''
        try:
            agent_state_schema = parse_json(self.engine.state_schema)
            agent_state = self._adapt_state_schema(state, agent_state_schema)
            response = self.agent.invoke(agent_state)
            if "messages" in response and len(response["messages"]) > 0:
                last_message = AIMessage(
                    content=response["messages"][-1].content, name=self.name
                )
            else:
                last_message = AIMessage(content="返回消息错误", name=self.name)
            return {"messages": [last_message]}
        except Exception as e:
            logger.error(e)
            return {"messages": [AIMessage(content=f"Error: {str(e)}", name=self.name)]}
        '''

    async def ainvoke(self, state: dict):
        pass
        '''
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
            logger.error(e)
            raise
        '''
    def _adapt_state_schema(self, state: dict, agent_state_schema: dict) -> dict:
        """
        根据agent_state_schema构建新的状态字典
        Args:
            state: 原始状态字典
            agent_state_schema: agent的状态模式定义
            
        Returns:
            构建后的新状态字典
        """
        agent_state = {}
        agent_schema_keys = set(agent_state_schema.keys())
        state_keys = set(state.keys())
        
        # 复制在agent_state_schema中存在的键值对
        for key in agent_schema_keys:
            if key in state:
                agent_state[key] = state[key]
            else:
                # agent_state[key] = None
                pass
                
        return agent_state
