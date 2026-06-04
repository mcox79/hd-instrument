"""cornerstone batch aggregator: read C1/C2/C3 cell metrics, emit batch verdict.

Reads the three per-cell metrics.json (cornerstone C1 post-processor + cornerstone
C2 + cornerstone C3) and emits a single batch-level verdict per the routing
aggregate gate:
  - ALL 3 HARD_PASS  -> batch HARD_PASS, Tier 1 frontier validation anchored
  - 2 of 3 HARD_PASS -> batch MIDDLE_BAND, partial validation
  - 0-1 HARD_PASS    -> batch HARD_FAIL, substantial reassessment

Idempotent + crash-tolerant: missing per-cell metrics are tagged FAILED_SETUP
and counted as non-HP in the aggregate.

ASCII-only. No em-dash.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import json
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

BATCH_ANCHOR = "cornerstone_c1_c2_c3_aggregate_llama_3_1_8b_v1_h100"

CELL_ANCHORS = {
    "C1": "substrate_hyperprobe_llama_3_1_8b_val_sim_replication_v1_h100",
    "C2": "substrate_deletion_cert_llama_3_1_8b_v1_h100",
    "C3": "substrate_drift_detection_refusal_benign_llama_3_1_8b_v1_h100",
}


def _read_cell(cell: str, anchor: str) -> dict:
    p = REPO / "data" / f"exp_{anchor}" / "metrics.json"
    if not p.exists():
        return {
            "cell": cell,
            "anchor": anchor,
            "verdict": "FAILED_SETUP",
            "verdict_msg": f"{cell} metrics.json not found at {p.relative_to(REPO)}",
            "path": str(p),
            "found": False,
        }
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
        m["cell"] = cell
        m["anchor"] = anchor
        m["path"] = str(p)
        m["found"] = True
        return m
    except Exception as e:
        return {
            "cell": cell,
            "anchor": anchor,
            "verdict": "FAILED_SETUP",
            "verdict_msg": f"{cell} metrics.json could not be parsed: {e}",
            "path": str(p),
            "found": False,
            "parse_error": str(e),
        }


def _classify_batch(verdicts: list) -> str:
    hp = sum(1 for v in verdicts if v == "HARD_PASS")
    if hp == 3:
        return "HARD_PASS"
    if hp == 2:
        return "MIDDLE_BAND"
    return "HARD_FAIL"


def _batch_msg(batch_verdict: str, cells: list) -> str:
    hp = sum(1 for c in cells if c["verdict"] == "HARD_PASS")
    mid = sum(1 for c in cells if c["verdict"] == "MIDDLE_BAND")
    hf = sum(1 for c in cells if c["verdict"] == "HARD_FAIL")
    failed = sum(1 for c in cells if c["verdict"] == "FAILED_SETUP")
    head = (f"Cornerstone batch (C1 hyperprobe + C2 deletion + C3 drift) at "
            f"Llama-3.1-8B frontier scale: "
            f"{hp} HARD_PASS / {mid} MIDDLE / {hf} HARD_FAIL / {failed} FAILED_SETUP. ")
    if batch_verdict == "HARD_PASS":
        tail = ("All three Tier 1 audit primitives empirically validated at 8B "
                "frontier scale. Cap_map founding: substrate audit primitive "
                "stack works at industrial LLM size. Pair with Phase 0.5 v1 "
                "Rung A (1B) for two-scale empirical anchor.")
    elif batch_verdict == "MIDDLE_BAND":
        partial_cells = [c["cell"] for c in cells if c["verdict"] != "HARD_PASS"]
        tail = (f"Partial frontier validation: cells {partial_cells} did not "
                f"reach HARD_PASS. Identify which audit primitive needs "
                f"scale-aware refinement before retrying.")
    else:
        failing = [c["cell"] for c in cells if c["verdict"] in ("HARD_FAIL", "FAILED_SETUP")]
        tail = (f"Substantial Tier 1 reassessment needed; cells {failing} "
                f"failed at frontier scale. Identify which BARRIER 8B exposes "
                f"per-cell.")
    return head + tail


def main() -> int:
    t0 = time.monotonic()
    out_dir = get_output_dir(BATCH_ANCHOR)
    out_dir.mkdir(parents=True, exist_ok=True)

    cells = []
    for cell_id, anchor in CELL_ANCHORS.items():
        m = _read_cell(cell_id, anchor)
        cells.append({
            "cell": cell_id,
            "anchor": anchor,
            "verdict": m.get("verdict", "UNKNOWN"),
            "verdict_msg": m.get("verdict_msg", ""),
            "found": m.get("found", False),
            "elapsed_s": m.get("elapsed_s"),
            "summary": m.get("summary"),
        })
        print(f"  {cell_id} ({anchor}): {m.get('verdict', 'UNKNOWN')}", flush=True)

    verdicts = [c["verdict"] for c in cells]
    batch_verdict = _classify_batch(verdicts)
    batch_msg = _batch_msg(batch_verdict, cells)
    print(f"BATCH verdict = {batch_verdict}", flush=True)
    print(f"BATCH msg = {batch_msg}", flush=True)

    metrics = {
        "anchor": BATCH_ANCHOR,
        "verdict": batch_verdict,
        "verdict_msg": batch_msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": {
            "n_HARD_PASS": sum(1 for v in verdicts if v == "HARD_PASS"),
            "n_MIDDLE_BAND": sum(1 for v in verdicts if v == "MIDDLE_BAND"),
            "n_HARD_FAIL": sum(1 for v in verdicts if v == "HARD_FAIL"),
            "n_FAILED_SETUP": sum(1 for v in verdicts if v == "FAILED_SETUP"),
            "cells": cells,
        },
        "cornerstone_batch": True,
    }
    write_metrics(out_dir, metrics)
    print(f"wrote batch metrics.json -> {out_dir}/metrics.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
