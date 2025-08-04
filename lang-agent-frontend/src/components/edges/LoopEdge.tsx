import type { LoopEdgeProps } from "@/types";

import { memo } from "react";
import { BaseEdge, EdgeLabelRenderer } from "@xyflow/react";
import { InputOtp } from "@heroui/react";

function LoopEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  markerEnd,
  data,
  onDataChange,
}: LoopEdgeProps) {
  const radiusX = (sourceX - targetX) * 0.6;
  const radiusY = (sourceX - targetX) * 0.3;
  const edgePath = `M ${sourceX} ${sourceY} A ${radiusX} ${radiusY} 0 1 0 ${
    targetX + 2
  } ${targetY - 5}`;
  const centerX = (sourceX + targetX) / 2;
  const centerY = (sourceY + targetY) / 2;
  const labelX = centerX;
  const labelY = centerY - 1.55 * radiusY;

  return (
    <>
      <BaseEdge
        id={id}
        markerEnd={markerEnd}
        path={edgePath}
        style={{ stroke: "green" }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: "all",
          }}
        >
          <InputOtp
            isRequired
            allowedKeys="^[0-9]*$"
            color="success"
            length={1}
            radius="lg"
            value={data.count}
            onValueChange={(value: string) =>
              onDataChange({ ...data, count: value })
            }
          />
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export default memo(LoopEdge);
