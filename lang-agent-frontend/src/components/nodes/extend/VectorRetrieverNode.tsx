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

export type VectorRetrieverNodeData = BaseNodeData & {
  vs_name: string;
  keywords: string;
};
export type VectorRetrieverNodeProps = NodeProps<VectorRetrieverNodeData>;

const VectorRetrieverNode: React.FC<VectorRetrieverNodeProps> = ({
  id,
  data,
  onDataChange,
}) => {
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
          <div className="font-black ml-2 w-full">向量召回</div>
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
              defaultValue={data.keywords}
              label="召回关键字"
              name="keywords"
              placeholder="请输入召回关键字"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, keywords: e.target.value })
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

const VectorRetrieverNodeConfig: NodeConfig<VectorRetrieverNodeData> = {
  type: "vector_retriever",
  description: "向量召回",
  data: {
    id: "",
    name: "vector_retriever",
    type: "vector_retriever",
    vs_name: "",
    keywords: "",
  },
  component: VectorRetrieverNode,
};

export default VectorRetrieverNodeConfig;
