"""
Pytest configuration and shared fixtures for kicad-sch-api tests.
"""

import logging
import tempfile
from pathlib import Path

import pytest

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Reduce noise from some modules during testing
logging.getLogger('kicad_sch_api.library.cache').setLevel(logging.WARNING)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_schematic_content():
    """Sample schematic content for testing."""
    return '''(kicad_sch (version 20250114) (generator "eeschema")
    (uuid "test-schematic-uuid-1234")
    (paper "A4")
    (title_block
        (title "Test Schematic")
        (date "2025-01-13")
        (rev "1.0")
        (company "Test Company")
    )
    (lib_symbols
        (symbol "Device:R" (pin_numbers hide) (pin_names (offset 0))
            (exclude_from_sim no) (in_bom yes) (on_board yes)
            (property "Reference" "R" (at 0 0 0)
                (effects (font (size 1.27 1.27)))
            )
            (property "Value" "R" (at 0 0 0)
                (effects (font (size 1.27 1.27)))
            )
            (property "Footprint" "" (at 0 0 0)
                (effects (font (size 1.27 1.27)) hide)
            )
            (symbol "Device:R_0_1"
                (rectangle (start -1.016 -2.54) (end 1.016 2.54)
                    (stroke (width 0.254) (type default))
                    (fill (type none))
                )
                (pin passive line (at 0 3.81 270) (length 1.27)
                    (name "~" (effects (font (size 1.27 1.27))))
                    (number "1" (effects (font (size 1.27 1.27))))
                )
                (pin passive line (at 0 -3.81 90) (length 1.27)
                    (name "~" (effects (font (size 1.27 1.27))))
                    (number "2" (effects (font (size 1.27 1.27))))
                )
            )
        )
        (symbol "Device:C" (pin_numbers hide) (pin_names (offset 0.254))
            (exclude_from_sim no) (in_bom yes) (on_board yes)
            (property "Reference" "C" (at 0.635 2.54 0)
                (effects (font (size 1.27 1.27)))
            )
            (property "Value" "C" (at 0.635 -2.54 0)
                (effects (font (size 1.27 1.27)))
            )
        )
    )
    (symbol (lib_id "Device:R") (at 127 95.25 0) (unit 1)
        (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
        (uuid "component-uuid-r1")
        (property "Reference" "R1" (at 127 91.44 0)
            (effects (font (size 1.27 1.27)))
        )
        (property "Value" "10k" (at 127 99.06 0)
            (effects (font (size 1.27 1.27)))
        )
        (property "Footprint" "" (at 125.73 95.25 90)
            (effects (font (size 1.27 1.27)) hide)
        )
        (property "Datasheet" "~" (at 127 95.25 0)
            (effects (font (size 1.27 1.27)) hide)
        )
        (pin "1" (uuid "pin-uuid-r1-1"))
        (pin "2" (uuid "pin-uuid-r1-2"))
        (instances
            (project "test-project"
                (path "/" (reference "R1") (unit 1))
            )
        )
    )
    (symbol_instances
        (path "/" (reference "R1") (unit 1))
    )
)'''


@pytest.fixture
def sample_schematic_file(temp_dir, sample_schematic_content):
    """Create a sample schematic file for testing."""
    sch_path = temp_dir / "sample.kicad_sch"
    with open(sch_path, 'w', encoding='utf-8') as f:
        f.write(sample_schematic_content)
    return sch_path


@pytest.fixture
def blank_schematic_content():
    """Minimal blank schematic content."""
    return '''(kicad_sch (version 20250114) (generator "eeschema")
    (uuid "blank-schematic-uuid")
    (paper "A4")
    (lib_symbols)
    (symbol_instances)
)'''


@pytest.fixture
def blank_schematic_file(temp_dir, blank_schematic_content):
    """Create a blank schematic file for testing."""
    sch_path = temp_dir / "blank.kicad_sch"
    with open(sch_path, 'w', encoding='utf-8') as f:
        f.write(blank_schematic_content)
    return sch_path


@pytest.fixture(autouse=True)
def reset_global_caches():
    """Reset global caches before each test."""
    # Reset symbol cache between tests
    from kicad_sch_api.library.cache import _global_cache
    if _global_cache:
        _global_cache.clear_cache()


class TestHelpers:
    """Helper methods for tests."""
    
    @staticmethod
    def assert_schematic_valid(sch):
        """Assert that schematic passes basic validation."""
        issues = sch.validate()
        errors = [issue for issue in issues if issue.level.value in ('error', 'critical')]
        if errors:
            error_messages = [str(error) for error in errors]
            pytest.fail(f"Schematic validation failed: {'; '.join(error_messages)}")
    
    @staticmethod
    def assert_file_contains_component(file_path, reference, lib_id=None, value=None):
        """Assert that file contains specified component."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert f'"Reference" "{reference}"' in content
        
        if lib_id:
            assert f'(lib_id "{lib_id}")' in content
        
        if value:
            assert f'"Value" "{value}"' in content
    
    @staticmethod
    def assert_file_not_contains_component(file_path, reference):
        """Assert that file does not contain specified component."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert f'"Reference" "{reference}"' not in content


# Make TestHelpers available at module level
pytest.TestHelpers = TestHelpers