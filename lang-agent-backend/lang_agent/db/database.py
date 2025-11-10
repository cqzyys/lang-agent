import logging
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from langchain_text_splitters import CharacterTextSplitter
from sqlalchemy import create_engine, delete, desc, select, update
from sqlalchemy.orm import sessionmaker
from xid import XID

from lang_agent.data_schema.request_params import (
    AgentParams,
    DocumentParams,
    MCPParams,
    ModelParams,
    VectorStoreParams
)
from lang_agent.setting.manager import resource_manager
from lang_agent.util import load_document
from lang_agent.logger import get_logger

from .models import Agent, Base, Chunk, Document, Mcp, Model, ModelType, VectorStore

load_dotenv()
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

logger = get_logger(__name__)

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
    model: ModelParams
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
    model: ModelParams
):
    with get_session() as session:
        existent_entity = select_model_by_name(model.name)
        if existent_entity and existent_entity.id != model.id:
            raise ValueError("Model Name Already Exists")
        stmt = select(Model).where(Model.id == model.id)
        entity = session.scalars(stmt).first()
        if resource_manager is not None:
            if entity.name == model.name and entity.type==model.type and entity.model_args == model.model_args and entity.disabled == model.disabled:
                pass
            else:
                if entity.name in resource_manager.models[entity.type]:
                    if entity.disabled == False:
                        del resource_manager.models[entity.type][entity.name]
                if model.disabled == False:
                    resource_manager.models[model.type][model.name] = (
                        resource_manager.init_model(model)
                    )
        entity.name = model.name
        entity.type = model.type
        entity.channel = model.channel
        entity.model_args = model.model_args
        entity.disabled = model.disabled


def save_model(model: ModelParams):
    if not select_model(model.id):
        create_model(model)
    else:
        update_model(model)


def delete_model(id: str):
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
        stmt = select(Model).order_by(Model.name)
        entities = session.scalars(stmt).all()
        return entities


def list_available_models(model_type:ModelType=None) -> list[Model]:
    with get_session() as session:
        stmt = select(Model).where(Model.disabled == False)
        if model_type:
            stmt = stmt.where(Model.type == model_type.value)
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
            data=agent.data,
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
        entity.data = agent.data
        entity.reuse_flag = agent.reuse_flag


def delete_agent(id: str):
    with get_session() as session:
        stmt = select(Agent).where(Agent.id == id)
        entity = session.scalars(stmt).first()
        session.delete(entity)


def list_agents() -> list[Agent]:
    with get_session() as session:
        stmt = select(Agent).order_by(Agent.name)
        entities = session.scalars(stmt).all()
        return entities


def list_available_agents() -> list[Agent]:
    with get_session() as session:
        stmt = select(Agent).where(Agent.disabled == False).order_by(Agent.name)
        entities = session.scalars(stmt).all()
        return entities


def list_reuse_agents() -> list[Agent]:
    with get_session() as session:
        stmt = select(Agent).where(Agent.reuse_flag == True and Agent.disabled == False).order_by(Agent.name)
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


async def save_mcp(mcp: MCPParams):
    if not select_mcp(mcp.id):
        await create_mcp(mcp)
    else:
        await update_mcp(mcp)


async def create_mcp(
    mcp: MCPParams
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
    mcp: MCPParams
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


def delete_mcp(id: str):
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
        stmt = select(Mcp).order_by(Mcp.name)
        entities = session.scalars(stmt).all()
        return entities


def list_available_mcps() -> list[Mcp]:
    with get_session() as session:
        stmt = select(Mcp).where(Mcp.disabled == False).order_by(Mcp.name)
        entities = session.scalars(stmt).all()
        return entities


async def save_vectorstore(
        vectorstore: VectorStoreParams
    ):
    if not select_vectorstore(vectorstore.id):
        await create_vectorstore(vectorstore)
    else:
        await update_vectorstore(vectorstore)


async def create_vectorstore(
    vectorstore: VectorStoreParams
) -> str:
    with get_session() as session:
        if select_vectorstore_by_name(vectorstore.name):
            raise ValueError("VectorStore Name Already Exists")
        id = XID().string()
        entity = VectorStore(
            id=id,
            name=vectorstore.name,
            type=vectorstore.type,
            uri=vectorstore.uri,
            db_name=vectorstore.db_name,
            collection_name=vectorstore.collection_name,
            embedding_name=vectorstore.embedding_name,
            password=vectorstore.password,
            user=vectorstore.user,
            disabled=vectorstore.disabled
        )
        session.add(entity)
        if resource_manager is not None and entity.disabled == False:
            vs = resource_manager.init_vectorstore(entity)
            if vs is not None:
                resource_manager.vectorstore_map[entity.name] = vs
        return id

def del_vs(name: str):
    if name in resource_manager.vectorstore_map:
        del resource_manager.vectorstore_map[name]
async def update_vectorstore(
    vectorstore: VectorStoreParams
):
    with get_session() as session:
        existent_entity = select_vectorstore_by_name(vectorstore.name)
        if existent_entity and existent_entity.id != vectorstore.id:
            raise ValueError("VectorStore Name Already Exists")
        stmt = select(VectorStore).where(VectorStore.id == vectorstore.id)
        entity = session.scalars(stmt).first()
        if resource_manager is not None:
            if vectorstore.disabled is False:
                vs = resource_manager.init_vectorstore(entity)
                if vs is not None:
                    resource_manager.vectorstore_map[entity.name] = vs
                else:
                    del_vs(entity.name)
            else:
                del_vs(entity.name)
        entity.name = vectorstore.name
        entity.disabled = vectorstore.disabled
        entity.type = vectorstore.type
        entity.uri = vectorstore.uri
        entity.user = vectorstore.user
        entity.password = vectorstore.password
        entity.db_name = vectorstore.db_name
        entity.collection_name = vectorstore.collection_name
        entity.embedding_name = vectorstore.embedding_name
        entity.disabled = vectorstore.disabled


def delete_vectorstore(id: str):
    with get_session() as session:
        stmt = select(VectorStore).where(VectorStore.id == id)
        entity = session.scalars(stmt).first()
        if resource_manager is not None and entity.disabled is False:
            del_vs(entity.name)
        session.delete(entity)


def select_vectorstore(id: str) -> VectorStore:
    with get_session() as session:
        stmt = select(VectorStore).where(VectorStore.id == id)
        entity = session.scalars(stmt).first()
        return entity


def select_vectorstore_by_name(name: str) -> VectorStore:
    with get_session() as session:
        stmt = select(VectorStore).where(VectorStore.name == name)
        entity = session.scalars(stmt).first()
        return entity


def list_vectorstores() -> list[VectorStore]:
    with get_session() as session:
        stmt = select(VectorStore).order_by(VectorStore.name)
        entities = session.scalars(stmt).all()
        return entities


def list_available_vectorstores() -> list[VectorStore]:
    with get_session() as session:
        stmt = select(VectorStore).where(
            VectorStore.disabled == False
        ).order_by(VectorStore.name)
        entities = session.scalars(stmt).all()
        return entities


def list_documents(vs_id:str) -> list[Document]:
    with get_session() as session:
        stmt = select(Document).where(
            Document.vs_id == vs_id
        ).where(
            Document.disabled == False
        ).order_by(desc(Document.created_at))
        entities = session.scalars(stmt).all()
        return entities

def create_document(params: DocumentParams) -> str:
    with get_session() as session:
        docs = load_document(params.file_path)
        try:
            chunk_size = int(os.getenv("CHUNK_SIZE", "2048"))
        except ValueError:
            chunk_size = 2048
            logger.warning("Invalid CHUNK_SIZE value, using default value: 2048")
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_size*0.05
        )
        for doc in docs:
            entity = Document(
                id=XID().string(),
                name=params.name,
                vs_id=params.vs_id,
                file_path=params.file_path,
            )
            session.add(entity)
            session.flush()
            entity.meta_data = doc.metadata | {
                "doc_id": entity.id,
                "created_at": entity.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }

            chunks = splitter.split_documents([doc])
            for chunk in chunks:
                chunk_entity = Chunk(
                    id=XID().string(),
                    content=chunk.page_content,
                    doc_id=entity.id,
                )
                session.add(chunk_entity)
                session.flush()
                chunk_entity.meta_data = chunk.metadata | {
                    "doc_id": entity.id,
                    "chunk_id": chunk_entity.id,
                    "created_at": chunk_entity.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            return entity.id

def delete_document(id: str):
    with get_session() as session:
        stmt = select(Document).where(Document.id == id)
        entity = session.scalars(stmt).first()
        if entity is not None:
            if entity.embedding_flag:
                vs_name = select_vectorstore(entity.vs_id).name
                vs = resource_manager.vectorstore_map[vs_name]
                chunk_ids = [chunk.id for chunk in list_chunks(id)]
                vs.delete(chunk_ids)
            chunk_stmt = delete(Chunk).where(Chunk.doc_id == entity.id)
            session.execute(chunk_stmt)
            session.delete(entity)
            try:
                os.remove(entity.file_path)
            except Exception as error:
                raise error

def select_document(id: str) -> Document:
    with get_session() as session:
        stmt = select(Document).where(Document.id == id)
        entity = session.scalars(stmt).first()
        return entity

def embed_document(doc_id: str):
    from langchain_core.documents import Document as Doc
    document = select_document(doc_id)
    vs_name = select_vectorstore(document.vs_id).name
    if vs_name not in resource_manager.vectorstore_map:
        raise ValueError("VectorStore Not Found")
    vs = resource_manager.vectorstore_map[vs_name]
    try:
        chunks: list[Chunk] = list_chunks(doc_id)
        docs = [
            Doc(
                id=chunk.id,
                page_content=chunk.content,
                metadata=chunk.meta_data
            ) for chunk in chunks
        ]
        vs.add_documents(docs)
        update_embedding_flag(doc_id, True)
    except Exception as error:
        logger.error("Failed to embed document: %s",error)
        raise error

def update_embedding_flag(doc_id: str, flag: bool):
    with get_session() as session:
        chunk_stmt = update(Chunk).where(Chunk.doc_id == doc_id).values(embedding_flag=flag)
        session.execute(chunk_stmt)
        stmt = update(Document).where(Document.id == doc_id).values(embedding_flag=flag)
        session.execute(stmt)

def list_chunks(doc_id: str) -> list[Chunk]:
    with get_session() as session:
        stmt = select(Chunk).where(Chunk.doc_id == doc_id)
        entities = session.scalars(stmt).all()
        return entities
