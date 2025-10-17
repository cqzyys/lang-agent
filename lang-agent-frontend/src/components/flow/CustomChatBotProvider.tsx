import { ChatBotProvider, useFlow } from "react-chatbotify";
import { Panel } from "@xyflow/react";
import { Button } from "@heroui/button";
import { nanoid } from "nanoid";
import { memo, useState } from "react";

import EmbeddedChatbot from "./EmbeddedChatbot";

import { Icon } from "@/components";
import { AgentData } from "@/types";

interface ChatBotWrapperProps {
  agent_data: AgentData;
  setRunning: (running: boolean) => void;
  setResult: React.Dispatch<React.SetStateAction<string>>;
}

const CustomChatBotWrapper: React.FC<ChatBotWrapperProps> = ({
  agent_data,
  setRunning,
  setResult,
}) => {
  const [chatId, setChatId] = useState("");
  const { restartFlow } = useFlow();

  //执行Agent
  const onRun = () => {
    setRunning(true);
    setChatId(nanoid(8));
    Promise.resolve().then(() => restartFlow());
  };

  return (
    <>
      <Panel position="top-left" style={{ left: 100 }}>
        <Button
          color="primary"
          size="sm"
          startContent={<Icon color="#006fee" type="run" />}
          variant="shadow"
          onPress={onRun}
        >
          运行
        </Button>
      </Panel>
      <EmbeddedChatbot
        agent_data={agent_data}
        chatId={chatId}
        setResult={setResult}
        setRunning={setRunning}
      />
    </>
  );
};

const App: React.FC<ChatBotWrapperProps> = ({
  agent_data,
  setRunning,
  setResult,
}) => {
  return (
    <ChatBotProvider>
      <CustomChatBotWrapper
        agent_data={agent_data}
        setResult={setResult}
        setRunning={setRunning}
      />
    </ChatBotProvider>
  );
};

export default memo(App);
