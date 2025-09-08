from fastapi import APIRouter, HTTPException, Query

from lang_agent.data_schema.request_params import ModelParams
from lang_agent.data_schema.response_models import (
    ApiResponse,
    ModelResponse,
)
from lang_agent.db.database import (
    Model,
    create_model,
    delete_model,
    list_embedding_models,
    list_llm_models,
    list_models,
    save_model,
    select_model,
    update_model,
)
from lang_agent.logger import get_logger
from lang_agent.setting.manager import resource_manager
from lang_agent.util import (
    obj_to_model,
    objs_to_models
)

MODEL_NOT_FOUND = "Model Not Found"

router = APIRouter(prefix="/model", tags=["Model"])
logger = get_logger(__name__)


@router.post("/save", status_code=200)
async def save(model: ModelParams):
    save_model(model, resource_manager)
    return ApiResponse(
        success=True,
    )


@router.post("/create", status_code=200)
async def create(model: ModelParams) -> ApiResponse:
    return ApiResponse(success=True, data=create_model(model, resource_manager))


@router.post("/update", status_code=200)
async def update(model: ModelParams) -> ApiResponse:
    update_model(model, resource_manager)
    return ApiResponse(success=True)


@router.post("/delete", status_code=200)
async def delete(id: str) -> ApiResponse:
    delete_model(id, resource_manager)
    return ApiResponse(success=True)


@router.get("/select", status_code=200)
async def select(id: str = Query(..., description="Model ID")) -> ApiResponse:
    model: Model = select_model(id)
    if not model:
        logger.error("Model Not Found")
        raise HTTPException(status_code=404, detail=MODEL_NOT_FOUND)
    return ApiResponse(success=True, data=obj_to_model(ModelResponse, model))


@router.get("/list", status_code=200)
async def list() -> ApiResponse:
    return ApiResponse(success=True, data=objs_to_models(ModelResponse, list_models()))


@router.get("/cached_llm", status_code=200)
async def cached_llm() -> ApiResponse:
    return ApiResponse(success=True, data=resource_manager.models["llm"].keys())


@router.get("/cached_embedding", status_code=200)
async def cached_embedding() -> ApiResponse:
    return ApiResponse(success=True, data=resource_manager.models["embedding"].keys())


@router.get("/llm_models", status_code=200)
async def llm_models() -> ApiResponse:
    return ApiResponse(
        success=True, data=objs_to_models(ModelResponse, list_llm_models())
    )


@router.get("/embedding_models", status_code=200)
async def embedding_models() -> ApiResponse:
    return ApiResponse(
        success=True, data=objs_to_models(ModelResponse, list_embedding_models())
    )
