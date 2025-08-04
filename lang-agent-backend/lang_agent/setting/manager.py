import json
import traceback
from typing import Any, Dict, List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from lang_agent.db.models import Mcp, Model
from lang_agent.logger import get_logger

logger = get_logger(__name__)


class ResourceInitializationError(Exception):
    pass


class ResourceManager:
    def __init__(self):
        self.models = {"llm": {}, "embedding": {}}
        self.mcp_map: Dict[str, Dict[str, BaseTool]] = {}

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


resource_manager = ResourceManager()
