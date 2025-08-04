export { default as StartNode, type StartNodeData } from "./core/StartNode";
export { default as EndNode } from "./core/EndNode";
export {
  default as UserInputNode,
  type UserInputNodeData,
} from "./core/UserInputNode";
export { default as LLMNode, type LLMNodeData } from "./core/LLMNode";
export {
  default as ReactAgentNode,
  type ReactAgentNodeData,
} from "./agent/ReactAgentNode";
export {
  default as SupervisorAgentNode,
  type SupervisorAgentNodeData,
} from "./agent/SupervisorAgentNode";
export {
  default as ReuseAgentNode,
  type ReUseAgentNodeData,
} from "./agent/ReuseAgentNode";

export interface NodeConfig<
  TData extends BaseNodeData = BaseNodeData,
  TProps extends NodeProps<TData> = NodeProps<TData>,
> {
  type: string;
  description: string;
  data: TData;
  component: React.ComponentType<TProps>;
}

export type BaseNodeData = {
  id: string;
  type: string;
  name: string;
  position?: Record<string, number>;
  d?: string;
  color?: string;
};

export type NodeProps<T> = {
  id: string;
  data: T;
  onDataChange: (data: T) => void;
};

export type BaseNodeProps = NodeProps<BaseNodeData>;
