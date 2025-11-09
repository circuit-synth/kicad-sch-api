"""
Tests for CLI setup commands (ksa_claude_setup and ksa_demo).
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import tempfile
import shutil


class TestKsaClaudeSetup:
    """Tests for the ksa_claude_setup command."""

    def test_setup_creates_claude_directory_if_missing(self, tmp_path):
        """Test that setup creates .claude/commands if it doesn't exist."""
        # Import here to avoid issues if module doesn't exist yet
        from kicad_sch_api.cli.setup_claude import main

        # Create a fake home directory without .claude
        fake_home = tmp_path / "home"
        fake_home.mkdir()

        with patch('pathlib.Path.home', return_value=fake_home):
            result = main([])

        assert result == 0
        assert (fake_home / ".claude" / "commands").exists()

    def test_setup_copies_commands_with_prefix(self, tmp_path):
        """Test that commands are copied with ksa- prefix."""
        from kicad_sch_api.cli.setup_claude import main

        fake_home = tmp_path / "home"
        fake_home.mkdir()

        with patch('pathlib.Path.home', return_value=fake_home):
            result = main([])

        assert result == 0

        # Check that files were copied with ksa- prefix
        commands_dir = fake_home / ".claude" / "commands"
        command_files = list(commands_dir.rglob("*.md"))

        # Should have copied 8 commands
        assert len(command_files) == 8

        # All command files should be prefixed with ksa-
        for cmd_file in command_files:
            assert cmd_file.stem.startswith("ksa-")

    def test_setup_preserves_existing_commands(self, tmp_path):
        """Test that setup doesn't overwrite existing .claude commands."""
        from kicad_sch_api.cli.setup_claude import main

        fake_home = tmp_path / "home"
        fake_home.mkdir()

        # Create existing .claude/commands with a file
        existing_commands = fake_home / ".claude" / "commands"
        existing_commands.mkdir(parents=True)
        existing_file = existing_commands / "my-command.md"
        existing_file.write_text("# My existing command")

        with patch('pathlib.Path.home', return_value=fake_home):
            result = main([])

        assert result == 0

        # Existing file should still be there
        assert existing_file.exists()
        assert existing_file.read_text() == "# My existing command"

        # New files should also be there
        command_files = list(existing_commands.rglob("*.md"))
        assert len(command_files) >= 9  # 8 new + 1 existing

    def test_setup_verbose_output(self, tmp_path, capsys):
        """Test verbose output shows copied files."""
        from kicad_sch_api.cli.setup_claude import main

        fake_home = tmp_path / "home"
        fake_home.mkdir()

        with patch('pathlib.Path.home', return_value=fake_home):
            result = main(['--verbose'])

        assert result == 0

        captured = capsys.readouterr()
        assert "✓" in captured.out or "✅" in captured.out
        assert "commands" in captured.out.lower()

    def test_setup_handles_permission_error(self, tmp_path, capsys):
        """Test graceful handling of permission errors."""
        from kicad_sch_api.cli.setup_claude import main

        fake_home = tmp_path / "home"
        fake_home.mkdir()

        # Make the directory read-only to trigger permission error
        with patch('pathlib.Path.home', return_value=fake_home):
            with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
                result = main([])

        # Should return error code
        assert result == 1

        captured = capsys.readouterr()
        assert "permission" in captured.err.lower() or "error" in captured.err.lower()


class TestKsaDemo:
    """Tests for the ksa_demo command."""

    def test_demo_creates_file_in_cwd(self, tmp_path):
        """Test that ksa_demo creates ksa_demo.py in current directory."""
        from kicad_sch_api.cli.demo import main

        # Run in temp directory
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = main([])

            assert result == 0
            assert (tmp_path / "ksa_demo.py").exists()
        finally:
            os.chdir(original_cwd)

    def test_demo_file_is_executable_python(self, tmp_path):
        """Test that generated demo file is valid Python."""
        from kicad_sch_api.cli.demo import main

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = main([])
            assert result == 0

            demo_file = tmp_path / "ksa_demo.py"
            content = demo_file.read_text()

            # Should have shebang
            assert content.startswith("#!/usr/bin/env python3")

            # Should have multiple demo sections
            assert "DEMO" in content
            assert "import kicad_sch_api" in content

            # Check it's syntactically valid Python
            compile(content, "ksa_demo.py", "exec")
        finally:
            os.chdir(original_cwd)

    def test_demo_refuses_to_overwrite(self, tmp_path, capsys):
        """Test that demo won't overwrite existing ksa_demo.py."""
        from kicad_sch_api.cli.demo import main

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create existing file
            existing = tmp_path / "ksa_demo.py"
            existing.write_text("# Existing content")

            # Try to create demo
            result = main([])

            # Should fail or prompt
            assert result == 1

            # Content should be unchanged
            assert existing.read_text() == "# Existing content"

            captured = capsys.readouterr()
            assert "exists" in captured.err.lower() or "exists" in captured.out.lower()
        finally:
            os.chdir(original_cwd)

    def test_demo_force_overwrite(self, tmp_path):
        """Test that --force flag allows overwriting."""
        from kicad_sch_api.cli.demo import main

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create existing file
            existing = tmp_path / "ksa_demo.py"
            existing.write_text("# Old content")

            # Force overwrite
            result = main(['--force'])

            assert result == 0

            # Content should be new
            new_content = existing.read_text()
            assert "# Old content" not in new_content
            assert "#!/usr/bin/env python3" in new_content
        finally:
            os.chdir(original_cwd)

    def test_demo_output_shows_next_steps(self, tmp_path, capsys):
        """Test that demo output shows how to run it."""
        from kicad_sch_api.cli.demo import main

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = main([])
            assert result == 0

            captured = capsys.readouterr()
            assert "python" in captured.out.lower()
            assert "ksa_demo.py" in captured.out
        finally:
            os.chdir(original_cwd)

    def test_demo_content_has_multiple_sections(self, tmp_path):
        """Test that demo showcases multiple features."""
        from kicad_sch_api.cli.demo import main

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = main([])
            assert result == 0

            content = (tmp_path / "ksa_demo.py").read_text()

            # Should have multiple demo sections
            assert content.count("DEMO") >= 3

            # Should showcase key features mentioned in requirements
            assert "duplicate" in content.lower() or "array" in content.lower()
            assert "layout" in content.lower() or "grid" in content.lower()
        finally:
            os.chdir(original_cwd)
