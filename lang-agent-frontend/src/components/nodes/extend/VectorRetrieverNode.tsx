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

import { VectorStoreConfig } from "./VectorStoreConfig";

import {
  DEFAULT_HANDLE_STYLE,
  KeyInput,
  BaseNodeData,
  NodeConfig,
  NodeProps,
} from "@/components";
import { useModelStore } from "@/store/model";

const vs_types = ["postgress", "milvus"];

const VectorRetrieverNodeConfig: NodeConfig<VectorRetrieverNodeData> = {
  type: "vector_retriever",
  description: "向量召回",
  data: {
    id: "",
    name: "vector_retriever",
    type: "vector_retriever",
    vs_type: "postgress",
    uri: "127.0.0.1:5432",
    user: "",
    password: "",
    db_name: "postgres",
    collection_name: "documents",
    embedding_name: "",
    keywords: "",
  },
  component: VectorRetrieverNode,
};

export type VectorRetrieverNodeData = BaseNodeData &
  VectorStoreConfig & {
    keywords: string;
  };
export type VectorRetrieverNodeProps = NodeProps<VectorRetrieverNodeData>;

export function VectorRetrieverNode({
  id,
  data,
  onDataChange,
}: VectorRetrieverNodeProps) {
  const { embeddings } = useModelStore();

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
              className="max-w-xs nodrag"
              label="类型"
              placeholder="请选择向量数据库类型"
              selectedKeys={new Set([data.vs_type])}
              selectionMode="single"
              size="sm"
              onSelectionChange={(keys) => {
                const value = Array.from(keys)[0] as string;

                onDataChange({ ...data, vs_type: value });
              }}
            >
              {vs_types.map((vs_type) => (
                <SelectItem key={vs_type}>{vs_type}</SelectItem>
              ))}
            </Select>
            <Input
              isRequired
              className="nodrag"
              defaultValue={data.uri}
              label="URI"
              name="uri"
              placeholder="请输入URI"
              radius="sm"
              size="sm"
              onChange={(e) => onDataChange({ ...data, uri: e.target.value })}
            />
            <Input
              className="nodrag"
              defaultValue={data.user}
              label="用户名"
              name="user"
              placeholder="请输入用户名"
              radius="sm"
              size="sm"
              onChange={(e) => onDataChange({ ...data, user: e.target.value })}
            />
            <Input
              className="nodrag"
              defaultValue={data.password}
              label="密码"
              name="password"
              placeholder="请输入密码"
              radius="sm"
              size="sm"
              type="password"
              onChange={(e) =>
                onDataChange({ ...data, password: e.target.value })
              }
            />
            <Input
              isRequired
              className="nodrag"
              defaultValue={data.db_name}
              label="数据库名"
              name="db_name"
              placeholder="请输入数据库名"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, db_name: e.target.value })
              }
            />
            <Input
              isRequired
              className="nodrag"
              defaultValue={data.collection_name}
              label="集合名"
              name="collection_name"
              placeholder="请输入集合名"
              radius="sm"
              size="sm"
              onChange={(e) =>
                onDataChange({ ...data, collection_name: e.target.value })
              }
            />
            <Select
              isRequired
              className="nodrag"
              label="嵌入模型"
              placeholder="请选择嵌入模型"
              selectedKeys={new Set([data.embedding_name])}
              selectionMode="single"
              size="sm"
              onSelectionChange={(keys) => {
                const value = Array.from(keys)[0] as string;

                onDataChange({ ...data, embedding_name: value });
              }}
            >
              {embeddings.map((embedding) => (
                <SelectItem key={embedding}>{embedding}</SelectItem>
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
}

export default VectorRetrieverNodeConfig;
