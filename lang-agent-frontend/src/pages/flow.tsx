import type { Agent, ConditionData } from "@/types";
import type {
  StartNodeData,
  UserInputNodeData,
  LLMNodeData,
  VLMNodeData,
  ReUseAgentNodeData,
  ReactAgentNodeData,
  SupervisorAgentNodeData,
} from "@/components";
import type {
  Node,
  Edge,
  EdgeProps,
  NodeChange,
  EdgeChange,
} from "@xyflow/react";

import log from "loglevel";
import { nanoid } from "nanoid";
import { useState, useEffect, useCallback, useMemo } from "react";
import {
  applyEdgeChanges,
  applyNodeChanges,
  ReactFlowProvider,
} from "@xyflow/react";
import {
  Accordion,
  AccordionItem,
  addToast,
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerHeader,
  Radio,
  RadioGroup,
  Switch,
  useDisclosure,
} from "@heroui/react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  StartNode,
  EndNode,
  UserInputNode,
  LLMNode,
  VLMNode,
  ReactAgentNode,
  SupervisorAgentNode,
  ReuseAgentNode,
  ConditionEdge,
  DroppableReactFlow,
  DraggableNode,
  NodeConfig,
  Icon,
} from "@/components";
import { apiClient } from "@/util";
import {
  useModelStore,
  useAgentStore,
  useMcpStore,
  useThemeStore,
  useFlowStore,
} from "@/store";
import "@xyflow/react/dist/style.css";

log.setLevel("debug");

const FlowPage: React.FC = () => {
  const location = useLocation();
  const { init_agent } = location.state || {};
  let init_nodes = [];
  let init_edges = [];

  if (init_agent && init_agent.data) {
    let agent_data = init_agent.data;

    if (typeof agent_data === "string") {
      try {
        agent_data = JSON.parse(agent_data);
      } catch (error) {
        log.error("Failed to parse agent_data as JSON:", error);
        agent_data = {};
      }
    }

    init_nodes = agent_data.nodes || [];
    init_edges = agent_data.edges || [];
  }
  const [agent, setAgent] = useState<Agent>(init_agent || { id: nanoid(8) });
  const [nodes, setNodes] = useState<Node[]>(init_nodes);
  const [edges, setEdges] = useState<Edge[]>(init_edges);
  const [reuseAgents, setReuseAgents] = useState<Agent[]>([]);
  const { dark, toggleDark } = useThemeStore();
  const navigate = useNavigate();
  const [extendNodeTypes, setExtendNodeTypes] = useState<Record<string, any>>(
    {},
  );
  const [extendNodes, setExtendNodes] = useState<
    Array<{ type: string; description: string; data: any }>
  >([]);
  const [customNodeTypes, setCustomNodeTypes] = useState<Record<string, any>>(
    {},
  );
  const [customNodes, setCustomNodes] = useState<
    Array<{ type: string; description: string; data: any }>
  >([]);
  const [result, setResult] = useState("");
  const {
    isOpen: isDrawerOpen,
    onOpen: onDrawerOpen,
    onOpenChange: onDrawerOpenChange,
  } = useDisclosure();

  useEffect(() => {
    useModelStore.getState().fetchModels();
    useAgentStore.getState().fetchReuseAgents();
    useMcpStore.getState().fetchMcpMap();
  }, []);

  useEffect(() => {
    useFlowStore.getState().setNodes(nodes);
  }, [nodes]);

  useEffect(() => {
    const fetchData = async () => {
      apiClient
        .get("/v1/agent/list_reuse")
        .then((response) => {
          setReuseAgents(response.data.data);
        })
        .catch((error) => {
          addToast({
            title: "获取Agent数据失败:" + error.response.data.error,
            timeout: 1000,
            shouldShowTimeoutProgress: true,
            color: "danger",
          });
        });
    };

    fetchData();
  }, []);
  const updateNodeData = useCallback(
    (nodeId: string, newData: Record<string, any>) => {
      setNodes((nds) =>
        nds.map(
          (node: Node) =>
            node.id === nodeId ? { ...node, data: newData } : node, //如果是nodeId则更新node的data数据
        ),
      );
    },
    [setNodes],
  );
  const updateEdgeData = useCallback(
    (edgeId: string, newData: Record<string, any>) => {
      setEdges((eds) =>
        eds.map(
          (edge: Edge) =>
            edge.id === edgeId ? { ...edge, data: newData } : edge, //如果是edgeId则更新edge的data数据
        ),
      );
    },
    [setEdges],
  );

  useEffect(() => {
    const loadNodeModules = async (
      nodeModules: Record<string, () => Promise<any>>,
    ) => {
      const types: Record<string, any> = {};
      const nodes: Array<{
        type: string;
        description: string;
        data: any;
      }> = [];
      const nodeModulePaths = Object.keys(nodeModules);
      const modulePromises = nodeModulePaths.map(async (path) => {
        const module = (await nodeModules[path]()) as {
          default: NodeConfig<any>;
        };
        const config = module.default;

        if (config && config.type && config.component) {
          types[config.type] = ({ data, id }: { data: any; id: string }) => (
            <config.component
              data={data}
              id={id}
              onDataChange={(newData) => updateNodeData(id, newData)}
            />
          );
          nodes.push({
            type: config.type,
            description: config.description,
            data: config.data,
          });
        }
      });

      await Promise.all(modulePromises);

      return { types, nodes };
    };
    const loadExtendNodeModules = async () => {
      const extendModules = import.meta.glob(
        "../components/nodes/extend/*.tsx",
      );
      const { types, nodes } = await loadNodeModules(extendModules);

      setExtendNodeTypes(types);
      setExtendNodes(nodes);
    };

    const loadCustomNodeModules = async () => {
      const customModules = import.meta.glob(
        "../components/nodes/custom/*.tsx",
      );
      const { types, nodes } = await loadNodeModules(customModules);

      setCustomNodeTypes(types);
      setCustomNodes(nodes);
    };

    loadExtendNodeModules();
    loadCustomNodeModules();
  }, []);

  //log("extendNodeTypes=", extendNodeTypes);
  //log("customNodeTypes=", customNodeTypes);

  const nodeTypes = useMemo(() => {
    return {
      ...extendNodeTypes,
      ...customNodeTypes,
      start: ({ data, id }: { data: StartNodeData; id: string }) => (
        <StartNode
          data={data}
          id={id}
          onDataChange={(newData) => updateNodeData(id, newData)}
        />
      ),
      end: () => <EndNode onDrawerOpen={onDrawerOpen} />,
      user_input: ({ data, id }: { data: UserInputNodeData; id: string }) => (
        <UserInputNode
          data={data}
          id={id}
          onDataChange={(newData) => updateNodeData(id, newData)}
        />
      ),
      llm: ({ data, id }: { data: LLMNodeData; id: string }) => (
        <LLMNode
          data={data}
          id={id}
          onDataChange={(newData) => updateNodeData(id, newData)}
        />
      ),
      vlm: ({ data, id }: { data: VLMNodeData; id: string }) => (
        <VLMNode
          data={data}
          id={id}
          onDataChange={(newData) => updateNodeData(id, newData)}
        />
      ),
      react_agent: ({ data, id }: { data: ReactAgentNodeData; id: string }) => (
        <ReactAgentNode
          data={data}
          id={id}
          onDataChange={(newData) => updateNodeData(id, newData)}
        />
      ),
      supervisor_agent: ({
        data,
        id,
      }: {
        data: SupervisorAgentNodeData;
        id: string;
      }) => (
        <SupervisorAgentNode
          data={data}
          id={id}
          onDataChange={(newData) => updateNodeData(id, newData)}
        />
      ),
      reuse_agent: ({ data, id }: { data: ReUseAgentNodeData; id: string }) => (
        <ReuseAgentNode
          data={data}
          id={id}
          onDataChange={(newData) => updateNodeData(id, newData)}
        />
      ),
    };
  }, [extendNodeTypes, customNodeTypes]);

  //console.log("nodeTypes=", nodeTypes);

  const edgeTypes = useMemo(
    () => ({
      condition: (edgeProps: EdgeProps) => {
        const { id, data } = edgeProps;

        return (
          <ConditionEdge
            {...edgeProps}
            data={data as ConditionData}
            onDataChange={(newData) => updateEdgeData(id, newData)}
          />
        );
      },
    }),
    [],
  );
  const onNodesChange = useCallback((changes: NodeChange[]) => {
    if (!Array.isArray(changes)) return;
    setNodes((nds) => applyNodeChanges(changes, nds));
  }, []);
  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((eds) => applyEdgeChanges(changes, eds));
  }, []);

  const coreNodes = [
    {
      description: "开始",
      type: "start",
      data: {
        name: "start",
        guiding_words: "你好，有什么可以帮助你的吗？",
        state_schema: '{ "messages": "list" }',
      },
    },
    { description: "结束", type: "end", data: { name: "end" } },
    {
      description: "输入",
      type: "user_input",
      data: { name: "user_input", state_field: "messages" },
    },
    {
      description: "LLM",
      type: "llm",
      data: {
        name: "llm",
        model: "qwen",
        system_prompt: "你是一个聪明的助手，你可以回答我的任何问题",
        user_prompt: "",
      },
    },
    {
      description: "VLM",
      type: "vlm",
      data: {
        name: "vlm",
        model: "o4-mini",
        system_prompt: "",
        user_prompt: "描述一下这张图片",
        image_url: "",
      },
    },
  ];

  const prebuiltAgents = [
    {
      description: "React",
      type: "react_agent",
      data: { name: "react_agent", model: "qwen2.5", tools: "" },
    },
    {
      description: "Supervisor",
      type: "supervisor_agent",
      data: { name: "supervisor_agent", model: "qwen2.5", agents: "" },
    },
  ];

  const [selectedEdgeType, setSelectedEdgeType] = useState("default");
  const prebuiltEdges = [
    { description: "默认边", type: "default" },
    { description: "条件边", type: "condition" },
  ];

  const onDragStart = (
    event: React.DragEvent<HTMLElement>,
    node: Record<string, any>,
  ) => {
    event.dataTransfer.setData("application/reactflow", JSON.stringify(node));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div>
      <div className="flex w-full justify-between mb-1">
        <Icon
          className="ml-5"
          size={32}
          type="out"
          onClick={() => {
            navigate("/");
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
      <div className="grid grid-cols-12 w-screen h-screen">
        <div className="col-span-2">
          <Accordion
            isCompact
            defaultExpandedKeys={[
              "core_nodes",
              "extend_nodes",
              "rebuilt_agents",
            ]}
            selectionMode="multiple"
            variant="splitted"
          >
            <AccordionItem
              key="core_nodes"
              aria-label="核心节点"
              title="核心节点"
            >
              <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                {coreNodes.map((nodeData) => (
                  <DraggableNode
                    key={nodeData.type}
                    node={nodeData}
                    onDragStart={onDragStart}
                  />
                ))}
              </ul>
            </AccordionItem>
            <AccordionItem
              key="extend_nodes"
              aria-label="扩展节点"
              title="扩展节点"
            >
              <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                {extendNodes.map((nodeData) => (
                  <DraggableNode
                    key={nodeData.type}
                    node={nodeData}
                    onDragStart={onDragStart}
                  />
                ))}
              </ul>
            </AccordionItem>
            <AccordionItem
              key="custom_nodes"
              aria-label="自定义节点"
              title="自定义节点"
            >
              <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                {customNodes.map((nodeData) => (
                  <DraggableNode
                    key={nodeData.type}
                    node={nodeData}
                    onDragStart={onDragStart}
                  />
                ))}
              </ul>
            </AccordionItem>
            <AccordionItem
              key="rebuilt_agents"
              aria-label="预制Agent"
              title="预制Agent"
            >
              {prebuiltAgents.map((node) => (
                <DraggableNode
                  key={node.type}
                  node={node}
                  onDragStart={onDragStart}
                />
              ))}
            </AccordionItem>
            <AccordionItem
              key="reuse_agents"
              aria-label="可复用Agent"
              title="可复用Agent"
            >
              {reuseAgents.map((agent) => {
                const node = {
                  type: "reuse_agent",
                  description: agent.name,
                  data: {
                    id: agent.id,
                    name: agent.name,
                    description: agent.description,
                    data: agent.data,
                  },
                };

                return (
                  <DraggableNode
                    key={agent.id}
                    node={node}
                    onDragStart={onDragStart}
                  />
                );
              })}
            </AccordionItem>
            <AccordionItem key="edges" aria-label="边" title="边">
              <RadioGroup color="secondary" defaultValue={selectedEdgeType}>
                {prebuiltEdges.map((edge) => (
                  <Radio
                    key={edge.type}
                    value={edge.type}
                    onChange={() => setSelectedEdgeType(edge.type)}
                  >
                    {edge.description}
                  </Radio>
                ))}
              </RadioGroup>
            </AccordionItem>
          </Accordion>
        </div>
        {/*右侧画布*/}
        <ReactFlowProvider>
          <div className="col-span-10">
            <DroppableReactFlow
              agent={agent}
              edgeTypes={edgeTypes}
              edges={edges}
              nodeTypes={nodeTypes}
              nodes={nodes}
              selectedEdgeType={selectedEdgeType}
              setAgent={setAgent}
              setEdges={setEdges}
              setNodes={setNodes}
              setResult={setResult}
              onEdgesChange={onEdgesChange}
              onNodesChange={onNodesChange}
            />
          </div>
        </ReactFlowProvider>

        <Drawer
          isOpen={isDrawerOpen}
          size="sm"
          onOpenChange={onDrawerOpenChange}
        >
          <DrawerContent>
            {() => (
              <>
                <DrawerHeader className="flex flex-col gap-1 bg-cyan-200">
                  执行结果
                </DrawerHeader>
                <DrawerBody className="bg-slate-100">
                  <p>{result}</p>
                </DrawerBody>
              </>
            )}
          </DrawerContent>
        </Drawer>
      </div>
    </div>
  );
};

export default FlowPage;
