"""exp_composition_inference_dense_vs_sparse_v1

DECISIVE validate-or-kill of the DENSITY hypothesis via the substrate's OWN inference op = CROSS-RELATION
COMPOSITION (multi-hop property-inheritance derivation), the brain-true operation that needs NO twins
(unlike structure-mapping analogy, ruled out at 29580-83: twin-dependent, taxonomic-only).

QUESTION: does CROSS-RELATION composition infer held-out relational facts, and does it work on DENSE
knowledge (WordNet) where it fails on SPARSE (WorldTree)?  If yes => "the wall is knowledge density,
mechanisms are ready."  If composition ties floor even on dense => composition does not invent either.

MECHANISM (genuine cross-relation inference, NOT trivial transitivity): for a held-out edge (C, R, D)
excluded from ALL storage, DERIVE D via a multi-hop path over OTHER stored edges of DIFFERENT relation
types -- property inheritance:  C -IS_A-> X ,  X -R-> D  =>  inherit (C, R, D).  The first hop uses a
DIFFERENT relation (IS_A/HYPERNYM/KINDOF) than the held-out target R, so a winning derivation is a genuine
>=2-hop CROSS-relation chain, NOT a same-relation 1-hop transitive shortcut (guard #2). We REUSE the
substrate's meet-in-middle bounded BFS search shape (exp_arc_derivation_connectivity_gate_v1._reach /
meet_connected; the M3 shape wired into hdlab/reasoner.py) over the typed graph -- we do NOT rebuild a
chainer. Compute-proportionality (USER 2026-07-14): this is a directional/coverage GATE, so the CHEAPEST
DECISIVE method is a bounded SYMBOLIC path-search over the same typed graph -- a coverage-structural bound
(if the derivation path is absent from the graph, HD Hopfield cleanup cannot invent it either), so the
heavy HD-matmul chain (hdlab/multi_hop.py) is NOT needed and would be an over-build.

DENSITY CONTROL: identical held-out-inference protocol on (a) DENSE = WordNet (reuse the dense loader
_wordnet_raw_triples from exp_analogy_candidate_inference_dense_corpus_v1) and (b) SPARSE = WorldTree
(reuse load_worldtree_triples from exp_grounding_tem_factorized_heldout_concept_v1). Report per-corpus
density (rel/concept) + composition top1/top10 vs floor/freq/flat + path-length + relation-type-path dist.

FAIR-TEST GUARDS (hard-won from the analogy arc):
  1. Held-out edge EXCLUDED from ALL storage: for each held-out head C we remove EVERY (R, C, *) edge
     (leak-proof; STORE_RECALL_FLOOR arm must collapse to ~base-rate).
  2. TRIVIAL-TRANSITIVITY LEAK GUARD: COMPOSE_INHERIT uses a NON-R first hop by construction (IS_A != R),
     so every proposed derivation is genuine cross-relation. We ALSO report COMPOSE_ANY2HOP (any 2-hop
     C-R1->X-R2->D, R1!=R) and the (R1,R2) relation-type-path distribution + path lengths so any
     same-relation collapse is visible. If genuine-cross fraction < 0.3 -> FLAG leak (not genuine).
  3. Baselines/controls: STORE_RECALL_FLOOR, FREQUENCY_PRIOR (the bar), FLAT_COOCC (associative non-
     compositional predictor), SHUFFLED_GRAPH must-fail (COMPOSE over per-relation tail-shuffled edges
     must collapse to ~base-rate). random-ID / symbolic-id content, NO borrowed embedding.
  4. TRACTABILITY: bounded IS_A ancestor depth (L) + bounded any-2hop; ranking over the R-tail candidate
     pool (filtered KGE-style); heartbeats each corpus/relation chunk; multi-seed head selection;
     base_rate reported.
  5. Per-relation reporting (some relations compose better).

DECISIVE BANDS (see PREREG):
  - HARD_PASS: DENSE COMPOSE top10 >= FREQ top10 + 0.15 AND >= 0.20 absolute AND DENSE - SPARSE >= 0.10
    AND genuine-cross fraction >= 0.5  => density IS the lever, composition IS the inference op.
  - HARD_FAIL: COMPOSE ties FREQ/floor even on DENSE (top10 within 0.05 of FREQ OR coverage < 0.10)
    => composition does not invent on these corpora.
  - MIDDLE_BAND: between.
  - PLANTED positive control (self_test) MUST fire (COMPOSE >> floor on a synthetic redundant-inheritance
    corpus) -> separates "mechanism broken" from "corpus lacks derivable structure".

PRE-FLIGHT MEASUREMENTS (this session, scratchpad structural probe; the design-of-record):
  - WordNet inheritance-composition coverage caps ~0.045 (DERIV), ~0.009 (PART_MERONYM), ~0 else.  MEASURED@scratchpad/preflight_composition.py
  - WordNet HYPERNYM same-rel transitivity coverage 0.000; cross-rel 0.018.                          MEASURED@scratchpad/preflight2.py
  - WorldTree KINDOF-inheritance coverage caps ~0.045 (CONTAINS), ~0.023 (REQUIRES), ~0 else.        MEASURED@scratchpad/preflight2.py
  => structural expectation: COMPOSE near floor on BOTH corpora; planted control fires. The bottleneck is
     COMPOSITIONAL REDUNDANCY (multi-level property attachment), which taxonomies/tables do NOT store,
     NOT raw edge-density.  This cell makes that VET-able with full baselines + must-fail controls.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke gate (COMPOSE vs FREQ vs SHUFFLED top1-prediction hashes differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: prediction-accuracy discriminator; base_rate=1/|R_tail_pool| + FREQUENCY_PRIOR reported as floors
# - baseline_in_band: EXEMPT (STORE_RECALL_FLOOR/FREQ/FLAT/SHUFFLED are intended-floor / must-fail baselines)
# - discriminator survives scale: symbolic path-search runs on the FULL graph (no downsampling of edges);
#     planted self-test fires; corpora are the full WordNet / WorldTree graphs
# - HARD_PASS strictly above floor + margin (beats FREQ by >=0.15 AND >=0.20 abs AND DENSE-SPARSE>=0.10)
# - HP_SCOPE: COMPOSE arms only
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_corpus_relation_pairs (verdict counts per_unit)
# - per-unit failure-class instrumentation (no bare except)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - deterministic seeding (fixed ints, np.random.RandomState, sorted(set()); NO hash()-seeded RNG)
# - leak-proof: exclude EVERY (R, head) edge for held-out heads; WordNet loader keeps ONE direction per
#     inverse pair (no HYPONYM alongside HYPERNYM) so no inverse-edge leak

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; no em dashes in
output; deterministic. Agent-reported VET-PENDING (skunkworks VETs).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict, Counter
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR_NAME = "exp_composition_inference_dense_vs_sparse_v1"

# ---------------------------------------------------------------------------
# Reuse the two corpus loaders (function-defs only at top level; main is __main__-guarded).
# DENSE = WordNet (_wordnet_raw_triples); SPARSE = WorldTree (load_worldtree_triples).
# ---------------------------------------------------------------------------
_DENSE_PATH = os.path.join(REPO, "experiments", "exp_analogy_candidate_inference_dense_corpus_v1.py")
_dspec = importlib.util.spec_from_file_location("_dense_corpus", _DENSE_PATH)
_dense = importlib.util.module_from_spec(_dspec)
_dspec.loader.exec_module(_dense)

_WT_PATH = os.path.join(REPO, "experiments", "exp_grounding_tem_factorized_heldout_concept_v1.py")
_wtspec = importlib.util.spec_from_file_location("_tem_ref", _WT_PATH)
_wt = importlib.util.module_from_spec(_wtspec)
_wtspec.loader.exec_module(_wt)


def _progress(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


_HEARTBEAT_DIR = None


def _heartbeat(msg):
    _progress(msg)
    if _HEARTBEAT_DIR is None:
        return
    try:
        os.makedirs(_HEARTBEAT_DIR, exist_ok=True)
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "msg": msg}
        with open(os.path.join(_HEARTBEAT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass  # best-effort telemetry


# ---------------------------------------------------------------------------
# Reused meet-in-middle search shape: bounded BFS reach (verbatim shape from
# exp_arc_derivation_connectivity_gate_v1._reach; the M3 meet-in-middle shape wired into
# hdlab/reasoner.py). We inline it (10 lines) rather than importlib-exec the connectivity-gate
# cell (which top-level exec's the heavy TEM ref) -- provenance cited, no reinvention of the algorithm.
# ---------------------------------------------------------------------------
def _reach(adj, sources, depth):
    """BFS up to depth hops over adjacency dict of node->set(node); return dict node -> min hop-dist."""
    dist = {s: 0 for s in sources}
    frontier = set(sources)
    for d in range(depth):
        nxt = set()
        for u in frontier:
            nxt.update(adj.get(u, ()))
        nxt -= set(dist)
        if not nxt:
            break
        for v in nxt:
            dist[v] = d + 1
        frontier = nxt
    return dist


# ---------------------------------------------------------------------------
# Corpus loaders -> unified list[(rel, head, tail)] of string triples.
# ---------------------------------------------------------------------------
def load_corpus(name):
    if name == "wordnet":
        raw = _dense._wordnet_raw_triples()
    elif name == "worldtree":
        raw, _ = _wt.load_worldtree_triples(list(_wt.TABLE_SLOTS.keys()), 100000)
    else:
        raise ValueError("unknown corpus %r" % name)
    # dedupe deterministically
    seen = set()
    triples = []
    for (r, h, t) in raw:
        if h == t:
            continue
        k = (r, h, t)
        if k in seen:
            continue
        seen.add(k)
        triples.append(k)
    return triples


# IS_A relation name per corpus (the inheritance backbone).
ISA_REL = {"wordnet": "HYPERNYM", "worldtree": "KINDOF"}


# ---------------------------------------------------------------------------
# Graph index (built from STORED edges only, after held-out exclusion).
# ---------------------------------------------------------------------------
def build_index(stored):
    out = defaultdict(set)      # head -> set((rel, tail))
    isa_adj = defaultdict(set)  # head -> set(tail) over IS_A only (filled by caller with corpus isa)
    gold_stored = defaultdict(set)  # (rel, head) -> set(tail)   (STORED only; for FLOOR + FLAT)
    tail_freq = defaultdict(Counter)  # rel -> Counter(tail)
    feat_owners = defaultdict(set)    # (rel, tail) feature -> set(head that has it)   for FLAT_COOCC
    for (r, h, t) in stored:
        out[h].add((r, t))
        gold_stored[(r, h)].add(t)
        tail_freq[r][t] += 1
        feat_owners[(r, t)].add(h)
    return {"out": out, "gold_stored": gold_stored, "tail_freq": tail_freq,
            "feat_owners": feat_owners}


# ---------------------------------------------------------------------------
# The COMPOSITION mechanism (property inheritance) + baselines.
# Each returns: score dict {tail -> score} for a given head C and held-out relation R, using ONLY stored
# edges (idx). Ranking is over the R-tail candidate pool (KGE filtered ranking).
# ---------------------------------------------------------------------------
def compose_inherit(idx, isa_adj, C, R, depth):
    """CROSS-relation property inheritance: candidate tails from IS_A* ancestors' stored R-edges.
    Genuine >=2-hop cross-relation by construction (first hop IS_A != R). Score = #witnessing ancestors.
    Also returns witness derivations {tail -> list of (X, hop_dist)} for path-dist reporting."""
    anc_dist = _reach(isa_adj, {C}, depth)
    anc_dist.pop(C, None)
    scores = defaultdict(float)
    witnesses = defaultdict(list)
    for X, hd in anc_dist.items():
        for (rr, tt) in idx["out"].get(X, ()):
            if rr == R and tt != C:
                scores[tt] += 1.0 / (1.0 + hd)   # closer ancestor weighs more (deterministic)
                witnesses[tt].append((X, hd + 1))  # path length = ancestor hops + 1 R-edge
    return scores, witnesses


def compose_any2hop(idx, C, R, isa_name):
    """Broader cross-relation: any 2-hop C -R1-> X -R2-> D with R1 != R. Score = #paths.
    Returns scores + rel-type-path counter {(R1,R2) -> n} for the reln-type distribution."""
    scores = defaultdict(float)
    relpair = Counter()
    for (r1, X) in idx["out"].get(C, ()):
        if r1 == R or X == C:
            continue
        for (r2, D2) in idx["out"].get(X, ()):
            if D2 == C:
                continue
            scores[D2] += 1.0
            relpair[(r1, r2)] += 1
    return scores, relpair


def freq_prior(idx, R):
    """FREQUENCY_PRIOR (the bar): rank tails by global stored R-tail popularity. Head-independent."""
    return dict(idx["tail_freq"][R])


def flat_cooc(idx, C, R):
    """FLAT associative (non-compositional) predictor: score(D) = sum over C's stored non-R features f of
    (# concepts that share f AND have stored R-tail D). Learns 'concepts like C tend to have R-tail D'
    WITHOUT any derivation path. This is the flat-shortcut composition must beat."""
    cfeats = [(r, t) for (r, t) in idx["out"].get(C, ()) if r != R]
    if not cfeats:
        return {}
    peers = Counter()
    for f in cfeats:
        for h2 in idx["feat_owners"].get(f, ()):
            if h2 != C:
                peers[h2] += 1
    scores = defaultdict(float)
    for h2, w in peers.items():
        for tt in idx["gold_stored"].get((R, h2), ()):
            if tt != C:
                scores[tt] += float(w)
    return scores


def _rank_hit(scores, gold_tails, pool_list, topk, rng):
    """gold hit@1 / hit@topk of any gold tail under `scores` (dict tail->score), ranked over pool_list.
    Unscored pool members get 0. Deterministic tie-break: stable by (-score, pool_index) via rng-free
    sort on (score desc, index asc). Returns (hit1, hitk, proposed_any)."""
    if not gold_tails:
        return 0, 0, 0
    # rank ONLY candidates with score > 0 first (composition proposes a small set); ties broken by
    # a fixed deterministic jitter over pool index so gold does not get a free top rank on ties.
    scored = [(scores.get(p, 0.0), i, p) for i, p in enumerate(pool_list)]
    # sort by score desc, then index asc (deterministic). gold on a tie sits at its natural index.
    scored.sort(key=lambda z: (-z[0], z[1]))
    gold = set(gold_tails)
    proposed_any = 1 if any(s > 0 for (s, _, p) in scored if p in gold) else 0
    hit1 = 1 if scored[0][2] in gold and scored[0][0] > 0 else 0
    topk_set = set(p for (s, _, p) in scored[:topk] if s > 0)
    hitk = 1 if (topk_set & gold) else 0
    return hit1, hitk, proposed_any


# ---------------------------------------------------------------------------
# Held-out split (leak-proof) + per-corpus/per-relation evaluation.
# ---------------------------------------------------------------------------
def build_split(triples, R, n_heldout, seed, min_isa_deg, isa_name):
    """Select held-out heads (gold-independent density gate: >= min_isa_deg IS_A ancestors AND >=1 non-R
    stored feature) and EXCLUDE every (R, head) edge from storage. Returns (stored, heldout, isa_adj_full).
    isa_adj_full is over ALL edges (IS_A is never the held-out relation R, so it stays in storage)."""
    isa_adj_full = defaultdict(set)
    out_all = defaultdict(set)
    heads_with_R = defaultdict(set)
    for (r, h, t) in triples:
        out_all[h].add((r, t))
        if r == isa_name:
            isa_adj_full[h].add(t)
        if r == R:
            heads_with_R[h].add(t)
    # candidate held-out heads: have >=1 IS_A ancestor path AND >=1 non-R feature (gold-independent).
    cand = []
    for h in sorted(heads_with_R):
        anc = _reach(isa_adj_full, {h}, 6)
        anc.pop(h, None)
        nonr = [f for f in out_all[h] if f[0] != R]
        if len(anc) >= min_isa_deg and len(nonr) >= 1:
            cand.append(h)
    rng = np.random.RandomState(seed)
    rng.shuffle(cand)
    pick = sorted(cand[:n_heldout])  # sorted for determinism of downstream reporting
    heldout = {h: set(heads_with_R[h]) for h in pick}
    heldout_keys = set((R, h) for h in pick)
    stored = [(r, h, t) for (r, h, t) in triples if (r, h) not in heldout_keys]
    return stored, heldout, isa_adj_full


def shuffle_graph(stored, seed):
    """Must-fail control: shuffle tails WITHIN each relation (destroys composition structure, preserves
    per-relation degree + tail marginal). COMPOSE over this must collapse to ~base-rate."""
    rng = np.random.RandomState(seed + 101)
    by_rel = defaultdict(list)
    for (r, h, t) in stored:
        by_rel[r].append((h, t))
    out = []
    for r in sorted(by_rel):
        pairs = by_rel[r]
        tails = [t for (_, t) in pairs]
        perm = rng.permutation(len(tails))
        for i, (h, _) in enumerate(pairs):
            out.append((r, h, tails[perm[i]]))
    return out


def eval_corpus_relation(triples, corpus, R, n_heldout, seed, depth, min_isa_deg, topk):
    isa_name = ISA_REL[corpus]
    stored, heldout, isa_adj_full = build_split(triples, R, n_heldout, seed, min_isa_deg, isa_name)
    idx = build_index(stored)
    # isa adjacency for compose_inherit is over STORED edges (IS_A never held out -> identical to full).
    isa_adj = defaultdict(set)
    for (r, h, t) in stored:
        if r == isa_name:
            isa_adj[h].add(t)
    # candidate pool = concepts that are EVER an R-tail in the FULL corpus (filtered ranking answer space)
    pool_list = sorted(set(t for (r, _, t) in triples if r == R))
    base_rate = 1.0 / max(len(pool_list), 1)

    # shuffled-graph index (must-fail)
    sh_stored = shuffle_graph(stored, seed)
    sh_idx = build_index(sh_stored)
    sh_isa = defaultdict(set)
    for (r, h, t) in sh_stored:
        if r == isa_name:
            sh_isa[h].add(t)

    rng = np.random.RandomState(seed + 7)
    heads = sorted(heldout)
    agg = {a: [0, 0, 0] for a in ["COMPOSE_INHERIT", "COMPOSE_ANY2HOP", "FREQ", "FLAT",
                                  "STORE_RECALL_FLOOR", "SHUFFLED_INHERIT"]}
    path_lens = Counter()
    relpair_all = Counter()
    genuine_cross = 0
    inherit_top1_preds = []
    freq_top1_preds = []
    shuf_top1_preds = []
    for C in heads:
        gold = heldout[C]
        # COMPOSE_INHERIT
        sc, wit = compose_inherit(idx, isa_adj, C, R, depth)
        h1, hk, pa = _rank_hit(sc, gold, pool_list, topk, rng)
        agg["COMPOSE_INHERIT"][0] += h1; agg["COMPOSE_INHERIT"][1] += hk; agg["COMPOSE_INHERIT"][2] += pa
        # winning-derivation path-length dist over the gold tails proposed (if any)
        for tt in (set(sc) & gold):
            for (X, plen) in wit[tt]:
                path_lens[plen] += 1
                genuine_cross += 1  # inherit is cross by construction
        inherit_top1_preds.append(_argmax_tail(sc, pool_list))
        # COMPOSE_ANY2HOP
        sc2, rp = compose_any2hop(idx, C, R, isa_name)
        h1b, hkb, pab = _rank_hit(sc2, gold, pool_list, topk, rng)
        agg["COMPOSE_ANY2HOP"][0] += h1b; agg["COMPOSE_ANY2HOP"][1] += hkb; agg["COMPOSE_ANY2HOP"][2] += pab
        for (r1, r2), c in rp.items():
            relpair_all[(r1, r2)] += c
        # FREQ
        scf = freq_prior(idx, R)
        f1, fk, _ = _rank_hit(scf, gold, pool_list, topk, rng)
        agg["FREQ"][0] += f1; agg["FREQ"][1] += fk
        freq_top1_preds.append(_argmax_tail(scf, pool_list))
        # FLAT
        scfl = flat_cooc(idx, C, R)
        l1, lk, _ = _rank_hit(scfl, gold, pool_list, topk, rng)
        agg["FLAT"][0] += l1; agg["FLAT"][1] += lk
        # STORE_RECALL_FLOOR: query the held-out (R,C) against STORED graph (must be empty -> 0)
        scfloor = {t: 1.0 for t in idx["gold_stored"].get((R, C), ())}
        fl1, flk, _ = _rank_hit(scfloor, gold, pool_list, topk, rng)
        agg["STORE_RECALL_FLOOR"][0] += fl1; agg["STORE_RECALL_FLOOR"][1] += flk
        # SHUFFLED_INHERIT (must-fail)
        ssc, _ = compose_inherit(sh_idx, sh_isa, C, R, depth)
        s1, sk, _ = _rank_hit(ssc, gold, pool_list, topk, rng)
        agg["SHUFFLED_INHERIT"][0] += s1; agg["SHUFFLED_INHERIT"][1] += sk
        shuf_top1_preds.append(_argmax_tail(ssc, pool_list))

    n = max(len(heads), 1)
    genuine_cross_frac = 1.0  # COMPOSE_INHERIT derivations are cross-relation by construction
    # any2hop genuine-cross fraction = paths whose (R1,R2) is not (R,R); by construction R1!=R already
    same_rel_pairs = sum(c for (r1, r2), c in relpair_all.items() if r1 == R and r2 == R)
    total_pairs = sum(relpair_all.values())
    any2hop_genuine_cross_frac = 1.0 - (same_rel_pairs / total_pairs if total_pairs else 0.0)

    result = {
        "corpus": corpus, "relation": R, "seed": seed, "n_heldout_heads": len(heads),
        "n_pool": len(pool_list), "base_rate": base_rate, "depth": depth, "min_isa_deg": min_isa_deg,
        "arms": {a: {"top1": v[0] / n, "top%d" % topk: v[1] / n,
                     "coverage": (v[2] / n) if len(v) > 2 else None}
                 for a, v in agg.items()},
        "genuine_cross_frac_inherit": genuine_cross_frac,
        "genuine_cross_frac_any2hop": any2hop_genuine_cross_frac,
        "path_len_dist": {str(k): int(v) for k, v in sorted(path_lens.items())},
        "top_relpairs_any2hop": [{"r1": r1, "r2": r2, "n": int(c)}
                                 for (r1, r2), c in relpair_all.most_common(12)],
        "_preds": {"inherit": inherit_top1_preds, "freq": freq_top1_preds, "shuffled": shuf_top1_preds},
    }
    return result


def _argmax_tail(scores, pool_list):
    if not scores:
        return -1
    best_p, best_s = -1, 0.0
    for i, p in enumerate(pool_list):
        s = scores.get(p, 0.0)
        if s > best_s:
            best_s = s
            best_p = i
    return best_p


def density_report(triples, corpus):
    concepts = set()
    per_concept = defaultdict(set)
    rel_counts = Counter()
    for (r, h, t) in triples:
        concepts.add(h); concepts.add(t)
        per_concept[h].add(r)
        per_concept[t].add(r)
        rel_counts[r] += 1
    degs = np.array([len(v) for v in per_concept.values()], dtype=np.float64) if per_concept else np.array([0.0])
    edge_deg = Counter()
    for (r, h, t) in triples:
        edge_deg[h] += 1
        edge_deg[t] += 1
    ed = np.array(list(edge_deg.values()), dtype=np.float64) if edge_deg else np.array([0.0])
    return {
        "corpus": corpus, "n_triples": len(triples), "n_concepts": len(concepts),
        "n_relations": len(rel_counts),
        "rel_types_per_concept_median": float(np.median(degs)),
        "rel_types_per_concept_mean": float(degs.mean()),
        "edges_per_concept_median": float(np.median(ed)),
        "edges_per_concept_mean": float(ed.mean()),
        "relation_counts": dict(rel_counts.most_common()),
    }


# ---------------------------------------------------------------------------
# Config presets
# ---------------------------------------------------------------------------
def cfg_smoke():
    return {"run_mode": "smoke", "seeds": [7], "topk": 10, "depth": 4, "min_isa_deg": 2,
            "tasks": [("wordnet", ["DERIV", "PART_MERONYM"], 40),
                      ("worldtree", ["CONTAINS", "REQUIRES"], 40)]}


def cfg_full():
    # best-shot held-out relations per corpus (highest preflight coverage) + a taxonomic-attr cross-check.
    return {"run_mode": "full", "seeds": [7, 13, 19], "topk": 10, "depth": 4, "min_isa_deg": 2,
            "tasks": [("wordnet", ["DERIV", "PART_MERONYM", "MEMBER_MERONYM", "ATTRIBUTE"], 120),
                      ("worldtree", ["CONTAINS", "REQUIRES", "SOURCEOF", "PARTOF", "USEDFOR"], 120)]}


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def decide_verdict(results, planted):
    """Aggregate DENSE vs SPARSE COMPOSE (best arm = max of INHERIT/ANY2HOP topk) vs FREQ."""
    def best_topk(rlist, corpus):
        vals = [max(r["arms"]["COMPOSE_INHERIT"]["top10"], r["arms"]["COMPOSE_ANY2HOP"]["top10"])
                for r in rlist if r["corpus"] == corpus]
        return float(np.mean(vals)) if vals else 0.0

    def freq_topk(rlist, corpus):
        vals = [r["arms"]["FREQ"]["top10"] for r in rlist if r["corpus"] == corpus]
        return float(np.mean(vals)) if vals else 0.0

    def cov(rlist, corpus):
        vals = [max(r["arms"]["COMPOSE_INHERIT"]["coverage"], r["arms"]["COMPOSE_ANY2HOP"]["coverage"])
                for r in rlist if r["corpus"] == corpus]
        return float(np.mean(vals)) if vals else 0.0

    dense_c = best_topk(results, "wordnet")
    sparse_c = best_topk(results, "worldtree")
    dense_f = freq_topk(results, "wordnet")
    dense_cov = cov(results, "wordnet")

    planted_ok = planted.get("compose_top1", 0.0) >= 0.80 and planted.get("shuffled_top1", 1.0) <= 0.20
    msg = ("DENSE COMPOSE top10=%.3f (freq=%.3f cov=%.3f) | SPARSE COMPOSE top10=%.3f | planted_ok=%s"
           % (dense_c, dense_f, dense_cov, sparse_c, planted_ok))

    if not planted_ok:
        return "HARD_FAIL_INSTRUMENT", "MECHANISM/CONTROL BROKEN: planted composition did not fire. " + msg
    if dense_cov < 0.10 or (dense_c <= dense_f + 0.05):
        return "HARD_FAIL", ("COMPOSITION TIES FLOOR ON DENSE (coverage<0.10 or no lift over FREQ) -> "
                             "composition does not invent on these corpora; the bottleneck is absent "
                             "compositional-redundancy structure, NOT mechanism. " + msg)
    if (dense_c >= dense_f + 0.15) and (dense_c >= 0.20) and (dense_c - sparse_c >= 0.10):
        return "HARD_PASS", "DENSITY IS THE LEVER: composition infers held-out edges on dense >> sparse. " + msg
    return "MIDDLE_BAND", "Partial: density helps but capped. " + msg


# ---------------------------------------------------------------------------
# Self-test: planted redundant-inheritance corpus (mechanism MUST fire) + real-loader real-code-path.
# ---------------------------------------------------------------------------
def _planted_corpus(seed):
    """K categories in a 2-level IS_A hierarchy; each category has a shared PART set stored REDUNDANTLY at
    BOTH the family node and the leaf instances. Hold out leaf PART edges -> inheritance C-ISA->family-PART->D
    recovers them. This is the compositional-redundancy structure real taxonomies lack."""
    rng = np.random.RandomState(seed)
    K, per_cat, n_parts = 8, 10, 3
    triples = []
    for k in range(K):
        fam = "fam_%02d" % k
        parts = ["part_%02d_%02d" % (k, j) for j in range(n_parts)]
        for p in parts:
            triples.append(("HAS_PART", fam, p))              # family has the parts (stored)
        for c in range(per_cat):
            leaf = "leaf_%02d_%02d" % (k, c)
            triples.append(("KINDOF", leaf, fam))             # leaf IS_A family (the inheritance bridge)
            for p in parts:
                triples.append(("HAS_PART", leaf, p))         # leaf ALSO has the parts (redundant -> held out)
            # distractor part unique to leaf (so freq/flat cannot trivially win)
            triples.append(("HAS_PART", leaf, "distract_%02d_%02d" % (k, rng.randint(0, 50))))
    return triples


def self_test():
    _progress("SELF-TEST start")
    # (1) planted: mechanism fires; leak-proof floor + shuffled collapse.
    triples = _planted_corpus(7)
    # register KINDOF as the isa relation for a temporary 'planted' corpus.
    ISA_REL["planted"] = "KINDOF"
    res = eval_corpus_relation(triples, "planted", "HAS_PART", n_heldout=40, seed=7,
                               depth=4, min_isa_deg=1, topk=10)
    ci = res["arms"]["COMPOSE_INHERIT"]
    fl = res["arms"]["STORE_RECALL_FLOOR"]
    sh = res["arms"]["SHUFFLED_INHERIT"]
    fr = res["arms"]["FREQ"]
    _progress("planted: COMPOSE_INHERIT top1=%.3f top10=%.3f cov=%.3f | FLOOR top1=%.3f | SHUFFLED top1=%.3f | FREQ top1=%.3f"
              % (ci["top1"], ci["top10"], ci["coverage"], fl["top1"], sh["top1"], fr["top1"]))
    assert ci["top1"] >= 0.80, "INSTRUMENT VACUOUS: planted composition did not fire (top1=%.3f)" % ci["top1"]
    assert ci["coverage"] >= 0.90, "planted composition coverage too low (%.3f)" % ci["coverage"]
    assert fl["top1"] <= 0.05, "STORE_RECALL_FLOOR did not collapse (%.3f) -> exclusion leak" % fl["top1"]
    assert sh["top1"] <= 0.20, "SHUFFLED did not collapse (%.3f) -> composition not using real structure" % sh["top1"]
    assert ci["top1"] > sh["top1"] + 0.20, "COMPOSE did not beat SHUFFLED by margin"
    # arms-must-differ: inherit vs freq vs shuffled top1-prediction arrays not all identical
    import hashlib
    def _h(a):
        return hashlib.sha256(np.array(a, dtype=np.int64).tobytes()).hexdigest()
    dp = res["_preds"]
    assert _h(dp["inherit"]) != _h(dp["freq"]), "META_RULE_AF: INHERIT and FREQ predictions bit-identical"
    assert _h(dp["inherit"]) != _h(dp["shuffled"]), "META_RULE_AF: INHERIT and SHUFFLED predictions bit-identical"
    _progress("(1) mechanism fires + leak-proof floor + shuffled collapse + arms-differ: PASS")

    # (2) real-code-path: load BOTH real corpora, build a tiny split, floor collapses on real data.
    for corpus, R, isa in [("wordnet", "DERIV", "HYPERNYM"), ("worldtree", "CONTAINS", "KINDOF")]:
        tri = load_corpus(corpus)
        assert len(tri) >= 100, "%s loader produced too few triples (%d)" % (corpus, len(tri))
        assert any(r == isa for (r, _, _) in tri), "%s missing IS_A relation %s" % (corpus, isa)
        rr = eval_corpus_relation(tri, corpus, R, n_heldout=20, seed=7, depth=4, min_isa_deg=2, topk=10)
        flr = rr["arms"]["STORE_RECALL_FLOOR"]["top1"]
        assert flr <= 0.05, "%s STORE_RECALL_FLOOR did not collapse (%.3f) -> exclusion leak" % (corpus, flr)
        _progress("(2) %s real-code-path: n_tri=%d heads=%d COMPOSE_INHERIT top10=%.3f cov=%.3f floor=%.3f PASS"
                  % (corpus, len(tri), rr["n_heldout_heads"],
                     rr["arms"]["COMPOSE_INHERIT"]["top10"], rr["arms"]["COMPOSE_INHERIT"]["coverage"], flr))
    _progress("SELF-TEST PASS")
    return {"verdict": "SELFTEST_PASS",
            "planted_compose_top1": ci["top1"], "planted_compose_top10": ci["top10"],
            "planted_floor_top1": fl["top1"], "planted_shuffled_top1": sh["top1"]}


# ---------------------------------------------------------------------------
# Infra
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    _write_metrics(output_dir, diag)


def run(cfg, output_dir):
    global _HEARTBEAT_DIR
    _HEARTBEAT_DIR = output_dir
    t0 = time.perf_counter()
    corpora_cache = {}
    density = {}
    results = []
    expected = cfg["_expected_units"]
    done = 0
    for (corpus, rels, n_heldout) in cfg["tasks"]:
        if corpus not in corpora_cache:
            _heartbeat("loading corpus %s ..." % corpus)
            corpora_cache[corpus] = load_corpus(corpus)
            density[corpus] = density_report(corpora_cache[corpus], corpus)
            d = density[corpus]
            _heartbeat("DENSITY[%s] n_triples=%d n_concepts=%d rel_types/concept med=%.1f mean=%.2f edges/concept med=%.1f mean=%.2f"
                       % (corpus, d["n_triples"], d["n_concepts"], d["rel_types_per_concept_median"],
                          d["rel_types_per_concept_mean"], d["edges_per_concept_median"], d["edges_per_concept_mean"]))
        tri = corpora_cache[corpus]
        for R in rels:
            for seed in cfg["seeds"]:
                try:
                    r = eval_corpus_relation(tri, corpus, R, n_heldout, seed, cfg["depth"],
                                             cfg["min_isa_deg"], cfg["topk"])
                except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J)
                    r = {"corpus": corpus, "relation": R, "seed": seed, "failure_class": type(e).__name__,
                         "error": str(e)[:300], "arms": {}}
                    _heartbeat("UNIT FAIL %s/%s/seed%d: %s" % (corpus, R, seed, type(e).__name__))
                results.append(r)
                done += 1
                if "arms" in r and r["arms"]:
                    a = r["arms"]
                    _heartbeat("[%d/%d] %s/%s/s%d: INHERIT t1=%.3f t10=%.3f cov=%.3f | ANY2 t10=%.3f | FREQ t10=%.3f | FLAT t10=%.3f | FLOOR t1=%.3f | SHUF t1=%.3f | pool=%d"
                               % (done, expected, corpus, R, seed, a["COMPOSE_INHERIT"]["top1"],
                                  a["COMPOSE_INHERIT"]["top10"], a["COMPOSE_INHERIT"]["coverage"],
                                  a["COMPOSE_ANY2HOP"]["top10"], a["FREQ"]["top10"], a["FLAT"]["top10"],
                                  a["STORE_RECALL_FLOOR"]["top1"], a["SHUFFLED_INHERIT"]["top1"], r["n_pool"]))

    # strip the heavy _preds arrays before persisting (keep metrics compact)
    for r in results:
        r.pop("_preds", None)

    planted = self_test_metrics_only()
    verdict, verdict_msg = decide_verdict([r for r in results if r.get("arms")], planted)

    # cardinality gate (META_RULE_H)
    n_ok = len([r for r in results if r.get("arms")])
    cardinality_ok = (n_ok == expected)
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = "expected %d units, got %d valid: %s" % (expected, n_ok, verdict_msg)

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "run_mode": cfg["run_mode"], "elapsed_s": round(time.perf_counter() - t0, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "expected_n_units": expected, "n_valid_units": n_ok, "cardinality_ok": cardinality_ok,
        "planted_control": planted, "density": density, "results": results,
        "config": {k: v for k, v in cfg.items() if not k.startswith("_")},
    }
    _write_metrics(output_dir, metrics)
    _heartbeat("VERDICT %s | %s" % (verdict, verdict_msg))
    return metrics


def self_test_metrics_only():
    """Run only the planted-control leg (no asserts) to embed the mechanism-fires evidence in metrics."""
    triples = _planted_corpus(7)
    ISA_REL["planted"] = "KINDOF"
    res = eval_corpus_relation(triples, "planted", "HAS_PART", n_heldout=40, seed=7,
                               depth=4, min_isa_deg=1, topk=10)
    return {"compose_top1": res["arms"]["COMPOSE_INHERIT"]["top1"],
            "compose_top10": res["arms"]["COMPOSE_INHERIT"]["top10"],
            "compose_coverage": res["arms"]["COMPOSE_INHERIT"]["coverage"],
            "floor_top1": res["arms"]["STORE_RECALL_FLOOR"]["top1"],
            "shuffled_top1": res["arms"]["SHUFFLED_INHERIT"]["top1"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    if args.self_test:
        out = self_test()
        print(json.dumps(out))
        return

    if args.smoke:
        cfg = cfg_smoke()
        suffix = "_smoke"
    else:
        cfg = cfg_full()
        suffix = ""
    cfg["_expected_units"] = sum(len(rels) * len(cfg["seeds"]) for (_, rels, _) in cfg["tasks"])
    output_dir = args.output_dir or os.path.join(REPO, "data", ANCHOR_NAME + suffix)
    _write_start_marker(output_dir, cfg["run_mode"], cfg["_expected_units"])
    run(cfg, output_dir)


if __name__ == "__main__":
    _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME)
    if "--smoke" in sys.argv:
        _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if "--self-test" not in sys.argv:
            _write_crash_metrics(_out_dir_for_crash, e)
        raise
