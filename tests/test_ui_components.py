"""
Unit tests for ui_components module.
"""

import tkinter as tk

import pandas as pd
import pytest

from ui_components import ExcelConfigDialog


@pytest.mark.gui
class TestExcelConfigDialog:
    """Tests for ExcelConfigDialog component."""

    @pytest.fixture
    def tk_root(self):
        """Create a Tk root window for GUI tests."""
        root = tk.Tk()
        root.withdraw()  # Hide the window
        yield root
        root.destroy()

    @pytest.fixture
    def sample_excel_file(self, tmp_path):
        """Create a sample Excel file for testing."""
        df = pd.DataFrame(
            {
                "Frame_ID": ["0x123", "0x456"],
                "Hex_Value": ["11223344", "AABBCCDD"],
                "Meaning": ["Message Type A", "Message Type B"],
            }
        )
        excel_file = tmp_path / "test.xlsx"
        df.to_excel(excel_file, index=False, sheet_name="Sheet1")
        return excel_file

    def test_dialog_initialization(self, tk_root, sample_excel_file):
        """Test ExcelConfigDialog initialization."""
        xl_file = pd.ExcelFile(str(sample_excel_file))
        dialog = ExcelConfigDialog(tk_root, xl_file)
        assert dialog.result is None
        dialog.destroy()

    def test_dialog_sheet_names(self, tk_root, sample_excel_file):
        """Test dialog loads correct sheet names."""
        xl_file = pd.ExcelFile(str(sample_excel_file))
        dialog = ExcelConfigDialog(tk_root, xl_file)
        assert "Sheet1" in xl_file.sheet_names
        dialog.destroy()
