# Cloud2Edge — Project Specification

## Overview
Agentic AI-powered cloud-to-edge infrastructure platform. Demonstrates low-level systems programming (C kernel module, Rust agent), containerized edge deployment (Docker/k3s), MCP integration, and DevSecOps CI/CD — built entirely with AI-assisted development (Amazon Q Developer).

## Target: Software development engineering with AI agentic workflow
Hits these keywords: C/Rust/Python, Kubernetes, edge systems, MCP/agentic AI, CI/CD, security, networking, containerization.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Cloud / Control Plane              │
│  ┌─────────────────┐    ┌────────────────────────┐  │
│  │ MCP Server      │ ◄──│  Python Orchestrator   │  │
│  │(Python/FastAPI) │    │  (agentic decision     │  │
│  │exposes tools    │    │   engine)              │  │
│  └────────┬────────┘    └────────────────────────┘  │
│           │MCP protocol (JSON-RPC over stdio/SSE)   │
└───────────┼─────────────────────────────────────────┘
            │
┌───────────┼──────────────────────────────────────────┐
│  Edge Node│(k3s pod / ARM device)                    │
│  ┌────────▼─────────┐    ┌────────────────────────┐  │
│  │ Rust Agent       │ ◄──│  C Kernel Module       │  │
│  │ (telemetry       │    │  (edge_sensor.ko)      │  │
│  │  collector +     │    │  sysfs/procfs/chardev  │  │
│  │  MCP client)     │    │  thermal/load/network  │  │
│  └──────────────────┘    └────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
Cloud2Edge/
├── kernel-module/
│   ├── src/
│   │   └── edge_sensor.c        # Kernel module: exposes system telemetry via procfs
│   ├── tests/
│   │   └── test_edge_sensor.sh  # Basic load/unload and read tests
│   ├── Makefile                 # Out-of-tree kernel build
│   └── VERSION                  # Component semver (0.1.0)
├── rust-agent/
│   ├── src/
│   │   └── main.rs             # Reads kernel telemetry, serves as MCP client
│   ├── Cargo.toml
│   └── VERSION
├── mcp-server/
│   ├── src/
│   │   └── server.py           # MCP server exposing edge tools (get_telemetry, deploy, restart)
│   ├── requirements.txt
│   └── VERSION
├── orchestrator/
│   ├── agent.py                # Agentic decision engine consuming MCP tools
│   ├── requirements.txt
│   └── VERSION
├── deploy/
│   ├── docker/
│   │   ├── Dockerfile.agent    # Rust agent container
│   │   └── Dockerfile.mcp      # MCP server container
│   └── k3s/
│       ├── namespace.yaml
│       ├── agent-deployment.yaml
│       ├── mcp-deployment.yaml
│       └── configmap.yaml
├── scripts/
│   ├── setup-k3s.sh            # Bootstrap k3s on edge node
│   └── deploy.sh               # Full deploy script
├── .github/
│   ├── workflows/
│   │   └── ci.yaml             # Build, lint, test pipeline
│   ├── ISSUE_TEMPLATE/
│   │   ├── feature.md           # Feature issue template
│   │   └── bug.md              # Bug report template
│   └── PULL_REQUEST_TEMPLATE.md
├── .gitignore
├── ARCHITECTURE.md              # System design & layered mental model
├── CHANGELOG.md                 # Per-component changelog
├── CONTRIBUTING.md              # Dev workflow, branching, versioning, CI/CD
├── README.md                    # Project overview with architecture diagram (milestone 6)
├── LICENSE                      # (milestone 6)
└── SPEC.md                      # This file
```

---

## Component Details

### 1. Kernel Module (C)
- Exposes simulated edge sensor data via `/proc/edge_sensor`
- Reports: CPU temp, memory pressure, network latency (simulated or real)
- Loadable/unloadable, out-of-tree build with Makefile
- Tests: load/unload, read validation, error handling

### 2. Rust Agent
- Reads from `/proc/edge_sensor` (or fallback to `/proc/stat`, `/proc/meminfo`)
- Periodically collects telemetry, formats as JSON
- Exposes HTTP endpoint for MCP server to query
- Minimal dependencies: tokio, serde, axum

### 3. MCP Server (Python)
- Implements Model Context Protocol (JSON-RPC)
- Tools exposed: `get_telemetry`, `restart_service`, `check_health`, `deploy_update`
- FastAPI + mcp SDK or manual JSON-RPC implementation
- Can be consumed by any MCP-compatible client (Claude, Q, custom)

### 4. Orchestrator (Python)
- Agentic loop: observe → decide → act
- Consumes MCP tools to monitor edge health and take action
- Example: if CPU temp > threshold → trigger restart via MCP tool
- Demonstrates spec-driven development pattern

### 5. Deployment
- Docker multi-stage builds for Rust agent and MCP server
- k3s manifests for edge deployment (lightweight Kubernetes)
- ConfigMap for thresholds and agent config
- Namespace isolation

### 6. CI/CD
- GitHub Actions: build kernel module (containerized), cargo build+clippy+test, Python lint+test
- Security: cargo-audit, pip-audit, hadolint for Dockerfiles

---

## Build Order
0. Project scaffolding — git init, workflow docs, templates, versioning, skeleton CI ✅
1. Kernel module (C) — get procfs interface working
2. Rust agent — read telemetry, serve HTTP
3. MCP server — expose tools
4. Docker containers — package agent + server
5. k3s manifests — deploy to edge cluster
6. Orchestrator — agentic decision loop
7. CI/CD pipeline — tie it all together
8. README with architecture diagram + LICENSE

---

## How to Use This Spec
Tell Amazon Q:
> "Read SPEC.md and start building from step 1 of the build order."

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow, branching, versioning, and CI/CD strategy.
