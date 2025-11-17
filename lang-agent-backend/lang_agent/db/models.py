from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.orm import declarative_base

from lang_agent.util.alchemy import JSONEncodedDict

Base = declarative_base()

class ModelType(str, Enum):
    LLM = "llm"
    EMBEDDING = "embedding"
    VLM = "vlm"

class BaseEntity(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    disabled = Column(Boolean, default=False, comment="是否禁用")

class Model(BaseEntity):
    __tablename__ = "model"
    id = Column(String, primary_key=True, unique=True, index=True, comment="模型id")
    name = Column(String, comment="模型名称")
    type = Column(String, comment="模型类型")
    channel = Column(String, comment="模型渠道")
    model_args = Column(String, comment="模型初始化参数")


class Agent(BaseEntity):
    __tablename__ = "agent"
    id = Column(String, primary_key=True, unique=True, index=True, comment="Agent ID")
    name = Column(String, comment="Agent名称")
    description = Column(String, comment="Agent描述")
    data = Column(JSONEncodedDict, comment="Agent数据")
    reuse_flag = Column(Boolean, default=False, comment="是否可复用")


class Mcp(BaseEntity):
    __tablename__ = "mcp"
    id = Column(String, primary_key=True, unique=True, index=True, comment="主键id")
    name = Column(String, comment="名称")
    description = Column(String, comment="MCP描述")
    mcp_args = Column(String, comment="MCP连接参数")

class VectorStore(BaseEntity):
    __tablename__ = "vectorstore"
    id = Column(String, primary_key=True, unique=True, index=True, comment="主键id")
    name = Column(String, comment="名称")
    type = Column(String, comment="向量库类型")
    uri = Column(String, comment="URI")
    user = Column(String, comment="用户名")
    password = Column(String, comment="密码")
    db_name = Column(String, comment="数据库名")
    collection_name = Column(String, comment="集合名")
    embedding_name = Column(String, comment="嵌入模型")

class Document(BaseEntity):
    __tablename__ = "document"
    id = Column(String, primary_key=True, unique=True, index=True, comment="文档ID")
    name = Column(String, comment="文档名")
    file_path = Column(String, comment="文件路径")
    meta_data = Column(JSONEncodedDict, comment="元数据")
    vs_id = Column(String, comment="向量库ID")
    embedding_flag = Column(Boolean, default=False, comment="是否向量化")


class Chunk(BaseEntity):
    __tablename__ = "chunk"
    id = Column(String, primary_key=True, unique=True, index=True, comment="文档块ID")
    content = Column(String, comment="内容")
    meta_data = Column(JSONEncodedDict, comment="元数据")
    doc_id = Column(String, comment="文档ID")
    embedding_flag = Column(Boolean, default=False, comment="是否向量化")
