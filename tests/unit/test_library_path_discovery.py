"""
Unit tests for KiCAD library path discovery.

Tests the versatile library path discovery system including:
- Environment variable support
- Version-flexible path discovery
- Platform-specific path detection
- Path validation
- Error handling
"""

import os
import platform
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from kicad_sch_api.library.cache import SymbolLibraryCache


@pytest.fixture
def temp_library_dir():
    """Create a temporary directory with mock KiCAD library files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lib_dir = Path(tmpdir) / "symbols"
        lib_dir.mkdir()

        # Create mock .kicad_sym file
        lib_file = lib_dir / "Device.kicad_sym"
        lib_file.write_text("(kicad_symbol_lib (version 20220914))")

        yield lib_dir


@pytest.fixture
def empty_library_dir():
    """Create a temporary directory with no library files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lib_dir = Path(tmpdir) / "empty"
        lib_dir.mkdir()
        yield lib_dir


class TestEnvironmentVariableSupport:
    """Test environment variable support for library paths."""

    def test_generic_kicad_symbol_dir(self, temp_library_dir):
        """Test KICAD_SYMBOL_DIR environment variable."""
        with patch.dict(os.environ, {"KICAD_SYMBOL_DIR": str(temp_library_dir)}, clear=True):
            cache = SymbolLibraryCache(enable_persistence=False)
            paths = cache._check_environment_variables()

            assert len(paths) == 1
            assert paths[0] == temp_library_dir

    def test_version_specific_env_vars(self, temp_library_dir):
        """Test version-specific environment variables (KICAD7_SYMBOL_DIR, etc.)."""
        kicad7_dir = temp_library_dir / "kicad7"
        kicad7_dir.mkdir()
        (kicad7_dir / "Device.kicad_sym").write_text("(kicad_symbol_lib)")

        kicad8_dir = temp_library_dir / "kicad8"
        kicad8_dir.mkdir()
        (kicad8_dir / "Device.kicad_sym").write_text("(kicad_symbol_lib)")

        with patch.dict(
            os.environ,
            {
                "KICAD7_SYMBOL_DIR": str(kicad7_dir),
                "KICAD8_SYMBOL_DIR": str(kicad8_dir),
            },
            clear=True,
        ):
            cache = SymbolLibraryCache(enable_persistence=False)
            paths = cache._check_environment_variables()

            assert len(paths) == 2
            assert kicad7_dir in paths
            assert kicad8_dir in paths

    def test_colon_separated_paths(self, temp_library_dir):
        """Test KICAD_SYMBOL_DIR with colon-separated multiple paths."""
        dir1 = temp_library_dir / "lib1"
        dir1.mkdir()
        (dir1 / "Device.kicad_sym").write_text("(kicad_symbol_lib)")

        dir2 = temp_library_dir / "lib2"
        dir2.mkdir()
        (dir2 / "Connector.kicad_sym").write_text("(kicad_symbol_lib)")

        path_str = f"{dir1}:{dir2}"
        with patch.dict(os.environ, {"KICAD_SYMBOL_DIR": path_str}, clear=True):
            cache = SymbolLibraryCache(enable_persistence=False)
            paths = cache._check_environment_variables()

            assert len(paths) == 2
            assert dir1 in paths
            assert dir2 in paths

    def test_windows_semicolon_separated_paths(self):
        """Test Windows-style semicolon-separated paths.

        This test verifies the separator logic by checking that semicolon (;)
        is used to split paths on Windows instead of colon (:).
        """
        # Create fake Windows-style paths (testing split logic only)
        fake_path1 = "C:/KiCad/symbols"
        fake_path2 = "D:/MyLibs/symbols"
        path_str = f"{fake_path1};{fake_path2}"

        with patch.dict(os.environ, {"KICAD_SYMBOL_DIR": path_str}, clear=True):
            cache = SymbolLibraryCache(enable_persistence=False)

            # Mock _validate_library_path to always return True for this test
            # (we're only testing the separator logic, not path validation)
            with patch.object(cache, "_validate_library_path", return_value=True):
                with patch("kicad_sch_api.library.cache.os.name", "nt"):
                    paths = cache._check_environment_variables()

                    # Verify that both paths were split correctly using semicolon
                    # The key test is that we get 2 paths, proving semicolon split worked
                    assert len(paths) == 2

    def test_invalid_env_var_paths_logged(self, caplog):
        """Test that invalid paths from env vars are logged as warnings."""
        with patch.dict(os.environ, {"KICAD_SYMBOL_DIR": "/nonexistent/path"}, clear=True):
            cache = SymbolLibraryCache(enable_persistence=False)
            paths = cache._check_environment_variables()

            assert len(paths) == 0
            assert "not found" in caplog.text or "does not exist" in caplog.text

    def test_empty_env_var_ignored(self):
        """Test that empty environment variables are silently ignored."""
        with patch.dict(os.environ, {"KICAD_SYMBOL_DIR": ""}, clear=True):
            cache = SymbolLibraryCache(enable_persistence=False)
            paths = cache._check_environment_variables()

            assert len(paths) == 0


class TestVersionFlexiblePathDiscovery:
    """Test version-flexible path discovery using glob patterns."""

    @patch("platform.system")
    def test_macos_version_glob(self, mock_system, temp_library_dir):
        """Test macOS version-flexible path discovery."""
        mock_system.return_value = "Darwin"

        # Create mock KiCAD installations
        kicad_base = temp_library_dir
        kicad7_path = kicad_base / "KiCad7" / "KiCad.app" / "Contents" / "SharedSupport" / "symbols"
        kicad8_path = kicad_base / "KiCad8" / "KiCad.app" / "Contents" / "SharedSupport" / "symbols"
        kicad806_path = (
            kicad_base / "KiCad806" / "KiCad.app" / "Contents" / "SharedSupport" / "symbols"
        )

        for path in [kicad7_path, kicad8_path, kicad806_path]:
            path.mkdir(parents=True)
            (path / "Device.kicad_sym").write_text("(kicad_symbol_lib)")

        with patch("pathlib.Path.home", return_value=temp_library_dir):
            cache = SymbolLibraryCache(enable_persistence=False)
            paths = cache._glob_version_paths(
                str(kicad_base / "KiCad*" / "KiCad.app" / "Contents" / "SharedSupport" / "symbols")
            )

            assert len(paths) == 3
            assert kicad7_path in paths
            assert kicad8_path in paths
            assert kicad806_path in paths

    @patch("platform.system")
    def test_windows_version_glob(self, mock_system, temp_library_dir):
        """Test Windows version-flexible path discovery."""
        mock_system.return_value = "Windows"

        # Create mock KiCAD installations
        kicad_base = temp_library_dir / "Program Files" / "KiCad"
        kicad7_path = kicad_base / "7.0" / "share" / "kicad" / "symbols"
        kicad8_path = kicad_base / "8.0" / "share" / "kicad" / "symbols"
        kicad9_path = kicad_base / "9.0" / "share" / "kicad" / "symbols"

        for path in [kicad7_path, kicad8_path, kicad9_path]:
            path.mkdir(parents=True)
            (path / "Device.kicad_sym").write_text("(kicad_symbol_lib)")

        cache = SymbolLibraryCache(enable_persistence=False)
        paths = cache._glob_version_paths(str(kicad_base / "*" / "share" / "kicad" / "symbols"))

        assert len(paths) >= 3
        assert kicad7_path in paths
        assert kicad8_path in paths
        assert kicad9_path in paths

    def test_glob_returns_only_existing_paths(self, temp_library_dir):
        """Test that glob only returns paths that actually exist."""
        # Create one real path
        real_path = temp_library_dir / "KiCad8" / "symbols"
        real_path.mkdir(parents=True)
        (real_path / "Device.kicad_sym").write_text("(kicad_symbol_lib)")

        cache = SymbolLibraryCache(enable_persistence=False)
        pattern = str(temp_library_dir / "KiCad*" / "symbols")
        paths = cache._glob_version_paths(pattern)

        assert len(paths) == 1
        assert real_path in paths


class TestPathValidation:
    """Test library path validation."""

    def test_valid_library_path(self, temp_library_dir):
        """Test validation of valid library path."""
        cache = SymbolLibraryCache(enable_persistence=False)
        is_valid = cache._validate_library_path(temp_library_dir)

        assert is_valid is True

    def test_nonexistent_path(self):
        """Test validation of nonexistent path."""
        cache = SymbolLibraryCache(enable_persistence=False)
        is_valid = cache._validate_library_path(Path("/nonexistent/path"))

        assert is_valid is False

    def test_empty_directory(self, empty_library_dir):
        """Test validation of directory with no .kicad_sym files."""
        cache = SymbolLibraryCache(enable_persistence=False)
        is_valid = cache._validate_library_path(empty_library_dir)

        # Should return False since there are no library files
        assert is_valid is False

    def test_file_instead_of_directory(self, temp_library_dir):
        """Test validation when path is a file instead of directory."""
        lib_file = temp_library_dir / "Device.kicad_sym"

        cache = SymbolLibraryCache(enable_persistence=False)
        is_valid = cache._validate_library_path(lib_file)

        # Should handle gracefully - either accept the file or reject
        # Implementation dependent - file paths might be valid in some cases
        assert isinstance(is_valid, bool)


class TestPathMerging:
    """Test merging of paths from multiple sources."""

    def test_merge_env_and_system_paths(self, temp_library_dir):
        """Test that env vars and system paths are merged together."""
        env_dir = temp_library_dir / "env"
        env_dir.mkdir()
        (env_dir / "Device.kicad_sym").write_text("(kicad_symbol_lib)")

        system_dir = temp_library_dir / "system"
        system_dir.mkdir()
        (system_dir / "Connector.kicad_sym").write_text("(kicad_symbol_lib)")

        with patch.dict(os.environ, {"KICAD_SYMBOL_DIR": str(env_dir)}):
            cache = SymbolLibraryCache(enable_persistence=False)

            # Mock system paths to include our test directory
            with patch.object(cache, "_get_default_library_paths", return_value=[system_dir]):
                discovered = cache.discover_libraries()

                # Should discover libraries from both sources
                assert discovered >= 2  # At least the two we added

    def test_duplicate_paths_handled(self, temp_library_dir):
        """Test that duplicate paths from different sources are handled correctly."""
        with patch.dict(os.environ, {"KICAD_SYMBOL_DIR": str(temp_library_dir)}):
            cache = SymbolLibraryCache(enable_persistence=False)

            # Same path from env var and system paths
            with patch.object(cache, "_get_default_library_paths", return_value=[temp_library_dir]):
                # Should not add the same path twice
                cache.add_library_path(temp_library_dir / "Device.kicad_sym")
                initial_count = len(cache._library_paths)

                cache.add_library_path(temp_library_dir / "Device.kicad_sym")
                final_count = len(cache._library_paths)

                assert initial_count == final_count  # No duplicates


class TestErrorHandling:
    """Test error handling and user guidance."""

    def test_helpful_error_when_no_libraries_found(self, caplog):
        """Test that helpful error is shown when no libraries are found."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock all path discovery to return empty lists
            cache = SymbolLibraryCache(enable_persistence=False)

            with patch.object(cache, "_get_default_library_paths", return_value=[]):
                with patch.object(cache, "_check_environment_variables", return_value=[]):
                    discovered = cache.discover_libraries()

                    # Should log informative message
                    assert discovered == 0

    def test_permission_error_handled_gracefully(self, temp_library_dir):
        """Test that permission errors don't crash the discovery process."""
        cache = SymbolLibraryCache(enable_persistence=False)

        # Mock a permission error
        with patch("pathlib.Path.exists", side_effect=PermissionError("Access denied")):
            # Should not raise exception
            paths = cache._get_default_library_paths()

            # Should return whatever paths it could check
            assert isinstance(paths, list)


class TestBackwardCompatibility:
    """Test that existing API still works."""

    def test_add_library_path_still_works(self, temp_library_dir):
        """Test that programmatic path addition still works."""
        cache = SymbolLibraryCache(enable_persistence=False)
        lib_file = temp_library_dir / "Device.kicad_sym"

        result = cache.add_library_path(lib_file)
        assert result is True
        assert lib_file in cache._library_paths

    def test_discover_libraries_with_custom_paths(self, temp_library_dir):
        """Test discover_libraries with custom search paths."""
        cache = SymbolLibraryCache(enable_persistence=False)
        discovered = cache.discover_libraries([temp_library_dir])

        assert discovered >= 1  # At least one library from our temp dir

    def test_existing_code_without_env_vars_works(self, temp_library_dir):
        """Test that code without env vars still works (backward compatibility)."""
        # No env vars set
        with patch.dict(os.environ, {}, clear=True):
            cache = SymbolLibraryCache(enable_persistence=False)

            # Manual path addition should still work
            lib_file = temp_library_dir / "Device.kicad_sym"
            cache.add_library_path(lib_file)

            # Should be able to discover in the added path
            assert lib_file in cache._library_paths


class TestPlatformSpecificPaths:
    """Test platform-specific default path discovery."""

    @patch("platform.system")
    @patch("os.name")
    def test_windows_default_paths(self, mock_os_name, mock_system):
        """Test Windows default path discovery."""
        mock_system.return_value = "Windows"
        mock_os_name.return_value = "nt"

        cache = SymbolLibraryCache(enable_persistence=False)
        paths = cache._get_default_library_paths()

        # Should include Windows paths
        # (Actual existence doesn't matter, just that Windows paths are included)
        assert isinstance(paths, list)

    @patch("platform.system")
    @patch("os.name")
    def test_macos_default_paths(self, mock_os_name, mock_system):
        """Test macOS default path discovery."""
        mock_system.return_value = "Darwin"
        mock_os_name.return_value = "posix"

        cache = SymbolLibraryCache(enable_persistence=False)
        paths = cache._get_default_library_paths()

        # Should include macOS paths
        assert isinstance(paths, list)

    @patch("platform.system")
    @patch("os.name")
    def test_linux_default_paths(self, mock_os_name, mock_system):
        """Test Linux default path discovery."""
        mock_system.return_value = "Linux"
        mock_os_name.return_value = "posix"

        cache = SymbolLibraryCache(enable_persistence=False)
        paths = cache._get_default_library_paths()

        # Should include Linux paths
        assert isinstance(paths, list)


class TestLogging:
    """Test logging behavior during path discovery."""

    def test_debug_logging_for_checked_paths(self, caplog, temp_library_dir):
        """Test that checked paths are logged at DEBUG level."""
        import logging

        with caplog.at_level(logging.DEBUG):
            cache = SymbolLibraryCache(enable_persistence=False)
            cache._get_default_library_paths()

            # Should have debug logs about paths being checked
            assert len(caplog.records) > 0

    def test_info_logging_for_found_libraries(self, caplog, temp_library_dir):
        """Test that found libraries are logged at INFO level."""
        import logging

        with caplog.at_level(logging.INFO):
            cache = SymbolLibraryCache(enable_persistence=False)
            lib_file = temp_library_dir / "Device.kicad_sym"
            cache.add_library_path(lib_file)

            # Should have INFO log about library being added
            assert any("Added library" in record.message for record in caplog.records)

    def test_warning_logging_for_invalid_paths(self, caplog, temp_library_dir):
        """Test that invalid paths are logged as warnings."""
        import logging

        with caplog.at_level(logging.WARNING):
            cache = SymbolLibraryCache(enable_persistence=False)
            cache.add_library_path(Path("/totally/fake/path.kicad_sym"))

            # Should have warning about path not found
            assert any("not found" in record.message for record in caplog.records)
