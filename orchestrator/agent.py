"""Cloud2Edge Orchestrator — Agentic observe-decide-act loop.

Monitors edge device telemetry and takes corrective action
when thresholds are exceeded.

Environment variables (from ConfigMap in k3s):
    AGENT_URL: Rust agent HTTP endpoint (default: http://localhost:3000)
    CPU_TEMP_THRESHOLD: Max CPU temp in °C before action (default: 80)
    MEM_PRESSURE_THRESHOLD: Max memory pressure % before action (default: 90)
    TCP_RETRANS_THRESHOLD: Max TCP retransmits before action (default: 50000)
"""

import asyncio
import json
import os
import logging

import httpx

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


def decide(telemetry: dict) -> list[str]:
    """Evaluate telemetry against thresholds. Returns list of actions to take."""
    actions = []

    cpu = telemetry.get("cpu_temp_c", -1)
    mem = telemetry.get("mem_pressure_pct", -1)
    tcp = telemetry.get("tcp_retrans_segs", -1)

    if cpu >= CPU_TEMP_THRESHOLD and cpu != -1:
        actions.append(f"cpu_temp={cpu}°C exceeds threshold {CPU_TEMP_THRESHOLD}°C")

    if mem >= MEM_PRESSURE_THRESHOLD and mem != -1:
        actions.append(f"mem_pressure={mem}% exceeds threshold {MEM_PRESSURE_THRESHOLD}%")

    if tcp >= TCP_RETRANS_THRESHOLD and tcp != -1:
        actions.append(f"tcp_retrans={tcp} exceeds threshold {TCP_RETRANS_THRESHOLD}")

    return actions


async def act(actions: list[str]):
    """Log actions. In production, this calls MCP tools (issue #16)."""
    for action in actions:
        log.warning("ACTION NEEDED: %s", action)


async def run_loop():
    """Main agentic loop: observe → decide → act, repeat."""
    log.info("orchestrator starting")
    log.info("thresholds: cpu=%d°C, mem=%d%%, tcp=%d", 
             CPU_TEMP_THRESHOLD, MEM_PRESSURE_THRESHOLD, TCP_RETRANS_THRESHOLD)
    log.info("polling agent at %s every %ds", AGENT_URL, POLL_INTERVAL)

    async with httpx.AsyncClient() as client:
        while True:
            telemetry = await observe(client)

            if telemetry:
                log.info("telemetry: %s", json.dumps(telemetry))
                actions = decide(telemetry)

                if actions:
                    await act(actions)
                else:
                    log.info("all metrics within thresholds")
            else:
                log.warning("no telemetry available, skipping cycle")

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run_loop())
