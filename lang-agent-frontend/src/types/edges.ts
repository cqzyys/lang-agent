import { type EdgeProps } from "@xyflow/react";

export type BaseEdgeData = {
  id?: string;
  type?: string;
  source?: string;
  source_name?: string;
};

export type DefaultEdgeData = BaseEdgeData & {
  target?: string;
  target_name?: string;
};

export type ConditionEdgeData = DefaultEdgeData & {
  expr?: string;
};

export type ConditionData = {
  expr?: string;
};

export type ConditionEdgeProps = EdgeProps & {
  data: ConditionData;
  onDataChange: (data: ConditionData) => void;
};

export type LoopEdgeData = DefaultEdgeData & {
  count?: string;
};

export type LoopData = {
  count?: string;
};

export type LoopEdgeProps = EdgeProps & {
  data: LoopData;
  onDataChange: (data: LoopData) => void;
};
