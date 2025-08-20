from typing import Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel):
    success: bool
    data: str | dict | list[T] | None = None
    error: Union[str, list, dict, None] = None
    status_code: int = 200


class AgentResponse(BaseModel):
    id: str = Field(..., description="AgentId")
    name: str = Field(..., description="Agent名称")
    description: Optional[str] = Field(None, description="Agent描述")
    data: Optional[str] = Field(None, description="Agent数据")
    reuse_flag: bool = Field(..., description="是否可复用")
    disabled: Optional[bool] = Field(False, description="是否禁用")


class McpResponse(BaseModel):
    id: str = Field(..., description="MCP ID")
    name: str = Field(..., description="MCP名称")
    description: Optional[str] = Field(None, description="MCP描述")
    mcp_args: Optional[str] = Field(None, description="MCP连接参数")
    disabled: Optional[bool] = Field(False, description="是否禁用")


class ModelResponse(BaseModel):
    id: str = Field(..., description="模型id")
    name: str = Field(..., description="模型名称")
    type: str = Field(..., description="模型类型")
    channel: Optional[str] = Field(None, description="模型渠道")
    model_args: Optional[str] = Field(None, description="模型初始化参数")
    disabled: Optional[bool] = Field(False, description="是否禁用")

class VectorStoreResponse(BaseModel):
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

def orm_to_model(model_cls: Type[BaseModel], orm_obj) -> BaseModel:
    return model_cls.model_validate(orm_obj, from_attributes=True).model_dump()


def orms_to_models(model_cls: Type[BaseModel], orm_objs) -> list[BaseModel]:
    return [orm_to_model(model_cls, orm_obj) for orm_obj in orm_objs]
