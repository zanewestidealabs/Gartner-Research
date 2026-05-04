"""
Normalize score dictionaries in the PreCyber v3-0 vendor data.

Problem: SVC sub-pillar scores (SVC-01..04) and -05 sub-pillars (EXM-05, AMT-05,
ADR-05, PPM-05) exist in sub_pillar_scores_current (24 keys) but NOT in
sub_pillar_scores_validated (16 keys) or sub_pillar_scores_v2_researched (16 keys).
The UI defaults to 'validated' mode, causing these scores to display as '-'.

Fix: Merge missing sub-pillar scores from sub_pillar_scores_current into all
older score dicts. Similarly merge SVC pillar score from pillar_scores into
older pillar score dicts.
"""
import json
import os

VENDOR_FILE = "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"

def normalize():
    filepath = os.path.join(os.path.dirname(__file__), VENDOR_FILE)
    with open(filepath, "r", encoding="utf-8-sig") as f:
        vendors = json.load(f)

    stats = {"vendors": 0, "sub_pillar_merges": 0, "pillar_merges": 0}

    for v in vendors:
        stats["vendors"] += 1
        name = v.get("vendor", "?")

        # Source of truth: sub_pillar_scores_current (24 keys) and pillar_scores (5 keys)
        current_subs = v.get("sub_pillar_scores_current", {})
        current_pillars = v.get("pillar_scores", {})

        if not current_subs:
            print(f"  SKIP {name}: no sub_pillar_scores_current")
            continue

        # Target sub-pillar dicts to backfill
        sub_targets = [
            "sub_pillar_scores_validated",
            "sub_pillar_scores_v2_researched",
        ]
        for key in sub_targets:
            target = v.get(key)
            if target is None:
                continue
            before = len(target)
            for sid, score in current_subs.items():
                if sid not in target:
                    target[sid] = score
                    stats["sub_pillar_merges"] += 1
            after = len(target)
            if after > before:
                print(f"  {name}: {key} {before} -> {after} keys")

        # Target pillar dicts to backfill
        pillar_targets = [
            "pillar_scores_validated",
            "pillar_scores_v2_researched",
        ]
        for key in pillar_targets:
            target = v.get(key)
            if target is None:
                continue
            for code, score in current_pillars.items():
                if code not in target:
                    target[code] = score
                    stats["pillar_merges"] += 1
                    print(f"  {name}: {key} added {code}={score}")

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {stats['vendors']} vendors, "
          f"{stats['sub_pillar_merges']} sub-pillar merges, "
          f"{stats['pillar_merges']} pillar merges")

    # Verify
    with open(filepath, "r", encoding="utf-8") as f:
        vendors = json.load(f)
    sample = vendors[0]
    for key in ["sub_pillar_scores_validated", "sub_pillar_scores_v2_researched", "sub_pillar_scores_current"]:
        d = sample.get(key, {})
        svc_keys = sorted([k for k in d if k.startswith("SVC")])
        five_keys = sorted([k for k in d if k.endswith("-05")])
        print(f"  {key}: {len(d)} keys, SVC={svc_keys}, -05={five_keys}")

if __name__ == "__main__":
    normalize()
