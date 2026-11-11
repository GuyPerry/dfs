"""Unit tests for cost center MCP tools via mock data."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


AGENT_ROOT = Path(__file__).parent.parent


def load_mock_tool(server_slug: str, tool_name: str):
    """Load a tool definition from mcp-mock.json."""
    mock_path = AGENT_ROOT / "mcp-mock.json"
    data = json.loads(mock_path.read_text())
    return data["servers"][server_slug]["tools"][tool_name]


# ---------------------------------------------------------------------------
# Test: Cost Center master data tool (REQ-01)
# ---------------------------------------------------------------------------

class TestCostCenterMasterDataTool:
    """Tests for cost center master data retrieval."""

    def test_mock_response_list_costcenters_has_results(self):
        """list_a_costcenter_2_for_sap_self returns a list with results."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenter-0001",
            "list_a_costcenter_2_for_sap_self",
        )
        response = tool["mock_response"]
        assert "d" in response
        assert "results" in response["d"]
        results = response["d"]["results"]
        assert len(results) >= 1
        # Each result should have key fields
        first = results[0]
        assert "CostCenter" in first
        assert "ControllingArea" in first
        assert "CostCenterName" in first

    def test_mock_response_get_single_costcenter(self):
        """get_a_costcenter_2_for_sap_self returns a single cost center entity."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenter-0001",
            "get_a_costcenter_2_for_sap_self",
        )
        response = tool["mock_response"]
        assert "d" in response
        entity = response["d"]
        assert "CostCenter" in entity
        assert "ControllingArea" in entity
        assert "CostCenterName" in entity
        assert "CostCenterResponsibleUser" in entity

    def test_input_schema_get_costcenter_requires_keys(self):
        """get_a_costcenter_2_for_sap_self requires key parameters."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenter-0001",
            "get_a_costcenter_2_for_sap_self",
        )
        required = tool["input_schema"]["required"]
        assert "ControllingArea" in required
        assert "CostCenter" in required

    def test_mock_response_count_costcenters(self):
        """count_a_costcenter_2_for_sap_self returns a numeric count."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenter-0001",
            "count_a_costcenter_2_for_sap_self",
        )
        assert isinstance(tool["mock_response"], int)
        assert tool["mock_response"] >= 0


# ---------------------------------------------------------------------------
# Test: Cost Center Hierarchy tool (REQ-02)
# ---------------------------------------------------------------------------

class TestCostCenterHierarchyTool:
    """Tests for cost center hierarchy retrieval."""

    def test_mock_response_list_hierarchy_has_results(self):
        """list_costcenterhierarchy_for_sap_self returns hierarchy list."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenterhierarchy-0001",
            "list_costcenterhierarchy_for_sap_self",
        )
        response = tool["mock_response"]
        assert "d" in response
        results = response["d"]["results"]
        assert len(results) >= 1
        assert "CostCenterHierarchy" in results[0]

    def test_mock_response_list_hierarchy_nodes(self):
        """list_costcenterhierarchynode_for_sap_self returns nodes with CostCenter assignments."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenterhierarchy-0001",
            "list_costcenterhierarchynode_for_sap_self",
        )
        results = tool["mock_response"]["d"]["results"]
        assert len(results) >= 1
        node = results[0]
        assert "HierarchyNode" in node
        assert "CostCenter" in node

    def test_mock_response_navigate_hierarchy_nodes(self):
        """list_costcenterhierarchy__costctrhierarchynode returns nodes via navigation."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenterhierarchy-0001",
            "list_costcenterhierarchy__costctrhierarchynode_for_sap_self",
        )
        results = tool["mock_response"]["d"]["results"]
        assert len(results) >= 1
        assert "CostCenter" in results[0]

    def test_input_schema_get_hierarchy_requires_keys(self):
        """get_costcenterhierarchy_for_sap_self requires controlling area and hierarchy."""
        tool = load_mock_tool(
            "sap-s4-ce-costcenterhierarchy-0001",
            "get_costcenterhierarchy_for_sap_self",
        )
        required = tool["input_schema"]["required"]
        assert "ControllingArea" in required
        assert "CostCenterHierarchy" in required


# ---------------------------------------------------------------------------
# Test: Cost Rate tool (REQ-03)
# ---------------------------------------------------------------------------

class TestCostRateTool:
    """Tests for cost rate retrieval."""

    def test_mock_response_list_actual_cost_rates(self):
        """list_actualcostrate_for_sap_self returns actual cost rates."""
        tool = load_mock_tool(
            "sap-s4-ce-costrate-0001",
            "list_actualcostrate_for_sap_self",
        )
        results = tool["mock_response"]["d"]["results"]
        assert len(results) >= 1
        rate = results[0]
        assert "CostCenter" in rate
        assert "ActivityType" in rate
        assert "CostRate" in rate
        assert "Currency" in rate

    def test_mock_response_get_single_actual_cost_rate(self):
        """get_actualcostrate_for_sap_self returns single cost rate entity."""
        tool = load_mock_tool(
            "sap-s4-ce-costrate-0001",
            "get_actualcostrate_for_sap_self",
        )
        entity = tool["mock_response"]["d"]
        assert "CostCenter" in entity
        assert "ActivityType" in entity
        assert "CostRate" in entity

    def test_input_schema_get_costrate_requires_keys(self):
        """get_actualcostrate_for_sap_self requires all key parameters."""
        tool = load_mock_tool(
            "sap-s4-ce-costrate-0001",
            "get_actualcostrate_for_sap_self",
        )
        required = tool["input_schema"]["required"]
        assert "ControllingArea" in required
        assert "CostCenter" in required
        assert "ActivityType" in required
        assert "FiscalYear" in required

    def test_mock_response_list_plan_cost_rates(self):
        """list_plancostrate_for_sap_self returns plan cost rates."""
        tool = load_mock_tool(
            "sap-s4-ce-costrate-0001",
            "list_plancostrate_for_sap_self",
        )
        results = tool["mock_response"]["d"]["results"]
        assert len(results) >= 1
        assert "PlanCostRate" in results[0]

    def test_cost_rate_value_is_string_decimal(self):
        """Cost rate values should be string decimals per SAP OData patterns."""
        tool = load_mock_tool(
            "sap-s4-ce-costrate-0001",
            "get_actualcostrate_for_sap_self",
        )
        cost_rate = tool["mock_response"]["d"]["CostRate"]
        assert isinstance(cost_rate, str)
        float(cost_rate)  # should be parseable as float
