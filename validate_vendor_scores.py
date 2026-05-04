import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "schema3-3.json"
INPUT_PATH = ROOT / "Vendor 3-7.json"
OUTPUT_PATH = ROOT / "Vendor 4-0 Validated.json"

PILLARS = ["PLA", "INV", "REM", "PMG", "LAW"]


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isnan(float(value))


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if _is_number(value):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _round_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return round(value / step) * step


def load_schema_subpillars(schema_path: Path) -> Tuple[List[str], Dict[str, str]]:
    """Return ordered list of sub-pillar ids and id->name map."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    taxonomy = schema.get("dfir_capability_taxonomy_v3.2", {})
    pillars = taxonomy.get("pillars", {})

    subpillar_ids: List[str] = []
    subpillar_names: Dict[str, str] = {}

    for pillar_key in pillars:
        pillar = pillars[pillar_key]
        subs = pillar.get("sub_capabilities", [])
        for sub in subs:
            sid = sub.get("id")
            name = sub.get("name")
            if isinstance(sid, str) and sid:
                subpillar_ids.append(sid)
                if isinstance(name, str) and name:
                    subpillar_names[sid] = name

    # Ensure we always have exactly the expected 20 in a stable order
    # Prefer schema order, but normalize grouping by PLA/INV/REM/PMG/LAW then 01-04.
    def sort_key(code: str) -> Tuple[int, int]:
        m = re.match(r"^(PLA|INV|REM|PMG|LAW)-(0?[1-9]\d*)$", code)
        if not m:
            return (999, 999)
        pillar, idx = m.group(1), int(m.group(2))
        return (PILLARS.index(pillar), idx)

    subpillar_ids = sorted(set(subpillar_ids), key=sort_key)
    return subpillar_ids, subpillar_names


def extract_current_subpillar_scores(vendor: Dict[str, Any], subpillar_ids: List[str]) -> Dict[str, float | None]:
    """Extract current scores from vendor.granular_mapping (supports nested dict per pillar)."""
    granular = vendor.get("granular_mapping") or {}
    current: Dict[str, float | None] = {}

    # granular_mapping is expected like {"PLA": {"PLA-01": 3, ...}, ...}
    for sid in subpillar_ids:
        pillar = sid.split("-")[0]
        value = None
        if isinstance(granular, dict):
            pillar_obj = granular.get(pillar)
            if isinstance(pillar_obj, dict):
                value = _to_float(pillar_obj.get(sid))
            # fallback: sometimes stored flat
            if value is None:
                value = _to_float(granular.get(sid))
        current[sid] = value

    return current


def validate_scores(
    current: Dict[str, float | None],
    vendor: Dict[str, Any],
    subpillar_ids: List[str],
    *,
    min_score: float = 0.0,
    max_score: float = 5.0,
    round_to: float = 0.25,
    pillar_tolerance: float = 0.25,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """Return validated sub-pillar scores and a metadata block describing changes."""

    notes: List[str] = []
    changes: Dict[str, Any] = {"filled_missing": [], "clamped": [], "pillar_adjustments": {}}

    # Start with clamped/filled current values
    validated: Dict[str, float] = {}

    # If missing, default to 0 (unknown/no evidence)
    for sid in subpillar_ids:
        v = current.get(sid)
        if v is None:
            validated[sid] = 0.0
            changes["filled_missing"].append(sid)
            continue
        v2 = _clamp(v, min_score, max_score)
        if v2 != v:
            changes["clamped"].append({"id": sid, "from": v, "to": v2})
        validated[sid] = v2

    # Pillar alignment: if pillar_scores exist, nudge the 4 sub-pillars to match the pillar score average
    pillar_scores = vendor.get("pillar_scores") or {}
    if not isinstance(pillar_scores, dict):
        pillar_scores = {}

    for pillar in PILLARS:
        pillar_score = _to_float(pillar_scores.get(pillar))
        if pillar_score is None:
            continue
        pillar_score = _clamp(pillar_score, min_score, max_score)

        pillar_subs = [sid for sid in subpillar_ids if sid.startswith(pillar + "-")]
        if len(pillar_subs) != 4:
            continue

        current_avg = sum(validated[sid] for sid in pillar_subs) / 4.0
        delta = pillar_score - current_avg

        if abs(delta) <= pillar_tolerance:
            continue

        # Apply a uniform delta to keep relative spacing and re-clamp.
        before = {sid: validated[sid] for sid in pillar_subs}
        after = {}
        for sid in pillar_subs:
            after[sid] = _clamp(validated[sid] + delta, min_score, max_score)

        # Recompute average after clamp; if clamps prevented alignment, we accept best effort.
        for sid in pillar_subs:
            validated[sid] = after[sid]

        changes["pillar_adjustments"][pillar] = {
            "pillar_score": pillar_score,
            "sub_avg_before": round(current_avg, 4),
            "delta_applied": round(delta, 4),
            "before": before,
            "after": after,
        }
        notes.append(f"Adjusted {pillar} sub-pillars by {delta:+.2f} to align with pillar_score.")

    # Round to step after all adjustments
    for sid in subpillar_ids:
        validated[sid] = _round_step(validated[sid], round_to)
        validated[sid] = _clamp(validated[sid], min_score, max_score)

    metadata = {"notes": notes, "changes": changes}
    return validated, metadata


def main() -> None:
    subpillar_ids, subpillar_names = load_schema_subpillars(SCHEMA_PATH)

    vendors = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if not isinstance(vendors, list):
        raise SystemExit("Vendor 3-7.json is not a list")

    out: List[Dict[str, Any]] = []

    for vendor in vendors:
        if not isinstance(vendor, dict):
            continue

        current = extract_current_subpillar_scores(vendor, subpillar_ids)
        validated, meta = validate_scores(current, vendor, subpillar_ids)

        # Build a normalized per-vendor block. Keep existing structure and add validated fields.
        vendor_out = dict(vendor)

        vendor_out["sub_pillar_scores_current"] = current
        vendor_out["sub_pillar_scores_validated"] = validated
        vendor_out["sub_pillar_schema_labels"] = {sid: subpillar_names.get(sid, sid) for sid in subpillar_ids}

        # Pillar scores should be the average of validated sub-pillars.
        pillar_scores_validated: Dict[str, float] = {}
        for pillar in PILLARS:
            pillar_subs = [sid for sid in subpillar_ids if sid.startswith(pillar + "-")]
            if not pillar_subs:
                continue
            avg = sum(validated[sid] for sid in pillar_subs) / len(pillar_subs)
            pillar_scores_validated[pillar] = round(avg, 2)
        vendor_out["pillar_scores_validated"] = pillar_scores_validated

        # Also provide a validated granular_mapping structure mirroring the app’s expected layout.
        granular_validated: Dict[str, Dict[str, float]] = {}
        for pillar in PILLARS:
            granular_validated[pillar] = {
                sid: validated[sid] for sid in subpillar_ids if sid.startswith(pillar + "-")
            }
        vendor_out["granular_mapping_validated"] = granular_validated

        vendor_out["scoring_validation"] = meta

        out.append(vendor_out)

    OUTPUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.name} with {len(out)} vendors")


if __name__ == "__main__":
    main()
