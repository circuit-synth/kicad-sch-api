"""Unit tests for KiCad CLI base executor."""

import os
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from kicad_sch_api.cli.base import KiCadExecutor, get_executor_info, set_execution_mode


class TestKiCadExecutor:
    """Test KiCadExecutor class."""

    def setup_method(self):
        """Reset class-level cache before each test."""
        KiCadExecutor._local_available = None
        KiCadExecutor._local_version = None
        KiCadExecutor._docker_available = None

    def test_local_detection_available(self):
        """Test detection when kicad-cli is available."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="9.0.0")

            KiCadExecutor._detect_local()

            assert KiCadExecutor._local_available is True
            assert KiCadExecutor._local_version == "9.0.0"

    def test_local_detection_not_available(self):
        """Test detection when kicad-cli is not available."""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            KiCadExecutor._detect_local()

            assert KiCadExecutor._local_available is False
            assert KiCadExecutor._local_version is None

    def test_docker_detection_available(self):
        """Test detection when Docker is available."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            KiCadExecutor._detect_docker()

            assert KiCadExecutor._docker_available is True

    def test_docker_detection_not_available(self):
        """Test detection when Docker is not available."""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            KiCadExecutor._detect_docker()

            assert KiCadExecutor._docker_available is False

    def test_run_local_mode(self):
        """Test running in local mode."""
        with patch('subprocess.run') as mock_run:
            # Setup: kicad-cli available
            KiCadExecutor._local_available = True
            KiCadExecutor._local_version = "9.0.0"
            KiCadExecutor._docker_available = False  # Prevent Docker detection

            mock_run.return_value = Mock(returncode=0, stdout="output", stderr="")

            executor = KiCadExecutor(mode='local')
            result = executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'])

            assert result.returncode == 0
            # Check the last call (the actual kicad-cli execution)
            args = mock_run.call_args[0][0]
            assert args[0] == 'kicad-cli'

    def test_run_docker_mode(self):
        """Test running in Docker mode."""
        with patch('subprocess.run') as mock_run, \
             patch.object(KiCadExecutor, '_ensure_docker_image'):

            # Setup: Docker available
            KiCadExecutor._docker_available = True

            mock_run.return_value = Mock(returncode=0, stdout="output", stderr="")

            executor = KiCadExecutor(mode='docker')
            result = executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'])

            assert result.returncode == 0
            args = mock_run.call_args[0][0]
            assert args[0] == 'docker'
            assert 'run' in args
            assert '--rm' in args

    def test_run_auto_mode_local_available(self):
        """Test auto mode when local is available."""
        with patch('subprocess.run') as mock_run:
            KiCadExecutor._local_available = True
            KiCadExecutor._docker_available = True

            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            executor = KiCadExecutor(mode='auto')
            executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'])

            # Should use local, not Docker
            args = mock_run.call_args[0][0]
            assert args[0] == 'kicad-cli'

    def test_run_auto_mode_fallback_to_docker(self):
        """Test auto mode fallback to Docker when local not available."""
        with patch('subprocess.run') as mock_run, \
             patch.object(KiCadExecutor, '_ensure_docker_image'):

            KiCadExecutor._local_available = False
            KiCadExecutor._docker_available = True

            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            executor = KiCadExecutor(mode='auto')
            executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'])

            # Should use Docker
            args = mock_run.call_args[0][0]
            assert args[0] == 'docker'

    def test_run_auto_mode_neither_available(self):
        """Test auto mode when neither local nor Docker available."""
        KiCadExecutor._local_available = False
        KiCadExecutor._docker_available = False

        executor = KiCadExecutor(mode='auto')

        with pytest.raises(RuntimeError, match="KiCad CLI not available"):
            executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'])

    def test_run_local_not_available(self):
        """Test running in local mode when kicad-cli not available."""
        KiCadExecutor._local_available = False

        executor = KiCadExecutor(mode='local')

        with pytest.raises(RuntimeError, match="kicad-cli not found"):
            executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'])

    def test_run_docker_not_available(self):
        """Test running in Docker mode when Docker not available."""
        KiCadExecutor._docker_available = False

        executor = KiCadExecutor(mode='docker')

        with pytest.raises(RuntimeError, match="Docker not found"):
            executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'])

    def test_environment_variable_mode_override(self):
        """Test that KICAD_CLI_MODE environment variable overrides mode."""
        with patch.dict(os.environ, {'KICAD_CLI_MODE': 'docker'}):
            executor = KiCadExecutor(mode='local')
            assert executor.mode == 'docker'

    def test_environment_variable_docker_image(self):
        """Test that KICAD_DOCKER_IMAGE environment variable works."""
        with patch.dict(os.environ, {'KICAD_DOCKER_IMAGE': 'kicad/kicad:8.0'}):
            executor = KiCadExecutor()
            assert executor.docker_image == 'kicad/kicad:8.0'

    def test_check_return_code(self):
        """Test that check parameter raises on non-zero exit code."""
        with patch('subprocess.run') as mock_run:
            KiCadExecutor._local_available = True

            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Error occurred"
            )

            executor = KiCadExecutor(mode='local')

            with pytest.raises(RuntimeError, match="KiCad CLI command failed"):
                executor.run(['sch', 'export', 'netlist', 'test.kicad_sch'], check=True)

    def test_check_false_no_exception(self):
        """Test that check=False doesn't raise on non-zero exit code."""
        with patch('subprocess.run') as mock_run:
            KiCadExecutor._local_available = True

            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")

            executor = KiCadExecutor(mode='local')
            result = executor.run(
                ['sch', 'export', 'netlist', 'test.kicad_sch'],
                check=False
            )

            assert result.returncode == 1


class TestUtilityFunctions:
    """Test utility functions."""

    def setup_method(self):
        """Reset class-level cache before each test."""
        KiCadExecutor._local_available = None
        KiCadExecutor._docker_available = None

    def test_get_executor_info(self):
        """Test get_executor_info function."""
        KiCadExecutor._local_available = True
        KiCadExecutor._local_version = "9.0.0"
        KiCadExecutor._docker_available = True

        info = get_executor_info()

        assert info.local_available is True
        assert info.local_version == "9.0.0"
        assert info.docker_available is True
        assert info.active_mode in ('auto', 'local', 'docker')

    def test_set_execution_mode(self):
        """Test set_execution_mode function."""
        set_execution_mode('docker')
        assert os.environ['KICAD_CLI_MODE'] == 'docker'

        set_execution_mode('local')
        assert os.environ['KICAD_CLI_MODE'] == 'local'
