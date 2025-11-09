"""
Reference tests for property positioning - validates against KiCAD native placement.

Each test loads a reference schematic created manually in KiCAD with fields_autoplaced
and verifies exact property positions match expected values.

Related:
- Issue #150: Default component property text positioning doesn't match KiCAD auto-placement
- PRD: docs/prd/property-positioning-prd.md
- Analysis: docs/PROPERTY_POSITIONING_ANALYSIS.md
- References: tests/reference_kicad_projects/property_positioning_*/
"""

import pytest

import kicad_sch_api as ksa


class TestResistorReferencePositioning:
    """Validate resistor property positioning against KiCAD reference.

    Reference: property_positioning_resistor/resistor.kicad_sch
    Component: Device:R at (100, 100, 0°)
    Pattern: Properties positioned RIGHT and STACKED vertically
    """

    @pytest.fixture
    def resistor_sch(self):
        """Load resistor reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_resistor/resistor.kicad_sch"
        )

    def test_load_resistor_reference(self, resistor_sch):
        """Reference schematic should load successfully."""
        assert resistor_sch is not None
        assert len(resistor_sch.components) == 1

    def test_resistor_has_fields_autoplaced(self, resistor_sch):
        """Component should have fields_autoplaced=True."""
        comp = resistor_sch.components[0]
        assert comp.fields_autoplaced is True

    def test_resistor_component_position(self, resistor_sch):
        """Component should be at expected position with 0° rotation."""
        comp = resistor_sch.components[0]
        assert comp.position.x == 100.0
        assert comp.position.y == 100.0
        assert comp.rotation == 0.0

    def test_resistor_reference_property_position(self, resistor_sch):
        """Reference property should be at (102.54, 98.7299, 0°).

        Expected offset from component: (+2.54, -1.2701)
        Pattern: RIGHT side, ABOVE component
        """
        comp = resistor_sch.components[0]
        ref_prop = comp.properties["Reference"]

        assert ref_prop["at"][0] == pytest.approx(102.54, abs=0.01)
        assert ref_prop["at"][1] == pytest.approx(98.7299, abs=0.01)
        assert ref_prop["at"][2] == 0.0  # No text rotation

    def test_resistor_value_property_position(self, resistor_sch):
        """Value property should be at (102.54, 101.2699, 0°).

        Expected offset from component: (+2.54, +1.2699)
        Pattern: RIGHT side, BELOW component
        """
        comp = resistor_sch.components[0]
        val_prop = comp.properties["Value"]

        assert val_prop["at"][0] == pytest.approx(102.54, abs=0.01)
        assert val_prop["at"][1] == pytest.approx(101.2699, abs=0.01)
        assert val_prop["at"][2] == 0.0

    def test_resistor_footprint_property_hidden(self, resistor_sch):
        """Footprint property should be hidden and positioned LEFT with 90° rotation."""
        comp = resistor_sch.components[0]
        fp_prop = comp.properties["Footprint"]

        assert fp_prop["effects"]["hide"] == "yes"
        assert fp_prop["at"][0] == pytest.approx(98.222, abs=0.01)  # LEFT of component
        assert fp_prop["at"][2] == 90.0  # Vertical text

    def test_resistor_properties_use_justify_left(self, resistor_sch):
        """Visible properties should use justify left."""
        comp = resistor_sch.components[0]

        ref_justify = comp.properties["Reference"]["effects"].get("justify")
        val_justify = comp.properties["Value"]["effects"].get("justify")

        assert ref_justify == "left"
        assert val_justify == "left"


class TestCapacitorReferencePositioning:
    """Validate capacitor property positioning against KiCAD reference.

    Reference: property_positioning_capacitor/capacitor.kicad_sch
    Component: Device:C at (118.11, 68.58, 0°)
    Pattern: Slight RIGHT offset, different from resistor
    """

    @pytest.fixture
    def capacitor_sch(self):
        """Load capacitor reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_capacitor/capacitor.kicad_sch"
        )

    def test_capacitor_has_different_offset_than_resistor(self, capacitor_sch):
        """Capacitor should use DIFFERENT offset than resistor.

        This validates library-specific positioning.
        Capacitor offset: (+0.64, ±2.54)
        Resistor offset: (+2.54, ±1.27)  ← DIFFERENT
        """
        comp = capacitor_sch.components[0]
        comp_x = comp.position.x
        comp_y = comp.position.y

        ref_prop = comp.properties["Reference"]
        ref_offset_x = ref_prop["at"][0] - comp_x
        ref_offset_y = ref_prop["at"][1] - comp_y

        # Capacitor uses +0.64 horizontal offset (not +2.54 like resistor)
        assert ref_offset_x == pytest.approx(0.64, abs=0.01)
        assert ref_offset_y == pytest.approx(2.54, abs=0.01)


class TestDiodeReferencePositioning:
    """Validate diode property positioning against KiCAD reference.

    Reference: property_positioning_diode/diode.kicad_sch
    Component: Device:D at (123.19, 81.28, 0°)
    Pattern: CENTERED vertical stacking (no horizontal offset)
    """

    @pytest.fixture
    def diode_sch(self):
        """Load diode reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_diode/diode.kicad_sch"
        )

    def test_diode_centered_vertical_stacking(self, diode_sch):
        """Diode should stack properties VERTICALLY on centerline.

        This is DIFFERENT from resistor (which offsets horizontally).
        Expected offset: (0, ±2.54) - no horizontal offset
        """
        comp = diode_sch.components[0]
        comp_x = comp.position.x
        comp_y = comp.position.y

        ref_prop = comp.properties["Reference"]
        val_prop = comp.properties["Value"]

        ref_offset_x = ref_prop["at"][0] - comp_x
        val_offset_x = val_prop["at"][0] - comp_x

        # No horizontal offset (centered)
        assert ref_offset_x == pytest.approx(0.0, abs=0.01)
        assert val_offset_x == pytest.approx(0.0, abs=0.01)

        # Vertical stacking
        ref_offset_y = ref_prop["at"][1] - comp_y
        val_offset_y = val_prop["at"][1] - comp_y

        assert ref_offset_y == pytest.approx(2.54, abs=0.01)  # Above
        assert val_offset_y == pytest.approx(-2.54, abs=0.01)  # Below


class TestInductorReferencePositioning:
    """Validate inductor property positioning against KiCAD reference.

    Reference: property_positioning_inductor/inductor.kicad_sch
    Component: Device:L at (96.52, 62.23, 0°)
    Pattern: HORIZONTAL stacking with 90° text rotation
    """

    @pytest.fixture
    def inductor_sch(self):
        """Load inductor reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_inductor/inductor.kicad_sch"
        )

    def test_inductor_horizontal_stacking(self, inductor_sch):
        """Inductor should stack properties HORIZONTALLY (left/right).

        Pattern: Reference LEFT (-1.27, 0), Value RIGHT (+1.91, 0)
        """
        comp = inductor_sch.components[0]
        comp_x = comp.position.x
        comp_y = comp.position.y

        ref_prop = comp.properties["Reference"]
        val_prop = comp.properties["Value"]

        ref_offset_x = ref_prop["at"][0] - comp_x
        val_offset_x = val_prop["at"][0] - comp_x

        # Horizontal stacking
        assert ref_offset_x == pytest.approx(-1.27, abs=0.01)  # Left
        assert val_offset_x == pytest.approx(1.91, abs=0.01)  # Right

        # No vertical offset (horizontal stacking)
        ref_offset_y = ref_prop["at"][1] - comp_y
        val_offset_y = val_prop["at"][1] - comp_y

        assert ref_offset_y == pytest.approx(0.0, abs=0.01)
        assert val_offset_y == pytest.approx(0.0, abs=0.01)

    def test_inductor_text_rotated_90deg(self, inductor_sch):
        """Inductor properties should have 90° text rotation."""
        comp = inductor_sch.components[0]

        ref_rotation = comp.properties["Reference"]["at"][2]
        val_rotation = comp.properties["Value"]["at"][2]

        assert ref_rotation == 90.0
        assert val_rotation == 90.0


class TestLEDReferencePositioning:
    """Validate LED property positioning against KiCAD reference.

    Reference: property_positioning_led/led.kicad_sch
    Component: Device:LED at (120.65, 73.66, 0°)
    Pattern: Same as diode (centered vertical stacking)
    """

    @pytest.fixture
    def led_sch(self):
        """Load LED reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_led/led.kicad_sch"
        )

    def test_led_same_pattern_as_diode(self, led_sch):
        """LED should use same pattern as diode (both are 2-pin polar).

        Expected: centered vertical stacking (0, ±2.54)
        """
        comp = led_sch.components[0]
        comp_x = comp.position.x
        comp_y = comp.position.y

        ref_prop = comp.properties["Reference"]

        ref_offset_x = ref_prop["at"][0] - comp_x
        ref_offset_y = ref_prop["at"][1] - comp_y

        # Centered like diode
        assert ref_offset_x == pytest.approx(0.0, abs=0.01)
        assert ref_offset_y == pytest.approx(2.54, abs=0.01)


class TestTransistorReferencePositioning:
    """Validate transistor property positioning against KiCAD reference.

    Reference: property_positioning_transistor_bjt/transistor_bjt.kicad_sch
    Component: Transistor_BJT:2N2219 at (127.0, 91.44, 0°)
    Pattern: RIGHT side with larger offset than 2-pin components
    """

    @pytest.fixture
    def transistor_sch(self):
        """Load transistor reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_transistor_bjt/transistor_bjt.kicad_sch"
        )

    def test_transistor_larger_horizontal_offset(self, transistor_sch):
        """Transistor should use larger horizontal offset (+5.08) than resistor (+2.54).

        3-pin component uses wider offset for clearance.
        """
        comp = transistor_sch.components[0]
        comp_x = comp.position.x

        ref_prop = comp.properties["Reference"]
        ref_offset_x = ref_prop["at"][0] - comp_x

        # Larger offset for 3-pin component
        assert ref_offset_x == pytest.approx(5.08, abs=0.01)


class TestOpAmpReferencePositioning:
    """Validate op-amp property positioning against KiCAD reference.

    Reference: property_positioning_op_amp/op_amp.kicad_sch
    Component: Amplifier_Operational:TL072 at (123.19, 40.64, 0°)
    Pattern: Centered with LARGE vertical spacing for IC
    """

    @pytest.fixture
    def op_amp_sch(self):
        """Load op-amp reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_op_amp/op_amp.kicad_sch"
        )

    def test_op_amp_large_ic_spacing(self, op_amp_sch):
        """Op-amp (IC) should use larger vertical spacing (±5.08) than 2-pin components.

        IC is taller, needs more vertical clearance.
        Expected: centered (0, ±5.08)
        """
        comp = op_amp_sch.components[0]
        comp_x = comp.position.x
        comp_y = comp.position.y

        ref_prop = comp.properties["Reference"]
        val_prop = comp.properties["Value"]

        # Centered horizontally
        ref_offset_x = ref_prop["at"][0] - comp_x
        assert ref_offset_x == pytest.approx(0.0, abs=0.01)

        # Large vertical spacing
        ref_offset_y = ref_prop["at"][1] - comp_y
        val_offset_y = val_prop["at"][1] - comp_y

        assert ref_offset_y == pytest.approx(5.08, abs=0.01)
        assert val_offset_y == pytest.approx(-5.08, abs=0.01)


class TestLogicICReferencePositioning:
    """Validate logic IC property positioning against KiCAD reference.

    Reference: property_positioning_logic_ic/logic_ic.kicad_sch
    Component: 74xx:74HC595 at (130.81, 57.15, 0°)
    Pattern: LEFT side with VERY LARGE vertical spacing
    """

    @pytest.fixture
    def logic_ic_sch(self):
        """Load logic IC reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_logic_ic/logic_ic.kicad_sch"
        )

    def test_logic_ic_left_positioning(self, logic_ic_sch):
        """Large logic IC should position properties LEFT with huge spacing.

        16-pin IC uses left positioning: (-7.62, ±13-16mm)
        Different from op-amp (centered).
        """
        comp = logic_ic_sch.components[0]
        comp_x = comp.position.x
        comp_y = comp.position.y

        ref_prop = comp.properties["Reference"]
        val_prop = comp.properties["Value"]

        # LEFT positioning
        ref_offset_x = ref_prop["at"][0] - comp_x
        val_offset_x = val_prop["at"][0] - comp_x

        assert ref_offset_x == pytest.approx(-7.62, abs=0.01)
        assert val_offset_x == pytest.approx(-7.62, abs=0.01)

        # Very large vertical spacing
        ref_offset_y = ref_prop["at"][1] - comp_y
        val_offset_y = val_prop["at"][1] - comp_y

        assert ref_offset_y == pytest.approx(13.97, abs=0.01)
        assert val_offset_y == pytest.approx(-16.51, abs=0.01)


class TestConnectorReferencePositioning:
    """Validate connector property positioning against KiCAD reference.

    Reference: property_positioning_connector/connector.kicad_sch
    Component: Connector:Conn_01x04_Pin at (137.16, 69.85, 0°)
    Pattern: Centered with multi-pin spacing
    """

    @pytest.fixture
    def connector_sch(self):
        """Load connector reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_connector/connector.kicad_sch"
        )

    def test_connector_centered_stacking(self, connector_sch):
        """Connector should use centered vertical stacking.

        Multi-pin connector: (0, ±5-7.62mm)
        """
        comp = connector_sch.components[0]
        comp_x = comp.position.x

        ref_prop = comp.properties["Reference"]
        ref_offset_x = ref_prop["at"][0] - comp_x

        # Centered
        assert ref_offset_x == pytest.approx(0.0, abs=0.01)


class TestCapacitorPolarizedReferencePositioning:
    """Validate polarized capacitor property positioning against KiCAD reference.

    Reference: property_positioning_capacitor_electrolytic/capacitor_electrolytic.kicad_sch
    Component: Device:C_Polarized at (139.70, 69.85, 0°)
    Pattern: Same as unpolarized capacitor
    """

    @pytest.fixture
    def cap_polarized_sch(self):
        """Load polarized capacitor reference schematic."""
        return ksa.Schematic.load(
            "tests/reference_kicad_projects/property_positioning_capacitor_electrolytic/capacitor_electrolytic.kicad_sch"
        )

    def test_polarized_capacitor_same_as_unpolarized(self, cap_polarized_sch):
        """Polarized capacitor should use same positioning as unpolarized.

        Expected: (+0.64, ±2.54) like Device:C
        """
        comp = cap_polarized_sch.components[0]
        comp_x = comp.position.x
        comp_y = comp.position.y

        ref_prop = comp.properties["Reference"]

        ref_offset_x = ref_prop["at"][0] - comp_x
        ref_offset_y = ref_prop["at"][1] - comp_y

        # Same as unpolarized capacitor
        assert ref_offset_x == pytest.approx(0.64, abs=0.01)
        assert ref_offset_y == pytest.approx(2.54, abs=0.01)


class TestFormatPreservationAcrossAllReferences:
    """Test round-trip format preservation for all 10 reference schematics."""

    @pytest.mark.parametrize(
        "ref_file",
        [
            "property_positioning_resistor/resistor.kicad_sch",
            "property_positioning_capacitor/capacitor.kicad_sch",
            "property_positioning_inductor/inductor.kicad_sch",
            "property_positioning_diode/diode.kicad_sch",
            "property_positioning_led/led.kicad_sch",
            "property_positioning_transistor_bjt/transistor_bjt.kicad_sch",
            "property_positioning_op_amp/op_amp.kicad_sch",
            "property_positioning_logic_ic/logic_ic.kicad_sch",
            "property_positioning_connector/connector.kicad_sch",
            "property_positioning_capacitor_electrolytic/capacitor_electrolytic.kicad_sch",
        ],
    )
    def test_round_trip_format_preservation(self, ref_file, tmp_path):
        """Each reference should round-trip with exact format preservation.

        Load → Save → Load should produce identical property positions.
        """
        import filecmp

        ref_path = f"tests/reference_kicad_projects/{ref_file}"

        # Load reference
        sch = ksa.Schematic.load(ref_path)

        # Save to temp
        temp_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(temp_file))

        # Files should be byte-identical (or semantically equivalent)
        # Note: Some whitespace/formatting differences may be acceptable
        assert filecmp.cmp(
            ref_path, str(temp_file), shallow=False
        ), f"Round-trip failed for {ref_file}"
