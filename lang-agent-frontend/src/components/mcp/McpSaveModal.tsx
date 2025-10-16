import { memo, useCallback, useEffect, useState } from "react";
import {
  addToast,
  Button,
  Input,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  Switch,
  Textarea,
} from "@heroui/react";

import { apiClient } from "@/util";
import { Mcp } from "@/types";

type McpProps = {
  id: string | undefined;
  isOpen: boolean;
  onOpenChange: () => void;
  onRefresh: () => void;
  setRunning: (running: boolean) => void;
};

function McpSaveModal({
  id,
  isOpen,
  onOpenChange,
  onRefresh,
  setRunning,
}: McpProps) {
  const init_mcp: Mcp = {
    id: "",
    name: "",
    description: "",
    mcp_args: '{"url":"","transport":"sse"}',
    disabled: false,
  };
  const [mcp, setMcp] = useState<Mcp>(init_mcp);

  useEffect(() => {
    if (id) {
      apiClient
        .get(`/v1/mcp/select?id=${id}`)
        .then((response) => {
          setMcp(response.data.data);
        })
        .catch((error) => {
          addToast({
            title: "获取MCP数据失败:" + error.response.data.error,
            timeout: 1000,
            shouldShowTimeoutProgress: true,
            color: "danger",
          });
        });
    } else {
      setMcp(init_mcp);
    }
  }, [id]);

  const onSave = useCallback(() => {
    setRunning(true);
    apiClient
      .post("/v1/mcp/save", mcp)
      .then(() => {
        addToast({
          title: "保存成功",
          timeout: 1000,
          shouldShowTimeoutProgress: true,
        });
        onRefresh();
      })
      .catch((error) => {
        addToast({
          title: "保存失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      })
      .finally(() => {
        setRunning(false);
      });
  }, [mcp]);

  return (
    <>
      <Modal isOpen={isOpen} placement="top-center" onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">保存</ModalHeader>
              <ModalBody>
                <Input
                  label="名称"
                  name="name"
                  placeholder="请输入MCP名称"
                  radius="sm"
                  size="sm"
                  value={mcp.name}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setMcp({ ...mcp, name: value });
                  }}
                />
                <Textarea
                  label="说明"
                  name="description"
                  placeholder="请输入MCP说明"
                  radius="sm"
                  size="sm"
                  value={mcp.description}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setMcp({ ...mcp, description: value });
                  }}
                />
                <Textarea
                  label="MCP参数"
                  name="mcp_args"
                  placeholder="请输入JSON格式的MCP参数"
                  radius="sm"
                  size="sm"
                  value={mcp.mcp_args}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setMcp({ ...mcp, mcp_args: value });
                  }}
                />
                <Switch
                  className="mr-5"
                  isSelected={mcp.disabled}
                  size="md"
                  onValueChange={(value: boolean) => {
                    setMcp({ ...mcp, disabled: value });
                  }}
                >
                  是否禁用
                </Switch>
              </ModalBody>
              <ModalFooter>
                <Button
                  color="primary"
                  onPress={() => {
                    onSave();
                    onClose();
                  }}
                >
                  确定
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}

export default memo(McpSaveModal);
