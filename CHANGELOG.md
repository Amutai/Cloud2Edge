# Changelog

All notable changes to Cloud2Edge components are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### mcp-server

### orchestrator

### deploy

### ci

---

## rust-agent [0.2.0] — 2026-05-04

### Added
- Telemetry struct with serde serialization
- `/proc/edge_sensor` parser (key=value format) with graceful error handling
- HTTP server (axum) on port 3000:
  - `GET /telemetry` — returns JSON or 503 if source unavailable
  - `GET /health` — returns 200 ok
- Modular structure: `telemetry.rs`, `server.rs`, `lib.rs`
- 5 unit tests (parsing) + 2 integration tests (HTTP endpoints)

---

## kernel-module [0.2.0] — 2026-05-04

### Added
- Out-of-tree kernel module build system (Makefile + kbuild)
- `/proc/edge_sensor` procfs interface with real telemetry:
  - CPU temperature via `thermal_zone_get_temp()` API
  - Memory pressure via `si_meminfo()`
  - TCP retransmit segments via `snmp_fold_field()`
- Returns `-1` for unavailable sources (no simulated fallbacks)
- Integration test script (`tests/test_edge_sensor.sh`) — 9 tests, 13 assertions
