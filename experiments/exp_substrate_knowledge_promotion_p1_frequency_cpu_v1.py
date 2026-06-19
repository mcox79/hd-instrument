"""
exp_substrate_knowledge_promotion_p1_frequency_cpu_v1.py -- CELL KP path P1: frequency-promotion candidate identification -- CPU/local (no heat, read-only).

ROUTING: Research priority steer -- KNOWLEDGE PROMOTION OPERATOR (5 substrate-only paths), the highest-leverage next architectural
  lever toward "substrate-on-all-knowledge" + recursive self-improvement. This cell implements PATH P1 (frequency-promotion):
  a T3 atom recurring (in-degree >= z) across >= K distinct corpus partitions has empirically proven FOUNDATIONAL and is a
  candidate to PROMOTE T3 -> T2. READ-ONLY: identifies candidates (does NOT write the canonical substrate -- promotion + the
  +0.01-macro benchmark-improvement check are Testbed-integration steps). NO LLM; pure relations + corpus-field stats (no heat).

  Verify-before-build feasibility map for the OTHER 4 paths at the current corpus (reported to Research):
   - P2 DRUM/NeuralLP differentiable rule mining (T1-axiom-candidates): substantial ML build (~2 days); deferred.
   - P3 SHARES_MATH bisimulation (T2 archetypes): GATED -- SHARES_MATH edges = 0 in the corpus (nothing to quotient).
   - P4 sleep-replay consolidation (T2 cortical archetypes): approximable via clustering of T3 algebra/composite vectors; moderate.
   - P5 Curry-Howard type promotion (T0 candidates, depth>=10): GATED -- proof graph is depth ~1.3 (need depth>=10 chains).
  So at the current corpus, P1 is the cleanly-feasible path; the "3-of-5 HARD-PASS" needs preconditions (SHARES_MATH edges,
  deeper DEPENDS_ON authoring) + the P2 build.

PRE-REGISTERED (P1 sub-path): HARD-PASS >= 5 sensible T3->T2 candidates (in-deg >= z_threshold AND ref'd by >= corpora_threshold
  distinct corpora), each a recognizable cross-domain foundational algorithm. MIDDLE 1-4. HARD-FAIL 0 (frequency signal absent).
  (The downstream benchmark-improvement +0.01 macro is a Testbed step after actual promotion.)
ASCII-only. CPU/local. --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_knowledge_promotion_p1_frequency_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
Z_THRESHOLD = 3; CORPORA_THRESHOLD = 3


def _norm(x):
    return str(x).split("::")[-1].strip()


def _selftest():
    # p1 rule: promote iff in_deg>=Z AND distinct ref-corpora>=K
    def qual(indeg, ncorp): return indeg >= Z_THRESHOLD and ncorp >= CORPORA_THRESHOLD
    assert qual(52, 7) and qual(3, 3) and not qual(2, 5) and not qual(10, 2)
    print("[selftest] PASS: substrate_knowledge_promotion_p1_frequency_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    atoms = PartitionedStore(root).all_atoms()

    def corpv(a): return str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()

    def tval(a):
        t = getattr(a, "tier", None); return str(getattr(t, "value", t) or "")
    corp = {_norm(a.id): corpv(a) for a in atoms}; tier = {_norm(a.id): tval(a) for a in atoms}
    indeg = Counter(); ref_corpora = defaultdict(set)
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
            if s and t and s != t:
                indeg[t] += 1
                if s in corp: ref_corpora[t].add(corp[s])
    t3 = [n for n in tier if tier[n] == "T3"]
    cands = []
    for n in t3:
        if indeg[n] >= Z_THRESHOLD and len(ref_corpora[n]) >= CORPORA_THRESHOLD:
            cands.append({"atom": n, "in_degree": indeg[n], "n_ref_corpora": len(ref_corpora[n]),
                          "ref_corpora": sorted(ref_corpora[n])})
    cands.sort(key=lambda c: -c["in_degree"])
    print("  T3 atoms=%d | in-deg>=%d: %d | P1 candidates (AND >=%d ref-corpora): %d" % (
        len(t3), Z_THRESHOLD, sum(1 for n in t3 if indeg[n] >= Z_THRESHOLD), CORPORA_THRESHOLD, len(cands)), flush=True)
    for c in cands[:12]:
        print("    PROMOTE T3->T2: %-34s in-deg=%d ref-corpora=%d %s" % (c["atom"], c["in_degree"], c["n_ref_corpora"], c["ref_corpora"]), flush=True)
    # save the candidate list for Testbed promotion + benchmark validation
    bf = REPO / "data" / "substrate_index" / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "kp_p1_frequency_promotion_candidates.json").write_text(json.dumps({"candidates": cands, "z_threshold": Z_THRESHOLD,
        "corpora_threshold": CORPORA_THRESHOLD}, indent=2), encoding="utf-8")
    return {"n_t3": len(t3), "n_candidates": len(cands), "candidates": cands[:20], "z_threshold": Z_THRESHOLD,
            "corpora_threshold": CORPORA_THRESHOLD}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["n_candidates"]
    s = "P1 candidates=%d (T3 in-deg>=%d AND >=%d ref-corpora) of %d T3 atoms; top=%s; saved to bench_reports/kp_p1_frequency_promotion_candidates.json (READ-ONLY -- Testbed promotes + benchmark-validates)" % (
        n, r["z_threshold"], r["corpora_threshold"], r["n_t3"], [c["atom"] for c in r["candidates"][:6]])
    if n >= 5:
        return ("HARD_PASS", "HARD_PASS: P1 frequency-promotion identifies %d T3->T2 candidates -- cross-domain foundational algorithms (recurring across >=%d corpora). The promotion operator's P1 path works: empirically-foundational T3 atoms are surfaced for promotion. " % (n, r["corpora_threshold"]) + s)
    if n >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: only %d P1 candidates -- weak frequency signal at current corpus. " % n + s)
    return ("HARD_FAIL", "HARD_FAIL: 0 P1 candidates -- no T3 atom recurs across >=%d corpora; frequency-promotion inactive at current corpus. " % r["corpora_threshold"] + s)


print("[config] anchor=%s mode=%s z=%d corpora=%d" % (ANCHOR_NAME, RUN_MODE, Z_THRESHOLD, CORPORA_THRESHOLD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
