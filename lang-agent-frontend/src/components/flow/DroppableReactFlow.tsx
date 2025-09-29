import type {
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
} from "@xyflow/react";

import log from "loglevel";
import { useCallback, useState } from "react";
import {
  useReactFlow,
  ReactFlow,
  Panel,
  MiniMap,
  addEdge,
} from "@xyflow/react";
import { nanoid } from "nanoid";
import { Button, useDisclosure, addToast, Spinner } from "@heroui/react";

import AgentSaveModal from "./AgentSaveModal";
import CustomChatBotProvider from "./CustomChatBotProvider";

import { Agent } from "@/types";
import { apiClient } from "@/util";
import { Icon, DEFAULT_EDGE_MARKER_STYLE } from "@/components";
import { getAgentData } from "@/util";

log.setLevel("debug");

interface DroppableReactFlowProps {
  agent: Agent;
  setAgent: React.Dispatch<React.SetStateAction<Agent>>;
  nodes: Node[];
  edges: Edge[];
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  nodeTypes: Record<string, any>;
  edgeTypes: Record<string, any>;
  setNodes: React.Dispatch<React.SetStateAction<Node[]>>;
  setEdges: React.Dispatch<React.SetStateAction<Edge[]>>;
  selectedEdgeType: string;
  setResult: React.Dispatch<React.SetStateAction<string>>;
}
export default function DroppableReactFlow({
  agent,
  setAgent,
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  nodeTypes,
  edgeTypes,
  setNodes,
  setEdges,
  selectedEdgeType,
  setResult,
}: DroppableReactFlowProps) {
  const { screenToFlowPosition } = useReactFlow();
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [running, setRunning] = useState<boolean>(false);

  //放置节点时触发
  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const node_str = event.dataTransfer.getData("application/reactflow");
    const node = JSON.parse(node_str);

    if (!node.type) return;
    const position = screenToFlowPosition({
      x: event.clientX,
      y: event.clientY,
    });
    //console.log(node.data);
    const newNode = {
      id: nanoid(8),
      type: node.type,
      position: position,
      data: node.data,
    };

    //更新节点数据
    setNodes((nds) => [...nds, newNode]);
  };

  const edgeDataMap: Record<string, any> = {
    condition: { expr: "" },
  };

  //连接时添加edge
  const onConnect = useCallback(
    (connection: Connection) => {
      const sourceNode = nodes.find((node) => node.id === connection.source);
      const targetNode = nodes.find((node) => node.id === connection.target);

      if (sourceNode && targetNode) {
        const newEdge = {
          ...connection,
          id: nanoid(8),
          type: selectedEdgeType,
          data: edgeDataMap[selectedEdgeType] || undefined,
          source: sourceNode.id, // 原始id作为 source
          target: targetNode.id, // 原始id作为 target
          sourceHandle: "output",
          targetHandle: "input",
          markerEnd: DEFAULT_EDGE_MARKER_STYLE,
        };

        setEdges((eds) => addEdge(newEdge, eds));
      }
    },
    [setEdges, nodes, selectedEdgeType],
  );

  const cleanFlow = () => {
    setNodes([]);
    setEdges([]);
  };

  const onClean = () => {
    cleanFlow();
  };

  //导入Agent的方法
  const onImport = () => {
    const input = document.createElement("input");

    input.type = "file";
    input.accept = ".json";
    input.onchange = (event) => {
      const target = event.target as HTMLInputElement;
      const file = target.files?.[0];

      if (!file) return;
      cleanFlow();
      const reader = new FileReader();

      reader.readAsText(file);
      reader.onload = (e) => {
        try {
          const result = e.target?.result;

          if (typeof result === "string") {
            const agent_json = JSON.parse(result);

            setAgent(agent_json);
            setNodes(agent_json.data.nodes);
            setEdges(agent_json.data.edges);
          } else {
            addToast({
              title: "文件读取失败",
              timeout: 1000,
              shouldShowTimeoutProgress: true,
              color: "danger",
            });
          }
        } catch (error) {
          if (error instanceof Error) {
            addToast({
              title: "文件解析失败:" + error.message,
              timeout: 1000,
              shouldShowTimeoutProgress: true,
              color: "danger",
            });
          }
        }
      };
    };
    input.click();
  };

  //保存Agent的方法
  const onSave = useCallback(() => {
    if (nodes.length === 0) {
      addToast({
        title: "请先添加节点",
        timeout: 1000,
        shouldShowTimeoutProgress: true,
        color: "danger",
      });

      return;
    }
    const agent_data = getAgentData(nodes, edges);
    const updated_agent = {
      ...agent,
      type: "reuse_agent",
      data: agent_data,
    };

    setAgent(updated_agent);
    log.debug(agent);
    apiClient
      .post("/v1/agent/save", updated_agent)
      .then(() => {
        addToast({
          title: "保存成功",
          timeout: 1000,
          shouldShowTimeoutProgress: true,
        });
      })
      .catch((error) => {
        addToast({
          title: "保存失败:" + error.response.data.error,
          timeout: 1000,
          shouldShowTimeoutProgress: true,
          color: "danger",
        });
      });
  }, [nodes, edges, agent]);

  //导出Agent
  const onExport = useCallback(() => {
    if (nodes.length === 0) {
      addToast({
        title: "请先添加节点",
        timeout: 1000,
        shouldShowTimeoutProgress: true,
        color: "danger",
      });

      return;
    } else {
      const agent_data = getAgentData(nodes, edges);
      const json_data = {
        ...agent,
        type: "reuse_agent",
        data: agent_data,
      };
      const json_str = JSON.stringify(json_data);
      //模拟下载
      const blob = new Blob([json_str], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = `${json_data.name}.json`;
      link.click();
      URL.revokeObjectURL(url);
    }
  }, [nodes, edges, agent]);

  return (
    <>
      <ReactFlow
        edgeTypes={edgeTypes}
        edges={edges}
        nodeTypes={nodeTypes}
        nodes={nodes}
        onConnect={onConnect}
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        onEdgesChange={onEdgesChange}
        onNodesChange={onNodesChange}
      >
        <Panel position="top-left">
          <Button
            color="primary"
            size="sm"
            startContent={<Icon color="#006fee" type="save" />}
            variant="shadow"
            onPress={onOpen}
          >
            保存
          </Button>
        </Panel>
        <Panel position="top-right" style={{ right: 100 }}>
          <Button
            isIconOnly
            color="primary"
            size="sm"
            variant="shadow"
            onPress={onClean}
          >
            <Icon color="#006fee" type="clean" />
          </Button>
        </Panel>
        <Panel position="top-right" style={{ right: 50 }}>
          <Button
            isIconOnly
            color="primary"
            size="sm"
            variant="shadow"
            onPress={onImport}
          >
            <Icon color="#006fee" type="import" />
          </Button>
        </Panel>
        <Panel position="top-right">
          <Button
            isIconOnly
            color="primary"
            size="sm"
            variant="shadow"
            onPress={onExport}
          >
            <Icon color="#006fee" type="export" />
          </Button>
        </Panel>
        <CustomChatBotProvider
          agent_data={getAgentData(nodes, edges)}
          setResult={setResult}
          setRunning={setRunning}
        />
        {running && (
          <Spinner className="absolute top-1/4 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50" />
        )}
        <MiniMap />
      </ReactFlow>
      <AgentSaveModal
        agent={agent}
        isOpen={isOpen}
        setAgent={setAgent}
        onOpenChange={onOpenChange}
        onSave={onSave}
      />
    </>
  );
}
