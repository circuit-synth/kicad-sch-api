"""
Base KiCad CLI executor with Docker fallback support.

This module provides the core infrastructure for executing kicad-cli commands
either locally or via Docker containers.
"""

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from kicad_sch_api.cli.types import ExecutionMode


@dataclass
class ExecutorInfo:
    """Information about available execution modes."""

    local_available: bool
    local_version: Optional[str]
    docker_available: bool
    docker_image: str
    active_mode: ExecutionMode


class KiCadExecutor:
    """
    Core executor for KiCad CLI commands with Docker fallback.

    Execution strategy:
    1. AUTO mode (default): Try local kicad-cli, fall back to Docker
    2. LOCAL mode: Force local kicad-cli (fail if not available)
    3. DOCKER mode: Force Docker (fail if Docker not available)

    Environment variables:
    - KICAD_CLI_MODE: Set execution mode (auto|local|docker)
    - KICAD_DOCKER_IMAGE: Override Docker image (default: kicad/kicad:latest)

    Example:
        >>> executor = KiCadExecutor()
        >>> result = executor.run(['sch', 'export', 'netlist', 'circuit.kicad_sch'])
    """

    # Class-level cache for detection results
    _local_available: Optional[bool] = None
    _local_version: Optional[str] = None
    _docker_available: Optional[bool] = None

    def __init__(
        self,
        mode: ExecutionMode = "auto",
        docker_image: str = "kicad/kicad:latest",
        verbose: bool = False,
    ):
        """
        Initialize KiCad executor.

        Args:
            mode: Execution mode (auto, local, or docker)
            docker_image: Docker image to use
            verbose: Print execution details
        """
        # Check environment variable override
        env_mode = os.getenv("KICAD_CLI_MODE", "").lower()
        if env_mode in ("auto", "local", "docker"):
            mode = env_mode  # type: ignore

        env_image = os.getenv("KICAD_DOCKER_IMAGE", "")
        if env_image:
            docker_image = env_image

        self.mode = mode
        self.docker_image = docker_image
        self.verbose = verbose

        # Detect capabilities on first use
        if KiCadExecutor._local_available is None:
            KiCadExecutor._detect_local()
        if KiCadExecutor._docker_available is None:
            KiCadExecutor._detect_docker()

    @classmethod
    def _detect_local(cls) -> None:
        """Detect if kicad-cli is available locally."""
        try:
            result = subprocess.run(
                ["kicad-cli", "version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                cls._local_available = True
                cls._local_version = result.stdout.strip()
            else:
                cls._local_available = False
                cls._local_version = None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            cls._local_available = False
            cls._local_version = None

    @classmethod
    def _detect_docker(cls) -> None:
        """Detect if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5,
            )
            cls._docker_available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            cls._docker_available = False

    def _run_local(
        self, args: List[str], cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        """Run kicad-cli locally."""
        if not KiCadExecutor._local_available:
            raise RuntimeError(
                "kicad-cli not found. Install KiCad or use Docker mode.\n"
                "Install: https://www.kicad.org/download/\n"
                "Docker: export KICAD_CLI_MODE=docker"
            )

        cmd = ["kicad-cli"] + args
        if self.verbose:
            print(f"Running locally: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
        )

        return result

    def _run_docker(
        self, args: List[str], cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        """Run kicad-cli via Docker."""
        if not KiCadExecutor._docker_available:
            raise RuntimeError(
                "Docker not found. Install Docker or use local mode.\n"
                "Install: https://docs.docker.com/get-docker/\n"
                "Local: Install KiCad from https://www.kicad.org/download/"
            )

        # Determine working directory
        if cwd:
            work_dir = cwd.resolve()
        else:
            work_dir = Path.cwd()

        # Build Docker command
        docker_cmd = [
            "docker",
            "run",
            "--rm",  # Remove container after execution
            "-v",
            f"{work_dir}:/workspace",  # Mount working directory
            "-w",
            "/workspace",  # Set working directory
        ]

        # Add user mapping on Linux/Mac to avoid permission issues
        if os.name != "nt":  # Not Windows
            uid = os.getuid()
            gid = os.getgid()
            docker_cmd.extend(["--user", f"{uid}:{gid}"])

        docker_cmd.extend(
            [
                self.docker_image,
                "kicad-cli",
            ]
            + args
        )

        if self.verbose:
            print(f"Running via Docker: {' '.join(docker_cmd)}")

        # Check if image exists, pull if needed
        self._ensure_docker_image()

        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
        )

        return result

    def _ensure_docker_image(self) -> None:
        """Ensure Docker image is available, pull if needed."""
        # Check if image exists
        result = subprocess.run(
            ["docker", "image", "inspect", self.docker_image],
            capture_output=True,
        )

        if result.returncode != 0:
            # Image not found, pull it
            if self.verbose:
                print(f"Pulling Docker image: {self.docker_image}")

            pull_result = subprocess.run(
                ["docker", "pull", self.docker_image],
                capture_output=not self.verbose,
            )

            if pull_result.returncode != 0:
                raise RuntimeError(f"Failed to pull Docker image: {self.docker_image}")

    def run(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Execute kicad-cli command.

        Args:
            args: Command arguments (e.g., ['sch', 'export', 'netlist', 'file.kicad_sch'])
            cwd: Working directory (default: current directory)
            check: Raise exception on non-zero exit code

        Returns:
            CompletedProcess with stdout, stderr, returncode

        Raises:
            RuntimeError: If execution fails or kicad-cli unavailable
        """
        if self.mode == "local":
            result = self._run_local(args, cwd)
        elif self.mode == "docker":
            result = self._run_docker(args, cwd)
        else:  # auto mode
            if KiCadExecutor._local_available:
                if self.verbose:
                    print(f"Using local KiCad CLI ({KiCadExecutor._local_version})")
                result = self._run_local(args, cwd)
            elif KiCadExecutor._docker_available:
                if self.verbose:
                    print("Local KiCad CLI not found, using Docker")
                result = self._run_docker(args, cwd)
            else:
                raise RuntimeError(
                    "KiCad CLI not available in any mode.\n\n"
                    "Install options:\n"
                    "1. Install KiCad: https://www.kicad.org/download/\n"
                    "2. Install Docker: https://docs.docker.com/get-docker/"
                )

        if check and result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            raise RuntimeError(f"KiCad CLI command failed:\n{error_msg}")

        return result

    @classmethod
    def get_info(cls) -> ExecutorInfo:
        """Get information about available execution modes."""
        if cls._local_available is None:
            cls._detect_local()
        if cls._docker_available is None:
            cls._detect_docker()

        # Determine active mode
        env_mode = os.getenv("KICAD_CLI_MODE", "auto").lower()
        if env_mode not in ("auto", "local", "docker"):
            env_mode = "auto"

        return ExecutorInfo(
            local_available=cls._local_available or False,
            local_version=cls._local_version,
            docker_available=cls._docker_available or False,
            docker_image=os.getenv("KICAD_DOCKER_IMAGE", "kicad/kicad:latest"),
            active_mode=env_mode,  # type: ignore
        )


# Convenience functions
def get_executor_info() -> ExecutorInfo:
    """
    Get information about KiCad CLI availability.

    Returns:
        ExecutorInfo with details about local and Docker availability

    Example:
        >>> info = get_executor_info()
        >>> print(f"Local: {info.local_available}, Docker: {info.docker_available}")
    """
    return KiCadExecutor.get_info()


def set_execution_mode(mode: ExecutionMode) -> None:
    """
    Set the execution mode for all KiCad CLI operations.

    Args:
        mode: Execution mode (auto, local, or docker)

    Example:
        >>> set_execution_mode('docker')  # Force Docker mode
    """
    os.environ["KICAD_CLI_MODE"] = mode
