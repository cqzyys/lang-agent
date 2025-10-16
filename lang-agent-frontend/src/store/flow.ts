import { create } from "zustand";
import { Node } from "@xyflow/react";

type FlowStore = {
  nodes: Node[];
  setNodes: (nodes: Node[]) => void;
};

export const useFlowStore = create<FlowStore>((set) => ({
  nodes: [],
  setNodes: (nodes) => set({ nodes }),
}));
