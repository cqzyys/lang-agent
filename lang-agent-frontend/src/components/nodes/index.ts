export {
  default as StartNode,
  type StartNodeData,
  startNodeInitData,
} from "./core/StartNode";
export { default as EndNode, endNodeInitData } from "./core/EndNode";
export {
  default as UserInputNode,
  type UserInputNodeData,
  userInputNodeInitData,
} from "./core/UserInputNode";
export {
  default as LLMNode,
  type LLMNodeData,
  llmNodeInitData,
} from "./core/LLMNode";
export {
  default as VLMNode,
  type VLMNodeData,
  vlmNodeInitData,
} from "./core/VLMNode";
export {
  default as ReactAgentNode,
  type ReactAgentNodeData,
  reactAgentNodeInitData,
} from "./agent/ReactAgentNode";
export {
  default as SupervisorAgentNode,
  type SupervisorAgentNodeData,
  supervisorAgentNodeInitData,
} from "./agent/SupervisorAgentNode";
export {
  default as ReuseAgentNode,
  type ReUseAgentNodeData,
} from "./agent/ReuseAgentNode";

export interface NodeConfigData<TData extends BaseNodeData = BaseNodeData> {
  type: string;
  description: string;
  data: TData;
}

export interface NodeConfig<
  TData extends BaseNodeData = BaseNodeData,
  TProps extends NodeProps<TData> = NodeProps<TData>,
> extends NodeConfigData<TData> {
  component: React.ComponentType<TProps>;
}

export type BaseNodeData = {
  id?: string;
  type?: string;
  name?: string;
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
