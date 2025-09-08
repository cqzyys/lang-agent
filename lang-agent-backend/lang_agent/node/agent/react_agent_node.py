from typing import Optional, Union

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from pydantic import Field, TypeAdapter

from lang_agent.setting.manager import resource_manager

from ..core import BaseNodeData, BaseNodeParam
from .base_agent import BaseAgentNode

__all__ = ["ReactAgentNode", "ReactAgentNodeParam"]


class ReactAgentNodeData(BaseNodeData):
    model: str = Field(..., description="模型名称")
    tools: Optional[list[str] | str] = Field(default=[], description="工具列表")


class ReactAgentNodeParam(BaseNodeParam):
    data: Optional[ReactAgentNodeData] = Field(default=None, description="节点数据")


class ReactAgentNode(BaseAgentNode):
    type = "react_agent"

    def __init__(self, param: Union[ReactAgentNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(ReactAgentNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)
        self.model: BaseLanguageModel = resource_manager.models["llm"][param.data.model]
        self.tools: list[BaseTool] = self.get_tools(param.data.tools)
        self.agent = create_react_agent(
            model=self.model, tools=self.tools, name=param.data.name
        )

    def get_tools(self, full_names: list[str] | str) -> list[BaseTool]:
        tools: list[BaseTool] = []
        if isinstance(full_names, str):
            for full_name in full_names.split(","):
                mcp_name = full_name.split(".")[0]
                tool_name = full_name.split(".")[1]
                if mcp_name not in resource_manager.mcp_map:
                    continue
                if tool_name not in resource_manager.mcp_map[mcp_name]:
                    continue
                tools.append(resource_manager.mcp_map[mcp_name][tool_name])
        return tools
