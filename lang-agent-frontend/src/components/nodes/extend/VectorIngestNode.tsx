import {
  Card,
  CardBody,
  CardHeader,
  Form,
  Input,
  Select,
  SelectItem,
} from "@heroui/react";
import { Handle, NodeResizer, Position } from "@xyflow/react";

import {
  DEFAULT_HANDLE_STYLE,
  KeyInput,
  BaseNodeData,
  NodeConfig,
  NodeProps,
} from "@/components";
import { useVsStore } from "@/store";

const VectorIngestNodeConfig: NodeConfig<VectorIngestNodeData> = {
  type: "vector_ingest",
  description: "向量存储",
  data: {
    id: "",
    name: "vector_ingest",
    type: "vector_ingest",
    vs_name: "",
    content: "",
    description: "",
  },
  component: VectorIngestNode,
};

export type VectorIngestNodeData = BaseNodeData & {
  vs_name: string;
  content: string;
  description: string;
};
export type VectorIngestNodeProps = NodeProps<VectorIngestNodeData>;

export function VectorIngestNode({
  id,
  data,
  onDataChange,
}: VectorIngestNodeProps) {
  const { vectorstores } = useVsStore();

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
          <div className="font-black ml-2 w-full">向量存储</div>
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
              isRequired
              className="nodrag"
              label="向量库"
              placeholder="请选择向量库"
              selectedKeys={new Set([data.vs_name])}
              selectionMode="single"
              size="sm"
              onSelectionChange={(keys) => {
                const value = Array.from(keys)[0] as string;

                onDataChange({ ...data, vs_name: value });
              }}
            >
              {vectorstores.map((vectorstore) => (
                <SelectItem key={vectorstore}>{vectorstore}</SelectItem>
              ))}
            </Select>
            <Input
              isRequired
              className="nodrag"
              defaultValue={data.content}
              label="文档内容"
              name="content"
              placeholder="请输入文档内容"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, content: e.target.value })
              }
            />
            <Input
              isRequired
              className="nodrag"
              defaultValue={data.description}
              label="文档描述"
              name="description"
              placeholder="请输入文档描述"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, description: e.target.value })
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
}

export default VectorIngestNodeConfig;
