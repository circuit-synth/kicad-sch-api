"""
Comprehensive tests for hierarchical schematic MCP tools.

Tests manage_sheets (add_pin, remove_pin actions) and manage_hierarchical_labels.
"""

import pytest
import pytest_asyncio
from mcp_server.tools.consolidated_tools import (
    manage_hierarchical_labels,
    manage_schematic,
    manage_sheets,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def schematic_with_sheet():
    """Create a schematic with a hierarchical sheet."""
    # Create parent schematic
    result = await manage_schematic(action="create", name="TestProject")
    assert result["success"] is True
    parent_uuid = result["uuid"]

    # Add hierarchical sheet
    sheet_result = await manage_sheets(
        action="add",
        name="TestSheet",
        filename="test_sheet.kicad_sch",
        position=(50.0, 50.0),
        size=(100.0, 100.0),
        project_name="TestProject",
    )
    assert sheet_result["success"] is True
    sheet_uuid = sheet_result["sheet_uuid"]

    return {
        "parent_uuid": parent_uuid,
        "sheet_uuid": sheet_uuid,
    }


@pytest_asyncio.fixture
async def child_schematic(schematic_with_sheet):
    """Create a child schematic with hierarchy context."""
    parent_uuid = schematic_with_sheet["parent_uuid"]
    sheet_uuid = schematic_with_sheet["sheet_uuid"]

    # Create child schematic
    result = await manage_schematic(action="create", name="TestProject")
    assert result["success"] is True

    # Set hierarchy context
    context_result = await manage_sheets(
        action="set_context",
        parent_uuid=parent_uuid,
        sheet_uuid=sheet_uuid,
    )
    assert context_result["success"] is True

    return {
        "parent_uuid": parent_uuid,
        "sheet_uuid": sheet_uuid,
    }


# ============================================================================
# Test manage_sheets with add_pin action
# ============================================================================


class TestManageSheetsAddPin:
    """Test manage_sheets with add_pin action."""

    @pytest.mark.asyncio
    async def test_add_pin_right_edge(self, schematic_with_sheet):
        """Test adding a pin on the right edge."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="VCC",
            pin_type="output",
            edge="right",
            position_along_edge=10.0,
        )

        assert result["success"] is True
        assert result["pin_name"] == "VCC"
        assert result["pin_type"] == "output"
        assert result["edge"] == "right"
        assert result["position_along_edge"] == 10.0
        assert "pin_uuid" in result

    @pytest.mark.asyncio
    async def test_add_pin_left_edge(self, schematic_with_sheet):
        """Test adding a pin on the left edge."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="GND",
            pin_type="input",
            edge="left",
            position_along_edge=20.0,
        )

        assert result["success"] is True
        assert result["edge"] == "left"

    @pytest.mark.asyncio
    async def test_add_pin_top_edge(self, schematic_with_sheet):
        """Test adding a pin on the top edge."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="CLK",
            pin_type="input",
            edge="top",
            position_along_edge=30.0,
        )

        assert result["success"] is True
        assert result["edge"] == "top"

    @pytest.mark.asyncio
    async def test_add_pin_bottom_edge(self, schematic_with_sheet):
        """Test adding a pin on the bottom edge."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="DATA",
            pin_type="bidirectional",
            edge="bottom",
            position_along_edge=40.0,
        )

        assert result["success"] is True
        assert result["edge"] == "bottom"

    @pytest.mark.asyncio
    async def test_add_pin_all_types(self, schematic_with_sheet):
        """Test adding pins with all valid pin types."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]
        pin_types = ["input", "output", "bidirectional", "tri_state", "passive"]

        for i, pin_type in enumerate(pin_types):
            result = await manage_sheets(
                action="add_pin",
                sheet_uuid=sheet_uuid,
                pin_name=f"PIN_{i}",
                pin_type=pin_type,
                edge="right",
                position_along_edge=float(i * 10),
            )

            assert result["success"] is True
            assert result["pin_type"] == pin_type

    @pytest.mark.asyncio
    async def test_add_pin_invalid_pin_type(self, schematic_with_sheet):
        """Test that invalid pin type returns error."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="INVALID",
            pin_type="invalid_type",
            edge="right",
            position_along_edge=10.0,
        )

        assert result["success"] is False
        assert result["error"] == "INVALID_PIN_TYPE"

    @pytest.mark.asyncio
    async def test_add_pin_invalid_edge(self, schematic_with_sheet):
        """Test that invalid edge returns error."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="INVALID",
            pin_type="output",
            edge="middle",
            position_along_edge=10.0,
        )

        assert result["success"] is False
        assert result["error"] == "INVALID_EDGE"


# ============================================================================
# Test manage_sheets with remove_pin action
# ============================================================================


class TestManageSheetsRemovePin:
    """Test manage_sheets with remove_pin action."""

    @pytest.mark.asyncio
    async def test_remove_pin_success(self, schematic_with_sheet):
        """Test successfully removing a sheet pin."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        # Add a pin first
        add_result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="VCC",
            pin_type="output",
            edge="right",
            position_along_edge=10.0,
        )
        assert add_result["success"] is True
        pin_uuid = add_result["pin_uuid"]

        # Remove the pin
        remove_result = await manage_sheets(
            action="remove_pin",
            sheet_uuid=sheet_uuid,
            pin_uuid=pin_uuid,
        )

        assert remove_result["success"] is True
        assert remove_result["pin_uuid"] == pin_uuid

    @pytest.mark.asyncio
    async def test_remove_pin_missing_params(self, schematic_with_sheet):
        """Test that missing parameters returns error."""
        result = await manage_sheets(
            action="remove_pin",
            sheet_uuid=schematic_with_sheet["sheet_uuid"],
            # Missing pin_uuid
        )

        assert result["success"] is False
        assert result["error"] == "INVALID_PARAMS"

    @pytest.mark.asyncio
    async def test_remove_nonexistent_pin(self, schematic_with_sheet):
        """Test removing a nonexistent pin succeeds silently (logs warning)."""
        sheet_uuid = schematic_with_sheet["sheet_uuid"]

        result = await manage_sheets(
            action="remove_pin",
            sheet_uuid=sheet_uuid,
            pin_uuid="nonexistent-uuid",
        )

        # Core library succeeds silently when pin doesn't exist (just logs warning)
        assert result["success"] is True


# ============================================================================
# Test manage_hierarchical_labels
# ============================================================================


class TestManageHierarchicalLabels:
    """Test manage_hierarchical_labels consolidated tool."""

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_input(self, child_schematic):
        """Test adding an input hierarchical label."""
        result = await manage_hierarchical_labels(
            action="add",
            text="INPUT_SIG",
            position=(100.0, 100.0),
            shape="input",
        )

        assert result["success"] is True
        assert result["text"] == "INPUT_SIG"
        assert result["shape"] == "input"
        assert result["position"]["x"] == 100.0
        assert result["position"]["y"] == 100.0
        assert "label_uuid" in result

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_output(self, child_schematic):
        """Test adding an output hierarchical label."""
        result = await manage_hierarchical_labels(
            action="add",
            text="OUTPUT_SIG",
            position=(150.0, 100.0),
            shape="output",
        )

        assert result["success"] is True
        assert result["shape"] == "output"

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_bidirectional(self, child_schematic):
        """Test adding a bidirectional hierarchical label."""
        result = await manage_hierarchical_labels(
            action="add",
            text="DATA",
            position=(200.0, 100.0),
            shape="bidirectional",
        )

        assert result["success"] is True
        assert result["shape"] == "bidirectional"

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_tri_state(self, child_schematic):
        """Test adding a tri-state hierarchical label."""
        result = await manage_hierarchical_labels(
            action="add",
            text="TRISTATE_SIG",
            position=(250.0, 100.0),
            shape="tri_state",
        )

        assert result["success"] is True
        assert result["shape"] == "tri_state"

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_passive(self, child_schematic):
        """Test adding a passive hierarchical label."""
        result = await manage_hierarchical_labels(
            action="add",
            text="PASSIVE_SIG",
            position=(300.0, 100.0),
            shape="passive",
        )

        assert result["success"] is True
        assert result["shape"] == "passive"

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_with_rotation(self, child_schematic):
        """Test adding a hierarchical label with rotation."""
        result = await manage_hierarchical_labels(
            action="add",
            text="ROTATED",
            position=(100.0, 150.0),
            shape="output",
            rotation=90.0,
        )

        assert result["success"] is True
        assert result["rotation"] == 90.0

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_with_custom_size(self, child_schematic):
        """Test adding a hierarchical label with custom size."""
        result = await manage_hierarchical_labels(
            action="add",
            text="LARGE",
            position=(100.0, 200.0),
            shape="output",
            size=2.54,
        )

        assert result["success"] is True
        assert result["size"] == 2.54

    @pytest.mark.asyncio
    async def test_add_hierarchical_label_invalid_shape(self, child_schematic):
        """Test that invalid shape returns error."""
        result = await manage_hierarchical_labels(
            action="add",
            text="INVALID",
            position=(100.0, 100.0),
            shape="invalid_shape",
        )

        assert result["success"] is False
        assert result["error"] == "INVALID_SHAPE"

    @pytest.mark.asyncio
    async def test_remove_hierarchical_label(self, child_schematic):
        """Test removing a hierarchical label."""
        # Add a label first
        add_result = await manage_hierarchical_labels(
            action="add",
            text="TO_REMOVE",
            position=(100.0, 100.0),
            shape="output",
        )
        assert add_result["success"] is True
        label_uuid = add_result["label_uuid"]

        # Remove the label
        remove_result = await manage_hierarchical_labels(
            action="remove",
            label_uuid=label_uuid,
        )

        assert remove_result["success"] is True
        assert remove_result["label_uuid"] == label_uuid

    @pytest.mark.asyncio
    async def test_remove_hierarchical_label_missing_params(self, child_schematic):
        """Test that missing label_uuid returns error."""
        result = await manage_hierarchical_labels(
            action="remove",
            # Missing label_uuid
        )

        assert result["success"] is False
        assert result["error"] == "INVALID_PARAMS"


# ============================================================================
# Test Complete Hierarchical Workflow
# ============================================================================


class TestHierarchicalWorkflowEndToEnd:
    """Test complete hierarchical schematic workflow."""

    @pytest.mark.asyncio
    async def test_complete_hierarchical_workflow(self):
        """Test complete workflow from parent to child with pins and labels."""
        # Step 1: Create parent schematic
        parent_result = await manage_schematic(action="create", name="ParentProject")
        assert parent_result["success"] is True
        parent_uuid = parent_result["uuid"]

        # Step 2: Add hierarchical sheet
        sheet_result = await manage_sheets(
            action="add",
            name="PowerSupply",
            filename="power.kicad_sch",
            position=(50.0, 50.0),
            size=(100.0, 80.0),
            project_name="ParentProject",
        )
        assert sheet_result["success"] is True
        sheet_uuid = sheet_result["sheet_uuid"]

        # Step 3: Add sheet pins to parent
        vcc_pin_result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="VCC",
            pin_type="output",
            edge="right",
            position_along_edge=20.0,
        )
        assert vcc_pin_result["success"] is True

        gnd_pin_result = await manage_sheets(
            action="add_pin",
            sheet_uuid=sheet_uuid,
            pin_name="GND",
            pin_type="output",
            edge="right",
            position_along_edge=40.0,
        )
        assert gnd_pin_result["success"] is True

        # Step 4: Create child schematic
        child_result = await manage_schematic(action="create", name="ParentProject")
        assert child_result["success"] is True

        # Step 5: Set hierarchy context
        context_result = await manage_sheets(
            action="set_context",
            parent_uuid=parent_uuid,
            sheet_uuid=sheet_uuid,
        )
        assert context_result["success"] is True

        # Step 6: Add hierarchical labels in child
        vcc_label_result = await manage_hierarchical_labels(
            action="add",
            text="VCC",
            position=(150.0, 100.0),
            shape="output",
        )
        assert vcc_label_result["success"] is True

        gnd_label_result = await manage_hierarchical_labels(
            action="add",
            text="GND",
            position=(150.0, 120.0),
            shape="output",
        )
        assert gnd_label_result["success"] is True

        # Verify everything succeeded
        assert vcc_pin_result["pin_name"] == "VCC"
        assert gnd_pin_result["pin_name"] == "GND"
        assert vcc_label_result["text"] == "VCC"
        assert gnd_label_result["text"] == "GND"

    @pytest.mark.asyncio
    async def test_multi_level_hierarchy(self):
        """Test multi-level hierarchy (3 levels)."""
        # Level 1: Top-level schematic
        top_result = await manage_schematic(action="create", name="TopLevel")
        assert top_result["success"] is True
        top_uuid = top_result["uuid"]

        # Add sheet to top level
        mid_sheet_result = await manage_sheets(
            action="add",
            name="MidLevel",
            filename="mid.kicad_sch",
            position=(50.0, 50.0),
            size=(100.0, 80.0),
            project_name="TopLevel",
        )
        assert mid_sheet_result["success"] is True
        mid_sheet_uuid = mid_sheet_result["sheet_uuid"]

        # Add pin to mid-level sheet
        await manage_sheets(
            action="add_pin",
            sheet_uuid=mid_sheet_uuid,
            pin_name="SIGNAL",
            pin_type="output",
            edge="right",
            position_along_edge=20.0,
        )

        # Level 2: Mid-level schematic
        mid_result = await manage_schematic(action="create", name="TopLevel")
        assert mid_result["success"] is True
        mid_uuid = mid_result["uuid"]

        await manage_sheets(
            action="set_context",
            parent_uuid=top_uuid,
            sheet_uuid=mid_sheet_uuid,
        )

        # Add sheet to mid level
        low_sheet_result = await manage_sheets(
            action="add",
            name="LowLevel",
            filename="low.kicad_sch",
            position=(50.0, 50.0),
            size=(100.0, 80.0),
            project_name="TopLevel",
        )
        assert low_sheet_result["success"] is True
        low_sheet_uuid = low_sheet_result["sheet_uuid"]

        # Add pin to low-level sheet
        await manage_sheets(
            action="add_pin",
            sheet_uuid=low_sheet_uuid,
            pin_name="DATA",
            pin_type="bidirectional",
            edge="right",
            position_along_edge=30.0,
        )

        # Level 3: Low-level schematic
        low_result = await manage_schematic(action="create", name="TopLevel")
        assert low_result["success"] is True

        await manage_sheets(
            action="set_context",
            parent_uuid=mid_uuid,
            sheet_uuid=low_sheet_uuid,
        )

        # Add label to low level
        label_result = await manage_hierarchical_labels(
            action="add",
            text="DATA",
            position=(150.0, 100.0),
            shape="bidirectional",
        )
        assert label_result["success"] is True
