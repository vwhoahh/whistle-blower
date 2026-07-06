# WhistleBlower
**Track:** Concierge Agents  
**One-liner:** An autonomous multi-agent system that hunts stale OAuth permissions, scores their risk, and revokes them — only with your explicit approval.

---

## Demo

### 🌐 Cybersecurity Dashboard (PRIMARY DEMO)
Launch the FastAPI server and open the interactive dashboard:
```bash
uv run python -m app.fast_api_app
# OR
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
```
Then open: **http://localhost:8000/dashboard**

The dashboard has two modes:
- **Story Playback** — 11 cinematic scenes stepping through a full OAuth hijacking mitigation workflow (no API key needed for demo)
- **Live AI Agent** — auto-activates when the backend is reachable; fires real agent sessions, streams SSE events, updates the graph and chat in real-time, and requires human approval before executing any revocation

### 🖥️ ADK Playground (Alternative)
```bash
make playground
# OR (Windows)
uv run adk web app --host 127.0.0.1 --port 18081 --reload_agents
```
Opens the ADK chat UI at **http://localhost:18081**. Type `Audit my apps` to run the full workflow.

### 📄 Full Session Capture
See `demo_output.md` for a complete captured session showing all agent reasoning steps, MCP tool calls, and risk scores.

### What the Demo Shows
- 15 varied apps scanned (4 High, 4 Medium, 4 Low, 2 First-Party, 1 Edge Case)
- Risk reasoning over scope risk + inactivity via `get_app_details`
- `RequestInput` gate requiring explicit yes/no before any revocation
- Post-revocation scan confirming 11 apps remain (4 revoked, ~27% attack surface reduction)
- Audit log confirming every action is traceable
- Dashboard graph nodes update in real-time from live backend data

---

## Problem Statement
Every user accumulates dozens of forgotten OAuth-connected apps over years. These hold permissions to Gmail, Drive, Calendar long after the app is abandoned. WhistleBlower audits this invisible attack surface autonomously and helps users clean it up safely.

---

## The 4 Concepts

### ADK Multi-Agent
- 3 agents: `orchestrator_agent`, `risk_analyst_agent`, `remediation_planner_agent`
- Delegation chain: `orchestrator_agent` delegates specialized analysis and planning using `AgentTool`
- Code pointer: [app/agent.py](app/agent.py#L98-L154) → agent definitions

### MCP Server
- `app/mcp_server.py` — FastMCP server with 8 tools:
  - `scan_oauth_apps` — Returns active applications with metadata
  - `revoke_app_access` — Revokes an application by its ID
  - `get_revocation_status` — Verifies connection or revocation state
  - `get_app_details` — Returns granular app details and overall scope risk
  - `save_scan_result` — Logs metrics and plan summary to history
  - `get_scan_diff` — Computes high-risk app delta between consecutive scans
  - `reset_demo_state` — Restores initial state for all mock apps
  - `get_audit_log` — Returns history trail from audit_log.json
- Code pointer: [app/agent.py](app/agent.py#L87-L95) (McpToolset with StdioConnectionParams)

### Security
- `FunctionNode` security_checkpoint runs before any agent sees input
- PII scrubbing (email/phone regex) and prompt injection detection on user inputs
- Human-in-the-loop: `RequestInput` gate pauses execution before ANY revocation
- Audit trail: every transaction and validation event is logged to `audit_log.json`
- Code pointer: [app/agent.py](app/agent.py#L157-L193)

### Agents CLI
- Run with: `adk run app`
- Code pointer: [agents-cli-manifest.yaml](agents-cli-manifest.yaml)

---

## Architecture

```
User
 │
 ├── http://localhost:8000/dashboard   ← Premium cybersecurity dashboard (Story + Live AI mode)
 │       │
 │       ├── GET  /api/apps            ← MCP scan_oauth_apps()
 │       ├── GET  /api/app-details/id  ← MCP get_app_details()
 │       ├── GET  /api/audit-log       ← MCP get_audit_log()
 │       ├── POST /api/revoke/id       ← MCP revoke_app_access()
 │       ├── POST /api/reset           ← MCP reset_demo_state()
 │       └── POST /run_sse (SSE)       ← Full agent execution stream
 │
 └── http://localhost:18081            ← ADK Playground (chat UI)

Agent Execution Flow:
START → security_checkpoint → [safe] orchestrator_node
      → orchestrator_agent (scan + delegate)
      → risk_analyst_agent (score)
      → remediation_planner_agent (REVOKE/KEEP)
      → RequestInput (human gate)
      → revocation execution
      → audit log
      [unsafe] → security_violation_handler
```

## Design Decisions
- **3 agents:** separation of concerns — scanning, reasoning, and planning are distinct tasks
- **`RequestInput` gate:** a concierge agent touching security must never act without explicit user consent
- **Pydantic output schemas:** structured outputs make agent decisions deterministic and testable
- **Audit log:** every action must be traceable — this is a security tool
- **Dual-mode dashboard:** Story mode for instant hackathon demo; Live mode for real agent execution

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/dashboard` | GET | Serves the premium cybersecurity dashboard |
| `/api/apps` | GET | Live list of connected OAuth apps |
| `/api/app-details/{id}` | GET | Scope risk profile for a specific app |
| `/api/revoke/{id}` | POST | Execute access revocation |
| `/api/audit-log` | GET | Live audit trail from `audit_log.json` |
| `/api/reset` | POST | Reset all app state for demo |
| `/run_sse` | POST | SSE stream — full agent execution |

---

## Evaluation

### Unit Tests
7 deterministic pytest tests covering MCP tool correctness.
```bash
uv run pytest tests/unit/ -v
```

### LLM-as-Judge Eval
A Claude judge model (claude-haiku-4-5) scores WhistleBlower's risk reasoning output across 6 cases on 3 criteria:
- **Correctness:** Did the agent identify the right risk level?
- **Completeness:** Did it explain WHY (scopes + inactivity)?
- **Clarity:** Is the explanation non-technical-user friendly?

```bash
ANTHROPIC_API_KEY=your_key python tests/eval/run_judge_eval.py
```
Sample result: Average 8.2/10, 6/6 keyword match (see `judge_results.json.example`)

### Eval Dataset
10 behaviour-driven eval cases in `tests/eval/datasets/basic-dataset.json` covering:
full audit, injection blocking, PII redaction, first-party app handling, cancellation, and risk explanation.

---

## Limitations & Roadmap
- Dashboard auto-activates Live AI Agent mode when backend is reachable; falls back to Story mode otherwise
- Demo uses mock OAuth data; live mode requires Google OAuth consent flow (roadmap)
- Browser extension scanning not yet supported (roadmap)
- Cross-user data isolation needed for multi-user deployment (roadmap)
