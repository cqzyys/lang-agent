from fastapi import APIRouter, HTTPException, Query

from lang_agent.data_schema.request_params import ModelParams
from lang_agent.data_schema.response_models import (
    ApiResponse,
    ModelResponse,
)
from lang_agent.db.database import (
    Model,
    ModelType,
    create_model,
    delete_model,
    list_available_models,
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
    save_model(model)
    return ApiResponse(
        success=True,
    )


@router.post("/create", status_code=200)
async def create(model: ModelParams) -> ApiResponse:
    return ApiResponse(success=True, data=create_model(model))


@router.post("/update", status_code=200)
async def update(model: ModelParams) -> ApiResponse:
    update_model(model)
    return ApiResponse(success=True)


@router.post("/delete", status_code=200)
async def delete(id: str) -> ApiResponse:
    delete_model(id)
    return ApiResponse(success=True)


@router.get("/select", status_code=200)
async def select(id: str = Query(..., description="Model ID")) -> ApiResponse:
    model: Model = select_model(id)
    if not model:
        logger.error("Model Not Found")
        raise HTTPException(status_code=404, detail=MODEL_NOT_FOUND)
    return ApiResponse(success=True, data=obj_to_model(model,ModelResponse))


@router.get("/list", status_code=200)
async def models() -> ApiResponse:
    return ApiResponse(success=True, data=objs_to_models(list_models(),ModelResponse))


@router.get("/cached_llm", status_code=200)
async def cached_llm() -> ApiResponse:
    return ApiResponse(
        success=True,
        data=list(resource_manager.models[ModelType.LLM.value].keys())
    )


@router.get("/cached_embedding", status_code=200)
async def cached_embedding() -> ApiResponse:
    return ApiResponse(
        success=True,
        data=list(resource_manager.models[ModelType.EMBEDDING.value].keys())
    )

@router.get("/cached_vlm", status_code=200)
async def cached_vlm() -> ApiResponse:
    return ApiResponse(
        success=True,
        data=list(resource_manager.models[ModelType.VLM.value].keys())
    )


@router.get("/llm_models", status_code=200)
async def llm_models() -> ApiResponse:
    return ApiResponse(
        success=True,
        data=objs_to_models(list_available_models(ModelType.LLM),ModelResponse)
    )

@router.get("/embedding_models", status_code=200)
async def embedding_models() -> ApiResponse:
    return ApiResponse(
        success=True,
        data=objs_to_models(list_available_models(ModelType.EMBEDDING),ModelResponse)
    )

@router.get("/vlm_models", status_code=200)
async def vlm_models() -> ApiResponse:
    return ApiResponse(
        success=True,
        data=objs_to_models(list_available_models(ModelType.VLM),ModelResponse)
    )
