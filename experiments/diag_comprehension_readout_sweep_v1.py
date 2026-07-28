"""FAST CPU DIAGNOSTIC (minutes): comprehension readout-richness sweep + forward-predictive probe.

NOT a dispatched cell. No queue, no GPU, no bank/push. Standalone script; run to completion in
the foreground and read results.json off disk.

QUESTION (mirrors tonight's linear-probe readout-limit-vs-representation-limit finding for
RELATIONAL structure, but applied to COMPREHENSION = order-sensitive sentence reading): is the
frozen MLM encoder (data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt) READOUT-limited
for comprehension (structure is there in the per-token hiddens, cheap-readout fix) or
REPRESENTATION-limited (order-sensitive structure genuinely absent, needs a forward-prediction
objective / new data)?

PROBE A -- READOUT-RICHNESS SWEEP. On the SAME frozen encoder + the SAME adversarial K-way
relational-cloze ruler (experiments/eval_battery_relational_cloze_v7.py, comprehension_specific =
LEARNED_DECODER_coherent - LEARNED_DECODER_scrambled >= 0.03 on the Tier-A balanced held-out set),
swap only the READOUT (how per-token hidden states h_i collapse into one sentence gestalt) across
five variants of increasing richness:
  1. MEAN_POOL       -- plain mean over non-pad h_i (the established baseline; order enters only
                        via h_i itself, the pooling op is permutation-invariant over the token set)
  2. (same MEAN_POOL gestalt, scored by v7's LEARNED_DECODER instead of COSINE_CENTROID) -- tests
     whether a trained linear classifier recovers more signal than naive cosine from the SAME
     order-blind-pooled features. (Reported as the LEARNED_DECODER column on the MEAN_POOL row;
     a separate bilinear PAIRWISE probe, as used in tonight's diag_readout_limit_probe_v1.py, is
     the natural richer-decoder analog for a RETRIEVAL/AUC task, not for this K-way classification
     ruler, whose richer-decoder analog IS a trained linear-softmax head.)
  3. LAST_NON_PAD_TOKEN -- take h at the final non-pad position (no pooling at all; that hidden
     state has seen the FULL sequence via self-attention, so it carries the most order-dependent
     single-vector summary of any of these readouts by construction).
  4. HRR_POSITION_BIND -- v5's _bind_pooled mechanism: HRR-bind (hdlab.binding.bind, FFT circular
     convolution) a FIXED per-position role vector with each h_i, sum over non-pad, normalize.
     Order-sensitive BY CONSTRUCTION (swapping i<->j binds to different role vectors).
  5. ATTENTION_POOL  -- a small LEARNED attention-pooling head (nn.Linear(d,1) score per token,
     softmax over non-pad positions, weighted sum), trained JOINTLY with the linear decoder on
     TRAIN-only cross-entropy (leak-proof) -- the richest LEARNED aggregation tried here.

For each of the five, does coherent beat scrambled (comprehension_specific), by how much? If ANY
readout recovers order-sensitivity -> READOUT-limited (cheap fix). If ALL stay order-blind ->
REPRESENTATION-limited (needs a forward objective / more data).

EFFICIENCY: the frozen-encoder forward pass is the expensive part. This script runs it exactly
ONCE per sentence set (TRAIN, TIER_A coherent, TIER_A scrambled) and CACHES the raw per-token
hidden states [N, L, D] + pad masks; every readout is then a cheap numpy/torch op on that cache,
so all 5 readouts + Probe B share 3 encoder passes total, not 15+.

PROBE B -- FORWARD-PREDICTIVE STRUCTURE. From the SAME cached TRAIN per-token hiddens, fit a
linear classifier h_i -> token_{i+1} (vocab capped to the top-300 most frequent next-tokens in a
sentence-level FIT split + one OTHER bucket, to keep the CPU cost bounded regardless of the
encoder's full 16000-token BPE vocab), evaluate top-1 accuracy on a disjoint sentence-level EVAL
split, and compare against a unigram (always-predict-FIT-majority-class) baseline. MLM is
bidirectional (sees the future at train time) -- this probe asks whether the frozen reps still
carry NEXT-token-predictive structure, which bears on whether a forward objective would add
something the MLM encoder lacks.

LEAK-PROOFING: reuses v7's build_dataset (Tier-A subjects never in TRAIN, asserted there).
Probe B's FIT/EVAL split is by SENTENCE index (not position), so no sentence contributes pairs to
both sides. Every readout's linear/attention decoder is fit ONLY on TRAIN gestalts/hiddens, never
on Tier-A (coherent or scrambled) -- scoring only READS the trained decoder forward.

REUSE (this is wiring + two new readout/decoder implementations, not new mechanism):
experiments.eval_battery_relational_cloze_v7 (build_bundle / build_dataset / annotate_items /
stratify_balanced / fit_linear_decoder / relation_centroids / score_pool_arms -- the ruler,
unchanged); experiments.exp_prop_extraction_selfteach_v6 (_cache_ids_for_sentences,
_frozen_hidden); experiments.exp_unified_self_learning_loop_v5 (_get_role_vectors,
READOUT_ROLE_SEED -- the HRR position-bind role vectors); experiments.exp_unified_self_learning_
loop_v2 (_scramble_words); experiments.diag_readout_limit_probe_v1 (load_frozen_encoder);
hdlab.binding.bind (HRR circular convolution). New code: compute_hidden_cache (single encode +
cache raw hiddens), the four readout pooling functions, AttnPool + its joint-training loop,
fit_next_token_probe (Probe B), and the orchestration in main().
"""
from __future__ import annotations

import os
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import json  # noqa: E402

import experiments.eval_battery_relational_cloze_v7 as V7  # noqa: E402
import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402
import experiments.exp_unified_self_learning_loop_v5 as LOOP5  # noqa: E402
from experiments.exp_prop_extraction_selfteach_v6 import (  # noqa: E402
    _cache_ids_for_sentences, _frozen_hidden,
)
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402
from hdlab.binding import bind  # noqa: E402

CKPT_PATH = V7.CKPT_PATH
OUT_DIR = os.path.join(_REPO, "data", "diag_comprehension_readout_sweep_v1")
SEED = 20260728
COMPREHENSION_SPECIFIC_MARGIN = 0.03   # matches v7's own threshold, for direct comparability

# Reduced-scale cfg: v7's FULL_CFG (max_lines=3M, max_shards=16) took ~1300s wall to build the
# bundle+dataset alone -- too slow for a single foreground call. This cfg cuts the two corpus
# scans (count_pass/collect_pass) ~20x and edges load ~4x while keeping the SAME K-way adversarial
# ruler construction (build_dataset/annotate_items/stratify_balanced unchanged), fast CPU minutes.
SWEEP_CFG = dict(
    min_deg=2, cap_eval_concepts=8000, heldout_count=800, min_mentions_eval=3,
    max_lines=1800000, dedup_cap=1800000, bpe_sample_lines=50, cap_mentions=16,
    max_len=32, n_freq_buckets=6, max_shards=16, encode_batch=256,
    top_n_relations=8, min_train_per_rel=5, max_sent_per_edge=2,
    K=4, pair_withhold_frac=0.15, tier_c_count_lo=5, tier_c_count_hi=5000,
    decoder_steps=400, decoder_lr=0.03, decoder_wd=0.005,
    stratify_cap_per_bucket=60, tier_bc_cap=60,
)
NEXT_VOCAB_CAP = 300


def _log(msg):
    print("[comprehension_readout_sweep] %s" % msg, flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


# ===========================================================================
# Single-encode cache: raw per-token hidden states + pad masks + token ids.
# Every readout below operates on this cache -- no repeated encoder forward passes.
# ===========================================================================
def compute_hidden_cache(model, tok, spec, sents, cfg, device):
    d = model.d_model
    if not sents:
        return (np.zeros((0, cfg["max_len"], d), dtype=np.float32),
                np.zeros((0, cfg["max_len"]), dtype=bool),
                np.zeros((0, cfg["max_len"]), dtype=np.int64))
    idcache = _cache_ids_for_sentences(tok, sents, cfg, spec)
    ids_np = np.stack([idcache[s] for s in sents], axis=0)
    bs = cfg["encode_batch"]
    Hs, Ms = [], []
    for i in range(0, ids_np.shape[0], bs):
        ids = torch.from_numpy(ids_np[i:i + bs]).to(device)
        h, pad_mask = _frozen_hidden(model, ids)
        Hs.append(h.cpu().numpy())
        Ms.append(pad_mask.cpu().numpy())
    H = np.concatenate(Hs, axis=0).astype(np.float32)
    M = np.concatenate(Ms, axis=0).astype(bool)
    return H, M, ids_np


# ===========================================================================
# Readout pooling functions: H [N,L,D] float32, M [N,L] bool (True=pad) -> G [N,D] float32
# ===========================================================================
def readout_mean_pool(H, M):
    keep = (~M).astype(np.float32)[..., None]
    s = (H * keep).sum(axis=1)
    cnt = keep.sum(axis=1)
    cnt = np.where(cnt < 1, 1, cnt)
    g = s / cnt
    n = np.linalg.norm(g, axis=1, keepdims=True)
    return (g / (n + 1e-8)).astype(np.float32)


def readout_last_non_pad(H, M):
    valid_len = (~M).sum(axis=1)
    idx = np.clip(valid_len - 1, 0, H.shape[1] - 1)
    g = H[np.arange(H.shape[0]), idx, :]
    n = np.linalg.norm(g, axis=1, keepdims=True)
    return (g / (n + 1e-8)).astype(np.float32)


def readout_hrr_position_bind(H, M):
    """v5's _bind_pooled mechanism, applied to already-cached hiddens (no re-encode)."""
    Ht = torch.from_numpy(H).float()
    B, L, D = Ht.shape
    roles = LOOP5._get_role_vectors(L, D).to(dtype=Ht.dtype)[:L]
    roles = roles.unsqueeze(0).expand(B, -1, -1)
    bound = bind(Ht.contiguous(), roles.contiguous())
    keep = (~torch.from_numpy(M)).float().unsqueeze(-1)
    bound = bound * keep
    rep = bound.sum(dim=1)
    rep = rep / (rep.norm(dim=1, keepdim=True) + 1e-8)
    return rep.numpy().astype(np.float32)


class AttnPool(nn.Module):
    """Small learned attention-pooling head: score each token, softmax over non-pad, weighted sum."""

    def __init__(self, d):
        super().__init__()
        self.score = nn.Linear(d, 1)

    def forward(self, H, M):
        s = self.score(H).squeeze(-1)
        s = s.masked_fill(M, float("-inf"))
        w = torch.softmax(s, dim=1)
        g = (w.unsqueeze(-1) * H).sum(dim=1)
        return g / (g.norm(dim=1, keepdim=True) + 1e-8)


# ===========================================================================
# Per-readout scoring: fit decoder+centroids on TRAIN gestalts only, score on Tier-A (coherent +
# scrambled) via v7's own score_pool_arms (identical adversarial K-way pool across every readout).
# ===========================================================================
def fit_linear_decoder_weighted(G_train, y_train, n_labels, steps, lr, wd, seed):
    """Same as v7.fit_linear_decoder but with inverse-class-frequency CE weighting. v7's plain CE
    collapsed to always-predict-majority on this reduced-scale, skewed (~66% one class) label
    distribution for EVERY readout tried (identical train_acc==train_majority_acc across
    MEAN_POOL/LAST_NON_PAD_TOKEN/HRR_POSITION_BIND/ATTENTION_POOL) -- an underpowered-fit artifact,
    not a representation finding. Class-balancing forces the decoder to use per-class boundaries."""
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
        raise FloatingPointError("LEARNED_DECODER (class-weighted) training diverged (non-finite loss)")
    return lin, last_loss


def _train_fit_sanity(logits_fn, G_train, y_train, n_labels):
    """VALIDITY GATE: does the trained decoder actually discriminate classes on its OWN TRAIN fit
    data, better than chance? First pass used plain train-accuracy-vs-majority-class, which caught
    a real collapse-to-prior bug under plain CE (identical train_acc==train_majority_acc across
    every readout). Fixing that with class-weighted CE (fit_linear_decoder_weighted) then made
    plain accuracy the WRONG gate: balancing deliberately trades raw accuracy for per-class recall
    on an 8-class label set where one class covers ~66% of TRAIN, so post-balancing train_acc
    normally sits BELOW majority_acc even when the decoder has genuinely learned per-class
    structure. The correct check is BALANCED accuracy (mean per-class recall) vs chance=1/n_labels
    -- this is what tells us the decoder is using G_train's per-class signal at all (a collapsed
    fit gives balanced_acc ~= chance; a working one clears it), independent of the majority skew."""
    with torch.no_grad():
        pred = logits_fn(torch.from_numpy(G_train).float()).numpy().argmax(axis=1)
    train_acc = float((pred == y_train).mean())
    recalls = []
    for c in range(n_labels):
        mask = (y_train == c)
        if mask.sum() > 0:
            recalls.append(float((pred[mask] == c).mean()))
    balanced_acc = float(np.mean(recalls)) if recalls else 0.0
    chance = 1.0 / n_labels
    return dict(train_acc=train_acc, balanced_acc=balanced_acc, chance=chance,
                train_beats_chance=bool(balanced_acc >= chance + 0.10))


def run_readout_arm(name, G_train, G_a, G_as, train_y, n_labels, tier_a_bal, label_relations,
                     steps, lr, wd, seed):
    lin_decoder, final_loss = fit_linear_decoder_weighted(G_train, train_y, n_labels, steps, lr, wd, seed)
    sanity = _train_fit_sanity(lin_decoder, G_train, train_y, n_labels)
    centroids = V7.relation_centroids(G_train, train_y, n_labels)
    res = V7.score_pool_arms(tier_a_bal, G_a, G_as, lin_decoder, centroids, label_relations)
    decoder_margin = res["LEARNED_DECODER"] - res["LEARNED_DECODER_SCRAMBLED"]
    cosine_margin = res["COSINE_CENTROID"] - res["COSINE_CENTROID_SCRAMBLED"]
    out = dict(name=name, decoder_final_loss=final_loss, cosine_margin=cosine_margin,
               decoder_margin=decoder_margin, train_fit_sanity=sanity,
               comprehension_specific=bool(decoder_margin >= COMPREHENSION_SPECIFIC_MARGIN
                                            and sanity["train_beats_chance"]))
    out.update(res)
    return out


def run_attention_pool_arm(H_train, M_train, train_y, H_a, M_a, H_as, M_as, n_labels,
                            tier_a_bal, label_relations, d_model, cfg, seed):
    torch.manual_seed(seed)
    attn = AttnPool(d_model)
    dec = nn.Linear(d_model, n_labels)
    opt = torch.optim.Adam(list(attn.parameters()) + list(dec.parameters()),
                            lr=cfg["decoder_lr"], weight_decay=cfg["decoder_wd"])
    Xt = torch.from_numpy(H_train).float()
    Mt = torch.from_numpy(M_train)
    yt = torch.from_numpy(train_y).long()
    counts = torch.clamp(torch.bincount(yt, minlength=n_labels).float(), min=1.0)
    class_weight = counts.sum() / (n_labels * counts)
    last_loss = float("nan")
    for _ in range(cfg["decoder_steps"]):
        opt.zero_grad()
        g = attn(Xt, Mt)
        logits = dec(g)
        loss = F.cross_entropy(logits, yt, weight=class_weight)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("ATTENTION_POOL joint training diverged (non-finite loss)")
    with torch.no_grad():
        G_train = attn(Xt, Mt).numpy()
        G_a = attn(torch.from_numpy(H_a).float(), torch.from_numpy(M_a)).numpy()
        G_as = attn(torch.from_numpy(H_as).float(), torch.from_numpy(M_as)).numpy()
    sanity = _train_fit_sanity(dec, G_train, train_y, n_labels)
    centroids = V7.relation_centroids(G_train, train_y, n_labels)
    res = V7.score_pool_arms(tier_a_bal, G_a, G_as, dec, centroids, label_relations)
    decoder_margin = res["LEARNED_DECODER"] - res["LEARNED_DECODER_SCRAMBLED"]
    cosine_margin = res["COSINE_CENTROID"] - res["COSINE_CENTROID_SCRAMBLED"]
    out = dict(name="ATTENTION_POOL", decoder_final_loss=last_loss, cosine_margin=cosine_margin,
               decoder_margin=decoder_margin, train_fit_sanity=sanity,
               comprehension_specific=bool(decoder_margin >= COMPREHENSION_SPECIFIC_MARGIN
                                            and sanity["train_beats_chance"]))
    out.update(res)
    return out


# ===========================================================================
# PROBE B: forward-predictive (next-token) structure in the frozen reps.
# ===========================================================================
def fit_next_token_probe(H, M, ids_np, d_model, seed, n_vocab_cap=NEXT_VOCAB_CAP, steps=150,
                          lr=0.05, wd=0.0):
    rng = np.random.default_rng(seed)
    N = H.shape[0]
    if N < 10:
        raise RuntimeError("too few TRAIN sentences (%d) for Probe B sentence-level split" % N)
    perm = rng.permutation(N)
    n_fit = int(0.8 * N)
    fit_rows, eval_rows = perm[:n_fit], perm[n_fit:]

    def _collect(rows):
        feats, labels = [], []
        for r in rows:
            valid_len = int((~M[r]).sum())
            for i in range(valid_len - 1):
                feats.append(H[r, i, :])
                labels.append(int(ids_np[r, i + 1]))
        return feats, labels

    fit_feats, fit_labels = _collect(fit_rows)
    eval_feats, eval_labels = _collect(eval_rows)
    if len(fit_feats) < 50 or len(eval_feats) < 20:
        raise RuntimeError("too few next-token pairs for Probe B (fit=%d eval=%d)"
                            % (len(fit_feats), len(eval_feats)))

    cnt = Counter(fit_labels)
    top = [tid for tid, _ in cnt.most_common(n_vocab_cap)]
    id_to_class = {tid: i for i, tid in enumerate(top)}
    other_class = len(top)

    def _map(labels):
        return np.array([id_to_class.get(t, other_class) for t in labels], dtype=np.int64)

    y_fit = _map(fit_labels)
    y_eval = _map(eval_labels)
    X_fit = torch.from_numpy(np.stack(fit_feats)).float()
    X_eval = torch.from_numpy(np.stack(eval_feats)).float()

    torch.manual_seed(seed)
    lin = nn.Linear(d_model, other_class + 1)
    opt = torch.optim.Adam(lin.parameters(), lr=lr, weight_decay=wd)
    yt = torch.from_numpy(y_fit).long()
    last_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        logits = lin(X_fit)
        loss = F.cross_entropy(logits, yt)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("Probe B next-token linear decoder diverged (non-finite loss)")

    with torch.no_grad():
        pred_eval = lin(X_eval).argmax(dim=1).numpy()
    probe_acc = float((pred_eval == y_eval).mean())

    majority_class = Counter(y_fit.tolist()).most_common(1)[0][0]
    unigram_acc = float((y_eval == majority_class).mean())

    return dict(n_fit_pairs=len(fit_feats), n_eval_pairs=len(eval_feats),
                n_vocab_classes=other_class + 1, probe_acc=probe_acc,
                unigram_baseline_acc=unigram_acc, lift=probe_acc - unigram_acc,
                final_ce=last_loss)


# ===========================================================================
# Main orchestration
# ===========================================================================
def main():
    t_wall0 = time.perf_counter()
    os.makedirs(OUT_DIR, exist_ok=True)
    _log("device=cpu ckpt=%s" % CKPT_PATH)

    model, tok, spec, ckpt_meta = load_frozen_encoder(CKPT_PATH)
    d_model = model.d_model
    device = torch.device("cpu")
    cfg = dict(SWEEP_CFG)

    t0 = time.perf_counter()
    bundle = V7.build_bundle(cfg)
    dataset = V7.build_dataset(bundle, cfg)
    t_dataset = time.perf_counter() - t0
    n_labels = len(dataset["label_relations"])
    K = min(cfg["K"], n_labels)
    label_relations = dataset["label_relations"]
    global_majority_rel = dataset["b0_global_majority"]
    _log("bundle+dataset built (%.1fs) n_labels=%d K=%d train=%d tier_a_raw=%d"
         % (t_dataset, n_labels, K, len(dataset["train_instances"]), len(dataset["tier_a_instances"])))

    tier_a_items = V7.annotate_items(dataset["tier_a_instances"], dataset, K)
    for it in tier_a_items:
        it["_global_majority_in_pool"] = global_majority_rel if global_majority_rel in it["pool"] else None
    tier_a_bal, strat_meta = V7.stratify_balanced(tier_a_items, K, cfg["stratify_cap_per_bucket"], SEED + 601)
    _log("TIER_A stratified: n=%d meta=%s" % (len(tier_a_bal), strat_meta))
    if len(tier_a_bal) < 20:
        raise RuntimeError("too few TIER_A balanced items (%d) -- widen SWEEP_CFG" % len(tier_a_bal))

    train_sents = [s for (_si, _ri, _oi, s) in dataset["train_instances"]]
    train_y = np.array([ri for (_si, ri, _oi, _s) in dataset["train_instances"]], dtype=np.int64)

    srng = np.random.default_rng(SEED + 202)
    tier_a_sents = [it["sent"] for it in tier_a_bal]
    tier_a_scr_sents = [LOOP2._scramble_words(it["sent"], srng) for it in tier_a_bal]

    t0 = time.perf_counter()
    H_train, M_train, ids_train = compute_hidden_cache(model, tok, spec, train_sents, cfg, device)
    t_enc_train = time.perf_counter() - t0
    _log("TRAIN encoded n=%d (%.1fs)" % (H_train.shape[0], t_enc_train))
    if H_train.shape[0] < 20:
        raise RuntimeError("too few TRAIN gestalts (%d)" % H_train.shape[0])

    t0 = time.perf_counter()
    H_a, M_a, ids_a = compute_hidden_cache(model, tok, spec, tier_a_sents, cfg, device)
    H_as, M_as, ids_as = compute_hidden_cache(model, tok, spec, tier_a_scr_sents, cfg, device)
    t_enc_tier_a = time.perf_counter() - t0
    _log("TIER_A (coherent+scrambled) encoded (%.1fs)" % t_enc_tier_a)

    steps, lr, wd = cfg["decoder_steps"], cfg["decoder_lr"], cfg["decoder_wd"]
    results = {}

    t0 = time.perf_counter()
    G_train = readout_mean_pool(H_train, M_train)
    G_a = readout_mean_pool(H_a, M_a)
    G_as = readout_mean_pool(H_as, M_as)
    results["MEAN_POOL"] = run_readout_arm("MEAN_POOL", G_train, G_a, G_as, train_y, n_labels,
                                            tier_a_bal, label_relations, steps, lr, wd, SEED)
    _log("MEAN_POOL done (%.1fs): %s" % (time.perf_counter() - t0,
         {k: results["MEAN_POOL"][k] for k in ("cosine_margin", "decoder_margin", "comprehension_specific", "train_fit_sanity")}))

    t0 = time.perf_counter()
    G_train = readout_last_non_pad(H_train, M_train)
    G_a = readout_last_non_pad(H_a, M_a)
    G_as = readout_last_non_pad(H_as, M_as)
    results["LAST_NON_PAD_TOKEN"] = run_readout_arm("LAST_NON_PAD_TOKEN", G_train, G_a, G_as, train_y,
                                                      n_labels, tier_a_bal, label_relations, steps, lr, wd, SEED)
    _log("LAST_NON_PAD_TOKEN done (%.1fs): %s" % (time.perf_counter() - t0,
         {k: results["LAST_NON_PAD_TOKEN"][k] for k in ("cosine_margin", "decoder_margin", "comprehension_specific", "train_fit_sanity")}))

    t0 = time.perf_counter()
    G_train = readout_hrr_position_bind(H_train, M_train)
    G_a = readout_hrr_position_bind(H_a, M_a)
    G_as = readout_hrr_position_bind(H_as, M_as)
    results["HRR_POSITION_BIND"] = run_readout_arm("HRR_POSITION_BIND", G_train, G_a, G_as, train_y,
                                                     n_labels, tier_a_bal, label_relations, steps, lr, wd, SEED)
    _log("HRR_POSITION_BIND done (%.1fs): %s" % (time.perf_counter() - t0,
         {k: results["HRR_POSITION_BIND"][k] for k in ("cosine_margin", "decoder_margin", "comprehension_specific", "train_fit_sanity")}))

    t0 = time.perf_counter()
    results["ATTENTION_POOL"] = run_attention_pool_arm(H_train, M_train, train_y, H_a, M_a, H_as, M_as,
                                                         n_labels, tier_a_bal, label_relations, d_model, cfg, SEED)
    _log("ATTENTION_POOL done (%.1fs): %s" % (time.perf_counter() - t0,
         {k: results["ATTENTION_POOL"][k] for k in ("cosine_margin", "decoder_margin", "comprehension_specific", "train_fit_sanity")}))

    t0 = time.perf_counter()
    probe_b = fit_next_token_probe(H_train, M_train, ids_train, d_model, SEED + 999)
    t_probe_b = time.perf_counter() - t0
    _log("PROBE_B (forward-predictive) done (%.1fs): probe_acc=%.4f unigram=%.4f lift=%.4f"
         % (t_probe_b, probe_b["probe_acc"], probe_b["unigram_baseline_acc"], probe_b["lift"]))

    any_readout_limited = any(results[r]["comprehension_specific"] for r in results)
    verdict = "READOUT_LIMITED" if any_readout_limited else "REPRESENTATION_LIMITED"
    winning_readouts = [r for r in results if results[r]["comprehension_specific"]]
    forward_structure_present = bool(probe_b["lift"] >= 0.02)

    verdict_msg = ("comprehension readout sweep: %s -- %s; %d/%d readouts show "
                   "comprehension_specific>=%.2f (winners=%s); Probe B forward-predictive lift=%.4f "
                   "(probe_acc=%.4f vs unigram=%.4f) -> forward_structure_present=%s"
                   % (verdict,
                      ("at least one readout recovers order-sensitivity from the frozen reps"
                       if any_readout_limited else
                       "no readout recovers order-sensitivity -- structure genuinely absent"),
                      len(winning_readouts), len(results), COMPREHENSION_SPECIFIC_MARGIN,
                      winning_readouts, probe_b["lift"], probe_b["probe_acc"],
                      probe_b["unigram_baseline_acc"], forward_structure_present))
    _log("VERDICT: %s" % verdict_msg)

    payload = dict(
        script=os.path.basename(_THIS), ts_iso=_now(), pid=os.getpid(),
        ckpt_path=CKPT_PATH, ckpt_meta=ckpt_meta, cfg=cfg, seed=SEED,
        n_labels=n_labels, K=K, label_relations=label_relations,
        n_train_instances=len(dataset["train_instances"]), n_tier_a_balanced=len(tier_a_bal),
        tier_a_strat_meta=strat_meta, chance_1_over_k=1.0 / K,
        t_stage=dict(dataset_build_s=t_dataset, encode_train_s=t_enc_train,
                     encode_tier_a_s=t_enc_tier_a),
        probe_a_readout_sweep=results,
        probe_b_forward_predictive=probe_b,
        verdict=verdict, verdict_msg=verdict_msg,
        winning_readouts=winning_readouts, forward_structure_present=forward_structure_present,
        comprehension_specific_margin=COMPREHENSION_SPECIFIC_MARGIN,
        note_caveat=("Reduced-scale harness (cap_eval_concepts=%s, max_lines=%s, decoder_steps=%s) "
                     "for CPU-minutes turnaround -- a diagnostic/instrument-validation run sharing "
                     "the eval_battery_relational_cloze_v7 ruler's adversarial K-way construction, "
                     "not a capability-scale claim. All five readouts are scored on the IDENTICAL "
                     "Tier-A balanced item set (same adversarial pools) so this is a fair, paired "
                     "comparison across readouts sharing one frozen encoder forward pass per "
                     "sentence set. Probe B's vocab is capped at top-%d next-tokens + OTHER for CPU "
                     "tractability against the encoder's full 16000-token BPE vocab."
                     % (cfg["cap_eval_concepts"], cfg["max_lines"], cfg["decoder_steps"], NEXT_VOCAB_CAP)),
        elapsed_s_total=time.perf_counter() - t_wall0,
    )
    tmp = os.path.join(OUT_DIR, "results.json.tmp")
    final = os.path.join(OUT_DIR, "results.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)
    _log("wrote %s (elapsed %.1fs)" % (final, payload["elapsed_s_total"]))
    return payload


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
