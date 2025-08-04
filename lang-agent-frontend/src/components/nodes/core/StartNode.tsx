import { memo } from "react";
import { Handle, Position, NodeResizer } from "@xyflow/react";
import {
  Card,
  CardBody,
  CardHeader,
  Form,
  Input,
  Textarea,
  useDisclosure,
} from "@heroui/react";

import {
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  Icon,
  KeyInput,
  NodeProps,
  StateSchemaModal,
} from "@/components";

export type StartNodeData = BaseNodeData & {
  guiding_words?: string;
  state_schema?: string;
};

export type StartNodeProps = NodeProps<StartNodeData>;

function StartNode({ id, data, onDataChange }: StartNodeProps) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  return (
    <>
      <NodeResizer isVisible={false} />
      <Card className="m-1 bg-slate-50">
        <CardHeader className="bg-teal-200">
          <div className="font-black ml-2 w-full">开始</div>
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
            <Textarea
              disableAutosize
              className="nodrag"
              defaultValue={data.guiding_words}
              label="引导词"
              maxRows={3}
              name="guiding_words"
              placeholder="请输入引导词"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, guiding_words: e.target.value })
              }
            />
            <Textarea
              disableAutosize
              isReadOnly
              className="nodrag"
              endContent={
                <Icon color="white" size={18} type="edit" onClick={onOpen} />
              }
              label="状态变量"
              maxRows={1}
              name="state_schema"
              placeholder="请输入状态变量"
              radius="sm"
              size="sm"
              value={data.state_schema}
            />
          </Form>
        </CardBody>
      </Card>
      <Handle
        id="output"
        position={Position.Right}
        style={DEFAULT_HANDLE_STYLE}
        type="source"
      />
      <StateSchemaModal
        data={data}
        isOpen={isOpen}
        onDataChange={onDataChange}
        onOpenChange={onOpenChange}
      />
    </>
  );
}

export default memo(StartNode);
