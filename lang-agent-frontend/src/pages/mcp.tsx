import { useEffect, useRef, useState } from "react";
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
import log from "loglevel";
import { Key } from "@react-types/shared";

import apiClient from "@/hooks";
import { Mcp } from "@/types";
import { Icon, McpSaveModal } from "@/components";

log.setLevel("debug");

const columns = [
  {
    key: "name",
    label: "名称",
    width: 200,
  },
  {
    key: "description",
    label: "说明",
    width: 300,
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

export default function McpPage() {
  const [mcps, setMcps] = useState<Mcp[]>([]);
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [running, setRunning] = useState<boolean>(false);
  const id = useRef<string>();
  const fetchData = async () => {
    apiClient
      .get("/v1/mcp/list")
      .then((response) => {
        setMcps(response.data.data);
      })
      .catch((error) => {
        addToast({
          title: "获取MCP数据失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const renderCell = React.useCallback((data: Mcp, columnKey: Key) => {
    function onDelete() {
      apiClient
        .post(`/v1/mcp/delete?id=${data.id}`)
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
                id.current = data.id;
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
            id.current = "";
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
        aria-label="MCP列表"
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
        <TableBody emptyContent={"没有数据可显示"} items={mcps}>
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
      <McpSaveModal
        id={id.current}
        isOpen={isOpen}
        setRunning={setRunning}
        onOpenChange={onOpenChange}
        onRefresh={fetchData}
      />
    </>
  );
}
