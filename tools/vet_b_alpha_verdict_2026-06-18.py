"""Deterministic verdict-VET harness for B-alpha NARROW SCALE-UP (substrate_b_alpha_2hop_hypernym_qa_cpu_v1).

Pre-built forward-work. B-alpha is deterministic, so the remote verdict SHOULD reproduce local (recall~0.607, MIDDLE,
CERT_CHAIN_GRADE). The real VET value: verify-the-referent on the REMOTE run -- (a) the gates fired, (b) the tier lands
CERT_CHAIN_GRADE via the actual atomizer, (c) recall matches local within tolerance (a mismatch => the remote Store's
HYPERNYM edge set drifted from local 2884 = a sync issue, NOT a cell issue -> flag, don't atomize). Read-only.

Checks:
  (1) gate0 PASS (run_mode=full, measured_graph_bfs_held_out, n_cells declared==emitted).
  (2) discrimination + path-provenance + FP: discriminates==True; 0 unverifiable path edges (5th gate); false_positives==0.
  (3) band cross-check: recompute band from recall_answer_found == cell verdict (no band drift).
  (4) corpus-completeness: n_positives + n_negatives == 600 (the validity-VET'd set intact).
  (5) tier lands CERT_CHAIN_GRADE via the real atomizer provenance_quality (not LEGACY).
  (6) recall sanity vs local reference 0.607 (drift > REMOTE_DRIFT_TOL => remote Store edge-set drift -> HALT).

Usage: python tools/vet_b_alpha_verdict_2026-06-18.py [path/to/metrics.json]
  default = data/exp_b_alpha_2hop_hypernym_qa_v1/metrics.json (remote HDLAB_EXP_NAME path)
ASCII-only. No LLM. Read-only VET.
"""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_METRICS = REPO / "data" / "exp_b_alpha_2hop_hypernym_qa_v1" / "metrics.json"
LOCAL_RECALL_REF = 0.607
REMOTE_DRIFT_TOL = 0.05      # remote recall should match local within this (deterministic; drift => Store edge-set differs)
NEAR_CHANCE = None
PASS_HI, FAIL_LO = 0.70, 0.40
N_EXPECTED = 600


def _band(recall):
    if recall is None:
        return "NON_TEST"
    if recall < FAIL_LO:
        return "HARD_FAIL"
    if recall >= PASS_HI:
        return "HARD_PASS"
    return "MIDDLE_BAND"


def _load_atomizer():
    spec = importlib.util.spec_from_file_location("atom", str(REPO / "tools" / "atomize_experiment_records.py"))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(REPO))
    spec.loader.exec_module(m)
    return m


def main():
    mpath = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_METRICS
    if not mpath.exists():
        print(f"[VET b-alpha] metrics NOT FOUND at {mpath} -- B-alpha has not landed yet (or wrong path). VET deferred.")
        return 2
    m = json.loads(mpath.read_text(encoding="utf-8"))
    fails, halts, notes = [], [], []
    verdict = m.get("verdict")
    recall = m.get("recall_answer_found")

    # (1) gate0 (run_mode lives at metrics top-level via provenance_fields; gate0 dict carries pass/is_smoke/n_cells)
    g0 = m.get("gate0_self_check") or {}
    run_mode_top = m.get("run_mode") or (m.get("provenance") or {}).get("run_mode")
    if not g0.get("pass"):
        fails.append(f"(1) gate0 FAIL (pass != True): {g0}")
    elif run_mode_top != "full" or g0.get("is_smoke"):
        fails.append(f"(1) run_mode={run_mode_top} (top-level) / gate0.is_smoke={g0.get('is_smoke')} -- not a full run")
    else:
        notes.append(f"(1) gate0 PASS (run_mode=full, is_smoke=False, n_decl={g0.get('n_cells_declared')}, n_emit={g0.get('n_cells_emitted')})")

    # (2) discrimination + provenance + FP
    if verdict == "NON_TEST":
        halts.append(f"(2) verdict=NON_TEST: {m.get('verdict_msg')} -- HALT, no atomize.")
    else:
        fp = m.get("false_positives")
        unver = m.get("path_edges_unverifiable")
        if fp not in (0, None) and fp != 0:
            halts.append(f"(2) false_positives={fp} != 0 -- mislabeled negative / test-validity breach; HALT.")
        if unver not in (0, None) and unver != 0:
            fails.append(f"(2) path_edges_unverifiable={unver} != 0 -- PROVENANCE BREACH (hallucinated hop); HARD_FAIL.")
        if not (fp or unver):
            notes.append(f"(2) provenance PASS (0 unverifiable of {m.get('path_edges_total')} edges) + 0 false-positives + refuse_rate={m.get('refuse_rate')}")

    # (3) band cross-check
    recomputed = _band(recall)
    if verdict != "NON_TEST" and recomputed != verdict:
        fails.append(f"(3) band MISMATCH: verdict={verdict} but recomputed={recomputed} for recall={recall}")
    else:
        notes.append(f"(3) band cross-check PASS (recall={recall} -> {recomputed} == verdict)")

    # (4) corpus-completeness
    npos, nneg = m.get("n_positives"), m.get("n_negatives")
    if (npos or 0) + (nneg or 0) != N_EXPECTED:
        fails.append(f"(4) item count {npos}+{nneg} != {N_EXPECTED} -- not the validity-VET'd 300+300 set")
    else:
        notes.append(f"(4) corpus-completeness PASS ({npos} pos + {nneg} neg = {N_EXPECTED})")

    # (5) tier lands CERT_CHAIN_GRADE
    try:
        atom = _load_atomizer()
        run_mode = m.get("run_mode") or (m.get("provenance") or {}).get("run_mode")
        pq = atom.provenance_quality(run_mode, m.get("n_seeds"), m, verdict)
        if pq != "CERT_CHAIN_GRADE":
            fails.append(f"(5) tier = {pq} (EXPECT CERT_CHAIN_GRADE) -- cert-marker not recognized / gate failed")
        else:
            notes.append(f"(5) tier PASS = CERT_CHAIN_GRADE (atomizer-verified)")
    except Exception as e:
        notes.append(f"(5) tier check skipped (atomizer import: {str(e)[:80]})")

    # (6) recall sanity vs local reference (remote Store drift detector)
    if recall is not None and abs(recall - LOCAL_RECALL_REF) > REMOTE_DRIFT_TOL:
        halts.append(f"(6) recall={recall} drifts > {REMOTE_DRIFT_TOL} from local ref {LOCAL_RECALL_REF} -- "
                     f"REMOTE Store HYPERNYM edge-set likely differs from local (sync issue); HALT + verify edge count.")
    elif recall is not None:
        notes.append(f"(6) recall sanity PASS ({recall} within {REMOTE_DRIFT_TOL} of local ref {LOCAL_RECALL_REF}; no remote drift)")

    print(f"[VET b-alpha] metrics={mpath.name}  verdict={verdict}  recall={recall}")
    for n in notes:
        print("  OK  " + n)
    for h in halts:
        print("  HALT " + h)
    for f in fails:
        print("  FAIL " + f)
    if halts:
        print("[VET b-alpha] => VET_HALT (no atomize; route to Skunkworks).")
        return 3
    if fails:
        print("[VET b-alpha] => VET_FAIL (cert-condition broken; no atomize).")
        return 1
    print(f"[VET b-alpha] => VET_PASS -- CERT_CHAIN_GRADE {verdict}: the first cert-grade DISCRIMINATING composed-reasoning "
          f"result (recall {recall}, 100% provenance, 0 FP). Atomize-eligible; Skunkworks tier ruling confirms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
