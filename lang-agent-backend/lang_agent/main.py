import argparse
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError

from lang_agent.api import router_v1
from lang_agent.api.v1.response_models import ApiResponse
from lang_agent.db import setup_database_connection
from lang_agent.logger import get_logger
from lang_agent.setting import async_checkpointer_shutdown, resource_manager
from lang_agent.util.util import error_to_str

logger = get_logger(__name__)


async def resource_init():
    logger.debug("init_mcps start......")
    await resource_manager.init_mcp_map()
    logger.debug("init_mcps end")
    logger.debug("init_models start......")
    resource_manager.init_models()
    logger.debug("init_models end")
    logger.debug("init_vectorstores start......")
    resource_manager.init_vectorstore_map()
    logger.debug("init_vectorstores end")


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(Path("lang_agent/tmp"), exist_ok=True)
    logger.debug("setup_database_connection start......")
    setup_database_connection()
    logger.debug("setup_database_connection end")
    await resource_init()
    yield
    await async_checkpointer_shutdown()


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        logger.error(exc.errors())
        return JSONResponse(
            status_code=422,
            content=ApiResponse(
                success=False,
                error=error_to_str(exc),
                status_code=422,
            ).model_dump(),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ):
        logger.error(exc.errors())
        return JSONResponse(
            status_code=422,
            content=ApiResponse(
                success=False,
                error=error_to_str(exc),
                status_code=422,
            ).model_dump(),
        )

    @app.exception_handler(ValueError)
    async def value_validation_exception_handler(request: Request, exc: ValueError):
        logger.error(exc)
        return JSONResponse(
            status_code=422,
            content=ApiResponse(
                success=False,
                error=error_to_str(exc),
                status_code=422,
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                success=False,
                error=error_to_str(exc),
                status_code=exc.status_code,
            ).model_dump(),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error(exc.detail)
        return JSONResponse(
            status_code=409,
            content=ApiResponse(
                success=False,
                error=error_to_str(exc),
                status_code=409,
            ).model_dump(),
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(exc.detail)
        return JSONResponse(
            status_code=500,
            content=ApiResponse(
                success=False,
                error=error_to_str(exc),
                status_code=500,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(exc)
        return JSONResponse(
            status_code=404,
            content=ApiResponse(
                success=False,
                error=error_to_str(exc),
                status_code=404,
            ).model_dump(),
        )


def run(host, port):
    # 初始化FastAPI
    app = FastAPI(title="Lang-Agent集成API", version="1.0.0", lifespan=lifespan)

    # 跨域配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def docs():
        return RedirectResponse(url="/docs")

    @app.get("/health")
    def get_health():
        return {"status": "OK"}

    # 全局异常处理
    register_exception_handlers(app)

    app.include_router(router_v1)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default=os.getenv("APP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("APP_PORT", "8810")))
    args = parser.parse_args()
    run(args.host, args.port)
