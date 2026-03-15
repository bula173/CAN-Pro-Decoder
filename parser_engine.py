from typing import Any, Callable, Dict, List, Optional

import cantools


class CANParser:
    """Handles the heavy lifting of reading and decoding CAN logs with high resilience."""

    @staticmethod
    def process_asc(
        path: str, db: cantools.database.Database, log_func: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        processed_data = []
        line_num = 0
        skipped_count = 0

        def _log(msg, level="INFO"):
            if log_func:
                log_func(msg, level)

        _log(f"Starting parse: {path}")

        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line_num += 1
                    p = line.split()

                    # 1. Skip headers, empty lines, or lines with too little data
                    if len(p) < 5 or any(
                        x in p for x in ["Status:", "Statistic:", "internal", "Begin", "End"]
                    ):
                        continue

                    try:
                        # 2. Find Direction anchor (Rx/Tx)
                        if "Rx" in p:
                            dir_idx = p.index("Rx")
                        elif "Tx" in p:
                            dir_idx = p.index("Tx")
                        else:
                            continue

                        # 3. Extract ID (ID is immediately before Rx/Tx)
                        raw_id_str = p[dir_idx - 1].lower()
                        clean_id_str = (
                            raw_id_str.replace("x", "").replace("h", "").replace("0x", "")
                        )
                        can_id = int(clean_id_str, 16)

                        # 4. Locate Data 'd' and DLC
                        if "d" not in p:
                            continue
                        d_idx = p.index("d")
                        dlc = int(p[d_idx + 1])

                        # 5. Extract ONLY the data bytes (ignore Length, BitCount, etc.)
                        # We start 2 indices after 'd' and take exactly 'dlc' items
                        payload_parts = p[d_idx + 2 : d_idx + 2 + dlc]

                        if len(payload_parts) < dlc:
                            _log(
                                f"Line {line_num}: ID {raw_id_str} expected {dlc} bytes, but found {len(payload_parts)}.",
                                "WARNING",
                            )
                            skipped_count += 1
                            continue

                        # Join and convert to bytes
                        hex_str = "".join(payload_parts)
                        try:
                            msg_bytes = bytes.fromhex(hex_str)
                        except ValueError:
                            _log(f"Line {line_num}: Data '{hex_str}' is not valid hex.", "ERROR")
                            skipped_count += 1
                            continue

                        # 6. DBC Decoding
                        msg_def = None
                        phys_data: Dict[str, Any] = {}
                        raw_vals: Dict[str, Any] = {}
                        msg_name = f"Unknown_0x{can_id:X}"

                        if db:
                            try:
                                msg_def = db.get_message_by_frame_id(can_id)
                                phys_data = db.decode_message(can_id, msg_bytes)
                                raw_vals = db.decode_message(can_id, msg_bytes, scaling=False)
                                msg_name = msg_def.name
                            except KeyError:
                                # Not in DBC: create dummy signals from the hex
                                phys_data = {"Raw_Data": " ".join(payload_parts).upper()}
                                raw_vals = {"Raw_Data": 0}
                            except Exception as e:
                                _log(f"Line {line_num}: Decode Error (0x{can_id:X}): {e}", "DEBUG")

                        # 7. Success - Append to data
                        processed_data.append(
                            {
                                "ts": p[0],
                                "id": f"{can_id:X}",
                                "name": msg_name,
                                "hex": " ".join(payload_parts).upper(),
                                "phys": phys_data,
                                "raw": raw_vals,
                                "def": msg_def,
                            }
                        )

                    except Exception as e:
                        _log(f"Line {line_num}: Unexpected error: {e}", "ERROR")
                        skipped_count += 1

            _log(f"Finished. Parsed: {len(processed_data)} | Skipped: {skipped_count}")

        except Exception as e:
            _log(f"Fatal File Access Error: {e}", "CRITICAL")

        return processed_data
