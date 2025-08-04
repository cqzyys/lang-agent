# Lang-Agent

This project is an agent configuration platform based on LangGraph technology that enables limited programmability. Traditional workflow-like projects typically pass the output of one node as the input of the next node. Lang-Agent allows custom [state variables](#state), which can be used as inputs and outputs for [nodes](#nodes) and [conditional edges](#conditional-edges), enabling more precise control.

## Tech Stack

- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [HeroUI](https://heroui.com)
- [ReactFlow](https://reactflow.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

## Installation and Startup

This project is divided into two sub-projects: the backend (`lang-agent-backend`) and the frontend (`lang-agent-frontend`).

### Clone the Project

```bash
git clone https://github.com/cqzyys/lang-agent.git
```

### lang-agent-backend: Installation and Startup

#### Initialize Python Environment

The backend project uses Poetry for package management. For usage instructions, refer to the [Poetry official documentation](https://python-poetry.org/docs/#installing-manually).

After installing Poetry, navigate to the backend project directory and execute the following commands to initialize the project environment:

```bash
cd lang-agent-backend
poetry env use python
poetry shell
poetry install 
```

#### Start the Project

```bash
python -m lang_agent.main
```

### lang-agent-frontend: Installation and Startup

#### Install Project Dependencies

The frontend project uses Yarn for package management. For usage instructions, refer to the [Yarn official documentation](https://yarnpkg.com/getting-started/install).

After installing Yarn, navigate to the frontend project directory and execute the following commands to install dependencies:

```bash
cd lang-agent-frontend
yarn install
```

#### Start the Project

```bash
yarn dev
```

Default access address: http://localhost:8820

## Usage Instructions

### Model Configuration

Click the **Model Configuration** tab to enter the model configuration page.

Click the **+** icon in the top-right corner to create a model connection.

- **Name**: Custom name for the model, must be unique.
- **Type**: Currently supports `llm` or `embedding`. The `llm` type can be used in nodes like [LLM Node](#llm-node), [ReactAgent](#reactagent), and [SupervisorAgent](#supervisoragent). The `embedding` type can be used in nodes like [Vector Retriever Node](#vector-retriever-node).
- **Channel**: Currently only supports channels compatible with OpenAI. More channels will be supported in the future.
- **Model Connection Parameters**: Model connection parameters. For details, refer to [ChatOpenAI](https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html).

### MCP Configuration

MCP essentially provides tools for large language models to access external services. It is only necessary in scenarios requiring tool calls. MCP can be used in nodes like [ReactAgent](#reactagent).

Click the **MCP Configuration** tab to enter the MCP configuration page.

Click the **+** icon in the top-right corner to configure an MCP connection.

- **Name**: Custom name for the MCP, must be unique.
- **Description**: Custom description for the MCP.
- **MCP Parameters**: MCP connection parameters. For details, refer to [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters).

### Agent Configuration

Agent configuration is the core functionality of this project, aiming to configure complex AI agents through visual drag-and-drop and input.

Click the **Agent Configuration** tab to view the Agent list. Click the **New Agent** card to enter the Agent configuration page.

The Agent configuration page is divided into two parts: the left side is called the **Resource Tree**, listing elements that can be used to build an Agent, including [nodes](#nodes), [agents](#agents), and [edges](#edges). The right side is called the **Canvas**, where you can display and configure the Agent. You can drag nodes and agents from the Resource Tree to the Canvas to create a new Agent.

#### Nodes

Nodes is a core concept in LangGraph and the basic elements for constructing an Agent. Most of the program logic is implemented through nodes. You can create nodes by dragging them from the Resource Tree to the Canvas. Selecting a node on the Canvas and pressing the Backspace key deletes it.

##### Start Node

The start node is the entry point of an Agent. Each Agent has exactly one start node.

- **Name**: Required, must be unique within the Agent.
- **Prompt**: Optional. If configured, a welcome message will be displayed when the Agent starts.
<a id="state"></a>
- **State Variables**: Required. A core concept in LangGraph, which can be understood as a global dictionary within the Agent. State variables are updated after node execution and can be used for logic control in nodes and conditional edges. By default, there is at least one state variable named `messages` to store conversation messages. Additional custom state variables can be added as needed. For usage rules, refer to [State Variable Usage Rules](#state-variable-usage-rules).

##### End Node

The end node is the endpoint of an Agent, indicating that the Agent execution is complete.

##### User Input Node

When user interaction is required, add a user input node to receive user input. For example, see [examples/loop_chat.json]()

- **Name**: Required, must be unique within the Agent.
- **Target State Variable**: Required. Defaults to `messages`, indicating that user input will be stored in the `messages` state variable.

##### LLM Node

A large language model node. Typically, an Agent will include at least one LLM node, which is the core node for implementing various scenarios. For example, see [examples/poet1.json]()

- **Name**: Required, must be unique within the Agent.
- **Model**: Required. Select from the LLM models configured in [Model Configuration](#model-configuration).
- **System Prompt**: Optional. The system prompt for the large language model. State variables can be used in the system prompt. For syntax rules, refer to [State Variable Usage Rules](#state-variable-usage-rules).
- **User Prompt**: Optional. The user prompt for the large language model. State variables can be used in the user prompt. For syntax rules, refer to [State Variable Usage Rules](#state-variable-usage-rules).

##### Counter Node

Implements an auto-increment function, used in conjunction with custom [state variables](#state). For example, see [examples/loop_demo.json]()

- **Name**: Required, must be unique within the Agent.
- **Target State Variable**: Required. Indicates which state variable will be auto-incremented.

##### Transform Node

Converts input and outputs it to the target state variable, used in conjunction with custom [state variables](#state). For example, see [examples/transform_demo.json]()

- **Name**: Required, must be unique within the Agent.
- **Target State Variable**: Required. Indicates which state variable will receive the transformed value.

##### Document Loader Node

Uploads documents in txt, pdf, docx, or md formats and outputs their content. For example, see [examples/vector_ingest_demo.json]()

- **Name**: Required, must be unique within the Agent.
- **Upload Document**: Required. Select a document from your local device.

##### Vector Ingest Node

A custom vector database node that implements vector storage. For example, see [vector_ingest_demo.json]()

- **Name**: Required, must be unique within the Agent.
- **Type**: Required. Select the vector database type (currently supports Postgres and Milvus).
- **URI**: Required. The URI of the vector database.
- **Username**: Optional. The username for the vector database (it is recommended to set this as an environment variable like `PGVECTOR_USER` or `MILVUS_USER`).
- **Password**: Optional. The password for the vector database (it is recommended to set this as an environment variable like `PGVECTOR_PASSWORD` or `MILVUS_PASSWORD`).
- **Database Name**: Required. The name of the vector database.
- **Collection Name**: Required. The name of the collection in the vector database.
- **Embedding Model**: Required. Select an embedding model from the configured [model configurations](#model-configuration).
- **Text Content**: Required. The text content to be vectorized and stored. State variables can be used here. For syntax rules, refer to [State Variable Usage Rules](#state-variable-usage-rules).

##### Vector Retriever Node

A custom vector database node that implements vector retrieval. For example, see [vector_retriever_demo.json]()

- **Name**: Required, must be unique within the Agent.
- **Type**: Required. Select the vector database type (currently supports Postgres and Milvus).
- **URI**: Required. The URI of the vector database.
- **Username**: Optional. The username for the vector database (it is recommended to set this as an environment variable like `PGVECTOR_USER` or `MILVUS_USER`).
- **Password**: Optional. The password for the vector database (it is recommended to set this as an environment variable like `PGVECTOR_PASSWORD` or `MILVUS_PASSWORD`).
- **Database Name**: Required. The name of the vector database.
- **Collection Name**: Required. The name of the collection in the vector database.
- **Embedding Model**: Required. Select an embedding model from the configured [model configurations](#model-configuration).
- **Search Keywords**: Required. The keywords for vector search. State variables can be used here. For syntax rules, refer to [State Variable Usage Rules](#state-variable-usage-rules).

#### Agents

Agents can also be viewed as special nodes, with two types: **Prebuilt Agents** and **Reusable Agents**.

<a id="rebuilt_agent"></a>
**Prebuilt Agents** are already encapsulated agents that can be directly dragged to the canvas for use.

<a id="reuse_agent"></a>
**Reusable Agents** are agents configured by users that have the **Reusable** option enabled in [Agent Configuration](#agent-configuration).

##### ReactAgent

Allows the large language model to autonomously call MCP tools to obtain the final output. MCP tools need to be configured in advance in [MCP Configuration](#mcp-configuration). For example, see [examples/react_agent_demo.json]()

- **Node Name**: Required, must be unique within the Agent.
- **Model**: Required. Select an LLM model from the [Model Configuration](#model-configuration).
- **Tools**: Required. Select tools available after completing the [MCP Configuration](#mcp-configuration).

##### SupervisorAgent

Allows the large language model to autonomously call other [Reusable Agents](#reuse-agent) to obtain the final output. For example, see [examples/supervisor_demo.json]()

- **Node Name**: Required, must be unique within the Agent.
- **Model**: Required. Select an LLM model from the [Model Configuration](#model-configuration).
- **Agent**: Required. Select an already configured [Reusable Agent](#reuse-agent).

#### Edges

Edges are a core concept in LangGraph, used to describe the execution order between nodes in an Agent. You can create edges by dragging between ports of two nodes on the Canvas. Selecting an edge and pressing the Backspace key deletes it.

##### Default Edge

Connects the source node to the target node, indicating that the target node will execute after the source node completes.

##### Conditional Edge

Connects the source node to the target node, indicating that after the source node completes, the target node will only execute if certain conditions are met. The condition expression of a conditional edge can use [state variables](#state). For syntax rules, refer to [State Variable Usage Rules](#state-variable-usage-rules). For example, see [examples/advance.json]()

#### Operations

##### Save

After configuring an Agent, click the Save button to save it to the database. Saved Agents can be viewed in the [Agent Configuration](#agent-configuration) section.

##### Run

Run the Agent, and the results can be viewed in the chatbot panel at the bottom-right of the interface.

##### Clear

Clears all content on the Canvas, including nodes and edges.

##### Export

Exports the content on the Canvas to a JSON file.

##### Import

Imports a JSON file onto the Canvas.

## State Variable Usage Rules

### messages State Variable

Can be used in system prompts, user prompts, and conditional edges. The syntax is `{{messages['x']}}`, where `x` is the name of a node in the Agent.

### Custom State Variables

Can be used in system prompts, user prompts, and conditional edges. The syntax is `{{y}}`, where `y` is the name of the custom state variable.
> Custom state variables currently do not support list types, but this may be added in the future.

## Custom Nodes

This project makes it very convenient to create custom nodes. Developers only need to focus on the implementation logic of the node itself and do not need to modify the project's execution code.

### Frontend Code Implementation

Create a file named `XXXNode.tsx` in the frontend project's extended node directory: `lang-agent-frontend/src/components/nodes/extend`. Pseudocode is as follows:

```tsx
import { Handle, Position, NodeResizer } from "@xyflow/react";
import { Card, CardBody, CardHeader } from "@heroui/react";

import {
  KeyInput,
  BaseNodeData,
  DEFAULT_HANDLE_STYLE,
  NodeProps,
  NodeConfig,
} from "@/components";

const XXXNodeConfig: NodeConfig<XXXNodeData> = {
  type: "xxx",
  description: "xxx",
  data: {
    id: "",
    type: "xxx",
    name: "xxx",
    yyy: "",
  },
  component: XXXNode,
};

export type XXXNodeData = BaseNodeData & {
  yyy: string;
};

export type XXXNodeProps = NodeProps<XXXNodeData>;

function XXXNode({ id, data, onDataChange }: XXXNodeProps) {
  return (
    <>
      <NodeResizer isVisible={false} />
      <Handle
        id="input"
        position={Position.Left}
        style={DEFAULT_HANDLE_STYLE}
        type="target"
      />
      <Card className="m-1 bg-slate-50">
        <CardHeader className="bg-slate-200">
          <div className="font-black ml-2 w-full">XXX</div>
        </CardHeader>
        <CardBody>
          <Form className="w-full max-w-xs">
          ...
          </Form>
        </CardBody>
      </Card>
      <Handle
        id="output"
        position={Position.Right}
        style={DEFAULT_HANDLE_STYLE}
        type="source"
      />
    </>
  );
}

export default XXXNodeConfig;
```

### Backend Code Implementation

Create a file named `XXX_node.py` in the backend project's extended node directory: `lang-agent-backend/lang-agent/node/extend`. Pseudocode is as follows:

```python
from typing import Optional, Union
from pydantic import Field, TypeAdapter
from ..core import BaseNode, BaseNodeData, BaseNodeParam


class XXXNodeData(BaseNodeData):
    yyy: str = Field(..., description="")


class XXXNodeParam(BaseNodeParam):
    data: Optional[XXXNodeData] = Field(default=None, description="Node Data")


class XXXNode(BaseNode):
    type = "xxx"

    def __init__(self, param: Union[XXXNodeParam, dict], state_schema: dict):
        adapter = TypeAdapter(XXXNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, state_schema)

    async def ainvoke(self, state: dict):
        '''ASync Business Processing Logic'''
``` 

## License

This project uses the MIT open-source license.