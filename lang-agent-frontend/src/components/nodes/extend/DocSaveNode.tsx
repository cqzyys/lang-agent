import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

const DocSaveNodeConfig: NodeConfig<DocSaveNodeData> = {
  type: "doc_save",
  description: "文档保存",
  data: {
    id: "",
    type: "doc_save",
    name: "doc_save",
    save_path: "",
  },
  component: DocSaveNode,
};

export type DocSaveNodeData = BaseNodeData & {
  save_path: string;
};

export type DocSaveNodeProps = NodeProps<DocSaveNodeData>;

function DocSaveNode({ id, data, onDataChange }: DocSaveNodeProps) {
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
          <div className="font-black ml-2 w-full">DocSave</div>
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
              errorMessage="请输入保存路径"
              label="保存路径"
              name="save_path"
              placeholder="请输入保存路径"
              radius="sm"
              size="sm"
              value={data.save_path}
              onChange={(e) =>
                onDataChange({ ...data, save_path: e.target.value })
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

export default DocSaveNodeConfig;
