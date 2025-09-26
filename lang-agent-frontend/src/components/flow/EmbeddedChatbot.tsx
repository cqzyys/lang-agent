import { memo } from "react";
import ChatBot, {
  Settings,
  Styles,
  usePaths,
  useMessages,
} from "react-chatbotify";
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

  // 消息处理函数
  const handleMessages = (messages: any[]) => {
    const last_message = messages.at(-1);

    if (last_message) {
      injectMessage(last_message.content);
      setResult(last_message.content);
    }
  };

  // 中断处理函数
  const handleInterrupts = (interrupts: any[]) => {
    if (interrupts && interrupts.length > 0) {
      const interrupt = interrupts[0];

      if (interrupt && interrupt.value && interrupt.value.messages) {
        injectMessage(interrupt.value.messages);
        goToPath(path_map[interrupt.value.interrupt_type] || "blank");
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
    },
    blank: {
      message: "",
      chatDisabled: async () => {
        return false;
      },
      path: "chat",
    },
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
    },
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
              }
            };

            reader.readAsDataURL(file);
          });
        }
      },
    },
  };

  return (
    <ChatBot flow={flow} id={chatId} settings={settings} styles={styles} />
  );
}

export default memo(EmbeddedChatbot);
