import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

export type CounterNodeData = BaseNodeData & {
  state_field: string;
};

export type CounterNodeProps = NodeProps<CounterNodeData>;

const CounterNode: React.FC<CounterNodeProps> = ({
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
          <div className="font-black ml-2 w-full">计数器</div>
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
              defaultValue={data.state_field}
              label="目标状态变量"
              name="state_field"
              placeholder="请输入目标状态变量"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, state_field: e.target.value })
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

const CounterNodeConfig: NodeConfig<CounterNodeData> = {
  type: "counter",
  description: "计数器",
  data: {
    id: "",
    type: "counter",
    name: "counter",
    state_field: "",
  },
  component: CounterNode,
};

export default CounterNodeConfig;
