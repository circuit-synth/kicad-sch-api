"""
Comprehensive tests for Issue #13: Public properties for all schematic elements.

Tests all new public collection properties and their APIs.
"""

import pytest

from kicad_sch_api.collections.labels import LabelCollection, LabelElement
from kicad_sch_api.core.nets import NetCollection, NetElement
from kicad_sch_api.core.no_connects import NoConnectCollection, NoConnectElement
from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.texts import TextCollection, TextElement
from kicad_sch_api.core.types import Label, LabelType, Net, NoConnect, Point, Text
from kicad_sch_api.utils.validation import ValidationError


class TestTextCollection:
    """Test text collection functionality."""

    def test_texts_property_exists(self):
        """Test that schematic has texts property."""
        sch = Schematic.create("Test")
        assert hasattr(sch, "texts")
        assert isinstance(sch.texts, TextCollection)

    def test_add_text(self):
        """Test adding text elements."""
        sch = Schematic.create("Test")
        text = sch.texts.add("Hello", position=(100, 100))

        assert len(sch.texts) == 1
        assert text.text == "Hello"
        assert text.position == Point(100, 100)
        assert text.size == 1.27  # Default size

    def test_add_text_with_custom_params(self):
        """Test adding text with custom parameters."""
        sch = Schematic.create("Test")
        text = sch.texts.add(
            "Custom", position=(50, 50), rotation=90, size=2.54, exclude_from_sim=True
        )

        assert text.text == "Custom"
        assert text.rotation == 90
        assert text.size == 2.54
        assert text.exclude_from_sim == True

    def test_get_text_by_uuid(self):
        """Test getting text by UUID."""
        sch = Schematic.create("Test")
        text = sch.texts.add("Test", position=(100, 100))

        found = sch.texts.get(text.uuid)
        assert found is not None
        assert found.text == "Test"

    def test_remove_text(self):
        """Test removing text elements."""
        sch = Schematic.create("Test")
        text = sch.texts.add("Remove Me", position=(100, 100))
        text_uuid = text.uuid

        assert len(sch.texts) == 1
        removed = sch.texts.remove(text_uuid)
        assert removed == True
        assert len(sch.texts) == 0

    def test_find_text_by_content(self):
        """Test finding texts by content."""
        sch = Schematic.create("Test")
        sch.texts.add("Hello World", position=(100, 100))
        sch.texts.add("Test Text", position=(150, 150))

        found = sch.texts.find_by_content("Hello World")
        assert len(found) == 1
        assert found[0].text == "Hello World"

    def test_find_text_substring(self):
        """Test finding texts with substring match."""
        sch = Schematic.create("Test")
        sch.texts.add("Hello World", position=(100, 100))
        sch.texts.add("Hello Test", position=(150, 150))
        sch.texts.add("Other", position=(200, 200))

        found = sch.texts.find_by_content("Hello", exact=False)
        assert len(found) == 2

    def test_filter_texts(self):
        """Test filtering texts with predicate."""
        sch = Schematic.create("Test")
        sch.texts.add("Small", position=(100, 100), size=1.0)
        sch.texts.add("Large", position=(150, 150), size=3.0)
        sch.texts.add("Medium", position=(200, 200), size=2.0)

        large_texts = sch.texts.filter(lambda t: t.size > 2.0)
        assert len(large_texts) == 1
        assert large_texts[0].text == "Large"

    def test_bulk_update_texts(self):
        """Test bulk updating texts."""
        sch = Schematic.create("Test")
        text1 = sch.texts.add("Text1", position=(100, 100), size=1.0)
        text2 = sch.texts.add("Text2", position=(150, 150), size=1.0)

        sch.texts.bulk_update(criteria=lambda t: t.size < 2.0, updates={"size": 3.0})

        assert text1.size == 3.0
        assert text2.size == 3.0

    def test_text_iteration(self):
        """Test iterating over texts."""
        sch = Schematic.create("Test")
        sch.texts.add("Text1", position=(100, 100))
        sch.texts.add("Text2", position=(150, 150))
        sch.texts.add("Text3", position=(200, 200))

        texts = list(sch.texts)
        assert len(texts) == 3

    def test_text_indexing(self):
        """Test indexing texts."""
        sch = Schematic.create("Test")
        text1 = sch.texts.add("Text1", position=(100, 100))
        text2 = sch.texts.add("Text2", position=(150, 150))

        assert sch.texts[0] == text1
        assert sch.texts[1] == text2

    def test_empty_text_error(self):
        """Test that empty text raises error."""
        sch = Schematic.create("Test")
        with pytest.raises(ValidationError):
            sch.texts.add("", position=(100, 100))


class TestLabelCollection:
    """Test label collection functionality."""

    def test_labels_property_exists(self):
        """Test that schematic has labels property."""
        sch = Schematic.create("Test")
        assert hasattr(sch, "labels")
        assert isinstance(sch.labels, LabelCollection)

    def test_add_label(self):
        """Test adding label elements."""
        sch = Schematic.create("Test")
        label = sch.labels.add("VCC", position=(100, 100))

        assert len(sch.labels) == 1
        assert label.text == "VCC"
        assert label.position == Point(100, 100)

    def test_find_label_by_text(self):
        """Test finding labels by text."""
        sch = Schematic.create("Test")
        sch.labels.add("VCC", position=(100, 100))
        sch.labels.add("GND", position=(150, 150))

        found = sch.labels.get_by_text("VCC")
        assert len(found) == 1
        assert found[0].text == "VCC"

    def test_get_label_by_text(self):
        """Test getting labels by text."""
        sch = Schematic.create("Test")
        label = sch.labels.add("VCC", position=(100, 100))

        found = sch.labels.get_by_text("VCC")
        assert len(found) == 1
        assert found[0] == label

    def test_remove_label(self):
        """Test removing labels."""
        sch = Schematic.create("Test")
        label = sch.labels.add("VCC", position=(100, 100))

        removed = sch.labels.remove(label.uuid)
        assert removed == True
        assert len(sch.labels) == 0

    def test_label_update_text(self):
        """Test updating label text."""
        sch = Schematic.create("Test")
        label = sch.labels.add("OLD", position=(100, 100))

        label.text = "NEW"
        assert label.text == "NEW"

        found = sch.labels.get_by_text("NEW")
        assert len(found) == 1

    def test_hierarchical_labels_property(self):
        """Test hierarchical_labels property."""
        sch = Schematic.create("Test")
        assert hasattr(sch, "hierarchical_labels")
        assert isinstance(sch.hierarchical_labels, LabelCollection)


class TestNoConnectCollection:
    """Test no-connect collection functionality."""

    def test_no_connects_property_exists(self):
        """Test that schematic has no_connects property."""
        sch = Schematic.create("Test")
        assert hasattr(sch, "no_connects")
        assert isinstance(sch.no_connects, NoConnectCollection)

    def test_add_no_connect(self):
        """Test adding no-connect elements."""
        sch = Schematic.create("Test")
        nc = sch.no_connects.add(position=(100, 100))

        assert len(sch.no_connects) == 1
        assert nc.position == Point(100, 100)

    def test_get_no_connect_by_uuid(self):
        """Test getting no-connect by UUID."""
        sch = Schematic.create("Test")
        nc = sch.no_connects.add(position=(100, 100))

        found = sch.no_connects.get(nc.uuid)
        assert found is not None
        assert found.position == Point(100, 100)

    def test_find_no_connect_at_position(self):
        """Test finding no-connects at position."""
        sch = Schematic.create("Test")
        nc = sch.no_connects.add(position=(100, 100))

        found = sch.no_connects.find_at_position((100, 100))
        assert len(found) == 1
        assert found[0] == nc

    def test_find_no_connect_with_tolerance(self):
        """Test finding no-connects with tolerance."""
        sch = Schematic.create("Test")
        nc = sch.no_connects.add(position=(100, 100))

        # Should find within tolerance
        found = sch.no_connects.find_at_position((100.05, 100.05), tolerance=0.1)
        assert len(found) == 1

        # Should not find outside tolerance
        found = sch.no_connects.find_at_position((100.2, 100.2), tolerance=0.1)
        assert len(found) == 0

    def test_remove_no_connect(self):
        """Test removing no-connects."""
        sch = Schematic.create("Test")
        nc = sch.no_connects.add(position=(100, 100))

        removed = sch.no_connects.remove(nc.uuid)
        assert removed == True
        assert len(sch.no_connects) == 0


class TestNetCollection:
    """Test net collection functionality."""

    def test_nets_property_exists(self):
        """Test that schematic has nets property."""
        sch = Schematic.create("Test")
        assert hasattr(sch, "nets")
        assert isinstance(sch.nets, NetCollection)

    def test_add_net(self):
        """Test adding net elements."""
        sch = Schematic.create("Test")
        net = sch.nets.add("GND")

        assert len(sch.nets) == 1
        assert net.name == "GND"

    def test_get_net_by_name(self):
        """Test getting net by name."""
        sch = Schematic.create("Test")
        net = sch.nets.add("VCC")

        found = sch.nets.get("VCC")
        assert found is not None
        assert found.name == "VCC"

    def test_add_component_to_net(self):
        """Test adding component connections to net."""
        sch = Schematic.create("Test")
        net = sch.nets.add("GND")

        net.add_connection("R1", "2")
        net.add_connection("C1", "1")

        assert len(net.components) == 2
        assert ("R1", "2") in net.components

    def test_remove_component_from_net(self):
        """Test removing component connections from net."""
        sch = Schematic.create("Test")
        net = sch.nets.add("GND")

        net.add_connection("R1", "2")
        net.remove_connection("R1", "2")

        assert len(net.components) == 0

    def test_find_net_by_component(self):
        """Test finding nets by component."""
        sch = Schematic.create("Test")
        net1 = sch.nets.add("GND")
        net2 = sch.nets.add("VCC")

        net1.add_connection("R1", "1")
        net2.add_connection("R1", "2")

        found = sch.nets.find_by_component("R1")
        assert len(found) == 2

    def test_find_net_by_component_and_pin(self):
        """Test finding nets by component and pin."""
        sch = Schematic.create("Test")
        net1 = sch.nets.add("GND")
        net2 = sch.nets.add("VCC")

        net1.add_connection("R1", "1")
        net2.add_connection("R1", "2")

        found = sch.nets.find_by_component("R1", pin="2")
        assert len(found) == 1
        assert found[0].name == "VCC"

    def test_remove_net(self):
        """Test removing nets."""
        sch = Schematic.create("Test")
        sch.nets.add("GND")

        removed = sch.nets.remove("GND")
        assert removed == True
        assert len(sch.nets) == 0

    def test_duplicate_net_name_error(self):
        """Test that duplicate net names raise error."""
        sch = Schematic.create("Test")
        sch.nets.add("GND")

        with pytest.raises(ValidationError):
            sch.nets.add("GND")


class TestSchematicModifiedTracking:
    """Test that modifications are tracked across all collections."""

    def test_modified_on_text_add(self):
        """Test schematic marked modified when text added."""
        sch = Schematic.create("Test")
        sch.texts.add("Test", position=(100, 100))
        assert sch.modified == True

    def test_modified_on_label_add(self):
        """Test schematic marked modified when label added."""
        sch = Schematic.create("Test")
        sch.labels.add("VCC", position=(100, 100))
        assert sch.modified == True

    def test_modified_on_no_connect_add(self):
        """Test schematic marked modified when no-connect added."""
        sch = Schematic.create("Test")
        sch.no_connects.add(position=(100, 100))
        assert sch.modified == True

    def test_modified_on_net_add(self):
        """Test schematic marked modified when net added."""
        sch = Schematic.create("Test")
        sch.nets.add("GND")
        assert sch.modified == True


class TestBackwardsCompatibility:
    """Test that existing functionality is not broken."""

    def test_existing_properties_accessible(self):
        """Test that existing properties are still accessible."""
        sch = Schematic.create("Test")

        assert hasattr(sch, "components")
        assert hasattr(sch, "wires")
        assert hasattr(sch, "junctions")
        assert hasattr(sch, "version")
        assert hasattr(sch, "generator")
        assert hasattr(sch, "uuid")
        assert hasattr(sch, "title_block")

    def test_can_mix_old_and_new_apis(self):
        """Test using old and new APIs together."""
        sch = Schematic.create("Test")

        # Add using new API
        text = sch.texts.add("Label", position=(100, 100))

        # Check using existing properties
        assert sch.version is not None
        assert sch.generator is not None

        # Mix operations
        label = sch.labels.add("VCC", position=(150, 150))
        assert len(sch.texts) == 1
        assert len(sch.labels) == 1
