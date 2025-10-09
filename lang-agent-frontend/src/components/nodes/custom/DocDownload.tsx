import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

const DocDowloadNodeConfig: NodeConfig<DocDowloadNodeData> = {
  type: "doc_dowload",
  description: "文档下载",
  data: {
    id: "",
    type: "doc_dowload",
    name: "doc_dowload",
    content: "",
  },
  component: DocDowloadNode,
};

export type DocDowloadNodeData = BaseNodeData & {
  content: string;
};

export type DocDowloadNodeProps = NodeProps<DocDowloadNodeData>;

function DocDowloadNode({ id, data, onDataChange }: DocDowloadNodeProps) {
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
          <div className="font-black ml-2 w-full">文档下载</div>
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
              errorMessage="请输入文档内容"
              label="文档内容"
              name="content"
              placeholder="请输入文档内容"
              radius="sm"
              size="sm"
              value={data.content}
              onChange={(e) =>
                onDataChange({ ...data, content: e.target.value })
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

export default DocDowloadNodeConfig;
