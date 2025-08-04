import asyncio
import os
import shutil
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest

from lang_agent.api.v1.request_params import AgentParams, ModelParams
from lang_agent.db.database import (
    create_agent,
    create_model,
    delete_agent,
    select_agent,
    select_model_by_name,
    update_agent,
)

# Force use of SelectorEventLoop to avoid ProactorEventLoop bug
selector_event_loop = asyncio.SelectorEventLoop()
asyncio.set_event_loop(selector_event_loop)


@pytest.fixture(scope="function")
def setup_test_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    db_url = f"sqlite:///{db_path}"

    from lang_agent.db.database import Database

    new_db = Database()

    import lang_agent.db.database as database_module

    original_db = database_module.db
    database_module.db = new_db

    new_db.configure(db_url)
    new_db.init_database()

    yield new_db.get_engine()

    database_module.db = original_db

    new_db.engine.dispose()
    shutil.rmtree(temp_dir)


resource_manager_mock = MagicMock()
resource_manager_mock.models = {"llm": {}, "embedding": {}}
resource_manager_mock.mcp_map = {}
resource_manager_mock.init_model.return_value = "mocked_model_instance"
resource_manager_mock.init_mcp = AsyncMock(return_value="mocked_mcp_instance")


def test_create_model(setup_test_db):
    model_id = create_model(
        ModelParams(name="test_model", type="llm", channel="openai", model_args="{}"),
        resource_manager_mock,
    )

    assert model_id is not None

    result = select_model_by_name("test_model")
    assert result is not None
    assert result.name == "test_model"

    with pytest.raises(ValueError):
        create_model(
            ModelParams(
                name="test_model", type="llm", channel="openai", model_args="{}"
            ),
            resource_manager_mock,
        )


# Test for Agent operations
def test_create_agent(setup_test_db):
    agent_id = "test_agent_123"
    agent_params = AgentParams(
        id=agent_id,
        name="TestAgent",
        description="A test agent",
        data={},
        reuse_flag=True,
        disabled=False,
    )
    # Create agent
    create_agent(agent_params)
    # Verify it's saved correctly
    result = select_agent(agent_id)
    assert result is not None
    assert result.name == "TestAgent"


def test_update_agent(setup_test_db):
    agent_id = "test_agent_456"
    initial_params = AgentParams(
        id=agent_id,
        name="InitialAgent",
        description="Initial description",
        data={},
        reuse_flag=False,
        disabled=False,
    )
    updated_params = AgentParams(
        id=agent_id,
        name="UpdatedAgent",
        description="Updated description",
        data={"new": "data"},
        reuse_flag=True,
        disabled=False,
    )
    # Create the agent first
    create_agent(initial_params)
    # Update the agent
    update_agent(updated_params)
    # Check if the update was successful
    result = select_agent(agent_id)
    assert result is not None
    assert result.name == "UpdatedAgent"
    assert result.description == "Updated description"
    assert result.data == '{"new": "data"}'
    assert result.reuse_flag == 1  # Boolean to int conversion
    assert result.disabled == 0


def test_delete_agent(setup_test_db):
    agent_id = "test_agent_789"
    agent_params = AgentParams(
        id=agent_id,
        name="ToDeleteAgent",
        description="Will be deleted",
        data={},
        reuse_flag=False,
        disabled=False,
    )
    # Create and then delete the agent
    create_agent(agent_params)
    delete_agent(agent_id)
    # Ensure it no longer exists
    result = select_agent(agent_id)
    assert result is None
