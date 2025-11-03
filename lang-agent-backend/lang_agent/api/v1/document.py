import os
from pathlib import Path
import traceback

from fastapi import APIRouter, UploadFile

from lang_agent.data_schema.request_params import DocumentParams
from lang_agent.data_schema.response_models import ApiResponse
from lang_agent.logger import get_logger
from lang_agent.db import (
    list_documents, create_document, delete_document, select_document,
    embed_document,
)
from lang_agent.util.convert import obj_to_model,objs_to_models
from lang_agent.data_schema.response_models import DocumentResponse

router = APIRouter(prefix="/doc", tags=["Document API"])
logger = get_logger(__name__)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
DOC_PATH = PROJECT_ROOT / "lang_agent/db/documents"

@router.post("/list", status_code=200)
async def list_docs(vs_id:str) -> ApiResponse:
    return ApiResponse(
        success=True,
        data=objs_to_models(list_documents(vs_id),DocumentResponse),
    )

@router.post("/upload", status_code=200)
async def upload(vs_id:str, file: UploadFile) -> ApiResponse:
    file_path = None
    try:
        dir_path = PROJECT_ROOT / "lang_agent/db/documents" / vs_id
        os.makedirs(dir_path, exist_ok=True)
        file_path = dir_path / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        params = DocumentParams(
            name=file.filename,
            file_path=str(file_path),
            vs_id=vs_id,
        )
        doc_id = create_document(params)
        return ApiResponse(
            success=True,
            data=doc_id,
        )
    except Exception as e:
        logger.error(traceback.format_exc())
        if file_path and file_path.exists():
            try:
                os.remove(file_path)
            except Exception as error:
                logger.error("Failed to cleanup file: %s", str(error))
        return ApiResponse(
            success=False,
            error=str(e),
        )

@router.post("/delete", status_code=200)
async def delete(doc_id:str) -> ApiResponse:
    delete_document(doc_id)
    return ApiResponse(
        success=True,
    )

@router.post("/select", status_code=200)
async def select(doc_id:str) -> ApiResponse:
    return ApiResponse(
        success=True,
        data=obj_to_model(select_document(doc_id),DocumentResponse),
    )

@router.post("/embed", status_code=200)
async def embed(doc_id:str) -> ApiResponse:
    embed_document(doc_id)
    return ApiResponse(
        success=True,
    )
