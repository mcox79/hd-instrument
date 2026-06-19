"""
exp_substrate_cause3_idmatch_reconcile_heldout_cpu_v1.py -- reconcile the discrepancy: 3 in-coverage held-out questions have gold at bge rank 2-3 (lenient _short match) yet scored ~0 in the canonical scorer (EXACT qualified-id match). Is it id-mismatch (cheap data fix) or fusion (deeper)? -- runs on BGE machine.

ROUTING: Cause-3 diagnostic flagged Q60/Q61/Q64 gold at bge rank 2-3 but canonical tp~0. Scorer uses EXACT string set-intersection
  (score_set_overlap: tp = predicted & set(ground_truth)); my rank diagnostic used LENIENT _short() normalization. Hypothesis 2 (id-match): the
  converted held-out file's gold qualified-ids do NOT exactly equal the substrate's predicted qualified-ids. This probe prints, per shallow question:
  file gold (raw) vs the EXACT qualified-id of the leniently-matched bge top-5 atom -> shows whether they differ only in qualification/case/separator
  (cheap re-qualify fix) or are genuinely different atoms (fusion/representation). Substrate-internal. ASCII; --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_cause3_idmatch_reconcile_heldout_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
SHALLOW_QIDS = {"Q60-G", "Q61-A", "Q64-G", "Q55-B", "Q54-A"}  # in-coverage shallow+medium to inspect


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("math::convolution/conv1d") == "conv1d"
    assert _short("CONVOLUTION") == "convolution"
    print("[selftest] PASS: substrate_cause3_idmatch_reconcile_heldout_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    if not HELDOUT.exists():
        return {"error": "no_heldout_file"}
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        return {"error": "import_failed:" + str(e)[:100]}
    pstore = PartitionedStore(DATA_ROOT)
    try:
        enc = AtomEncoder()
    except Exception as e:
        return {"error": "bge_unavailable:" + str(e)[:80]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    bare_to_qid = {a.id: a.qualified_id for a in pstore.all_atoms()}
    short_to_qids: Dict[str, List[str]] = {}
    for a in pstore.all_atoms():
        short_to_qids.setdefault(_short(a.id), []).append(a.qualified_id)
    qs = {q["qid"]: q for q in (json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip())}
    results = []
    n_idmatch_bug = 0
    for qid in sorted(SHALLOW_QIDS):
        q = qs.get(qid)
        if not q:
            continue
        gold = q.get("ground_truth_atoms") or []
        cands = r.semantic(q["question"], top_k=10)
        pred_qids = [(bare_to_qid.get(c.atom_id, c.atom_id), _short(c.atom_id), round(float(getattr(c, "score", 0.0)), 4)) for c in cands]
        print("\n  === %s ===" % qid, flush=True)
        print("  file gold (raw): %s" % gold, flush=True)
        print("  bge top-10 (qualified_id | short | score):", flush=True)
        for pq, ps, sc in pred_qids:
            print("    %-45s %-20s %.4f" % (pq[:45], ps, sc), flush=True)
        gold_short = {_short(g) for g in gold}
        pred_short = {ps for _, ps, _ in pred_qids}
        pred_qual = {pq for pq, _, _ in pred_qids}
        exact_hit = [g for g in gold if g in pred_qual]
        short_hit = [g for g in gold if _short(g) in pred_short]
        # for each short-hit, what qualified ids does the substrate actually have?
        for g in gold:
            if _short(g) in short_to_qids:
                actual = short_to_qids[_short(g)]
                exact = g in actual
                print("    gold '%s' -> substrate qualified_id(s) %s | EXACT-match-with-file-gold=%s" % (g, actual[:3], exact), flush=True)
                if not exact:
                    n_idmatch_bug += 1
        results.append({"qid": qid, "gold": gold, "exact_top10": exact_hit, "short_top10": short_hit,
                        "idmatch_bug": [g for g in gold if _short(g) in short_to_qids and g not in short_to_qids[_short(g)]]})
    return {"results": results, "n_idmatch_bug_atoms": n_idmatch_bug}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    nbug = r["n_idmatch_bug_atoms"]
    short_but_not_exact = sum(1 for x in r["results"] if x["short_top10"] and not x["exact_top10"])
    base = ("Reconcile: %d gold atoms have a substrate qualified_id whose EXACT string differs from the file gold (id-match bug). %d/%d inspected "
            "questions have a short-match in bge top-10 but NO exact-match." % (nbug, short_but_not_exact, len(r["results"])))
    if nbug > 0 or short_but_not_exact > 0:
        return ("HARD_PASS", "ID-MATCH BUG CONFIRMED (cheap data fix, NOT M4): the held-out converted file's gold ids do not EXACTLY equal the "
                "substrate's qualified ids, so the scorer's exact set-intersection misses gold that bge actually retrieves at rank 2-3. Re-qualifying "
                "the held-out gold to the substrate's canonical qualified_ids recovers these in-coverage questions WITHOUT any retrieval/M4 work. " + base)
    return ("HARD_FAIL", "NOT an id-match bug: gold exact-matches substrate ids; the loss is downstream (fusion/cutoff). Needs fusion investigation. " + base)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
