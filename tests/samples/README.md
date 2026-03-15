# Sample Files for CAN Pro-Decoder Testing

This directory contains sample DBC and ASC files for testing the parsing engine without needing the full GUI.

## Files

### `example.dbc`
A CAN database file (DBC format) that defines the message structure for an automotive system with:

- **Messages:**
  - `EngineStatus` (0x100): Engine RPM, temperature, throttle position, fuel level
  - `TransmissionData` (0x200): Gear position, oil temperature, line pressure
  - `VehicleSpeed` (0x400): Vehicle speed, wheel pulse, ABS/TC status
  - `BatteryStatus` (0x800): Battery voltage and charging current
  - `WarningFlags` (0x1000): System warning flags

### `example.asc`
A Vector ASCII log file with sample CAN traffic (48 message entries) containing realistic data corresponding to the DBC file structure.

This is the input format that the application parses.

## Quick Test

To test the parser without the GUI:

```bash
# With venv activated
python tests/samples/test_parser.py
```

This will:
1. Load the DBC file
2. Parse the ASC log file
3. Display sample decoded messages
4. Show message statistics

## What to Expect

✓ The parser should decode CAN messages and extract physical values from signals
✓ Each message will have decoded signal values (engine speed in RPM, temp in °C, etc.)
✓ The output will show timestamps, IDs, message names, and signal breakdowns

## Using These Files in Your Tests

```python
import cantools
from parser_engine import CANParser
from pathlib import Path

samples_dir = Path(__file__).parent / "samples"
dbc = cantools.database.load_file(str(samples_dir / "example.dbc"))
data = CANParser.process_asc(str(samples_dir / "example.asc"), dbc)
```

## Creating Your Own Files

- **DBC files**: Can be exported from tools like Vector CANoe, PEAK PCAN View, or Python cantools
- **ASC files**: Recorded from existing CAN tools or created programmatically

See [Contributing Guide](../../CONTRIBUTING.md) for more details.
