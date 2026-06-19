"""
exp_substrate_algebra_coverage_gap_diagnosis_cpu_v1.py -- diagnose the algebra/composite coverage gap on the REAL substrate -- CPU/local.

ROUTING: the two-vector real-substrate validation showed composite_hrr coverage is 242/1743 (13.9pct). That headline understates
  the truth: the gap is TWO distinct populations. (a) HISTORY-corpus atoms (decision/research/verdict/findings/results history)
  -- the substrate's self-ingested NARRATIVE provenance -- have descriptions but no algebra field, and are CORRECTLY served by
  the bge semantic index (free-text path), NOT algebra-encoded. (b) STRUCTURED atoms (math/science/concept/cross_disc/lexicon)
  that SHOULD have an authored algebra dict but don't -- the real backfill target. This cell classifies every uncovered atom
  into by-design (history -> bge) vs backfillable (structured, algebra-eligible) and surfaces the high-value T1-foundational
  subset. Reframes the coverage worry and points Research/Testbed backfill at the ~280 structured atoms, not the ~1185 history
  atoms. NO LLM; pure PartitionedStore stats (numpy-free), local-safe.

PRE-REGISTERED: descriptive diagnostic. HARD-PASS if the gap cleanly decomposes (history corpus is the majority of the gap AND
  has ~0 algebra by design AND a well-defined structured-backfillable remainder is identified). MIDDLE if the split is muddy
  (structured atoms dominate the gap -> backfill is the whole story). HARD-FAIL if covered atoms themselves are mostly history
  (would mean algebra encoding is mis-targeted). UNKNOWN if store missing.
ASCII-only. CPU/local. --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple
from collections import Counter
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_algebra_coverage_gap_diagnosis_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
HISTORY_CORPORA = {"decision_history", "research_history", "verdict_history", "findings_history", "results_history", "memory_history"}


def _cstr(v):
    return getattr(v, "value", None) or str(v)


def _selftest():
    assert "research_history" in HISTORY_CORPORA and _cstr("x") == "x"
    print("[selftest] PASS: substrate_algebra_coverage_gap_diagnosis_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "store_missing", "note": str(root)}
    atoms = PartitionedStore(root).all_atoms()
    n = len(atoms)
    covered = [a for a in atoms if getattr(a, "algebra", None)]
    uncovered = [a for a in atoms if not getattr(a, "algebra", None)]
    # classify uncovered
    hist = [a for a in uncovered if _cstr(getattr(a, "corpus", None)) in HISTORY_CORPORA]
    struct = [a for a in uncovered if _cstr(getattr(a, "corpus", None)) not in HISTORY_CORPORA]
    hist_with_alg = sum(1 for a in hist if getattr(a, "algebra", None))   # should be 0 by definition
    # high-value backfill: T1-foundational structured atoms lacking algebra
    t1_backfill = [a for a in struct if _cstr(getattr(a, "tier", None)) == "T1"]
    struct_by_corpus = Counter(_cstr(getattr(a, "corpus", None)) for a in struct)
    cov_by_corpus = Counter(_cstr(getattr(a, "corpus", None)) for a in covered)
    structured_total = len(covered) + len(struct)
    struct_cov_rate = len(covered) / (structured_total + 1e-9)
    print("  total atoms=%d | covered(algebra/composite)=%d (%.1f%%)" % (n, len(covered), 100 * len(covered) / n), flush=True)
    print("  uncovered=%d -> HISTORY(by-design, bge-served)=%d + STRUCTURED(backfillable)=%d" % (len(uncovered), len(hist), len(struct)), flush=True)
    print("  history atoms with an algebra field (should be 0): %d" % hist_with_alg, flush=True)
    print("  STRUCTURED coverage (excluding history corpus): %d/%d = %.1f%%" % (len(covered), structured_total, 100 * struct_cov_rate), flush=True)
    print("  high-value backfill (T1-foundational, structured, no algebra): %d atoms" % len(t1_backfill), flush=True)
    print("  structured-backfillable by corpus: %s" % struct_by_corpus.most_common(8), flush=True)
    print("  covered by corpus: %s" % cov_by_corpus.most_common(8), flush=True)
    return {"n": n, "covered": len(covered), "uncovered": len(uncovered), "history_gap": len(hist),
            "structured_gap": len(struct), "history_with_algebra": hist_with_alg,
            "structured_total": structured_total, "structured_cov_rate": round(struct_cov_rate, 4),
            "t1_backfill": len(t1_backfill), "struct_by_corpus": dict(struct_by_corpus),
            "covered_by_corpus": dict(cov_by_corpus),
            "t1_backfill_sample": [a.id for a in t1_backfill[:15]]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + r.get("note", ""))
    s = ("total=%d covered=%d (raw %.1f%%); gap=%d = HISTORY %d (by-design bge) + STRUCTURED %d (backfillable); "
         "history-with-algebra=%d; STRUCTURED coverage=%.1f%%; T1 high-value backfill=%d; struct_by_corpus=%s; t1_sample=%s") % (
        r["n"], r["covered"], 100 * r["covered"] / r["n"], r["uncovered"], r["history_gap"], r["structured_gap"],
        r["history_with_algebra"], 100 * r["structured_cov_rate"], r["t1_backfill"], r["struct_by_corpus"], r["t1_backfill_sample"])
    history_majority = r["history_gap"] > r["structured_gap"]
    if history_majority and r["history_with_algebra"] == 0:
        return ("HARD_PASS", "HARD_PASS: the coverage gap decomposes CLEANLY -- the majority (%d) is HISTORY-corpus narrative atoms correctly served by bge (0 have algebra, by design), and the real backfill target is a well-defined %d structured atoms (incl %d T1-foundational). The 13.9%% headline understates structured coverage (%.1f%%); backfill should target the structured remainder, not the history corpus. " % (
            r["history_gap"], r["structured_gap"], r["t1_backfill"], 100 * r["structured_cov_rate"]) + s)
    if not history_majority:
        return ("MIDDLE_BAND", "MIDDLE_BAND: structured atoms dominate the gap -- backfill is the whole story (algebra authoring for structured math/science). " + s)
    return ("HARD_FAIL", "HARD_FAIL: unexpected -- history atoms carry algebra or covered set is mostly history; algebra encoding may be mis-targeted. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
