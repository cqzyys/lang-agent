import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

export type CommandNodeData = BaseNodeData & {
  command: string;
  cwd: string;
};

export type CommandNodeProps = NodeProps<CommandNodeData>;

const CommandNode: React.FC<CommandNodeProps> = ({
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
          <div className="font-black ml-2 w-full">命令执行节点</div>
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
              isRequired
              className="nodrag"
              defaultValue={data.command}
              label="执行命令"
              name="command"
              placeholder="请输入执行命令"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, command: e.target.value })
              }
            />
            <Input
              className="nodrag"
              defaultValue={data.cwd}
              label="命令执行目录"
              name="cwd"
              placeholder="请输入命令执行目录"
              radius="sm"
              size="sm"
              onChange={(e) => onDataChange({ ...data, cwd: e.target.value })}
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

const CommandNodeConfig: NodeConfig<CommandNodeData> = {
  type: "command",
  description: "命令执行",
  data: {
    id: "",
    type: "command",
    name: "command",
    command: "",
    cwd: "",
  },
  component: CommandNode,
};

export default CommandNodeConfig;
