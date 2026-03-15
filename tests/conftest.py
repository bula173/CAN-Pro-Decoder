"""
Pytest configuration and shared fixtures for CAN Pro-Decoder tests.
"""

from pathlib import Path
from typing import Generator

import cantools
import pytest


@pytest.fixture
def sample_dbc_path() -> Path:
    """Return path to a sample DBC file for testing."""
    sample_dir = Path(__file__).parent / "samples"
    sample_dir.mkdir(exist_ok=True)
    return sample_dir / "sample.dbc"


@pytest.fixture
def sample_dbc_db() -> cantools.database.Database:
    """Load the example DBC file for testing."""
    sample_dir = Path(__file__).parent / "samples"
    dbc_path = sample_dir / "example.dbc"
    if not dbc_path.exists():
        pytest.skip("example.dbc not found")
    return cantools.database.load_file(str(dbc_path), strict=False)


@pytest.fixture
def sample_asc_data() -> str:
    """Return sample ASC (Vector ASCII) log data for testing."""
    return """FormatVersion=5.0

{CHANNEL}
ID=1h
Baudrate=500000

{ASCLII_LOG}
0.000000 1  123h   Rx   8 11 22 33 44 55 66 77 88
0.100000 1  456h   Tx   4 AA BB CC DD
0.200000 1  123h   Rx   8 11 22 33 44 55 66 77 88
"""


@pytest.fixture
def temp_test_dir(tmp_path) -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    yield tmp_path


@pytest.fixture(autouse=True)
def reset_state():
    """Reset any global state between tests."""
    yield
    # Cleanup code here if needed
