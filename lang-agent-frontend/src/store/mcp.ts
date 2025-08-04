import { create } from "zustand";

import apiClient from "@/hooks";
import { McpMap } from "@/types";

type McpStore = {
  mcp_map: McpMap;
  fetchMcpMap: () => Promise<void>;
};

export const mcpMap = async () => {
  const { data } = await apiClient.get("/v1/mcp/cached_mcp_map");

  return data.data;
};

export const useMcpStore = create<McpStore>((set) => ({
  mcp_map: {},
  fetchMcpMap: async () => {
    const mcp_map = await mcpMap();

    set({ mcp_map });
  },
}));
