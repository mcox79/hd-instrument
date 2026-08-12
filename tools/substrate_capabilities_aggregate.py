"""Aggregate substrate_capability_registry.jsonl (per-test rows) into per-capability view.

Reads:
  data/substrate_capability_registry.jsonl   (4449+ per-test rows)
  data/substrate_capability_descriptions.json (editable mouseover descriptions)

Writes:
  data/substrate_capabilities_view.json       (one row per capability_family,
                                                with click-to-expand per-test array)

Schema of view rows:
  {capability_family, stage, tier, tier_evidence, peak_assessment, peak_explanation,
   phase_pct, phase_axes_observed, n_tests, n_tests_24h, latest_test_ts,
   verdict_distribution, description, axes_typical, tests: [per-test array]}

No silent excepts (META_RULE_J): record-and-halt on parse errors.
Atomic-write via tmp+replace (META_RULE_idempotent).

Usage:
  python tools/substrate_capabilities_aggregate.py
  (run via scheduled task every 15 min; no args; idempotent)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO / "data" / "substrate_capability_registry.jsonl"
DESC_PATH = REPO / "data" / "substrate_capability_descriptions.json"
VIEW_PATH = REPO / "data" / "substrate_capabilities_view.json"


def _iso_to_dt(iso_str: str) -> datetime | None:
    """Parse ISO-8601 to UTC datetime; returns None on parse fail."""
    if not iso_str:
        return None
    s = iso_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _load_registry(path: Path) -> list[dict]:
    """Read all rows; no silent except — halt on parse error with file:line."""
    rows = []
    if not path.exists():
        raise FileNotFoundError(f"registry missing: {path}")
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{lineno} JSON parse fail: {e}")
    return rows


def _load_descriptions(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _tier_from_history(tests: list[dict], now: datetime) -> tuple[str, str]:
    """Derive tier from verdict history per design heuristic.

    Returns (tier, evidence_str).
      chain-grade: >=1 HARD_PASS at run_mode=full
      measured-mechanism: >=1 HARD_PASS at smoke, but full HARD_FAIL or saturation
      honest-negative: >=3 HARD_FAIL with no PASS in last 30d
      exploring: default
    """
    full_hp = [t for t in tests if t.get("verdict") == "HARD_PASS" and t.get("run_mode") == "full"]
    if full_hp:
        # Sort newest first
        full_hp.sort(key=lambda t: t.get("mtime") or "", reverse=True)
        latest = full_hp[0]
        return ("chain-grade", f"HARD_PASS at full ({latest.get('anchor_name','?')} @ {latest.get('mtime','?')})")

    smoke_hp = [t for t in tests if t.get("verdict") in ("HARD_PASS", "SMOKE_HARD_PASS") and t.get("run_mode") == "smoke"]
    saturated = any(t.get("saturation") for t in tests)
    full_hf = [t for t in tests if t.get("verdict") == "HARD_FAIL" and t.get("run_mode") == "full"]
    if smoke_hp and (saturated or full_hf):
        latest = smoke_hp[0]
        cause = "saturated" if saturated else "full HARD_FAIL"
        return ("measured-mechanism", f"smoke HARD_PASS ({latest.get('anchor_name','?')}); {cause}")

    hf = [t for t in tests if t.get("verdict") == "HARD_FAIL"]
    any_pass = [t for t in tests if "HARD_PASS" in (t.get("verdict") or "") or "PASS" == t.get("verdict")]
    if len(hf) >= 3 and not any_pass:
        return ("honest-negative", f">=3 HARD_FAIL no PASS")
    if smoke_hp:
        return ("measured-mechanism", f"smoke HARD_PASS ({smoke_hp[0].get('anchor_name','?')}); no full yet")

    return ("exploring", f"{len(tests)} tests; no chain-grade-eligible verdict")


def _peak_assessment(tests: list[dict]) -> tuple[str, str]:
    """Color + explanation. Heuristic per design doc.

    Returns (color_token, explanation).
      blue:  saturated default (metric>=0.95 + saturation=true + no harder-axis test)
      green: mid-range (metric in [0.50, 0.95] OR harder-axis discriminated)
      yellow: just-above-bar (metric in [0.30, 0.50])
      gray:  no peak metric available
    """
    # Mine per_arm_metrics for max float value seen
    peak = -1.0
    peak_anchor = None
    any_saturated = False
    for t in tests:
        if t.get("saturation"):
            any_saturated = True
        per_arm = t.get("per_arm_metrics") or {}
        for k, v in per_arm.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                # Skip obviously-non-metric keys (seeds, dims, counts)
                kl = k.lower()
                if any(skip in kl for skip in ("seed", "n_", "_n", "elapsed", "size", "dim", "epoch", "k=", "_k", "depth", "rate", "freq", "ts")):
                    if not any(want in kl for want in ("acc", "lift", "pass_rate", "top1", "cosine", "frac", "gap", "ratio")):
                        continue
                if 0.0 <= float(v) <= 1.0 and float(v) > peak:
                    peak = float(v)
                    peak_anchor = t.get("anchor_name")
    if peak < 0:
        return ("gray", "no scalar [0,1] metric in per_arm_metrics")
    if peak >= 0.95 and any_saturated:
        return ("blue", f"peak={peak:.3f} saturated ({peak_anchor})")
    if peak >= 0.50:
        return ("green", f"peak={peak:.3f} ({peak_anchor})")
    if peak >= 0.30:
        return ("yellow", f"peak={peak:.3f} just-above-bar ({peak_anchor})")
    return ("gray", f"peak={peak:.3f} below-bar ({peak_anchor})")


def _phase_coverage(tests: list[dict]) -> tuple[int, dict, bool]:
    """Aggregate axes_tested across all tests; return (phase_pct, axes_dict, cliff_found).

    Rubric:
      ~5%: single point only / 0 axes swept
      ~25%: one axis with >=3 distinct values
      ~50%: two axes with >=3 values each
      ~80%: 3+ axes with >=3 values each AND at least one HARD_FAIL boundary
    """
    axes_values: dict[str, set] = defaultdict(set)
    has_hf_boundary = False
    for t in tests:
        ax = t.get("axes_tested") or {}
        if isinstance(ax, dict):
            for k, v in ax.items():
                # Only hashable scalars
                if isinstance(v, (int, float, str, bool)):
                    axes_values[k].add(v)
        if t.get("verdict") == "HARD_FAIL":
            has_hf_boundary = True

    swept_axes = sum(1 for k, vs in axes_values.items() if len(vs) >= 3)
    axes_summary = {k: sorted(list(vs), key=lambda x: (type(x).__name__, x))[:10] for k, vs in axes_values.items() if len(vs) >= 2}

    if swept_axes >= 3 and has_hf_boundary:
        pct = 80
    elif swept_axes >= 2:
        pct = 50
    elif swept_axes >= 1:
        pct = 25
    else:
        pct = 5
    return (pct, axes_summary, has_hf_boundary)


def aggregate(now: datetime | None = None) -> dict:
    if now is None:
        now = datetime.now(tz=timezone.utc)
    rows = _load_registry(REGISTRY_PATH)
    descs = _load_descriptions(DESC_PATH)

    by_family: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        fam = r.get("capability_family") or "other"
        by_family[fam].append(r)

    out_rows = []
    for fam, tests in by_family.items():
        # Pick the dominant stage (mode; should be uniform per family)
        stages = Counter(t.get("stage") for t in tests if t.get("stage") is not None)
        stage = stages.most_common(1)[0][0] if stages else -1

        verdict_dist = Counter(t.get("verdict") or "?" for t in tests)

        tier, tier_evidence = _tier_from_history(tests, now)
        peak_color, peak_expl = _peak_assessment(tests)
        phase_pct, phase_axes, cliff = _phase_coverage(tests)

        # Latest test timestamp + last-24h count
        latest_ts = None
        n_24h = 0
        for t in tests:
            mt = t.get("mtime") or t.get("ts_iso")
            dt = _iso_to_dt(mt)
            if dt is None:
                continue
            if latest_ts is None or dt > latest_ts:
                latest_ts = dt
            if (now - dt).total_seconds() < 86400:
                n_24h += 1

        # Description from config; fallback to family-name
        desc_entry = descs.get(fam) or {}
        description = desc_entry.get("description") or f"Capability family '{fam}' ({len(tests)} tests across {len(phase_axes)} axes); no curated description yet."
        axes_typical = desc_entry.get("axes_typical") or list(phase_axes.keys())[:4]
        stage_label = desc_entry.get("stage_label") or f"Stage {stage}"

        # Per-test array (compact)
        compact_tests = []
        # Sort newest first
        tests_sorted = sorted(tests, key=lambda t: t.get("mtime") or "", reverse=True)
        for t in tests_sorted[:50]:  # cap at 50 most recent for table row
            compact_tests.append({
                "anchor_name": t.get("anchor_name"),
                "verdict": t.get("verdict"),
                "run_mode": t.get("run_mode"),
                "axes_tested": t.get("axes_tested") or {},
                "saturation": t.get("saturation"),
                "elapsed_s": t.get("elapsed_s"),
                "mtime": t.get("mtime"),
                "verdict_msg_head": (t.get("verdict_msg_head") or "")[:200],
            })

        out_rows.append({
            "capability_family": fam,
            "stage": stage,
            "stage_label": stage_label,
            "tier": tier,
            "tier_evidence": tier_evidence,
            "peak_assessment": peak_color,
            "peak_explanation": peak_expl,
            "phase_pct": phase_pct,
            "phase_axes_observed": phase_axes,
            "cliff_found": cliff,
            "n_tests": len(tests),
            "n_tests_24h": n_24h,
            "latest_test_ts": latest_ts.isoformat().replace("+00:00", "Z") if latest_ts else None,
            "verdict_distribution": dict(verdict_dist.most_common(8)),
            "description": description,
            "axes_typical": axes_typical,
            "tests": compact_tests,
            "n_tests_truncated": max(0, len(tests) - 50),
        })

    # Sort: stage ASC (but -1 last), tier (chain-grade first), phase_pct ASC (gap-surface)
    tier_rank = {"chain-grade": 0, "measured-mechanism": 1, "exploring": 2, "honest-negative": 3}
    def sort_key(r):
        s = r["stage"]
        s_eff = 99 if s == -1 else s
        return (s_eff, tier_rank.get(r["tier"], 9), r["phase_pct"])
    out_rows.sort(key=sort_key)

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "n_tests_total": len(rows),
        "n_capabilities": len(out_rows),
        "rows": out_rows,
    }


def _atomic_write_json(path: Path, payload: dict) -> None:
    """tmp + os.replace = atomic on Windows + POSIX."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    payload = aggregate()
    _atomic_write_json(VIEW_PATH, payload)
    print(f"wrote {VIEW_PATH} | n_capabilities={payload['n_capabilities']} n_tests_total={payload['n_tests_total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
