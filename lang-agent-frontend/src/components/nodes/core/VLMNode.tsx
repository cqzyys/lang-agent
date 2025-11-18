import { memo, useState } from "react";
import { Handle, Position, NodeResizer } from "@xyflow/react";
import {
  Card,
  CardBody,
  CardHeader,
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerHeader,
  Form,
  Input,
  Select,
  SelectItem,
  Textarea,
  useDisclosure,
} from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  Icon,
  StateList,
  NodeConfigData,
} from "@/components";
import { useModelStore, useFlowStore } from "@/store";

export type VLMNodeData = BaseNodeData & {
  model: string;
  system_prompt?: string;
  user_prompt?: string;
  image_url?: string;
};

export const vlmNodeInitData: NodeConfigData<VLMNodeData> = {
  description: "VLM",
  type: "vlm",
  data: {
    name: "vlm",
    model: "o4-mini",
    system_prompt: "",
    user_prompt: "描述一下这张图片",
    image_url: "",
  },
};

export type VLMNodeProps = NodeProps<VLMNodeData>;

const VLMNode: React.FC<VLMNodeProps> = ({ id, data, onDataChange }) => {
  const { vlms } = useModelStore();
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [activeTriggerRef, setActiveTriggerRef] = useState<{
    current: HTMLInputElement;
  }>();
  const [activeValue, setActiveValue] = useState<string | undefined>(undefined);
  const nodes = useFlowStore((state) => state.nodes);

  return (
    <>
      <NodeResizer isVisible={false} />
      <Card className="m-1 bg-slate-50">
        <CardHeader className="bg-yellow-200">
          <div className="font-black ml-2 w-full">VLM</div>
          <Icon type="setting" onClick={onOpen} />
        </CardHeader>
        <CardBody>
          <Form className="w-full max-w-xs">
            <KeyInput id={id} />
            <Input
              isRequired
              className="nodrag"
              errorMessage="请输入名称"
              label="名称"
              name="name"
              placeholder="请输入名称"
              radius="sm"
              size="sm"
              value={data.name}
              onChange={(e) => onDataChange({ ...data, name: e.target.value })}
            />
            <Select
              className="max-w-xs nodrag"
              label="模型"
              name="model"
              placeholder="请选择模型"
              selectedKeys={new Set([data.model])}
              selectionMode="single"
              size="sm"
              onSelectionChange={(keys) => {
                const value = Array.from(keys)[0] as string;

                onDataChange({ ...data, model: value });
              }}
            >
              {vlms.map((vlm) => (
                <SelectItem key={vlm}>{vlm}</SelectItem>
              ))}
            </Select>
            <Textarea
              disableAutosize
              autoComplete="off"
              className="nodrag"
              label="系统提示词"
              maxRows={3}
              name="system_prompt"
              placeholder="请输入系统提示词"
              radius="sm"
              size="sm"
              value={data.system_prompt || ""}
              onChange={(e) => {
                onDataChange({ ...data, system_prompt: e.target.value });
                setActiveTriggerRef({ current: e.target as HTMLInputElement });
                setActiveValue(e.target.value);
              }}
            />
            <Textarea
              disableAutosize
              autoComplete="off"
              className="nodrag"
              label="用户提示词"
              maxRows={3}
              name="user_prompt"
              placeholder="请输入用户提示词"
              radius="sm"
              size="sm"
              value={data.user_prompt || ""}
              onChange={(e) => {
                onDataChange({ ...data, user_prompt: e.target.value });
                setActiveTriggerRef({ current: e.target as HTMLInputElement });
                setActiveValue(e.target.value);
              }}
            />
            <Input
              isRequired
              className="nodrag"
              errorMessage="请输入图片URL"
              label="图片URL"
              name="image_url"
              placeholder="请输入图片URL"
              radius="sm"
              size="sm"
              value={data.image_url}
              onChange={(e) => {
                onDataChange({ ...data, image_url: e.target.value });
                setActiveTriggerRef({ current: e.target as HTMLInputElement });
                setActiveValue(e.target.value);
              }}
            />
          </Form>
        </CardBody>
      </Card>
      <Handle
        id="input"
        position={Position.Left}
        style={DEFAULT_HANDLE_STYLE}
        type="target"
      />
      <Handle
        id="output"
        position={Position.Right}
        style={DEFAULT_HANDLE_STYLE}
        type="source"
      />

      <Drawer isOpen={isOpen} size="sm" onOpenChange={onOpenChange}>
        <DrawerContent>
          {() => (
            <>
              <DrawerHeader className="flex flex-col gap-1 bg-gray-200">
                详情
              </DrawerHeader>
              <DrawerBody className="bg-slate-100">
                <Form className="w-full max-w-xs">
                  <Input
                    isRequired
                    className="nodrag"
                    errorMessage="请输入名称"
                    label="名称"
                    name="name"
                    placeholder="请输入名称"
                    radius="sm"
                    size="sm"
                    value={data.name}
                    onChange={(e) =>
                      onDataChange({ ...data, name: e.target.value })
                    }
                  />
                  <Select
                    className="max-w-xs nodrag"
                    label="模型"
                    name="model"
                    placeholder="请选择模型"
                    selectedKeys={new Set([data.model])}
                    selectionMode="single"
                    size="sm"
                    onSelectionChange={(keys) => {
                      const value = Array.from(keys)[0] as string;

                      onDataChange({ ...data, model: value });
                    }}
                  >
                    {vlms.map((vlm) => (
                      <SelectItem key={vlm}>{vlm}</SelectItem>
                    ))}
                  </Select>
                  <Textarea
                    className="nodrag"
                    label="系统提示词"
                    maxRows={8}
                    minRows={8}
                    name="system_prompt"
                    placeholder="请输入系统提示词"
                    radius="sm"
                    size="sm"
                    value={data.system_prompt || ""}
                    onChange={(e) => {
                      onDataChange({ ...data, system_prompt: e.target.value });
                    }}
                  />
                  <Textarea
                    className="nodrag"
                    label="用户提示词"
                    maxRows={8}
                    minRows={8}
                    name="user_prompt"
                    placeholder="请输入用户提示词"
                    radius="sm"
                    size="sm"
                    value={data.user_prompt || ""}
                    onChange={(e) => {
                      onDataChange({ ...data, user_prompt: e.target.value });
                    }}
                  />
                  <Input
                    isRequired
                    className="nodrag"
                    errorMessage="请输入图片URL"
                    label="图片URL"
                    name="image_url"
                    placeholder="请输入图片URL"
                    radius="sm"
                    size="sm"
                    value={data.image_url}
                    onChange={(e) =>
                      onDataChange({ ...data, image_url: e.target.value })
                    }
                  />
                </Form>
              </DrawerBody>
            </>
          )}
        </DrawerContent>
      </Drawer>

      <StateList
        data={data}
        nodes={nodes}
        triggerRef={activeTriggerRef}
        value={activeValue}
        onDataChange={onDataChange}
      />
    </>
  );
};

export default memo(VLMNode);
