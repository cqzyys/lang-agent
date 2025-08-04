import { memo } from "react";
import ChatBot, { Settings, Styles } from "react-chatbotify";
import { addToast } from "@heroui/react";

import apiClient from "@/hooks";
import { AgentData } from "@/types";

const settings: Settings = {
  tooltip: {
    mode: "NEVER",
  },
  header: {
    title: "",
  },
  footer: {
    text: "",
  },
  chatHistory: {
    disabled: true,
  },
  chatWindow: {
    defaultOpen: false,
  },
  chatInput: {
    enabledPlaceholderText: "请输入信息...",
  },
};

const styles: Styles = {
  notificationBadgeStyle: {
    width: "20px",
    height: "20px",
  },
  chatButtonStyle: {
    width: "40px",
    height: "40px",
  },
};

interface EmbeddedChatbotProps {
  chatId: string;
  agent_data: AgentData;
}

function EmbeddedChatbot({ chatId, agent_data }: EmbeddedChatbotProps) {
  const flow = {
    start: {
      message: "",
      path: "loop",
    },
    loop: {
      message: async (params: any) => {
        const loadingMsg = await params.injectMessage("⏳ 正在思考中...");

        apiClient
          .post("/v1/agent/arun", {
            chat_id: chatId,
            agent_data: agent_data,
            state: { messages: params.userInput },
          })
          .then((response) => {
            params.injectMessage(response.data.messages.at(-1).content);
          })
          .catch((error) => {
            addToast({
              title: "请求失败:" + error.response.data.detail,
              timeout: 1000,
              shouldShowTimeoutProgress: true,
              color: "danger",
            });
          })
          .finally(() => {
            params.removeMessage(loadingMsg.id);
          });
      },
      path: "loop",
    },
  };

  return (
    <ChatBot flow={flow} id={chatId} settings={settings} styles={styles} />
  );
}

export default memo(EmbeddedChatbot);
