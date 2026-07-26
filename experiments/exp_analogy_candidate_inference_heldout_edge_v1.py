"""exp_analogy_candidate_inference_heldout_edge_v1

Brain-true structure-mapping analogy (Gentner/SME; LISA) candidate-inference: predict a relational
edge that was NEVER stored -- excluded from train_facts, from associative memory M, and from every
bind/store call -- from a structurally-similar KNOWN base concept, on real WorldTree typed relations.

Fixes the store-then-recall confound in 29578/29579 (exp_grounding_tem_factorized_heldout_concept_v1),
whose held-out fact was still written into M at test time (code-confirmed lines 609-611), making
"generalization" actually lookup (RANDOM_G tied FACTORIZED_G, gap=0.0008).

Design-of-record: notes/research_learned_inference_generalization_analogy_metalearning_2026-07-26.md
Pre-reg: preregs/2026-07-26_exp_analogy_candidate_inference_heldout_edge_v1.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-query top-1 prediction hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: prediction-accuracy discriminator; base_rate=1/n_dict + FREQUENCY_PRIOR reported as floors
# - baseline_in_band: EXEMPT (STORE_RECALL_FLOOR/FLAT/FREQUENCY_PRIOR are intended-floor baselines)
# - discriminator survives scale (planted self-test: ANALOGY >> FREQUENCY_PRIOR/RANDOM_ALIGNMENT)
# - HARD_PASS strictly above floor + margin (10x base-rate or 15pp, per design-of-record)
# - HP_SCOPE per-arm declaration (ANALOGY only)
# - cardinality_ok: EXPECTED_N_UNITS gate
# - per-unit failure-class instrumentation (no bare except)
# - all numbers tagged in the design note/prereg
# - deterministic seeding (fixed ints, np.random.RandomState(seed+offset), sorted(set()); NO hash())

REUSE (verbatim, via importlib exec of the exact reference module -- no reinvention, no copy drift):
- load_worldtree_triples / TABLE_SLOTS  (WorldTree typed-triple loader; same 17-relation subset)
- build_random_content / random_g_table / make_unitary / bind_batch / unbind_batch / _l2norm
- build_memory / retrieve_tail_vec / cleanup           (STORE_RECALL_FLOOR arm ONLY)
- train_flat / FlatMLP / flat_predict                  (FLAT-MLP baseline)
Analogy alignment + candidate-inference + the 3 must-fail controls are NEW code (this cell).

ASCII-only. No emojis. No em dashes in output.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

from hdlab.binding import bind as ref_bind, unbind as ref_unbind

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR_NAME = "exp_analogy_candidate_inference_heldout_edge_v1"

# ---------------------------------------------------------------------------
# Verbatim reuse: exec the exact reference module and pull its functions.
# ---------------------------------------------------------------------------
_REF_PATH = os.path.join(REPO, "experiments", "exp_grounding_tem_factorized_heldout_concept_v1.py")
_spec = importlib.util.spec_from_file_location("_tem_ref_v1", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)  # top-level only defines functions; main is __main__-guarded

load_worldtree_triples = _ref.load_worldtree_triples
TABLE_SLOTS = _ref.TABLE_SLOTS
build_random_content = _ref.build_random_content
random_g_table = _ref.random_g_table
make_unitary = _ref.make_unitary
bind_batch = _ref.bind_batch
unbind_batch = _ref.unbind_batch
_l2norm = _ref._l2norm
build_memory = _ref.build_memory
retrieve_tail_vec = _ref.retrieve_tail_vec
cleanup = _ref.cleanup
train_flat = _ref.train_flat
flat_predict = _ref.flat_predict


def _progress(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# Exclusion-enforced split: hold out ALL (a, R, *) edges for selected heads.
# ---------------------------------------------------------------------------

def build_analogy_split(triples, seed, heldout_rels, n_heldout_per_rel):
    """Return the exclusion-enforced split.

    For each relation R in heldout_rels, select up to n_heldout_per_rel HEADS that (i) are the head of
    >=1 R-edge and (ii) have >=1 edge (either slot) under a relation != R (so analogy has structure to
    align on). Remove ALL (a,R,*) edges of every selected head from stored_fac. gold[R][a] = set of
    a's true R-tails. stored_fac never contains any held-out head's R-edge (the fix).
    """
    rng = np.random.RandomState(seed)
    concepts = sorted(set([t[1] for t in triples] + [t[2] for t in triples]))
    cidx = {c: i for i, c in enumerate(concepts)}
    rel_names = sorted(set(t[0] for t in triples))
    ridx = {r: i for i, r in enumerate(rel_names)}
    fac = [(ridx[r], cidx[a], cidx[b]) for (r, a, b) in triples]

    # per-concept relation participation (either slot) -> alignability check
    rels_of_concept = defaultdict(set)
    for (r, a, b) in fac:
        rels_of_concept[a].add(r)
        rels_of_concept[b].add(r)

    # heads of each relation, and their tail sets
    heads_of_rel = defaultdict(lambda: defaultdict(set))  # R -> head -> set(tails)
    for (r, a, b) in fac:
        heads_of_rel[r][a].add(b)

    heldout = {}          # R_idx -> {head_idx: set(gold_tail_idx)}
    heldout_pairs = set()  # (R_idx, head_idx) removed from storage
    for rname in heldout_rels:
        if rname not in ridx:
            continue
        R = ridx[rname]
        cand = [a for a in heads_of_rel[R]
                if len(rels_of_concept[a] - {R}) >= 1]  # has non-R structure to align on
        cand = sorted(cand)                              # deterministic base order
        rng.shuffle(cand)
        pick = cand[:n_heldout_per_rel]
        heldout[R] = {a: set(heads_of_rel[R][a]) for a in pick}
        for a in pick:
            heldout_pairs.add((R, a))

    stored_fac = [f for f in fac if (f[0], f[1]) not in heldout_pairs]

    return {
        "concepts": concepts, "cidx": cidx, "rel_names": rel_names, "ridx": ridx,
        "fac": fac, "stored_fac": stored_fac,
        "heldout": heldout, "heldout_pairs": heldout_pairs,
        "n_dict": len(concepts),
    }


# ---------------------------------------------------------------------------
# Relational profiles (sparse (rel, slot, neighbor) features; random-ID; IDF-weighted).
# ---------------------------------------------------------------------------

def build_profiles(stored_fac, n_dict, use_idf=True, role_weight=0.5):
    """Per-concept sparse relational profile with TWO Gentner-faithful feature kinds, both keyed with
    the relation at index 0 so leak-proof exclusion (drop relation R) is a single f[0]==R test.

    (1) PARALLEL-CONNECTIVITY (strong): (r, slot, neighbor_idx) -- shared exact relational PARTNER.
        Concept a (head of (r,a,b)) owns (r,0,b); tail b owns (r,1,a). Weighted by count.
    (2) RELATIONAL-SIGNATURE (dense fallback): (r, slot, None) -- participates in relation r as slot s
        (partner-agnostic structural fingerprint). Presence-weighted by role_weight. This is the
        densifier: exact-partner overlap fires on <30% of WorldTree heads (measured), starving the
        mechanism; role-signature lets structurally-similar concepts align even without an identical
        partner. Still purely relational + content-agnostic (no borrowed embedding).

    IDF (over both kinds) down-weights high-frequency features (relation-skew guard, per design note).
    Returns feats: concept -> {feature: base_weight}, and idf: feature -> idf_weight.
    """
    feats = defaultdict(lambda: defaultdict(float))
    seen = defaultdict(set)   # feature -> set(concepts) for document frequency
    role_seen = defaultdict(set)  # (concept) -> set of role-features already credited (presence)
    for (r, a, b) in stored_fac:
        fa = (r, 0, b)
        fb = (r, 1, a)
        feats[a][fa] += 1.0
        feats[b][fb] += 1.0
        seen[fa].add(a)
        seen[fb].add(b)
        ra = (r, 0, None)
        rb = (r, 1, None)
        if ra not in role_seen[a]:
            feats[a][ra] += role_weight
            role_seen[a].add(ra)
            seen[ra].add(a)
        if rb not in role_seen[b]:
            feats[b][rb] += role_weight
            role_seen[b].add(rb)
            seen[rb].add(b)
    idf = {}
    for f, cs in seen.items():
        d = len(cs)
        idf[f] = float(np.log((n_dict + 1.0) / (d + 1.0)) + 1.0) if use_idf else 1.0
    return feats, idf


def _vec_excl_R(feats_c, idf, R):
    """Weighted feature dict for one concept, EXCLUDING all features of relation-type R (leak-proof)."""
    out = {}
    for f, w in feats_c.items():
        if f[0] == R:
            continue
        out[f] = w * idf.get(f, 1.0)
    return out


def align_scores(query_head, feats, idf, R, norms, inv):
    """Cosine alignment sim(query_head, E) for all E sharing a non-R feature. Returns {E: cos}."""
    va = _vec_excl_R(feats[query_head], idf, R)
    na = norms.get(query_head, 0.0)
    if na == 0.0 or not va:
        return {}
    acc = defaultdict(float)
    for f, val in va.items():
        for (E, vale) in inv.get(f, ()):
            if E == query_head:
                continue
            acc[E] += val * vale
    out = {}
    for E, dot in acc.items():
        ne = norms.get(E, 0.0)
        if ne > 0.0:
            out[E] = dot / (na * ne)
    return out


def _build_align_index(feats, idf, R, concepts_universe):
    """Norms (over non-R features) + inverted index (feature -> [(concept, weightedval)])."""
    norms = {}
    inv = defaultdict(list)
    for c in concepts_universe:
        v = _vec_excl_R(feats[c], idf, R)
        if not v:
            norms[c] = 0.0
            continue
        s = 0.0
        for f, val in v.items():
            s += val * val
            inv[f].append((c, val))
        norms[c] = float(np.sqrt(s))
    return norms, inv


def analogy_predict(heldout_R, feats, idf, R, r_tails_of, base_pool, n_dict, topk,
                    topk_align, mode, rng):
    """Candidate-inference predictions for every held-out head under relation R.

    mode: 'analogy'  -- real cosine alignment, real E->D projection.
          'random'   -- RANDOM_ALIGNMENT: random similarity score (necessity control).
          'shuffled' -- SHUFFLED_PROFILE: profiles reassigned to wrong concept identities.
          'scrambled'-- SCRAMBLED_ANALOGY_SOURCE: real alignment, E->D projection permuted.
    Returns list of top-k prediction lists (one per head), aligned to sorted(heldout_R).
    """
    heads = sorted(heldout_R.keys())
    universe = sorted(base_pool)  # only concepts that HAVE a stored R-edge can be projected from

    # r_tails_of maps E -> set(D) (real). For 'scrambled', permute the D assignment across R-edges.
    proj = r_tails_of
    if mode == "scrambled":
        edges = [(E, D) for E in r_tails_of for D in r_tails_of[E]]
        Ds = [D for (_, D) in edges]
        perm = np.arange(len(Ds))
        rng.shuffle(perm)
        proj = defaultdict(set)
        for i, (E, _) in enumerate(edges):
            proj[E].add(Ds[perm[i]])

    # For 'shuffled', reassign which concept owns which profile (identity <-> profile permutation).
    feats_use = feats
    if mode == "shuffled":
        all_c = sorted(feats.keys())
        permc = np.array(all_c)
        rng.shuffle(permc)
        remap = {all_c[i]: int(permc[i]) for i in range(len(all_c))}
        feats_use = {c: feats[remap[c]] for c in all_c}

    if mode in ("analogy", "shuffled", "scrambled"):
        norms, inv = _build_align_index(feats_use, idf, R, sorted(set(universe) | set(heads)))

    preds = []
    for a in heads:
        if mode == "random":
            sims = {E: float(rng.random()) for E in universe if E != a}
        else:
            sims = align_scores(a, feats_use, idf, R, norms, inv)
            sims = {E: s for E, s in sims.items() if E in base_pool and E != a}
        if not sims:
            preds.append([])
            continue
        top_E = sorted(sims.items(), key=lambda kv: kv[1], reverse=True)[:topk_align]
        cand = defaultdict(float)
        for E, s in top_E:
            for D in proj.get(E, ()):  # candidate inference: project base's R-tail onto query
                if s > cand[D]:
                    cand[D] = s
        ranked = sorted(cand.items(), key=lambda kv: kv[1], reverse=True)[:topk]
        preds.append([int(D) for (D, _) in ranked])
    return preds


def frequency_prior_predict(heldout_R, r_tail_counts, topk):
    """FREQUENCY_PRIOR: predict the globally most-frequent R-tails (relation-skew confound baseline)."""
    ranked = [D for (D, _) in sorted(r_tail_counts.items(), key=lambda kv: kv[1], reverse=True)[:topk]]
    return [list(ranked) for _ in sorted(heldout_R.keys())]


# ---------------------------------------------------------------------------
# Set-based top-k accuracy (gold is a SET of the head's true R-tails).
# ---------------------------------------------------------------------------

def set_topk_acc(preds, gold_sets, k):
    if not gold_sets:
        return 0.0
    hit = 0
    for i, gs in enumerate(gold_sets):
        row = preds[i][:k] if i < len(preds) else []
        if gs and any(int(d) in gs for d in row):
            hit += 1
    return hit / len(gold_sets)


# ---------------------------------------------------------------------------
# Store-recall FLOOR + FLAT arms on the exclusion-enforced split.
# ---------------------------------------------------------------------------

def eval_store_recall_floor(S, N, gen, topk):
    """Bind/unbind/cleanup over M built from stored_fac (held-out R-edges truly absent). MUST collapse."""
    concepts = S["concepts"]
    R = len(S["rel_names"])
    X = build_random_content(concepts, N, gen)
    G = random_g_table(R, N, gen)
    M = build_memory(S["stored_fac"], G, X)  # bundled Hebbian memory over STORED facts only
    q_r, q_a, gold_sets = [], [], []
    for Rr in sorted(S["heldout"].keys()):
        for a in sorted(S["heldout"][Rr].keys()):
            q_r.append(Rr)
            q_a.append(a)
            gold_sets.append(set(int(t) for t in S["heldout"][Rr][a]))
    if not q_a:
        return {"top1": 0.0, "top10": 0.0, "n": 0}, []
    qr = torch.tensor(q_r, dtype=torch.long)
    qav = X[torch.tensor(q_a, dtype=torch.long)]
    pred_idx = cleanup(retrieve_tail_vec(qr, qav, G, M), X, topk=topk)
    preds = [[int(x) for x in row if x >= 0] for row in pred_idx]
    return {"top1": set_topk_acc(preds, gold_sets, 1),
            "top10": set_topk_acc(preds, gold_sets, topk), "n": len(gold_sets)}, preds


def eval_flat(S, N, R, flat_steps, gen, topk):
    """FLAT-MLP trained on stored_fac, predicting held-out R-tails. PREDICTED ho_lift ~ 0."""
    concepts = S["concepts"]
    X = build_random_content(concepts, N, gen)
    mlp = train_flat(S["stored_fac"], X, R, flat_steps, gen)
    q, gold_sets = [], []
    for Rr in sorted(S["heldout"].keys()):
        for a in sorted(S["heldout"][Rr].keys()):
            gs = set(int(t) for t in S["heldout"][Rr][a])
            q.append((Rr, a, next(iter(gs))))  # tail arg ignored by flat_predict; gold via set
            gold_sets.append(gs)
    if not q:
        return {"top1": 0.0, "top10": 0.0, "n": 0}, []
    pred_idx = flat_predict(mlp, q, X, R, topk=topk)
    preds = [[int(x) for x in row if x >= 0] for row in pred_idx]
    return {"top1": set_topk_acc(preds, gold_sets, 1),
            "top10": set_topk_acc(preds, gold_sets, topk), "n": len(gold_sets)}, preds


# ---------------------------------------------------------------------------
# Analogy family evaluation (per relation, then pooled).
# ---------------------------------------------------------------------------

def eval_analogy_family(S, topk, topk_align, use_idf, seed, role_weight=0.5):
    """Run ANALOGY + FREQUENCY_PRIOR + 3 must-fail controls. Returns per-arm metrics + per-arm top-1
    prediction arrays (for ARMS-MUST-DIFFER) + out-degree diagnostic."""
    feats, idf = build_profiles(S["stored_fac"], S["n_dict"], use_idf=use_idf, role_weight=role_weight)

    # per relation: r_tails_of (E -> set(D)), tail counts, base pool
    r_tails = defaultdict(lambda: defaultdict(set))
    r_tail_counts = defaultdict(lambda: defaultdict(int))
    for (r, a, b) in S["stored_fac"]:
        r_tails[r][a].add(b)
        r_tail_counts[r][b] += 1

    arms = {m: {"preds": [], "gold": [], "top1_arr": []}
            for m in ["ANALOGY", "FREQUENCY_PRIOR",
                      "SCRAMBLED_ANALOGY_SOURCE", "SHUFFLED_PROFILE", "RANDOM_ALIGNMENT"]}
    outdeg_hits = []  # (nonR_outdeg, hit_top1) for ANALOGY only

    for Rr in sorted(S["heldout"].keys()):
        heldout_R = S["heldout"][Rr]
        heads = sorted(heldout_R.keys())
        gold_sets = [set(int(t) for t in heldout_R[a]) for a in heads]
        base_pool = set(r_tails[Rr].keys())

        rng_a = np.random.RandomState(seed + 101 + Rr)
        rng_s = np.random.RandomState(seed + 202 + Rr)
        rng_h = np.random.RandomState(seed + 303 + Rr)
        rng_r = np.random.RandomState(seed + 404 + Rr)

        p_an = analogy_predict(heldout_R, feats, idf, Rr, r_tails[Rr], base_pool,
                               S["n_dict"], topk, topk_align, "analogy", rng_a)
        p_sc = analogy_predict(heldout_R, feats, idf, Rr, r_tails[Rr], base_pool,
                               S["n_dict"], topk, topk_align, "scrambled", rng_s)
        p_sh = analogy_predict(heldout_R, feats, idf, Rr, r_tails[Rr], base_pool,
                               S["n_dict"], topk, topk_align, "shuffled", rng_h)
        p_rd = analogy_predict(heldout_R, feats, idf, Rr, r_tails[Rr], base_pool,
                               S["n_dict"], topk, topk_align, "random", rng_r)
        p_fp = frequency_prior_predict(heldout_R, r_tail_counts[Rr], topk)

        for name, p in [("ANALOGY", p_an), ("FREQUENCY_PRIOR", p_fp),
                        ("SCRAMBLED_ANALOGY_SOURCE", p_sc), ("SHUFFLED_PROFILE", p_sh),
                        ("RANDOM_ALIGNMENT", p_rd)]:
            arms[name]["preds"].extend(p)
            arms[name]["gold"].extend(gold_sets)
            for i, gs in enumerate(gold_sets):
                row = p[i][:1] if i < len(p) else []
                arms[name]["top1_arr"].append(1 if (gs and any(int(d) in gs for d in row)) else 0)

        # out-degree diagnostic (ANALOGY): non-R distinct features as structural richness proxy
        for i, a in enumerate(heads):
            deg = len(_vec_excl_R(feats[a], idf, Rr))
            hit = arms["ANALOGY"]["top1_arr"][-(len(heads) - i)]
            outdeg_hits.append((deg, hit))

    out = {}
    for name in arms:
        g = arms[name]["gold"]
        p = arms[name]["preds"]
        out[name] = {"top1": set_topk_acc(p, g, 1), "top10": set_topk_acc(p, g, topk), "n": len(g)}

    # out-degree vs accuracy relationship (pearson corr of deg vs hit) + tercile accuracies
    outdeg_corr = 0.0
    outdeg_bins = {}
    if len(outdeg_hits) >= 4:
        degs = np.array([d for (d, _) in outdeg_hits], dtype=np.float64)
        hits = np.array([h for (_, h) in outdeg_hits], dtype=np.float64)
        if degs.std() > 1e-9 and hits.std() > 1e-9:
            outdeg_corr = float(np.corrcoef(degs, hits)[0, 1])
        order = np.argsort(degs)
        thirds = np.array_split(order, 3)
        for bi, idxs in enumerate(thirds):
            if len(idxs):
                outdeg_bins["tercile_%d" % bi] = {
                    "deg_mean": float(degs[idxs].mean()),
                    "acc_top1": float(hits[idxs].mean()), "n": int(len(idxs))}

    top1_arrays = {name: np.array(arms[name]["top1_arr"], dtype=np.int64) for name in arms}
    pred_lists = {name: [list(map(int, r)) for r in arms[name]["preds"]] for name in arms}
    return out, top1_arrays, pred_lists, {"outdeg_corr": outdeg_corr, "outdeg_bins": outdeg_bins,
                                          "n_queries": len(outdeg_hits)}


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF) on per-query top-1 prediction arrays.
# ---------------------------------------------------------------------------

def arms_must_differ(pred_lists, floor_preds, flat_preds):
    """Hash the ACTUAL per-query prediction lists (not 0/1 hit arrays -- multiple arms genuinely
    scoring 0 have identical hit-arrays but distinct predictions; hashing hits gave a false AF trip).
    Only a collision INVOLVING the ANALOGY mechanism arm gates HARD_FAIL (duplicate-mechanism bug);
    control-vs-control coincidental collisions are logged, not gated."""
    digests = {}
    for name, preds in pred_lists.items():
        digests[name] = hashlib.sha256(json.dumps(preds).encode("utf-8")).hexdigest()
    digests["STORE_RECALL_FLOOR"] = hashlib.sha256(
        json.dumps(floor_preds).encode("utf-8")).hexdigest()
    digests["FLAT"] = hashlib.sha256(json.dumps(flat_preds).encode("utf-8")).hexdigest()
    names = sorted(digests)
    collisions = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if digests[names[i]] == digests[names[j]]:
                collisions.append((names[i], names[j]))
    return digests, collisions


# ---------------------------------------------------------------------------
# Core run
# ---------------------------------------------------------------------------

def run_experiment(cfg, output_dir):
    t0 = time.perf_counter()
    N = cfg["N"]
    seeds = cfg["seeds"]
    topk = cfg["topk"]
    topk_align = cfg["topk_align"]
    use_idf = cfg["use_idf"]

    _progress("loading WorldTree triples ...")
    triples, rel_names = load_worldtree_triples(cfg["rel_types"], cfg["max_rows_per_rel"])
    _progress("loaded %d triples across %d relation types" % (len(triples), len(rel_names)))
    if len(triples) < 20:
        raise ValueError("INSUFFICIENT_DATA: only %d triples parsed" % len(triples))

    arm_names = ["STORE_RECALL_FLOOR", "FLAT", "ANALOGY", "FREQUENCY_PRIOR",
                 "SCRAMBLED_ANALOGY_SOURCE", "SHUFFLED_PROFILE", "RANDOM_ALIGNMENT"]

    per_seed = []
    arm_digests_logged = None
    arm_collisions_logged = None
    for si, seed in enumerate(seeds):
        _progress("seed %d/%d (seed=%d)" % (si + 1, len(seeds), seed))
        gen = torch.Generator().manual_seed(seed)
        S = build_analogy_split(triples, seed, cfg["heldout_rels"], cfg["n_heldout_per_rel"])
        R = len(S["rel_names"])
        n_dict = S["n_dict"]
        base_rate = 1.0 / max(n_dict, 1)
        n_heldout = sum(len(S["heldout"][r]) for r in S["heldout"])
        _progress("  n_dict=%d R=%d n_heldout=%d n_stored=%d base_rate=%.5f"
                  % (n_dict, R, n_heldout, len(S["stored_fac"]), base_rate))
        if n_heldout < 4:
            raise ValueError("INSUFFICIENT_HELDOUT: only %d held-out heads" % n_heldout)

        # --- THE GATE FIRST: store-recall floor on the exclusion-enforced split ---
        floor, floor_preds = eval_store_recall_floor(S, N, gen, topk)
        _progress("  STORE_RECALL_FLOOR top1=%.5f top10=%.5f (base_rate=%.5f)"
                  % (floor["top1"], floor["top10"], base_rate))

        flat, flat_preds = eval_flat(S, N, R, cfg["flat_steps"], gen, topk)
        _progress("  FLAT top1=%.5f top10=%.5f" % (flat["top1"], flat["top10"]))

        an_out, top1_arrays, pred_lists, diag = eval_analogy_family(
            S, topk, topk_align, use_idf, seed, role_weight=cfg["role_weight"])
        _progress("  ANALOGY top1=%.5f top10=%.5f | FREQ_PRIOR top1=%.5f | "
                  "RANDOM_ALIGN top1=%.5f SCRAMBLED top1=%.5f SHUFFLED top1=%.5f | outdeg_corr=%.3f"
                  % (an_out["ANALOGY"]["top1"], an_out["ANALOGY"]["top10"],
                     an_out["FREQUENCY_PRIOR"]["top1"], an_out["RANDOM_ALIGNMENT"]["top1"],
                     an_out["SCRAMBLED_ANALOGY_SOURCE"]["top1"], an_out["SHUFFLED_PROFILE"]["top1"],
                     diag["outdeg_corr"]))

        arms = {"STORE_RECALL_FLOOR": floor, "FLAT": flat}
        arms.update(an_out)

        if arm_digests_logged is None:
            arm_digests_logged, arm_collisions_logged = arms_must_differ(
                pred_lists, floor_preds, flat_preds)

        per_seed.append({"seed": seed, "R": R, "n_dict": n_dict, "base_rate": base_rate,
                         "n_heldout": n_heldout, "n_stored": len(S["stored_fac"]),
                         "arms": arms, "outdeg_diag": diag})

    # ---------------- aggregate ----------------
    def agg(arm, key):
        vals = [ps["arms"][arm][key] for ps in per_seed if arm in ps["arms"]]
        return float(np.mean(vals)) if vals else 0.0

    summary = {a: {"top1": agg(a, "top1"), "top10": agg(a, "top10")} for a in arm_names}
    base_rate = float(np.mean([ps["base_rate"] for ps in per_seed]))
    outdeg_corr = float(np.mean([ps["outdeg_diag"]["outdeg_corr"] for ps in per_seed]))

    floor_top1 = summary["STORE_RECALL_FLOOR"]["top1"]
    flat_top1 = summary["FLAT"]["top1"]
    analogy_top1 = summary["ANALOGY"]["top1"]
    freq_top1 = summary["FREQUENCY_PRIOR"]["top1"]

    # collapse band for must-fail controls: within noise of FREQUENCY_PRIOR / base-rate floor
    collapse_band = max(freq_top1, 3.0 * base_rate) + 0.03
    control_names = ["SCRAMBLED_ANALOGY_SOURCE", "SHUFFLED_PROFILE", "RANDOM_ALIGNMENT"]
    controls = {c: {"top1": summary[c]["top1"],
                    "collapsed": summary[c]["top1"] <= collapse_band} for c in control_names}
    controls_collapse = all(controls[c]["collapsed"] for c in control_names)

    # store-recall floor MUST be near base-rate (leak detector). Elevated (~0.8) => exclusion leaked.
    floor_leak_band = max(20.0 * base_rate, 0.02)
    store_recall_collapsed = floor_top1 <= floor_leak_band

    def clears(x, ref):
        return (x - ref >= 0.15) or (x >= 10.0 * base_rate and ref <= 2.0 * base_rate)

    clears_floor_hp = clears(analogy_top1, floor_top1)
    clears_flat_hp = clears(analogy_top1, flat_top1)
    beats_freq_prior = (analogy_top1 - freq_top1) >= 0.05
    positive_outdeg = outdeg_corr > 0.0
    ties_floor_flat = (analogy_top1 - floor_top1 <= 0.05) and (analogy_top1 - flat_top1 <= 0.05)
    clears_floor_mb = (analogy_top1 - floor_top1 >= 0.05) and (analogy_top1 - flat_top1 >= 0.05)
    structure_genuine = beats_freq_prior and positive_outdeg

    # cardinality
    expected_units = len(seeds) * len(arm_names)
    actual_units = sum(len(ps["arms"]) for ps in per_seed)
    cardinality_ok = actual_units >= expected_units
    # AF gate: only a collision INVOLVING the ANALOGY mechanism arm is a duplicate-mechanism bug.
    # Control/baseline arms that genuinely collapse can coincide without being an implementation bug.
    arm_collisions_logged = arm_collisions_logged or []
    analogy_collision = [p for p in arm_collisions_logged if "ANALOGY" in p]
    arms_differ = (len(analogy_collision) == 0)

    # ---------------- verdict ----------------
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_BIT_IDENTICAL_META_RULE_AF"
    elif not store_recall_collapsed:
        verdict = "HARD_FAIL_STORE_RECALL_FLOOR_ELEVATED_EXCLUSION_LEAKED"
    elif not controls_collapse:
        verdict = "HARD_FAIL_MUSTFAIL_CONTROL_DID_NOT_COLLAPSE"
    elif ties_floor_flat:
        verdict = "HARD_FAIL_ANALOGY_TIES_FLOOR_AND_FLAT"
    elif clears_floor_hp and clears_flat_hp and structure_genuine:
        verdict = "HARD_PASS"
    elif clears_floor_mb and (not structure_genuine):
        verdict = "MIDDLE_BAND_ANALOGY_CLEARS_FLOOR_BUT_FREQ_OR_OUTDEG_CONFOUND"
    elif clears_floor_mb:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "ANALOGY top1=%.5f top10=%.5f | STORE_RECALL_FLOOR=%.5f (leak_band=%.4f collapsed=%s) | "
        "FLAT=%.5f | FREQ_PRIOR=%.5f (beats=%s) | controls[SCRAM=%.5f SHUF=%.5f RAND=%.5f] "
        "collapse_band=%.4f collapse=%s | clears_floor=%s clears_flat=%s outdeg_corr=%.3f "
        "structure_genuine=%s base_rate=%.5f n_heldout=%d"
        % (analogy_top1, summary["ANALOGY"]["top10"], floor_top1, floor_leak_band,
           store_recall_collapsed, flat_top1, freq_top1, beats_freq_prior,
           summary["SCRAMBLED_ANALOGY_SOURCE"]["top1"], summary["SHUFFLED_PROFILE"]["top1"],
           summary["RANDOM_ALIGNMENT"]["top1"], collapse_band, controls_collapse,
           clears_floor_hp, clears_flat_hp, outdeg_corr, structure_genuine, base_rate,
           int(np.sum([ps["n_heldout"] for ps in per_seed]))))

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": time.perf_counter() - t0,
        "run_mode": cfg["run_mode"],
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {k: v for k, v in cfg.items() if k != "seeds"},
        "seeds": seeds,
        "n_triples": len(triples),
        "n_rel_types_loaded": len(rel_names),
        "base_rate_floor": base_rate,
        "arm_summary": summary,
        "primary_metric": "analogy_top1 (held-out edge NEVER stored)",
        "store_recall_floor_top1": floor_top1,
        "store_recall_collapsed": store_recall_collapsed,
        "floor_leak_band": floor_leak_band,
        "flat_top1": flat_top1,
        "analogy_top1": analogy_top1,
        "frequency_prior_top1": freq_top1,
        "analogy_minus_floor": analogy_top1 - floor_top1,
        "analogy_minus_flat": analogy_top1 - flat_top1,
        "analogy_minus_freq_prior": analogy_top1 - freq_top1,
        "controls": controls,
        "collapse_band": collapse_band,
        "controls_collapse": controls_collapse,
        "clears_floor_hp": clears_floor_hp,
        "clears_flat_hp": clears_flat_hp,
        "beats_frequency_prior": beats_freq_prior,
        "outdeg_corr_mean": outdeg_corr,
        "positive_outdegree": positive_outdeg,
        "structure_genuine": structure_genuine,
        "cardinality_ok": cardinality_ok,
        "expected_units": expected_units,
        "actual_units": actual_units,
        "arms_differ_verified": arms_differ,
        "arm_digests": arm_digests_logged,
        "arm_collisions": arm_collisions_logged,
        "per_seed": per_seed,
    }
    return metrics


# ---------------------------------------------------------------------------
# Self-test: planted graph with structural twins -> ANALOGY >> FREQUENCY_PRIOR / RANDOM_ALIGNMENT,
# STORE_RECALL_FLOOR collapses, SHUFFLED_PROFILE collapses. Instrument-fires proof.
# ---------------------------------------------------------------------------

def self_test():
    _progress("SELF-TEST start")
    # (1) parity: batched bind/unbind == hdlab reference primitive.
    g = torch.Generator().manual_seed(1)
    a = _l2norm(torch.randn(3, 64, generator=g))
    b = _l2norm(torch.randn(3, 64, generator=g))
    cb = bind_batch(a, b)
    cref = torch.stack([ref_bind(a[i], b[i]) for i in range(3)])
    assert torch.allclose(cb, cref, atol=1e-4), "bind parity vs hdlab.binding FAILED"
    ub = unbind_batch(cb, b)
    uref = torch.stack([ref_unbind(cref[i], b[i]) for i in range(3)])
    assert torch.allclose(ub, uref, atol=1e-4), "unbind parity vs hdlab.binding FAILED"
    _progress("parity vs hdlab.binding: PASS")

    # (2) planted graph. K category-clusters. Concepts in a cluster share attribute-neighbors under
    #     non-CATEGORY relations (structural twins) AND share the same CATEGORY tail. Holding out a
    #     twin's CATEGORY edge => analogy aligns to a cluster-mate and projects the shared category.
    #     FREQUENCY_PRIOR (balanced categories) cannot. STORE_RECALL_FLOOR cannot (edge not stored).
    rng = np.random.RandomState(7)
    K = 8                      # clusters / categories
    per_cluster = 12
    n_attr_rel = 4             # non-category relation types
    triples = []               # (rel_name, head, tail)
    categories = ["CAT_%02d" % k for k in range(K)]
    attr_pool = ["attr_%02d_%02d" % (k, j) for k in range(K) for j in range(3)]
    heads = []
    for k in range(K):
        shared_attrs = ["attr_%02d_%02d" % (k, j) for j in range(3)]  # cluster-defining attributes
        for c in range(per_cluster):
            h = "c_%02d_%02d" % (k, c)
            heads.append((h, k))
            # CATEGORY edge (this is the held-out relation-type under test)
            triples.append(("CATEGORY", h, categories[k]))
            # non-category attribute edges shared within the cluster (structural twins)
            for ai, at in enumerate(shared_attrs):
                triples.append(("ATTR_%d" % (ai % n_attr_rel), h, at))
            # a bit of idiosyncratic noise edge
            triples.append(("ATTR_%d" % (rng.randint(0, n_attr_rel)),
                            h, attr_pool[rng.randint(0, len(attr_pool))]))

    S = build_analogy_split(triples, 7, ["CATEGORY"], n_heldout_per_rel=K * 4)
    # exclusion assert: no held-out (CATEGORY, head) pair survives in stored_fac
    Rc = S["ridx"]["CATEGORY"]
    for (r, a_, b_) in S["stored_fac"]:
        assert not (r == Rc and (Rc, a_) in S["heldout_pairs"]), "EXCLUSION LEAK in stored_fac"

    an_out, top1_arrays, pred_lists, diag = eval_analogy_family(
        S, topk=10, topk_align=20, use_idf=True, seed=7, role_weight=0.5)
    gen = torch.Generator().manual_seed(7)
    floor, _ = eval_store_recall_floor(S, 128, gen, topk=10)

    an1 = an_out["ANALOGY"]["top1"]
    fp1 = an_out["FREQUENCY_PRIOR"]["top1"]
    rd1 = an_out["RANDOM_ALIGNMENT"]["top1"]
    sh1 = an_out["SHUFFLED_PROFILE"]["top1"]
    sc1 = an_out["SCRAMBLED_ANALOGY_SOURCE"]["top1"]
    _progress("planted: ANALOGY=%.3f FREQ_PRIOR=%.3f RANDOM_ALIGN=%.3f SHUFFLED=%.3f SCRAMBLED=%.3f "
              "STORE_RECALL_FLOOR=%.3f outdeg_corr=%.3f"
              % (an1, fp1, rd1, sh1, sc1, floor["top1"], diag["outdeg_corr"]))

    base_rate = 1.0 / S["n_dict"]
    assert an1 >= 0.80, "INSTRUMENT VACUOUS: ANALOGY did not solve the planted twins (%.3f)" % an1
    assert an1 > fp1 + 0.20, "ANALOGY did not beat FREQUENCY_PRIOR (%.3f vs %.3f)" % (an1, fp1)
    assert an1 > rd1 + 0.20, "ANALOGY did not beat RANDOM_ALIGNMENT necessity control (%.3f vs %.3f)" % (an1, rd1)
    assert sh1 < an1 - 0.20, "SHUFFLED_PROFILE did not collapse (%.3f vs %.3f)" % (sh1, an1)
    assert floor["top1"] <= max(20.0 * base_rate, 0.02), (
        "STORE_RECALL_FLOOR did not collapse (%.3f) -> exclusion leak in planted test" % floor["top1"])
    _progress("SELF-TEST PASS (instrument fires: analogy solves twins >> freq/random; shuffled+floor collapse)")
    return {"verdict": "SELFTEST_PASS", "planted_analogy": an1, "planted_freq_prior": fp1,
            "planted_random_align": rd1, "planted_shuffled": sh1, "planted_scrambled": sc1,
            "planted_store_recall_floor": floor["top1"], "planted_outdeg_corr": diag["outdeg_corr"]}


# ---------------------------------------------------------------------------
# Config presets
# ---------------------------------------------------------------------------

DEFAULT_RELS = list(TABLE_SLOTS.keys())


def cfg_full():
    return {"run_mode": "full", "N": 1024, "seeds": [7, 13, 19],
            "rel_types": DEFAULT_RELS, "max_rows_per_rel": 1000,
            "heldout_rels": ["KINDOF", "PARTOF", "CAUSE", "USEDFOR", "MADEOF"],
            "n_heldout_per_rel": 120, "flat_steps": 500,
            "topk": 10, "topk_align": 50, "use_idf": True, "role_weight": 0.5}


def cfg_smoke():
    # KINDOF held-out edges (the cheap decisive floor test) but load several relations so ANALOGY has
    # non-KINDOF structure to align on (alignment excludes the predicted relation-type entirely).
    return {"run_mode": "smoke", "N": 256, "seeds": [7],
            "rel_types": ["KINDOF", "PARTOF", "SYNONYMY", "MADEOF", "USEDFOR", "CAUSE"],
            "max_rows_per_rel": 400,
            "heldout_rels": ["KINDOF"], "n_heldout_per_rel": 50, "flat_steps": 150,
            "topk": 10, "topk_align": 50, "use_idf": True, "role_weight": 0.5}


# ---------------------------------------------------------------------------
# Infra: start marker, crash metrics, atomic write
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    _write_metrics(output_dir, diag)


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
        cfg = cfg_full()  # default FULL (defensive per sec.16)
        suffix = ""
    output_dir = args.output_dir or os.path.join(REPO, "data", ANCHOR_NAME + suffix)
    expected_units = len(cfg["seeds"]) * 7
    _write_start_marker(output_dir, cfg["run_mode"], expected_units)
    metrics = run_experiment(cfg, output_dir)
    _write_metrics(output_dir, metrics)
    _progress("VERDICT %s | %s" % (metrics["verdict"], metrics["verdict_msg"]))


if __name__ == "__main__":
    _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        if "--smoke" in sys.argv:
            _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if "--self-test" not in sys.argv:
            _write_crash_metrics(_out_dir_for_crash, e)
        raise
