import { Route, Routes } from "react-router-dom";
import { useEffect } from "react";
import log from "loglevel";

import HomePage from "@/pages/home";
import FlowPage from "@/pages/flow";
import {
  useModelStore,
  useAgentStore,
  useMcpStore,
  useThemeStore,
} from "@/store";

if (import.meta.env.MODE === "development") {
  log.setLevel("debug");
} else {
  log.setLevel("warn");
}
function App() {
  useEffect(() => {
    const loadData = async () => {
      try {
        await Promise.all([
          useModelStore.getState().fetchModels(),
          useAgentStore.getState().fetchReuseAgents(),
          useMcpStore.getState().fetchMcpMap(),
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
      </Routes>
    </main>
  );
}

export default App;
