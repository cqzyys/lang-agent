import { Dispatch, memo, SetStateAction } from "react";
import {
  Button,
  Input,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  Textarea,
} from "@heroui/react";

import { Agent } from "@/types";

interface AgentSaveModalProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  agent: Agent;
  setAgent: Dispatch<SetStateAction<Agent>>;
  onSave: () => void;
}

const App: React.FC<AgentSaveModalProps> = ({
  isOpen,
  onOpenChange,
  agent,
  setAgent,
  onSave,
}) => {
  return (
    <>
      <Modal isOpen={isOpen} placement="top-center" onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">保存</ModalHeader>
              <ModalBody>
                <Input
                  label="名称"
                  name="name"
                  placeholder="请输入Agent名称"
                  radius="sm"
                  size="sm"
                  value={agent?.name}
                  variant="bordered"
                  onChange={(e) => {
                    setAgent({ ...agent, name: e.target.value });
                  }}
                />
                <Textarea
                  label="描述"
                  name="name"
                  placeholder="请输入Agent描述"
                  radius="sm"
                  size="sm"
                  value={agent?.description}
                  variant="bordered"
                  onChange={(e) => {
                    setAgent({ ...agent, description: e.target.value });
                  }}
                />
              </ModalBody>
              <ModalFooter>
                <Button
                  color="primary"
                  onPress={() => {
                    onSave();
                    onClose();
                  }}
                >
                  确定
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
};

export default memo(App);
