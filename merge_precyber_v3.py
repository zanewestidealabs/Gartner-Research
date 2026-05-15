"""
merge_precyber_v3.py — Merge researched new vendors back into 3-0 SVC Pricing.json
====================================================================================

Reads:
  - Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json  (live file with 87 vendors)
  - Preemptive Cybersecurity Vendor 3-1 New Vendors.json  (freshly researched records)

For each vendor in 3-1, replaces or merges into the matching record in 3-0.
Writes the updated 3-0 in-place (with a dated backup first).

Usage:
  python merge_precyber_v3.py           # merge and overwrite 3-0
  python merge_precyber_v3.py --dry-run # show what would be merged, no write
"""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT      = Path(__file__).resolve().parent
LIVE_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
NEW_FILE  = ROOT / "Preemptive Cybersecurity Vendor 3-1 New Vendors.json"
BACKUP_DIR = ROOT / "research" / "backups"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source", type=str, default=None,
                        help="Override source file (default: 3-1 New Vendors.json)")
    args = parser.parse_args()

    source_file = ROOT / args.source if args.source else NEW_FILE

    live = json.loads(LIVE_FILE.read_text(encoding="utf-8"))
    new_vendors = json.loads(source_file.read_text(encoding="utf-8"))

    # Index new vendors by name
    new_by_name = {v["vendor"]: v for v in new_vendors}

    updated = 0
    result = []
    for vendor in live:
        name = vendor.get("vendor", "")
        if name in new_by_name:
            merged = {**vendor, **new_by_name[name]}  # new data overwrites seed fields
            result.append(merged)
            updated += 1
            print(f"  MERGED: {name}")
        else:
            result.append(vendor)

    print(f"\nTotal merged: {updated} / {len(new_vendors)} new vendor records")
    print(f"Total vendors in output: {len(result)}")

    if args.dry_run:
        print("\n[DRY-RUN] No files written.")
        return

    # Backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"3-0 SVC Pricing BACKUP {ts}.json"
    shutil.copy2(LIVE_FILE, backup)
    print(f"\nBackup saved: {backup.name}")

    # Write
    LIVE_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated: {LIVE_FILE.name}")


if __name__ == "__main__":
    main()
