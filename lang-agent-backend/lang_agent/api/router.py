from fastapi import APIRouter

from lang_agent.api.v1 import (
    agent_router,
    mcp_router,
    model_router,
    vectorstore_router,
    document_router
)

router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(agent_router)
router_v1.include_router(model_router)
router_v1.include_router(mcp_router)
router_v1.include_router(vectorstore_router)
router_v1.include_router(document_router)
