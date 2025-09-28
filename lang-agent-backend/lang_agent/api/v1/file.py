import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from lang_agent.logger import get_logger

router = APIRouter(prefix="/file", tags=["File"])
logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
@router.get("/download/{filename}", summary="文件下载", status_code=200)
async def download(filename: str):
    dir_path = PROJECT_ROOT / "tmp/download"
    file_path = dir_path / filename
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException("文件不存在")
