# cloud2edge — Architecture & System Design

## What It Does

A closed-loop autonomous edge management system. A kernel module on an edge device collects hardware telemetry, a Rust agent reads and serves it, an MCP server exposes it as callable tools, and a Python orchestrator makes agentic decisions (observe → decide → act) — all deployed via containers on lightweight k8s (k3s).

**In short: edge infrastructure that can monitor and heal itself through AI-driven tooling.**

---

## System Design — Layered Mental Model

```
Layer 4: BRAIN           — Orchestrator (Python) — agentic loop, makes decisions
              ↕ MCP protocol (JSON-RPC)
Layer 3: INTERFACE       — MCP Server (Python/FastAPI) — translates intent → actions
              ↕ HTTP/REST
Layer 2: NERVOUS SYSTEM  — Rust Agent — collects, aggregates, serves telemetry
              ↕ procfs read
Layer 1: BODY            — Kernel Module (C) — raw hardware/OS telemetry
```

Data flows up. Commands flow down. Each layer has a single responsibility and a clean contract with its neighbors. Any layer can be swapped independently.

The MCP layer is the key innovation — it makes the system **tool-callable by any AI agent**, not just our orchestrator.

---

## Why Each Component Exists

| Component | Why | JD Signal |
|-----------|-----|-----------|
| Kernel Module (C) | Ground-truth telemetry from the OS via procfs — the Linux-native way | Low-level C, kernel, hypervisor knowledge |
| Rust Agent | Safe, fast, zero-overhead bridge between kernel and network. C is too low-level for HTTP, Python too slow for tight polling | Rust, systems languages |
| MCP Server (Python) | Makes edge telemetry consumable by any AI tool — this is the agentic harness | MCP, agentic AI, spec-driven dev |
| Orchestrator (Python) | Proves the loop: observe → reason → act via MCP tools | AI-assisted practices, agentic harnesses |
| Docker + k3s | Edge devices can't run full k8s. k3s is production-grade lightweight orchestration | Kubernetes, containerization, edge |
| CI/CD | Automated build/test/lint across C, Rust, Python | CI/CD, cargo-audit, static analysis |

---

## Implementation Flow (Bottom-Up)

Each layer is testable in isolation before the next one depends on it.

1. **Kernel Module** — Foundation. Expose telemetry via `/proc/edge_sensor`. Test load/unload/read.
2. **Rust Agent** — Read procfs, serve JSON over HTTP. Test with `curl`.
3. **MCP Server** — Wrap agent API in MCP tools (`get_telemetry`, `restart_service`, etc.). Now any AI client can call them.
4. **Docker Containers** — Package agent + server. Multi-stage builds for small edge images.
5. **k3s Manifests** — Deploy containers. Runs on any edge node with k3s.
6. **Orchestrator** — The brain. Consumes MCP tools in an agentic loop. Last because it's easiest to iterate on and most demo-friendly.
7. **CI/CD** — Codify everything that's been working manually.

**Why bottom-up?** You never build on an unverified foundation. This is how you'd engineer a real edge system.

---

## The Interview Story

This project gives you a narrative at every level:

- **Low-level**: "I wrote a kernel module that exposes telemetry via procfs"
- **Systems**: "A Rust agent polls it and serves JSON over HTTP"
- **AI/Agentic**: "An MCP server makes it tool-callable by any AI agent"
- **DevOps**: "Deployed on k3s with Docker, CI/CD with GitHub Actions"
- **Architecture**: "Clean layered design, each component independently testable and swappable"
