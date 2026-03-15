"""
Unit tests for parser_engine module.
"""

import pytest

from parser_engine import CANParser


@pytest.mark.unit
class TestCANParser:
    """Tests for CANParser class."""

    def test_process_asc_basic(self, sample_dbc_db, tmp_path):
        """Test basic ASC file parsing."""
        # Create a temporary ASC file
        asc_file = tmp_path / "test.asc"
        asc_content = """FormatVersion=5.0

{CHANNEL}
ID=1h
Baudrate=500000

{ASCLII_LOG}
0.000000 1  123h   Rx   8 11 22 33 44 55 66 77 88
0.100000 1  456h   Tx   4 AA BB CC DD
"""
        asc_file.write_text(asc_content)

        # Parse the file
        result = CANParser.process_asc(str(asc_file), sample_dbc_db)

        # Should parse without errors
        assert isinstance(result, list)

    def test_process_asc_empty_file(self, sample_dbc_db, tmp_path):
        """Test parsing empty ASC file."""
        asc_file = tmp_path / "empty.asc"
        asc_file.write_text("")

        result = CANParser.process_asc(str(asc_file), sample_dbc_db)

        assert result == []

    def test_process_asc_malformed_lines(self, sample_dbc_db, tmp_path):
        """Test that malformed lines are gracefully skipped."""
        asc_file = tmp_path / "malformed.asc"
        asc_content = """FormatVersion=5.0

{CHANNEL}
ID=1h

{ASCLII_LOG}
0.000000 1  123h   Rx   8 11 22 33 44 55 66 77 88
GARBAGE_LINE
0.100000 1  456h   Tx   4 AA BB CC DD
"""
        asc_file.write_text(asc_content)

        # Should not crash, just skip bad lines
        result = CANParser.process_asc(str(asc_file), sample_dbc_db)
        assert isinstance(result, list)

    def test_process_asc_with_logging(self, sample_dbc_db, tmp_path):
        """Test ASC processing with custom logging function."""
        asc_file = tmp_path / "test.asc"
        asc_content = """FormatVersion=5.0

{ASCLII_LOG}
0.000000 1  123h   Rx   8 11 22 33 44 55 66 77 88
"""
        asc_file.write_text(asc_content)

        log_messages = []

        def log_func(msg, level="INFO"):
            log_messages.append((msg, level))

        CANParser.process_asc(str(asc_file), sample_dbc_db, log_func=log_func)

        # Should have logged messages
        assert len(log_messages) > 0
        assert any("parse" in msg[0].lower() for msg in log_messages)
