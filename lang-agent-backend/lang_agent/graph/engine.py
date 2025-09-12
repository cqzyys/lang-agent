from typing import (
    Any,
    Optional,
    Type,
)

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot

from lang_agent.edge import ConditionEdge
from lang_agent.edge.util import EdgeData, Target
from lang_agent.node import BaseNode
from lang_agent.node.agent import BaseAgentNode
from lang_agent.node.node_factory import NodeFactory
from lang_agent.setting import async_checkpointer
from lang_agent.util import parse_type


class DynamicState(MessagesState):
    pass


class GraphEngine:
    def __init__(self, agent_data: dict, config: Optional[Type[Any]] = None):
        self.agent_data = agent_data
        self.state_schema = agent_data["state_schema"]
        self.graph_config = config
        self.node_map = {}
        self.edge_map = {}
        self.graph = None
        self.subgraphs = False

    async def compile(self):
        nodes: list[dict] = self.agent_data["nodes"]
        edges: list[dict] = self.agent_data["edges"]
        for key, value in self.state_schema.items():
            if key == "messages":
                continue
            DynamicState.__annotations__[key] = parse_type(value)
        graph_builder = StateGraph(DynamicState)
        start_node, end_nodes, input_nodes = await self._init_nodes(
            graph_builder, nodes
        )
        await self._init_edges(graph_builder, edges, start_node, end_nodes)
        graph: CompiledStateGraph = graph_builder.compile(
            checkpointer=await async_checkpointer(), interrupt_before=input_nodes
        )
        graph.get_graph().print_ascii()
        self.graph = graph

    async def _init_nodes(self, graph_builder: StateGraph, nodes: list[dict]):
        start_node: str = None
        end_nodes: list[str] = []
        input_nodes: list[str] = []
        for param in nodes:
            node: BaseNode = NodeFactory.instance(param, state_schema=self.state_schema)
            if node.__class__.type == "start":
                start_node = node.name
            if node.__class__.type == "end":
                end_nodes.append(node.name)
            if node.__class__.type == "user_input":
                input_nodes.append(node.name)
            if isinstance(node, BaseAgentNode):
                graph_builder.add_node(node.name, node.agent)
                self.subgraphs = True
            else:
                graph_builder.add_node(node.name, node.ainvoke)
            self.node_map[node.name] = node
        return start_node, end_nodes, input_nodes

    async def _init_edges(
        self, graph_builder: StateGraph, edges, start_node: str, end_nodes: list[str]
    ):
        for param in edges:
            if param["source_name"] in self.edge_map:
                edge_data = self.edge_map[param["source_name"]]
            else:
                edge_data: EdgeData = EdgeData(
                    source=param["source"], source_name=param["source_name"]
                )
            if param["type"] == "default":
                edge_data.targets[param["target_name"]] = Target(
                    type=param["type"],
                    target=param["target"],
                    target_name=param["target_name"],
                )
            if param["type"] == "condition":
                edge_data.targets[param["target_name"]] = Target(
                    type=param["type"],
                    target=param["target"],
                    target_name=param["target_name"],
                    expr=param["data"]["expr"],
                )
            if param["source_name"] not in self.edge_map:
                self.edge_map[edge_data.source_name] = edge_data

        graph_builder.add_edge(START, start_node)
        for edge_data in self.edge_map.values():
            default_targets = [
                target
                for target in edge_data.targets.values()
                if target.type == "default"
            ]
            condition_targets = [
                target
                for target in edge_data.targets.values()
                if target.type == "condition"
            ]
            for target in default_targets:
                graph_builder.add_edge(edge_data.source_name, target.target_name)
            if len(condition_targets) > 0:
                edge = ConditionEdge(edge_data.source_name, condition_targets)
                graph_builder.add_conditional_edges(edge.source, edge.route)
        for end_node in end_nodes:
            graph_builder.add_edge(end_node, END)

    async def ainvoke(self, state: dict, subgraphs: bool = False) -> dict:
        if "messages" not in state:
            state["messages"] = []
        snapshot: StateSnapshot = await self.graph.aget_state(
            config=self.graph_config, subgraphs=subgraphs
        )
        if snapshot.next == ():
            return await self.graph.ainvoke(
                input=state,
                config=self.graph_config,
                subgraphs=subgraphs
            )
        return await self.aresume(state,subgraphs)


    async def aresume(self, state: dict, subgraphs: bool = False) -> dict:
        def _get_config(snapshot: StateSnapshot):
            if subgraphs:
                subgraphs_config = self._get_subgraphs_config(snapshot)
                if subgraphs_config is not None:
                    return subgraphs_config
            return snapshot.config

        snapshot: StateSnapshot = await self.graph.aget_state(
            config=self.graph_config,
            subgraphs=subgraphs
        )
        config = _get_config(snapshot)
        if state is not None:
            await self.graph.aupdate_state(config=config, values=state)
            snapshot: StateSnapshot = await self.graph.aget_state(
                config=self.graph_config,
                subgraphs=subgraphs
            )
            config = _get_config(snapshot)            
        return await self.graph.ainvoke(
            input=None,
            config=config,
            subgraphs=subgraphs
        )


    def _get_subgraphs_config(self,snapshot: StateSnapshot):
        for task in snapshot.tasks:
            if task.name == snapshot.next[0]:
                sub_snapshot = task.state
                if sub_snapshot:
                    config = sub_snapshot.config
                    sub_config = self._get_subgraphs_config(sub_snapshot)
                    if sub_config is not None:
                        config = sub_config
                    return config
                return None
            return None
