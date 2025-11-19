"""BOM property auditing and management."""

import csv
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

from ..core.schematic import Schematic
from .matcher import PropertyMatcher


@dataclass
class ComponentIssue:
    """Component with missing properties."""
    schematic: str
    reference: str
    value: str
    footprint: str
    lib_id: str
    missing_properties: List[str]
    existing_properties: Dict[str, str]


class BOMPropertyAuditor:
    """Audit and manage BOM properties in KiCad schematics.

    This class provides methods to:
    - Find components missing required properties
    - Bulk update properties based on match criteria
    - Transform/copy properties between fields
    - Generate CSV reports

    Example:
        >>> auditor = BOMPropertyAuditor()
        >>> issues = auditor.audit_directory(
        ...     Path("~/designs"),
        ...     required_properties=["PartNumber", "Manufacturer"]
        ... )
        >>> auditor.generate_csv_report(issues, Path("report.csv"))
    """

    def audit_schematic(
        self,
        schematic_path: Path,
        required_properties: List[str],
        exclude_dnp: bool = False
    ) -> List[ComponentIssue]:
        """Audit single schematic for missing properties.

        Args:
            schematic_path: Path to .kicad_sch file
            required_properties: List of property names to check for
            exclude_dnp: Skip components marked "Do Not Populate"

        Returns:
            List of components with missing properties
        """
        issues = []

        try:
            sch = Schematic.load(str(schematic_path))

            for component in sch.components.all():
                if exclude_dnp and not component.in_bom:
                    continue

                # Check which required properties are missing
                missing = []
                for prop in required_properties:
                    if not component.get_property(prop):
                        missing.append(prop)

                # If any properties missing, record the issue
                if missing:
                    issues.append(ComponentIssue(
                        schematic=str(schematic_path),
                        reference=component.reference,
                        value=component.value,
                        footprint=component.footprint or "",
                        lib_id=component.lib_id,
                        missing_properties=missing,
                        existing_properties=dict(component.properties)
                    ))

        except Exception as e:
            print(f"ERROR loading {schematic_path}: {e}")

        return issues

    def audit_directory(
        self,
        directory: Path,
        required_properties: List[str],
        recursive: bool = True,
        exclude_dnp: bool = False
    ) -> List[ComponentIssue]:
        """Scan directory for schematics and audit all.

        Args:
            directory: Directory to scan
            required_properties: Properties to check for
            recursive: Scan subdirectories
            exclude_dnp: Skip DNP components

        Returns:
            List of all issues found across all schematics
        """
        all_issues = []

        # Find all .kicad_sch files
        if recursive:
            schematic_files = list(directory.rglob("*.kicad_sch"))
        else:
            schematic_files = list(directory.glob("*.kicad_sch"))

        # Audit each schematic
        for sch_file in schematic_files:
            issues = self.audit_schematic(sch_file, required_properties, exclude_dnp)
            all_issues.extend(issues)

        return all_issues

    def generate_csv_report(
        self,
        issues: List[ComponentIssue],
        output_path: Path
    ) -> None:
        """Generate CSV report from audit results.

        Args:
            issues: List of component issues
            output_path: Where to write CSV file
        """
        if not issues:
            return

        # Collect all property names that exist across components
        all_property_names = set()
        for issue in issues:
            all_property_names.update(issue.existing_properties.keys())

        # Create CSV with dynamic columns
        fieldnames = [
            "Schematic",
            "Reference",
            "Value",
            "Footprint",
            "LibID",
            "MissingProperties",
        ]

        # Add common properties as columns
        common_props = ["Tolerance", "Manufacturer", "MPN", "Datasheet", "Description"]
        for prop in common_props:
            if prop in all_property_names:
                fieldnames.append(prop)

        # Write CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for issue in issues:
                row = {
                    "Schematic": issue.schematic,
                    "Reference": issue.reference,
                    "Value": issue.value,
                    "Footprint": issue.footprint,
                    "LibID": issue.lib_id,
                    "MissingProperties": ", ".join(issue.missing_properties),
                }

                # Add existing properties
                for prop in common_props:
                    if prop in fieldnames:
                        prop_value = issue.existing_properties.get(prop, "")
                        if isinstance(prop_value, dict):
                            prop_value = prop_value.get('value', str(prop_value))
                        row[prop] = prop_value

                writer.writerow(row)

    def update_properties(
        self,
        directory: Path,
        match_criteria: Dict[str, str],
        property_updates: Dict[str, str],
        dry_run: bool = False,
        recursive: bool = True,
        exclude_dnp: bool = False
    ) -> int:
        """Bulk update properties on matching components.

        Args:
            directory: Directory containing schematics
            match_criteria: Component match criteria (field->pattern)
            property_updates: Properties to set (name->value)
            dry_run: If True, don't actually save changes
            recursive: Scan subdirectories
            exclude_dnp: Skip DNP components

        Returns:
            Number of components updated
        """
        # Find all schematics
        if recursive:
            schematic_files = list(directory.rglob("*.kicad_sch"))
        else:
            schematic_files = list(directory.glob("*.kicad_sch"))

        updated_count = 0

        for sch_path in schematic_files:
            try:
                sch = Schematic.load(str(sch_path))
                sch_modified = False

                for component in sch.components.all():
                    if exclude_dnp and not component.in_bom:
                        continue

                    if PropertyMatcher.matches(component, match_criteria):
                        for prop_name, prop_value in property_updates.items():
                            if not dry_run:
                                component.set_property(prop_name, prop_value)
                            sch_modified = True
                            updated_count += 1

                if sch_modified and not dry_run:
                    sch.save(str(sch_path))

            except Exception as e:
                print(f"ERROR updating {sch_path}: {e}")

        return updated_count

    def transform_properties(
        self,
        directory: Path,
        transformations: List[Tuple[str, str]],
        only_if_empty: bool = False,
        dry_run: bool = False,
        recursive: bool = True,
        exclude_dnp: bool = False
    ) -> int:
        """Copy/rename properties on components.

        Args:
            directory: Directory containing schematics
            transformations: List of (source_prop, dest_prop) tuples
            only_if_empty: Only copy if destination is empty
            dry_run: Don't actually save changes
            recursive: Scan subdirectories
            exclude_dnp: Skip DNP components

        Returns:
            Number of components updated
        """
        # Find all schematics
        if recursive:
            schematic_files = list(directory.rglob("*.kicad_sch"))
        else:
            schematic_files = list(directory.glob("*.kicad_sch"))

        updated_count = 0

        for sch_path in schematic_files:
            try:
                sch = Schematic.load(str(sch_path))
                sch_modified = False

                for component in sch.components.all():
                    if exclude_dnp and not component.in_bom:
                        continue

                    for from_prop, to_prop in transformations:
                        source_value = component.get_property(from_prop)
                        dest_value = component.get_property(to_prop)

                        if not source_value:
                            continue  # Nothing to copy

                        if only_if_empty and dest_value:
                            continue  # Destination already has value

                        if not dry_run:
                            component.set_property(to_prop, source_value)
                        sch_modified = True
                        updated_count += 1

                if sch_modified and not dry_run:
                    sch.save(str(sch_path))

            except Exception as e:
                print(f"ERROR transforming {sch_path}: {e}")

        return updated_count
