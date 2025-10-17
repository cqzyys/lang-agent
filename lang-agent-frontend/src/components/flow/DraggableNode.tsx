import { memo } from "react";

import { Icon } from "@/components";

interface DraggableNodeProps {
  node: {
    type: string;
    description: string | undefined;
  };
  onDragStart?: (e: React.DragEvent<HTMLDivElement>, node: any) => void;
  onDoubleClick?: (e: React.MouseEvent<HTMLDivElement>, node: any) => void;
}

const App: React.FC<DraggableNodeProps> = ({
  node,
  onDragStart,
  onDoubleClick,
}) => {
  return (
    <div
      draggable
      className="flex"
      onDoubleClick={(e) => onDoubleClick?.(e, node)}
      onDragStart={(e) => onDragStart?.(e, node)}
    >
      <Icon className="mr-2" type={node.type} />
      <span>{node.description}</span>
    </div>
  );
};

export default memo(App);
