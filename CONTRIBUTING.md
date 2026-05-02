# Cloud2Edge — Contributing & Development Workflow

## Git Workflow: Issue-Driven GitHub Flow

All work is tracked through GitHub Issues, organized into Milestones that map to the build order. `main` is always deployable.

### Rules

- `main` is protected — no direct pushes
- All work goes through PRs linked to issues
- PRs require CI passing before merge
- Squash merge to keep history clean

### Branch Naming

```
<issue#>-<component>-<short-description>
```

Examples:
```
1-kernel-procfs-interface
5-rust-agent-http-server
12-mcp-server-tools
18-orchestrator-agentic-loop
```

---

## Conventional Commits

Every commit message follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

### Types

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `chore` | Maintenance, deps, config |
| `refactor` | Code change that neither fixes nor adds |
| `test` | Adding or updating tests |
| `ci` | CI/CD pipeline changes |

### Scopes

| Scope | Component |
|-------|-----------|
| `kernel` | kernel-module/ |
| `rust-agent` | rust-agent/ |
| `mcp` | mcp-server/ |
| `orchestrator` | orchestrator/ |
| `deploy` | deploy/ (Docker, k3s) |
| `ci` | .github/workflows/ |

### Examples

```
feat(kernel): add procfs temperature reading
fix(rust-agent): handle missing /proc/edge_sensor gracefully
feat(mcp): add restart_service tool
test(orchestrator): decision logic unit tests
ci: add cargo-audit step
docs: update architecture diagram
```

---

## Versioning

Each component is independently versioned using [Semantic Versioning](https://semver.org/). The single source of truth is a `VERSION` file in each component directory.

```
kernel-module/VERSION    → 0.1.0
rust-agent/VERSION       → 0.1.0
mcp-server/VERSION       → 0.1.0
orchestrator/VERSION     → 0.1.0
```

- **Major** (1.x.x): breaking change to the component's interface
- **Minor** (x.1.x): new feature, backward-compatible
- **Patch** (x.x.1): bug fix

Start at `0.1.0`. Bump to `1.0.0` when the component is production-ready.

### Git Tags

Tags are prefixed by component:

```
kernel-v0.1.0
agent-v0.1.0
mcp-v0.1.0
orch-v0.1.0
```

Full-system milestone releases use a meta-tag: `release-v0.1.0`

---

## Releases

- When a component hits a milestone → tag it → create a GitHub Release with changelog excerpt
- Release artifacts: Docker images tagged with version (e.g., `cloud2edge/rust-agent:0.2.0`)
- Milestone releases (all components working together) get the meta-tag

---

## Issue Milestones

Issues are grouped into milestones matching the bottom-up build order.

### Milestone 1: Foundation (kernel-module)

| # | Title |
|---|-------|
| 1 | `feat(kernel)`: scaffold Makefile and module skeleton |
| 2 | `feat(kernel)`: implement procfs telemetry interface |
| 3 | `test(kernel)`: load/unload and read validation tests |

### Milestone 2: Telemetry Agent (rust-agent)

| # | Title |
|---|-------|
| 4 | `feat(rust-agent)`: scaffold Cargo project |
| 5 | `feat(rust-agent)`: read /proc/edge_sensor |
| 6 | `feat(rust-agent)`: HTTP server with axum |
| 7 | `test(rust-agent)`: unit + integration tests |

### Milestone 3: MCP Interface (mcp-server)

| # | Title |
|---|-------|
| 8 | `feat(mcp)`: scaffold FastAPI project |
| 9 | `feat(mcp)`: implement get_telemetry tool |
| 10 | `feat(mcp)`: implement restart_service + check_health tools |
| 11 | `test(mcp)`: MCP protocol validation |

### Milestone 4: Containerization (deploy)

| # | Title |
|---|-------|
| 12 | `feat(deploy)`: Dockerfile for rust-agent |
| 13 | `feat(deploy)`: Dockerfile for mcp-server |
| 14 | `feat(deploy)`: k3s manifests |

### Milestone 5: Brain (orchestrator)

| # | Title |
|---|-------|
| 15 | `feat(orchestrator)`: agentic observe-decide-act loop |
| 16 | `feat(orchestrator)`: MCP tool consumption |
| 17 | `test(orchestrator)`: decision logic tests |

### Milestone 6: CI/CD & Polish

| # | Title |
|---|-------|
| 18 | `ci`: full path-filtered pipelines (enhance skeleton) |
| 19 | `ci`: security scanning (cargo-audit, pip-audit, hadolint) |
| 20 | `docs`: README with architecture diagram |

---

## CI/CD: Path-Filtered Pipelines

CI only builds what changed. Triggers are filtered by path:

| Changed Path | Pipeline |
|-------------|----------|
| `kernel-module/**` | Build + test kernel module |
| `rust-agent/**` | `cargo build` + `clippy` + `test` + `cargo-audit` |
| `mcp-server/**` | Python lint + test + `pip-audit` |
| `orchestrator/**` | Python lint + test |
| `deploy/docker/**` | `hadolint` + `docker build` |

A full integration test runs on `main` after merge.

---

## PR Workflow

1. Pick an issue from the current milestone
2. Create a branch: `<issue#>-<component>-<description>`
3. Implement with conventional commits
4. Open PR → link to issue
5. CI must pass
6. Squash merge into `main`
7. Delete the branch
