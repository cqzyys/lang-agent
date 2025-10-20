import { memo } from "react";
import { Handle, Position, NodeResizer } from "@xyflow/react";
import {
  Card,
  CardBody,
  CardHeader,
  Form,
  Input,
  Select,
  SelectItem,
} from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
} from "@/components";
import { useModelStore, useAgentStore } from "@/store";

export type SupervisorAgentNodeData = BaseNodeData & {
  model: string;
  agents?: string;
};

export type SupervisorAgentNodeProps = NodeProps<SupervisorAgentNodeData>;

const SupervisorAgentNode: React.FC<SupervisorAgentNodeProps> = ({
  id,
  data,
  onDataChange,
}) => {
  const { llms } = useModelStore();
  const { reuse_agents } = useAgentStore();

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
        <CardHeader className="bg-cyan-200">
          <div className="font-black ml-2 w-full">SupervisorAgent</div>
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
              placeholder="请选择模型"
              selectedKeys={new Set([data.model])}
              selectionMode="single"
              size="sm"
              onSelectionChange={(keys) => {
                const value = Array.from(keys)[0] as string;

                onDataChange({ ...data, model: value });
              }}
            >
              {llms.map((llm) => (
                <SelectItem key={llm}>{llm}</SelectItem>
              ))}
            </Select>
            <Select
              className="max-w-xs nodrag"
              label="Agent"
              placeholder="请选择Agent"
              selectedKeys={new Set(data.agents && data.agents.split(","))}
              selectionMode="multiple"
              onSelectionChange={(keys) =>
                onDataChange({ ...data, agents: Array.from(keys).join(",") })
              }
            >
              {reuse_agents.map((agent) => (
                <SelectItem key={agent}>{agent}</SelectItem>
              ))}
            </Select>
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

export default memo(SupervisorAgentNode);
