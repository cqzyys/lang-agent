import { Route, Routes } from "react-router-dom";
import { useEffect } from "react";
import log from "loglevel";

import HomePage from "@/pages/home";
import FlowPage from "@/pages/flow";
import DocumentPage from "@/pages/document";
import {
  useModelStore,
  useAgentStore,
  useMcpStore,
  useThemeStore,
  useVsStore,
} from "@/store";

if (import.meta.env.MODE === "development") {
  log.setLevel("debug");
} else {
  log.setLevel("warn");
}
const App: React.FC = () => {
  useEffect(() => {
    const loadData = async () => {
      try {
        await Promise.all([
          useModelStore.getState().fetchModels(),
          useAgentStore.getState().fetchReuseAgents(),
          useMcpStore.getState().fetchMcpMap(),
          useVsStore.getState().fetchReuseVectorStores(),
        ]);
      } catch (error) {
        log.error("初始化数据加载失败:", error);
      }
    };

    loadData();
  }, []);

  const { dark } = useThemeStore();

  return (
    <main
      className={
        dark
          ? "dark text-foreground bg-background h-screen"
          : "text-foreground bg-background h-screen"
      }
    >
      <Routes>
        <Route element={<HomePage />} path="/" />
        <Route element={<FlowPage />} path="/flow" />
        <Route element={<DocumentPage />} path="/document" />
      </Routes>
    </main>
  );
};

export default App;
