"""Electrical Rule Check (ERC) functionality using kicad-cli."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from kicad_sch_api.cli.base import KiCadExecutor
from kicad_sch_api.cli.types import ErcFormat, ErcSeverity, Units


@dataclass
class ErcViolation:
    """Represents a single ERC violation."""

    severity: str
    type: str
    description: str
    sheet: str
    position: Optional[Dict[str, float]] = None


@dataclass
class ErcReport:
    """ERC report with violations and summary."""

    violations: List[ErcViolation]
    error_count: int
    warning_count: int
    exclusion_count: int
    schematic_path: Path
    raw_output: str

    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return self.error_count > 0

    def has_warnings(self) -> bool:
        """Check if report contains any warnings."""
        return self.warning_count > 0

    def has_violations(self) -> bool:
        """Check if report contains any violations."""
        return len(self.violations) > 0

    def get_errors(self) -> List[ErcViolation]:
        """Get all error-level violations."""
        return [v for v in self.violations if v.severity == "error"]

    def get_warnings(self) -> List[ErcViolation]:
        """Get all warning-level violations."""
        return [v for v in self.violations if v.severity == "warning"]


def run_erc(
    schematic_path: Path,
    output_path: Optional[Path] = None,
    format: ErcFormat = "json",
    severity: ErcSeverity = "all",
    units: Units = "mm",
    exit_code_violations: bool = False,
    variables: Optional[Dict[str, str]] = None,
    executor: Optional[KiCadExecutor] = None,
) -> ErcReport:
    """
    Run Electrical Rule Check (ERC) on schematic using kicad-cli.

    Validates schematic for electrical errors like unconnected pins,
    conflicting drivers, etc.

    Args:
        schematic_path: Path to .kicad_sch file
        output_path: Output report path (auto-generated if None)
        format: Report format ('json' or 'report')
        severity: Severity levels to report ('all', 'error', 'warning', 'exclusions')
        units: Measurement units for coordinates ('mm', 'in', 'mils')
        exit_code_violations: Return non-zero exit code if violations exist
        variables: Project variables to override (key=value pairs)
        executor: Custom KiCadExecutor instance (creates default if None)

    Returns:
        ErcReport with violations and summary

    Raises:
        RuntimeError: If kicad-cli not found or ERC fails
        FileNotFoundError: If schematic file doesn't exist

    Example:
        >>> from pathlib import Path
        >>> report = run_erc(Path('circuit.kicad_sch'))
        >>> if report.has_errors():
        ...     print(f"Found {report.error_count} errors:")
        ...     for error in report.get_errors():
        ...         print(f"  - {error.description}")

        >>> # Check for specific severity
        >>> report = run_erc(
        ...     Path('circuit.kicad_sch'),
        ...     severity='error',  # Only errors
        ... )

        >>> # Generate human-readable report
        >>> report = run_erc(
        ...     Path('circuit.kicad_sch'),
        ...     format='report',
        ... )
        >>> print(report.raw_output)
    """
    schematic_path = Path(schematic_path)

    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")

    # Auto-generate output path if not provided
    if output_path is None:
        ext = ".json" if format == "json" else ".rpt"
        output_path = schematic_path.with_stem(f"{schematic_path.stem}_erc").with_suffix(ext)
    else:
        output_path = Path(output_path)

    # Create executor if not provided
    if executor is None:
        executor = KiCadExecutor()

    # Build command
    args = [
        "sch",
        "erc",
        "--output",
        str(output_path),
        "--format",
        format,
        "--units",
        units,
    ]

    # Add severity flags
    if severity == "all":
        args.append("--severity-all")
    elif severity == "error":
        args.append("--severity-error")
    elif severity == "warning":
        args.append("--severity-warning")
    elif severity == "exclusions":
        args.append("--severity-exclusions")

    # Add optional parameters
    if exit_code_violations:
        args.append("--exit-code-violations")

    if variables:
        for key, value in variables.items():
            args.extend(["--define-var", f"{key}={value}"])

    # Add schematic path
    args.append(str(schematic_path))

    # Execute command (don't check return code if exit_code_violations is True)
    result = executor.run(args, cwd=schematic_path.parent, check=not exit_code_violations)

    # Read output file
    output_content = output_path.read_text()

    # Parse report
    if format == "json":
        report = _parse_json_report(output_content, schematic_path)
    else:
        report = _parse_text_report(output_content, schematic_path)

    return report


def _parse_json_report(content: str, schematic_path: Path) -> ErcReport:
    """Parse JSON ERC report."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # If JSON parsing fails, return empty report
        return ErcReport(
            violations=[],
            error_count=0,
            warning_count=0,
            exclusion_count=0,
            schematic_path=schematic_path,
            raw_output=content,
        )

    violations = []
    error_count = 0
    warning_count = 0
    exclusion_count = 0

    # Parse violations from JSON
    for violation_data in data.get("violations", []):
        violation = ErcViolation(
            severity=violation_data.get("severity", "unknown"),
            type=violation_data.get("type", "unknown"),
            description=violation_data.get("description", ""),
            sheet=violation_data.get("sheet", ""),
            position=violation_data.get("position"),
        )
        violations.append(violation)

        if violation.severity == "error":
            error_count += 1
        elif violation.severity == "warning":
            warning_count += 1
        elif violation.severity == "exclusion":
            exclusion_count += 1

    return ErcReport(
        violations=violations,
        error_count=error_count,
        warning_count=warning_count,
        exclusion_count=exclusion_count,
        schematic_path=schematic_path,
        raw_output=content,
    )


def _parse_text_report(content: str, schematic_path: Path) -> ErcReport:
    """Parse text ERC report."""
    # For text reports, do simple counting
    lines = content.split("\n")
    error_count = sum(1 for line in lines if "error" in line.lower())
    warning_count = sum(1 for line in lines if "warning" in line.lower())

    return ErcReport(
        violations=[],  # Text format doesn't provide structured violations
        error_count=error_count,
        warning_count=warning_count,
        exclusion_count=0,
        schematic_path=schematic_path,
        raw_output=content,
    )
