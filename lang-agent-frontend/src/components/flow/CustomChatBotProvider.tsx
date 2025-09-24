import { ChatBotProvider, useMessages } from "react-chatbotify";
import { Panel } from "@xyflow/react";
import { Button } from "@heroui/button";
import { nanoid } from "nanoid";
import { addToast } from "@heroui/react";
import { useRef } from "react";

import EmbeddedChatbot from "./EmbeddedChatbot";

import { Icon } from "@/components";
import apiClient from "@/hooks";
import { AgentData } from "@/types";

interface ChatBotWrapperProps {
  agent_data: AgentData;
  setRunning: (running: boolean) => void;
  setResult: React.Dispatch<React.SetStateAction<string>>;
}

function CustomChatBotWrapper({
  agent_data,
  setRunning,
  setResult,
}: ChatBotWrapperProps) {
  const { messages, injectMessage, removeMessage } = useMessages();
  const chatId = useRef("");
  //执行Agent
  const onRun = () => {
    setRunning(true);
    chatId.current = nanoid(8);
    apiClient
      .post("/v1/agent/arun", {
        chat_id: chatId.current,
        agent_data: agent_data,
        state: {},
      })
      .then((response) => {
        //清除原来的messages
        messages.forEach((message: any) => {
          removeMessage(message.id);
        });
        //重新写入messages
        response.data.messages.forEach((message: any, index: number) => {
          if (message.type === "ai") {
            injectMessage(message.content);
          } else {
            injectMessage(message.content, "user");
          }
          if (index === response.data.messages.length - 1) {
            setResult(message.content);
          }
        });
      })
      .catch((error) => {
        addToast({
          title: "请求失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      })
      .finally(() => {
        setRunning(false);
      });
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
        chatId={chatId.current}
        setResult={setResult}
      />
    </>
  );
}

function CustomChatBotProvider({
  agent_data,
  setRunning,
  setResult,
}: ChatBotWrapperProps) {
  return (
    <ChatBotProvider>
      <CustomChatBotWrapper
        agent_data={agent_data}
        setResult={setResult}
        setRunning={setRunning}
      />
    </ChatBotProvider>
  );
}

export default CustomChatBotProvider;
