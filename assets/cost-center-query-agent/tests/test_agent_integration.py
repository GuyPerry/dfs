"""Integration tests for the cost center query agent end-to-end flow."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import StructuredTool


AGENT_ROOT = Path(__file__).parent.parent


def _make_mock_tool(name: str, description: str, response: dict) -> StructuredTool:
    """Create a StructuredTool with a mock async function returning fixed data."""

    async def _fn(**kwargs):
        return json.dumps(response)

    return StructuredTool.from_function(
        coroutine=_fn,
        name=name,
        description=description,
        return_direct=False,
    )


def _load_mock_tools() -> list[StructuredTool]:
    """Build a minimal set of mock tools from mcp-mock.json."""
    mock_path = AGENT_ROOT / "mcp-mock.json"
    data = json.loads(mock_path.read_text())
    tools = []
    for _slug, server in data["servers"].items():
        for tool_name, tool_def in server["tools"].items():
            tools.append(
                _make_mock_tool(
                    name=tool_name,
                    description=tool_def["description"],
                    response=tool_def["mock_response"],
                )
            )
    return tools


# ---------------------------------------------------------------------------
# Integration: Agent invoke
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_agent_invoke_cost_center_query(add_agent_to_path):
    """Agent returns a completed response for a cost center lookup query."""
    from agent import SampleAgent

    mock_tools = _load_mock_tools()

    # Mock the LLM to return a canned response without calling AI Core
    mock_ai_message = AIMessage(content="Cost center CC-1000 is 'Corporate IT', responsible: JDOE, controlling area: A000.")
    mock_llm_response = {"messages": [mock_ai_message]}

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_llm_response
        response = await agent.invoke(
            query="What is cost center CC-1000?",
            context_id="test-context-001",
            tools=mock_tools,
        )

    assert response.status == "completed"
    assert response.message
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_invoke_hierarchy_query(add_agent_to_path):
    """Agent returns a completed response for a hierarchy query."""
    from agent import SampleAgent

    mock_tools = _load_mock_tools()

    mock_ai_message = AIMessage(content="Hierarchy HIER-001 'Main Hierarchy' contains nodes: NODE-001 (CC-1000), NODE-002 (CC-2000).")
    mock_llm_response = {"messages": [mock_ai_message]}

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_llm_response
        response = await agent.invoke(
            query="Which cost centers are in hierarchy group HIER-001?",
            context_id="test-context-002",
            tools=mock_tools,
        )

    assert response.status == "completed"
    assert response.message


@pytest.mark.asyncio
async def test_agent_invoke_cost_rate_query(add_agent_to_path):
    """Agent returns a completed response for a cost rate query."""
    from agent import SampleAgent

    mock_tools = _load_mock_tools()

    mock_ai_message = AIMessage(content="The actual cost rate for CC-1000, activity type LAB, fiscal year 2026 is 125.00 USD.")
    mock_llm_response = {"messages": [mock_ai_message]}

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_llm_response
        response = await agent.invoke(
            query="What is the cost rate for cost center CC-1000 activity type LAB?",
            context_id="test-context-003",
            tools=mock_tools,
        )

    assert response.status == "completed"
    assert response.message


@pytest.mark.asyncio
async def test_agent_stream_emits_processing_then_result(add_agent_to_path):
    """Agent stream() yields a 'Processing...' chunk then a completed result."""
    from agent import SampleAgent

    mock_tools = _load_mock_tools()
    mock_ai_message = AIMessage(content="Cost center CC-2000 is Finance Department.")
    mock_llm_response = {"messages": [mock_ai_message]}

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_llm_response
        chunks = []
        async for chunk in agent.stream(
            query="Tell me about cost center CC-2000",
            context_id="test-context-004",
            tools=mock_tools,
        ):
            chunks.append(chunk)

    assert len(chunks) >= 2
    # First chunk should be a working status
    assert chunks[0]["is_task_complete"] is False
    # Last chunk should be completed
    assert chunks[-1]["is_task_complete"] is True
    assert chunks[-1]["content"]


@pytest.mark.asyncio
async def test_agent_handles_error_gracefully(add_agent_to_path):
    """Agent stream() yields an error message when execution fails."""
    from agent import SampleAgent

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.side_effect = RuntimeError("Simulated AI Core failure")
        chunks = []
        async for chunk in agent.stream(
            query="What is cost center 9999?",
            context_id="test-context-err",
            tools=[],
        ):
            chunks.append(chunk)

    last = chunks[-1]
    assert last["is_task_complete"] is True
    assert "error" in last["content"].lower() or "encountered" in last["content"].lower()


@pytest.mark.asyncio
async def test_system_prompt_contains_readonly_instruction(add_agent_to_path):
    """System prompt must explicitly prohibit write operations."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "READ-ONLY" in prompt or "never perform write" in prompt.lower() or "must never perform write" in prompt.lower()


@pytest.mark.asyncio
async def test_system_prompt_instructs_tool_use(add_agent_to_path):
    """System prompt must instruct agent to use tools for live data."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "MUST use tools" in prompt or "use tools to retrieve" in prompt.lower()


@pytest.mark.asyncio
async def test_agent_milestone_m1_logging(add_agent_to_path, caplog):
    """Milestone M1 is logged when a cost center master data query resolves."""
    import logging
    from agent import SampleAgent

    mock_tools = _load_mock_tools()
    mock_ai_message = AIMessage(content="Cost center CC-1000: Corporate IT.")
    mock_llm_response = {"messages": [mock_ai_message]}

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_llm_response
        with caplog.at_level(logging.INFO, logger="agent"):
            await agent._run_agent(
                query="What is cost center CC-1000?",
                context_id="test-context-m1",
                tools=mock_tools,
            )

    log_messages = " ".join(caplog.messages)
    assert "M1.achieved" in log_messages or "M4.achieved" in log_messages
