"""Salvage tool: extract per-arm p50/p95/p99 data from _heartbeat.jsonl of the
v1 stage2_commercial_M_latency_percentiles cell (all 3 seeds) and write
partial_metrics.json siblings so the surviving data is a usable MM candidate.

v1 cells timed out at 3600s having completed 7/9 arms per seed (M=1M torch_cpu
and M=1M torch_cuda missing). metrics.json was never written because it only
lands at end. Heartbeat rows include p50_us / p99_us / cleanup_recall / build_s
per completed arm -- enough to write a MM-candidate partial_metrics.json.

Usage:
    python tools/salvage_commercial_M_latency_v1_heartbeats_to_partial_metrics.py

Writes to:
    data/exp_stage2_commercial_M_latency_percentiles_v1_seed_{7,13,19}/partial_metrics.json

ASCII-only. Read-only w.r.t. remote; local-write only.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEEDS = (7, 13, 19)


def extract_arms_from_heartbeat(hb_path: Path) -> list[dict]:
    """Return list of completed-arm records (rows that include p50_us in extra)."""
    arms = []
    with hb_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            extra = row.get("extra") or {}
            # Completed-arm rows carry p50_us; arm_start rows carry phase="arm_start".
            if "p50_us" not in extra:
                continue
            # Skip SELFTEST arm; only main-sweep arms belong in the salvage.
            arm_name = extra.get("arm", "")
            if arm_name.startswith("SELFTEST_"):
                continue
            arms.append({
                "arm_name": arm_name,
                "M": int(extra["M"]),
                "N": int(extra["N"]),
                "backend": extra["backend"],
                "p50_s": float(extra["p50_us"]) / 1e6,
                "p99_s": float(extra["p99_us"]) / 1e6,
                "cleanup_recall": float(extra["cleanup_recall"]),
                "build_s": float(extra["build_s"]),
                "arm_wall_s": float(row.get("elapsed_s") or 0.0),
                "arm_ts_iso": row.get("ts_iso", ""),
                "arm_status": "OK",
                "source": "heartbeat_salvage_v1_timeout",
            })
    return arms


def main() -> int:
    total_arms = 0
    per_seed_out = {}
    for seed in SEEDS:
        exp_dir = REPO / "data" / f"exp_stage2_commercial_M_latency_percentiles_v1_seed_{seed}"
        hb = exp_dir / "_heartbeat.jsonl"
        if not hb.exists():
            print(f"seed_{seed}: MISSING {hb}")
            continue
        arms = extract_arms_from_heartbeat(hb)
        total_arms += len(arms)
        # Per-arm status summary
        completed = sorted({(a["M"], a["backend"]) for a in arms})
        expected_grid = [(M, b) for M in (100_000, 500_000, 1_000_000)
                         for b in ("numpy", "torch_cpu", "torch_cuda")]
        missing = [(M, b) for M, b in expected_grid if (M, b) not in completed]
        salvage = {
            "verdict": "SALVAGE_PARTIAL",
            "verdict_msg": (f"seed_{seed} v1 cell timed out at 3600s remote; "
                            f"{len(arms)}/9 arms recovered from heartbeat; "
                            f"missing={missing}"),
            "summary": (f"stage2_commercial_M_latency_percentiles_v1 seed_{seed} "
                        f"partial (heartbeat salvage) arms={len(arms)}/9"),
            "elapsed_s": max((a["arm_wall_s"] for a in arms), default=0.0),
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "run_mode": "full",
            "anchor_name": f"stage2_commercial_M_latency_percentiles_v1_seed_{seed}",
            "seed": seed,
            "n_arms_recovered": len(arms),
            "n_arms_expected": 9,
            "missing_arms_M_backend": [
                {"M": M, "backend": b} for M, b in missing
            ],
            "per_arm": arms,
            "salvage_source": str(hb.relative_to(REPO)),
            "salvage_note": (
                "Reconstructed from _heartbeat.jsonl after 3600s remote timeout. "
                "Values are p50 / p99 / recall / build_s per completed arm. "
                "p95 / mean / std / min / max / timings_hash not available "
                "(heartbeat schema logs only summary percentiles). "
                "Verdict gates from v1 pre-reg can be computed for the 7 "
                "recovered arms except HP_CUDA_SPEEDUP at M=1M (requires the "
                "missing M=1M torch_cuda arm) and HP_M1M_UNDER_100MS (same)."
            ),
        }
        out_path = exp_dir / "partial_metrics.json"
        tmp = exp_dir / "partial_metrics.json.tmp"
        tmp.write_text(json.dumps(salvage, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_path))
        print(f"seed_{seed}: {len(arms)}/9 arms -> {out_path.relative_to(REPO)}")
        per_seed_out[seed] = str(out_path)

    print(f"\nTotal arms salvaged across {len(SEEDS)} seeds: {total_arms} "
          f"(expected {9 * len(SEEDS)} = 27)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
