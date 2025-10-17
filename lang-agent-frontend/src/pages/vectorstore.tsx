import { useEffect, useState } from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  getKeyValue,
  addToast,
  useDisclosure,
  Spinner,
} from "@heroui/react";
import React from "react";
import { Key } from "@react-types/shared";

import { apiClient } from "@/util";
import { VectorStore } from "@/types";
import { Icon, VectorStoreSaveModal } from "@/components";

const columns = [
  {
    key: "name",
    label: "向量库名称",
    width: 200,
  },
  {
    key: "type",
    label: "类型",
    width: 200,
  },
  {
    key: "disabled",
    label: "是否禁用",
    width: 200,
  },
  {
    key: "actions",
    label: "操作",
    width: 200,
  },
];

const VectorStorePage: React.FC = () => {
  const [vectorstores, setVectorStores] = useState<VectorStore[]>([]);
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [running, setRunning] = useState<boolean>(false);
  const [id, setId] = useState<string>();
  const fetchData = async () => {
    apiClient
      .get("/v1/vectorstore/list")
      .then((response) => {
        setVectorStores(response.data.data);
      })
      .catch((error) => {
        addToast({
          title: "获取向量库数据失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const renderCell = React.useCallback((data: VectorStore, columnKey: Key) => {
    function onDelete() {
      apiClient
        .post(`/v1/vectorstore/delete?id=${data.id}`)
        .then(() => {
          fetchData();
          addToast({
            title: "删除成功",
            timeout: 1000,
            shouldShowTimeoutProgress: true,
          });
        })
        .catch((error) => {
          addToast({
            title: "删除失败:" + error.response.data.error,
            timeout: 1000,
            shouldShowTimeoutProgress: true,
            color: "danger",
          });
        });
    }

    switch (columnKey) {
      case "actions":
        return (
          <div className="relative flex items-center gap-2">
            <Icon
              size={18}
              type="edit"
              onClick={() => {
                setId(data.id);
                onOpen();
              }}
            />
            <Icon size={18} type="trash" onClick={onDelete} />
          </div>
        );
      case "disabled":
        return data.disabled ? "是" : "否";
      default:
        return getKeyValue(data, columnKey);
    }
  }, []);

  const topContent = React.useMemo(() => {
    return (
      <div className="flex items-center w-full">
        <Icon
          className="ml-auto"
          size={18}
          type="add"
          onClick={() => {
            setId(undefined);
            onOpen();
          }}
        />
      </div>
    );
  }, []);

  return (
    <>
      <Table
        isStriped
        aria-label="向量库列表"
        color="warning"
        selectionMode="single"
        topContent={topContent}
      >
        <TableHeader columns={columns}>
          {(column) => (
            <TableColumn
              key={column.key}
              align={column.key === "actions" ? "start" : "center"}
              width={column.width}
            >
              {column.label}
            </TableColumn>
          )}
        </TableHeader>
        <TableBody emptyContent={"没有数据可显示"} items={vectorstores}>
          {(item) => (
            <TableRow key={item.id}>
              {(columnKey) => {
                return <TableCell>{renderCell(item, columnKey)}</TableCell>;
              }}
            </TableRow>
          )}
        </TableBody>
      </Table>
      {running && (
        <Spinner className="absolute top-1/4 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50" />
      )}
      <VectorStoreSaveModal
        id={id}
        isOpen={isOpen}
        setRunning={setRunning}
        onOpenChange={onOpenChange}
        onRefresh={fetchData}
      />
    </>
  );
};

export default VectorStorePage;
