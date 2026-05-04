#!/usr/bin/env python3
"""Extract 'Source: <url>' from capability_analysis into a dedicated field.

- Adds vendor['capability_analysis_source'] when a URL is found.
- Removes the 'Source: ...' fragment from vendor['capability_analysis'].
- Processes all vendor datasets in the current directory whose filenames start with 'vendor' (case-insensitive) and end with '.json'.

Usage:
  python extract_capability_analysis_source.py
  python extract_capability_analysis_source.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

URL_RE = re.compile(r"https?://[^\s\]\)\}\>\"']+", re.IGNORECASE)
SOURCE_LINE_RE = re.compile(r"\s*source\s*:\s*(https?://\S+)", re.IGNORECASE)
SOURCE_ANY_RE = re.compile(r"\s*source\s*:\s*https?://\S+", re.IGNORECASE)


def _load_json(path: Path) -> Any:
    # Some files may contain a UTF-8 BOM.
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError:
        return json.loads(path.read_text(encoding="utf-8"))


def _dump_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _extract_source(text: str) -> Tuple[str, Optional[str]]:
    if not isinstance(text, str) or not text.strip():
        return text, None

    # Prefer explicit "Source:" marker.
    m = SOURCE_LINE_RE.search(text)
    url: Optional[str] = None
    if m:
        raw = m.group(1)
        url_match = URL_RE.search(raw)
        if url_match:
            url = url_match.group(0).rstrip(".,;)")
    else:
        # Fallback: if it literally contains "Source:" but regex didn't match cleanly.
        if re.search(r"\bsource\s*:\b", text, re.IGNORECASE):
            url_match = URL_RE.search(text)
            if url_match:
                url = url_match.group(0).rstrip(".,;)")

    if not url:
        return text, None

    # Remove the Source: ... fragment (and surrounding whitespace/newlines).
    cleaned = SOURCE_ANY_RE.sub("", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = "\n".join([ln.rstrip() for ln in cleaned.splitlines()]).strip()

    return cleaned, url


def _coerce_vendor_list(data: Any) -> Optional[List[Dict[str, Any]]]:
    if isinstance(data, list) and all(isinstance(x, dict) for x in data):
        return data  # type: ignore[return-value]
    if isinstance(data, dict):
        # Some datasets may be wrapped; pick the first list value.
        for v in data.values():
            if isinstance(v, list) and all(isinstance(x, dict) for x in v):
                return v  # type: ignore[return-value]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract 'Source: <url>' from capability_analysis into capability_analysis_source")
    ap.add_argument("--dry-run", action="store_true", help="Analyze and report, but do not write files")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    files = sorted(
        [p for p in root.iterdir() if p.is_file() and p.suffix.lower() == ".json" and p.name.lower().startswith("vendor")]
    )

    if not files:
        print("No vendor*.json files found.")
        return 0

    total_files = 0
    total_vendors = 0
    extracted = 0
    changed_text = 0

    for path in files:
        try:
            data = _load_json(path)
        except json.JSONDecodeError as e:
            print(f"SKIP (invalid JSON): {path.name} ({e})")
            continue
        vendors = _coerce_vendor_list(data)
        if vendors is None:
            continue

        total_files += 1
        file_changed = False

        for vendor in vendors:
            total_vendors += 1
            text = vendor.get("capability_analysis")
            if not isinstance(text, str):
                continue

            cleaned, url = _extract_source(text)
            if not url:
                continue

            prev = vendor.get("capability_analysis_source")
            if prev != url:
                vendor["capability_analysis_source"] = url
                extracted += 1
                file_changed = True

            if cleaned != text:
                vendor["capability_analysis"] = cleaned
                changed_text += 1
                file_changed = True

        if file_changed and not args.dry_run:
            _dump_json(path, data)
            print(f"Updated: {path.name}")

    print(f"Scanned files: {total_files}")
    print(f"Vendors scanned: {total_vendors}")
    print(f"Sources extracted: {extracted}")
    print(f"Analysis text cleaned: {changed_text}")
    if args.dry_run:
        print("Dry run: no files were written")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
