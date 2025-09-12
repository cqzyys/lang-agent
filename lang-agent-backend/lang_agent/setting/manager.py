import traceback
import json
import os
from typing import Any, Dict, List

from langchain_core.tools import BaseTool
from langchain_core.vectorstores import VectorStore as VS
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from lang_agent.db.models import Mcp, Model, VectorStore
from lang_agent.logger import get_logger

logger = get_logger(__name__)


class ResourceInitializationError(Exception):
    pass


class ResourceManager:
    def __init__(self):
        self.models = {"llm": {}, "embedding": {}}
        self.mcp_map: Dict[str, Dict[str, BaseTool]] = {}
        self.vectorstore_map: Dict[str, VS] = {}

    def init_models(self):
        from lang_agent.db.database import list_available_models

        model_list: List[Model] = list_available_models()
        for model in model_list:
            try:
                self.models[model.type][model.name] = self.init_model(model)
            except ResourceInitializationError:
                logger.error(
                    "Initialize Model [%s] Failed: \n %s",
                    model.name,
                    traceback.format_exc()
                )
                continue

    def init_model(self, model: Model) -> Any:
        try:
            args = json.loads(model.model_args)
        except json.JSONDecodeError as je:
            raise ResourceInitializationError(
                f"Invalid arguments for {model.name}"
            ) from je
        match model.type:
            case "llm":
                if model.channel == "openai":
                    return ChatOpenAI(**args)
                raise ResourceInitializationError(
                    f"Unsupported LLM channel: {model.channel} for {model.name}"
                )
            case "embedding":
                if model.channel == "openai":
                    return OpenAIEmbeddings(**args)
                raise ResourceInitializationError(
                    f"Unsupported LLM channel: {model.channel} for {model.name}"
                )
            case _:
                raise ResourceInitializationError(f"Unknown Model Type: {model.type}")

    async def init_mcp_map(self):
        from lang_agent.db.database import list_available_mcps

        mcps: List[Mcp] = list_available_mcps()
        for mcp in mcps:
            try:
                tools_map = await self.init_mcp(mcp)
                self.mcp_map[mcp.name] = tools_map
            except ResourceInitializationError:
                continue
        logger.info("Initialize MCP Success: %s", self.mcp_map)

    async def init_mcp(self, mcp: Mcp) -> Dict[str, BaseTool]:
        try:
            mcp_args = json.loads(mcp.mcp_args)
        except json.JSONDecodeError as je:
            raise ResourceInitializationError(
                f"Invalid arguments for {mcp.name}"
            ) from je
        try:
            tools: List[BaseTool] = await load_mcp_tools(
                session=None, connection=mcp_args
            )
            return {tool.name: tool for tool in tools}
        except ExceptionGroup as e:
            logger.error(
                "Initialize MCP [%s] Error: \n %s", mcp.name, traceback.format_exc()
            )
            raise ResourceInitializationError(f"Failed to initialize {mcp.name}") from e

    def init_vectorstore_map(self):
        from lang_agent.db.database import list_available_vectorstores

        vectorstore_list: List[VectorStore] = list_available_vectorstores()
        for vectorstore in vectorstore_list:
            try:
                vs = self.init_vectorstore(
                        vectorstore
                    )
                if vs is not None:
                    self.vectorstore_map[vectorstore.name] = vs
            except ResourceInitializationError:
                logger.error(
                    "Initialize VectorStore [%s] Failed: \n %s",
                    vectorstore.name,
                    traceback.format_exc()
                )
                continue

    def init_vectorstore(self, vectorstore: VectorStore) -> VS:
        if vectorstore.embedding_name not in self.models.get("embedding", {}):
            logger.error("Embedding Model Not Found: %s", vectorstore.embedding_name)
            return None
        match vectorstore.type:
            case "postgres":
                from langchain_postgres import PGVector
                try:
                    user = vectorstore.user or os.getenv("PGVECTOR_USER", "")
                    password = vectorstore.password or os.getenv(
                        "PGVECTOR_PASSWORD", ""
                    )
                    connection = f"postgresql+psycopg://{user}:{password}@{vectorstore.uri}/{vectorstore.db_name}"
                    return PGVector(
                        embeddings=resource_manager.models["embedding"][
                            vectorstore.embedding_name],
                        collection_name=vectorstore.collection_name,
                        connection=connection,
                        use_jsonb=True,
                    )
                except Exception as e:
                    logger.error("Failed To Initialize PGVector: %s", e)
                    return None
                    #raise RuntimeError("Failed To Initialize PGVector") from e
            case "milvus":
                from langchain_milvus import Milvus
                from pymilvus import MilvusException
                try:
                    user = vectorstore.user or os.getenv("MILVUS_USER", "")
                    password = vectorstore.password or os.getenv(
                        "MILVUS_PASSWORD", ""
                    )
                    return Milvus(
                        embedding_function=resource_manager.models["embedding"][
                            vectorstore.embedding_name],
                        connection_args={
                            "uri": vectorstore.uri,
                            "user": user,
                            "password": password,
                            "db_name": vectorstore.db_name,
                        },
                        collection_name=vectorstore.collection_name,
                        auto_id=True,
                    )
                except MilvusException as e:
                    logger.error("Failed To Initialize Milvus: %s", e)
                    return None
                    #raise RuntimeError("Failed To Initialize Milvus") from e
            case _:
                logger.error("Unsupported Vector Store Type: %s", vectorstore.type)
                return None

resource_manager = ResourceManager()
