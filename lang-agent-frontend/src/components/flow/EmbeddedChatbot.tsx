import { memo } from "react";
import ChatBot, { Settings, Styles, usePaths } from "react-chatbotify";
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

  const flow = {
    start: {
      message: async (params: any) => {
        if (chatId) {
          apiClient
            .post("/v1/agent/arun", {
              chat_id: chatId,
              agent_data: agent_data,
              state: {},
            })
            .then((response) => {
              let last_message = response.data.messages.at(-1);

              params.injectMessage(last_message.content);
              setResult(last_message.content);
              //如果返回状态有__interrupt__代表graph执行中断
              const interrupts = response.data.__interrupt__;

              if (interrupts) {
                params.injectMessage(interrupts[0]["value"]["messages"]);

                goToPath(
                  path_map[interrupts[0]["value"]["interrupt_type"]] || "blank",
                );
              } else {
                goToPath("blank");
              }
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
        const loadingMsg = await params.injectMessage("⏳ 正在思考中...");

        apiClient
          .post("/v1/agent/arun", {
            chat_id: chatId,
            agent_data: agent_data,
            state: { messages: params.userInput },
          })
          .then((response) => {
            let last_message = response.data.messages.at(-1);

            params.injectMessage(last_message.content);
            setResult(last_message.content);
            const interrupts = response.data.__interrupt__;

            if (interrupts) {
              goToPath(
                path_map[interrupts[0]["value"]["interrupt_type"]] || "blank",
              );
            } else {
              goToPath("blank");
            }
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
    },
    upload: {
      chatDisabled: true,
      file: async (params: any) => {
        const uploadingMsg = await params.injectMessage("⏳ 文档上传中...");
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
                    let last_message = response.data.messages.at(-1);

                    params.injectMessage(last_message.content);
                    setResult(last_message.content);
                    const interrupts = response.data.__interrupt__;

                    if (interrupts) {
                      goToPath(
                        path_map[interrupts[0]["value"]["interrupt_type"]] ||
                          "blank",
                      );
                    } else {
                      goToPath("blank");
                    }
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
                    params.removeMessage(uploadingMsg.id);
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
