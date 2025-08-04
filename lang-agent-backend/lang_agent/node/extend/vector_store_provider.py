import os
from typing import Optional
from pydantic import BaseModel
from langchain_core.vectorstores import VectorStore
from dotenv import load_dotenv

from lang_agent.logger import get_logger
from lang_agent.setting import resource_manager

load_dotenv()
logger = get_logger(__name__)

class VectorStoreConfig(BaseModel):
    vs_type: str
    uri: str
    user: str
    password: str
    db_name: str
    collection_name: str
    embedding_name: str

class VectorStoreProvider:
    @staticmethod
    def init(config: VectorStoreConfig) -> Optional[VectorStore]:
        if config.embedding_name not in resource_manager.models.get("embedding", {}):
            logger.error("Embedding Model Not Found: %s", config.embedding_name)
            return None
        match config.vs_type:
            case "postgress":
                from langchain_postgres import PGVector
                try:
                    user = config.user or os.getenv("PGVECTOR_USER", "")
                    password = config.password or os.getenv(
                        "PGVECTOR_PASSWORD", ""
                    )
                    connection = f"postgresql+psycopg://{user}:{password}@{config.uri}/{config.db_name}"
                    return PGVector(
                        embeddings=resource_manager.models["embedding"][
                            config.embedding_name],
                        collection_name=config.collection_name,
                        connection=connection,
                        use_jsonb=True,
                    )
                except Exception as e:
                    logger.error("Failed To Initialize PGVector: %s", e)
                    raise RuntimeError("Failed To Initialize PGVector") from e
            case "milvus":
                from langchain_milvus import Milvus
                from pymilvus import MilvusException
                try:
                    user = config.user or os.getenv("MILVUS_USER", "")
                    password = config.password or os.getenv(
                        "MILVUS_PASSWORD", ""
                    )
                    return Milvus(
                        embedding_function=resource_manager.models["embedding"][
                            config.embedding_name],
                        connection_args={
                            "uri": config.uri,
                            "user": user,
                            "password": password,
                            "db_name": config.db_name,
                        },
                        collection_name=config.collection_name,
                    )
                except MilvusException as e:
                    logger.error("Failed To Initialize Milvus: %s", e)
                    raise RuntimeError("Failed To Initialize Milvus") from e
            case _:
                logger.error("Unsupported Vector Store Type: %s", config.vs_type)
                raise RuntimeError(f"Unsupported Vector Store Type: {config.vs_type}")
