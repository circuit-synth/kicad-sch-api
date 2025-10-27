"""Document export functionality (PDF, SVG, DXF) using kicad-cli."""

from pathlib import Path
from typing import Dict, List, Optional

from kicad_sch_api.cli.base import KiCadExecutor


def export_pdf(
    schematic_path: Path,
    output_path: Optional[Path] = None,
    theme: Optional[str] = None,
    black_and_white: bool = False,
    drawing_sheet: Optional[Path] = None,
    exclude_drawing_sheet: bool = False,
    default_font: str = "KiCad Font",
    exclude_pdf_property_popups: bool = False,
    exclude_pdf_hierarchical_links: bool = False,
    exclude_pdf_metadata: bool = False,
    no_background_color: bool = False,
    pages: Optional[List[int]] = None,
    variables: Optional[Dict[str, str]] = None,
    executor: Optional[KiCadExecutor] = None,
) -> Path:
    """
    Export schematic as PDF using kicad-cli.

    Args:
        schematic_path: Path to .kicad_sch file
        output_path: Output PDF path (auto-generated if None)
        theme: Color theme to use (default: schematic settings)
        black_and_white: Export in black and white
        drawing_sheet: Path to custom drawing sheet
        exclude_drawing_sheet: Don't include drawing sheet
        default_font: Default font name (default: "KiCad Font")
        exclude_pdf_property_popups: Don't generate property popups
        exclude_pdf_hierarchical_links: Don't generate clickable hierarchical links
        exclude_pdf_metadata: Don't generate PDF metadata from variables
        no_background_color: Don't set background color
        pages: List of page numbers to export (None = all pages)
        variables: Project variables to override
        executor: Custom KiCadExecutor instance

    Returns:
        Path to generated PDF file

    Example:
        >>> from pathlib import Path
        >>> pdf = export_pdf(
        ...     Path('circuit.kicad_sch'),
        ...     theme='KiCad Classic',
        ... )
    """
    schematic_path = Path(schematic_path)

    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")

    if output_path is None:
        output_path = schematic_path.with_suffix(".pdf")
    else:
        output_path = Path(output_path)

    if executor is None:
        executor = KiCadExecutor()

    # Build command
    args = ["sch", "export", "pdf", "--output", str(output_path)]

    if theme:
        args.extend(["--theme", theme])

    if black_and_white:
        args.append("--black-and-white")

    if drawing_sheet:
        args.extend(["--drawing-sheet", str(drawing_sheet)])

    if exclude_drawing_sheet:
        args.append("--exclude-drawing-sheet")

    args.extend(["--default-font", default_font])

    if exclude_pdf_property_popups:
        args.append("--exclude-pdf-property-popups")

    if exclude_pdf_hierarchical_links:
        args.append("--exclude-pdf-hierarchical-links")

    if exclude_pdf_metadata:
        args.append("--exclude-pdf-metadata")

    if no_background_color:
        args.append("--no-background-color")

    if pages:
        args.extend(["--pages", ",".join(map(str, pages))])

    if variables:
        for key, value in variables.items():
            args.extend(["--define-var", f"{key}={value}"])

    args.append(str(schematic_path))

    # Execute command
    executor.run(args, cwd=schematic_path.parent)

    return output_path


def export_svg(
    schematic_path: Path,
    output_dir: Optional[Path] = None,
    theme: Optional[str] = None,
    black_and_white: bool = False,
    drawing_sheet: Optional[Path] = None,
    exclude_drawing_sheet: bool = False,
    default_font: str = "KiCad Font",
    no_background_color: bool = False,
    pages: Optional[List[int]] = None,
    variables: Optional[Dict[str, str]] = None,
    executor: Optional[KiCadExecutor] = None,
) -> List[Path]:
    """
    Export schematic as SVG using kicad-cli.

    Args:
        schematic_path: Path to .kicad_sch file
        output_dir: Output directory (default: schematic directory)
        theme: Color theme to use (default: schematic settings)
        black_and_white: Export in black and white
        drawing_sheet: Path to custom drawing sheet
        exclude_drawing_sheet: Don't include drawing sheet
        default_font: Default font name (default: "KiCad Font")
        no_background_color: Don't set background color
        pages: List of page numbers to export (None = all pages)
        variables: Project variables to override
        executor: Custom KiCadExecutor instance

    Returns:
        List of paths to generated SVG files

    Example:
        >>> from pathlib import Path
        >>> svgs = export_svg(
        ...     Path('circuit.kicad_sch'),
        ...     theme='KiCad Classic',
        ... )
        >>> for svg in svgs:
        ...     print(f"Generated: {svg}")
    """
    schematic_path = Path(schematic_path)

    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")

    if output_dir is None:
        output_dir = schematic_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    if executor is None:
        executor = KiCadExecutor()

    # Build command
    args = ["sch", "export", "svg", "--output", str(output_dir)]

    if theme:
        args.extend(["--theme", theme])

    if black_and_white:
        args.append("--black-and-white")

    if drawing_sheet:
        args.extend(["--drawing-sheet", str(drawing_sheet)])

    if exclude_drawing_sheet:
        args.append("--exclude-drawing-sheet")

    args.extend(["--default-font", default_font])

    if no_background_color:
        args.append("--no-background-color")

    if pages:
        args.extend(["--pages", ",".join(map(str, pages))])

    if variables:
        for key, value in variables.items():
            args.extend(["--define-var", f"{key}={value}"])

    args.append(str(schematic_path))

    # Execute command
    executor.run(args, cwd=schematic_path.parent)

    # Find generated SVG files
    svg_files = list(output_dir.glob(f"{schematic_path.stem}*.svg"))

    return svg_files


def export_dxf(
    schematic_path: Path,
    output_dir: Optional[Path] = None,
    theme: Optional[str] = None,
    black_and_white: bool = False,
    drawing_sheet: Optional[Path] = None,
    exclude_drawing_sheet: bool = False,
    default_font: str = "KiCad Font",
    no_background_color: bool = False,
    pages: Optional[List[int]] = None,
    variables: Optional[Dict[str, str]] = None,
    executor: Optional[KiCadExecutor] = None,
) -> List[Path]:
    """
    Export schematic as DXF using kicad-cli.

    Args:
        schematic_path: Path to .kicad_sch file
        output_dir: Output directory (default: schematic directory)
        theme: Color theme to use (default: schematic settings)
        black_and_white: Export in black and white
        drawing_sheet: Path to custom drawing sheet
        exclude_drawing_sheet: Don't include drawing sheet
        default_font: Default font name (default: "KiCad Font")
        no_background_color: Don't set background color
        pages: List of page numbers to export (None = all pages)
        variables: Project variables to override
        executor: Custom KiCadExecutor instance

    Returns:
        List of paths to generated DXF files

    Example:
        >>> from pathlib import Path
        >>> dxfs = export_dxf(Path('circuit.kicad_sch'))
    """
    schematic_path = Path(schematic_path)

    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")

    if output_dir is None:
        output_dir = schematic_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    if executor is None:
        executor = KiCadExecutor()

    # Build command
    args = ["sch", "export", "dxf", "--output", str(output_dir)]

    if theme:
        args.extend(["--theme", theme])

    if black_and_white:
        args.append("--black-and-white")

    if drawing_sheet:
        args.extend(["--drawing-sheet", str(drawing_sheet)])

    if exclude_drawing_sheet:
        args.append("--exclude-drawing-sheet")

    args.extend(["--default-font", default_font])

    if no_background_color:
        args.append("--no-background-color")

    if pages:
        args.extend(["--pages", ",".join(map(str, pages))])

    if variables:
        for key, value in variables.items():
            args.extend(["--define-var", f"{key}={value}"])

    args.append(str(schematic_path))

    # Execute command
    executor.run(args, cwd=schematic_path.parent)

    # Find generated DXF files
    dxf_files = list(output_dir.glob(f"{schematic_path.stem}*.dxf"))

    return dxf_files
