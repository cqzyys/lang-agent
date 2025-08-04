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
  Select,
  SelectItem,
  SharedSelection,
  Switch,
  Textarea,
} from "@heroui/react";

import apiClient from "@/hooks";
import { Model } from "@/types";

const types = [
  { id: "llm", name: "llm" },
  { id: "embedding", name: "embedding" },
];

const channels = [{ id: "openai", name: "openai" }];

type ModalProps = {
  id: string | undefined;
  isOpen: boolean;
  onOpenChange: () => void;
  onRefresh: () => void;
  setRunning: (running: boolean) => void;
};

function ModelSaveModal({
  id,
  isOpen,
  onOpenChange,
  onRefresh,
  setRunning,
}: ModalProps) {
  const init_model: Model = {
    id: "",
    type: "llm",
    name: "",
    channel: "openai",
    model_args:
      '{"base_url": "https://api.openai.com/v1","api_key": "sk-","model": "gpt-4o"}',
    disabled: false,
  };
  const [model, setModel] = useState<Model>(init_model);

  useEffect(() => {
    const fetchData = async () => {
      apiClient
        .get(`/v1/model/select?id=${id}`)
        .then((response) => {
          setModel(response.data.data);
        })
        .catch((error) => {
          addToast({
            title: "获取模型数据失败:" + error.response.data.error,
            timeout: 1000,
            shouldShowTimeoutProgress: true,
            color: "danger",
          });
        });
    };

    if (id) {
      fetchData();
    } else {
      setModel(init_model);
    }
  }, [id]);

  const onSave = useCallback(() => {
    setRunning(true);
    apiClient
      .post("/v1/model/save", model)
      .then(() => {
        setRunning(false);
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
  }, [model]);

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
                  placeholder="请输入模型名称"
                  radius="sm"
                  size="sm"
                  value={model.name}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setModel({ ...model, name: value });
                  }}
                />
                <Select
                  className="nodrag"
                  items={types}
                  label="类型"
                  placeholder="请选择模型类型"
                  selectedKeys={new Set([model.type])}
                  selectionMode="single"
                  size="sm"
                  onSelectionChange={(keys: SharedSelection) => {
                    const value = Array.from(keys)[0] as string;

                    setModel({ ...model, type: value });
                  }}
                >
                  {(type) => <SelectItem key={type.id}>{type.name}</SelectItem>}
                </Select>
                <Select
                  className="nodrag"
                  items={channels}
                  label="渠道"
                  placeholder="请选择渠道"
                  selectedKeys={new Set([model.channel])}
                  selectionMode="single"
                  size="sm"
                  onSelectionChange={(keys: SharedSelection) => {
                    const value = Array.from(keys)[0] as string;

                    setModel({ ...model, channel: value });
                  }}
                >
                  {(channel) => (
                    <SelectItem key={channel.id}>{channel.name}</SelectItem>
                  )}
                </Select>
                <Textarea
                  label="模型连接参数"
                  name="model_args"
                  placeholder="请输入JSON格式的模型连接参数"
                  radius="sm"
                  size="sm"
                  value={model.model_args}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setModel({ ...model, model_args: value });
                  }}
                />
                <Switch
                  className="mr-5"
                  isSelected={model.disabled}
                  size="md"
                  onValueChange={(value: boolean) => {
                    setModel({ ...model, disabled: value });
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

export default memo(ModelSaveModal);
