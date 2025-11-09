#!/usr/bin/env python3
"""
FIXTURES LIBRARY TEMPLATE: Reusable Test Fixtures and Setup

This template demonstrates creating a library of reusable fixtures for pin
connection testing. Use this to:
  - Avoid duplicating setup code across tests
  - Create standard test schematics
  - Build common component combinations
  - Factory fixtures for flexible component creation
  - Shared test data and constants

Key Features:
  - Basic fixtures (empty schematic, single component)
  - Factory fixtures (create components with custom params)
  - Complex fixtures (multi-component circuits)
  - Data fixtures (test values, expected coordinates)
  - Scope management (session, module, function)
  - Documentation of fixture purposes
  - Logging to trace fixture creation
  - Examples of pytest fixture patterns

Can be used in conftest.py for project-wide availability,
or imported directly into test modules.

Copy and customize for your test fixture library.
"""

import logging
import os
import tempfile
from typing import List, Tuple

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

logger = logging.getLogger(__name__)


# ============================================================================
# BASIC FIXTURES
# ============================================================================


class TestBasicFixtures:
    """Examples of basic fixture patterns."""

    @pytest.fixture
    def empty_schematic(self):
        """
        Fixture: Create empty schematic.

        Scope: Function (new for each test)
        Use when: You need to start with a blank canvas
        """
        logger.info("Creating empty_schematic fixture")
        return ksa.create_schematic("Empty Test")

    @pytest.fixture
    def single_resistor_schematic(self):
        """
        Fixture: Create schematic with one resistor.

        Scope: Function
        Use when: Testing basic component operations
        """
        logger.info("Creating single_resistor_schematic fixture")
        sch = ksa.create_schematic("Single Resistor Test")

        resistor = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100.0, 100.0)
        )

        logger.info(f"Added R1 at {resistor.position}")
        return sch

    @pytest.fixture
    def two_resistor_schematic(self):
        """
        Fixture: Create schematic with two resistors.

        Scope: Function
        Use when: Testing connections between components
        """
        logger.info("Creating two_resistor_schematic fixture")
        sch = ksa.create_schematic("Two Resistor Test")

        r1 = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100.0, 100.0)
        )

        r2 = sch.components.add(
            lib_id="Device:R", reference="R2", value="20k", position=(150.0, 100.0)  # To the right
        )

        logger.info(f"Added R1 at {r1.position}, R2 at {r2.position}")
        return sch

    def test_using_empty_schematic(self, empty_schematic):
        """Example: Using basic fixture."""
        assert len(empty_schematic.components) == 0

    def test_using_single_resistor(self, single_resistor_schematic):
        """Example: Using single resistor fixture."""
        assert len(single_resistor_schematic.components) == 1
        r1 = single_resistor_schematic.components.get("R1")
        assert r1 is not None


# ============================================================================
# FACTORY FIXTURES
# ============================================================================


class TestFactoryFixtures:
    """Flexible fixtures that create components with custom parameters."""

    @pytest.fixture
    def schematic_factory(self):
        """
        Fixture: Factory for creating schematics with custom names.

        Returns a function that creates schematics.
        Allows tests to create multiple schematics with different names.
        """

        def _create_schematic(name="Test Schematic"):
            logger.info(f"Creating schematic: {name}")
            return ksa.create_schematic(name)

        return _create_schematic

    @pytest.fixture
    def resistor_factory(self):
        """
        Fixture: Factory for creating resistors with custom values.

        Returns a function that creates resistors in a schematic.

        Usage:
            sch = ksa.create_schematic("Test")
            r1 = resistor_factory(sch, "R1", "10k", (100, 100))
        """

        def _add_resistor(
            schematic,
            reference: str = "R1",
            value: str = "10k",
            position: Tuple[float, float] = (100.0, 100.0),
            rotation: float = 0.0,
        ):
            """
            Create and add resistor to schematic.

            Args:
                schematic: Schematic to add to
                reference: Component reference (e.g., "R1", "R2")
                value: Component value (e.g., "10k", "1M")
                position: (x, y) coordinates
                rotation: Rotation angle (0, 90, 180, 270)

            Returns:
                Created Component object
            """
            logger.info(f"Creating {reference}: {value} at {position}, {rotation}°")

            comp = schematic.components.add(
                lib_id="Device:R",
                reference=reference,
                value=value,
                position=position,
                rotation=rotation,
            )

            return comp

        return _add_resistor

    @pytest.fixture
    def component_factory(self):
        """
        Fixture: General-purpose component factory.

        Allows creating any type of component with parameters.
        """

        def _add_component(
            schematic,
            lib_id: str,
            reference: str,
            value: str = "test",
            position: Tuple[float, float] = (100.0, 100.0),
            rotation: float = 0.0,
        ):
            """Create and add component to schematic."""
            logger.info(f"Creating {reference} ({lib_id})")

            comp = schematic.components.add(
                lib_id=lib_id,
                reference=reference,
                value=value,
                position=position,
                rotation=rotation,
            )

            return comp

        return _add_component

    def test_using_resistor_factory(self, resistor_factory):
        """Example: Using factory fixture."""
        sch = ksa.create_schematic("Factory Test")

        # Create multiple resistors with factory
        r1 = resistor_factory(sch, "R1", "10k", (100, 100), 0)
        r2 = resistor_factory(sch, "R2", "20k", (150, 100), 90)

        assert r1.reference == "R1"
        assert r2.reference == "R2"
        assert r2.rotation == 90.0

    def test_using_component_factory(self, component_factory):
        """Example: Using general component factory."""
        sch = ksa.create_schematic("Component Factory Test")

        # Create different component types
        r1 = component_factory(sch, "Device:R", "R1", "10k")
        c1 = component_factory(sch, "Device:C", "C1", "100nF")

        assert len(sch.components) == 2


# ============================================================================
# COMPLEX CIRCUIT FIXTURES
# ============================================================================


class TestComplexFixtures:
    """Fixtures for complete circuits and common topologies."""

    @pytest.fixture
    def voltage_divider_schematic(self):
        """
        Fixture: Complete voltage divider circuit.

        Components:
          - VCC power supply
          - R1 (10k) from VCC to VOUT
          - R2 (10k) from VOUT to GND
          - GND ground symbol

        Usage: Test circuits that need multiple connected components
        """
        logger.info("Creating voltage_divider_schematic fixture")
        sch = ksa.create_schematic("Voltage Divider")

        # Add VCC (top)
        vcc = sch.components.add(
            lib_id="power:VCC", reference="#PWR01", value="VCC", position=(100.0, 50.0)
        )

        # Add R1 (top resistor)
        r1 = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100.0, 100.0)
        )

        # Add R2 (bottom resistor)
        r2 = sch.components.add(
            lib_id="Device:R", reference="R2", value="10k", position=(100.0, 150.0)
        )

        # Add GND (bottom)
        gnd = sch.components.add(
            lib_id="power:GND", reference="#PWR02", value="GND", position=(100.0, 200.0)
        )

        logger.info("Voltage divider created: VCC → R1 → R2 → GND")
        return sch

    @pytest.fixture
    def rc_filter_schematic(self):
        """
        Fixture: RC low-pass filter circuit.

        Components:
          - R (1k resistor)
          - C (100nF capacitor)
          - Input and output nodes

        Topology:
          VIN → R → |C| → GND
                    └→ VOUT
        """
        logger.info("Creating rc_filter_schematic fixture")
        sch = ksa.create_schematic("RC Filter")

        # Series resistor
        r = sch.components.add(
            lib_id="Device:R", reference="R1", value="1k", position=(100.0, 100.0), rotation=0
        )

        # Shunt capacitor
        c = sch.components.add(
            lib_id="Device:C", reference="C1", value="100nF", position=(150.0, 100.0), rotation=90
        )

        logger.info("RC filter created: R1 in series, C1 to ground")
        return sch

    @pytest.fixture
    def multi_stage_amplifier_schematic(self):
        """
        Fixture: Multi-stage amplifier circuit (simplified).

        Components:
          - Input coupling capacitor
          - Two-stage transistor amplifier
          - Output coupling capacitor
          - Biasing resistors

        Use for: Testing complex pin routing in larger circuits
        """
        logger.info("Creating multi_stage_amplifier_schematic fixture")
        sch = ksa.create_schematic("Multi-Stage Amplifier")

        # Input stage
        cin = sch.components.add(
            lib_id="Device:C", reference="C_in", value="10uF", position=(50.0, 100.0)
        )

        # First stage transistor (simplified with resistor for testing)
        r1 = sch.components.add(
            lib_id="Device:R", reference="R_load1", value="10k", position=(100.0, 50.0)
        )

        # Second stage
        r2 = sch.components.add(
            lib_id="Device:R", reference="R_load2", value="10k", position=(150.0, 50.0)
        )

        # Output stage
        cout = sch.components.add(
            lib_id="Device:C", reference="C_out", value="10uF", position=(200.0, 100.0)
        )

        logger.info("Multi-stage amplifier created with 4 components")
        return sch

    def test_using_voltage_divider(self, voltage_divider_schematic):
        """Example: Using complex circuit fixture."""
        assert len(voltage_divider_schematic.components) == 4

        r1 = voltage_divider_schematic.components.get("R1")
        r2 = voltage_divider_schematic.components.get("R2")

        assert r1 is not None
        assert r2 is not None

        # Test pin positions
        r1_pin1 = r1.get_pin_position("1")
        r2_pin2 = r2.get_pin_position("2")

        assert r1_pin1 is not None
        assert r2_pin2 is not None


# ============================================================================
# FILE MANAGEMENT FIXTURES
# ============================================================================


class TestFileFixtures:
    """Fixtures for temporary file handling."""

    @pytest.fixture
    def temp_schematic_file(self):
        """
        Fixture: Create temporary schematic file with automatic cleanup.

        Scope: Function
        Cleanup: Automatically deleted after test

        Usage:
            def test_save_load(temp_schematic_file):
                sch.save(temp_schematic_file)
                sch2 = ksa.Schematic.load(temp_schematic_file)
        """
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as f:
            temp_path = f.name

        logger.info(f"Created temporary file: {temp_path}")

        yield temp_path  # Provide to test

        # Cleanup
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info(f"Cleaned up: {temp_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {temp_path}: {e}")

    @pytest.fixture
    def temp_directory(self):
        """
        Fixture: Create temporary directory for test files.

        Scope: Function
        Cleanup: Entire directory deleted after test
        """
        temp_dir = tempfile.mkdtemp(prefix="kicad_test_")
        logger.info(f"Created temporary directory: {temp_dir}")

        yield temp_dir

        # Cleanup
        try:
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {temp_dir}: {e}")

    def test_using_temp_file(self, temp_schematic_file, single_resistor_schematic):
        """Example: Using temporary file fixture."""
        # Save schematic to temp file
        single_resistor_schematic.save(temp_schematic_file)

        # Verify file exists
        assert os.path.exists(temp_schematic_file)

        # Load and verify
        sch2 = ksa.Schematic.load(temp_schematic_file)
        assert len(sch2.components) == 1


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================


class TestDataFixtures:
    """Fixtures providing test data and expected values."""

    @pytest.fixture
    def standard_resistor_values(self):
        """
        Fixture: Common resistor values for testing.

        Returns list of (value_str, numeric_value) tuples
        """
        return [
            ("1k", 1000),
            ("10k", 10000),
            ("100k", 100000),
            ("1M", 1000000),
            ("1.5k", 1500),
            ("47k", 47000),
        ]

    @pytest.fixture
    def component_positions(self):
        """
        Fixture: Standard test positions.

        Returns dict of position names and coordinates
        """
        return {
            "origin": (0.0, 0.0),
            "near_origin": (10.0, 10.0),
            "standard": (100.0, 100.0),
            "large": (500.0, 500.0),
            "grid_aligned": (25.4, 25.4),  # 10 x 10 mil grid
        }

    @pytest.fixture
    def pin_spacing_data(self):
        """
        Fixture: Expected pin spacings for standard components.

        Returns dict mapping component library IDs to pin distances (mm)
        """
        return {
            "Device:R": 3.81,  # Resistor pins 3.81mm apart
            "Device:C": 3.81,  # Capacitor pins 3.81mm apart
            "Device:D": 3.81,  # Diode pins 3.81mm apart
            "Device:L": 3.81,  # Inductor pins 3.81mm apart
        }

    def test_using_test_data_fixtures(
        self, standard_resistor_values, component_positions, pin_spacing_data
    ):
        """Example: Using test data fixtures."""
        # Use resistor values
        sch = ksa.create_schematic("Data Test")

        for value_str, numeric_val in standard_resistor_values:
            r = sch.components.add(
                lib_id="Device:R",
                reference=f"R_{numeric_val}",
                value=value_str,
                position=component_positions["standard"],
            )
            assert r.value == value_str

        # Verify pin spacing
        expected_spacing = pin_spacing_data["Device:R"]
        assert expected_spacing == 3.81


# ============================================================================
# FIXTURE COMPOSITION
# ============================================================================


class TestFixtureComposition:
    """Examples of using multiple fixtures together."""

    @pytest.fixture
    def configured_test_environment(self, empty_schematic, resistor_factory, temp_schematic_file):
        """
        Fixture: Compose multiple fixtures for complete test environment.

        Combines:
          - Empty schematic
          - Resistor factory
          - Temporary file for persistence

        Returns tuple of (schematic, factory, filepath)
        """
        logger.info("Setting up complete test environment")
        return empty_schematic, resistor_factory, temp_schematic_file

    def test_using_composed_fixtures(self, configured_test_environment):
        """Example: Using composed fixtures."""
        sch, r_factory, temp_file = configured_test_environment

        # Create components
        r1 = r_factory(sch, "R1", "10k", (100, 100), 0)
        r2 = r_factory(sch, "R2", "20k", (150, 100), 90)

        # Save
        sch.save(temp_file)

        # Load and verify
        sch2 = ksa.Schematic.load(temp_file)
        assert len(sch2.components) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
