"""
Unit tests for Jupyter/IPython rich display (Issue #179 Phase 4).

Tests the _repr_html_() method for SymbolDefinition to enable rich display
in Jupyter notebooks.
"""

import pytest

from kicad_sch_api.core.types import PinType, Point, SchematicPin
from kicad_sch_api.library.cache import SymbolDefinition


class TestSymbolDefinitionReprHtml:
    """Test SymbolDefinition._repr_html_() method."""

    def test_repr_html_returns_string(self):
        """Should return HTML string."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
        )

        html = symbol._repr_html_()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_repr_html_contains_lib_id(self):
        """Should display lib_id."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
        )

        html = symbol._repr_html_()

        assert "Device:R" in html

    def test_repr_html_contains_library_and_prefix(self):
        """Should display library and reference prefix."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
        )

        html = symbol._repr_html_()

        assert "Device" in html
        assert "Reference Prefix" in html

    def test_repr_html_includes_description(self):
        """Should display description when available."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor component",
        )

        html = symbol._repr_html_()

        assert "Resistor component" in html

    def test_repr_html_includes_keywords(self):
        """Should display keywords when available."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            keywords="passive component",
        )

        html = symbol._repr_html_()

        assert "Keywords" in html
        assert "passive component" in html

    def test_repr_html_includes_datasheet_link(self):
        """Should display clickable datasheet link."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            datasheet="https://example.com/datasheet.pdf",
        )

        html = symbol._repr_html_()

        assert "Datasheet" in html
        assert "https://example.com/datasheet.pdf" in html
        assert "href=" in html

    def test_repr_html_shows_power_symbol(self):
        """Should indicate power symbols."""
        symbol = SymbolDefinition(
            lib_id="power:GND",
            name="GND",
            library="power",
            reference_prefix="#PWR",
            power_symbol=True,
        )

        html = symbol._repr_html_()

        assert "Power Symbol" in html

    def test_repr_html_shows_multi_unit_symbol(self):
        """Should show unit count for multi-unit symbols."""
        symbol = SymbolDefinition(
            lib_id="Amplifier_Operational:TL072",
            name="TL072",
            library="Amplifier_Operational",
            reference_prefix="U",
            units=3,
        )

        html = symbol._repr_html_()

        assert "Units" in html

    def test_repr_html_shows_extends(self):
        """Should show parent symbol when extending."""
        symbol = SymbolDefinition(
            lib_id="Custom:SpecialR",
            name="SpecialR",
            library="Custom",
            reference_prefix="R",
            extends="R",
        )

        html = symbol._repr_html_()

        assert "Extends" in html

    def test_repr_html_includes_pins_table(self):
        """Should display pins in HTML table."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            pins=[
                SchematicPin(
                    number="1",
                    name="~",
                    pin_type=PinType.PASSIVE,
                    position=Point(0, 0),
                ),
                SchematicPin(
                    number="2",
                    name="~",
                    pin_type=PinType.PASSIVE,
                    position=Point(0, 0),
                ),
            ],
        )

        html = symbol._repr_html_()

        assert "Pins" in html
        assert "<table" in html
        assert "Pin #" in html
        assert "Name" in html
        assert "Type" in html

    def test_repr_html_shows_pin_details(self):
        """Should show pin number, name, and type."""
        symbol = SymbolDefinition(
            lib_id="Custom:Test",
            name="Test",
            library="Custom",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="1",
                    name="VCC",
                    pin_type=PinType.POWER_IN,
                    position=Point(0, 0),
                )
            ],
        )

        html = symbol._repr_html_()

        assert "1" in html  # Pin number
        assert "VCC" in html  # Pin name
        assert "power_in" in html.lower()  # Pin type (case-insensitive check)

    def test_repr_html_no_pins_message(self):
        """Should show message when no pins."""
        symbol = SymbolDefinition(
            lib_id="Custom:NoPins",
            name="NoPins",
            library="Custom",
            reference_prefix="U",
        )

        html = symbol._repr_html_()

        assert "No pins defined" in html

    def test_repr_html_includes_metadata(self):
        """Should display metadata footer."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            pins=[
                SchematicPin(
                    number="1",
                    name="~",
                    pin_type=PinType.PASSIVE,
                    position=Point(0, 0),
                )
            ],
            graphic_elements=[{"type": "rectangle"}],
        )

        html = symbol._repr_html_()

        assert "pins" in html
        assert "graphic elements" in html

    def test_repr_html_styling(self):
        """Should include CSS styling."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
        )

        html = symbol._repr_html_()

        # Check for inline styles
        assert "style=" in html
        assert "border" in html
        assert "color" in html

    def test_repr_html_pin_type_colors(self):
        """Should color-code different pin types."""
        symbol = SymbolDefinition(
            lib_id="Custom:MultiType",
            name="MultiType",
            library="Custom",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="1",
                    name="IN",
                    pin_type=PinType.INPUT,
                    position=Point(0, 0),
                ),
                SchematicPin(
                    number="2",
                    name="OUT",
                    pin_type=PinType.OUTPUT,
                    position=Point(0, 0),
                ),
                SchematicPin(
                    number="3",
                    name="VCC",
                    pin_type=PinType.POWER_IN,
                    position=Point(0, 0),
                ),
            ],
        )

        html = symbol._repr_html_()

        # Should contain color codes (hex colors start with #)
        assert "#" in html
        # Different pins should have different colors
        # (This is a basic check - could be more sophisticated)
        assert html.count("color:") >= 3


class TestJupyterDisplayIntegration:
    """Integration tests for Jupyter display."""

    def test_symbol_displays_in_notebook_environment(self):
        """Should work with IPython/Jupyter display system."""
        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
            pins=[
                SchematicPin(
                    number="1",
                    name="~",
                    pin_type=PinType.PASSIVE,
                    position=Point(0, 0),
                ),
                SchematicPin(
                    number="2",
                    name="~",
                    pin_type=PinType.PASSIVE,
                    position=Point(0, 0),
                ),
            ],
        )

        # IPython/Jupyter looks for _repr_html_ method
        assert hasattr(symbol, "_repr_html_")
        assert callable(symbol._repr_html_)

        # Calling it should return valid HTML
        html = symbol._repr_html_()
        assert "<div" in html
        assert "</div>" in html


class TestRealWorldUsageScenarios:
    """Test real-world usage patterns in Jupyter."""

    def test_display_search_results(self):
        """User searches and displays results in notebook."""
        # Create mock search results
        resistors = [
            SymbolDefinition(
                lib_id="Device:R",
                name="R",
                library="Device",
                reference_prefix="R",
                description="Resistor",
            ),
            SymbolDefinition(
                lib_id="Device:R_Variable",
                name="R_Variable",
                library="Device",
                reference_prefix="R",
                description="Variable resistor",
            ),
        ]

        # Each should have HTML representation
        for symbol in resistors:
            html = symbol._repr_html_()
            assert "Device" in html
            assert "resistor" in html.lower()

    def test_display_esp32_with_many_pins(self):
        """User displays ESP32 module with many pins."""
        # Create ESP32-like symbol with multiple pins
        pins = []
        pin_names = ["GND", "VCC", "EN", "GPIO0", "GPIO2", "TXD", "RXD"]
        for i, name in enumerate(pin_names, 1):
            pins.append(
                SchematicPin(
                    number=str(i),
                    name=name,
                    pin_type=PinType.POWER_IN if name in ["GND", "VCC"] else PinType.BIDIRECTIONAL,
                    position=Point(0, 0),
                )
            )

        esp32 = SymbolDefinition(
            lib_id="RF_Module:ESP32-WROOM-32",
            name="ESP32-WROOM-32",
            library="RF_Module",
            reference_prefix="U",
            description="WiFi/Bluetooth module",
            pins=pins,
        )

        html = esp32._repr_html_()

        # Should display all pins
        for name in pin_names:
            assert name in html

        # Should have table structure
        assert "<table" in html
        assert "<tr" in html
        assert "<td" in html

    def test_display_power_symbol(self):
        """User displays power supply symbol."""
        gnd = SymbolDefinition(
            lib_id="power:GND",
            name="GND",
            library="power",
            reference_prefix="#PWR",
            description="Ground symbol",
            power_symbol=True,
            pins=[
                SchematicPin(
                    number="1",
                    name="GND",
                    pin_type=PinType.POWER_IN,
                    position=Point(0, 0),
                )
            ],
        )

        html = gnd._repr_html_()

        # Should indicate it's a power symbol
        assert "Power Symbol" in html
        assert "GND" in html

    def test_compare_symbols_side_by_side(self):
        """User compares multiple symbols."""
        symbols = [
            SymbolDefinition(
                lib_id="Device:R",
                name="R",
                library="Device",
                reference_prefix="R",
                description="Resistor",
                pins=[SchematicPin("1", "~", PinType.PASSIVE, Point(0, 0))],
            ),
            SymbolDefinition(
                lib_id="Device:C",
                name="C",
                library="Device",
                reference_prefix="C",
                description="Capacitor",
                pins=[SchematicPin("1", "~", PinType.PASSIVE, Point(0, 0))],
            ),
        ]

        # Each should have unique HTML
        htmls = [s._repr_html_() for s in symbols]

        assert len(htmls) == 2
        assert "Resistor" in htmls[0]
        assert "Capacitor" in htmls[1]
