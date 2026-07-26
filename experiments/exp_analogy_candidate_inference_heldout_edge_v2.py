"""exp_analogy_candidate_inference_heldout_edge_v2

Brain-vs-us delta iteration on v1's clean HARD_FAIL (commit 70a2ea10e). v1 ran structure-mapping
analogy the NON-brain way (flat cosine over an edge-bag of ALL 17 bundled relations) and lost to a
FREQUENCY_PRIOR (analogy_top1=0.0259 < freq_prior=0.0724). The brain-fidelity audit named two
divergences, both of which v1 violated and both of which the data says matter:

  (1) CAPACITY: the brain integrates ~2-4 relations at once (Halford relational-complexity ~4 vars;
      LISA synchrony ~2-3 propositions). v1 flat-bundled ALL 17 relations -> drowned the signal
      (KINDOF-alone smoke ANALOGY=0.12 MIDDLE_BAND vs 17-bundle=0.026 full).
  (2) STRUCTURED ALIGNMENT: the brain does 1-to-1 structural CORRESPONDENCE + systematicity (prefers
      deeply-interconnected relational systems). v1 used flat COSINE of an edge-bag (discards
      correspondence + systematicity).

v2 closes BOTH and keeps every v1 guardrail (they are why the negative was trustworthy):
  - THE ONE CHANGE is the analogy mechanism (capacity-limited + SME structural correspondence).
  - REUSED VERBATIM from v1: leak-proof exclusion-from-ALL-storage (build_analogy_split),
    STORE_RECALL_FLOOR arm (must still collapse to base-rate), FLAT-MLP baseline, FREQUENCY_PRIOR
    arm (the bar to beat), the 3 must-fail controls (SCRAMBLED / SHUFFLED / RANDOM_ALIGNMENT), the
    relational-profile builder + IDF, and the same WorldTree corpus/splits for comparability.

2x2 ABLATION (this cell's attribution engine -- so a HARD_FAIL is INFORMATIVE about which divergence
matters, and a HARD_PASS attributes the win):
  - ABLATE_NEITHER_V1     = flat cosine, all relations  (reproduces v1's ANALOGY mechanism; a
                            positive-control-at-test-regime reproducer per Gate D)
  - ABLATE_CAPACITY_ONLY  = flat cosine, top-m relations (isolates the capacity divergence)
  - ABLATE_STRUCTURE_ONLY = structured correspondence, all relations (isolates structured alignment)
  - ANALOGY_v2 (BOTH)     = structured correspondence, top-m relations (the primary arm)
capacity_effect / structure_effect are 2x2 main effects (report which drove any gain).

Design-of-record: notes/research_learned_inference_generalization_analogy_metalearning_2026-07-26.md
                  (Steps 1a + HARD-FAIL forks b/c: capacity-limited 2-4 relations; structural alignment)
Base cell forked: experiments/exp_analogy_candidate_inference_heldout_edge_v1.py (commit 70a2ea10e)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-query top-1 prediction hash-test; ANALOGY_v2 collisions gate)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: prediction-accuracy discriminator; base_rate=1/n_dict + FREQUENCY_PRIOR reported as floors
# - baseline_in_band: EXEMPT (STORE_RECALL_FLOOR/FLAT/FREQUENCY_PRIOR are intended-floor baselines)
# - discriminator survives scale (planted self-test: ANALOGY_v2 >> FREQUENCY_PRIOR/RANDOM_ALIGNMENT; smoke at full-N KINDOF)
# - HARD_PASS strictly above floor + margin (beats FREQ_PRIOR by >=0.05 AND FLAT by clear margin)
# - HP_SCOPE per-arm declaration (ANALOGY_v2 only)
# - cardinality_ok: EXPECTED_N_UNITS gate
# - per-unit failure-class instrumentation (no bare except)
# - all numbers tagged in the design note/prereg (MEASURED@ / CITED@ / THEORETICAL@)
# - deterministic seeding (fixed ints, np.random.RandomState(seed+offset), sorted(set()); NO hash())

REUSE (verbatim, via importlib exec of the exact reference module -- no reinvention, no copy drift):
- load_worldtree_triples / TABLE_SLOTS  (WorldTree typed-triple loader; same 17-relation subset)
- build_random_content / random_g_table / make_unitary / bind_batch / unbind_batch / _l2norm
- build_memory / retrieve_tail_vec / cleanup           (STORE_RECALL_FLOOR arm ONLY)
- train_flat / FlatMLP / flat_predict                  (FLAT-MLP baseline)
REUSE (verbatim from v1): build_analogy_split, build_profiles, _vec_excl_R, frequency_prior_predict,
                          set_topk_acc, eval_store_recall_floor, eval_flat.
NEW code (this cell): capacity-limited + structured (SME) alignment scorer + 2x2 ablation family.

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
ANCHOR_NAME = "exp_analogy_candidate_inference_heldout_edge_v2"

# ---------------------------------------------------------------------------
# Verbatim reuse: exec the exact reference module (WorldTree loader + primitives + FLAT baseline).
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

# ---------------------------------------------------------------------------
# Verbatim reuse from v1: split + profiles + floor/flat + freq-prior + set-topk.
# (exec the v1 cell to pull them without copy drift.)
# ---------------------------------------------------------------------------
_V1_PATH = os.path.join(REPO, "experiments", "exp_analogy_candidate_inference_heldout_edge_v1.py")
_v1spec = importlib.util.spec_from_file_location("_analogy_v1", _V1_PATH)
_v1 = importlib.util.module_from_spec(_v1spec)
_v1spec.loader.exec_module(_v1)

build_analogy_split = _v1.build_analogy_split
build_profiles = _v1.build_profiles
_vec_excl_R = _v1._vec_excl_R
frequency_prior_predict = _v1.frequency_prior_predict
set_topk_acc = _v1.set_topk_acc
eval_store_recall_floor = _v1.eval_store_recall_floor
eval_flat = _v1.eval_flat


def _progress(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ===========================================================================
# THE ONE CHANGE: capacity-limited + structured (SME) alignment.
# ===========================================================================
#
# Representation (from v1 build_profiles): each concept owns sparse features keyed at index 0 by the
# relation-type, so leak-proofing (drop the predicted relation R) is a single f[0]==R test.
#   (r, slot, neighbor) -- exact relational PARTNER (parallel connectivity; strong SME evidence)
#   (r, slot, None)     -- relational ROLE signature (weak structural fingerprint)
#
# CAPACITY (divergence 1): rank the query concept's (relation, slot) roles by informativeness
#   (summed IDF) and keep only the top `cap_rels` (~2-4, Halford). Bundling ALL roles is what
#   drowned v1's signal.
#
# STRUCTURED ALIGNMENT (divergence 2): score a base E by SME structural correspondence over the
#   (capacity-limited) role set:
#     - one-to-one PARTNER correspondence: IDF-weighted count of EXACT shared partners under each
#       shared (relation, slot) role (set intersection = one-to-one at the partner level; use IDF
#       not raw multiplicity so a single high-count edge cannot dominate).
#     - weak ROLE match when both play the same (relation, slot) role without a shared partner.
#     - SYSTEMATICITY: multiply the summed per-role match by n_matched_roles ** gamma so a base
#       that matches C on a CONNECTED set of relations beats a base with one isolated big overlap.
#   This is Gentner/SME structural evaluation, NOT bag cosine. Still leak-proof (roles exclude R;
#   E's R-edge is used ONLY for projection, never for scoring) and content-agnostic (random-ID
#   neighbors; no borrowed embedding).


def build_scoring_index(feats, idf, R, base_pool, concept_universe):
    """Per-held-out-relation-R structures for the unified scorer.

    Returns a dict with:
      key_info[c]   : {(r,slot): sum_idf}                 -- capacity ranking (informativeness)
      key_sqnorm[c] : {(r,slot): sum(val^2)}              -- per-key cosine-norm contribution
      total_norm[c] : sqrt(sum all non-R val^2)           -- NEITHER/STRUCTURE_ONLY cosine denom
      inv[f]        : [(E, valE)] for E in base_pool       -- inverted index (base candidates only)
      idf           : passed through (for structured partner weighting)
    All feature vectors EXCLUDE relation R (leak-proof).
    """
    key_info = defaultdict(lambda: defaultdict(float))
    key_sqnorm = defaultdict(lambda: defaultdict(float))
    total_norm = {}
    inv = defaultdict(list)
    base_set = set(base_pool)
    for c in concept_universe:
        s2 = 0.0
        for f, w in feats[c].items():
            if f[0] == R:
                continue
            val = w * idf.get(f, 1.0)
            k = (f[0], f[1])
            key_info[c][k] += idf.get(f, 1.0)
            key_sqnorm[c][k] += val * val
            s2 += val * val
            if c in base_set:
                inv[f].append((c, val))
        total_norm[c] = float(np.sqrt(s2))
    return {"key_info": key_info, "key_sqnorm": key_sqnorm, "total_norm": total_norm,
            "inv": inv, "idf": idf}


def _cap_keys(key_info_c, cap_rels):
    """Top-`cap_rels` (relation,slot) roles of a concept by summed-IDF (deterministic tie-break)."""
    items = sorted(key_info_c.items(), key=lambda kv: (-kv[1], kv[0]))
    if cap_rels is None:
        return set(k for k, _ in items)
    return set(k for k, _ in items[:cap_rels])


def score_bases(query, idx, feats, R, cap_rels, structured, struct_role_weight, gamma):
    """Alignment score of `query` against every base_pool concept (via inverted index).

    cap_rels   : None = all roles; int = capacity-limited to top-cap_rels roles of the query.
    structured : False = flat IDF-cosine over the (subset of) shared features;
                 True  = SME structural correspondence (one-to-one partners + systematicity).
    Returns {E: score}. Blind to relation R (features exclude R). E's R-edge never enters here.
    """
    q_feats = {f: w for f, w in feats[query].items() if f[0] != R}
    if not q_feats:
        return {}
    keys_allowed = _cap_keys(idx["key_info"].get(query, {}), cap_rels)
    idf = idx["idf"]
    inv = idx["inv"]

    # active query features (restricted to the allowed capacity roles)
    active = {}
    for f, w in q_feats.items():
        k = (f[0], f[1])
        if k in keys_allowed:
            active[f] = w * idf.get(f, 1.0)
    if not active:
        return {}

    # accumulate shared features per candidate base E
    shared = defaultdict(list)  # E -> [(feature, valQ, valE)]
    for f, valq in active.items():
        for (E, vale) in inv.get(f, ()):
            if E == query:
                continue
            shared[E].append((f, valq, vale))
    if not shared:
        return {}

    if not structured:
        # flat IDF-cosine over the capacity subset.
        if cap_rels is None:
            qnorm = idx["total_norm"].get(query, 0.0)
        else:
            qnorm = float(np.sqrt(sum(idx["key_sqnorm"][query].get(k, 0.0) for k in keys_allowed)))
        if qnorm == 0.0:
            return {}
        out = {}
        for E, sh in shared.items():
            dot = sum(vq * ve for (_, vq, ve) in sh)
            if cap_rels is None:
                enorm = idx["total_norm"].get(E, 0.0)
            else:
                enorm = float(np.sqrt(sum(idx["key_sqnorm"][E].get(k, 0.0) for k in keys_allowed)))
            if enorm > 0.0:
                out[E] = dot / (qnorm * enorm)
        return out

    # structured: SME correspondence + systematicity.
    out = {}
    for E, sh in shared.items():
        per_key = defaultdict(float)
        role_key = defaultdict(float)
        for (f, vq, ve) in sh:
            k = (f[0], f[1])
            if f[2] is None:
                # shared role signature (weak); credited only if no partner also carries this key
                role_key[k] += struct_role_weight * idf.get(f, 1.0)
            else:
                # exact shared partner: one-to-one parallel connectivity, IDF-weighted (count once)
                per_key[k] += idf.get(f, 1.0)
        matched = set(per_key.keys())
        total = float(sum(per_key.values()))
        for k, rv in role_key.items():
            if k not in per_key:      # role-only match: weak evidence, adds to systematicity breadth
                total += rv
                matched.add(k)
        n_matched = len(matched)
        if n_matched == 0 or total <= 0.0:
            continue
        out[E] = total * (float(n_matched) ** gamma)
    return out


def analogy_predict_v2(heldout_R, feats, idx, R, r_tails_of, base_pool, topk, topk_align,
                       cap_rels, structured, struct_role_weight, gamma, mode, rng):
    """Candidate-inference predictions for every held-out head under relation R.

    mode: 'analogy'   -- real alignment (cap_rels/structured control the ablation cell).
          'random'    -- RANDOM_ALIGNMENT necessity control (random score, real projection).
          'shuffled'  -- SHUFFLED_PROFILE (concept<->profile identity permutation).
          'scrambled' -- SCRAMBLED_ANALOGY_SOURCE (real alignment, permuted E->D projection).
    Controls use the PRIMARY v2 mechanism config (cap_rels/structured as passed).
    """
    heads = sorted(heldout_R.keys())
    universe = sorted(base_pool)

    # projection map E -> set(D); 'scrambled' permutes the D assignment across R-edges.
    proj = r_tails_of
    if mode == "scrambled":
        edges = [(E, D) for E in r_tails_of for D in r_tails_of[E]]
        Ds = [D for (_, D) in edges]
        perm = np.arange(len(Ds))
        rng.shuffle(perm)
        proj = defaultdict(set)
        for i, (E, _) in enumerate(edges):
            proj[E].add(Ds[perm[i]])

    # 'shuffled' reassigns which concept owns which profile, then rebuilds the scoring index.
    feats_use = feats
    idx_use = idx
    if mode == "shuffled":
        all_c = sorted(feats.keys())
        permc = np.array(all_c)
        rng.shuffle(permc)
        remap = {all_c[i]: int(permc[i]) for i in range(len(all_c))}
        feats_use = {c: feats[remap[c]] for c in all_c}
        idx_use = build_scoring_index(feats_use, idx["idf"], R, universe,
                                      sorted(set(universe) | set(heads)))

    preds = []
    for a in heads:
        if mode == "random":
            sims = {E: float(rng.random()) for E in universe if E != a}
        else:
            sims = score_bases(a, idx_use, feats_use, R, cap_rels, structured,
                               struct_role_weight, gamma)
            sims = {E: s for E, s in sims.items() if E in base_pool and E != a}
        if not sims:
            preds.append([])
            continue
        top_E = sorted(sims.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:topk_align]
        cand = defaultdict(float)
        for E, s in top_E:
            for D in proj.get(E, ()):
                if s > cand[D]:
                    cand[D] = s
        ranked = sorted(cand.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:topk]
        preds.append([int(D) for (D, _) in ranked])
    return preds


# ---------------------------------------------------------------------------
# Analogy family evaluation: 2x2 ablation + FREQ_PRIOR + 3 controls; per relation + pooled.
# ---------------------------------------------------------------------------

# (arm_name, cap_flag, structured_flag) for the 4 ablation cells.
ABLATION = [
    ("ABLATE_NEITHER_V1", None, False),     # flat cosine, all relations  (reproduces v1 ANALOGY)
    ("ABLATE_CAPACITY_ONLY", "CAP", False),  # flat cosine, top-m relations
    ("ABLATE_STRUCTURE_ONLY", None, True),   # structured, all relations
    ("ANALOGY_v2", "CAP", True),             # structured, top-m relations  (PRIMARY)
]
CONTROL_ARMS = ["SCRAMBLED_ANALOGY_SOURCE", "SHUFFLED_PROFILE", "RANDOM_ALIGNMENT"]
ANALOGY_ARMS = [a for (a, _, _) in ABLATION] + CONTROL_ARMS + ["FREQUENCY_PRIOR"]


def eval_analogy_family(S, topk, topk_align, use_idf, seed, cap_rels, struct_role_weight, gamma,
                        role_weight=0.5):
    """Run the 4 ablation arms + FREQUENCY_PRIOR + 3 must-fail controls. Returns pooled per-arm
    metrics, per-relation per-arm metrics, per-arm top-1 prediction arrays (ARMS-MUST-DIFFER),
    per-arm prediction lists, and the ANALOGY_v2 out-degree diagnostic."""
    feats, idf = build_profiles(S["stored_fac"], S["n_dict"], use_idf=use_idf, role_weight=role_weight)

    r_tails = defaultdict(lambda: defaultdict(set))
    r_tail_counts = defaultdict(lambda: defaultdict(int))
    for (r, a, b) in S["stored_fac"]:
        r_tails[r][a].add(b)
        r_tail_counts[r][b] += 1

    arms = {m: {"preds": [], "gold": [], "top1_arr": []} for m in ANALOGY_ARMS}
    per_rel = defaultdict(dict)  # rel_name -> arm -> {top1, top10, n}
    outdeg_hits = []             # (nonR_key_count, hit_top1) for ANALOGY_v2 only
    n_cap_bound = 0              # query heads where the capacity cap actually prunes (roles > cap_rels)
    n_query_total = 0
    n_zero_role = 0             # query heads with NO non-R roles (cannot be analogized at all)

    for Rr in sorted(S["heldout"].keys()):
        rel_name = S["rel_names"][Rr]
        heldout_R = S["heldout"][Rr]
        heads = sorted(heldout_R.keys())
        gold_sets = [set(int(t) for t in heldout_R[a]) for a in heads]
        base_pool = set(r_tails[Rr].keys())
        universe = sorted(set(base_pool) | set(heads) | set(feats.keys()))
        idx = build_scoring_index(feats, idf, Rr, sorted(base_pool), universe)

        rel_preds = {}
        # 4 ablation cells (real alignment, mode='analogy', cap/structured varied)
        for (arm, capf, structf) in ABLATION:
            cap = cap_rels if capf == "CAP" else None
            rng = np.random.RandomState(seed + 101 + Rr)
            p = analogy_predict_v2(heldout_R, feats, idx, Rr, r_tails[Rr], base_pool, topk,
                                   topk_align, cap, structf, struct_role_weight, gamma, "analogy", rng)
            rel_preds[arm] = p
        # controls use the PRIMARY v2 config (cap_rels, structured=True)
        rng_s = np.random.RandomState(seed + 202 + Rr)
        rng_h = np.random.RandomState(seed + 303 + Rr)
        rng_r = np.random.RandomState(seed + 404 + Rr)
        rel_preds["SCRAMBLED_ANALOGY_SOURCE"] = analogy_predict_v2(
            heldout_R, feats, idx, Rr, r_tails[Rr], base_pool, topk, topk_align,
            cap_rels, True, struct_role_weight, gamma, "scrambled", rng_s)
        rel_preds["SHUFFLED_PROFILE"] = analogy_predict_v2(
            heldout_R, feats, idx, Rr, r_tails[Rr], base_pool, topk, topk_align,
            cap_rels, True, struct_role_weight, gamma, "shuffled", rng_h)
        rel_preds["RANDOM_ALIGNMENT"] = analogy_predict_v2(
            heldout_R, feats, idx, Rr, r_tails[Rr], base_pool, topk, topk_align,
            cap_rels, True, struct_role_weight, gamma, "random", rng_r)
        rel_preds["FREQUENCY_PRIOR"] = frequency_prior_predict(heldout_R, r_tail_counts[Rr], topk)

        for name in ANALOGY_ARMS:
            p = rel_preds[name]
            arms[name]["preds"].extend(p)
            arms[name]["gold"].extend(gold_sets)
            for i, gs in enumerate(gold_sets):
                row = p[i][:1] if i < len(p) else []
                arms[name]["top1_arr"].append(1 if (gs and any(int(d) in gs for d in row)) else 0)
            per_rel[rel_name][name] = {"top1": set_topk_acc(p, gold_sets, 1),
                                       "top10": set_topk_acc(p, gold_sets, topk),
                                       "n": len(gold_sets)}

        # out-degree diagnostic (ANALOGY_v2): distinct non-R (relation,slot) roles as richness proxy
        p_an = rel_preds["ANALOGY_v2"]
        for i, a in enumerate(heads):
            deg = len(idx["key_info"].get(a, {}))
            hit = 1 if (gold_sets[i] and i < len(p_an) and any(int(d) in gold_sets[i]
                                                               for d in p_an[i][:1])) else 0
            outdeg_hits.append((deg, hit))
            n_query_total += 1
            if deg == 0:
                n_zero_role += 1
            if cap_rels is not None and deg > cap_rels:
                n_cap_bound += 1

    out = {}
    for name in ANALOGY_ARMS:
        g = arms[name]["gold"]
        p = arms[name]["preds"]
        out[name] = {"top1": set_topk_acc(p, g, 1), "top10": set_topk_acc(p, g, topk), "n": len(g)}

    outdeg_corr = 0.0
    outdeg_bins = {}
    if len(outdeg_hits) >= 4:
        degs = np.array([d for (d, _) in outdeg_hits], dtype=np.float64)
        hits = np.array([h for (_, h) in outdeg_hits], dtype=np.float64)
        if degs.std() > 1e-9 and hits.std() > 1e-9:
            outdeg_corr = float(np.corrcoef(degs, hits)[0, 1])
        order = np.argsort(degs)
        for bi, idxs in enumerate(np.array_split(order, 3)):
            if len(idxs):
                outdeg_bins["tercile_%d" % bi] = {"deg_mean": float(degs[idxs].mean()),
                                                  "acc_top1": float(hits[idxs].mean()),
                                                  "n": int(len(idxs))}

    top1_arrays = {name: np.array(arms[name]["top1_arr"], dtype=np.int64) for name in ANALOGY_ARMS}
    pred_lists = {name: [list(map(int, r)) for r in arms[name]["preds"]] for name in ANALOGY_ARMS}
    diag = {"outdeg_corr": outdeg_corr, "outdeg_bins": outdeg_bins, "n_queries": len(outdeg_hits),
            "cap_bound_frac": (n_cap_bound / n_query_total) if n_query_total else 0.0,
            "zero_role_frac": (n_zero_role / n_query_total) if n_query_total else 0.0}
    return out, top1_arrays, pred_lists, dict(per_rel), diag


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF): only an ANALOGY_v2-involving collision gates HARD_FAIL.
# ---------------------------------------------------------------------------

def arms_must_differ(pred_lists, floor_preds, flat_preds):
    digests = {name: hashlib.sha256(json.dumps(preds).encode("utf-8")).hexdigest()
               for name, preds in pred_lists.items()}
    digests["STORE_RECALL_FLOOR"] = hashlib.sha256(json.dumps(floor_preds).encode("utf-8")).hexdigest()
    digests["FLAT"] = hashlib.sha256(json.dumps(flat_preds).encode("utf-8")).hexdigest()
    names = sorted(digests)
    collisions = [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))
                  if digests[names[i]] == digests[names[j]]]
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
    cap_rels = cfg["cap_rels"]
    struct_role_weight = cfg["struct_role_weight"]
    gamma = cfg["gamma"]

    _progress("loading WorldTree triples ...")
    triples, rel_names = load_worldtree_triples(cfg["rel_types"], cfg["max_rows_per_rel"])
    _progress("loaded %d triples across %d relation types" % (len(triples), len(rel_names)))
    if len(triples) < 20:
        raise ValueError("INSUFFICIENT_DATA: only %d triples parsed" % len(triples))

    arm_names = ["STORE_RECALL_FLOOR", "FLAT"] + ANALOGY_ARMS

    per_seed = []
    arm_digests_logged = None
    arm_collisions_logged = None
    per_rel_accum = defaultdict(lambda: defaultdict(lambda: {"top1": [], "top10": []}))
    for si, seed in enumerate(seeds):
        _progress("seed %d/%d (seed=%d)" % (si + 1, len(seeds), seed))
        gen = torch.Generator().manual_seed(seed)
        S = build_analogy_split(triples, seed, cfg["heldout_rels"], cfg["n_heldout_per_rel"])
        R = len(S["rel_names"])
        n_dict = S["n_dict"]
        base_rate = 1.0 / max(n_dict, 1)
        n_heldout = sum(len(S["heldout"][r]) for r in S["heldout"])
        _progress("  n_dict=%d R=%d n_heldout=%d n_stored=%d base_rate=%.5f cap_rels=%s gamma=%.2f"
                  % (n_dict, R, n_heldout, len(S["stored_fac"]), base_rate, cap_rels, gamma))
        if n_heldout < 4:
            raise ValueError("INSUFFICIENT_HELDOUT: only %d held-out heads" % n_heldout)

        # --- THE GATE FIRST: store-recall floor on the exclusion-enforced split ---
        floor, floor_preds = eval_store_recall_floor(S, N, gen, topk)
        _progress("  STORE_RECALL_FLOOR top1=%.5f top10=%.5f (base_rate=%.5f)"
                  % (floor["top1"], floor["top10"], base_rate))

        flat, flat_preds = eval_flat(S, N, R, cfg["flat_steps"], gen, topk)
        _progress("  FLAT top1=%.5f top10=%.5f" % (flat["top1"], flat["top10"]))

        an_out, top1_arrays, pred_lists, per_rel, diag = eval_analogy_family(
            S, topk, topk_align, use_idf, seed, cap_rels, struct_role_weight, gamma,
            role_weight=cfg["role_weight"])
        _progress("  ANALOGY_v2 top1=%.5f top10=%.5f | FREQ_PRIOR top1=%.5f | "
                  "NEITHER=%.5f CAP_ONLY=%.5f STRUCT_ONLY=%.5f | "
                  "RAND=%.5f SCRAM=%.5f SHUF=%.5f | outdeg_corr=%.3f"
                  % (an_out["ANALOGY_v2"]["top1"], an_out["ANALOGY_v2"]["top10"],
                     an_out["FREQUENCY_PRIOR"]["top1"], an_out["ABLATE_NEITHER_V1"]["top1"],
                     an_out["ABLATE_CAPACITY_ONLY"]["top1"], an_out["ABLATE_STRUCTURE_ONLY"]["top1"],
                     an_out["RANDOM_ALIGNMENT"]["top1"], an_out["SCRAMBLED_ANALOGY_SOURCE"]["top1"],
                     an_out["SHUFFLED_PROFILE"]["top1"], diag["outdeg_corr"]))

        arms = {"STORE_RECALL_FLOOR": floor, "FLAT": flat}
        arms.update(an_out)

        for rel_name, armd in per_rel.items():
            for arm, m in armd.items():
                per_rel_accum[rel_name][arm]["top1"].append(m["top1"])
                per_rel_accum[rel_name][arm]["top10"].append(m["top10"])

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

    per_rel_summary = {}
    for rel_name, armd in per_rel_accum.items():
        per_rel_summary[rel_name] = {arm: {"top1": float(np.mean(m["top1"])),
                                           "top10": float(np.mean(m["top10"]))}
                                     for arm, m in armd.items()}

    floor_top1 = summary["STORE_RECALL_FLOOR"]["top1"]
    flat_top1 = summary["FLAT"]["top1"]
    analogy_top1 = summary["ANALOGY_v2"]["top1"]
    freq_top1 = summary["FREQUENCY_PRIOR"]["top1"]
    neither_top1 = summary["ABLATE_NEITHER_V1"]["top1"]
    cap_only_top1 = summary["ABLATE_CAPACITY_ONLY"]["top1"]
    struct_only_top1 = summary["ABLATE_STRUCTURE_ONLY"]["top1"]

    # 2x2 attribution (which brain divergence moved the needle)
    capacity_effect = 0.5 * ((cap_only_top1 - neither_top1) + (analogy_top1 - struct_only_top1))
    structure_effect = 0.5 * ((struct_only_top1 - neither_top1) + (analogy_top1 - cap_only_top1))
    interaction = analogy_top1 - cap_only_top1 - struct_only_top1 + neither_top1
    if capacity_effect >= structure_effect and capacity_effect > 0.005:
        driver = "CAPACITY"
    elif structure_effect > capacity_effect and structure_effect > 0.005:
        driver = "STRUCTURE"
    else:
        driver = "NEITHER_MOVED"

    # must-fail control collapse band: within noise of FREQUENCY_PRIOR / base-rate floor
    collapse_band = max(freq_top1, 3.0 * base_rate) + 0.03
    controls = {c: {"top1": summary[c]["top1"], "collapsed": summary[c]["top1"] <= collapse_band}
                for c in CONTROL_ARMS}
    controls_collapse = all(controls[c]["collapsed"] for c in CONTROL_ARMS)

    floor_leak_band = max(20.0 * base_rate, 0.02)
    store_recall_collapsed = floor_top1 <= floor_leak_band

    # positive-control (Gate D): NEITHER should reproduce v1's ANALOGY at the SAME regime.
    neither_reproduces_v1 = None  # informational; not gating (v1 metric read at report time)

    def clears(x, ref):
        return (x - ref >= 0.15) or (x >= 10.0 * base_rate and ref <= 2.0 * base_rate)

    clears_floor_hp = clears(analogy_top1, floor_top1)
    clears_flat_hp = clears(analogy_top1, flat_top1)
    beats_freq_prior = (analogy_top1 - freq_top1) >= 0.05
    beats_flat = (analogy_top1 - flat_top1) >= 0.05
    positive_outdeg = outdeg_corr > 0.0
    ties_floor_flat = (analogy_top1 - floor_top1 <= 0.05) and (analogy_top1 - flat_top1 <= 0.05)
    clears_floor_mb = (analogy_top1 - floor_top1 >= 0.05) and (analogy_top1 - flat_top1 >= 0.05)
    structure_genuine = beats_freq_prior and positive_outdeg

    # cardinality
    expected_units = len(seeds) * len(arm_names)
    actual_units = sum(len(ps["arms"]) for ps in per_seed)
    cardinality_ok = actual_units >= expected_units
    # AF gate: a collision AMONG ABLATION SIBLINGS is EXPECTED when a factor (capacity cap / structure
    # flag) is a no-op on the corpus slice -- e.g. concepts with <= cap_rels roles => the cap prunes
    # nothing => ANALOGY_v2 == STRUCTURE_ONLY bit-identical. That is DATA (WorldTree is relation-sparse
    # per concept), not a duplicate-mechanism bug. The AF gate fires ONLY when ANALOGY_v2 is bit-
    # identical to a NON-ablation arm (a control/baseline) -- THAT would mean the alignment did nothing
    # (mechanism == its own shuffled/random control), a real bug.
    ABLATION_ARM_SET = {"ABLATE_NEITHER_V1", "ABLATE_CAPACITY_ONLY", "ABLATE_STRUCTURE_ONLY",
                        "ANALOGY_v2"}
    arm_collisions_logged = arm_collisions_logged or []
    analogy_bug_collisions = [list(p) for p in arm_collisions_logged
                              if ("ANALOGY_v2" in p)
                              and not (p[0] in ABLATION_ARM_SET and p[1] in ABLATION_ARM_SET)]
    ablation_sibling_collisions = [list(p) for p in arm_collisions_logged
                                   if p[0] in ABLATION_ARM_SET and p[1] in ABLATION_ARM_SET]
    arms_differ = (len(analogy_bug_collisions) == 0)
    cap_bound_frac = float(np.mean([ps["outdeg_diag"].get("cap_bound_frac", 0.0) for ps in per_seed]))
    zero_role_frac = float(np.mean([ps["outdeg_diag"].get("zero_role_frac", 0.0) for ps in per_seed]))

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
    elif not beats_freq_prior:
        verdict = "HARD_FAIL_ANALOGY_v2_STILL_LOSES_OR_TIES_FREQUENCY_PRIOR"
    elif clears_floor_hp and clears_flat_hp and beats_freq_prior and beats_flat and structure_genuine:
        verdict = "HARD_PASS"
    elif clears_floor_mb and beats_freq_prior and (not positive_outdeg):
        verdict = "MIDDLE_BAND_ANALOGY_v2_BEATS_FREQ_BUT_OUTDEG_FLAT"
    elif clears_floor_mb:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "ANALOGY_v2 top1=%.5f top10=%.5f | FREQ_PRIOR=%.5f (beats=%s d=%+.4f) | FLAT=%.5f (beats=%s) | "
        "STORE_RECALL_FLOOR=%.5f (leak_band=%.4f collapsed=%s) | "
        "ABLATION[NEITHER=%.5f CAP_ONLY=%.5f STRUCT_ONLY=%.5f] "
        "cap_effect=%+.4f struct_effect=%+.4f interaction=%+.4f driver=%s | "
        "controls[SCRAM=%.5f SHUF=%.5f RAND=%.5f] collapse_band=%.4f collapse=%s | "
        "cap_bound_frac=%.3f zero_role_frac=%.3f | "
        "clears_floor=%s clears_flat=%s outdeg_corr=%.3f structure_genuine=%s base_rate=%.5f n_heldout=%d"
        % (analogy_top1, summary["ANALOGY_v2"]["top10"], freq_top1, beats_freq_prior,
           analogy_top1 - freq_top1, flat_top1, beats_flat, floor_top1, floor_leak_band,
           store_recall_collapsed, neither_top1, cap_only_top1, struct_only_top1,
           capacity_effect, structure_effect, interaction, driver,
           summary["SCRAMBLED_ANALOGY_SOURCE"]["top1"], summary["SHUFFLED_PROFILE"]["top1"],
           summary["RANDOM_ALIGNMENT"]["top1"], collapse_band, controls_collapse,
           cap_bound_frac, zero_role_frac,
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
        "per_relation_summary": per_rel_summary,
        "primary_metric": "analogy_v2_top1 (held-out edge NEVER stored; capacity-limited structured alignment)",
        "store_recall_floor_top1": floor_top1,
        "store_recall_collapsed": store_recall_collapsed,
        "floor_leak_band": floor_leak_band,
        "flat_top1": flat_top1,
        "analogy_v2_top1": analogy_top1,
        "frequency_prior_top1": freq_top1,
        "analogy_minus_floor": analogy_top1 - floor_top1,
        "analogy_minus_flat": analogy_top1 - flat_top1,
        "analogy_minus_freq_prior": analogy_top1 - freq_top1,
        "beats_frequency_prior": beats_freq_prior,
        "beats_flat": beats_flat,
        "ablation": {"NEITHER_V1": neither_top1, "CAPACITY_ONLY": cap_only_top1,
                     "STRUCTURE_ONLY": struct_only_top1, "BOTH_ANALOGY_v2": analogy_top1},
        "capacity_effect": capacity_effect,
        "structure_effect": structure_effect,
        "ablation_interaction": interaction,
        "driver": driver,
        "neither_reproduces_v1": neither_reproduces_v1,
        "controls": controls,
        "collapse_band": collapse_band,
        "controls_collapse": controls_collapse,
        "clears_floor_hp": clears_floor_hp,
        "clears_flat_hp": clears_flat_hp,
        "outdeg_corr_mean": outdeg_corr,
        "positive_outdegree": positive_outdeg,
        "structure_genuine": structure_genuine,
        "cardinality_ok": cardinality_ok,
        "expected_units": expected_units,
        "actual_units": actual_units,
        "arms_differ_verified": arms_differ,
        "arm_digests": arm_digests_logged,
        "arm_collisions": arm_collisions_logged,
        "analogy_bug_collisions": analogy_bug_collisions,
        "ablation_sibling_collisions": ablation_sibling_collisions,
        "cap_bound_frac": cap_bound_frac,
        "zero_role_frac": zero_role_frac,
        "cap_rels": cap_rels,
        "per_seed": per_seed,
    }
    return metrics


# ---------------------------------------------------------------------------
# Self-test: planted graph with structural twins -> ANALOGY_v2 >> FREQUENCY_PRIOR / RANDOM_ALIGNMENT,
# STORE_RECALL_FLOOR + SHUFFLED collapse, and BOTH >= NEITHER (ablation sane).
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

    # (2) planted graph: K clusters; concepts in a cluster share EXACT attribute-partners under
    #     non-CATEGORY relations (structural twins) AND the same CATEGORY tail. Holding out a twin's
    #     CATEGORY edge => structured capacity-limited alignment aligns to a cluster-mate (exact
    #     shared partners + systematicity) and projects the shared category. FREQUENCY_PRIOR (balanced
    #     categories) cannot; STORE_RECALL_FLOOR cannot (edge never stored).
    rng = np.random.RandomState(7)
    K = 8
    per_cluster = 12
    n_attr_rel = 4
    triples = []
    categories = ["CAT_%02d" % k for k in range(K)]
    attr_pool = ["attr_%02d_%02d" % (k, j) for k in range(K) for j in range(3)]
    for k in range(K):
        shared_attrs = ["attr_%02d_%02d" % (k, j) for j in range(3)]
        for c in range(per_cluster):
            h = "c_%02d_%02d" % (k, c)
            triples.append(("CATEGORY", h, categories[k]))
            for ai, at in enumerate(shared_attrs):
                triples.append(("ATTR_%d" % (ai % n_attr_rel), h, at))
            triples.append(("ATTR_%d" % (rng.randint(0, n_attr_rel)),
                            h, attr_pool[rng.randint(0, len(attr_pool))]))

    S = build_analogy_split(triples, 7, ["CATEGORY"], n_heldout_per_rel=K * 4)
    Rc = S["ridx"]["CATEGORY"]
    for (r, a_, b_) in S["stored_fac"]:
        assert not (r == Rc and (Rc, a_) in S["heldout_pairs"]), "EXCLUSION LEAK in stored_fac"

    an_out, top1_arrays, pred_lists, per_rel, diag = eval_analogy_family(
        S, topk=10, topk_align=20, use_idf=True, seed=7, cap_rels=4, struct_role_weight=0.25,
        gamma=1.0, role_weight=0.5)
    gen = torch.Generator().manual_seed(7)
    floor, _ = eval_store_recall_floor(S, 128, gen, topk=10)

    an1 = an_out["ANALOGY_v2"]["top1"]
    fp1 = an_out["FREQUENCY_PRIOR"]["top1"]
    rd1 = an_out["RANDOM_ALIGNMENT"]["top1"]
    sh1 = an_out["SHUFFLED_PROFILE"]["top1"]
    sc1 = an_out["SCRAMBLED_ANALOGY_SOURCE"]["top1"]
    neither = an_out["ABLATE_NEITHER_V1"]["top1"]
    _progress("planted: ANALOGY_v2=%.3f FREQ_PRIOR=%.3f RANDOM_ALIGN=%.3f SHUFFLED=%.3f SCRAMBLED=%.3f "
              "NEITHER_V1=%.3f STORE_RECALL_FLOOR=%.3f outdeg_corr=%.3f"
              % (an1, fp1, rd1, sh1, sc1, neither, floor["top1"], diag["outdeg_corr"]))

    base_rate = 1.0 / S["n_dict"]
    assert an1 >= 0.80, "INSTRUMENT VACUOUS: ANALOGY_v2 did not solve the planted twins (%.3f)" % an1
    assert an1 > fp1 + 0.20, "ANALOGY_v2 did not beat FREQUENCY_PRIOR (%.3f vs %.3f)" % (an1, fp1)
    assert an1 > rd1 + 0.20, "ANALOGY_v2 did not beat RANDOM_ALIGNMENT (%.3f vs %.3f)" % (an1, rd1)
    assert sh1 < an1 - 0.20, "SHUFFLED_PROFILE did not collapse (%.3f vs %.3f)" % (sh1, an1)
    assert an1 >= neither - 1e-9, "ABLATION INVERTED: BOTH < NEITHER on planted (%.3f < %.3f)" % (an1, neither)
    assert floor["top1"] <= max(20.0 * base_rate, 0.02), (
        "STORE_RECALL_FLOOR did not collapse (%.3f) -> exclusion leak in planted test" % floor["top1"])
    _progress("SELF-TEST PASS (v2 instrument fires: capacity+structured solves twins >> freq/random; "
              "shuffled+floor collapse; ablation non-inverted)")
    return {"verdict": "SELFTEST_PASS", "planted_analogy_v2": an1, "planted_freq_prior": fp1,
            "planted_random_align": rd1, "planted_shuffled": sh1, "planted_scrambled": sc1,
            "planted_neither_v1": neither, "planted_store_recall_floor": floor["top1"],
            "planted_outdeg_corr": diag["outdeg_corr"]}


# ---------------------------------------------------------------------------
# Config presets
# ---------------------------------------------------------------------------

DEFAULT_RELS = list(TABLE_SLOTS.keys())


def cfg_full():
    return {"run_mode": "full", "N": 1024, "seeds": [7, 13, 19],
            "rel_types": DEFAULT_RELS, "max_rows_per_rel": 1000,
            "heldout_rels": ["KINDOF", "PARTOF", "CAUSE", "USEDFOR", "MADEOF"],
            "n_heldout_per_rel": 120, "flat_steps": 500,
            "topk": 10, "topk_align": 50, "use_idf": True, "role_weight": 0.5,
            "cap_rels": 4, "struct_role_weight": 0.25, "gamma": 1.0}


def cfg_smoke():
    # KINDOF held-out (v1 smoke ANALOGY=0.12 MB) but load several relations so alignment has non-KINDOF
    # structure. Full-N (N=1024) so the discriminator survives scale (DISCRIMINATOR-MUST-SURVIVE-SCALE).
    return {"run_mode": "smoke", "N": 1024, "seeds": [7],
            "rel_types": ["KINDOF", "PARTOF", "SYNONYMY", "MADEOF", "USEDFOR", "CAUSE"],
            "max_rows_per_rel": 400,
            "heldout_rels": ["KINDOF"], "n_heldout_per_rel": 50, "flat_steps": 150,
            "topk": 10, "topk_align": 50, "use_idf": True, "role_weight": 0.5,
            "cap_rels": 4, "struct_role_weight": 0.25, "gamma": 1.0}


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
    expected_units = len(cfg["seeds"]) * (2 + len(ANALOGY_ARMS))
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
