from fastapi import APIRouter, HTTPException, Query

from lang_agent.api.v1.request_params import VectorStoreParams
from lang_agent.api.v1.response_models import (
    ApiResponse,
    VectorStoreResponse,
)
from lang_agent.db.database import (
    VectorStore,
    create_vectorstore,
    delete_vectorstore,
    list_vectorstores,
    save_vectorstore,
    select_vectorstore,
    update_vectorstore,
)
from lang_agent.logger import get_logger
from lang_agent.setting.manager import resource_manager
from lang_agent.util import (
    obj_to_model,
    objs_to_models
)

VECTORSTORE_NOT_FOUND = "VectorStore Not Found"

router = APIRouter(prefix="/vectorstore", tags=["VectorStore"])
logger = get_logger(__name__)


@router.get("/cached_vectorstores", status_code=200)
async def cached_vectorstores():
    data = resource_manager.vectorstore_map.keys()
    return ApiResponse(success=True, data=data)


@router.post("/save", status_code=200)
async def save(vectorstore: VectorStoreParams):
    await save_vectorstore(vectorstore, resource_manager)
    return ApiResponse(
        success=True,
    )


@router.post("/create", status_code=200)
async def create(vectorstore: VectorStoreParams) -> ApiResponse:
    return ApiResponse(
        success=True,
        data=await create_vectorstore(vectorstore, resource_manager)
    )


@router.post("/update", status_code=200)
async def update(vectorstore: VectorStoreParams) -> ApiResponse:
    await update_vectorstore(vectorstore, resource_manager)
    return ApiResponse(success=True)


@router.post("/delete", status_code=200)
async def delete(id: str) -> ApiResponse:
    delete_vectorstore(id, resource_manager)
    return ApiResponse(success=True)


@router.get("/select", status_code=200)
async def select(id: str = Query(..., description="VectorStore ID")) -> ApiResponse:
    vectorstore: VectorStore = select_vectorstore(id)
    if not vectorstore:
        logger.error("VectorStore Not Found")
        raise HTTPException(status_code=404, detail=VECTORSTORE_NOT_FOUND)
    return ApiResponse(
        success=True,
        data=obj_to_model(VectorStoreResponse, vectorstore)
    )


@router.get("/list", status_code=200)
async def vectorstores() -> ApiResponse:
    return ApiResponse(
        success=True,
        data=objs_to_models(VectorStoreResponse, list_vectorstores())
    )
