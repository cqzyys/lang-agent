from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Model(Base):
    __tablename__ = "model"
    id = Column(String, primary_key=True, unique=True, index=True, comment="模型id")
    name = Column(String, comment="模型名称")
    type = Column(String, comment="模型类型")
    channel = Column(String, comment="模型渠道")
    model_args = Column(String, comment="模型初始化参数")
    disabled = Column(Boolean, default=False, comment="是否禁用")


class Agent(Base):
    __tablename__ = "agent"
    id = Column(String, primary_key=True, unique=True, index=True, comment="Agent ID")
    name = Column(String, comment="Agent名称")
    description = Column(String, comment="Agent描述")
    data = Column(String, comment="Agent数据")
    reuse_flag = Column(Boolean, default=False, comment="是否可复用")
    disabled = Column(Boolean, default=False, comment="是否禁用")


class Mcp(Base):
    __tablename__ = "mcp"
    id = Column(String, primary_key=True, unique=True, index=True, comment="主键id")
    name = Column(String, comment="名称")
    description = Column(String, comment="MCP描述")
    mcp_args = Column(String, comment="MCP连接参数")
    disabled = Column(Boolean, default=False, comment="是否禁用")

class VectorStore(Base):
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
    disabled = Column(Boolean, default=False, comment="是否禁用")
