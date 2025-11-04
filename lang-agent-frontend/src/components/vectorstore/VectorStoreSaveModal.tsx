import { memo, useCallback, useEffect, useState } from "react";
import {
  addToast,
  Button,
  Input,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  Select,
  SelectItem,
  SharedSelection,
  Switch,
} from "@heroui/react";

import { apiClient } from "@/util";
import { VectorStore } from "@/types";
import { useModelStore } from "@/store/model";

const types = [
  { id: "postgres", name: "postgres" },
  { id: "milvus", name: "milvus" },
];

type ModalProps = {
  id: string | undefined;
  isOpen: boolean;
  onOpenChange: () => void;
  onRefresh: () => void;
  setRunning: (running: boolean) => void;
};

const App: React.FC<ModalProps> = ({
  id,
  isOpen,
  onOpenChange,
  onRefresh,
  setRunning,
}) => {
  const { embeddings, fetchModels } = useModelStore();
  const init_vectorstore: VectorStore = {
    id: "",
    name: "",
    type: "postgres",
    uri: "127.0.0.1:5432",
    user: "",
    password: "",
    db_name: "postgres",
    collection_name: "documents",
    embedding_name: "",
    disabled: false,
  };
  const [vectorstore, setVectorStore] = useState<VectorStore>(init_vectorstore);

  useEffect(() => {
    if (id) {
      apiClient
        .get(`/v1/vectorstore/select?id=${id}`)
        .then((response) => {
          setVectorStore(response.data.data);
        })
        .catch((error) => {
          addToast({
            title: "获取向量库数据失败:" + error.response.data.error,
            timeout: 1000,
            shouldShowTimeoutProgress: true,
            color: "danger",
          });
        });
    } else {
      setVectorStore(init_vectorstore);
    }
  }, [id]);

  useEffect(() => {
    if (isOpen) {
      fetchModels();
    }
  }, [isOpen, fetchModels]);

  const onSave = useCallback(() => {
    setRunning(true);
    apiClient
      .post("/v1/vectorstore/save", vectorstore)
      .then(() => {
        setRunning(false);
        addToast({
          title: "保存成功",
          timeout: 1000,
          shouldShowTimeoutProgress: true,
        });
        onRefresh();
      })
      .catch((error) => {
        addToast({
          title: "保存失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      })
      .finally(() => {
        setRunning(false);
      });
  }, [vectorstore]);

  return (
    <>
      <Modal isOpen={isOpen} placement="top-center" onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">保存</ModalHeader>
              <ModalBody>
                <Input
                  isRequired
                  label="名称"
                  name="name"
                  placeholder="请输入向量名称"
                  radius="sm"
                  size="sm"
                  value={vectorstore.name}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setVectorStore({ ...vectorstore, name: value });
                  }}
                />
                <Select
                  isRequired
                  className="nodrag"
                  items={types}
                  label="类型"
                  placeholder="请选择向量库类型"
                  selectedKeys={new Set([vectorstore.type])}
                  selectionMode="single"
                  size="sm"
                  onSelectionChange={(keys: SharedSelection) => {
                    const value = Array.from(keys)[0] as string;

                    setVectorStore({ ...vectorstore, type: value });
                  }}
                >
                  {(type) => <SelectItem key={type.id}>{type.name}</SelectItem>}
                </Select>
                <Input
                  isRequired
                  label="URI"
                  name="uri"
                  placeholder="请输入URI"
                  radius="sm"
                  size="sm"
                  value={vectorstore.uri}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setVectorStore({ ...vectorstore, uri: value });
                  }}
                />
                <Input
                  label="用户名"
                  name="user"
                  placeholder="请输入用户名"
                  radius="sm"
                  size="sm"
                  value={vectorstore.user}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setVectorStore({ ...vectorstore, user: value });
                  }}
                />
                <Input
                  label="密码"
                  name="password"
                  placeholder="请输入密码"
                  radius="sm"
                  size="sm"
                  type="password"
                  value={vectorstore.password}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setVectorStore({ ...vectorstore, password: value });
                  }}
                />
                <Input
                  isRequired
                  label="数据库名"
                  name="db_name"
                  placeholder="请输入数据库名"
                  radius="sm"
                  size="sm"
                  value={vectorstore.db_name}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setVectorStore({ ...vectorstore, db_name: value });
                  }}
                />
                <Input
                  isRequired
                  label="集合名"
                  name="collection_name"
                  placeholder="请输入集合名"
                  radius="sm"
                  size="sm"
                  value={vectorstore.collection_name}
                  variant="bordered"
                  onValueChange={(value: string) => {
                    setVectorStore({ ...vectorstore, collection_name: value });
                  }}
                />
                <Select
                  isRequired
                  className="nodrag"
                  label="嵌入模型"
                  placeholder="请选择嵌入模型"
                  selectedKeys={new Set([vectorstore.embedding_name])}
                  selectionMode="single"
                  size="sm"
                  onSelectionChange={(keys) => {
                    const value = Array.from(keys)[0] as string;

                    setVectorStore({ ...vectorstore, embedding_name: value });
                  }}
                >
                  {embeddings.map((embedding) => (
                    <SelectItem key={embedding}>{embedding}</SelectItem>
                  ))}
                </Select>
                <Switch
                  className="mr-5"
                  isSelected={vectorstore.disabled}
                  size="md"
                  onValueChange={(value: boolean) => {
                    setVectorStore({ ...vectorstore, disabled: value });
                  }}
                >
                  是否禁用
                </Switch>
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
