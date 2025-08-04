import json
import logging
import os
from contextlib import contextmanager
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from xid import XID

from lang_agent.api.v1.request_params import AgentParams, MCPParams, ModelParams
from lang_agent.setting import ResourceManager

from .models import Agent, Base, Mcp, Model

load_dotenv()
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


class Database:
    def __init__(self):
        self.engine = None
        self._initialized = False

    def configure(self, db_url, pool_size=5, max_overflow=2, pool_recycle=3600):
        if self._initialized:
            raise RuntimeError("Database is already initialized")
        self.engine = create_engine(
            db_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
            echo=True,
        )
        self._initialized = True

    def get_engine(self):
        if self.engine is None:
            raise RuntimeError(
                "Database engine not configured. Please call configure() first."
            )
        return self.engine

    def init_database(self):
        Base.metadata.create_all(self.get_engine())


db = Database()


def setup_database_connection():
    db_url = os.getenv("DB_URL", "sqlite:///lang_agent/db/main.db")
    pool_size = int(os.getenv("POOL_SIZE", "5"))
    max_overflow = int(os.getenv("MAX_OVERFLOW", "2"))
    pool_recycle = int(os.getenv("POOL_RECYCLE", "3600"))
    db.configure(db_url, pool_size, max_overflow, pool_recycle)
    db.init_database()


@contextmanager
def get_session():
    session = sessionmaker(bind=db.get_engine(), expire_on_commit=False)()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def create_model(
    model: ModelParams, resource_manager: Optional[ResourceManager] = None
) -> str:
    with get_session() as session:
        if select_model_by_name(model.name):
            raise ValueError("Model Name Already Exists")
        id = XID().string()
        entity = Model(
            id=id,
            name=model.name,
            type=model.type,
            channel=model.channel,
            model_args=model.model_args,
        )
        session.add(entity)
        if resource_manager is not None:
            resource_manager.models[entity.type][entity.name] = (
                resource_manager.init_model(entity)
            )
        return id


def update_model(
    model: ModelParams, resource_manager: Optional[ResourceManager] = None
):
    with get_session() as session:
        existent_entity = select_model_by_name(model.name)
        if existent_entity and existent_entity.id != model.id:
            raise ValueError("Model Name Already Exists")
        stmt = select(Model).where(Model.id == model.id)
        entity = session.scalars(stmt).first()
        if resource_manager is not None:
            if entity.model_args != model.model_args or (
                entity.disabled == True and model.disabled == False
            ):
                resource_manager.models[entity.type][entity.name] = (
                    resource_manager.init_model(entity)
                )
            if entity.disabled == False and model.disabled == True:
                del resource_manager.models[entity.type][entity.name]
        entity.name = model.name
        entity.type = model.type
        entity.channel = model.channel
        entity.model_args = model.model_args
        entity.disabled = model.disabled


def save_model(model: ModelParams, resource_manager: Optional[ResourceManager] = None):
    if not select_model(model.id):
        create_model(model, resource_manager)
    else:
        update_model(model, resource_manager)


def delete_model(id: str, resource_manager: Optional[ResourceManager] = None):
    with get_session() as session:
        stmt = select(Model).where(Model.id == id)
        entity = session.scalars(stmt).first()
        if resource_manager is not None and entity.disabled == False:
            del resource_manager.models[entity.type][entity.name]
        session.delete(entity)


def select_model(id: str) -> Model:
    with get_session() as session:
        stmt = select(Model).where(Model.id == id)
        entity = session.scalars(stmt).first()
        return entity


def select_model_by_name(name: str) -> Model:
    with get_session() as session:
        stmt = select(Model).where(Model.name == name)
        entity = session.scalars(stmt).first()
        return entity


def list_models() -> list[Model]:
    with get_session() as session:
        stmt = select(Model)
        entities = session.scalars(stmt).all()
        return entities


def list_available_models() -> list[Model]:
    with get_session() as session:
        stmt = select(Model).where(Model.disabled == False)
        entities = session.scalars(stmt).all()
        return entities


def list_llm_models() -> list[Model]:
    with get_session() as session:
        stmt = select(Model).where(Model.type == "llm" and Model.disabled == False)
        entities = session.scalars(stmt).all()
        return entities


def list_embedding_models() -> list[Model]:
    with get_session() as session:
        stmt = select(Model).where(
            Model.type == "embedding" and Model.disabled == False
        )
        entities = session.scalars(stmt).all()
        return entities


def save_agent(agent: AgentParams):
    if not select_agent(agent.id):
        create_agent(agent)
    else:
        update_agent(agent)


def create_agent(agent: AgentParams):
    with get_session() as session:
        if select_agent_by_name(agent.name):
            raise ValueError("Agent Name Already Exists")
        entity = Agent(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            data=json.dumps(agent.data, ensure_ascii=False),
            reuse_flag=False,
        )
        session.add(entity)


def update_agent(agent: AgentParams):
    with get_session() as session:
        existent_entity = select_agent_by_name(agent.name)
        if existent_entity and existent_entity.id != agent.id:
            raise ValueError("Agent Name Already Exists")
        stmt = select(Agent).where(Agent.id == agent.id)
        entity = session.scalars(stmt).first()
        entity.name = agent.name
        entity.description = agent.description
        entity.data = json.dumps(agent.data, ensure_ascii=False)
        entity.reuse_flag = agent.reuse_flag


def delete_agent(id: str):
    with get_session() as session:
        stmt = select(Agent).where(Agent.id == id)
        entity = session.scalars(stmt).first()
        session.delete(entity)


def list_agents() -> list[Agent]:
    with get_session() as session:
        stmt = select(Agent)
        entities = session.scalars(stmt).all()
        return entities


def list_available_agents() -> list[Agent]:
    with get_session() as session:
        stmt = select(Agent).where(Agent.disabled == False)
        entities = session.scalars(stmt).all()
        return entities


def list_reuse_agents() -> list[Agent]:
    with get_session() as session:
        stmt = select(Agent).where(Agent.reuse_flag == True and Agent.disabled == False)
        entities = session.scalars(stmt).all()
        return entities


def select_agent(id: str) -> Agent:
    with get_session() as session:
        stmt = select(Agent).where(Agent.id == id)
        entity = session.scalars(stmt).first()
        return entity


def select_agent_by_name(name: str) -> Agent:
    with get_session() as session:
        stmt = select(Agent).where(Agent.name == name)
        entity = session.scalars(stmt).first()
        return entity


async def save_mcp(mcp: MCPParams, resource_manager: Optional[ResourceManager] = None):
    if not select_mcp(mcp.id):
        await create_mcp(mcp, resource_manager)
    else:
        await update_mcp(mcp, resource_manager)


async def create_mcp(
    mcp: MCPParams, resource_manager: Optional[ResourceManager] = None
) -> str:
    with get_session() as session:
        if select_mcp_by_name(mcp.name):
            raise ValueError("MCP Name Already Exists")
        id = XID().string()
        entity = Mcp(
            id=id, name=mcp.name, description=mcp.description, mcp_args=mcp.mcp_args
        )
        session.add(entity)
        if resource_manager is not None and entity.disabled == False:
            resource_manager.mcp_map[entity.name] = await resource_manager.init_mcp(
                entity
            )
        return id


async def update_mcp(
    mcp: MCPParams, resource_manager: Optional[ResourceManager] = None
):
    with get_session() as session:
        existent_entity = select_mcp_by_name(mcp.name)
        if existent_entity and existent_entity.id != mcp.id:
            raise ValueError("Mcp Name Already Exists")
        stmt = select(Mcp).where(Mcp.id == mcp.id)
        entity = session.scalars(stmt).first()
        if resource_manager is not None:
            if entity.mcp_args != mcp.mcp_args or (
                entity.disabled == True and mcp.disabled == False
            ):
                resource_manager.mcp_map[entity.name] = await resource_manager.init_mcp(
                    entity
                )
            if entity.disabled == False and mcp.disabled == True:
                del resource_manager.mcp_map[entity.name]
        entity.name = mcp.name
        entity.description = mcp.description
        entity.mcp_args = mcp.mcp_args
        entity.disabled = mcp.disabled


def delete_mcp(id: str, resource_manager: Optional[ResourceManager] = None):
    with get_session() as session:
        stmt = select(Mcp).where(Mcp.id == id)
        entity = session.scalars(stmt).first()
        if resource_manager is not None and entity.disabled == False:
            del resource_manager.mcp_map[entity.name]
        session.delete(entity)


def select_mcp(id: str) -> Mcp:
    with get_session() as session:
        stmt = select(Mcp).where(Mcp.id == id)
        entity = session.scalars(stmt).first()
        return entity


def select_mcp_by_name(name: str) -> Mcp:
    with get_session() as session:
        stmt = select(Mcp).where(Mcp.name == name)
        entity = session.scalars(stmt).first()
        return entity


def list_mcps() -> list[Mcp]:
    with get_session() as session:
        stmt = select(Mcp)
        entities = session.scalars(stmt).all()
        return entities


def list_available_mcps() -> list[Mcp]:
    with get_session() as session:
        stmt = select(Mcp).where(Mcp.disabled == False)
        entities = session.scalars(stmt).all()
        return entities
