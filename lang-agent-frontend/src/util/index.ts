import type { Node, Edge } from "@xyflow/react";

import log from "loglevel";

import { AgentData } from "@/types";

export { apiClient } from "./http";

log.setLevel("debug");

export const getAgentData = (nodes: Node[], edges: Edge[]) => {
  const id_map: Record<string, any> = {};

  nodes.forEach((node: Node) => {
    id_map[node.id] = node.data.name;
  });
  let agent_data: AgentData = { state_schema: {}, nodes: [], edges: [] };

  nodes.map((node: Node) => {
    if (node.type === "start") {
      if (typeof node.data.state_schema === "string") {
        try {
          agent_data.state_schema = JSON.parse(node.data.state_schema);
        } catch (e) {
          log.error("state_schema JSON解析失败", e);
        }
      }
    }
  });
  agent_data.nodes = nodes;
  agent_data.edges = edges.map((edge: Edge) => ({
    ...edge,
    source_name: id_map[edge.source],
    target_name: id_map[edge.target],
  }));

  //log.debug(agent_data);
  return agent_data;
};
