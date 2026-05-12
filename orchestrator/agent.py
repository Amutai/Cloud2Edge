"""Cloud2Edge Orchestrator — Agentic observe-decide-act loop.

Monitors edge device telemetry and takes corrective action
when thresholds are exceeded. Calls MCP tools for actions.

Environment variables (from ConfigMap in k3s):
    AGENT_URL: Rust agent HTTP endpoint (default: http://localhost:3000)
    CPU_TEMP_THRESHOLD: Max CPU temp in °C before action (default: 80)
    MEM_PRESSURE_THRESHOLD: Max memory pressure % before action (default: 90)
    TCP_RETRANS_THRESHOLD: Max TCP retransmits before action (default: 50000)
    MCP_SERVER_PATH: Path to MCP server script (default: ../mcp-server/src/server.py)
    RESTART_TARGET: Service to restart on threshold breach (default: edge-agent)
"""

import asyncio
import json
import os
import logging
import sys

import httpx
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("orchestrator")

AGENT_URL = os.environ.get("AGENT_URL", "http://localhost:3000")
CPU_TEMP_THRESHOLD = int(os.environ.get("CPU_TEMP_THRESHOLD", "80"))
MEM_PRESSURE_THRESHOLD = int(os.environ.get("MEM_PRESSURE_THRESHOLD", "90"))
TCP_RETRANS_THRESHOLD = int(os.environ.get("TCP_RETRANS_THRESHOLD", "50000"))
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "10"))
MCP_SERVER_PATH = os.environ.get("MCP_SERVER_PATH", "../mcp-server/src/server.py")
RESTART_TARGET = os.environ.get("RESTART_TARGET", "edge-agent")


async def observe(client: httpx.AsyncClient) -> dict | None:
    """Fetch telemetry from the rust-agent."""
    try:
        resp = await client.get(f"{AGENT_URL}/telemetry", timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
        log.warning("agent returned %d: %s", resp.status_code, resp.text)
        return None
    except httpx.ConnectError:
        log.error("cannot reach agent at %s", AGENT_URL)
        return None
    except httpx.TimeoutException:
        log.error("agent request timed out")
        return None


def decide(telemetry: dict) -> list[dict]:
    """Evaluate telemetry against thresholds. Returns list of actions to take."""
    actions = []

    cpu = telemetry.get("cpu_temp_c", -1)
    mem = telemetry.get("mem_pressure_pct", -1)
    tcp = telemetry.get("tcp_retrans_segs", -1)

    if cpu >= CPU_TEMP_THRESHOLD and cpu != -1:
        actions.append({
            "reason": f"cpu_temp={cpu}°C exceeds threshold {CPU_TEMP_THRESHOLD}°C",
            "tool": "restart_service",
            "args": {"service_name": RESTART_TARGET},
        })

    if mem >= MEM_PRESSURE_THRESHOLD and mem != -1:
        actions.append({
            "reason": f"mem_pressure={mem}% exceeds threshold {MEM_PRESSURE_THRESHOLD}%",
            "tool": "restart_service",
            "args": {"service_name": RESTART_TARGET},
        })

    if tcp >= TCP_RETRANS_THRESHOLD and tcp != -1:
        actions.append({
            "reason": f"tcp_retrans={tcp} exceeds threshold {TCP_RETRANS_THRESHOLD}",
            "tool": "check_health",
            "args": {},
        })

    return actions


async def act(session: ClientSession, actions: list[dict]):
    """Execute actions by calling MCP tools."""
    for action in actions:
        log.warning("ACTION: %s", action["reason"])
        try:
            result = await session.call_tool(action["tool"], action["args"])
            log.info("MCP tool '%s' result: %s", action["tool"], result.content[0].text)
        except Exception as e:
            log.error("MCP tool '%s' failed: %s", action["tool"], e)


async def run_loop():
    """Main agentic loop: observe → decide → act, repeat."""
    log.info("orchestrator starting")
    log.info("thresholds: cpu=%d°C, mem=%d%%, tcp=%d",
             CPU_TEMP_THRESHOLD, MEM_PRESSURE_THRESHOLD, TCP_RETRANS_THRESHOLD)
    log.info("polling agent at %s every %ds", AGENT_URL, POLL_INTERVAL)
    log.info("MCP server: %s", MCP_SERVER_PATH)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[MCP_SERVER_PATH],
        env={**os.environ, "AGENT_URL": AGENT_URL},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            log.info("MCP tools available: %s", [t.name for t in tools.tools])

            async with httpx.AsyncClient() as client:
                while True:
                    telemetry = await observe(client)

                    if telemetry:
                        log.info("telemetry: %s", json.dumps(telemetry))
                        actions = decide(telemetry)

                        if actions:
                            await act(session, actions)
                        else:
                            log.info("all metrics within thresholds")
                    else:
                        log.warning("no telemetry available, skipping cycle")

                    await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run_loop())
