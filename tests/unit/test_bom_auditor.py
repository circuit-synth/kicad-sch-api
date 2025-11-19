#!/usr/bin/env python3
"""
Tests for BOM property auditor.

Tests audit, update, and transform functionality.
"""

import sys
from pathlib import Path

import pytest

# Add kicad-sch-api to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent)
)

import kicad_sch_api as ksa
from kicad_sch_api.bom.auditor import BOMPropertyAuditor, ComponentIssue
from kicad_sch_api.bom.matcher import PropertyMatcher


def get_property_value(component, prop_name):
    """Helper to extract property value, handling both str and dict returns."""
    prop = component.get_property(prop_name)
    if prop is None:
        return None
    if isinstance(prop, dict):
        return prop.get("value")
    return prop


@pytest.fixture
def test_fixtures_dir(tmp_path):
    """Create test fixtures on-the-fly for each test."""
    fixtures_dir = tmp_path / "bom_test"
    fixtures_dir.mkdir()

    # 1. Perfect compliance schematic (all have PartNumber)
    perfect = ksa.create_schematic("PerfectCompliance")
    r1 = perfect.components.add("Device:R", "R1", "10k", position=(100, 100))
    r1.set_property("PartNumber", "RC0805FR-0710KL")
    r1.set_property("Manufacturer", "Yageo")
    perfect.save(str(fixtures_dir / "perfect.kicad_sch"))

    # 2. No compliance schematic (none have PartNumber)
    missing = ksa.create_schematic("MissingPartNumbers")
    missing.components.add("Device:R", "R1", "10k", position=(100, 100))
    missing.components.add("Device:R", "R2", "100k", position=(100, 120))
    missing.components.add("Device:C", "C1", "100nF", position=(120, 100))
    missing.save(str(fixtures_dir / "missing.kicad_sch"))

    # 3. Mixed compliance (some have, some don't)
    mixed = ksa.create_schematic("MixedCompliance")
    r1 = mixed.components.add("Device:R", "R1", "10k", position=(100, 100))
    r1.set_property("PartNumber", "RC0805FR-0710KL")
    mixed.components.add("Device:R", "R2", "100k", position=(100, 120))  # No PartNumber
    c1 = mixed.components.add("Device:C", "C1", "100nF", position=(120, 100))
    c1.set_property("PartNumber", "GRM123456")
    mixed.save(str(fixtures_dir / "mixed.kicad_sch"))

    # 4. Test with MPN property (for transform tests)
    with_mpn = ksa.create_schematic("WithMPN")
    r1 = with_mpn.components.add("Device:R", "R1", "10k", position=(100, 100))
    r1.set_property("MPN", "MPN123")  # Has MPN but not PartNumber
    with_mpn.save(str(fixtures_dir / "with_mpn.kicad_sch"))

    # 5. DNP component test
    with_dnp = ksa.create_schematic("WithDNP")
    r1 = with_dnp.components.add("Device:R", "R1", "10k", position=(100, 100))
    r1.set_property("PartNumber", "RC0805FR-0710KL")
    r2 = with_dnp.components.add("Device:R", "R2", "100k", position=(100, 120))
    r2.set_property("dnp", "1")  # DNP component without PartNumber
    with_dnp.save(str(fixtures_dir / "with_dnp.kicad_sch"))

    return fixtures_dir


class TestPropertyMatcher:
    """Test property matching logic."""

    def test_parse_criteria(self):
        """Should parse criteria string correctly."""
        criteria = PropertyMatcher.parse_criteria("value=10k,footprint=*0805*")
        assert criteria == {"value": "10k", "footprint": "*0805*"}

    def test_parse_empty_criteria(self):
        """Should handle empty criteria."""
        criteria = PropertyMatcher.parse_criteria("")
        assert criteria == {}

    def test_exact_match(self, test_fixtures_dir):
        """Should match exact values."""
        sch = ksa.Schematic.load(str(test_fixtures_dir / "perfect.kicad_sch"))
        comp = next(sch.components)

        assert PropertyMatcher.matches(comp, {"value": "10k"}) is True
        assert PropertyMatcher.matches(comp, {"value": "100k"}) is False

    def test_wildcard_match(self, test_fixtures_dir):
        """Should match wildcards."""
        sch = ksa.Schematic.load(str(test_fixtures_dir / "perfect.kicad_sch"))
        comp = next(sch.components)

        assert PropertyMatcher.matches(comp, {"reference": "R*"}) is True
        assert PropertyMatcher.matches(comp, {"reference": "C*"}) is False

    def test_empty_property_match(self, test_fixtures_dir):
        """Should match empty/missing properties."""
        sch = ksa.Schematic.load(str(test_fixtures_dir / "missing.kicad_sch"))
        comp = next(sch.components)

        assert PropertyMatcher.matches(comp, {"PartNumber": ""}) is True

    def test_multiple_criteria_and_logic(self, test_fixtures_dir):
        """Multiple criteria should use AND logic."""
        sch = ksa.Schematic.load(str(test_fixtures_dir / "perfect.kicad_sch"))
        comp = next(sch.components)

        # Both match
        assert PropertyMatcher.matches(comp, {"value": "10k", "reference": "R1"}) is True
        # Only one matches
        assert PropertyMatcher.matches(comp, {"value": "10k", "reference": "R2"}) is False


class TestAuditMode:
    """Test audit functionality."""

    def test_audit_finds_missing_partnumbers(self, test_fixtures_dir):
        """Should find all components missing PartNumber."""
        auditor = BOMPropertyAuditor()
        issues = auditor.audit_directory(
            test_fixtures_dir, required_properties=["PartNumber"], recursive=False
        )

        # Should find: 3 from missing.kicad_sch + 1 from mixed.kicad_sch + 1 from with_mpn.kicad_sch + 1 from with_dnp.kicad_sch = 6
        assert len(issues) >= 5

    def test_audit_perfect_compliance(self, test_fixtures_dir):
        """perfect.kicad_sch should have 0 issues."""
        auditor = BOMPropertyAuditor()
        issues = auditor.audit_schematic(
            test_fixtures_dir / "perfect.kicad_sch", required_properties=["PartNumber"]
        )

        assert len(issues) == 0

    def test_audit_all_missing(self, test_fixtures_dir):
        """missing.kicad_sch should have 3 missing PartNumbers."""
        auditor = BOMPropertyAuditor()
        issues = auditor.audit_schematic(
            test_fixtures_dir / "missing.kicad_sch", required_properties=["PartNumber"]
        )

        assert len(issues) == 3

    def test_audit_exclude_dnp(self, test_fixtures_dir):
        """Should exclude DNP components when requested."""
        auditor = BOMPropertyAuditor()

        # Without exclude_dnp
        issues_with_dnp = auditor.audit_schematic(
            test_fixtures_dir / "with_dnp.kicad_sch",
            required_properties=["PartNumber"],
            exclude_dnp=False,
        )

        # With exclude_dnp
        issues_without_dnp = auditor.audit_schematic(
            test_fixtures_dir / "with_dnp.kicad_sch",
            required_properties=["PartNumber"],
            exclude_dnp=True,
        )

        # Should find DNP component without exclude flag
        assert len(issues_with_dnp) > len(issues_without_dnp)

    def test_generate_csv_report(self, test_fixtures_dir, tmp_path):
        """Should generate CSV report."""
        auditor = BOMPropertyAuditor()
        issues = auditor.audit_directory(
            test_fixtures_dir, required_properties=["PartNumber"], recursive=False
        )

        report_path = tmp_path / "report.csv"
        auditor.generate_csv_report(issues, report_path)

        assert report_path.exists()

        # Verify CSV content
        content = report_path.read_text()
        assert "Schematic,Reference,Value,Footprint,LibID,MissingProperties" in content
        assert "R1" in content or "R2" in content


class TestUpdateMode:
    """Test bulk property update functionality."""

    def test_update_dry_run_shows_matches(self, test_fixtures_dir):
        """Dry run should show what would be updated without changing files."""
        auditor = BOMPropertyAuditor()

        count = auditor.update_properties(
            test_fixtures_dir,
            match_criteria={"value": "10k", "lib_id": "Device:R"},
            property_updates={"PartNumber": "TEST123"},
            dry_run=True,
            recursive=False,
        )

        # Should find all R1 resistors with 10k value
        assert count > 0

    def test_update_pattern_matching_wildcard(self, test_fixtures_dir):
        """Wildcard match should work with * patterns."""
        auditor = BOMPropertyAuditor()

        count = auditor.update_properties(
            test_fixtures_dir,
            match_criteria={"reference": "R*"},
            property_updates={"TestProp": "TestValue"},
            dry_run=True,
            recursive=False,
        )

        assert count > 0

    def test_update_multiple_properties(self, test_fixtures_dir):
        """Should be able to set multiple properties at once."""
        auditor = BOMPropertyAuditor()

        count = auditor.update_properties(
            test_fixtures_dir,
            match_criteria={"value": "10k"},
            property_updates={
                "PartNumber": "XXX",
                "Manufacturer": "YYY",
                "Tolerance": "1%",
            },
            dry_run=True,
            recursive=False,
        )

        assert count > 0

    def test_update_runs_successfully(self, test_fixtures_dir):
        """Update command should run without errors and actually update."""
        auditor = BOMPropertyAuditor()

        # Run update (not dry-run)
        count = auditor.update_properties(
            test_fixtures_dir,
            match_criteria={"reference": "R1", "value": "10k"},
            property_updates={"TestProperty": "TestValue123"},
            dry_run=False,
            recursive=False,
        )

        assert count > 0

        # Verify properties were actually updated
        sch = ksa.Schematic.load(str(test_fixtures_dir / "missing.kicad_sch"))
        for comp in sch.components:
            if comp.reference == "R1" and comp.value == "10k":
                assert get_property_value(comp, "TestProperty") == "TestValue123"


class TestTransformMode:
    """Test property copy/transform functionality."""

    def test_transform_runs_successfully(self, test_fixtures_dir):
        """Transform command should run without errors."""
        auditor = BOMPropertyAuditor()

        # Run transform to copy MPN to PartNumber
        count = auditor.transform_properties(
            test_fixtures_dir,
            transformations=[("MPN", "PartNumber")],
            only_if_empty=False,
            dry_run=False,
            recursive=False,
        )

        assert count > 0

        # Verify transformation happened
        sch = ksa.Schematic.load(str(test_fixtures_dir / "with_mpn.kicad_sch"))
        for comp in sch.components:
            if comp.reference == "R1":
                assert get_property_value(comp, "PartNumber") == "MPN123"

    def test_transform_only_if_empty_preserves_existing(self, test_fixtures_dir):
        """--only-if-empty should not overwrite existing properties."""
        # First set both MPN and PartNumber on a component
        test_sch = test_fixtures_dir / "mixed.kicad_sch"
        sch = ksa.Schematic.load(str(test_sch))

        for comp in sch.components:
            if comp.reference == "R1":
                comp.set_property("MPN", "NEW_MPN_VALUE")
                # R1 already has PartNumber set
                break

        sch.save(str(test_sch))

        # Run transform with only_if_empty
        auditor = BOMPropertyAuditor()
        count = auditor.transform_properties(
            test_fixtures_dir,
            transformations=[("MPN", "PartNumber")],
            only_if_empty=True,
            dry_run=False,
            recursive=False,
        )

        # Verify PartNumber was NOT overwritten
        sch = ksa.Schematic.load(str(test_sch))
        for comp in sch.components:
            if comp.reference == "R1":
                # Should still have original PartNumber
                assert get_property_value(comp, "PartNumber") == "RC0805FR-0710KL"
                assert get_property_value(comp, "MPN") == "NEW_MPN_VALUE"


class TestComponentIssue:
    """Test ComponentIssue dataclass."""

    def test_component_issue_creation(self, test_fixtures_dir):
        """Should create ComponentIssue with all fields."""
        auditor = BOMPropertyAuditor()
        issues = auditor.audit_schematic(
            test_fixtures_dir / "missing.kicad_sch", required_properties=["PartNumber"]
        )

        assert len(issues) > 0

        issue = issues[0]
        assert isinstance(issue, ComponentIssue)
        assert issue.schematic_path
        assert issue.reference
        assert issue.missing_properties == ["PartNumber"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
