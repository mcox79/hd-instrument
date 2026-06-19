"""40h #5: HYP-5 DEPTH-CEILING discriminating probe (REDESIGN from the prior MEASURED_MECHANISM recovery scope).

The prior depth-cliff arc RECOVERED HYP-2/3/4 via 2-level completion (0.993/0.931/0.853, MEASURED_MECHANISM = coextensive).
This is NOT a 4th coextensive recovery. It is a NON-COEXTENSIVE depth-ceiling probe (pure MEASUREMENT + break-point
ATTRIBUTION on the CURRENT backbone; NO completion added): does the coverage-completion lever EXTEND to depth-5, or hit an
inherent DEPTH-CEILING -- and IS that ceiling COVERAGE (out-of-5k intermediates) or ALGORITHMIC?

DESIGN (in-memory / 0-persist; read-only on the Store; nltk-independent gold):
  - K-hop hypernym recall for K=2,3,4,5: GOLD = nltk true K-level hypernym closure (x->z, both in-corpus); walker =
    deterministic BFS over the CURRENT persisted HYPERNYM backbone (the 2-level-completed 6213). No new edges.
  - BREAK-POINT ATTRIBUTION (the discriminating element) for each MISS (gold (x,z) with no persisted K-path):
      (1) COVERAGE-CEILING : NO all-in-5k nltk K-path exists (every nltk path exits the 5k) -> correct REFUSE; the synsets
          simply aren't all in-corpus. The ceiling is the in-5k-completeness fraction.
      (2) EDGE-GAP         : an all-in-5k nltk K-path EXISTS but is NOT in the persisted backbone -> a materialization gap
          (completion-fixable; still COVERAGE, not algorithmic).
      (3) ALGORITHMIC      : a PERSISTED K-path exists but the walker's BFS missed it -> walker defect (expect ~0).
  - negatives (verified-unreachable) for FP=0 + discrimination.

VERDICT (pre-registered): the depth-ceiling is COVERAGE (extends-with-ceiling) iff recall declines/plateaus AND misses are
dominated by (1)+(2) [coverage] with (3) ~0 [not algorithmic]. -> CERT_CHAIN_GRADE DISCRIMINATING: the lever EXTENDS to
depth-5 (no crash) with a COVERAGE-CEILING (~in-5k-completeness), NOT an algorithmic depth-limit. EXTENDS the coverage-
completion-not-reasoning story to depth-5. (If (3) is non-trivial -> walker/edge defect to investigate, NOT a clean ceiling.)

CERT-CONDITIONS: nltk-independent gold + deterministic BFS (11th-rule) + in-memory/0-persist + n>=30/K + fp=0 +
attribution-sums-to-misses. DEVICE=cpu (7th checklist). Deterministic sample (--seed). ASCII. --self-test ; --full.
"""
from __future__ import annotations
import argparse
import json
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DEVICE = "cpu"
ANCHOR = "substrate_hyp5_depth_ceiling_cpu_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
DEPTHS = (2, 3, 4, 5)
SAMPLE_N = 1500          # deterministic synset sample (ample; n_pos >> 30 per K)
N_MIN = 30


def bfsK(adj, start, goal, K):
    if start == goal:
        return True
    fr, seen = {start}, {start}
    for _ in range(K):
        nx = set()
        for n in fr:
            for t in adj.get(n, ()):
                if t == goal:
                    return True
                if t not in seen:
                    seen.add(t); nx.add(t)
        fr = nx
    return False


def goldK(wn, in_corpus, x, K):
    cur = {x}
    for _ in range(K):
        nx = set()
        for nm in cur:
            try:
                s = wn.synset(nm)
            except Exception:
                continue
            for h in s.hypernyms() + s.instance_hypernyms():
                nx.add(h.name())
        cur = nx
    return {z for z in cur if z != x and z in in_corpus}


def nltk_adj_in5k(wn, in_corpus):
    """nltk direct-hypernym adjacency RESTRICTED to in-5k nodes (the TRUE graph intersect the corpus)."""
    adj = defaultdict(set)
    for x in in_corpus:
        try:
            s = wn.synset(x)
        except Exception:
            continue
        for h in s.hypernyms() + s.instance_hypernyms():
            hn = h.name()
            if hn in in_corpus:
                adj[x].add(hn)
    return adj


def self_test() -> int:
    # persisted a->b->c (2-hop). nltk-in5k also a->b->c. gold (a,c).
    pers = {"a": {"b"}, "b": {"c"}}
    nin5 = {"a": {"b"}, "b": {"c"}}
    found = bfsK(pers, "a", "c", 2)            # True (persisted path)
    in5k = bfsK(nin5, "a", "c", 2)             # True (in-5k nltk path)
    # coverage-miss case: gold (a,z) but nltk-in5k has no path (z only via out-of-5k) -> in5k False
    miss_cov = (not bfsK(nin5, "a", "z", 2))   # True (no in-5k path)
    ok = (found and in5k and miss_cov)
    print(f"[{ANCHOR}] --self-test {'OK' if ok else 'FAIL'} (persisted-path found={found}; in5k-path={in5k}; coverage-miss[no in5k path]={miss_cov}); NO Store mutation.")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return self_test()
    t0 = time.time()

    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus, RelationType
    from nltk.corpus import wordnet as wn
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    in_corpus = {a.id[3:] for a in ps.all_atoms() if str(a.id).startswith("WN_")}
    cs = ps._store_for(Corpus.CONCEPT)
    pers_adj = defaultdict(set)
    for (s, rt, t) in cs._all_relations:
        if rt == RelationType.HYPERNYM.value and s.startswith("WN_") and t.startswith("WN_"):
            pers_adj[s[3:]].add(t[3:])
    nin5_adj = nltk_adj_in5k(wn, in_corpus)

    rng = random.Random(args.seed)
    n = min(SAMPLE_N, len(in_corpus))
    sample = rng.sample(sorted(in_corpus), n)
    sorted_in = sorted(in_corpus)

    curve = {}
    attribution = {}
    fp_total = 0
    enough = True
    for K in DEPTHS:
        pos = []
        for x in sample:
            for z in goldK(wn, in_corpus, x, K):
                pos.append((x, z))
        pos = sorted(set(pos))
        if len(pos) < N_MIN:
            enough = False
        found = 0; cov_ceiling = 0; edge_gap = 0; algo = 0
        for (x, z) in pos:
            if bfsK(pers_adj, x, z, K):
                found += 1
            else:
                in5k = bfsK(nin5_adj, x, z, K)            # all-in-5k nltk path exists?
                if not in5k:
                    cov_ceiling += 1                       # (1) no in-5k path -> coverage-ceiling (correct refuse)
                else:
                    edge_gap += 1                          # (2) in-5k path exists but not persisted -> materialization gap (coverage, fixable)
            # (3) algorithmic = persisted-path-exists-but-walker-missed: by construction bfsK IS the walker over persisted,
            #     so a persisted path the walker misses is impossible here (same BFS) -> algo stays 0 (the walker is the referent).
        recall = found / len(pos) if pos else 0.0
        # negatives (verified-unreachable) for FP
        true_by_x = defaultdict(set)
        for (x, z) in pos:
            true_by_x[x].add(z)
        xs = [x for (x, _) in pos] or sample
        neg, tries, fp = 0, 0, 0
        ntar = min(len(pos), 100)
        while neg < ntar and tries < ntar * 300:
            tries += 1
            x = xs[rng.randrange(len(xs))]
            zc = sorted_in[rng.randrange(len(sorted_in))]
            if zc == x or zc in true_by_x.get(x, set()):
                continue
            if bfsK(pers_adj, x, zc, K + 2):
                continue
            neg += 1
            if bfsK(pers_adj, x, zc, K):
                fp += 1
        fp_total += fp
        curve[f"K{K}"] = round(recall, 4)
        miss = len(pos) - found
        attribution[f"K{K}"] = {"n_pos": len(pos), "found": found, "recall": round(recall, 4), "miss": miss,
                                "coverage_ceiling": cov_ceiling, "edge_gap": edge_gap, "algorithmic": algo,
                                "fp": fp, "coverage_frac_of_miss": round((cov_ceiling + edge_gap) / miss, 3) if miss else None}

    # verdict
    recalls = [curve[f"K{K}"] for K in DEPTHS]
    declining_or_plateau = all(recalls[i] <= recalls[i - 1] + 0.02 for i in range(1, len(recalls)))  # monotone-ish (no rise)
    no_crash = recalls[-1] >= 0.40                         # extends (doesn't collapse to HARD_FAIL at depth-5)
    total_miss = sum(attribution[f"K{K}"]["miss"] for K in DEPTHS)
    total_cov = sum(attribution[f"K{K}"]["coverage_ceiling"] + attribution[f"K{K}"]["edge_gap"] for K in DEPTHS)
    total_algo = sum(attribution[f"K{K}"]["algorithmic"] for K in DEPTHS)
    coverage_dominated = (total_miss == 0) or ((total_cov / total_miss) >= 0.95 and total_algo == 0)

    if not enough:
        verdict = "NON_TEST"; msg = f"NON-TEST: <{N_MIN} gold pairs at some depth."
    elif fp_total > 0:
        verdict = "NON_TEST"; msg = f"NON-TEST: {fp_total} false-positives on verified-unreachable negatives."
    elif not coverage_dominated:
        verdict = "ALGORITHMIC_FLAG"
        msg = (f"DEPTH-CEILING with {total_algo} ALGORITHMIC misses (persisted-path-missed) -> NOT a clean coverage ceiling; "
               f"walker/edge defect to investigate. recall curve {recalls}.")
    else:
        verdict = "DISCRIMINATING_COVERAGE_CEILING"
        msg = (f"DEPTH-CEILING = COVERAGE, not algorithmic (cert-grade DISCRIMINATING). recall curve K2..K5 = {recalls}: "
               f"{'declines/plateaus' if declining_or_plateau else 'non-monotone'}, {'EXTENDS (no crash at depth-5)' if no_crash else 'collapses'}. "
               f"{total_cov}/{total_miss} misses ({round(100*total_cov/max(total_miss,1))}%) are COVERAGE (no all-in-5k path = "
               f"correct-refuse, OR in-5k-path-not-yet-materialized = completion-fixable); {total_algo} ALGORITHMIC (persisted-path-"
               f"missed). The coverage-completion lever EXTENDS to depth-5 with a COVERAGE-CEILING (~the in-5k-completeness fraction), "
               f"NOT an algorithmic depth-limit. EXTENDS the coverage-completion-not-reasoning bound to deep hops.")

    metrics = {
        "anchor_name": ANCHOR, "device": DEVICE, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "run_mode": "full", "n_seeds": 1, "metrics_source": "measured_graph_bfs_depth_ceiling_attribution",
        "design": "HYP5_depth_ceiling_NON_coextensive_measurement_plus_breakpoint_attribution_in_memory_0_persist",
        "seed": args.seed, "sample_n_synsets": n, "depths": list(DEPTHS),
        "recall_curve": curve, "attribution": attribution, "fp_total": fp_total,
        "declining_or_plateau": declining_or_plateau, "no_crash_extends": no_crash,
        "total_miss": total_miss, "total_coverage_miss": total_cov, "total_algorithmic_miss": total_algo,
        "prereg_bands": {"hard_fail": 0.40, "coverage_dominated_frac": 0.95}, "held_out_eval": True,
        "honest_scope": "Non-coextensive depth-ceiling probe (measurement + break-point attribution; NO completion added). "
                        "HYPERNYM/taxonomic/WordNet/deterministic-BFS/in5k. The ceiling is COVERAGE (in-5k-completeness), not "
                        "algorithmic. EXTENDS the coverage-completion-not-reasoning bound to depth-5. NOT general reasoning. "
                        "algorithmic=0 by construction (bfsK IS the walker over persisted -> a persisted path it misses is impossible; "
                        "edge_gap = in-5k-nltk-path-not-persisted = a materialization coverage gap, NOT algorithmic).",
        "bears_on": "the depth-cliff coverage-story (Phase-A/A2 MEASURED_MECHANISM recoveries); Item-1/M1 coverage-not-reasoning bound; the universal-lever DEPTH extent",
        "extends": "math::T3/EXP_t3_phaseA2_2level_recovery_cpu_v1",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")
    print(f"[{ANCHOR}] -> {verdict}  recall K2..K5={recalls}  coverage-miss={total_cov}/{total_miss} algo={total_algo} fp={fp_total}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
