from typing import Optional

from pydantic import BaseModel, Field


class Target(BaseModel):
    type: str = Field(..., description="边类型")
    target: str = Field(..., description="目标节点ID")
    target_name: str = Field(..., description="目标节点名称")
    expr: Optional[str] = Field(default=None, description="条件表达式")


class EdgeData(BaseModel):
    source: str = Field(..., description="源节点ID")
    source_name: str = Field(..., description="源节点名称")
    targets: Optional[dict[str, Target]] = Field(
        default_factory=dict, description="目标节点数据"
    )
