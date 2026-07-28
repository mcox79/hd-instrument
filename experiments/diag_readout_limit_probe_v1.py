"""LIGHTWEIGHT LOCAL-CPU DIAGNOSTIC (minutes): representation-limit vs readout-limit probe.

NOT a dispatched cell. No queue, no GPU, no bank/push. Standalone analysis script; run to
completion in the foreground and read results.json off disk.

QUESTION: is the frozen encoder's ~0.56 held-out-NEW relational-AUC ceiling a REPRESENTATION
limit (the relational structure isn't in the reps) or a READOUT limit (the structure IS there
but the cosine-nearest-neighbor readout under-decodes it)?

METHOD: on the FROZEN encoder checkpoint
  data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt  (FULL run, seed=7, d_model=512,
  6 layers, selected_arm=ARM_FUSE_ZAVG at train time -- NOTE that fact is about the SEMANTIC arm
  selection, not this diagnostic's relational readout)
reuse v2's machinery (load_concept_universe, count_pass, build_split, collect_pass,
encode_concept_text_reps, load_adjacency, _auc_from_scores) at a REDUCED scale (CPU, minutes,
not the full 10M-line / ~24k-concept regime) to build a fresh leak-proof held-out-to-NEW-concept
relational task, then compare READOUTS on the SAME frozen reps:

  BASELINE_COSINE : cosine nearest-neighbor over the frozen text reps.  [the CURRENT readout]
  PROBE_DIAG       : a learned DIAGONAL-weighted cosine (per-dim reweighting), a linear map.
  PROBE_BILINEAR   : a learned low-rank LINEAR PROJECTION (d->r) then cosine, a linear map.
  FUSE_ZAVG_REF    : grounding+text z-avg fusion (reference point vs the reported 0.60-0.65 band).
  SHUFFLE / POPULARITY : validity controls (must sit near 0.5; if not, the reduced-scale harness
    itself is broken and the PROBE numbers below are not trustworthy).

LEAK-PROOFNESS (mirrors the v3_relobj leak-gate discipline): PROBE_DIAG and PROBE_BILINEAR are
fit ONLY on TRAIN-TRAIN edges (both endpoints in split['train_eval_idx']); held-out concepts and
any edge touching them NEVER enter the fit. Self-test asserts this by construction (subset check)
before any probe score is trusted.

INTERPRETATION:
  PROBE >> BASELINE (say +0.05 or more) on held-out-NEW -> READOUT-limit: the structure is
    linearly present in the frozen reps; a cheaper learned-readout fix may rival the encoder
    retrain running concurrently on GPU.
  PROBE ~= BASELINE -> REPRESENTATION-limit: not linearly decodable; the retrain (relational
    objective) is the right fix; this VALIDATES that in-flight spend.
  A linear probe is stronger than cosine but weaker than a full nonlinear readout, and an
  above-chance-but-modest gain is ambiguous -- reported honestly either way.

Output: data/diag_readout_limit_probe_v1/results.json (raw numbers; no verdict machinery, no
pre-reg, no dispatch -- this script is read inline by the caller).
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
from tokenizers import Tokenizer

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_scale_meaning_learn_arc_heldout_v2 import (  # noqa: E402
    load_concept_universe, count_pass, build_split, collect_pass,
    build_grounding_reps, encode_concept_text_reps, load_adjacency,
    TinyTransformer, _auc_from_scores,
)

CKPT_PATH = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2",
                          "ckpt_seed_7.pt")
OUT_DIR = os.path.join(_REPO, "data", "diag_readout_limit_probe_v1")

DIAG_CFG = dict(
    min_deg=2, cap_eval_concepts=3000, heldout_count=400, min_mentions_eval=8,
    max_lines=3000000, dedup_cap=2000000, bpe_sample_lines=100, cap_mentions=8,
    max_len=24, n_freq_buckets=6, max_shards=16, encode_batch=256,
)
DIAG_SEED = 20260727


def _log(msg):
    print("[diag_readout_probe] %s" % msg, flush=True)


def _z1_rows(mat):
    mu = mat.mean(axis=1, keepdims=True)
    sd = mat.std(axis=1, keepdims=True)
    return np.where(sd > 1e-12, (mat - mu) / (sd + 1e-8), mat - mu)


# ---------------------------------------------------------------------------
# Step 1: load frozen encoder + build reduced-scale leak-proof split + reps
# ---------------------------------------------------------------------------
def load_frozen_encoder(ckpt_path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    mc = ckpt["model_cfg"]
    model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                            mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    tok = Tokenizer.from_str(ckpt["tokenizer_json"])
    spec = ckpt["spec"]
    meta = dict(seed=int(ckpt["seed"]), run_mode=ckpt["run_mode"], anchor=ckpt["anchor"],
                w_star_semantic=float(ckpt["w_star"]), selected_arm_semantic=ckpt["selected_arm"],
                model_cfg=mc)
    return model, tok, spec, meta


def build_reduced_scale_bundle(cfg, model, tok, spec):
    device = torch.device("cpu")
    t_stage = {}
    t0 = time.perf_counter()
    universe = load_concept_universe(cfg)
    t_stage["universe_s"] = time.perf_counter() - t0
    _log("universe K=%d (%.1fs)" % (universe["K"], t_stage["universe_s"]))

    t0 = time.perf_counter()
    counts, corpus_stats = count_pass(cfg, universe["surf_to_idx"])
    t_stage["count_pass_s"] = time.perf_counter() - t0
    _log("count_pass done (%.1fs) kept=%d dup_rate=%.4f"
         % (t_stage["count_pass_s"], corpus_stats["n_kept"], corpus_stats["dup_rate"]))

    t0 = time.perf_counter()
    split = build_split(universe, counts, cfg)
    t_stage["split_s"] = time.perf_counter() - t0
    _log("split: heldout=%d train_eval=%d median_mentions_heldout=%.0f"
         % (split["split_meta"]["n_heldout"], split["split_meta"]["n_train_eval"],
            split["split_meta"]["median_mentions_heldout"]))

    t0 = time.perf_counter()
    postings, _bpe_lines, collect_meta = collect_pass(cfg, universe, split)
    t_stage["collect_pass_s"] = time.perf_counter() - t0
    _log("collect_pass done (%.1fs) train_lines=%d held_lines=%d"
         % (t_stage["collect_pass_s"], collect_meta["n_train_lines"], collect_meta["n_held_lines"]))

    t0 = time.perf_counter()
    adj, deg, n_shards = load_adjacency(universe, cfg)
    t_stage["adjacency_s"] = time.perf_counter() - t0
    _log("adjacency loaded (%.1fs) n_shards=%d" % (t_stage["adjacency_s"], n_shards))

    t0 = time.perf_counter()
    ground = build_grounding_reps(universe, split)
    text_reps, mrep_cnt = encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    t_stage["encode_s"] = time.perf_counter() - t0
    have_text = np.linalg.norm(text_reps, axis=1) > 1e-8
    _log("encode done (%.1fs) concepts_with_text=%d/%d"
         % (t_stage["encode_s"], int(have_text.sum()), universe["K"]))

    return dict(universe=universe, counts=counts, corpus_stats=corpus_stats, split=split,
                postings=postings, collect_meta=collect_meta, adj=adj, deg=deg,
                n_shards=n_shards, ground=ground, text_reps=text_reps, mrep_cnt=mrep_cnt,
                have_text=have_text, t_stage=t_stage)


# ---------------------------------------------------------------------------
# Step 2: leak-proof TRAIN-TRAIN pair builder (mirrors relational_eval's
# degree-matched negative sampling, restricted so BOTH endpoints are train-eval)
# ---------------------------------------------------------------------------
def build_train_pairs(split, adj, deg, have_text, seed, n_anchors=2000, max_pos=8):
    train_idx = split["train_eval_idx"]
    train_set = set(int(x) for x in train_idx.tolist())
    deg_bin = {}
    for t in train_idx.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(t)
    max_deg = int(deg[train_idx].max()) if train_idx.shape[0] else 0
    rng = np.random.default_rng(seed + 501)
    anchors = [int(i) for i in train_idx.tolist() if have_text[i]]
    rng.shuffle(anchors)
    anchors = anchors[:n_anchors]
    pi, pj, lab = [], [], []
    for a in anchors:
        pos = sorted(j for j in adj[a] if j in train_set and have_text[j] and j != a)
        if not pos:
            continue
        pos = pos[:max_pos]
        exclude = set(adj[a]) | {a}
        negs, used = [], set()
        for p in pos:
            dp = int(deg[p])
            picked = -1
            for tol in range(0, max_deg + 1):
                cands = []
                for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                    if dd in deg_bin:
                        cands.extend(deg_bin[dd])
                cands = [c for c in cands if c not in exclude and c not in used and have_text[c]]
                if cands:
                    picked = cands[int(rng.integers(0, len(cands)))]
                    break
            if picked < 0:
                continue
            negs.append(picked)
            used.add(picked)
        for p in pos:
            pi.append(a); pj.append(p); lab.append(1.0)
        for n in negs:
            pi.append(a); pj.append(n); lab.append(0.0)
    pi = np.asarray(pi, dtype=np.int64)
    pj = np.asarray(pj, dtype=np.int64)
    lab = np.asarray(lab, dtype=np.float32)
    # LEAK-PROOF SELF-TEST: every pair endpoint must be in train_eval_idx; zero overlap with held_idx.
    held_set = set(int(x) for x in split["held_idx"].tolist())
    endpoints = set(pi.tolist()) | set(pj.tolist())
    assert endpoints.issubset(train_set), "LEAK: a fit-pair endpoint is outside train_eval_idx"
    assert endpoints.isdisjoint(held_set), "LEAK: a fit-pair endpoint is a held-out concept"
    return pi, pj, lab, dict(n_anchors_used=len(anchors), n_pairs=int(lab.shape[0]),
                             n_pos=int(lab.sum()), n_neg=int((1 - lab).sum()),
                             leak_check="PASS_disjoint_from_held")


# ---------------------------------------------------------------------------
# Step 3: fit the two linear readouts (TRAIN-TRAIN only)
# ---------------------------------------------------------------------------
def fit_diag_probe(text_reps, pi, pj, lab, steps=500, lr=0.03, weight_decay=1e-2, seed=0):
    """Diagonal-weighted cosine: score = sum_k w_k * x_k * y_k. L2-regularized (n_pairs ~
    O(1e3) vs d=512 params -- weight_decay damps overfit to the small TRAIN-TRAIN fit set)."""
    torch.manual_seed(seed)
    d = text_reps.shape[1]
    X = torch.from_numpy(text_reps).float()
    w = torch.ones(d, requires_grad=True)   # init at plain-cosine equivalent (w=1 everywhere)
    opt = torch.optim.Adam([w], lr=lr, weight_decay=weight_decay)
    pi_t, pj_t, lab_t = torch.from_numpy(pi).long(), torch.from_numpy(pj).long(), torch.from_numpy(lab)
    xi, xj = X[pi_t], X[pj_t]
    last_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        score = (xi * xj * w).sum(dim=1)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(score, lab_t)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("PROBE_DIAG training diverged (non-finite loss)")
    return w.detach().numpy(), last_loss


def fit_bilinear_probe(text_reps, pi, pj, lab, r=32, steps=500, lr=0.01, weight_decay=5e-2, seed=0):
    """Low-rank linear projection d->r then cosine. r kept small (32, not 128) + weight_decay
    because n_pairs (~1e3-1e4) is small relative to r*d params -- an overparameterized bilinear
    probe would overfit the fit pairs and underperform at held-out eval for reasons that are
    about the PROBE, not the representation; this is the fair-test guard for that failure mode."""
    torch.manual_seed(seed)
    d = text_reps.shape[1]
    X = torch.from_numpy(text_reps).float()
    P = torch.nn.Linear(d, r, bias=False)
    torch.nn.init.orthogonal_(P.weight)
    opt = torch.optim.Adam(P.parameters(), lr=lr, weight_decay=weight_decay)
    pi_t, pj_t, lab_t = torch.from_numpy(pi).long(), torch.from_numpy(pj).long(), torch.from_numpy(lab)
    xi_raw, xj_raw = X[pi_t], X[pj_t]
    last_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        xi = P(xi_raw); xj = P(xj_raw)
        xi = xi / (xi.norm(dim=1, keepdim=True) + 1e-8)
        xj = xj / (xj.norm(dim=1, keepdim=True) + 1e-8)
        score = (xi * xj).sum(dim=1) * 4.0   # fixed temperature for logits
        loss = torch.nn.functional.binary_cross_entropy_with_logits(score, lab_t)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("PROBE_BILINEAR training diverged (non-finite loss)")
    return P.weight.detach().numpy(), last_loss    # [r, d]


# ---------------------------------------------------------------------------
# Step 4: held-out-NEW relational eval -- same candidate construction for every arm (paired)
# ---------------------------------------------------------------------------
def eval_relational_all_arms(text_reps, ground, split, adj, deg, have_text, w_diag, P_bilinear, seed):
    held = split["held_idx"]
    train_pool = split["train_eval_idx"]
    train_set = set(int(x) for x in train_pool.tolist())
    deg_bin = {}
    for t in train_pool.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(t)
    max_deg = int(deg[train_pool].max()) if train_pool.shape[0] else 0
    rng = np.random.default_rng(seed + 909)
    elig_q = [int(h) for h in held.tolist() if have_text[h]]

    # collapse control: text reps permuted across the eligible query ids
    if elig_q:
        eq = np.array(sorted(elig_q), dtype=np.int64)
        perm = rng.permutation(eq.shape[0])
        text_sh = text_reps.copy()
        text_sh[eq] = text_reps[eq][perm]
    else:
        text_sh = text_reps

    arm_names = ["BASELINE_COSINE", "PROBE_DIAG", "PROBE_BILINEAR", "FUSE_ZAVG_REF",
                 "SHUFFLE_CONTROL", "POPULARITY_CONTROL"]
    out = {a: [] for a in arm_names}
    per_query = []   # list of {arm_name: per-query AUC} -- same query -> paired across arms
    n_used = 0
    for h in elig_q:
        pos_neigh = sorted(j for j in adj[h] if j in train_set and have_text[j])
        if not pos_neigh:
            continue
        pos_neigh = pos_neigh[:8]
        exclude = set(adj[h]) | {h}
        negs, used, ok = [], set(), True
        for p in pos_neigh:
            dp = int(deg[p])
            picked = -1
            for tol in range(0, max_deg + 1):
                cands = []
                for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                    if dd in deg_bin:
                        cands.extend(deg_bin[dd])
                cands = [c for c in cands if c not in exclude and c not in used and have_text[c]]
                if cands:
                    picked = cands[int(rng.integers(0, len(cands)))]
                    break
            if picked < 0:
                ok = False
                break
            negs.append(picked)
            used.add(picked)
        if not ok or not negs:
            continue
        n_used += 1
        cand = np.array(pos_neigh + negs, dtype=np.int64)
        posm = np.array([True] * len(pos_neigh) + [False] * len(negs))

        ct = text_reps[h] @ text_reps[cand].T
        cd = (text_reps[h][None, :] * text_reps[cand] * w_diag[None, :]).sum(axis=1)
        ph = P_bilinear @ text_reps[h]
        ph = ph / (np.linalg.norm(ph) + 1e-8)
        pc = text_reps[cand] @ P_bilinear.T
        pc = pc / (np.linalg.norm(pc, axis=1, keepdims=True) + 1e-8)
        cb = pc @ ph
        cg = ground[h] @ ground[cand].T
        czavg = 0.5 * (_z1_rows(cg[None, :])[0] + _z1_rows(ct[None, :])[0])
        cs = text_sh[h] @ text_reps[cand].T
        pop = np.log1p(deg[cand].astype(np.float64))

        per_q_ok = True
        per_q = {}
        for a, sc in (("BASELINE_COSINE", ct), ("PROBE_DIAG", cd), ("PROBE_BILINEAR", cb),
                      ("FUSE_ZAVG_REF", czavg), ("SHUFFLE_CONTROL", cs), ("POPULARITY_CONTROL", pop)):
            au = _auc_from_scores(sc, posm)
            if au is not None:
                out[a].append(au)
                per_q[a] = au
            else:
                per_q_ok = False
        if per_q_ok:
            per_query.append(per_q)
    res = {a: (float(np.mean(v)) if v else None) for a, v in out.items()}
    res["_n_query"] = n_used
    return res, per_query


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_wall0 = time.perf_counter()
    os.makedirs(OUT_DIR, exist_ok=True)
    _log("device=cpu (no GPU touched; not dispatched to any queue)")

    if not os.path.exists(CKPT_PATH):
        raise FileNotFoundError("frozen checkpoint not found: %s" % CKPT_PATH)
    model, tok, spec, ckpt_meta = load_frozen_encoder(CKPT_PATH)
    _log("frozen encoder loaded: %s" % ckpt_meta)

    bundle = build_reduced_scale_bundle(DIAG_CFG, model, tok, spec)
    split = bundle["split"]

    pi, pj, lab, fit_meta = build_train_pairs(split, bundle["adj"], bundle["deg"],
                                              bundle["have_text"], DIAG_SEED)
    _log("train-train fit pairs: %s" % fit_meta)
    if lab.shape[0] < 40:
        raise RuntimeError("too few TRAIN-TRAIN fit pairs (%d) -- widen DIAG_CFG" % lab.shape[0])

    t0 = time.perf_counter()
    w_diag, diag_loss = fit_diag_probe(bundle["text_reps"], pi, pj, lab, seed=DIAG_SEED)
    t_diag_fit = time.perf_counter() - t0
    _log("PROBE_DIAG fit done (%.1fs) final_bce=%.4f" % (t_diag_fit, diag_loss))

    t0 = time.perf_counter()
    P_bilinear, bilin_loss = fit_bilinear_probe(bundle["text_reps"], pi, pj, lab, seed=DIAG_SEED)
    t_bilin_fit = time.perf_counter() - t0
    _log("PROBE_BILINEAR fit done (%.1fs) final_bce=%.4f" % (t_bilin_fit, bilin_loss))

    # ARMS-MUST-DIFFER-style sanity: probe weights must have actually moved from init.
    diag_moved = float(np.abs(w_diag - 1.0).mean())
    assert diag_moved > 1e-4, "PROBE_DIAG weights did not move from init -- training no-op"

    # TRAIN-FIT SANITY: does each probe actually RANK its own fit pairs better than plain
    # cosine? (BCE can be miscalibrated -- e.g. temperature-scaled logits -- while ranking/AUC
    # is fine; this checks the thing that actually matters for a nearest-neighbor readout.)
    Xtr = bundle["text_reps"]
    xi_tr, xj_tr = Xtr[pi], Xtr[pj]
    cos_fit = (xi_tr * xj_tr).sum(axis=1)
    diag_fit_score = (xi_tr * xj_tr * w_diag[None, :]).sum(axis=1)
    proj_i = (P_bilinear @ xi_tr.T).T
    proj_j = (P_bilinear @ xj_tr.T).T
    proj_i = proj_i / (np.linalg.norm(proj_i, axis=1, keepdims=True) + 1e-8)
    proj_j = proj_j / (np.linalg.norm(proj_j, axis=1, keepdims=True) + 1e-8)
    bilin_fit_score = (proj_i * proj_j).sum(axis=1)
    train_auc = dict(
        cosine=_auc_from_scores(cos_fit, lab.astype(bool)),
        diag=_auc_from_scores(diag_fit_score, lab.astype(bool)),
        bilinear=_auc_from_scores(bilin_fit_score, lab.astype(bool)),
    )
    _log("TRAIN-FIT-PAIR AUC (sanity, on the fit set itself): %s" % train_auc)

    eval_res, per_query = eval_relational_all_arms(
        bundle["text_reps"], bundle["ground"], split,
        bundle["adj"], bundle["deg"], bundle["have_text"], w_diag, P_bilinear, DIAG_SEED)
    _log("held-out-NEW relational eval: %s" % eval_res)

    baseline = eval_res["BASELINE_COSINE"]
    diag_auc = eval_res["PROBE_DIAG"]
    bilin_auc = eval_res["PROBE_BILINEAR"]
    n_q = eval_res["_n_query"]
    validity_ok = (eval_res["SHUFFLE_CONTROL"] is not None and 0.40 <= eval_res["SHUFFLE_CONTROL"] <= 0.60
                  and eval_res["POPULARITY_CONTROL"] is not None and 0.40 <= eval_res["POPULARITY_CONTROL"] <= 0.60)

    best_probe = None
    best_probe_auc = None
    if diag_auc is not None and bilin_auc is not None:
        best_probe, best_probe_auc = (("PROBE_DIAG", diag_auc) if diag_auc >= bilin_auc
                                      else ("PROBE_BILINEAR", bilin_auc))
    margin = (best_probe_auc - baseline) if (best_probe_auc is not None and baseline is not None) else None

    # PAIRED BOOTSTRAP CI on the margin (same held-out queries -> paired resampling; more
    # powerful than an unpaired test and the right test given both arms share query/candidate
    # sets). Also cross-checks against the TRAIN-FIT-PAIR AUC sanity computed above: a probe
    # that fails to beat cosine on its OWN fit pairs but "wins" at held-out is a noise flag,
    # not a readout-limit finding, regardless of the point-estimate margin.
    boot_ci = None
    train_corroborates = None
    if best_probe is not None and n_q >= 10:
        b_vals = np.array([q["BASELINE_COSINE"] for q in per_query])
        p_vals = np.array([q[best_probe] for q in per_query])
        rng_b = np.random.default_rng(DIAG_SEED + 7777)
        n = b_vals.shape[0]
        boot_margins = np.empty(2000, dtype=np.float64)
        for bi in range(2000):
            idx = rng_b.integers(0, n, size=n)
            boot_margins[bi] = p_vals[idx].mean() - b_vals[idx].mean()
        lo, hi = float(np.percentile(boot_margins, 2.5)), float(np.percentile(boot_margins, 97.5))
        boot_ci = dict(probe=best_probe, point_margin=float(p_vals.mean() - b_vals.mean()),
                      ci95_lo=lo, ci95_hi=hi, ci_excludes_zero=bool(lo > 0.0))
        _log("paired bootstrap 95%% CI on held-out margin (%s - BASELINE_COSINE): [%.4f, %.4f]"
             % (best_probe, lo, hi))
        train_key = "diag" if best_probe == "PROBE_DIAG" else "bilinear"
        train_margin = (train_auc[train_key] - train_auc["cosine"]) if (
            train_auc[train_key] is not None and train_auc["cosine"] is not None) else None
        train_corroborates = bool(train_margin is not None and train_margin > 0.0)
        _log("train-fit-pair margin for %s vs cosine: %s (corroborates=%s)"
             % (best_probe, train_margin, train_corroborates))

    if not validity_ok:
        read = ("AMBIGUOUS: validity controls out of [0.40,0.60] band (shuffle=%s pop=%s) -- the "
                "reduced-scale harness itself needs re-checking before trusting PROBE numbers."
                % (eval_res["SHUFFLE_CONTROL"], eval_res["POPULARITY_CONTROL"]))
    elif n_q < 40:
        read = "AMBIGUOUS: underpowered (n_query=%d < 40) -- numbers are directional only." % n_q
    elif margin is not None and margin >= 0.05 and boot_ci is not None and boot_ci["ci_excludes_zero"] \
            and train_corroborates:
        read = ("READOUT-limit signal (CORROBORATED): best linear probe (%s) beats cosine-NN "
                "baseline by +%.4f on held-out-NEW relational AUC; 95%% paired-bootstrap CI on the "
                "margin excludes zero [%.4f, %.4f]; AND the probe also beats cosine on its OWN "
                "TRAIN-fit pairs (not just held-out) -- structure looks linearly decodable; a "
                "cheaper learned-readout fix is worth trying before/alongside the encoder retrain."
                % (best_probe, margin, boot_ci["ci95_lo"], boot_ci["ci95_hi"]))
    elif margin is not None and margin >= 0.05 and (boot_ci is None or not boot_ci["ci_excludes_zero"]
                                                     or not train_corroborates):
        read = ("READOUT-limit signal (UNCORROBORATED / CAUTION): point-estimate margin is large "
                "(+%.4f, %s) but %s -- treat as SUGGESTIVE not decisive; the point estimate alone "
                "should NOT be used to redirect spend off the encoder retrain without a larger/"
                "cross-validated follow-up."
                % (margin, best_probe,
                   ("the 95%% bootstrap CI does not clearly exclude zero [%.4f, %.4f]"
                    % (boot_ci["ci95_lo"], boot_ci["ci95_hi"]) if boot_ci is not None
                    else "no CI could be computed")
                   if (boot_ci is None or not boot_ci["ci_excludes_zero"])
                   else "the probe did NOT beat cosine on its own TRAIN-fit pairs (train_corroborates=False)"))
    elif margin is not None and margin > 0.0:
        read = ("WEAK/AMBIGUOUS: best linear probe (%s) beats baseline by only +%.4f (< 0.05) -- "
                "modest, not a clean readout-limit signal; consistent with either a small readout "
                "gain or noise." % (best_probe, margin))
    else:
        read = ("REPRESENTATION-limit signal: linear probes do NOT beat the cosine-NN baseline "
                "(margin=%s) on held-out-NEW relational AUC -- relational structure is not "
                "linearly decodable from the frozen reps; the concurrent encoder retrain "
                "(relational objective) is the right fix." % margin)

    _log("READ: %s" % read)

    result = dict(
        ts_iso=datetime.now(timezone.utc).isoformat(),
        script=os.path.basename(_THIS),
        purpose="representation-limit vs readout-limit diagnostic (not a dispatched cell)",
        ckpt_path=CKPT_PATH, ckpt_meta=ckpt_meta,
        diag_cfg=DIAG_CFG, diag_seed=DIAG_SEED,
        corpus_stats=bundle["corpus_stats"], split_meta=split["split_meta"],
        collect_meta=bundle["collect_meta"], t_stage=bundle["t_stage"],
        fit_pairs_meta=fit_meta,
        probe_fit=dict(diag_fit_s=t_diag_fit, diag_final_bce=diag_loss, diag_weight_moved=diag_moved,
                       bilinear_fit_s=t_bilin_fit, bilinear_final_bce=bilin_loss, bilinear_rank=32,
                       train_fit_pair_auc=train_auc),
        held_out_relational_auc=eval_res,
        validity_ok=validity_ok, n_query=n_q,
        baseline_cosine_auc=baseline, probe_diag_auc=diag_auc, probe_bilinear_auc=bilin_auc,
        best_probe=best_probe, best_probe_auc=best_probe_auc, margin_over_baseline=margin,
        bootstrap_ci=boot_ci, train_corroborates=train_corroborates,
        read=read,
        note_caveat=("A linear probe is stronger than cosine-NN but weaker than a full nonlinear "
                    "readout; reduced-scale harness (cap_eval_concepts=%d, max_lines=%d) means the "
                    "BASELINE_COSINE number here is NOT expected to exactly reproduce a prior "
                    "full-scale ~0.56 report -- this is an internally-controlled PAIRED comparison "
                    "(same encoder, same split, same candidate sets across all arms), which is the "
                    "part that answers the readout-vs-representation question."
                    % (DIAG_CFG["cap_eval_concepts"], DIAG_CFG["max_lines"])),
        elapsed_s_total=time.perf_counter() - t_wall0,
    )
    tmp = os.path.join(OUT_DIR, "results.json.tmp")
    final = os.path.join(OUT_DIR, "results.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    os.replace(tmp, final)
    _log("wrote %s (elapsed %.1fs)" % (final, result["elapsed_s_total"]))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- diagnostic script; print full traceback and exit nonzero
        traceback.print_exc()
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "crash.txt"), "w", encoding="utf-8") as f:
            f.write("%s: %s\n\n%s" % (type(e).__name__, e, traceback.format_exc()))
        sys.exit(1)
