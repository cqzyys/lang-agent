import { create } from "zustand";

import apiClient from "@/hooks";

type ModelStore = {
  llms: string[];
  embeddings: string[];
  fetchModels: () => Promise<void>;
};

export const cachedLLM = async () => {
  const { data } = await apiClient.get("/v1/model/cached_llm");

  return data.data;
};

export const cachedEmbedding = async () => {
  const { data } = await apiClient.get("/v1/model/cached_embedding");

  return data.data;
};

export const useModelStore = create<ModelStore>((set) => ({
  llms: [],
  embeddings: [],
  fetchModels: async () => {
    const llms = await cachedLLM();
    const embeddings = await cachedEmbedding();

    set({ llms, embeddings });
  },
}));
