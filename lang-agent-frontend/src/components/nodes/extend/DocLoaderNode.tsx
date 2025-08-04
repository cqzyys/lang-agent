import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

const DocLoaderNodeConfig: NodeConfig<DocLoaderNodeData> = {
  type: "doc_loader",
  description: "文档加载",
  data: {
    id: "",
    type: "doc_loader",
    name: "doc_loader",
    file_name: "",
    file_content: "",
  },
  component: DocLoaderNode,
};

export type DocLoaderNodeData = BaseNodeData & {
  file_name: string;
  file_content: string;
};

export type DocLoaderNodeProps = NodeProps<DocLoaderNodeData>;

function DocLoaderNode({ id, data, onDataChange }: DocLoaderNodeProps) {
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
          <div className="font-black ml-2 w-full">文档加载</div>
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
              label="上传文档"
              name="files"
              radius="sm"
              size="sm"
              type="file"
              onChange={(e) => {
                const files = e.target.files;

                if (files && files.length > 0) {
                  const file = files[0];
                  const reader = new FileReader();

                  reader.onload = () => {
                    onDataChange({
                      ...data,
                      file_name: file.name,
                      file_content: reader.result as string,
                    });
                  };
                  reader.readAsDataURL(file);
                }
              }}
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

export default DocLoaderNodeConfig;
