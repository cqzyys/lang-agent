import json
from typing import Optional, Union

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field, TypeAdapter

from lang_agent.db import Agent, select_agent_by_name
from lang_agent.setting.manager import resource_manager

from ..core import BaseNodeData, BaseNodeParam
from .base_agent import BaseAgentNode
from .reuse_agent_node import ReuseAgentNode, ReuseAgentNodeData, ReuseAgentNodeParam

__all__ = ["SupervisorAgentNode", "SupervisorAgentNodeParam"]


class SupervisorState(MessagesState):
    next: Optional[str] = Field(default="", description="下一个步骤")
    steps: int = Field(default=0, description="最大步数")


class RouteResponse(BaseModel):
    next: Optional[str] = Field(default=None, description="下一个步骤")


class SupervisorAgentNodeData(BaseNodeData):
    model: str = Field(..., description="模型名称")
    agents: Optional[list[str] | str] = Field(default=[], description="代理列表")


class SupervisorAgentNodeParam(BaseNodeParam):
    data: Optional[SupervisorAgentNodeData] = Field(
        default=None, description="节点数据"
    )


class SupervisorAgentNode(BaseAgentNode):
    type = "supervisor_agent"

    def __init__(
        self, param: Union[SupervisorAgentNodeParam, dict], **kwargs
    ):
        adapter = TypeAdapter(SupervisorAgentNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.max_steps = 5
        self.model: BaseLanguageModel = resource_manager.models["llm"][param.data.model]
        self.agents: list[Agent] = self.get_agents(param.data.agents)
        self._init_members()
        self.agent = self.compile()

    def get_agents(self, agent_names: list[str] | str) -> list[Agent]:
        if isinstance(agent_names, str):
            agent_names = agent_names.split(",")
        return [select_agent_by_name(agent_name) for agent_name in agent_names]

    def _init_members(self):
        errors, members, options = [], [], []
        for agent in self.agents:
            if not agent.description:
                errors.append(f"Agent description is missing for {agent.name}")
            members.append(f"{agent.name}: {agent.description}")
            options.append(agent.name)
        if errors:
            raise ValueError("\n".join(errors))
        self.members = "\n".join(members)
        self.options = ",".join(options + ["FINISH"])

    def _supervisor(self, state: SupervisorState):
        messages = state.get("messages", [])
        if "steps" not in state:
            state["steps"] = 0
        user_prompt = """
            你是一名管理者，负责协调多个人员的工作。
            你管辖的人员的情况如下：
            {{members}}
            这是你可以选择的选项：
            {{options}}
            你需要分析历史会话，选择最合适的人员来进行下一步的工作，
            如果你认为目标已达成、用户的问题已被解决、或无法继续推进，请选择 'FINISH'。
            请始终以JSON格式{"next":"xxxxxx"}输出结果，不要输出其它内容
        """
        template = ChatPromptTemplate.from_messages(
            [MessagesPlaceholder(variable_name="messages"), ("user", user_prompt)],
            template_format="mustache",
        ).partial(members=self.members, options=self.options)
        supervisor_chain = template | self.model.with_structured_output(
            schema=RouteResponse
        )
        result: RouteResponse = supervisor_chain.invoke({"messages": messages})
        return {"next": result.next, "steps": state["steps"] + 1}

    def _route(self, state: SupervisorState):
        next_step = state["next"]
        if next_step not in self.options.split(","):
            return "FINISH"
        return next_step if state["steps"] <= self.max_steps else "FINISH"

    def compile(self):
        graph_builder = StateGraph(SupervisorState)
        graph_builder.add_node("Supervisor", self._supervisor)
        for agent in self.agents:
            agent_data = json.loads(agent.data)
            param: ReuseAgentNodeParam = ReuseAgentNodeParam(id=agent.id)
            param.data = ReuseAgentNodeData(name=agent.name, data=agent_data)
            reuse_agent = ReuseAgentNode(
                param,
                state_schema = agent_data["state_schema"]
            )
            graph_builder.add_node(agent.name, reuse_agent.ainvoke)
        graph_builder.add_edge(START, "Supervisor")
        route = {agent.name: agent.name for agent in self.agents}
        route["FINISH"] = END
        graph_builder.add_conditional_edges("Supervisor", self._route, route)
        for agent in self.agents:
            graph_builder.add_edge(agent.name, "Supervisor")
        graph = graph_builder.compile()
        graph.get_graph().print_ascii()
        return graph
