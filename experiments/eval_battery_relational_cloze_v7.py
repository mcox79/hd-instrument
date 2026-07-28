"""COMPREHENSION EVAL BATTERY -- PRIMARY SUB-TEST: relational cloze v7 (anti-Peng adversarial K-way).

NOT a dispatched cell. No queue, no GPU, no bank/push. Standalone reusable module + script:
run to completion in the foreground (CPU, minutes) on the frozen ckpt_seed_7 checkpoint, read
results.json off disk. Callable again for future encoder/readout/consolidation variants via
run_battery(ckpt_path=...).

WHY (the gate this fixes): notes/brain_fidelity_full_pipeline_element_audit_2026-07-28.md ranked
the eval METRIC as severity-3 but GATING all higher-severity rows -- if the metric can't separate
comprehension from memorization, no upstream fix (encoder objective, readout, consolidation) can
be credited. Concretely: relational-AUC is compressed near chance (0.51-0.56, ~0.05 dynamic
range, exp_scale_meaning_learn_arc_heldout_v2.py::relational_eval) and v6's fact-cloze replacement
fell into the EXACT Peng et al. (2020) trap it was built to diagnose:
data/exp_prop_extraction_selfteach_v6/metrics.json -> b0_identity_acc=0.754 against a
B0_HARD_FAIL_MIN=0.65 band. Predicting the relation from OBJECT IDENTITY ALONE (a frequency
table, no sentence read) solved 75% of held items.

DESIGN (see notes/brain_faithful_comprehension_eval_battery_design_2026-07-28.md +
notes/research_comprehension_eval_battery_lit_grounding_2026-07-28.md for the full lit-scan):
the field-standard fix (Poliak/Gururangan hypothesis-only-baseline gate; Gardner contrast-sets;
Zellers HellaSwag adversarial-filtering) is NOT a better classifier -- it's a different, per-item
CANDIDATE POOL, adversarially constructed against B0 itself, PLUS eval-set STRATIFICATION so B0's
"always guess the object's majority relation" strategy is forced toward ~1/K by construction:

  1. Per held item (subject, true_relation, object, real co-occurring sentence), rank ALL label
     relations by B0's train-only per-object frequency table. Candidate pool = top-K by that
     ranking, always including the true relation (inject-replace-lowest if it fell outside top-K).
  2. b0_rank_of_true = the true relation's position in that per-object ranking (1 = B0's own top
     guess for this object). THE KEY FIX (the part v7 adds beyond just building a K-pool): a raw
     held set is DOMINATED by rank-1 items (that is mechanically WHY the old b0_identity_acc was
     0.754 -- CSKG's relation distribution is itself majority-skewed per object, so the "next"
     edge of a given object usually IS its own dominant relation). Building a K-pool alone does
     NOT fix this: B0's forced-choice-within-the-pool prediction is ALWAYS the object's rank-1
     pool member, so B0's within-pool accuracy still equals (fraction of items where true==rank1)
     -- unchanged from the unconstrained task unless that fraction itself is fixed at 1/K. So v7
     STRATIFIES the eval set: bucket items by min(b0_rank_of_true, K) and subsample to a balanced
     cap PER BUCKET. Now B0's "always guess rank-1" strategy is correct on exactly the rank-1
     bucket and wrong on every other bucket -- forcing B0_KWAY accuracy toward 1/K BY
     CONSTRUCTION, not by hoping the classifier gets confused. This is the ruler-validation gate
     this script exists to run (see build_verdict()).
  3. Three-tier held-out (KB-completion transductive/inductive precedent):
       Tier A (new concept): subject never appears in ANY train edge (reuses V2.build_split's
         leak-proof freq-stratified sha256-ranked concept split, the standing split every loop
         cell v1-v6 uses).
       Tier B (new concept-pair): subject AND object each individually seen in train, but that
         exact (subject,object) PAIR withheld from every train instance (deterministic sha256
         rank over "subject|object", a NEW split axis this design introduces) -- catches
         memorized-triple lookup vs. genuinely generalized relational reading.
       Tier C (new relation-type): one whole relation type held out of TRAIN entirely (zero
         instances, zero B0 signal) and tested via the sentence alone -- the hardest tier; a
         simple linear decoder is NOT expected to generalize here (no weight vector ever trains
         for that output unit) and this is reported as an honest, informative floor-check, not a
         capability claim.
  4. Controls carried over from v6: concept-pair-preserving word-scramble (LOOP2._scramble_words
     -- same token multiset, order destroyed) and the wrong-dominant-relation slice (here: simply
     the rank>=2 buckets of the Tier-A stratified set -- B0's forced pick is ALWAYS rank-1, so its
     accuracy on this slice is 0% by construction, an even cleaner control than v6's open-set
     wrong_rel_slice).

SIGNAL PATH ("does the ruler leave room for a real comprehension signal to separate from chance"):
  - COSINE_CENTROID: fully closed-form, NO training. Sentence gestalt = ContentRoleReadout(d,
    mode="fixed") applied to the frozen encoder's per-token hidden states (v6's own class,
    imported directly -- content-addressed, position-invariant by construction, order-sensitive
    because h_i is itself already context-mixed by self-attention; a FIXED random projection, so
    this arm needs zero gradient steps). Score = cosine(g_held, per-relation TRAIN centroid).
  - LEARNED_DECODER: a single nn.Linear(d, n_relations) fit by ~400 Adam steps on CACHED, already-
    computed TRAIN gestalts (fit is near-instantaneous once gestalts are cached -- same cost class
    as tonight's diag_readout_limit_probe_v1.py PROBE_BILINEAR, ~40-50s wall for a similarly-sized
    fit) -- the "learned leak-proof decoder (fit train-only), not just cosine" ingredient the
    director's task explicitly asked to carry over from that probe's finding (+0.067 AUC margin
    over cosine-NN on held-out-NEW).
  Both arms only need ONE batched frozen forward pass over train sentences (to build cached
  gestalts + fit the centroids/linear head) and ONE over held sentences (all tiers + their
  scrambled twins) -- no repeated encoder passes, no encoder fine-tuning, no heavy training
  anywhere in this script. CPU, minutes.

LEAK-PROOFING: TRAIN instances never include a Tier-A held subject, a Tier-B withheld pair, or any
Tier-C-relation edge (asserted by self_test() and by a runtime assertion in build_dataset()).
Every distractor / stratification draw uses np.random.default_rng(seed + fixed_offset), matching
the existing convention in relational_eval (seed+71) and v6 (seed+202/301/401).

REUSE (this is ~95% wiring, not new mechanism): V2.load_concept_universe / count_pass /
build_split / collect_pass (concept universe + leak-proof split + postings, unchanged);
v6._load_typed_edges / _find_cooccurring_sentences / _b0_table / ContentRoleReadout /
_frozen_hidden / _cache_ids_for_sentences (typed-edge loading, distant-supervision sentence
lookup, B0 table, and the content-addressed readout class, all imported directly, zero
reimplementation); LOOP2._build_encoder_from_ckpt / _scramble_words (frozen encoder loader +
scramble control, same as v6); diag_readout_limit_probe_v1.load_frozen_encoder (this session's
own frozen-checkpoint loader, identical convention). The only NEW code is: the per-item
adversarial pool + b0_rank computation, the rank-stratified balanced sampling, the Tier-B/Tier-C
split construction, and the two signal-path scorers.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_scale_meaning_learn_arc_heldout_v2 as V2  # noqa: E402
import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402
from experiments.exp_prop_extraction_selfteach_v6 import (  # noqa: E402
    ContentRoleReadout, _frozen_hidden, _cache_ids_for_sentences,
    _load_typed_edges, _find_cooccurring_sentences,
)
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402

ANCHOR_NAME = "eval_battery_relational_cloze_v7"
CKPT_PATH = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")
OUT_DIR = os.path.join(_REPO, "data", "eval_battery_relational_cloze_v7")

PAIR_SPLIT_SALT = "eval_battery_v7_pair_withhold::"

# ---------------------------------------------------------------------------
# Config profiles. FULL kept reduced-scale (CPU minutes, not V2's full 10M-line regime) -- this
# is a diagnostic/eval-battery instrument, not a capability-scale claim; see note_caveat in output.
# ---------------------------------------------------------------------------
FULL_CFG = dict(
    min_deg=2, cap_eval_concepts=6000, heldout_count=500, min_mentions_eval=8,
    max_lines=3000000, dedup_cap=2500000, bpe_sample_lines=100, cap_mentions=32,
    max_len=32, n_freq_buckets=6, max_shards=16, encode_batch=256,
    top_n_relations=16, min_train_per_rel=15, max_sent_per_edge=2,
    K=4, pair_withhold_frac=0.15, tier_c_count_lo=80, tier_c_count_hi=1200,
    decoder_steps=400, decoder_lr=0.02, decoder_wd=0.02,
    stratify_cap_per_bucket=60, tier_bc_cap=200,
)
SELFTEST_CFG = dict(
    min_deg=0, cap_eval_concepts=None, heldout_count=6, min_mentions_eval=0,
    max_lines=None, dedup_cap=10000, bpe_sample_lines=10, cap_mentions=10,
    max_len=16, n_freq_buckets=2, max_shards=1, encode_batch=8,
    top_n_relations=6, min_train_per_rel=1, max_sent_per_edge=2,
    K=4, pair_withhold_frac=0.3, tier_c_count_lo=1, tier_c_count_hi=10000,
    decoder_steps=40, decoder_lr=0.05, decoder_wd=0.01,
    stratify_cap_per_bucket=3, tier_bc_cap=20,
)
SEED = 20260728


def _log(msg):
    print("[eval_battery_v7] %s" % msg, flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _pair_rank(subj_surf, obj_surf):
    h = hashlib.sha256((PAIR_SPLIT_SALT + subj_surf + "|" + obj_surf).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / float(2 ** 64)


# ===========================================================================
# STAGE 1: universe / split / postings / typed edges (reuses V2 + v6 exactly)
# ===========================================================================
def build_bundle(cfg):
    t_stage = {}
    t0 = time.perf_counter()
    universe = V2.load_concept_universe(cfg)
    t_stage["universe_s"] = time.perf_counter() - t0
    _log("universe K=%d (%.1fs)" % (universe["K"], t_stage["universe_s"]))

    t0 = time.perf_counter()
    counts, corpus_stats = V2.count_pass(cfg, universe["surf_to_idx"])
    t_stage["count_pass_s"] = time.perf_counter() - t0
    _log("count_pass done (%.1fs) kept=%d" % (t_stage["count_pass_s"], corpus_stats["n_kept"]))

    t0 = time.perf_counter()
    split = V2.build_split(universe, counts, cfg)
    t_stage["split_s"] = time.perf_counter() - t0
    _log("split heldout=%d train_eval=%d" % (len(split["held_idx"]), len(split["train_eval_idx"])))

    t0 = time.perf_counter()
    postings, _bpe_lines, collect_meta = V2.collect_pass(cfg, universe, split)
    t_stage["collect_pass_s"] = time.perf_counter() - t0
    _log("collect_pass done (%.1fs) train_lines=%d held_lines=%d"
         % (t_stage["collect_pass_s"], collect_meta["n_train_lines"], collect_meta["n_held_lines"]))

    t0 = time.perf_counter()
    shard_paths = sorted(glob.glob(V2.EDGES_GLOB))[:cfg["max_shards"]]
    edges = _load_typed_edges(shard_paths, universe["surf_to_idx"])
    t_stage["edges_s"] = time.perf_counter() - t0
    _log("typed edges=%d from %d shards (%.1fs)" % (len(edges), len(shard_paths), t_stage["edges_s"]))

    return dict(universe=universe, counts=counts, corpus_stats=corpus_stats, split=split,
                postings=postings, collect_meta=collect_meta, edges=edges,
                n_shards=len(shard_paths), t_stage=t_stage)


# ===========================================================================
# STAGE 2: pick Tier-C relation + relation label space + train/tierB/tierC/tierA
# instance construction. Leak-proofing is enforced by construction + asserted below.
# ===========================================================================
def _pick_tier_c_relation(edges, is_held, cfg, rng_tiebreak_seed):
    """Deterministic: among relations whose (both-endpoints-non-held) count sits in
    [tier_c_count_lo, tier_c_count_hi] (mid-frequency -- not the dominant relation, not too rare
    to get eval power), pick the one closest to the geometric mid of that band; ties broken
    alphabetically for full determinism (no RNG actually needed, kept as a documented arg for
    clarity)."""
    del rng_tiebreak_seed
    cnt = Counter()
    for (si, rel, oi) in edges:
        if not is_held[si] and not is_held[oi]:
            cnt[rel] += 1
    target = (cfg["tier_c_count_lo"] * cfg["tier_c_count_hi"]) ** 0.5
    cands = sorted([r for r, c in cnt.items() if cfg["tier_c_count_lo"] <= c <= cfg["tier_c_count_hi"]],
                    key=lambda r: (abs(cnt[r] - target), r))
    if not cands:
        return None, cnt
    return cands[0], cnt


def build_dataset(bundle, cfg):
    universe, split, postings, edges = bundle["universe"], bundle["split"], bundle["postings"], bundle["edges"]
    surfaces = universe["surfaces"]
    is_held = split["is_held"]

    tier_c_rel, both_nonheld_counts = _pick_tier_c_relation(edges, is_held, cfg, SEED)
    if tier_c_rel is None:
        raise RuntimeError("no candidate Tier-C relation in count band [%d,%d] -- widen band or "
                            "regime too small" % (cfg["tier_c_count_lo"], cfg["tier_c_count_hi"]))
    _log("tier_c_relation=%s (both-non-held count=%d)" % (tier_c_rel, both_nonheld_counts[tier_c_rel]))

    kept_rel = sorted([r for r, c in both_nonheld_counts.items() if c >= cfg["min_train_per_rel"]],
                       key=lambda r: (-both_nonheld_counts[r], r))[:cfg["top_n_relations"]]
    if tier_c_rel not in kept_rel:
        kept_rel = kept_rel[:-1] + [tier_c_rel] if len(kept_rel) >= cfg["top_n_relations"] else kept_rel + [tier_c_rel]
    label_relations = sorted(kept_rel)
    trainable_relations = [r for r in label_relations if r != tier_c_rel]
    rel_to_idx = {r: i for i, r in enumerate(label_relations)}
    if len(trainable_relations) < 2:
        raise RuntimeError("fewer than 2 trainable relations (%d) after Tier-C exclusion"
                            % len(trainable_relations))

    # pair-withhold set (Tier B split axis): rank ALL both-endpoint-non-held pairs by sha256; the
    # LOWEST pair_withhold_frac fraction by rank is reserved for Tier B (never in TRAIN).
    nonheld_pairs = sorted(set((si, oi) for (si, rel, oi) in edges
                                if not is_held[si] and not is_held[oi] and rel in trainable_relations))
    ranked_pairs = sorted(nonheld_pairs, key=lambda p: _pair_rank(surfaces[p[0]], surfaces[p[1]]))
    n_withhold = int(len(ranked_pairs) * cfg["pair_withhold_frac"])
    tier_b_pairs = set(ranked_pairs[:n_withhold])

    def _instances(edge_iter, cap_per_edge, dedupe_seen=None):
        out = []
        for (si, rel, oi) in edge_iter:
            ri = rel_to_idx.get(rel)
            if ri is None:
                continue
            sents = _find_cooccurring_sentences(postings, si, surfaces[oi], cap_per_edge)
            if not sents:
                continue
            for s in sents:
                out.append((si, ri, oi, s))
        return out

    train_edges = [(si, rel, oi) for (si, rel, oi) in edges
                   if rel in trainable_relations and not is_held[si] and not is_held[oi]
                   and (si, oi) not in tier_b_pairs]
    tier_a_edges = [(si, rel, oi) for (si, rel, oi) in edges
                    if rel in trainable_relations and is_held[si]]
    tier_b_edges = [(si, rel, oi) for (si, rel, oi) in edges
                    if rel in trainable_relations and not is_held[si] and not is_held[oi]
                    and (si, oi) in tier_b_pairs]
    tier_c_edges = [(si, rel, oi) for (si, rel, oi) in edges
                    if rel == tier_c_rel and not is_held[si] and not is_held[oi]]

    train_instances = _instances(train_edges, cfg["max_sent_per_edge"])
    tier_a_instances = _instances(tier_a_edges, cfg["max_sent_per_edge"])
    tier_b_instances = _instances(tier_b_edges, cfg["max_sent_per_edge"])
    tier_c_instances = _instances(tier_c_edges, cfg["max_sent_per_edge"])

    # LEAK-PROOF ASSERTIONS (by construction, re-verified at runtime -- mirrors the diag script's
    # build_train_pairs leak-check pattern).
    train_subjects = set(si for (si, _ri, _oi, _s) in train_instances)
    train_pairs = set((si, oi) for (si, _ri, oi, _s) in train_instances)
    tier_a_subjects = set(si for (si, _ri, _oi, _s) in tier_a_instances)
    assert train_subjects.isdisjoint(tier_a_subjects), "LEAK: a Tier-A held subject appears in TRAIN"
    tier_b_pairs_used = set((si, oi) for (si, _ri, oi, _s) in tier_b_instances)
    assert train_pairs.isdisjoint(tier_b_pairs_used), "LEAK: a Tier-B withheld pair appears in TRAIN"
    train_relations_seen = set(r for (_si, r, _oi, _s) in train_instances)
    assert tier_c_rel not in set(label_relations[i] for i in
                                  set(ri for (_si, ri, _oi, _s) in train_instances)), \
        "LEAK: Tier-C relation has TRAIN instances"

    b0_table, b0_global_majority = _build_b0_table(train_instances, label_relations)

    return dict(
        label_relations=label_relations, trainable_relations=trainable_relations,
        rel_to_idx=rel_to_idx, tier_c_relation=tier_c_rel,
        train_instances=train_instances, tier_a_instances=tier_a_instances,
        tier_b_instances=tier_b_instances, tier_c_instances=tier_c_instances,
        n_pair_withhold=len(tier_b_pairs), n_pair_pool=len(ranked_pairs),
        b0_table=b0_table, b0_global_majority=b0_global_majority,
        n_edges_total=len(edges),
    )


def _build_b0_table(train_instances, label_relations):
    """Per-object relation Counter from TRAIN instances only (v6._b0_table lineage, generalized
    to return the FULL ranking not just argmax, since v7 needs per-object rank-of-true)."""
    obj_rel_counts = defaultdict(Counter)
    global_counts = Counter()
    for (_si, ri, oi, _s) in train_instances:
        obj_rel_counts[oi][ri] += 1
        global_counts[ri] += 1
    global_majority = global_counts.most_common(1)[0][0] if global_counts else 0
    return dict(obj_rel_counts), global_majority


# ===========================================================================
# STAGE 3: adversarial K-way pool construction + rank-of-true (the ruler fix, Section 3)
# ===========================================================================
def _relation_ranking_for_object(b0_table, global_majority, oi, n_labels):
    """Full ranking of label-relation indices for object oi, desc by TRAIN count, ties broken by
    relation index (deterministic). Objects never seen in TRAIN fall back to a single global-
    majority-first ordering (matches v6's _b0_pred fallback semantics)."""
    counts = b0_table.get(oi)
    if counts is None:
        order = [global_majority] + [r for r in range(n_labels) if r != global_majority]
        return order, False
    scored = [(counts.get(r, 0), r) for r in range(n_labels)]
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [r for (_c, r) in scored], True


def build_pool_for_item(b0_table, global_majority, oi, true_ri, n_labels, K):
    ranking, has_signal = _relation_ranking_for_object(b0_table, global_majority, oi, n_labels)
    rank_of_true = ranking.index(true_ri) + 1  # 1-indexed
    pool = list(ranking[:K])
    injected = False
    if true_ri not in pool:
        pool[-1] = true_ri
        injected = True
    b0_pred = pool[0]  # ranking is desc by count, and true was only ever swapped into the LAST slot
    return dict(pool=pool, rank_of_true=rank_of_true, injected=injected, b0_pred=b0_pred,
                has_train_signal=has_signal)


def annotate_items(instances, dataset, K):
    n_labels = len(dataset["label_relations"])
    out = []
    for (si, ri, oi, s) in instances:
        pdat = build_pool_for_item(dataset["b0_table"], dataset["b0_global_majority"], oi, ri, n_labels, K)
        out.append(dict(si=si, ri=ri, oi=oi, sent=s, **pdat))
    return out


def stratify_balanced(items, K, cap_per_bucket, seed):
    """Force B0's identity-only accuracy to ~1/K BY CONSTRUCTION (Section 3 fix, corrected).

    B0 always picks the pool's rank-1 relation (the object's own highest train-count relation), so
    B0 accuracy == fraction of items whose true relation is rank-1 for that object (frac_rank1).
    A prior version bucketed by min(rank,K) and CAPPED every bucket at a constant -- that does NOT
    balance when the real data is rank-skewed (CSKG is majority-relation-skewed per object, so the
    rank-1 bucket dominates and survives capping). The correct construction targets frac_rank1 =
    1/K directly: KEEP ALL rank>=2 items (the ones that require reading the sentence), and
    DOWNSAMPLE the rank-1 items to n_others/(K-1) so rank-1 is exactly a 1/K share of the total.
    Then B0 = n_rank1_kept / (n_rank1_kept + n_others) -> 1/K. If rank-1 items are already scarce
    (< target), keep them all (B0 lands at or below 1/K, still near chance). cap_per_bucket bounds
    the rank>=2 tail for runtime (rarely binding at this scale)."""
    rng = np.random.default_rng(seed)
    rank1 = [it for it in items if it["rank_of_true"] == 1]
    others = [it for it in items if it["rank_of_true"] >= 2]
    # bound the rank>=2 tail per within-pool position bucket (min(rank,K)) for runtime only
    other_buckets = defaultdict(list)
    for it in others:
        other_buckets[min(it["rank_of_true"], K)].append(it)
    others_kept = []
    for b in sorted(other_buckets):
        lst = other_buckets[b]
        if cap_per_bucket is not None and len(lst) > cap_per_bucket:
            idx = rng.choice(len(lst), size=cap_per_bucket, replace=False)
            lst = [lst[i] for i in sorted(idx.tolist())]
        others_kept.extend(lst)
    n_others = len(others_kept)
    target_rank1 = int(round(n_others / max(1, (K - 1)))) if n_others > 0 else 0
    rank1_kept = rank1
    if len(rank1) > target_rank1:
        idx = rng.choice(len(rank1), size=target_rank1, replace=False)
        rank1_kept = [rank1[i] for i in sorted(idx.tolist())]
    out = rank1_kept + others_kept
    rng.shuffle(out)
    raw_by_bucket = defaultdict(int)
    kept_by_bucket = defaultdict(int)
    for it in items:
        raw_by_bucket[min(it["rank_of_true"], K)] += 1
    for it in out:
        kept_by_bucket[min(it["rank_of_true"], K)] += 1
    meta = dict(bucket_sizes_raw={int(k): int(v) for k, v in sorted(raw_by_bucket.items())},
                bucket_sizes_kept={int(k): int(v) for k, v in sorted(kept_by_bucket.items())},
                n_rank1_available=len(rank1), n_rank1_kept=len(rank1_kept),
                n_rank_ge2_kept=n_others, target_rank1=target_rank1,
                implied_b0=(len(rank1_kept) / len(out)) if out else None,
                n_buckets_present=len(raw_by_bucket))
    return out, meta


# ===========================================================================
# STAGE 4: signal path -- sentence gestalt (fixed content-addressed readout, zero training) +
# a small leak-proof learned linear decoder fit ONLY on cached TRAIN gestalts.
# ===========================================================================
def compute_gestalts(model, tok, spec, sents, cfg, readout, device):
    if not sents:
        return np.zeros((0, readout.role_proj.out_features if readout.mode == "learned"
                          else model.d_model), dtype=np.float32)
    idcache = _cache_ids_for_sentences(tok, sents, cfg, spec)
    ids_np = np.stack([idcache[s] for s in sents], axis=0)
    bs = cfg["encode_batch"]
    out = []
    for i in range(0, ids_np.shape[0], bs):
        ids = torch.from_numpy(ids_np[i:i + bs]).to(device)
        h, pad_mask = _frozen_hidden(model, ids)
        with torch.no_grad():
            g = readout(h, pad_mask)
        out.append(g.cpu().numpy())
    return np.concatenate(out, axis=0).astype(np.float32)


def fit_linear_decoder(G_train, y_train, n_labels, steps, lr, wd, seed):
    """DECODER-COLLAPSE FIX (2026-07-28, diag_comprehension_readout_sweep_v1 shotgun): plain CE on
    v7's skewed TRAIN label distribution (one relation ~65-66% of items at this regime) collapses
    the fit to always-predict-majority -- LEARNED_DECODER(coherent) == LEARNED_DECODER(scrambled)
    == MAJORITY_KWAY exactly, so comprehension_specific reads False BY ARTIFACT (the decoder never
    learned per-class structure at all, so it obviously can't tell coherent from scrambled). Fix:
    inverse-class-frequency CE weighting (identical formula to the shotgun's
    fit_linear_decoder_weighted) so the decoder cannot minimize loss by collapsing to the prior.
    See _train_fit_sanity for the paired validity gate (train balanced_acc must clear chance)."""
    torch.manual_seed(seed)
    d = G_train.shape[1]
    lin = nn.Linear(d, n_labels)
    opt = torch.optim.Adam(lin.parameters(), lr=lr, weight_decay=wd)
    X = torch.from_numpy(G_train).float()
    y = torch.from_numpy(y_train).long()
    counts = torch.clamp(torch.bincount(y, minlength=n_labels).float(), min=1.0)
    class_weight = counts.sum() / (n_labels * counts)
    last_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        logits = lin(X)
        loss = F.cross_entropy(logits, y, weight=class_weight)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("LEARNED_DECODER training diverged (non-finite loss)")
    return lin, last_loss


def _train_fit_sanity(lin_decoder, G_train, y_train, n_labels, margin=0.10):
    """VALIDITY GATE (2026-07-28): does the fitted decoder actually discriminate classes on its OWN
    TRAIN fit, better than chance? Balanced accuracy (mean per-class recall) is the correct check
    under class-weighted CE -- raw train_acc is the WRONG gate once weighting is on, because
    balancing deliberately trades raw accuracy for per-class recall on a skewed label set (post-
    balancing train_acc can sit BELOW the majority-class rate even when the decoder has genuinely
    learned per-class structure). A collapsed fit gives balanced_acc ~= chance regardless of
    train_acc; a working fit clears it by construction. If this gate fails, the run must FLAG
    'decoder underfit' rather than silently report a null comprehension_specific verdict."""
    with torch.no_grad():
        pred = lin_decoder(torch.from_numpy(G_train).float()).numpy().argmax(axis=1)
    train_acc = float((pred == y_train).mean())
    recalls = []
    for c in range(n_labels):
        mask = (y_train == c)
        if mask.sum() > 0:
            recalls.append(float((pred[mask] == c).mean()))
    balanced_acc = float(np.mean(recalls)) if recalls else 0.0
    chance = 1.0 / n_labels
    return dict(train_acc=train_acc, balanced_acc=balanced_acc, chance=chance,
                decoder_valid=bool(balanced_acc >= chance + margin))


def relation_centroids(G_train, y_train, n_labels):
    d = G_train.shape[1]
    cent = np.zeros((n_labels, d), dtype=np.float32)
    for r in range(n_labels):
        mask = (y_train == r)
        if mask.sum() > 0:
            v = G_train[mask].mean(axis=0)
            nrm = np.linalg.norm(v)
            cent[r] = v / (nrm + 1e-8) if nrm > 1e-8 else v
    return cent


# ===========================================================================
# STAGE 5: K-way forced-choice scoring per arm
# ===========================================================================
def score_pool_arms(items, G, G_scrambled, lin_decoder, centroids, label_relations):
    """Returns per-arm accuracy over `items` (list of annotated dicts, `G`/`G_scrambled` aligned
    row-for-row with `items`)."""
    n = len(items)
    if n == 0:
        return dict(n=0)
    with torch.no_grad():
        dec_logits = lin_decoder(torch.from_numpy(G).float()).numpy()
        dec_logits_scr = lin_decoder(torch.from_numpy(G_scrambled).float()).numpy() if G_scrambled is not None else None
    correct = dict(B0_KWAY=0, MAJORITY_KWAY=0, COSINE_CENTROID=0, LEARNED_DECODER=0,
                   COSINE_CENTROID_SCRAMBLED=0, LEARNED_DECODER_SCRAMBLED=0)
    ranks_seen = []
    for k, it in enumerate(items):
        pool = it["pool"]
        ranks_seen.append(it["rank_of_true"])
        correct["B0_KWAY"] += int(it["b0_pred"] == it["ri"])
        # majority-kway: pick the globally-most-frequent relation IN the pool (fixed table, no
        # per-object signal at all -- a strictly weaker baseline than B0_KWAY).
        gm = it.get("_global_majority_in_pool")
        correct["MAJORITY_KWAY"] += int(gm == it["ri"]) if gm is not None else 0
        pool_arr = np.array(pool, dtype=np.int64)
        cos_scores = centroids[pool_arr] @ G[k]
        cos_pred = pool[int(np.argmax(cos_scores))]
        correct["COSINE_CENTROID"] += int(cos_pred == it["ri"])
        dec_scores = dec_logits[k][pool_arr]
        dec_pred = pool[int(np.argmax(dec_scores))]
        correct["LEARNED_DECODER"] += int(dec_pred == it["ri"])
        if G_scrambled is not None:
            cos_scores_s = centroids[pool_arr] @ G_scrambled[k]
            cos_pred_s = pool[int(np.argmax(cos_scores_s))]
            correct["COSINE_CENTROID_SCRAMBLED"] += int(cos_pred_s == it["ri"])
            dec_scores_s = dec_logits_scr[k][pool_arr]
            dec_pred_s = pool[int(np.argmax(dec_scores_s))]
            correct["LEARNED_DECODER_SCRAMBLED"] += int(dec_pred_s == it["ri"])
    res = {k: (v / n) for k, v in correct.items()}
    res["n"] = n
    res["mean_rank_of_true"] = float(np.mean(ranks_seen))
    res["frac_rank1"] = float(np.mean([r == 1 for r in ranks_seen]))
    return res


# ===========================================================================
# MAIN ORCHESTRATION -- one call, callable again for any future ckpt/variant
# ===========================================================================
def run_battery(ckpt_path=CKPT_PATH, cfg=None, seed=SEED, out_dir=OUT_DIR, write_output=True):
    cfg = dict(cfg or FULL_CFG)
    t_wall0 = time.perf_counter()
    os.makedirs(out_dir, exist_ok=True)
    _log("device=cpu ckpt=%s" % ckpt_path)

    model, tok, spec, ckpt_meta = load_frozen_encoder(ckpt_path)
    bundle = build_bundle(cfg)
    dataset = build_dataset(bundle, cfg)
    n_labels = len(dataset["label_relations"])
    K = min(cfg["K"], n_labels)
    _log("label_relations=%d trainable=%d tier_c=%s K=%d"
         % (n_labels, len(dataset["trainable_relations"]), dataset["tier_c_relation"], K))
    _log("instances: train=%d tierA=%d tierB=%d tierC=%d (pair_pool=%d withheld=%d)"
         % (len(dataset["train_instances"]), len(dataset["tier_a_instances"]),
            len(dataset["tier_b_instances"]), len(dataset["tier_c_instances"]),
            dataset["n_pair_pool"], dataset["n_pair_withhold"]))

    global_majority_rel = dataset["b0_global_majority"]

    tier_a_items = annotate_items(dataset["tier_a_instances"], dataset, K)
    for it in tier_a_items:
        it["_global_majority_in_pool"] = global_majority_rel if global_majority_rel in it["pool"] else None
    tier_a_bal, tier_a_strat_meta = stratify_balanced(tier_a_items, K, cfg["stratify_cap_per_bucket"], seed + 601)
    _log("TIER A stratified: %s" % tier_a_strat_meta)

    def _annot_cap(instances, cap, seed_off):
        items = annotate_items(instances, dataset, K)
        for it in items:
            it["_global_majority_in_pool"] = global_majority_rel if global_majority_rel in it["pool"] else None
        if len(items) > cap:
            rng = np.random.default_rng(seed + seed_off)
            idx = sorted(rng.choice(len(items), size=cap, replace=False).tolist())
            items = [items[i] for i in idx]
        return items

    tier_b_items = _annot_cap(dataset["tier_b_instances"], cfg["tier_bc_cap"], 701)
    tier_c_items = _annot_cap(dataset["tier_c_instances"], cfg["tier_bc_cap"], 801)

    # scramble control sentences (concept-pair-preserving; same multiset, order destroyed)
    srng = np.random.default_rng(seed + 202)

    def _scr(items):
        return [LOOP2._scramble_words(it["sent"], srng) for it in items]

    device = torch.device("cpu")
    readout = ContentRoleReadout(model.d_model, mode="fixed", seed=seed)

    train_sents = [s for (_si, _ri, _oi, s) in dataset["train_instances"]]
    train_y = np.array([ri for (_si, ri, _oi, _s) in dataset["train_instances"]], dtype=np.int64)
    t0 = time.perf_counter()
    G_train = compute_gestalts(model, tok, spec, train_sents, cfg, readout, device)
    t_encode_train = time.perf_counter() - t0
    _log("train gestalts computed n=%d (%.1fs)" % (G_train.shape[0], t_encode_train))
    if G_train.shape[0] < 20:
        raise RuntimeError("too few TRAIN gestalts (%d) to fit a decoder -- widen regime" % G_train.shape[0])

    t0 = time.perf_counter()
    lin_decoder, decoder_final_loss = fit_linear_decoder(
        G_train, train_y, n_labels, cfg["decoder_steps"], cfg["decoder_lr"], cfg["decoder_wd"], seed)
    t_fit = time.perf_counter() - t0
    decoder_sanity = _train_fit_sanity(lin_decoder, G_train, train_y, n_labels)
    _log("LEARNED_DECODER fit done (%.1fs) final_ce=%.4f sanity=%s"
         % (t_fit, decoder_final_loss, decoder_sanity))
    centroids = relation_centroids(G_train, train_y, n_labels)

    def _score_tier(name, items):
        sents = [it["sent"] for it in items]
        scr_sents = _scr(items)
        G = compute_gestalts(model, tok, spec, sents, cfg, readout, device)
        G_scr = compute_gestalts(model, tok, spec, scr_sents, cfg, readout, device)
        res = score_pool_arms(items, G, G_scr, lin_decoder, centroids, dataset["label_relations"])
        _log("%s: %s" % (name, {k: v for k, v in res.items() if k != "n" or True}))
        return res

    tier_a_res = _score_tier("TIER_A (balanced)", tier_a_bal)
    tier_a_rank1_only = [it for it in tier_a_bal if it["rank_of_true"] == 1]
    tier_a_rank_ge2 = [it for it in tier_a_bal if it["rank_of_true"] >= 2]
    wrong_dominant_res = _score_tier("TIER_A wrong-dominant-relation slice (rank>=2)", tier_a_rank_ge2)
    tier_b_res = _score_tier("TIER_B (new concept-pair)", tier_b_items)
    tier_c_res = _score_tier("TIER_C (new relation-type)", tier_c_items)

    chance = 1.0 / K
    verdict_block = build_verdict(tier_a_res, wrong_dominant_res, chance, cfg, decoder_sanity)

    payload = dict(
        anchor_name=ANCHOR_NAME, ts_iso=_now(), pid=os.getpid(),
        ckpt_path=ckpt_path, ckpt_meta=ckpt_meta, cfg=cfg, seed=seed,
        corpus_stats=bundle["corpus_stats"], split_meta=bundle["split"]["split_meta"],
        collect_meta=bundle["collect_meta"], t_stage=bundle["t_stage"],
        K=K, n_labels=n_labels, label_relations=dataset["label_relations"],
        trainable_relations=dataset["trainable_relations"], tier_c_relation=dataset["tier_c_relation"],
        n_instances=dict(train=len(dataset["train_instances"]), tier_a_raw=len(tier_a_items),
                         tier_a_balanced=len(tier_a_bal), tier_b=len(tier_b_items), tier_c=len(tier_c_items)),
        tier_a_strat_meta=tier_a_strat_meta,
        decoder_fit=dict(t_encode_train_s=t_encode_train, t_fit_s=t_fit, final_ce=decoder_final_loss,
                          train_fit_sanity=decoder_sanity),
        chance_1_over_k=chance,
        tier_a=tier_a_res, tier_a_rank1_only_n=len(tier_a_rank1_only),
        wrong_dominant_slice=wrong_dominant_res,
        tier_b=tier_b_res, tier_c=tier_c_res,
        verdict=verdict_block["verdict"], verdict_msg=verdict_block["verdict_msg"],
        verdict_detail=verdict_block,
        note_caveat=("Reduced-scale harness (cap_eval_concepts=%s, max_lines=%s) for CPU-minutes "
                     "turnaround; this is a diagnostic/instrument-validation run, not a capability-"
                     "scale claim. Tier B/C are capped at %d items and may be underpowered -- see "
                     "n_instances. LEARNED_DECODER uses a FIXED (untrained) content-addressed "
                     "readout + a small trained linear head fit ONLY on cached TRAIN gestalts; it "
                     "is a linear probe (stronger than cosine, weaker than a full nonlinear "
                     "readout), matching tonight's diag_readout_limit_probe_v1 finding."
                     % (cfg["cap_eval_concepts"], cfg["max_lines"], cfg["tier_bc_cap"])),
        elapsed_s_total=time.perf_counter() - t_wall0,
    )
    if write_output:
        tmp = os.path.join(out_dir, "results.json.tmp")
        final = os.path.join(out_dir, "results.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        os.replace(tmp, final)
        _log("wrote %s (elapsed %.1fs)" % (final, payload["elapsed_s_total"]))
    return payload


def build_verdict(tier_a_res, wrong_dominant_res, chance, cfg, decoder_sanity):
    """THE META-VALIDATION: does the adversarial + stratified construction actually drop B0 to
    ~1/K? Report honestly either way -- a broken ruler must be reported broken, not shipped.

    DECODER-VALIDITY GATE (2026-07-28): decoder_sanity (from _train_fit_sanity, TRAIN balanced_acc
    vs chance=1/n_labels) is a HARD PRECONDITION for trusting comprehension_specific. A decoder
    that collapsed to the majority class on its own TRAIN fit cannot possibly carry a real
    coherent-vs-scrambled signal -- reporting comprehension_specific=False from a collapsed fit is
    the exact artifact this gate exists to catch. If decoder_valid is False, comprehension_specific
    is forced to None (not measured, not "False") and the verdict is DECODER_UNDERFIT."""
    b0 = tier_a_res.get("B0_KWAY")
    n = tier_a_res.get("n", 0)
    tol = 0.10  # sampling slack around 1/K
    ruler_valid_b0_near_chance = bool(b0 is not None and abs(b0 - chance) <= tol)
    ruler_valid_b0_far_from_old_075 = bool(b0 is not None and b0 < 0.45)
    scramble_near_chance = bool(
        tier_a_res.get("COSINE_CENTROID_SCRAMBLED") is not None
        and abs(tier_a_res["COSINE_CENTROID_SCRAMBLED"] - chance) <= 0.20)
    majority_near_chance = bool(
        tier_a_res.get("MAJORITY_KWAY") is not None and tier_a_res["MAJORITY_KWAY"] <= chance + tol)
    decoder_above_chance = bool(
        tier_a_res.get("LEARNED_DECODER") is not None
        and tier_a_res["LEARNED_DECODER"] >= chance + 0.05)
    cosine_above_chance = bool(
        tier_a_res.get("COSINE_CENTROID") is not None
        and tier_a_res["COSINE_CENTROID"] >= chance + 0.05)
    signal_path_solvable = bool(decoder_above_chance or cosine_above_chance)
    wrong_dominant_b0_zero = bool(wrong_dominant_res.get("B0_KWAY") == 0.0) if wrong_dominant_res.get("n", 0) > 0 else None

    decoder_valid = bool(decoder_sanity.get("decoder_valid", False))
    decoder_margin = None
    if (tier_a_res.get("LEARNED_DECODER") is not None
            and tier_a_res.get("LEARNED_DECODER_SCRAMBLED") is not None):
        decoder_margin = tier_a_res["LEARNED_DECODER"] - tier_a_res["LEARNED_DECODER_SCRAMBLED"]
    comprehension_specific = (bool(decoder_margin is not None and decoder_margin >= 0.03)
                               if decoder_valid else None)

    ruler_ok = bool(ruler_valid_b0_near_chance and ruler_valid_b0_far_from_old_075 and n >= 20)
    if not decoder_valid:
        verdict = "DECODER_UNDERFIT"
    elif ruler_ok and signal_path_solvable:
        verdict = "RULER_VALID_AND_SOLVABLE"
    elif ruler_ok and not signal_path_solvable:
        verdict = "RULER_VALID_BUT_TASK_TOO_HARD"
    elif not ruler_ok and n < 20:
        verdict = "UNDERPOWERED"
    else:
        verdict = "RULER_STILL_BROKEN"
    msg = ("v7 ruler-check: b0_kway=%.3f (chance=%.3f, tol=%.2f) n=%d near_chance=%s "
           "far_from_old_0.754=%s scramble_near_chance=%s majority_near_chance=%s "
           "decoder_acc=%s cosine_acc=%s signal_path_solvable=%s wrong_dominant_b0=%s "
           "decoder_valid=%s (balanced_acc=%.3f vs chance=%.3f) decoder_margin=%s "
           "comprehension_specific=%s -> %s"
           % (b0 if b0 is not None else -1, chance, tol, n, ruler_valid_b0_near_chance,
              ruler_valid_b0_far_from_old_075, scramble_near_chance, majority_near_chance,
              tier_a_res.get("LEARNED_DECODER"), tier_a_res.get("COSINE_CENTROID"),
              signal_path_solvable, wrong_dominant_b0_zero, decoder_valid,
              decoder_sanity.get("balanced_acc", -1), decoder_sanity.get("chance", -1),
              decoder_margin, comprehension_specific, verdict))
    return dict(verdict=verdict, verdict_msg=msg,
                ruler_valid_b0_near_chance=ruler_valid_b0_near_chance,
                ruler_valid_b0_far_from_old_075=ruler_valid_b0_far_from_old_075,
                scramble_near_chance=scramble_near_chance, majority_near_chance=majority_near_chance,
                decoder_above_chance=decoder_above_chance, cosine_above_chance=cosine_above_chance,
                signal_path_solvable=signal_path_solvable, wrong_dominant_b0_zero=wrong_dominant_b0_zero,
                decoder_valid=decoder_valid, decoder_sanity=decoder_sanity, decoder_margin=decoder_margin,
                comprehension_specific=comprehension_specific, n_tier_a=n)


def _selftest_decoder_validity_gate():
    """CAN-FAIL gate for the 2026-07-28 decoder-collapse fix itself: does _train_fit_sanity
    correctly FLAG a deliberately-collapsed fit as invalid, AND correctly PASS a genuinely-fit
    decoder on the same class-skew? Two halves:

    (a) COLLAPSED: a stub 'decoder' that always predicts the majority class regardless of input
        (mirrors the exact plain-CE collapse the shotgun caught) on a skewed 4-class TRAIN set
        (200/20/20/20). Per-class recall = (1.0, 0, 0, 0) -> balanced_acc == chance == 0.25 exactly
        -- decoder_valid MUST be False.
    (b) WORKING: fit_linear_decoder (the FIXED, class-weighted version) on the SAME class-skewed
        label vector but with perfectly-separable one-hot features (trivial for any correct
        optimizer to solve) -- decoder_valid MUST be True with balanced_acc >> chance.

    If either half fails, the fix (or the gate itself) is broken independent of any real model."""
    n_labels = 4
    rng = np.random.default_rng(5)
    y = np.array([0] * 200 + [1] * 20 + [2] * 20 + [3] * 20, dtype=np.int64)
    perm = rng.permutation(len(y))
    y = y[perm]

    class _CollapsedStub:
        """Callable mimicking nn.Linear's __call__ signature; always emits majority-class logits."""
        def __call__(self, X):
            n = X.shape[0]
            logits = torch.zeros(n, n_labels)
            logits[:, 0] = 10.0
            return logits

    collapsed_sanity = _train_fit_sanity(_CollapsedStub(), np.zeros((len(y), 2), dtype=np.float32),
                                          y, n_labels)
    assert abs(collapsed_sanity["balanced_acc"] - 0.25) <= 1e-6, (
        "DECODER-GATE SELF-TEST: collapsed-stub balanced_acc=%.4f != chance=0.25 exactly "
        "(gate math itself is wrong)" % collapsed_sanity["balanced_acc"])
    assert collapsed_sanity["decoder_valid"] is False, (
        "DECODER-GATE SELF-TEST FAILED: gate did NOT flag a deliberately-collapsed (always-"
        "majority) fit as invalid -- balanced_acc=%.4f chance=%.4f" % (
            collapsed_sanity["balanced_acc"], collapsed_sanity["chance"]))

    G_onehot = np.eye(n_labels, dtype=np.float32)[y]
    lin, _loss = fit_linear_decoder(G_onehot, y, n_labels, steps=200, lr=0.1, wd=0.0, seed=3)
    working_sanity = _train_fit_sanity(lin, G_onehot, y, n_labels)
    assert working_sanity["decoder_valid"] is True, (
        "DECODER-GATE SELF-TEST FAILED: gate did NOT pass a genuinely-fit decoder on trivially-"
        "separable (one-hot) features -- balanced_acc=%.4f chance=%.4f (fix may have broken "
        "fit_linear_decoder's ability to learn at all)" % (
            working_sanity["balanced_acc"], working_sanity["chance"]))
    return dict(collapsed=collapsed_sanity, working=working_sanity)


# ===========================================================================
# SELF-TEST -- exercises the REAL functions (F.1: real_code_path) at tiny N + a synthetic
# stratified-bucket math check that proves the CONSTRUCTION forces chance independent of any
# real model (the harness-math must be right regardless of what the encoder does).
# ===========================================================================
def _selftest_stratified_bucket_math():
    """Synthetic, RANK-SKEWED (mirrors real CSKG skew so it actually validates the fix, not an
    artificially-balanced toy): object 0 has fixed B0 ranking r0>r1>r2>r3. We build a heavily
    rank-1-DOMINATED item set (200 rank-1, 20 rank-2, 5 rank-3, 40 rank-4) -- exactly the shape
    that broke the prior capped stratifier. After the corrected stratify_balanced, B0's identity-
    only accuracy (== frac_rank1) must land at ~1/K, because rank-1 is downsampled to a 1/K share
    of the kept total. This is the CAN-FAIL ruler-math gate: if it doesn't drop to ~1/K on skewed
    data, the ruler is broken regardless of any real model."""
    n_labels = 4
    K = 4
    b0_table = {0: Counter({0: 100, 1: 50, 2: 10, 3: 1})}
    global_majority = 0
    counts_by_rank = {1: 200, 2: 20, 3: 5, 4: 40}   # deliberately skewed toward rank-1
    items = []
    for true_ri, nn in ((0, counts_by_rank[1]), (1, counts_by_rank[2]),
                        (2, counts_by_rank[3]), (3, counts_by_rank[4])):
        for _ in range(nn):
            items.append(dict(si=0, ri=true_ri, oi=0, sent="x"))
    annotated = []
    for it in items:
        pdat = build_pool_for_item(b0_table, global_majority, it["oi"], it["ri"], n_labels, K)
        annotated.append(dict(**it, **pdat))
    bal, meta = stratify_balanced(annotated, K, cap_per_bucket=None, seed=1)
    b0_correct = sum(1 for it in bal if it["b0_pred"] == it["ri"])
    b0_acc = b0_correct / len(bal)
    # on skewed data, rank>=2 total = 65, target_rank1 = round(65/3) = 22, so B0 = 22/87 = 0.253
    assert abs(b0_acc - 1.0 / K) <= 0.03, (
        "RULER-MATH SELF-TEST FAILED: balanced-stratified B0 accuracy=%.4f not within 0.03 of "
        "1/K=%.4f on RANK-SKEWED data -- the construction itself is broken, independent of any "
        "real model (meta=%s)" % (b0_acc, 1.0 / K, meta))
    return b0_acc


def self_test():
    t0 = time.perf_counter()
    torch.manual_seed(7)
    np.random.seed(7)

    b0_acc = _selftest_stratified_bucket_math()
    _log("SELFTEST bucket-math: balanced B0_KWAY acc=%.4f (expected exactly 1/K; this construction "
         "is what keeps B0/memorization-proofness near chance and is UNCHANGED by the 2026-07-28 "
         "decoder fix -- B0_KWAY never touches the decoder)" % b0_acc)

    gate_res = _selftest_decoder_validity_gate()
    _log("SELFTEST decoder-validity-gate: collapsed balanced_acc=%.4f (valid=%s, expect False), "
         "working balanced_acc=%.4f (valid=%s, expect True)"
         % (gate_res["collapsed"]["balanced_acc"], gate_res["collapsed"]["decoder_valid"],
            gate_res["working"]["balanced_acc"], gate_res["working"]["decoder_valid"]))

    # --- real_code_path (F.1): construct REAL objects at tiny N (typed edges loaded from a real
    # tiny synthetic shard file, real B0 table, real pool construction, real stratification, real
    # gestalt/decoder fit on a tiny frozen toy model) -- not a synthetic-only branch.
    out_dir = os.path.join(_REPO, "data", ANCHOR_NAME + "_selftest")
    os.makedirs(out_dir, exist_ok=True)
    surfaces = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]
    surf_to_idx = {s: i for i, s in enumerate(surfaces)}
    relations = ["/r/UsedFor", "/r/LocatedNear", "/r/HasProperty", "/r/CapableOf", "/r/PartOf", "/r/MadeOf"]
    rng = np.random.default_rng(11)
    shard_path = os.path.join(out_dir, "edges_shard_00.jsonl")
    raw = []
    with open(shard_path, "w", encoding="utf-8") as f:
        for si in range(8):
            for k in range(4):
                oi = int(rng.integers(0, 8))
                if oi == si:
                    continue
                rel = relations[int(rng.integers(0, len(relations)))]
                f.write(json.dumps(dict(subject=surfaces[si], relation=rel, obj=surfaces[oi])) + "\n")
                raw.append((si, rel, oi))
    edges = _load_typed_edges([shard_path], surf_to_idx)
    assert len(edges) == len(raw), "REAL_CODE_PATH: _load_typed_edges dropped/gained edges"

    is_held = np.zeros(8, dtype=bool)
    is_held[6] = True
    is_held[7] = True
    cfg = dict(SELFTEST_CFG)
    cfg["min_train_per_rel"] = 1
    tier_c_rel, both_nonheld_counts = _pick_tier_c_relation(edges, is_held, cfg, SEED)
    assert tier_c_rel is not None, "REAL_CODE_PATH: no Tier-C relation found in toy universe"
    kept_rel = sorted([r for r, c in both_nonheld_counts.items() if c >= 1],
                       key=lambda r: (-both_nonheld_counts[r], r))
    if tier_c_rel not in kept_rel:
        kept_rel.append(tier_c_rel)
    label_relations = sorted(kept_rel)
    rel_to_idx = {r: i for i, r in enumerate(label_relations)}
    trainable = [r for r in label_relations if r != tier_c_rel]

    train_instances = [(si, rel_to_idx[rel], oi, "the " + surfaces[si] + " is near the " + surfaces[oi])
                       for (si, rel, oi) in edges
                       if rel in trainable and not is_held[si] and not is_held[oi]]
    tier_a_instances = [(si, rel_to_idx[rel], oi, "the " + surfaces[si] + " is near the " + surfaces[oi])
                        for (si, rel, oi) in edges if rel in trainable and is_held[si]]
    b0_table, gmaj = _build_b0_table(train_instances, label_relations)
    assert isinstance(b0_table, dict), "REAL_CODE_PATH: _build_b0_table did not return a dict"

    n_labels = len(label_relations)
    K = min(4, n_labels)
    if tier_a_instances and train_instances:
        items = [dict(si=si, ri=ri, oi=oi, sent=s) for (si, ri, oi, s) in tier_a_instances]
        for it in items:
            pdat = build_pool_for_item(b0_table, gmaj, it["oi"], it["ri"], n_labels, K)
            it.update(pdat)
            assert it["ri"] in it["pool"], "ADVERSARIAL-POOL SELF-TEST FAILED: true relation not in pool"
            assert len(it["pool"]) == K, "pool size != K"
        bal, meta = stratify_balanced(items, K, cap_per_bucket=2, seed=3)
        _log("SELFTEST real toy stratify meta=%s" % meta)

    # tiny frozen toy encoder + gestalt + decoder fit, exercising the REAL model-facing functions
    toy_d, toy_vocab, toy_maxlen = 16, 32, 12
    toy_model = V2.TinyTransformer(toy_vocab, toy_maxlen, toy_d, 1, 2, 2, 0)
    toy_model.eval()
    for p in toy_model.parameters():
        p.requires_grad_(False)
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    tk = Tokenizer(models.BPE(unk_token="[UNK]"))
    tk.pre_tokenizer = pre_tokenizers.Whitespace()
    tr = trainers.BpeTrainer(vocab_size=toy_vocab, special_tokens=["[PAD]", "[UNK]", "[MASK]"])
    tk.train_from_iterator([s for (_si, _ri, _oi, s) in train_instances] or ["x y z"], trainer=tr)
    toy_spec = dict(pad=tk.token_to_id("[PAD]") or 0, mask=tk.token_to_id("[MASK]") or 1)
    toy_cfg = dict(max_len=toy_maxlen, encode_batch=4)
    readout = ContentRoleReadout(toy_d, mode="fixed", seed=7)
    sents = [s for (_si, _ri, _oi, s) in (train_instances or [(0, 0, 0, "the alpha is near the beta")])]
    G = compute_gestalts(toy_model, tk, toy_spec, sents, toy_cfg, readout, torch.device("cpu"))
    assert G.shape[0] == len(sents), "REAL_CODE_PATH: compute_gestalts row count mismatch"
    y = np.array([ri for (_si, ri, _oi, _s) in train_instances] or [0], dtype=np.int64)
    toy_y = y % max(1, n_labels)
    lin, loss = fit_linear_decoder(G, toy_y, n_labels, steps=20, lr=0.05, wd=0.0, seed=1)
    assert np.isfinite(loss), "REAL_CODE_PATH: toy decoder fit produced non-finite loss"
    cent = relation_centroids(G, toy_y, n_labels)
    assert cent.shape == (n_labels, toy_d), "REAL_CODE_PATH: centroid shape mismatch"
    toy_sanity = _train_fit_sanity(lin, G, toy_y, n_labels)
    assert set(toy_sanity) == {"train_acc", "balanced_acc", "chance", "decoder_valid"}, (
        "REAL_CODE_PATH: _train_fit_sanity schema drift on toy decoder fit")

    elapsed = time.perf_counter() - t0
    _log("SELF_TEST PASS (%.2fs): bucket-math exact-1/K verified, decoder-validity-gate verified "
         "on both a deliberately-collapsed stub and a genuinely-fit decoder, real typed-edge/B0/"
         "pool/stratify/gestalt/decoder/sanity code paths all exercised at tiny N" % elapsed)
    return dict(verdict="SELF_TEST_PASS", elapsed_s=elapsed, bucket_math_b0_acc=b0_acc,
                decoder_gate_selftest=gate_res, toy_decoder_sanity=toy_sanity)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--ckpt", default=CKPT_PATH)
    args = ap.parse_args()
    if args.self_test:
        res = self_test()
        print(json.dumps(res, indent=2))
        return
    run_battery(ckpt_path=args.ckpt, cfg=FULL_CFG, seed=SEED)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        traceback.print_exc()
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "crash.txt"), "w", encoding="utf-8") as f:
            f.write("%s: %s\n\n%s" % (type(e).__name__, e, traceback.format_exc()))
        sys.exit(1)
