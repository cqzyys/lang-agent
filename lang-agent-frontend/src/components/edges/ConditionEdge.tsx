import type { ConditionEdgeProps } from "@/types";

import { memo } from "react";
import {
  Position,
  BaseEdge,
  EdgeLabelRenderer,
  getSimpleBezierPath,
} from "@xyflow/react";
import { Input } from "@heroui/react";

const App: React.FC<ConditionEdgeProps> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  markerEnd,
  data,
  onDataChange,
}) => {
  let edgePath = "";
  let labelX = 0;
  let labelY = 0;

  if (sourceX < targetX) {
    [edgePath, labelX, labelY] = getSimpleBezierPath({
      sourceX: sourceX,
      sourceY: sourceY,
      sourcePosition: Position.Right,
      targetX: targetX,
      targetY: targetY,
      targetPosition: Position.Left,
    });
  } else {
    const radiusX = (sourceX - targetX) * 0.6;
    const radiusY = (sourceX - targetX) * 0.3;

    edgePath = `M ${sourceX} ${sourceY} A ${radiusX} ${radiusY} 0 1 0 ${
      targetX + 2
    } ${targetY - 5}`;
    const centerX = (sourceX + targetX) / 2;
    const centerY = (sourceY + targetY) / 2;

    labelX = centerX;
    labelY = centerY - 1.55 * radiusY;
  }

  return (
    <>
      <BaseEdge id={id} markerEnd={markerEnd} path={edgePath} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: "all",
          }}
        >
          <Input
            isRequired
            className="nodrag nopan"
            errorMessage="请输入限定条件"
            name="expr"
            placeholder="限定条件"
            radius="sm"
            size="sm"
            value={data.expr}
            onChange={(e) => onDataChange({ ...data, expr: e.target.value })}
          />
        </div>
      </EdgeLabelRenderer>
    </>
  );
};

export default memo(App);
