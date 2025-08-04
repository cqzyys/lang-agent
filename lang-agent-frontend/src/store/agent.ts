import { create } from "zustand";

import apiClient from "@/hooks";
import { Agent } from "@/types";

type AgentStore = {
  reuse_agents: string[];
  fetchReuseAgents: () => Promise<void>;
};

export const useAgentStore = create<AgentStore>((set) => ({
  reuse_agents: [],
  fetchReuseAgents: async () => {
    const { data } = await apiClient.get("/v1/agent/list_reuse");

    set({ reuse_agents: data.data.map((agent: Agent) => agent.name) });
  },
}));
