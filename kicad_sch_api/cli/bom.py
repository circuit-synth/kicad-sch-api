"""Bill of Materials (BOM) export functionality using kicad-cli."""

from pathlib import Path
from typing import List, Optional

from kicad_sch_api.cli.base import KiCadExecutor


def export_bom(
    schematic_path: Path,
    output_path: Optional[Path] = None,
    preset: Optional[str] = None,
    format_preset: Optional[str] = None,
    fields: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    group_by: Optional[List[str]] = None,
    sort_field: str = "Reference",
    sort_asc: bool = True,
    filter: Optional[str] = None,
    exclude_dnp: bool = False,
    include_excluded_from_bom: bool = False,
    field_delimiter: str = ",",
    string_delimiter: str = '"',
    ref_delimiter: str = ",",
    ref_range_delimiter: str = "",
    keep_tabs: bool = False,
    keep_line_breaks: bool = False,
    executor: Optional[KiCadExecutor] = None,
) -> Path:
    """
    Export Bill of Materials (BOM) from schematic using kicad-cli.

    Generates a CSV file with component information, suitable for manufacturing
    and procurement.

    Args:
        schematic_path: Path to .kicad_sch file
        output_path: Output BOM path (auto-generated if None)
        preset: Named BOM preset from schematic (e.g., "Grouped By Value")
        format_preset: Named BOM format preset (e.g., "CSV")
        fields: List of fields to export (default: Reference, Value, Footprint, Qty, DNP)
        labels: List of labels for exported fields
        group_by: Fields to group references by when values match
        sort_field: Field name to sort by (default: "Reference")
        sort_asc: Sort ascending (True) or descending (False)
        filter: Filter string to remove output lines
        exclude_dnp: Exclude components marked Do-Not-Populate
        include_excluded_from_bom: Include components marked 'Exclude from BOM'
        field_delimiter: Separator between fields/columns (default: ",")
        string_delimiter: Character to surround fields with (default: '"')
        ref_delimiter: Character between individual references (default: ",")
        ref_range_delimiter: Character for reference ranges (default: "", use "-" for ranges like "R1-R5")
        keep_tabs: Keep tab characters from input fields
        keep_line_breaks: Keep line break characters from input fields
        executor: Custom KiCadExecutor instance (creates default if None)

    Returns:
        Path to generated BOM file

    Raises:
        RuntimeError: If kicad-cli not found or BOM generation fails
        FileNotFoundError: If schematic file doesn't exist

    Example:
        >>> from pathlib import Path
        >>> bom = export_bom(
        ...     Path('circuit.kicad_sch'),
        ...     fields=['Reference', 'Value', 'Footprint', 'MPN'],
        ...     group_by=['Value', 'Footprint'],
        ...     exclude_dnp=True,
        ... )
        >>> print(f"BOM: {bom}")

    Common use cases:
        # Simple BOM with default fields
        >>> export_bom(Path('circuit.kicad_sch'))

        # Manufacturing BOM (exclude DNP, group by value)
        >>> export_bom(
        ...     Path('circuit.kicad_sch'),
        ...     group_by=['Value', 'Footprint'],
        ...     exclude_dnp=True,
        ... )

        # BOM with manufacturer part numbers
        >>> export_bom(
        ...     Path('circuit.kicad_sch'),
        ...     fields=['Reference', 'Value', 'Footprint', 'MPN', 'Manufacturer'],
        ...     group_by=['MPN'],
        ... )
    """
    schematic_path = Path(schematic_path)

    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")

    # Auto-generate output path if not provided
    if output_path is None:
        output_path = schematic_path.with_suffix(".csv")
    else:
        output_path = Path(output_path)

    # Create executor if not provided
    if executor is None:
        executor = KiCadExecutor()

    # Build command
    args = [
        "sch",
        "export",
        "bom",
        "--output",
        str(output_path),
    ]

    # Add optional parameters
    if preset:
        args.extend(["--preset", preset])

    if format_preset:
        args.extend(["--format-preset", format_preset])

    if fields:
        args.extend(["--fields", ",".join(fields)])

    if labels:
        args.extend(["--labels", ",".join(labels)])

    if group_by:
        args.extend(["--group-by", ",".join(group_by)])

    if sort_field:
        args.extend(["--sort-field", sort_field])

    if sort_asc:
        args.append("--sort-asc")

    if filter:
        args.extend(["--filter", filter])

    if exclude_dnp:
        args.append("--exclude-dnp")

    if include_excluded_from_bom:
        args.append("--include-excluded-from-bom")

    # Delimiter options
    args.extend(["--field-delimiter", field_delimiter])
    args.extend(["--string-delimiter", string_delimiter])
    args.extend(["--ref-delimiter", ref_delimiter])

    if ref_range_delimiter:
        args.extend(["--ref-range-delimiter", ref_range_delimiter])

    if keep_tabs:
        args.append("--keep-tabs")

    if keep_line_breaks:
        args.append("--keep-line-breaks")

    # Add schematic path
    args.append(str(schematic_path))

    # Execute command
    executor.run(args, cwd=schematic_path.parent)

    return output_path
