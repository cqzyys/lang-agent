import { Handle, Position, NodeResizer } from "@xyflow/react";
import {
  Card,
  CardBody,
  CardHeader,
  Form,
  Input,
  Textarea,
} from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

const ExecutorNodeConfig: NodeConfig<ExecutorNodeData> = {
  type: "executor",
  description: "代码执行器",
  data: {
    id: "",
    type: "executor",
    name: "executor",
    code: "",
  },
  component: ExecutorNode,
};

export type ExecutorNodeData = BaseNodeData & {
  code: string;
};

export type ExecutorNodeProps = NodeProps<ExecutorNodeData>;

function ExecutorNode({ id, data, onDataChange }: ExecutorNodeProps) {
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
          <div className="font-black ml-2 w-full">代码执行器</div>
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
              defaultValue={data.code}
              label="Python代码"
              maxRows={3}
              name="code"
              placeholder="请输入Python代码"
              radius="sm"
              size="sm"
              onChange={(e) => onDataChange({ ...data, code: e.target.value })}
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

export default ExecutorNodeConfig;
