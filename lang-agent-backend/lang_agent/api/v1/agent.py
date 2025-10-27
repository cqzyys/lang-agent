import json
import traceback

from fastapi import APIRouter, Body, HTTPException, Query

from lang_agent.data_schema.request_params import AgentParams, AgentRunParams
from lang_agent.data_schema.response_models import (
    AgentResponse,
    ApiResponse,
)
from lang_agent.db.database import (
    Agent,
    create_agent,
    delete_agent,
    list_available_agents,
    list_reuse_agents,
    save_agent,
    select_agent,
    update_agent,
)
from lang_agent.graph import GraphEngine
from lang_agent.logger import get_logger
from lang_agent.util import (
    obj_to_model,
    objs_to_models
)

AGENT_NOT_FOUND = "Agent Not Found"
INVALID_AGENT_DATA = "Invalid Agent Data Format"
GRAPH_COMPILE_FAILED = "Graph Compile Failed"

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = get_logger(__name__)


@router.post("/save", status_code=200)
async def save(agent: AgentParams):
    save_agent(agent)
    return ApiResponse(
        success=True,
    )


@router.post("/create", status_code=200)
async def create(agent: AgentParams) -> ApiResponse:
    create_agent(agent)
    return ApiResponse(
        success=True,
    )


@router.get("/select", status_code=200)
async def select(id: str = Query(..., description="Agent ID")) -> ApiResponse:
    agent: Agent = select_agent(id)
    if not agent:
        logger.error("Agent Not Found")
        raise HTTPException(status_code=404, detail=AGENT_NOT_FOUND)
    return ApiResponse(
        success=True,
        data=obj_to_model(agent,AgentResponse)
    )


@router.post("/update", status_code=200)
async def update(agent: AgentParams) -> ApiResponse:
    update_agent(agent)
    return ApiResponse(
        success=True,
    )


@router.post("/delete", status_code=200)
async def delete(id: str) -> ApiResponse:
    delete_agent(id)
    return ApiResponse(
        success=True,
    )


@router.get("/list", status_code=200)
async def list():
    return ApiResponse(
        success=True,
        data=objs_to_models(list_available_agents(),AgentResponse)
    )


@router.get("/list_reuse", status_code=200)
async def list_reuse():
    return ApiResponse(
        success=True,
        data=objs_to_models(list_reuse_agents(),AgentResponse)
    )


@router.post("/arun", status_code=200)
async def arun(
    params: AgentRunParams = Body(...),
) -> dict:
    compiled_engine = await compile_engine(
        params.chat_id,
        params.agent_data,
        params.agent_name
    )
    return await compiled_engine.ainvoke(params.state,compiled_engine.has_subgraphs)


@router.post("/arun_by_agent_id", status_code=200)
async def arun_by_agent_id(
    chat_id: str,
    agent_id: str,
    state: dict = Body(...),
) -> dict:
    agent: Agent = select_agent(agent_id)
    if not agent:
        logger.error("Agent Not Found")
        raise HTTPException(status_code=404, detail=AGENT_NOT_FOUND)
    try:
        agent_data = json.loads(agent.data)
    except json.JSONDecodeError as e:
        logger.error("Invalid agent data format: %s (Raw data: %s)", e, agent.data)
        raise HTTPException(status_code=400, detail=INVALID_AGENT_DATA) from e
    return await arun(
        params=AgentRunParams(
            chat_id=chat_id,
            agent_data=agent_data,
            state=state,
            agent_name=agent.name
        )
    )


async def compile_engine(
        chat_id: str,
        agent_data: dict,
        agent_name: str = None
) -> GraphEngine:
    from lang_agent.graph.callback import LoggerOutputCallback
    callbacks = [LoggerOutputCallback()]
    config = {
        "configurable": {"thread_id": chat_id},
        "recursion_limit": 50,
        "callbacks": callbacks
    }
    graph_engine = GraphEngine(
        agent_data = agent_data,
        config = config,
        agent_name = agent_name
    )
    try:
        await graph_engine.compile()
    except Exception as e:
        logger.error(f"{GRAPH_COMPILE_FAILED}: \n %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=GRAPH_COMPILE_FAILED) from e
    return graph_engine
