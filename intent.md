# Finance Cost Center Query Agent

Demo AI agent for Finance / Cost Center queries

## Business challenge

Finance teams spend significant time answering routine questions about cost centers — such as budget vs. actuals, cost center details, and hierarchy lookups — by manually navigating SAP S/4HANA. An AI agent can answer these questions instantly in natural language, reducing response time and enabling self-service for finance users.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to answer cost center queries | ~10 min (manual lookup) | < 1 min | Demo | Financial Master Data Management | agent-derived |
| Finance team self-service rate | Low | High | Demo | Financial Analytics | agent-derived |

## Key Milestones

1. **Agent responds to cost center lookup queries** — user can ask "What is cost center 1000?" and receive structured details.
2. **Budget vs. actuals queries answered** — agent retrieves and compares planned vs. actual costs for a given cost center.
3. **Cost center hierarchy navigation** — agent can traverse the cost center hierarchy and answer org-level questions.
4. **Natural language interface live** — agent deployed and accessible via A2A protocol for end-user testing.
5. **Demo validated** — agent correctly answers at least 5 representative finance queries end-to-end.
fdfd
## Business Architecture (RBA)

### End-to-End Process

Finance — Record to Report (generic)

### Process Hierarchy

```
Finance (E2E)
└── Record to Report (generic)
    └── Perform accounting and financial close (generic) (BPS-413)
        └── Perform financial reporting
```

### Summary

The agent maps to the Record to Report process, specifically financial reporting and master data management at the cost center level within SAP S/4HANA.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Read cost center master data | SAP S/4HANA Cost Center API | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | — | — | — | — | No | OData API available; no pre-built MCP server found |
| Read cost center hierarchy | SAP S/4HANA Cost Center Hierarchy API | `sap.s4:apiResource:CE_COSTCENTERHIERARCHY_0001:v1` | — | — | — | — | No | OData API available |
| Read cost rates | SAP S/4HANA Cost Rate API | `sap.s4:apiResource:CE_COSTRATE_0001:v1` | — | — | — | — | No | OData API available |
| Financial reporting / analytics | SAP S/4HANA, SAP Analytics Cloud | — | — | — | — | — | Maybe | Financial Analytics capability present in S/4HANA; detailed actuals may require additional API access |
| Natural language agent interface | Custom Python A2A agent | — | — | — | — | — | Yes | No standard SAP agent for cost center Q&A; custom development required |

### Key findings

- SAP S/4HANA provides OData APIs for cost center master data, hierarchy, and cost rates — these are the primary data sources.
- No pre-built MCP servers were found for cost center APIs; a custom MCP translation layer will be needed.
- The agent will be built as a pro-code Python A2A agent consuming the OData APIs via MCP tools.
- Financial Analytics capability is available in S/4HANA but detailed actuals queries may require scoping during specification.
- This is a demo scenario — the agent will focus on read-only queries (no write operations).

## Recommendations

### Finance Cost Center Query AI Agent

#### Executive Summary

Python A2A agent for natural language cost center queries via S/4HANA APIs.

#### Recommended Solution

Build a pro-code Python AI agent using the A2A protocol. The agent will connect to SAP S/4HANA via OData APIs (Cost Center, Cost Center Hierarchy, Cost Rate) to answer natural language questions about cost centers, budgets, and actuals. An MCP translation file will expose these APIs as agent tools.

#### Recommended solution category

AI Agent

#### Intent fit
85%
