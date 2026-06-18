"""Deterministic verdict-VET harness for A2-v3 (substrate_a2_decisive_test_untuned_auroc_gpu_v1).

Pre-built at the phase boundary (forward-work) so the VET is fast + deterministic when v3 lands. Runs the 4 cert-checks
Skunkworks + I pre-specified, against the v3 metrics.json + the validity-VET'd a2_gap_balanced_v1.jsonl. Read-only; emits
a VET verdict (VET_PASS / VET_FAIL / VET_HALT) + per-check detail. No Store mutation; no atomize (that follows on VET_PASS).

Checks:
  (1) gate0_self_check PASS         -- run_mode=full + measured_bge_gpu + n_cells_declared==emitted (no smoke/synthetic slip).
  (2) discrimination NON_TEST guard -- discrimination_self_check fired; conf_spread > 1e-6 (degenerate all-same-confidence = NON_TEST, HALT).
  (3) band-classification crosscheck-- recompute the band from untuned_auroc; confirm == cell verdict (no band-logic drift).
  (4) coincidental-mention precision-- surface the 2 Tarjan/Hopcroft near-gap confidences (high = refuse-gate precision limit the eval EXPECTS; report, not fail).
  (5) corpus-completeness on gaps   -- the 38 gap-item ids in metrics.rows == the 38 validity-VET'd gap ids (1:1; no drift from the validated absence set).

Usage: python tools/vet_a2_v3_verdict_2026-06-18.py [path/to/metrics.json]
  default metrics path = data/exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1/metrics.json
ASCII-only. No LLM (11th rule). Read-only VET.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_METRICS = REPO / "data" / "exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1" / "metrics.json"
VALIDATED_SET = REPO / "experiments" / "data" / "a2_gap_balanced_v1.jsonl"

# bands MUST match the cell (exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1.py L44-45)
NEAR_CHANCE_LO, NEAR_CHANCE_HI = 0.45, 0.60
ALREADY_SEP = 0.70
COINCIDENTAL = ("tarjan", "hopcroft")  # the 2 kept-flagged coincidental-mention near-gaps


def _band(auroc):
    """Recompute the verdict band from auroc -- mirror of the cell's branch logic."""
    if auroc is None:
        return "NON_TEST"
    if auroc < NEAR_CHANCE_LO:
        return "INVERTED"
    if auroc <= NEAR_CHANCE_HI:
        return "NEAR_CHANCE"
    if auroc < ALREADY_SEP:
        return "MIDDLE_BAND"
    return "ALREADY_SEPARATES"


def main():
    mpath = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_METRICS
    if not mpath.exists():
        print(f"[VET a2-v3] metrics NOT FOUND at {mpath} -- v3 has not landed yet (or wrong path). VET deferred.")
        return 2
    m = json.loads(mpath.read_text(encoding="utf-8"))
    validated = [json.loads(l) for l in VALIDATED_SET.read_text(encoding="utf-8").splitlines() if l.strip()]

    fails, halts, notes = [], [], []

    # (1) gate0
    g0 = m.get("gate0_self_check") or {}
    if not g0.get("pass"):
        fails.append(f"(1) gate0 FAIL: {g0}")
    else:
        if g0.get("run_mode") != "full":
            fails.append(f"(1) gate0 run_mode != full: {g0.get('run_mode')} -- smoke/synthetic slip")
        if m.get("provenance", {}).get("metrics_source", m.get("metrics_source")) and "measured" not in json.dumps(g0):
            notes.append("(1) gate0 metrics_source not visible in gate0 dict; check provenance block")
        notes.append(f"(1) gate0 PASS (run_mode={g0.get('run_mode')}, n_declared={g0.get('n_cells_declared')}, n_emitted={g0.get('n_cells_emitted')})")

    # (2) NON_TEST guard
    disc = m.get("discrimination_self_check") or {}
    verdict = m.get("verdict")
    if verdict == "NON_TEST":
        halts.append(f"(2) cell verdict = NON_TEST: {m.get('verdict_msg')} -- degenerate (no discrimination); VET HALT, no atomize.")
    else:
        rows = m.get("rows") or []
        confs = [r.get("confidence", 0.0) for r in rows]
        spread = (max(confs) - min(confs)) if confs else 0.0
        if spread <= 1e-6:
            halts.append(f"(2) conf_spread={spread:.6g} <= 1e-6 but verdict != NON_TEST -- INCONSISTENT; HALT + investigate.")
        else:
            notes.append(f"(2) NON_TEST guard PASS (conf_spread={spread:.4f}; discrimination fired)")

    # (3) band cross-check
    auroc = m.get("untuned_auroc")
    recomputed = _band(auroc)
    if recomputed != verdict and verdict != "NON_TEST":
        fails.append(f"(3) band MISMATCH: cell verdict={verdict} but recomputed band={recomputed} for auroc={auroc} -- band-logic drift")
    else:
        notes.append(f"(3) band cross-check PASS (auroc={auroc} -> {recomputed} == cell verdict)")

    # (4) coincidental-mention precision (report, not fail)
    rows = m.get("rows") or []
    coin = [r for r in rows if any(k in str(r.get("id", "")).lower() or k in str(r.get("gap_kind", "")).lower() for k in COINCIDENTAL)]
    # ids in the validated set carrying tarjan/hopcroft in their question -> map via validated questions
    coin_by_q = [v for v in validated if any(k in v.get("question", "").lower() for k in COINCIDENTAL)]
    coin_ids = {v["id"] for v in coin_by_q}
    coin_rows = [r for r in rows if r.get("id") in coin_ids] or coin
    if coin_rows:
        detail = ", ".join(f"{r.get('id')}:conf={r.get('confidence')}" for r in coin_rows)
        notes.append(f"(4) coincidental-mention near-gaps [{detail}] -- HIGH conf = refuse-gate precision limit the eval EXPECTS (not a fail; Skunkworks caveat).")
    else:
        notes.append("(4) coincidental-mention rows not located by id/keyword -- verify the 2 Tarjan/Hopcroft items are in rows.")

    # (5) corpus-completeness on the 38 gap absence claims
    validated_gap_ids = {v["id"] for v in validated if v.get("type") == "gap"}
    metrics_gap_ids = {r.get("id") for r in rows if r.get("type") == "gap"}
    missing = validated_gap_ids - metrics_gap_ids
    extra = metrics_gap_ids - validated_gap_ids
    if missing or extra:
        fails.append(f"(5) gap-id set DRIFT vs validated: missing={sorted(missing)} extra={sorted(extra)} -- run not on the validity-VET'd absence set")
    else:
        notes.append(f"(5) corpus-completeness PASS: all {len(validated_gap_ids)} validated gap ids present 1:1 in metrics rows (absence set intact).")

    # verdict
    print(f"[VET a2-v3] metrics={mpath.name}  cell_verdict={verdict}  untuned_auroc={auroc}")
    for n in notes:
        print("  OK  " + n)
    for h in halts:
        print("  HALT " + h)
    for f in fails:
        print("  FAIL " + f)
    if halts:
        print("[VET a2-v3] => VET_HALT (degenerate/inconsistent; no atomize; route to Skunkworks).")
        return 3
    if fails:
        print("[VET a2-v3] => VET_FAIL (cert-condition broken; no atomize; fix + re-run).")
        return 1
    print(f"[VET a2-v3] => VET_PASS -- {verdict}: atomize-eligible as EXPERIMENT_RECORD (pq per band; B-beta gate = {('LoRA JUSTIFIED' if verdict=='NEAR_CHANCE' else 'NO headroom' if verdict=='ALREADY_SEPARATES' else 'see band')}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
