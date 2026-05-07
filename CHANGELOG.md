# Changelog

All notable changes to Cloud2Edge components are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### rust-agent

### mcp-server

### orchestrator

### deploy

### ci

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
