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


if __name__ == "__main__":
    mcp.run()
