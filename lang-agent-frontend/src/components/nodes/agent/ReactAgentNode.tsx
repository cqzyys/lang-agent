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
  SelectSection,
} from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
} from "@/components";
import { useModelStore, useMcpStore } from "@/store";

export type ReactAgentNodeData = BaseNodeData & {
  model: string;
  tools?: string;
};

export type ReactAgentNodeProps = NodeProps<ReactAgentNodeData>;

const ReactAgentNode: React.FC<ReactAgentNodeProps> = ({
  id,
  data,
  onDataChange,
}) => {
  const { llms } = useModelStore();
  const { mcp_map } = useMcpStore();

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
          <div className="font-black ml-2 w-full">ReactAgent</div>
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
              label="工具"
              placeholder="请选择工具"
              selectedKeys={new Set(data.tools && data.tools.split(","))}
              selectionMode="multiple"
              size="sm"
              onSelectionChange={(keys) =>
                onDataChange({ ...data, tools: Array.from(keys).join(",") })
              }
            >
              {Object.entries(mcp_map).map((key) => (
                <SelectSection key={key[0]} showDivider title={key[0]}>
                  {key[1].map((tool) => (
                    <SelectItem key={`${key[0]}.${tool}`}>{tool}</SelectItem>
                  ))}
                </SelectSection>
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

export default memo(ReactAgentNode);
