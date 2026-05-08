import asyncio
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.server import mcp, get_telemetry, check_health, restart_service


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestToolDiscovery:
    """Validate MCP tool registration and schemas."""

    @pytest.mark.asyncio
    async def test_all_tools_registered(self):
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        assert names == {"get_telemetry", "check_health", "restart_service"}

    @pytest.mark.asyncio
    async def test_get_telemetry_no_params(self):
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "get_telemetry")
        required = tool.inputSchema.get("required", [])
        assert required == []

    @pytest.mark.asyncio
    async def test_restart_service_requires_service_name(self):
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "restart_service")
        assert "service_name" in tool.inputSchema.get("required", [])
        assert tool.inputSchema["properties"]["service_name"]["type"] == "string"


class TestGetTelemetry:
    """Validate get_telemetry tool behavior."""

    @pytest.mark.asyncio
    async def test_returns_error_when_agent_down(self):
        result = await get_telemetry()
        assert "error" in result or "cannot reach" in result

    @pytest.mark.asyncio
    async def test_returns_string(self):
        result = await get_telemetry()
        assert isinstance(result, str)


class TestCheckHealth:
    """Validate check_health tool behavior."""

    @pytest.mark.asyncio
    async def test_reports_unhealthy_when_agent_down(self):
        result = await check_health()
        assert "unhealthy" in result

    @pytest.mark.asyncio
    async def test_returns_string(self):
        result = await check_health()
        assert isinstance(result, str)


class TestRestartService:
    """Validate restart_service tool behavior."""

    @pytest.mark.asyncio
    async def test_invalid_service_returns_failure(self):
        result = await restart_service("nonexistent-test-service-xyz")
        assert "failed" in result or "error" in result

    @pytest.mark.asyncio
    async def test_returns_string(self):
        result = await restart_service("nonexistent-test-service-xyz")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_empty_service_name(self):
        result = await restart_service("")
        assert "failed" in result or "error" in result
