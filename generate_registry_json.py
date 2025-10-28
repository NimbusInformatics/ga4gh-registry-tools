#!/usr/bin/env python3
"""
Convert a spreadsheet of GA4GH service registrations into a JSON array
compatible with the GA4GH Service Registry "services" resource.

Implements Option B: json.dump(..., default=_json_default) to serialize
pandas.Timestamp/datetime objects as ISO 8601 strings (and stringify
unknown types as a last resort).

Usage:
  python generate_registry_json.py \
      --input "DRS Server Registration  (Responses)-2.xlsx" \
      --sheet "Form Responses 1" \
      --config config.yaml \
      --output services.json \
      --drop-empty

Config (YAML):
  - mapping: dict of target JSON dot-path -> source spreadsheet column
             or {"const": "..."} for constants
  - passthrough_columns: list of sheet columns to copy into x-extra:{...}
  - required_fields: list of sheet columns that must be present per-row
  - array_name: if set (e.g., "services"), wrap output in {"services":[...]}

Example mapping keys can include:
  id, name, description, url, version, environment
  type.group, type.artifact, type.version
  organization.id, organization.name, organization.url
"""

import argparse
import json
import os
from typing import Any, Dict, Optional

import datetime as dt
import numpy as np
import pandas as pd
import yaml


# ----------------------------
# JSON helpers
# ----------------------------
def _json_default(o: Any) -> Any:
    """json.dump fallback: datetimes -> ISO 8601; everything else -> str."""
    if isinstance(o, (pd.Timestamp, dt.datetime, dt.date)):
        return pd.to_datetime(o).isoformat()
    # last resort: stringify unknowns
    return str(o)


# ----------------------------
# Dataframe helpers
# ----------------------------
def load_dataframe(path: str, sheet: Optional[str]) -> pd.DataFrame:
    """Load Excel/CSV/TSV into a DataFrame."""
    lower = path.lower()
    if lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(path, sheet_name=sheet)
    if lower.endswith(".csv"):
        return pd.read_csv(path)
    if lower.endswith(".tsv"):
        return pd.read_csv(path, sep="\t")
    # Try Excel by default if unknown
    return pd.read_excel(path, sheet_name=sheet)


# ----------------------------
# Dict utilities
# ----------------------------
def _set_deep(d: Dict[str, Any], path: str, value: Any) -> None:
    """Set a value in nested dict using dot path, creating nested dicts as needed."""
    keys = path.split(".")
    cur = d
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value


def _slugify(key: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in key).strip("-")


# ----------------------------
# Main transform
# ----------------------------
def build_records(
    df: pd.DataFrame,
    mapping: Dict[str, Any],
    passthrough_cols: list[str],
    required_fields: list[str],
    drop_empty: bool,
) -> list[dict]:
    records: list[dict] = []

    for _, row in df.iterrows():
        # Skip rows missing required spreadsheet fields (if configured)
        if required_fields:
            missing = [
                c for c in required_fields
                if pd.isna(row.get(c, None)) or str(row.get(c)).strip() == ""
            ]
            if missing:
                continue

        obj: Dict[str, Any] = {}

        # Apply mapping
        for target_path, rule in mapping.items():
            if isinstance(rule, dict) and "const" in rule:
                val = rule["const"]
            else:
                col = rule
                val = row.get(col, None)

            # Normalize "empties"
            if pd.isna(val):
                val = None

            if isinstance(val, str):
                val = val.strip()

            if drop_empty and (val is None or val == ""):
                continue

            if val is not None and val != "":
                _set_deep(obj, target_path, val)

        # Optional: add x-extra with passthrough columns from the sheet
        xextra: Dict[str, Any] = {}
        for col in passthrough_cols:
            val = row.get(col, None)
            if pd.isna(val) or val is None:
                continue
            if isinstance(val, str):
                val = val.strip()
                if drop_empty and val == "":
                    continue
            key = _slugify(col)
            xextra[key] = val

        # Helpful special-case: parse a "Geolocation (latitude, longitude)" style column
        # to structured x-extra values (lat/lon floats). Keep original too.
        for k in list(xextra.keys()):
            if "geolocation-latitude--longitude" in k and isinstance(xextra[k], str):
                raw = xextra[k]
                try:
                    parts = [p.strip() for p in str(raw).split(",")]
                    if len(parts) == 2:
                        lat = float(parts[0])
                        lon = float(parts[1])
                        xextra["geolocation"] = {"lat": lat, "lon": lon}
                except Exception:
                    pass

        if xextra:
            obj.setdefault("x-extra", {}).update(xextra)

        records.append(obj)

    return records


# ----------------------------
# CLI
# ----------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Spreadsheet -> GA4GH Service Registry JSON")
    ap.add_argument("--input", required=True, help="Path to input spreadsheet (.xlsx/.xls/.csv/.tsv)")
    ap.add_argument("--sheet", default=None, help="Worksheet name (if Excel). Default: first sheet")
    ap.add_argument("--config", required=True, help="YAML config mapping columns -> JSON fields")
    ap.add_argument("--output", required=True, help="Path to write JSON output")
    ap.add_argument("--drop-empty", action="store_true",
                    help="Drop fields with empty/null values from the output objects")
    args = ap.parse_args()

    # Load config
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    mapping: Dict[str, Any] = cfg.get("mapping", {})
    passthrough_cols: list[str] = cfg.get("passthrough_columns", [])
    array_name: Optional[str] = cfg.get("array_name", None)
    required_fields: list[str] = cfg.get("required_fields", [])

    # Load data
    df = load_dataframe(args.input, args.sheet)

    # Build JSON records
    records = build_records(
        df=df,
        mapping=mapping,
        passthrough_cols=passthrough_cols,
        required_fields=required_fields,
        drop_empty=args.drop_empty,
    )

    # Write output; Option B: use default=_json_default to serialize datetimes
    out = {array_name: records} if array_name else records
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=_json_default)

    print(f"Wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()