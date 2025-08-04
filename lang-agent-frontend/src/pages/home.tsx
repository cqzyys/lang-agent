import { Tabs, Tab, Switch } from "@heroui/react";

import AgentPage from "./agent";
import ModelPage from "./model";
import McpPage from "./mcp";

import { Icon } from "@/components";
import { useThemeStore } from "@/store";

function HomePage() {
  const { dark, toggleDark } = useThemeStore();

  return (
    <div className="flex w-full flex-col">
      <div className="flex w-full justify-end">
        <Switch
          className="mr-5"
          isSelected={!dark}
          size="md"
          onValueChange={toggleDark}
        >
          <Icon type="sun" />
        </Switch>
      </div>
      <Tabs aria-label="Options" className="mt-4" isVertical={true}>
        <Tab
          key="agent"
          className="ml-8 mr-8 mt-4 font-black"
          title="Agent配置"
        >
          <AgentPage />
        </Tab>
        <Tab key="model" className="ml-8 mr-8 mt-4 font-black" title="模型配置">
          <ModelPage />
        </Tab>
        <Tab
          key="MCP"
          className="ml-8 mr-8 mt-4 mb-4 font-black"
          title="MCP配置"
        >
          <McpPage />
        </Tab>
      </Tabs>
    </div>
  );
}

export default HomePage;
