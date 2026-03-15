#!/usr/bin/env python3
"""
Cross-platform development environment setup script for CAN Pro-Decoder.

This script sets up the Python development environment by:
1. Detecting the current operating system and Python environment
2. Creating a virtual environment
3. Installing development dependencies from pyproject.toml
4. Installing pre-commit hooks
5. Validating the setup
"""

import platform
import subprocess
import sys
from pathlib import Path


def log(message: str, level: str = "INFO"):
    """Print timestamped log message."""
    colors = {
        "INFO": "\033[94m",  # Blue
        "SUCCESS": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "RESET": "\033[0m",
    }
    color = colors.get(level, "")
    reset = colors["RESET"]
    print(f"{color}[{level}]{reset} {message}")


def run_cmd(cmd: list, description: str = "") -> bool:
    """Execute a shell command and return success status."""
    try:
        if description:
            log(f"Running: {description}", "INFO")
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        log(f"Command failed: {' '.join(cmd)}", "ERROR")
        return False
    except FileNotFoundError:
        log(f"Command not found: {cmd[0]}", "ERROR")
        return False


def main():
    """Main setup routine."""
    log("=" * 60, "INFO")
    log("CAN Pro-Decoder Development Environment Setup", "INFO")
    log("=" * 60, "INFO")

    # 1. Detect environment
    log(f"Detected OS: {platform.system()}", "INFO")
    log(f"Python Version: {sys.version.split()[0]}", "INFO")

    project_root = Path(__file__).parent
    venv_path = project_root / "venv"

    # 2. Create virtual environment
    if venv_path.exists():
        log(f"Virtual environment already exists at {venv_path}", "WARNING")
        use_existing = input("Use existing venv? (y/n): ").strip().lower() == "y"
        if not use_existing:
            log("Removing old venv...", "INFO")
            import shutil

            shutil.rmtree(venv_path)

    if not venv_path.exists():
        log(f"Creating virtual environment at {venv_path}...", "INFO")
        if not run_cmd(
            [sys.executable, "-m", "venv", str(venv_path)],
            "Creating venv",
        ):
            log("Failed to create virtual environment", "ERROR")
            return 1

    # 3. Determine activation command and python path
    if platform.system() == "Windows":
        activate_cmd = str(venv_path / "Scripts" / "activate.bat")
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        activate_cmd = str(venv_path / "bin" / "activate")
        python_exe = venv_path / "bin" / "python"

    log(f"Using Python: {python_exe}", "INFO")

    # 4. Upgrade pip
    log("Upgrading pip...", "INFO")
    if not run_cmd(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrade pip",
    ):
        log("Warning: Failed to upgrade pip, continuing...", "WARNING")

    # 5. Install dependencies (app is not meant to be installed as a package)
    log("Installing project dependencies...", "INFO")
    packages = [
        "cantools>=41.1.1",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "matplotlib>=3.3.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "ruff>=0.1.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
        "pyinstaller>=6.0.0",
    ]
    if not run_cmd(
        [str(python_exe), "-m", "pip", "install"] + packages,
        "Install all dependencies",
    ):
        log("Failed to install dependencies", "ERROR")
        return 1

    # 6. Install pre-commit hooks
    log("Installing pre-commit hooks...", "INFO")
    if not run_cmd(
        [str(python_exe), "-m", "pre_commit", "install"],
        "Install pre-commit hooks",
    ):
        log("Warning: Failed to install pre-commit hooks", "WARNING")

    # 7. Validate setup
    log("Validating setup...", "INFO")
    packages = ["cantools", "pandas", "pytest", "black", "ruff", "mypy"]
    missing = []

    for package in packages:
        result = subprocess.run(
            [str(python_exe), "-c", f"import {package}"],
            capture_output=True,
        )
        if result.returncode != 0:
            missing.append(package)

    if missing:
        log(f"Missing packages: {', '.join(missing)}", "WARNING")
    else:
        log("All required packages are installed!", "SUCCESS")

    # 8. Print next steps
    log("=" * 60, "SUCCESS")
    log("Setup complete!", "SUCCESS")
    log("=" * 60, "SUCCESS")
    log("Next steps:", "INFO")
    if platform.system() == "Windows":
        log(f"1. Activate venv: {activate_cmd}", "INFO")
    else:
        log(f"1. Activate venv: source {activate_cmd}", "INFO")
    log("2. Run tests: pytest", "INFO")
    log("3. Format code: black .", "INFO")
    log("4. Lint code: ruff check .", "INFO")
    log("5. Type check: mypy .", "INFO")

    return 0


if __name__ == "__main__":
    sys.exit(main())
