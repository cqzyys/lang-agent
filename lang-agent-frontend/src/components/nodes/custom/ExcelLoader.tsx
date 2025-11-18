import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader, Form, Input } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

export type ExcelLoaderNodeData = BaseNodeData & {
  guiding_words: string;
};

export type ExcelLoaderNodeProps = NodeProps<ExcelLoaderNodeData>;

const ExcelLoaderNode: React.FC<ExcelLoaderNodeProps> = ({
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
          <div className="font-black ml-2 w-full">Excel加载</div>
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

const ExcelLoaderNodeConfig: NodeConfig<ExcelLoaderNodeData> = {
  type: "excel_loader",
  description: "Excel加载",
  data: {
    id: "",
    type: "excel_loader",
    name: "excel_loader",
    guiding_words: "请上传excel文件",
  },
  component: ExcelLoaderNode,
};

export default ExcelLoaderNodeConfig;
