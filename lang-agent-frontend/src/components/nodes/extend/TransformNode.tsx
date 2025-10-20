import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

export type TransformNodeData = BaseNodeData & {
  origin_state_field?: string;
  target_state_field?: string;
};

export type TransformNodeProps = NodeProps<TransformNodeData>;

const TransformNode: React.FC<TransformNodeProps> = ({
  id,
  data,
  onDataChange,
}) => {
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
        <CardHeader className="bg-slate-200">
          <div className="font-black ml-2 w-full">转换</div>
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
            <Input
              className="nodrag"
              defaultValue={data.origin_state_field}
              label="来源状态变量"
              name="origin_state_field"
              placeholder="请输入来源状态变量"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, origin_state_field: e.target.value })
              }
            />
            <Input
              className="nodrag"
              defaultValue={data.target_state_field}
              label="目标状态变量"
              name="target_state_field"
              placeholder="请输入目标状态变量"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, target_state_field: e.target.value })
              }
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
};

const TransformNodeConfig: NodeConfig<TransformNodeData> = {
  type: "transform",
  description: "转换器",
  data: {
    id: "",
    type: "transform",
    name: "transform",
    origin_state_field: "",
    target_state_field: "",
  },
  component: TransformNode,
};

export default TransformNodeConfig;
