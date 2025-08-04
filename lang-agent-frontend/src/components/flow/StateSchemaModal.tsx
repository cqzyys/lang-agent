import { useCallback, memo, useState, useRef } from "react";
import {
  Form,
  Input,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  Select,
  SelectItem,
} from "@heroui/react";
import { nanoid } from "nanoid";

import { Icon } from "@/components";

const types = [
  { id: "str", name: "str" },
  { id: "int", name: "int" },
  { id: "float", name: "float" },
  { id: "bool", name: "bool" },
  { id: "list", name: "list" },
];

function StateSchemaModal({ isOpen, onOpenChange, data, onDataChange }: any) {
  const state_schema: Record<string, string> = JSON.parse(data.state_schema);
  const [schemaList, setSchemaList] = useState(Object.entries(state_schema));
  const currentIndex = useRef(0);
  const onAdd = useCallback(() => {
    setSchemaList((prev) => [...prev, ["", "str"]]);
  }, [schemaList, setSchemaList]);

  const onDelete = useCallback(
    (index: number) => {
      setSchemaList((prev) => {
        const newList = [...prev];

        newList.splice(index, 1);

        return newList;
      });
    },
    [schemaList, setSchemaList],
  );

  const onFieldBlur = useCallback(
    (field: string) => {
      schemaList[currentIndex.current][0] = field;
    },
    [schemaList, setSchemaList],
  );

  const onTypeBlur = useCallback(
    (type: string) => {
      schemaList[currentIndex.current][1] = type;
    },
    [schemaList, setSchemaList],
  );

  const onSave = useCallback(() => {
    const stateSchema: Record<string, string> = Object.fromEntries(schemaList);

    onDataChange({
      ...data,
      state_schema: JSON.stringify(stateSchema),
    });
  }, [data, schemaList, onDataChange]);

  return (
    <>
      <Modal
        hideCloseButton={true}
        isOpen={isOpen}
        placement="top-center"
        onOpenChange={onOpenChange}
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalBody>
                <Form>
                  {schemaList.map(([key, value], index) => {
                    let isShow = index === schemaList.length - 1;
                    let isReadOnly = key === "messages" ? true : false;

                    return (
                      <div
                        key={nanoid(4)}
                        className="flex w-full items-center gap-2"
                        onFocus={(_e) => {
                          currentIndex.current = index;
                        }}
                      >
                        <Input
                          key={nanoid(4)}
                          defaultValue={key}
                          isReadOnly={isReadOnly}
                          name="field"
                          size="sm"
                          onBlur={(e) => {
                            onFieldBlur(e.target.value);
                          }}
                        />
                        <Select
                          aria-label="选择字段类型"
                          className="nodrag"
                          isDisabled={isReadOnly}
                          items={types}
                          selectedKeys={new Set([value])}
                          selectionMode="single"
                          size="sm"
                          onSelectionChange={(keys) => {
                            const value = Array.from(keys)[0] as string;

                            onTypeBlur(value);
                          }}
                        >
                          {(type) => (
                            <SelectItem key={type.id}>{type.name}</SelectItem>
                          )}
                        </Select>
                        <div className="flex w-24" id="actions">
                          {!isReadOnly && (
                            <Icon
                              color="white"
                              size={18}
                              type="delete"
                              onClick={() => {
                                onDelete(index);
                              }}
                            />
                          )}
                          {isShow && (
                            <Icon
                              color="white"
                              size={18}
                              type="add"
                              onClick={onAdd}
                            />
                          )}
                        </div>
                      </div>
                    );
                  })}
                </Form>
              </ModalBody>
              <ModalFooter>
                <Icon
                  color="white"
                  size={18}
                  type="save"
                  onClick={() => {
                    onSave();
                    onClose();
                  }}
                />
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}

export default memo(StateSchemaModal);
