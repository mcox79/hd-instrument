"""Witness for the PROMOTED hdlab organ hdlab/grounded_semantic_graph.py (Q111, 2026-09-01).

Three checks:
  [1] BUILDS: hdlab GroundedSemanticGraph().build() -> report node/edge counts + build time.
  [2] CONTEXT DIFFERENTIATION (can-fail): 'bank' in a river context vs a money context must differ.
  [3] FAITHFUL PROMOTION (byte-exact behavior): build the ORIGINAL experiment organ
      experiments.grounded_semantic_graph_organ.GroundedSemanticGraph and assert the hdlab organ's
      select_sense returns the IDENTICAL synset name on >= 4 probe (lemma, pos, context) cases.

Run:  .venv/Scripts/python.exe verification/test_grounded_semantic_graph_organ.py
Glass-box, LM-free, deterministic. NO external LLM.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# probe cases: (lemma, pos, context_words) -- clearly-ambiguous words with disambiguating contexts
PROBES = [
    ("bank", "N", ["river", "water", "flow", "shore"]),
    ("bank", "N", ["money", "loan", "account", "deposit"]),
    ("plant", "N", ["factory", "machine", "industry", "production"]),
    ("plant", "N", ["garden", "flower", "leaf", "soil", "grow"]),
    ("crane", "N", ["bird", "fly", "wing", "marsh", "water"]),
    ("bass", "N", ["music", "guitar", "sound", "song", "play"]),
]


def main() -> int:
    results = {}

    # ---------------------------------------------------------------------------------------------
    print("=" * 90)
    print("[1] BUILD hdlab organ: hdlab/grounded_semantic_graph.py")
    print("=" * 90, flush=True)
    from hdlab.grounded_semantic_graph import GroundedSemanticGraph as HdlabGSG
    t0 = time.time()
    g = HdlabGSG().build()
    build_s = time.time() - t0
    n_nodes = len(g.syn2idx)
    n_edges = g.n_edges
    print("BUILT hdlab organ: %d synset nodes, %d edges, %.1fs" % (n_nodes, n_edges, build_s), flush=True)
    check1 = (n_nodes > 100000 and n_edges > 100000 and g.T is not None)
    results["[1] builds"] = check1
    print("[1] PASS: builds with plausible node/edge counts" if check1 else "[1] FAIL: build looked wrong")

    # ---------------------------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("[2] CONTEXT DIFFERENTIATION (can-fail): river-'bank' vs money-'bank' must differ")
    print("=" * 90, flush=True)
    river = g.select_sense("bank", "N", ["river", "water", "flow", "shore"])
    money = g.select_sense("bank", "N", ["money", "loan", "account", "deposit"])
    print("  select_sense('bank' | river-context) -> %s" % river)
    print("  select_sense('bank' | money-context) -> %s" % money, flush=True)
    check2 = (river is not None and money is not None and river != money)
    results["[2] context differentiation"] = check2
    print("[2] PASS: senses differ by context" if check2 else "[2] FAIL: senses did NOT differ")

    # ---------------------------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("[3] FAITHFUL PROMOTION: hdlab select_sense == experiment-organ select_sense on %d probes" % len(PROBES))
    print("=" * 90, flush=True)
    from experiments.grounded_semantic_graph_organ import GroundedSemanticGraph as ExpGSG
    t0 = time.time()
    ge = ExpGSG().build()
    print("BUILT experiment organ: %d nodes, %d edges, %.1fs" % (len(ge.syn2idx), ge.n_edges, time.time() - t0), flush=True)
    all_match = True
    n_diff_contexts = 0
    for lemma, pos, ctx in PROBES:
        hd = g.select_sense(lemma, pos, ctx)
        ex = ge.select_sense(lemma, pos, ctx)
        match = (hd == ex)
        all_match = all_match and match
        print("  %-6s %-2s ctx=%-45s hdlab=%-16s exp=%-16s %s"
              % (lemma, pos, str(ctx)[:45], hd, ex, "OK" if match else "MISMATCH"), flush=True)
    # sanity: the two 'bank' probes and the two 'plant' probes should each disambiguate differently
    bank_r = g.select_sense(*("bank", "N", PROBES[0][2]))
    bank_m = g.select_sense(*("bank", "N", PROBES[1][2]))
    plant_f = g.select_sense(*("plant", "N", PROBES[2][2]))
    plant_g = g.select_sense(*("plant", "N", PROBES[3][2]))
    n_diff_contexts = int(bank_r != bank_m) + int(plant_f != plant_g)
    print("  (context-sensitivity sanity: bank river!=money=%s, plant factory!=garden=%s)"
          % (bank_r != bank_m, plant_f != plant_g))
    check3 = all_match
    results["[3] byte-faithful (identical to experiment organ)"] = check3
    print("[3] PASS: hdlab organ matches the experiment organ on all probes"
          if check3 else "[3] FAIL: hdlab organ diverged from the experiment organ")

    # ---------------------------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    for k, v in results.items():
        print("  %-55s %s" % (k, "PASS" if v else "FAIL"))
    ok = all(results.values())
    print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
    return 0 if ok else 1


def test_grounded_semantic_graph_organ():
    """pytest entry point."""
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
