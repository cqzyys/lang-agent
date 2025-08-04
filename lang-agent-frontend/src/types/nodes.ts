export type BaseNodeData = {
  id?: string;
  type?: string;
  name?: string;
  position?: Record<string, number>;
};

export type NodeProps<T> = {
  id: string;
  data: T;
  onDataChange: (data: T) => void;
};

export type BaseNodeProps = NodeProps<BaseNodeData>;
