import { memo, useState } from "react";
import ChatBot, {
  Settings,
  Styles,
  usePaths,
  useMessages,
} from "react-chatbotify";
import { addToast } from "@heroui/react";
import MarkdownRenderer, {
  MarkdownRendererBlock,
} from "@rcb-plugins/markdown-renderer";

import apiClient from "@/hooks";
import { AgentData, Message, Interrupt } from "@/types";

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
    allowNewline: true,
    enabledPlaceholderText: "请输入信息...",
  },
  fileAttachment: {
    accept: ".md,.txt",
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
  setResult: React.Dispatch<React.SetStateAction<string>>;
  setRunning: (running: boolean) => void;
}

const path_map: Record<string, string> = {
  doc_loader: "upload",
  user_input: "blank",
};

function EmbeddedChatbot({
  chatId,
  agent_data,
  setResult,
  setRunning,
}: EmbeddedChatbotProps) {
  const { goToPath } = usePaths();
  const { injectMessage, removeMessage } = useMessages();
  const [messageMap, setMessageMap] = useState<Record<string, string>>({});

  // 消息处理函数
  const handleMessages = (messages: Message[]) => {
    messages.forEach((message: Message, index: number) => {
      if (!(message.id in messageMap) && message.message_show) {
        if (message.type === "ai") {
          injectMessage(message.content);
        } else {
          injectMessage(message.content, "user");
        }
        setMessageMap({ ...messageMap, [message.id]: message.content });
      }
      if (index === messages.length - 1) {
        setResult(message.content);
      }
    });
  };

  // 中断处理函数
  const handleInterrupts = (interrupts: Interrupt[]) => {
    if (interrupts && interrupts.length > 0) {
      const interrupt = interrupts[0];

      if (interrupt && interrupt.value && interrupt.value.message) {
        injectMessage(interrupt.value.message);
        goToPath(path_map[interrupt.value.type] || "blank");
      } else {
        goToPath("blank");
      }
    } else {
      goToPath("blank");
    }
  };

  // 错误处理函数
  const handleError = (error: any, titlePrefix: string = "请求失败:") => {
    const errorMessage =
      error.response?.data?.error || error.response?.data?.detail || "未知错误";

    addToast({
      title: titlePrefix + errorMessage,
      timeout: 1000,
      shouldShowTimeoutProgress: true,
      color: "danger",
    });
  };

  const flow = {
    start: {
      message: async () => {
        if (chatId) {
          apiClient
            .post("/v1/agent/arun", {
              chat_id: chatId,
              agent_data: agent_data,
              state: {},
            })
            .then((response) => {
              handleMessages(response.data.messages);
              handleInterrupts(response.data.__interrupt__);
            })
            .catch((error) => {
              handleError(error);
            })
            .finally(() => {
              setRunning(false);
            });
        }
      },
      renderMarkdown: ["BOT", "USER"],
    } as MarkdownRendererBlock,
    blank: {
      message: async () => {
        return "";
      },
      chatDisabled: async () => {
        return false;
      },
      path: async () => {
        return "chat";
      },
      renderMarkdown: ["BOT", "USER"],
    } as MarkdownRendererBlock,
    chat: {
      message: async (params: any) => {
        const loadingMsg = await injectMessage("⏳ 正在思考中...");

        apiClient
          .post("/v1/agent/arun", {
            chat_id: chatId,
            agent_data: agent_data,
            state: { messages: params.userInput },
          })
          .then((response) => {
            handleMessages(response.data.messages);
            handleInterrupts(response.data.__interrupt__);
          })
          .catch((error) => {
            handleError(error);
          })
          .finally(() => {
            if (loadingMsg) {
              removeMessage(loadingMsg.id);
            }
          });
      },
      renderMarkdown: ["BOT", "USER"],
    } as MarkdownRendererBlock,
    upload: {
      chatDisabled: true,
      file: async (params: any) => {
        const loadingMsg = await injectMessage("⏳ 正在思考中...");
        const files: FileList = params.files;

        if (files && files.length > 0) {
          const newFiles: Array<{
            file_name: string;
            file_content: string;
          }> = [];
          let processedFiles = 0;

          Array.from(files).forEach((file) => {
            const reader = new FileReader();

            reader.onload = () => {
              newFiles.push({
                file_name: file.name,
                file_content: reader.result as string,
              });

              processedFiles++;
              // 当所有文件都处理完毕时更新状态
              if (processedFiles === files.length) {
                apiClient
                  .post("/v1/agent/arun", {
                    chat_id: chatId,
                    agent_data: agent_data,
                    state: { files: newFiles },
                  })
                  .then(async (response) => {
                    handleMessages(response.data.messages);
                    //await new Promise((resolve) => setTimeout(resolve, 1000));
                    handleInterrupts(response.data.__interrupt__);
                  })
                  .catch((error) => {
                    handleError(error);
                  })
                  .finally(() => {
                    if (loadingMsg) {
                      removeMessage(loadingMsg.id);
                    }
                  });
              }
            };

            reader.readAsDataURL(file);
          });
        }
      },
      renderMarkdown: ["BOT", "USER"],
    } as MarkdownRendererBlock,
  };

  const plugins = [MarkdownRenderer()];

  return (
    <ChatBot
      flow={flow}
      id={chatId}
      plugins={plugins}
      settings={settings}
      styles={styles}
    />
  );
}

export default memo(EmbeddedChatbot);
