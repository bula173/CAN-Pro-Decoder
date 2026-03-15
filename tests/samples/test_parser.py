#!/usr/bin/env python3
"""
Example script to test CAN parsing with sample DBC and ASC files.
Run this to verify the parser works before the GUI is available.
"""

import sys
from pathlib import Path
from typing import Dict

import cantools

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from parser_engine import CANParser  # noqa: E402


def main():
    """Test the parser with sample files."""
    samples_dir = Path(__file__).parent
    dbc_file = samples_dir / "example.dbc"
    asc_file = samples_dir / "example.asc"

    print("=" * 70)
    print("CAN Pro-Decoder Parser Test")
    print("=" * 70)

    # Load DBC
    print(f"\n[1] Loading DBC file: {dbc_file.name}")
    if not dbc_file.exists():
        print(f"❌ DBC file not found: {dbc_file}")
        return 1

    try:
        db = cantools.database.load_file(str(dbc_file), strict=False)
        print("✓ DBC loaded successfully")
        print(f"  Messages: {len(db.messages)}")
        for msg in db.messages:
            print(f"    - {msg.name} (0x{msg.frame_id:X}): {len(msg.signals)} signals")
    except Exception as e:
        print(f"❌ Failed to load DBC: {e}")
        return 1

    # Parse ASC
    print(f"\n[2] Parsing ASC log file: {asc_file.name}")
    if not asc_file.exists():
        print(f"❌ ASC file not found: {asc_file}")
        return 1

    log_messages = []

    def log_callback(msg, level="INFO"):
        log_messages.append((msg, level))
        print(f"  [{level}] {msg}")

    try:
        data = CANParser.process_asc(str(asc_file), db, log_func=log_callback)
        print("\n✓ Parsing complete")
        print(f"  Total entries: {len(data)}")
    except Exception as e:
        print(f"❌ Failed to parse ASC: {e}")
        return 1

    # Display sample data
    print("\n[3] Sample Parsed Messages (first 10):")
    print("-" * 70)
    for i, entry in enumerate(data[:10]):
        print(f"\n  Entry {i}:")
        print(f"    Time:    {entry['ts']}")
        print(f"    ID:      0x{entry['id'].upper()}")
        print(f"    Name:    {entry['name']}")
        print(f"    Hex:     {entry['hex']}")
        if entry["phys"]:
            print("    Signals:")
            for sig_name, sig_value in entry["phys"].items():
                print(f"      - {sig_name}: {sig_value}")

    # Statistics
    print("\n[4] Message Statistics:")
    print("-" * 70)
    msg_types: Dict[str, int] = {}
    for entry in data:
        msg_name = entry["name"]
        msg_types[msg_name] = msg_types.get(msg_name, 0) + 1

    for msg_name in sorted(msg_types.keys()):
        print(f"  {msg_name}: {msg_types[msg_name]} occurrences")

    print("\n" + "=" * 70)
    print("✓ Parser test completed successfully!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
