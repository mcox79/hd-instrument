"""Salvage tool: parse runner-log-style rows from hrr_depth_budget_curve_v1
(Dim I A2 Donoho-Tanner probe) after USER-authorized kill at ~8h40m elapsed.

Log format:
    [seed=S IDX/168] <variant>_V<V>_k<k>_M<M>_<cleanup>: n=N hit=H recall=R wall=Ws

Config header rows are skipped. Only seed_7 has data (kill hit at cell 167/168
of seed_7; seeds 13/19 never started).

Writes:
    data/exp_hrr_depth_budget_curve_v1/partial_metrics.json

ASCII-only. Local read/write only.
"""
from __future__ import annotations
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXP_DIR = REPO / "data" / "exp_hrr_depth_budget_curve_v1"
LOG_PATH = EXP_DIR / "hrr_depth_budget_curve_v1.log"
OUT_PATH = EXP_DIR / "partial_metrics.json"

ROW_RE = re.compile(
    r"^\[seed=(?P<seed>\d+)\s+(?P<idx>\d+)/(?P<total>\d+)\]\s+"
    r"(?P<arm>[A-Za-z0-9_]+):\s+"
    r"n=(?P<n>\d+)\s+hit=(?P<hit>\d+)\s+recall=(?P<recall>[0-9.]+)\s+"
    r"wall=(?P<wall>[0-9.]+)s\s*$"
)
ARM_RE = re.compile(
    r"^(?P<variant>ELEM_BIPOLAR|FHRR_CC)_V(?P<V>\d+)_k(?P<k>\d+)"
    r"_M(?P<M>\d+)_(?P<cleanup>OFF|ON)$"
)


def parse_arm(name: str) -> dict:
    m = ARM_RE.match(name)
    if not m:
        return {"arm_raw": name, "parse_error": True}
    return {
        "arm_raw": name,
        "variant": m.group("variant"),
        "V": int(m.group("V")),
        "k": int(m.group("k")),
        "M": int(m.group("M")),
        "cleanup": m.group("cleanup"),
    }


def main() -> int:
    if not LOG_PATH.exists():
        print(f"MISSING log: {LOG_PATH}")
        return 1
    per_arm = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            m = ROW_RE.match(line.strip())
            if not m:
                continue
            arm_fields = parse_arm(m.group("arm"))
            per_arm.append({
                "seed": int(m.group("seed")),
                "idx": int(m.group("idx")),
                "arms_per_seed": int(m.group("total")),
                "arm_name": m.group("arm"),
                **arm_fields,
                "n": int(m.group("n")),
                "hit": int(m.group("hit")),
                "recall": float(m.group("recall")),
                "wall_s": float(m.group("wall")),
                "arm_status": "OK",
            })
    seeds_seen = sorted({r["seed"] for r in per_arm})
    expected_total = 168 * 3  # 504 arms across 3 seeds
    salvage = {
        "verdict": "SALVAGE_PARTIAL",
        "verdict_msg": (
            f"USER-authorized kill at ~8h40m elapsed; "
            f"{len(per_arm)}/{expected_total} arms recovered from runner log; "
            f"seed coverage={seeds_seen} (seeds 13/19 never ran); "
            f"Dim I A2 Donoho-Tanner probe SURFACE preserved for seed_7."
        ),
        "summary": (
            f"hrr_depth_budget_curve_v1 kill+salvage arms={len(per_arm)}/504 "
            f"seeds={seeds_seen}"
        ),
        "elapsed_s": sum(r["wall_s"] for r in per_arm),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "run_mode": "full",
        "anchor_name": "hrr_depth_budget_curve_v1",
        "salvaged_from": "runner_log",
        "salvage_source": str(LOG_PATH.relative_to(REPO)),
        "n_arms_salvaged": len(per_arm),
        "n_arms_expected": expected_total,
        "seed_coverage": "seed_7_only" if seeds_seen == [7] else str(seeds_seen),
        "seeds_seen": seeds_seen,
        "seeds_missing": [s for s in (7, 13, 19) if s not in seeds_seen],
        "per_arm": per_arm,
        "salvage_note": (
            "Reconstructed from runner stdout log after USER-authorized kill. "
            "Single-seed coverage (seed_7 only) means no CV / no error bars, "
            "but Donoho-Tanner cliff surface shape (variant x cleanup x k x M) "
            "is preserved for the 167/168 arms that ran. Skunkworks may "
            "atomize as MM (mechanism candidate) not CG (chain-grade)."
        ),
    }
    tmp = OUT_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(salvage, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(OUT_PATH))
    print(f"SALVAGED {len(per_arm)}/{expected_total} arms -> {OUT_PATH.relative_to(REPO)}")
    print(f"seeds_seen={seeds_seen}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
