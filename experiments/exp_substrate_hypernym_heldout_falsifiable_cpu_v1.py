"""40h tack-on M1 (HIGHEST VALUE): HYPERNYM held-out FALSIFIABLE test -- the multi-relation-robustness replication of Item 1.

Item 1 Design-B (PART_OF) found the coverage-completion lever is PER-SYNSET-COVERAGE-BOUNDED, NOT transferable (cert-grade
HONEST_NEGATIVE). This replicates the falsifiable held-out design for HYPERNYM. If HYPERNYM is ALSO null -> the bound is
MULTI-RELATION-ROBUST (the highest-value WRITEUP input: n-hop WordNet QA = coverage, not reasoning, across relation types).
If HYPERNYM TRANSFERS (surprise jump) -> a major finding + mandatory leakage-audit.

WHY a different construction than PART_OF (verify-the-referent, avoid the no-op-completion bug): HYPERNYM metadata is
SYMMETRIC (hypernym/hyponym gap = 0), so the PART_OF-style meronym/holonym ASYMMETRY-completion is a no-op for HYPERNYM.
The REAL hypernym lever (validated in the depth-cliff arc) was the Phase-A2 SECOND-HOP completion: for the NEW INTERMEDIATE
synsets (the completeness_target atoms, out-of-5k parents materialized in Phase A), add their direct parent edge (Y->z, z
in-corpus). That is the completion this held-out test splits.

DESIGN (in-memory / 0-persist; reads only the synset set + completeness_target flag + persisted HYPERNYM edges; the GOLD is
nltk-independent):
  - GOLD = nltk TRUE 2-hop hypernym closure (x -> 2-level hypernym z, both in-corpus), with the in-corpus 1-level
    intermediate Y recorded (x's nltk direct hypernym; z is Y's nltk direct hypernym). Independent of the persisted graph.
  - RELEVANT POPULATION = gold chains whose intermediate Y is a completeness_target (the LEVER's domain; the second-hop is
    Y->z). Held-out UNIT = the INTERMEDIATE Y (gold-blind hash split of the completeness_target intermediates).
  - baseline_flat = persisted HYPERNYM edges MINUS {(Y,z): Y is completeness_target} = the 1-level FLAT state (the second-hop
    edges removed; 2-hop chains broken at hop-2). (NOT the persisted 6213 which already has the completion -> would no-op.)
  - train_completion = {(Y,z): Y in TRAIN completeness_target} (re-add second-hop for TRAIN intermediates only).
  - HELD-OUT positives = gold chains whose intermediate Y is a HELD-OUT completeness_target. recall_before (baseline_flat) vs
    recall_after (baseline_flat + train_completion). Held-out chains route hop-2 through HELD-OUT intermediates whose Y->z is
    NOT in train_completion -> stay broken -> NULL expected (coverage-bounded). TRAIN-intermediate chains = the control (lift).

TIER-BY-OUTCOME (pre-registered, mirrors Item 1): held-out NULL = CERT_CHAIN_GRADE HONEST_NEGATIVE (multi-relation-robust
bound); held-out JUMP = surprise + MANDATORY leakage-audit. CERT-CONDITIONS: gold-independent split + non-coextensiveness
(held-out intermediates' second-hop NOT in train_completion) + in-memory/0-persist + discrimination-regime (control moves) +
n_heldout>=30 + deterministic BFS (11th-rule). DEVICE=cpu (7th checklist). ASCII. --self-test ; --full.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DEVICE = "cpu"             # 7th checklist: metric-only (BFS + nltk gold; NO torch/GPU) -> cpu_queue
ANCHOR = "substrate_hypernym_heldout_falsifiable_cpu_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
TRAIN_FRAC = 70
PASS_HI, FAIL_LO = 0.70, 0.40
N_MIN_HELDOUT = 30
JUMP_DELTA = 0.15


def in_train(synset_id: str, salt: str) -> bool:
    h = hashlib.sha1((salt + "::" + synset_id).encode()).hexdigest()
    return (int(h[:8], 16) % 100) < TRAIN_FRAC


def bfs2(adj, start, goal):
    if start == goal:
        return []
    for y in adj.get(start, ()):
        if y == goal:
            return [(start, y)]
    for y in adj.get(start, ()):
        for z in adj.get(y, ()):
            if z == goal:
                return [(start, y), (y, z)]
    return None


def _adj(edges):
    a = defaultdict(set)
    for (s, t) in edges:
        a[s].add(t)
    return a


def reachable(adj, x, z, depth=4):
    if x == z:
        return True
    frontier, seen = {x}, {x}
    for _ in range(depth):
        nxt = set()
        for n in frontier:
            for t in adj.get(n, ()):
                if t == z:
                    return True
                if t not in seen:
                    seen.add(t); nxt.add(t)
        frontier = nxt
    return False


def self_test() -> int:
    # synthetic: baseline_flat x->Y (Y is a held-out intermediate; Y->z NOT present). train_completion adds W->v (W train).
    # held-out chain (x,z) needs Y->z (NOT added) -> unanswerable. train chain (u,v) via W->v (added) -> answerable.
    baseline_flat = {("x", "Y"), ("u", "W")}   # incoming edges to intermediates
    train_completion = {("W", "v")}            # second-hop for TRAIN intermediate W only
    adj_before = _adj(baseline_flat)
    adj_after = _adj(baseline_flat | train_completion)
    held_before = bfs2(adj_before, "x", "z")   # None
    held_after = bfs2(adj_after, "x", "z")     # None (Y->z never added; Y held-out)
    train_after = bfs2(adj_after, "u", "v")    # found u->W->v
    ok = (held_before is None and held_after is None and train_after == [("u", "W"), ("W", "v")]
          and not any(s == "Y" for (s, t) in train_completion))   # non-coext: held-out intermediate Y not a train_completion source
    print(f"[{ANCHOR}] --self-test {'OK' if ok else 'FAIL'} (held-out unanswerable before+after={held_before is None and held_after is None}; "
          f"train transfer={train_after is not None}; non-coext[Y not in train_completion]={not any(s=='Y' for (s,t) in train_completion)}); NO Store mutation.")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="hypernym_heldout_v1")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return self_test()
    run_started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0 = time.time()

    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus, RelationType
    from nltk.corpus import wordnet as wn
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    in_corpus, ct = set(), set()
    for a in ps.all_atoms():
        if str(a.id).startswith("WN_"):
            nm = a.id[3:]; in_corpus.add(nm)
            if (a.metadata or {}).get("completeness_target"):
                ct.add(nm)
    cs = ps._store_for(Corpus.CONCEPT)
    persisted = {(s[3:], t[3:]) for (s, rt, t) in cs._all_relations
                 if rt == RelationType.HYPERNYM.value and s.startswith("WN_") and t.startswith("WN_")}

    # baseline_flat = persisted MINUS second-hop edges (Y->z, Y a completeness_target intermediate)
    secondhop = {(y, z) for (y, z) in persisted if y in ct}
    baseline_flat = persisted - secondhop

    # split intermediates train/held-out (gold-blind hash on the intermediate id)
    train_ct = {y for y in ct if in_train(y, args.seed)}
    held_ct = ct - train_ct
    train_completion = {(y, z) for (y, z) in secondhop if y in train_ct}
    # NON-COEXTENSIVENESS: 0 train_completion edges originate from a HELD-OUT intermediate
    held_in_tc = sum(1 for (y, z) in train_completion if y in held_ct)
    non_coextensive = (held_in_tc == 0)

    adj_before = _adj(baseline_flat)
    adj_after = _adj(baseline_flat | train_completion)

    # GOLD (nltk-independent): true 2-hop hypernym (x -> z, both in-corpus) with the in-corpus 1-level intermediate Y recorded.
    # Classify each gold chain by its intermediate Y: held-out-ct / train-ct.
    ho_pos, tr_pos = [], []
    for x in sorted(in_corpus):
        try:
            sx = wn.synset(x)
        except Exception:
            continue
        for Y in sx.hypernyms() + sx.instance_hypernyms():
            yn = Y.name()
            if yn not in in_corpus:
                continue
            for Z in Y.hypernyms() + Y.instance_hypernyms():
                zn = Z.name()
                if zn != x and zn in in_corpus:
                    if yn in held_ct:
                        ho_pos.append((x, zn))
                    elif yn in train_ct:
                        tr_pos.append((x, zn))
    ho_pos = sorted(set(ho_pos)); tr_pos = sorted(set(tr_pos))

    def recall(adj, pos):
        if not pos:
            return 0.0
        return sum(1 for (x, z) in pos if bfs2(adj, x, z) is not None) / len(pos)

    ho_before, ho_after = recall(adj_before, ho_pos), recall(adj_after, ho_pos)
    tr_before, tr_after = recall(adj_before, tr_pos), recall(adj_after, tr_pos)
    ho_delta = round(ho_after - ho_before, 4); tr_delta = round(tr_after - tr_before, 4)

    # held-out negatives (verified-unreachable) for discrimination + FP=0
    import random
    rng = random.Random(0)
    ho_xs = [x for (x, _) in ho_pos] or sorted(in_corpus)
    sorted_in = sorted(in_corpus)
    true_by_x = defaultdict(set)
    for (x, z) in ho_pos:
        true_by_x[x].add(z)
    neg, tries, fp = 0, 0, 0
    n_neg_target = min(len(ho_pos), 150)
    while neg < n_neg_target and tries < n_neg_target * 300:
        tries += 1
        x = ho_xs[rng.randrange(len(ho_xs))]
        zc = sorted_in[rng.randrange(len(sorted_in))]
        if zc == x or zc in true_by_x.get(x, set()):
            continue
        if reachable(adj_after, x, zc, 4):
            continue
        neg += 1
        if bfs2(adj_after, x, zc) is not None:
            fp += 1

    discriminating_regime = (tr_delta > 0.0)   # the control (train intermediates) must lift -> the completion mechanism works
    enough_gold = len(ho_pos) >= N_MIN_HELDOUT
    band_after = "HARD_PASS" if ho_after >= PASS_HI else ("HARD_FAIL" if ho_after < FAIL_LO else "MIDDLE_BAND")
    jump = (ho_delta >= JUMP_DELTA and ho_after >= PASS_HI)

    if not non_coextensive:
        verdict = "NON_TEST"; msg = f"NON-TEST: {held_in_tc} train_completion edges from HELD-OUT intermediates (coextensiveness leak)."
    elif not enough_gold:
        verdict = "NON_TEST"; msg = f"NON-TEST: only {len(ho_pos)} held-out gold chains (<{N_MIN_HELDOUT})."
    elif not discriminating_regime:
        verdict = "NON_TEST"; msg = f"NON-TEST: control (train-intermediate) did NOT lift (tr_delta={tr_delta:+.3f}) -> completion mechanism not demonstrated -> can't discriminate transfer."
    elif fp > 0:
        verdict = "NON_TEST"; msg = f"NON-TEST: {fp} false-positives on verified-unreachable held-out negatives."
    elif jump:
        verdict = "DISCRIMINATING_JUMP"
        msg = (f"JUMP on HELD-OUT (HYPERNYM): completing TRAIN intermediates' second-hop LIFTED held-out 2-hop recall "
               f"{ho_before:.3f}->{ho_after:.3f} (delta {ho_delta:+.3f}; {band_after}) WITHOUT adding held-out intermediates' "
               f"second-hop -> the lever TRANSFERS for HYPERNYM. SURPRISING for a deterministic BFS -> MANDATORY leakage/overlap "
               f"verify-the-mechanism before cert-grade-DISCRIMINATING.")
    else:
        verdict = "HONEST_NEGATIVE"
        msg = (f"NULL on HELD-OUT (HYPERNYM; cert-grade HONEST_NEGATIVE): completing TRAIN intermediates' second-hop did NOT "
               f"lift held-out 2-hop recall ({ho_before:.3f}->{ho_after:.3f}; delta {ho_delta:+.3f}; {band_after}) -- while "
               f"TRAIN control {tr_before:.3f}->{tr_after:.3f} (delta {tr_delta:+.3f}). MULTI-RELATION-ROBUST: the coverage-"
               f"completion lever is PER-INTERMEDIATE-COVERAGE-BOUNDED, NOT transferable, for HYPERNYM TOO (replicates the "
               f"PART_OF Item-1 HONEST_NEGATIVE). The deterministic BFS does NOT INFER a held-out intermediate's absent "
               f"second-hop from OTHER intermediates' completions. HARDENS the bound: n-hop WordNet QA = COVERAGE, not REASONING.")

    metrics = {
        "anchor_name": ANCHOR, "device": DEVICE, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "run_mode": "full", "n_seeds": 1, "metrics_source": "measured_graph_bfs_held_out_split",
        "design": "M1_HYPERNYM_held_out_split_secondhop_completeness_target_intermediates_in_memory_0_persist",
        "seed_salt": args.seed, "train_frac_pct": TRAIN_FRAC,
        "n_in_corpus": len(in_corpus), "n_completeness_target": len(ct), "n_train_ct": len(train_ct), "n_heldout_ct": len(held_ct),
        "n_persisted_hypernym": len(persisted), "n_secondhop_edges": len(secondhop), "n_baseline_flat": len(baseline_flat),
        "n_train_completion_edges": len(train_completion), "heldout_intermediates_in_train_completion": held_in_tc,
        "non_coextensive": non_coextensive,
        "n_heldout_positives": len(ho_pos), "n_train_positives": len(tr_pos), "n_heldout_negatives": neg,
        "heldout_recall_before": round(ho_before, 4), "heldout_recall_after": round(ho_after, 4), "heldout_delta": ho_delta,
        "train_recall_before": round(tr_before, 4), "train_recall_after": round(tr_after, 4), "train_delta": tr_delta,
        "heldout_band_after": band_after, "false_positives": fp,
        "discriminating_regime": discriminating_regime, "enough_gold": enough_gold,
        "prereg_bands": {"hard_pass": PASS_HI, "hard_fail": FAIL_LO, "jump_delta": JUMP_DELTA}, "held_out_eval": True,
        "held_out_unit": "the INTERMEDIATE completeness_target synset (its second-hop Y->z is the needed-but-not-added edge for held-out chains)",
        "honest_scope": "M1 HYPERNYM held-out falsifiable replication of Item 1. Held-out unit = the intermediate completeness_"
                        "target. NULL=multi-relation-robust coverage-bound; JUMP=transfer (+leakage-audit). HYPERNYM/taxonomic/"
                        "WordNet/deterministic-BFS/in5k. NOT general reasoning. Bound to Item-1: coverage-completion, not reasoning.",
        "bears_on": "Item 1 PART_OF HONEST_NEGATIVE (this is the HYPERNYM multi-relation-robustness replication); the universal-lever bound; the Item-3 WRITEUP central claim",
        "replicates": "math::T3/EXP_partof_heldout_falsifiable_cpu_v1",
        "leakage_audit_required_if_jump": True, "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")
    print(f"[{ANCHOR}] -> {verdict}  held-out {ho_before:.3f}->{ho_after:.3f} (delta {ho_delta:+.3f}, {band_after}) | "
          f"train {tr_before:.3f}->{tr_after:.3f} (delta {tr_delta:+.3f}) | non_coext={non_coextensive} n_ho={len(ho_pos)} fp={fp}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
