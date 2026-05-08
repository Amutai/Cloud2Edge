import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

AGENT_URL = "http://localhost:3000"

mcp = FastMCP("edge-mcp-server")


@mcp.tool()
async def get_telemetry() -> str:
    """Get current edge device telemetry (CPU temp, memory pressure, TCP retransmits)."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{AGENT_URL}/telemetry", timeout=5.0)
            if resp.status_code == 200:
                return resp.text
            return f"agent returned {resp.status_code}: {resp.text}"
        except httpx.ConnectError:
            return "error: cannot reach rust-agent at localhost:3000"
        except httpx.TimeoutException:
            return "error: rust-agent request timed out"


@mcp.tool()
async def check_health() -> str:
    """Check if the edge agent is running and responsive."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{AGENT_URL}/health", timeout=5.0)
            if resp.status_code == 200:
                return f"healthy: agent responded '{resp.text}'"
            return f"unhealthy: agent returned {resp.status_code}"
        except httpx.ConnectError:
            return "unhealthy: cannot reach rust-agent at localhost:3000"
        except httpx.TimeoutException:
            return "unhealthy: rust-agent request timed out"


@mcp.tool()
async def restart_service(service_name: str) -> str:
    """Restart a systemd service on the edge device.

    Args:
        service_name: Name of the systemd service to restart (e.g., 'edge-agent', 'nginx').

    Production usage:
        Requires the MCP server process to have permission to run systemctl.
        Options:
          - Run MCP server as root (not recommended)
          - Add sudoers rule: mcp-user ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart *
          - Run as systemd service with CAP_SYS_ADMIN capability

    Returns:
        Success or failure message with stderr output if applicable.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            "systemctl", "restart", service_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)

        if proc.returncode == 0:
            return f"success: {service_name} restarted"
        else:
            err = stderr.decode().strip()
            return f"failed: systemctl returned {proc.returncode}: {err}"
    except FileNotFoundError:
        return "error: systemctl not found (not a systemd system?)"
    except PermissionError:
        return "error: permission denied — see tool docstring for setup"
    except asyncio.TimeoutError:
        return f"error: restart of {service_name} timed out after 30s"


if __name__ == "__main__":
    mcp.run()
