# Changelog

All notable changes to Cloud2Edge components are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## ci [1.0.0] — 2026-05-12

### Added
- Full path-filtered GitHub Actions pipeline (Rust, Python, Docker)
- Security scanning: cargo-audit, pip-audit, hadolint
- Per-component jobs: build, lint, test, audit
- README with architecture diagram, quickstart, AI client integration guide
- MIT LICENSE

---

## orchestrator [0.2.0] — 2026-05-11

### Added
- Agentic observe → decide → act loop with configurable poll interval
- Threshold evaluation for CPU temp, memory pressure, TCP retransmits
- MCP tool consumption via stdio client (spawns MCP server as subprocess)
- Calls `restart_service` on CPU/memory breach, `check_health` on network breach
- All config via environment variables (k3s ConfigMap compatible)
- 13 unit tests for decision logic

---

## deploy [0.1.0] — 2026-05-08

### Added
- Multi-stage Dockerfile for rust-agent (debian:bookworm-slim, ~32MB)
- Dockerfile for mcp-server (python:3.12-slim)
- k3s manifests: namespace, configmap, agent deployment, mcp-server deployment
- Agent pod mounts host /proc/edge_sensor via hostPath
- MCP server reads AGENT_URL from environment (ConfigMap in k3s)
- Resource limits sized for edge devices

---

## mcp-server [0.2.0] — 2026-05-08

### Added
- MCP server using FastMCP SDK (stdio transport)
- `get_telemetry` tool — queries rust-agent HTTP endpoint
- `check_health` tool — reports agent availability
- `restart_service(service_name)` tool — calls `systemctl restart`, real system calls
- All tools report honest errors, no simulated responses
- 10 protocol validation tests (pytest + pytest-asyncio)

---

## rust-agent [0.2.0] — 2026-05-07

### Added
- Telemetry struct with serde serialization
- `/proc/edge_sensor` parser (key=value format) with graceful error handling
- HTTP server (axum) on port 3000:
  - `GET /telemetry` — returns JSON or 503 if source unavailable
  - `GET /health` — returns 200 ok
- Modular structure: `telemetry.rs`, `server.rs`, `lib.rs`
- 5 unit tests (parsing) + 2 integration tests (HTTP endpoints)

---

## kernel-module [0.2.0] — 2026-05-07

### Added
- Out-of-tree kernel module build system (Makefile + kbuild)
- `/proc/edge_sensor` procfs interface with real telemetry:
  - CPU temperature via `thermal_zone_get_temp()` API
  - Memory pressure via `si_meminfo()`
  - TCP retransmit segments via `snmp_fold_field()`
- Returns `-1` for unavailable sources (no simulated fallbacks)
- Integration test script (`tests/test_edge_sensor.sh`) — 9 tests, 13 assertions
