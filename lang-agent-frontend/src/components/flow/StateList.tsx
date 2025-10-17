import {
  memo,
  useEffect,
  useState,
  ReactNode,
  RefObject,
  useMemo,
} from "react";
import { Listbox, ListboxItem } from "@heroui/react";
import { createPortal } from "react-dom";
import { Node } from "@xyflow/react";

import { genStateList } from "@/util";
import { BaseNodeData } from "@/types";

export type StateListProps = {
  value: string | undefined;
  triggerRef: RefObject<HTMLInputElement> | undefined;
  nodes: Node[];
  data: BaseNodeData;
  onDataChange: (data: any) => void;
};

type ListboxWrapperProps = {
  children: ReactNode;
  isShown: boolean;
  position: { x: number; y: number };
};

const ListboxWrapper: React.FC<ListboxWrapperProps> = ({
  children,
  isShown,
  position,
}) => {
  const [portalElement, setPortalElement] = useState<HTMLElement | null>(null);

  useEffect(() => {
    setPortalElement(document.body);
  }, []);
  const element = (
    <div
      className={`w-full max-w-[260px] border-small px-1 py-2 rounded-small ${isShown ? "block" : "hidden"}`}
      style={{
        position: "absolute",
        left: `${position.x}px`,
        top: `${position.y}px`,
        zIndex: 1000,
        backgroundColor: "white", // 设置白色背景
        border: "1px solid #e5e7eb", // 添加边框
        boxShadow:
          "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)", //添加阴影
      }}
    >
      {children}
    </div>
  );

  if (!isShown || !portalElement) {
    return null;
  }

  return createPortal(element, portalElement);
};

const App: React.FC<StateListProps> = ({
  value,
  triggerRef,
  nodes,
  data,
  onDataChange,
}) => {
  const [isShown, setIsShown] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const states = genStateList(nodes);
  const stateItems = useMemo(
    () =>
      states.map((state) => ({
        key: state,
        label: state,
      })),
    [states],
  );

  // 监听value变化，检查最后两个字符是否为{{
  useEffect(() => {
    if (value && value.length >= 2) {
      const lastTwoChars = value.substring(value.length - 2);

      if (lastTwoChars === "{{") {
        setIsShown(true);
        if (triggerRef?.current) {
          const inputRect = triggerRef.current.getBoundingClientRect();

          setPosition({
            x: inputRect.left + inputRect.width,
            y: inputRect.top,
          });
        }
      } else {
        setIsShown(false);
      }
    }
  }, [value]);

  // 监听键盘事件，按下ESC键时设置isShown为false
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsShown(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    // 清理事件监听器
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <ListboxWrapper isShown={isShown} position={position}>
      <Listbox
        items={stateItems}
        onAction={(key) => {
          if (triggerRef?.current) {
            const inputElement = triggerRef.current as HTMLInputElement;
            const inputName = inputElement.name;
            const inputValue = inputElement.value;
            const value = key as string;

            if (inputName) {
              onDataChange({
                ...data,
                [inputName]: inputValue + value + "}}",
              });
              setIsShown(false);
            }
          }
        }}
      >
        {(item) => {
          return <ListboxItem key={item.key}>{item.label}</ListboxItem>;
        }}
      </Listbox>
    </ListboxWrapper>
  );
};

export default memo(App);
