from fastapi import APIRouter, HTTPException, Query

from lang_agent.data_schema.request_params import MCPParams
from lang_agent.data_schema.response_models import (
    ApiResponse,
    McpResponse,
)
from lang_agent.db.database import (
    Mcp,
    create_mcp,
    delete_mcp,
    list_mcps,
    save_mcp,
    select_mcp,
    update_mcp,
)
from lang_agent.logger import get_logger
from lang_agent.setting.manager import resource_manager
from lang_agent.util import (
    obj_to_model,
    objs_to_models
)

MCP_NOT_FOUND = "Mcp Not Found"

router = APIRouter(prefix="/mcp", tags=["MCP"])
logger = get_logger(__name__)


@router.get("/cached_mcp_map", status_code=200)
async def cached_mcp_map():
    data = {key: list(item.keys()) for key, item in resource_manager.mcp_map.items()}
    return ApiResponse(success=True, data=data)


@router.post("/save", status_code=200)
async def save(mcp: MCPParams):
    await save_mcp(mcp)
    return ApiResponse(
        success=True,
    )


@router.post("/create", status_code=200)
async def create(mcp: MCPParams) -> ApiResponse:
    return ApiResponse(success=True, data=await create_mcp(mcp))


@router.post("/update", status_code=200)
async def update(mcp: MCPParams) -> ApiResponse:
    await update_mcp(mcp)
    return ApiResponse(success=True)


@router.post("/delete", status_code=200)
async def delete(id: str) -> ApiResponse:
    delete_mcp(id)
    return ApiResponse(success=True)


@router.get("/select", status_code=200)
async def select(id: str = Query(..., description="MCP ID")) -> ApiResponse:
    mcp: Mcp = select_mcp(id)
    if not mcp:
        logger.error("MCP Not Found")
        raise HTTPException(status_code=404, detail=MCP_NOT_FOUND)
    return ApiResponse(success=True, data=obj_to_model(mcp,McpResponse))


@router.get("/list", status_code=200)
async def mcps() -> ApiResponse:
    return ApiResponse(success=True, data=objs_to_models(list_mcps(),McpResponse))
