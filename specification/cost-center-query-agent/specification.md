# Specification: cost-center-query-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` for full context
- [x] Bootstrap agent code in `assets/cost-center-query-agent/` using the `sap-agent-bootstrap` skill (invoke from inside `assets/cost-center-query-agent/`, use copy commands)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skills are needed for this agent — all interactions are single tool calls (cost center lookup, hierarchy, cost rates). The system prompt is sufficient.

---

## Project-Specific Tasks

### System Prompt

- [x] Open `assets/cost-center-query-agent/app/agent.py` and add a system prompt (`@prompt_section`) that:
  - Instructs the agent to answer natural language questions about cost centers, cost center hierarchy, and cost rates using only MCP tools
  - Explicitly states: "You MUST use tools to retrieve live data. Never fabricate, guess, or invent data."
  - Instructs the agent to set page size parameters (`top`, `limit`, etc.) to a maximum of 100 on every paginated tool call
  - Instructs the agent to relay tool errors verbatim without embellishment
  - Instructs the agent that it is read-only: "You must never perform write, update, or delete operations on any SAP data."
  - Covers the three supported query types:
    1. Cost center master data lookup (name, responsible person, controlling area, validity)
    2. Cost center hierarchy navigation (list cost centers under a group/node)
    3. Cost rate retrieval by cost center and activity type

### Cost Center Master Data Query (REQ-01)

- [x] Wire the MCP tool for cost center master data so the agent can answer "What is cost center 1000?" and similar queries
- [x] Verify the agent returns: name, responsible person, controlling area, and validity dates for a given cost center ID
- [x] Handle the case where the cost center is not found: agent informs the user and requests clarification

### Cost Center Hierarchy Navigation (REQ-02)

- [x] Wire the MCP tool for cost center hierarchy so the agent can answer "Which cost centers are in group X?"
- [x] Verify the agent returns a structured list of cost centers under a given hierarchy node or group

### Cost Rate Query (REQ-03)

- [x] Wire the MCP tool for cost rates so the agent can answer "What is the cost rate for cost center 1000 and activity type LAB?"
- [x] Verify the agent returns the applicable cost rate for the given cost center and activity type

### Guardrails (REQ-05)

- [x] Confirm the system prompt explicitly prohibits any write operations
- [x] Confirm the agent does not attempt any create, update, or delete tool calls

---

## Data Dependencies

No data product ORD IDs — all data sourced directly from SAP S/4HANA OData APIs via MCP tools.

## API Integration

MCP API: `sap.s4:apiResource:CE_COSTCENTER_0001:v1`
MCP tool scope: read-only
Resources in scope: CostCenter, CostCenterText

MCP API: `sap.s4:apiResource:CE_COSTCENTERHIERARCHY_0001:v1`
MCP tool scope: read-only
Resources in scope: CostCenterHierarchy, CostCenterHierarchyNode

MCP API: `sap.s4:apiResource:CE_COSTRATE_0001:v1`
MCP tool scope: read-only
Resources in scope: CostRate

API spec files:
- `specification/cost-center-query-agent/api-specs/CE_COSTCENTER_0001.edmx`
- `specification/cost-center-query-agent/api-specs/CE_COSTCENTERHIERARCHY_0001.edmx`
- `specification/cost-center-query-agent/api-specs/CE_COSTRATE_0001.edmx`

---

## Business Instrumentation

- [x] Implement business step instrumentation for each milestone from the PRD using the pattern `[MILESTONE_ID].[achieved|missed]: [description]` and OpenTelemetry custom spans:
  - `M1`: cost center master data query resolved / did not complete
  - `M2`: cost rate query resolved / did not complete
  - `M3`: cost center hierarchy query resolved / did not complete
  - `M4`: agent deployed and responding to natural language queries / not functional
  - `M5`: demo validated — 5 queries answered correctly / incomplete or failed
- [x] Extract business logic from `stream()` into a plain async helper (e.g. `_run_agent()`) and instrument that method — never use `with tracer.start_as_current_span(...)` inside an async generator
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

- [x] Invoke `mcp-translation-file` skill for each of the three API spec files:
  - `specification/cost-center-query-agent/api-specs/CE_COSTCENTER_0001.edmx`
  - `specification/cost-center-query-agent/api-specs/CE_COSTCENTERHIERARCHY_0001.edmx`
  - `specification/cost-center-query-agent/api-specs/CE_COSTRATE_0001.edmx`
- [x] After `mcp-translation-file` completes, invoke `setup-solution` skill to create MCP server assets and register them
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — never import directly from `sap_cloud_sdk.agentgateway`
- [x] Extract ORD IDs from generated MCP server `asset.yaml` files and add to agent's `asset.yaml` under `requires`
- [x] After `mcp-translation-file` and `setup-solution` complete, generate `mcp-mock.json` using the `mcp-mock-config` skill

---

## Testing

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write unit tests in `assets/cost-center-query-agent/tests/` — one per MCP tool (cost center read, hierarchy read, cost rate read)
- [x] Write one integration test executing end-to-end agent flow with mocked LLM responses and mocked MCP tools
- [x] Run `pytest` from `assets/cost-center-query-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Run `pytest` again from `assets/cost-center-query-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/cost-center-query-agent/`
