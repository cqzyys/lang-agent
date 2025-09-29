import { create } from "zustand";

import { apiClient } from "@/util";

type VsStore = {
  vectorstores: string[];
  fetchReuseVectorStores: () => Promise<void>;
};

export const useVsStore = create<VsStore>((set) => ({
  vectorstores: [],
  fetchReuseVectorStores: async () => {
    const { data } = await apiClient.get("/v1/vectorstore/cached_vectorstores");

    set({
      vectorstores: data.data,
    });
  },
}));
