import { create } from "zustand";

import { apiClient } from "@/util";

type ModelStore = {
  llms: string[];
  embeddings: string[];
  vlms: string[];
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

export const cachedVLM = async () => {
  const { data } = await apiClient.get("/v1/model/cached_vlm");

  return data.data;
};

export const useModelStore = create<ModelStore>((set) => ({
  llms: [],
  embeddings: [],
  vlms: [],
  fetchModels: async () => {
    const llms = await cachedLLM();
    const embeddings = await cachedEmbedding();
    const vlms = await cachedVLM();

    set({ llms, embeddings, vlms });
  },
}));
