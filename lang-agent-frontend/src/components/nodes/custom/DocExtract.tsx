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
  NodeConfig,
} from "@/components";
import { useModelStore } from "@/store/model";

const DocExtractNodeConfig: NodeConfig<DocExtractNodeData> = {
  type: "doc_extract",
  description: "文献萃取",
  data: {
    id: "",
    type: "doc_extract",
    name: "doc_extract",
    guiding_words: "",
    model: "qwen2.5-instruct",
  },
  component: DocExtractNode,
};

export type DocExtractNodeData = BaseNodeData & {
  guiding_words: string;
  model: string;
};

export type DocExtractNodeProps = NodeProps<DocExtractNodeData>;

function DocExtractNode({ id, data, onDataChange }: DocExtractNodeProps) {
  const { llms } = useModelStore();

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
          <div className="font-black ml-2 w-full">文献萃取</div>
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
              errorMessage="请输入引导词"
              label="引导词"
              name="guiding_words"
              placeholder="请输入引导词"
              radius="sm"
              size="sm"
              value={data.guiding_words}
              onChange={(e) =>
                onDataChange({ ...data, guiding_words: e.target.value })
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
              {llms.map((llm) => (
                <SelectItem key={llm}>{llm}</SelectItem>
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
}

export default DocExtractNodeConfig;
