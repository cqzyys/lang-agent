import log from "loglevel";
import { useState, useEffect, useMemo } from "react";
import {
  addToast,
  getKeyValue,
  Spinner,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableColumn,
  TableHeader,
  TableRow,
} from "@heroui/react";
import { useLocation, useNavigate } from "react-router-dom";
import { Key } from "@react-types/shared";
import { ColumnSize } from "@react-types/table";
import React from "react";

import { Icon } from "@/components";
import { apiClient } from "@/util";
import { Document } from "@/types";
import { useThemeStore } from "@/store";

import "@xyflow/react/dist/style.css";

log.setLevel("debug");

const columns: {
  key: string;
  label: string;
  width: ColumnSize;
}[] = [
  {
    key: "name",
    label: "文件名",
    width: "20%",
  },
  {
    key: "file_path",
    label: "文件路径",
    width: "40%",
  },
  {
    key: "embedding_flag",
    label: "是否向量化",
    width: "10%",
  },
  {
    key: "actions",
    label: "操作",
    width: "20%",
  },
];

const DocumentPage: React.FC = () => {
  const location = useLocation();
  const { vs_id } = location.state || {};
  const { dark, toggleDark } = useThemeStore();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [running, setRunning] = useState<boolean>(false);
  const navigate = useNavigate();
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const fetchData = async () => {
    apiClient
      .post(`/v1/doc/list?vs_id=${vs_id}`)
      .then((response) => {
        setDocuments(response.data.data);
      })
      .catch((error) => {
        addToast({
          title: "获取文档数据失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const renderCell = React.useCallback((data: Document, columnKey: Key) => {
    function onDelete() {
      apiClient
        .post(`/v1/doc/delete?doc_id=${data.id}`)
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

    function onEmbed() {
      setRunning(true);
      apiClient
        .post(`/v1/doc/embed?doc_id=${data.id}`)
        .then(() => {
          fetchData();
          addToast({
            title: "向量化成功",
            timeout: 1000,
            shouldShowTimeoutProgress: true,
          });
        })
        .catch((error) => {
          addToast({
            title: "向量化失败:" + error.response.data.error,
            timeout: 1000,
            shouldShowTimeoutProgress: true,
            color: "danger",
          });
        })
        .finally(() => {
          setRunning(false);
        });
    }

    switch (columnKey) {
      case "actions":
        return (
          <div className="relative flex items-center gap-2">
            <Icon size={18} type="trash" onClick={onDelete} />
            {!data.embedding_flag && (
              <Icon size={18} type="embedding" onClick={onEmbed} />
            )}
          </div>
        );
      case "embedding_flag":
        return data.embedding_flag ? "是" : "否";
      default:
        return getKeyValue(data, columnKey);
    }
  }, []);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;

    if (!files || files.length === 0) return;

    const file = files[0];
    const formData = new FormData();

    formData.append("file", file);
    //formData.append("vs_id", vs_id);

    setRunning(true);
    apiClient
      .post(`/v1/doc/upload?vs_id=${vs_id}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then(() => {
        fetchData();
        addToast({
          title: "文档导入成功",
          timeout: 1000,
          shouldShowTimeoutProgress: true,
        });
      })
      .catch((error) => {
        addToast({
          title: "文档导入失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      })
      .finally(() => {
        setRunning(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      });
  };

  const triggerFileSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const topContent = useMemo(() => {
    return (
      <div className="flex items-center w-full">
        <input
          ref={fileInputRef}
          accept=".txt,.pdf,.doc,.docx,.md"
          style={{ display: "none" }}
          type="file"
          onChange={handleFileUpload}
        />
        <Icon
          className="ml-auto"
          size={24}
          type="import"
          onClick={() => {
            triggerFileSelect();
          }}
        />
      </div>
    );
  }, []);

  return (
    <div>
      <div className="flex w-full justify-between mb-1">
        <Icon
          className="ml-5"
          size={32}
          type="out"
          onClick={() => {
            navigate("/", { state: { activatedTab: "vectorstore" } });
          }}
        />
        <Switch
          className="mr-5"
          isSelected={!dark}
          size="md"
          onValueChange={toggleDark}
        >
          <Icon size={32} type="sun" />
        </Switch>
      </div>
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
        <TableBody emptyContent={"没有数据可显示"} items={documents}>
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
    </div>
  );
};

export default DocumentPage;
