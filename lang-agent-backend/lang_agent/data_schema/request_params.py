from typing import Optional

from pydantic import BaseModel, Field


class ModelParams(BaseModel):
    id: Optional[str] = Field(None, description="模型id")
    name: str = Field(..., description="模型名称")
    type: str = Field(..., description="模型类型")
    channel: Optional[str] = Field(None, description="模型渠道")
    model_args: Optional[str] = Field(None, description="模型初始化参数")
    disabled: Optional[bool] = Field(False, description="是否禁用")


class AgentParams(BaseModel):
    id: str = Field(..., description="AgentId")
    name: str = Field(..., description="Agent名称")
    description: Optional[str] = Field(None, description="Agent描述")
    data: Optional[dict] = Field(None, description="Agent数据")
    reuse_flag: Optional[bool] = Field(False, description="是否复用")
    disabled: Optional[bool] = Field(False, description="是否禁用")


class AgentRunParams(BaseModel):
    chat_id: str = Field(..., description="会话ID")
    agent_data: dict = Field(..., description="Agent数据")
    state: dict = Field(..., description="状态变量")
    agent_name: Optional[str] = Field(default=None, description="Agent名称")


class MCPParams(BaseModel):
    id: Optional[str] = Field(None, description="MCPid")
    name: str = Field(..., description="MCP名称")
    description: Optional[str] = Field(None, description="MCP描述")
    mcp_args: Optional[str] = Field(None, description="MCP连接参数")
    disabled: Optional[bool] = Field(False, description="是否禁用")

class VectorStoreParams(BaseModel):
    id: Optional[str] = Field(None, description="向量库id")
    name: str = Field(..., description="向量库名称")
    type: str = Field(..., description="向量库类型")
    uri: str = Field(..., description="URI")
    user: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    db_name: str = Field(..., description="数据库名")
    collection_name: str = Field(..., description="集合名")
    embedding_name: str = Field(..., description="嵌入模型")
    disabled: Optional[bool] = Field(False, description="是否禁用")
