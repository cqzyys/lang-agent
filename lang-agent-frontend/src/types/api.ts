import type { BaseNodeData, DefaultEdgeData, ConditionEdgeData } from "@/types";

export type AgentData = {
  state_schema: Record<string, any>;
  nodes: Array<BaseNodeData>;
  edges: Array<DefaultEdgeData | ConditionEdgeData>;
};

export type Agent = {
  id?: string;
  type?: string;
  name?: string;
  description?: string;
  data?: Record<string, any>;
  reuse_flag: boolean;
  disabled?: boolean;
};

export type Model = {
  id?: string;
  type: string;
  name?: string;
  channel: string;
  model_args?: string;
  disabled?: boolean;
};

export type Mcp = {
  id?: string;
  name?: string;
  description?: string;
  mcp_args?: string;
  disabled?: boolean;
};

export type McpMap = Record<string, string[]>;
