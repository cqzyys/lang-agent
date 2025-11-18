import { memo } from "react";
import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardHeader } from "@heroui/react";

import {
  DEFAULT_HANDLE_STYLE,
  NodeConfigData,
  BaseNodeData,
} from "@/components";

export type EndNodeData = BaseNodeData;

export const endNodeInitData: NodeConfigData<EndNodeData> = {
  description: "结束",
  type: "end",
  data: {
    name: "end",
  },
};

export type EndNodeProps = {
  onDrawerOpen: () => void;
};

const EndNode: React.FC<EndNodeProps> = ({ onDrawerOpen }) => {
  return (
    <>
      <NodeResizer isVisible={false} />
      <Handle
        id="input"
        position={Position.Left}
        style={DEFAULT_HANDLE_STYLE}
        type="target"
      />
      <Card className="m-1 bg-red-200">
        <CardHeader
          onDoubleClick={() => {
            onDrawerOpen();
          }}
        >
          <div className="font-black text-center w-full m-1">结束</div>
        </CardHeader>
      </Card>
    </>
  );
};

export default memo(EndNode);
