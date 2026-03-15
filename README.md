# CAN Pro-Decoder v0.3

A high-performance CAN log analyzer and signal visualizer built for Windows using Python, Tkinter, and Matplotlib. Specifically optimized for the **MSYS2 UCRT64** environment.

## Features
* **DBC Parsing**: Load standard `.dbc` files to decode raw CAN traffic.
* **ASC Log Support**: Process Vector ASCII log files.
* **Live Filtering**: Search by Message Name or ID in real-time.
* **Signal Analysis**: Graph multiple signals on a synchronized timeline.
* **Signal Inspector**: Detailed breakdown of physical values and units.

## Quick Start

### Option 1: Download Pre-Built Windows Executable (Easiest)

No installation or Python required!

1. Go to [Releases](../../releases)
2. Download the latest `CAN_Pro_Decoder.exe`
3. Run the executable directly on Windows 7 or later

**No Python installation needed** – everything is bundled into the executable.

---

### Option 2: Run from Source (Development)

Clone & setup the project for development:

```bash
git clone <repository-url>
cd CAN-Pro-Decoder
python setup_dev.py
```

The setup script will:
- Create a Python virtual environment
- Install all dependencies from `pyproject.toml`
- Install code quality tools (Black, Ruff, Mypy)
- Set up pre-commit hooks

Activate & run:
```bash
# Activate virtual environment
source venv/bin/activate              # macOS/Linux
# or
.\venv\Scripts\activate               # Windows

# Run the application
python main.py
```

For full development setup instructions, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Platform Support

This project is optimized for **Windows** and tested on **MSYS2 UCRT64** environment. For MSYS2 installation instructions and system-level dependency management, refer to the [CONTRIBUTING.md](CONTRIBUTING.md) guide.
