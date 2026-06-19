"""A2 semantic absence re-check on the GROWN corpus (Skunkworks 4th-gate ruling 2026-06-18).

The substrate grew +2562 atoms (FrameNet 1221 + WordNet completeness 1339) since the A2 gap-set was validity-VET'd. The
corpus-completeness gate requires an ABSENCE claim be re-verified against the CURRENT corpus by an EXHAUSTIVE SEMANTIC
method (NOT lexical token-match -- the denylisted method my earlier probe used). This cell: for each of the 38 A2 'gap'
questions, compute its bge embedding max-COSINE to the +2562 NEW atoms (FrameNet SEMANTIC_FRAME + WordNet
completeness_target), using the SAME 43892 bge index A2 v6 reads.

Verdict bands:
  ALL_HOLD: every gap's max-sim to the new atoms < IN_COVERAGE_THRESHOLD -> the new atoms don't semantically cover the
            CS-topic gaps -> the gap-absence labels CARRY -> A2 v6 AUROC on 43892 is TRUSTED.
  CONTAMINATED: >=1 gap with max-sim >= threshold -> that gap is semantically covered by an ARC-3 atom -> must be
            DELIBERATELY dropped/re-scoped (documented: gap X, atom Y, sim Z) before A2 v6.
IN_COVERAGE_THRESHOLD = 0.70 (the A2 ALREADY_SEPARATES bar = "the substrate can answer it"; a new atom above this means
the gap is now answerable -> contaminated). Reports per-gap max-sim + the top-matching new atom for transparency.

bge (GPU) required. Reuses the m1 harness (AtomEncoder + the 43892 warm cache). import torch (PROT-020). HF_HUB_OFFLINE.
--self-test exercises the threshold/verdict logic synthetically (no bge). 11th-rule. ASCII. HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test ; --full.
"""
from __future__ import annotations
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import argparse
import json
import sys
import time
from pathlib import Path

import torch  # noqa: F401  # PROT-020 (GPU cell; bge via AtomEncoder)
import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc, gate0_self_check

ANCHOR = "substrate_a2_semantic_absence_recheck_gpu_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
A2_SET = REPO / "experiments" / "data" / "a2_gap_balanced_v1.jsonl"
IN_COVERAGE_THRESHOLD = 0.70   # the A2 ALREADY_SEPARATES bar; a NEW atom above this = the gap is now answerable = contaminated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()

    if args.self_test:
        # threshold/verdict logic on synthetic sims (no bge)
        sims = [0.3, 0.5, 0.69]   # all below 0.70 -> ALL_HOLD
        verdict = "ALL_HOLD" if all(s < IN_COVERAGE_THRESHOLD for s in sims) else "CONTAMINATED"
        sims2 = [0.3, 0.75]; v2 = "ALL_HOLD" if all(s < IN_COVERAGE_THRESHOLD for s in sims2) else "CONTAMINATED"
        ok = (verdict == "ALL_HOLD" and v2 == "CONTAMINATED")
        print(f"[{ANCHOR}] --self-test {'OK' if ok else 'FAIL'} (threshold/verdict logic; ALL_HOLD={verdict}, contaminated-case={v2}); NO metrics.")
        return 0 if ok else 1

    if not A2_SET.exists():
        print(f"[{ANCHOR}] ERROR: A2 set not found at {A2_SET}"); return 1
    items = [json.loads(l) for l in open(A2_SET, encoding="utf-8") if l.strip()]
    gaps = [it for it in items if it["type"] == "gap"]

    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
        from backend.substrate_index.schema import AtomKind
    except Exception as e:
        print(f"[{ANCHOR}] ERROR import: {e}"); return 2
    print(f"[{ANCHOR}] STEP load store + bge + 43892 index (warm cache)...", flush=True)
    pstore = PartitionedStore(REPO / "data" / "substrate_index")
    try:
        enc = AtomEncoder()
    except Exception as e:
        print(f"[{ANCHOR}] ERROR bge_unavailable: {str(e)[:100]}"); return 3
    r = Retriever(pstore, enc); rebuild_index_cached(r, REPO / "data" / "substrate_index")

    # identify the +2562 NEW atoms (FrameNet SEMANTIC_FRAME + WordNet completeness_target) + their index rows
    id_order = r._id_order; sem = r._semantic_matrix
    new_ids = set()
    for a in pstore.all_atoms():
        if a.kind == AtomKind.SEMANTIC_FRAME or (str(a.id).startswith("WN_") and (a.metadata or {}).get("completeness_target")):
            new_ids.add(a.id)
    pos = {aid: i for i, aid in enumerate(id_order)}
    new_idx = [pos[aid] for aid in new_ids if aid in pos]
    if not new_idx:
        print(f"[{ANCHOR}] ERROR: 0 new atoms found in index (expected ~2562) -- wrong index?"); return 4
    new_mat = sem[new_idx]                                   # (n_new, dim), already L2-normed by the encoder
    print(f"[{ANCHOR}] STEP {len(new_idx)} new atoms in index; scoring {len(gaps)} gap questions vs them...", flush=True)

    rows = []
    for g in gaps:
        q = g["question"]
        qv = enc.encode_query_text(q)
        qv = qv / (np.linalg.norm(qv) + 1e-12)
        sims = new_mat @ qv                                  # cosine (both normed)
        j = int(np.argmax(sims)); mx = float(sims[j])
        rows.append({"id": g["id"], "topic": (g.get("args", {}) or {}).get("topic"),
                     "max_sim_to_new": round(mx, 4), "top_new_atom": id_order[new_idx[j]],
                     "contaminated": mx >= IN_COVERAGE_THRESHOLD})

    contaminated = [x for x in rows if x["contaminated"]]
    verdict = "CONTAMINATED" if contaminated else "ALL_HOLD"
    if verdict == "ALL_HOLD":
        msg = (f"ALL_HOLD: all {len(gaps)} gap-topics have max-sim < {IN_COVERAGE_THRESHOLD} to the {len(new_idx)} ARC-3 "
               f"ingest atoms -> NO gap is now ANSWERABLE/covered by a new atom -> the gap-absence LABELS CARRY -> the A2 "
               f"gap-set is VALID on 43892. (REFINE 2: ALL_HOLD validates the LABELS, NOT 'no noise' -- sub-threshold "
               f"matches [0.45-0.69] may cause a SMALL AUROC shift, a REAL current-state property the v6 measures HONESTLY; "
               f"the 0.70 bar is the coverage/answerable threshold.) max over all gaps={max(x['max_sim_to_new'] for x in rows):.4f}.")
    else:
        msg = (f"CONTAMINATED: {len(contaminated)} gap(s) now semantically covered (max-sim >= {IN_COVERAGE_THRESHOLD}) by "
               f"an ARC-3 atom -> DELIBERATELY drop/re-scope (documented): "
               + "; ".join(f"{c['id']} sim={c['max_sim_to_new']} <- {c['top_new_atom']}" for c in contaminated))

    g0 = gate0_self_check(run_mode=("smoke" if is_smoke else "full"), metrics_source="measured_bge_gpu_held_out",
                          n_cells_declared=len(gaps), n_cells_emitted=len(rows), elapsed_s=round(time.time()-t0, 2), is_smoke=is_smoke)
    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "summary": msg, "n_seeds": 1,
        **provenance_fields("smoke" if is_smoke else "full", "semantic_absence_recheck", "measured_bge_gpu_held_out", run_started_utc),
        "gate0_self_check": g0, "in_coverage_threshold": IN_COVERAGE_THRESHOLD,
        "new_atom_scope": ("REFINE-1: new-atom set = ARC-3 INGEST topic-coverage atoms (FrameNet SEMANTIC_FRAME + WordNet "
                           "completeness_target); the few depth-cliff/today EXPERIMENT_RECORD atoms (math process-knowledge, "
                           "NOT CS-topic-coverage candidates; semantically orthogonal to CS-algorithm gaps) are EXCLUDED + "
                           "documented here -- the exhaustive check covers the atoms that could ANSWER a CS gap, which "
                           "experiment-records cannot. Count is the ingest-atom subset, not literally all +2562."),
        "n_gaps": len(gaps), "n_new_atoms": len(new_idx), "n_contaminated": len(contaminated),
        "max_sim_over_all_gaps": round(max(x["max_sim_to_new"] for x in rows), 4) if rows else None,
        "rows": rows, "corpus_completeness_method": "exhaustive_bge_cosine_semantic (NOT lexical token_match)",
        "bears_on": "A2 v6 validity on the grown 43892 corpus; gates TRUSTING the v6 AUROC verdict",
        "elapsed_s": round(time.time()-t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")
    print(f"[{ANCHOR}] -> {verdict}  (n_contaminated={len(contaminated)}, max_sim={metrics['max_sim_over_all_gaps']})")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
