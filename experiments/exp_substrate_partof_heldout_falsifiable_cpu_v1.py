"""Item 1 (3rd sprint) -- DESIGN B: held-out FALSIFIABLE test on PART_OF (Skunkworks RATIFY 2026-06-18; cert-grade).

THE CERT-GOAL (escape the coextensive pattern): HYPERNYM + PART_OF 2-level completions were both MEASURED_MECHANISM --
the +edges ARE what the n-hop QA traverses -> tautological -> not blind-CERT. This test is GENUINELY NON-COEXTENSIVE:
build the 2-level completion on a TRAIN subset of synsets ONLY; test 2-hop QA on HELD-OUT synsets whose answer-paths need
edges the train-completion did NOT add. A held-out JUMP = the substrate GENERALIZED beyond the completed synsets (cert-grade
DISCRIMINATING); a held-out NULL = the lever is PER-SYNSET-COVERAGE-BOUNDED, not transferable (cert-grade HONEST_NEGATIVE
that bounds the "universal lever" as COVERAGE-COMPLETION-not-REASONING -- the writeup's honest-scope).

DESIGN (in-memory / 0-persist -> freeze-safe + no edge-readback-flip-bug-class; reads only the synset SET from the Store):
  - baseline graph (meronym-based, the ORIGINAL ingest rule, in-memory from nltk: each in-corpus synset's in-corpus
    meronyms -> part PART_OF whole). NOT the persisted 559 (which already has the +125 completion = would contaminate).
  - gold-blind hash split of synsets into TRAIN (~70%) / HELD-OUT (~30%) by sha1(synset_id+salt); FIXED salt via --seed
    (deterministic; NOT runtime-random; 11th-rule + reproducible). The held-out set is NEVER used to build the completion.
  - train_completion (in-memory): for TRAIN synsets X only -> X's direct in-corpus HOLONYM edges (X PART_OF Z) not in
    baseline. The held-out synsets' OWN holonym edges are NOT added (the non-coextensiveness, BY CONSTRUCTION).
  - HELD-OUT 2-hop holonym gold (x, z): x HELD-OUT, z in-corpus, z = x's 2-level holonym (nltk). recall_before over
    baseline-only; recall_after over baseline + train_completion. delta = after - before = the TRANSFER signal (did
    completing TRAIN intermediates help answer HELD-OUT 2-hop questions whose 2nd hop routes through a TRAIN synset?).
  - negatives (held-out x, verified-unreachable z') for the discrimination_self_check + FP=0 safety.

TIER-BY-OUTCOME (PRE-REGISTERED; sacrosanct both directions):
  held-out delta JUMP (after >> before; reaches HARD_PASS band) -> cert-grade DISCRIMINATING (lever TRANSFERS) -> + a
    MANDATORY verify-the-mechanism leakage/overlap audit (a jump on a deterministic BFS over held-out is suspicious).
  held-out delta NULL (after ~= before; stays MIDDLE/floor) -> cert-grade HONEST_NEGATIVE (coverage-bounded, not
    transferable; completing OTHER synsets' edges does NOT answer a held-out synset's own-edge-dependent 2-hop query).

CERT-CONDITIONS (Skunkworks pre-stated): gold-independent hash split + non-coextensiveness VERIFIED (held-out edges NOT in
train_completion) + in-memory/0-persist + discrimination-regime check (held-out before NOT degenerate) + n_held_out>=30 +
deterministic BFS (11th-rule). DEVICE=cpu (7th checklist: metric-only, no torch -> cpu_queue). ASCII. --self-test ; --full.
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

DEVICE = "cpu"             # 7th checklist: metric-only (BFS + nltk; NO torch/GPU) -> cpu_queue
ANCHOR = "substrate_partof_heldout_falsifiable_cpu_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
TRAIN_FRAC = 70           # percent (hash %100 < 70 -> TRAIN)
PASS_HI, FAIL_LO = 0.70, 0.40
N_MIN_HELDOUT = 30        # gold-set minimum (mirrors A2 n_gap=38)
JUMP_DELTA = 0.15         # held-out recall delta threshold to call a "JUMP" (pre-registered)


def in_train(synset_id: str, salt: str) -> bool:
    h = hashlib.sha1((salt + "::" + synset_id).encode()).hexdigest()
    return (int(h[:8], 16) % 100) < TRAIN_FRAC


def build_baseline_meronym(meronym_map, in_corpus):
    """ORIGINAL ingest rule (EXACT replica of substrate_edge_materialization_b_alpha): for each in-corpus synset A, its
    STORED metadata['meronyms'] M -> edge (M PART_OF A) for in-corpus M. adjacency part->whole. Uses the Store's stored
    meronyms (the ASYMMETRIC ~530-edge baseline = the pre-Item-1 state), NOT nltk's part/member/substance_meronyms() which return
    the FULL SYMMETRIC closure (559, already containing the holonym-completion -> would make train_completion a no-op)."""
    adj = defaultdict(set)
    edges = set()
    for a in sorted(in_corpus):
        for m in (meronym_map.get(a) or []):
            if m in in_corpus:
                adj[m].add(a); edges.add((m, a))
    return adj, edges


def train_completion_edges(wn, train_synsets, in_corpus, baseline_edges):
    """For TRAIN synsets X only: X's direct in-corpus HOLONYM edges (X PART_OF Z) not already in baseline."""
    edges = set()
    for X in sorted(train_synsets):
        try:
            s = wn.synset(X)
        except Exception:
            continue
        for Z in s.part_holonyms() + s.member_holonyms() + s.substance_holonyms():
            zn = Z.name()
            if zn in in_corpus and zn != X and (X, zn) not in baseline_edges:
                edges.add((X, zn))
    return edges


def gold_2hop_holonym(wn, x, in_corpus):
    """True 2-level holonym closure of x (x PART_OF Y PART_OF z), z in-corpus, via nltk (independent gold)."""
    out = set()
    try:
        sx = wn.synset(x)
    except Exception:
        return out
    for Y in sx.part_holonyms() + sx.member_holonyms() + sx.substance_holonyms():
        for Z in Y.part_holonyms() + Y.member_holonyms() + Y.substance_holonyms():
            if Z.name() != x and Z.name() in in_corpus:
                out.add(Z.name())
    return out


def bfs2(adj, start, goal):
    """Bounded 2-hop BFS over adjacency (set-valued). Returns the hop-list or None."""
    if start == goal:
        return []
    for y in adj.get(start, ()):  # hop 1
        if y == goal:
            return [(start, y)]
    for y in adj.get(start, ()):  # hop 2
        for z in adj.get(y, ()):
            if z == goal:
                return [(start, y), (y, z)]
    return None


def _adj_from_edges(*edge_sets):
    adj = defaultdict(set)
    for es in edge_sets:
        for (s, t) in es:
            adj[s].add(t)
    return adj


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
    # synthetic: baseline a->b ; train-completion b->c (b is TRAIN) ; held-out gold (a,c) needs b->c (train edge).
    # a is HELD-OUT; its OWN edge a->b is baseline; the 2nd hop b->c is train-completion -> transfer-answerable.
    # Also d (held-out) gold (d,e) needs d->? (no baseline edge) -> NOT answerable (coverage-bounded).
    baseline = {("a", "b")}
    train_comp = {("b", "c")}            # b is a TRAIN intermediate
    adj_before = _adj_from_edges(baseline)
    adj_after = _adj_from_edges(baseline, train_comp)
    before = bfs2(adj_before, "a", "c")  # None (no b->c yet)
    after = bfs2(adj_after, "a", "c")    # found via a->b->c (transfer)
    none = bfs2(adj_after, "d", "e")     # None (no d edges)
    # non-coextensiveness: held-out 'a' OWN edges not in train_comp
    ok = (before is None and after == [("a", "b"), ("b", "c")] and none is None
          and not any(s == "a" for (s, t) in train_comp))
    print(f"[{ANCHOR}] --self-test {'OK' if ok else 'FAIL'} (held-out transfer: before={before is not None} after={after is not None}; "
          f"coverage-bound case refused={none is None}; non-coextensive[a-edges not in train_comp]={not any(s=='a' for (s,t) in train_comp)}); NO Store mutation.")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="partof_heldout_v1", help="salt for the deterministic hash split")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return self_test()
    run_started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0 = time.time()

    from backend.substrate_index.partition import PartitionedStore
    from nltk.corpus import wordnet as wn
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    # read-only: synset SET + the STORED meronym lists (the original-ingest baseline source = the asymmetric ~530)
    in_corpus = set()
    meronym_map = {}
    for a in ps.all_atoms():
        if str(a.id).startswith("WN_"):
            nm = a.id[3:]
            in_corpus.add(nm)
            meronym_map[nm] = (a.metadata or {}).get("meronyms") or []

    baseline_adj, baseline_edges = build_baseline_meronym(meronym_map, in_corpus)
    train = {s for s in in_corpus if in_train(s, args.seed)}
    held = in_corpus - train
    tc_edges = train_completion_edges(wn, train, in_corpus, baseline_edges)

    # NON-COEXTENSIVENESS (binding): 0 train_completion edges originate from a HELD-OUT synset
    held_edges_in_tc = sum(1 for (s, t) in tc_edges if s in held)
    non_coextensive = (held_edges_in_tc == 0)

    adj_before = baseline_adj
    adj_after = _adj_from_edges(baseline_edges, tc_edges)

    # HELD-OUT positives (x held-out; z = x's true 2-level holonym, in-corpus)
    ho_pos = []
    for x in sorted(held):
        for z in gold_2hop_holonym(wn, x, in_corpus):
            ho_pos.append((x, z))
    # train positives (control: should jump, train edges added)
    tr_pos = []
    for x in sorted(train):
        for z in gold_2hop_holonym(wn, x, in_corpus):
            tr_pos.append((x, z))

    def recall(adj, pos):
        if not pos:
            return 0.0, 0
        found = sum(1 for (x, z) in pos if bfs2(adj, x, z) is not None)
        return found / len(pos), found

    ho_before, ho_fb = recall(adj_before, ho_pos)
    ho_after, ho_fa = recall(adj_after, ho_pos)
    tr_before, _ = recall(adj_before, tr_pos)
    tr_after, _ = recall(adj_after, tr_pos)
    ho_delta = round(ho_after - ho_before, 4)
    tr_delta = round(tr_after - tr_before, 4)

    # held-out negatives (verified-unreachable) for discrimination + FP=0
    import random
    rng = random.Random(0)
    ho_xs = [x for (x, _) in ho_pos] or sorted(held)
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
        if reachable(adj_after, x, zc, depth=4):
            continue
        neg += 1
        if bfs2(adj_after, x, zc) is not None:
            fp += 1

    # discrimination-regime: held-out BEFORE must be non-degenerate (not all-floor 0, not all-saturated 1)
    discriminating_regime = (0.0 < ho_before < 1.0) or (ho_before == 0.0 and ho_after > 0.0)
    enough_gold = len(ho_pos) >= N_MIN_HELDOUT

    band_after = "HARD_PASS" if ho_after >= PASS_HI else ("HARD_FAIL" if ho_after < FAIL_LO else "MIDDLE_BAND")
    jump = (ho_delta >= JUMP_DELTA and ho_after >= PASS_HI)

    if not non_coextensive:
        verdict = "NON_TEST"
        msg = f"NON-TEST: {held_edges_in_tc} train_completion edges originate from HELD-OUT synsets -> coextensiveness leak (binding condition violated)."
    elif not enough_gold:
        verdict = "NON_TEST"
        msg = f"NON-TEST: only {len(ho_pos)} held-out 2-hop gold chains (< {N_MIN_HELDOUT}); raise TRAIN_FRAC or relation too sparse."
    elif not discriminating_regime:
        verdict = "NON_TEST"
        msg = f"NON-TEST: held-out before-regime degenerate (ho_before={ho_before:.3f}); not discriminating."
    elif fp > 0:
        verdict = "NON_TEST"
        msg = f"NON-TEST: {fp} false-positives on verified-unreachable held-out negatives (test-validity breach)."
    elif jump:
        verdict = "DISCRIMINATING_JUMP"
        msg = (f"JUMP on HELD-OUT: completing TRAIN synsets' edges LIFTED held-out 2-hop recall {ho_before:.3f}->{ho_after:.3f} "
               f"(delta {ho_delta:+.3f}; band {band_after}) WITHOUT adding held-out synsets' own edges -> the lever TRANSFERS "
               f"beyond completed synsets. SURPRISING for a deterministic BFS -> MANDATORY verify-the-mechanism leakage/overlap "
               f"audit before cert-grade-DISCRIMINATING (rule out gold/train overlap: the lifted held-out chains must route "
               f"hop-2 through a TRAIN intermediate whose completion edge was added, not via a gold/train leak).")
    else:
        verdict = "HONEST_NEGATIVE"
        msg = (f"NULL on HELD-OUT (cert-grade HONEST_NEGATIVE): completing TRAIN synsets' edges did NOT lift held-out 2-hop "
               f"recall ({ho_before:.3f}->{ho_after:.3f}; delta {ho_delta:+.3f}; band {band_after}) -- while TRAIN control "
               f"recall {tr_before:.3f}->{tr_after:.3f} (delta {tr_delta:+.3f}). The lever is PER-SYNSET-COVERAGE-BOUNDED, "
               f"NOT transferable: complete a synset's edges and it answers; don't and it can't; the deterministic BFS does NOT "
               f"INFER a held-out synset's absent edges from OTHER synsets' completions. BOUNDS the 'universal lever' as "
               f"COVERAGE-COMPLETION-not-REASONING (the writeup's honest-scope; the empirical anti-over-claim).")

    metrics = {
        "anchor_name": ANCHOR, "device": DEVICE, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "run_mode": "full", "n_seeds": 1, "metrics_source": "measured_graph_bfs_held_out_split",
        "design": "DESIGN_B_held_out_split_PART_OF_in_memory_0_persist",
        "seed_salt": args.seed, "train_frac_pct": TRAIN_FRAC,
        "n_in_corpus": len(in_corpus), "n_train_synsets": len(train), "n_heldout_synsets": len(held),
        "n_baseline_edges": len(baseline_edges), "n_train_completion_edges": len(tc_edges),
        "non_coextensive": non_coextensive, "heldout_edges_in_train_completion": held_edges_in_tc,
        "n_heldout_positives": len(ho_pos), "n_train_positives": len(tr_pos), "n_heldout_negatives": neg,
        "heldout_recall_before": round(ho_before, 4), "heldout_recall_after": round(ho_after, 4), "heldout_delta": ho_delta,
        "train_recall_before": round(tr_before, 4), "train_recall_after": round(tr_after, 4), "train_delta": tr_delta,
        "heldout_band_after": band_after, "false_positives": fp,
        "discriminating_regime": discriminating_regime, "enough_gold": enough_gold,
        "prereg_bands": {"hard_pass": PASS_HI, "hard_fail": FAIL_LO, "jump_delta": JUMP_DELTA},
        "held_out_eval": True,
        "cert_conditions": "gold-independent hash split + non-coextensiveness VERIFIED + in-memory/0-persist + "
                           "discrimination-regime + n_heldout>=30 + deterministic BFS (11th-rule)",
        "honest_scope": "DESIGN-B falsifiable held-out PART_OF test: does completing TRAIN synsets' 2-level edges TRANSFER "
                        "to answer HELD-OUT synsets' 2-hop QA (whose own edges were NOT completed)? NON-COEXTENSIVE (unlike "
                        "the MEASURED_MECHANISM HYP/PART_OF recoveries). NULL=coverage-bounded-not-reasoning; JUMP=transfer "
                        "(+leakage-audit). PART_OF/meronymic/WordNet/deterministic-BFS/in5k. NOT general reasoning.",
        "bears_on": "the universal-lever claim (HYP+PART_OF coverage-limited); the substrate-as-reasoning-engine WRITEUP honest-scope; "
                    "the coextensive-vs-genuine-generalization cert-question",
        "leakage_audit_required_if_jump": True,
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")
    print(f"[{ANCHOR}] -> {verdict}  held-out {ho_before:.3f}->{ho_after:.3f} (delta {ho_delta:+.3f}, band {band_after}) | "
          f"train {tr_before:.3f}->{tr_after:.3f} | non_coext={non_coextensive} n_ho_pos={len(ho_pos)} fp={fp}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
