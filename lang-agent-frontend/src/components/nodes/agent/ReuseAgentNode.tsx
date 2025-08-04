import { memo } from "react";
import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  DEFAULT_HANDLE_STYLE,
  KeyInput,
  BaseNodeData,
  NodeProps,
} from "@/components";

export type ReUseAgentNodeData = BaseNodeData & {
  data?: string;
};

export type ReUseAgentNodeProps = NodeProps<ReUseAgentNodeData>;

function ReuseAgentNode({ id, data, onDataChange }: ReUseAgentNodeProps) {
  return (
    <>
      <NodeResizer isVisible={false} />
      <Handle
        id="input"
        position={Position.Left}
        style={DEFAULT_HANDLE_STYLE}
        type="target"
      />
      <Card className="m-1 bg-slate-50">
        <CardHeader className="bg-orange-200">
          <div className="font-black ml-2 w-full">Agent</div>
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
          </Form>
        </CardBody>
      </Card>
      <Handle
        id="output"
        position={Position.Right}
        style={DEFAULT_HANDLE_STYLE}
        type="source"
      />
    </>
  );
}

export default memo(ReuseAgentNode);
