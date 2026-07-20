"""SETTLING-FIX: learned-recurrent settling rehabilitation of the settling-parse-selector HARD_FAIL (v1).

DIAGNOSIS (per notes/research_brain_learned_recurrent_settling_sentence_gestalt_2026-07-20.md): the
beta=20 one-shot softmax cleanup used in exp_settling_parse_selector_richness_v1 is the ZERO-NOISE
LIMIT of the Hopfield/EBM/diffusion family (arXiv:2506.05178) -- it collapses to a near-fixed-point in
~1 iteration, so residual-of-change sits at the float32 numerical noise floor by construction (MEASURED@
d:/AI/hd-instrument/data/settling_parse_selector_richness_v1/metrics.json:per_level_summary.tok17000000.
mean_final_residual = 1.4789402484893799e-05, pooled seeds 7+13). The brain's Sentence-Gestalt mechanism
(Rabovsky, Hansen & McClelland 2018, Nature Human Behaviour) stays graded because (i) its loss has no
one-hot target and (ii) training shifts "the work" from activation-change to connection-weights.

FIX (same temperature axis, not a new mechanism): (1) a hand-set DAMPED step (alpha<1) forces multi-
step-by-construction (diffusion-model trick); (2) a LEARNED scalar effective-beta fit to a HELD-OUT
slice of gold labels targets the sub-critical/near-beta_c graded regime (Ramsauer et al. 2020/2021;
arXiv:2311.18434 establishes beta_c is data-dependent, not universal).

4 VARIANTS (same codebook / same item set / same seed policy -- ONLY the settling dynamic varies):
  (A) BASELINE -- the already-measured one-shot beta=20 cleanup (reused verbatim via the imported
      `settle()` from exp_settling_parse_selector_richness_v1 -- this IS the HARD_FAIL floor).
  (B) DAMPED-STEP alone -- x <- x + alpha*(cleanup(x)-x), alpha<1 HAND-SET, SAME beta=20.
  (C) DAMPED-STEP + LEARNED effective-beta -- same damping, beta fit by grid search on a HELD-OUT FIT
      split of gold labels, scored on the disjoint EVAL split.
  (D) MUST-FAIL CONTROL -- same damped-step structure, but the per-iteration cleanup DIRECTION is
      replaced by a random unit vector (deterministic per-item RNG) -- decouples "multi-step recurrence"
      from "learned/meaningful direction."

PRIOR ART (credit; build-on, not reinvent):
  - Rabovsky, Hansen & McClelland 2018 (Nature Human Behaviour) -- residual-of-change as coherence.
  - Ramsauer et al. 2020/2021 -- modern Hopfield beta-as-fixed-point-class-selector.
  - arXiv:2311.18434 -- beta_c is a fittable, data-dependent scalar (the C-variant's grounding).
  - arXiv:2506.05178 -- Hopfield/EBM/diffusion zero-noise-limit unification (the B/D damped-step trick).
  - Reuses exp_settling_parse_selector_richness_v1.py's codebook/item/role/settle machinery verbatim
    (load_pp_candidates, select_balanced_items, build_fixed_vocab, build_richness_codebook,
    make_role_atoms, compose_candidate, settle, score_baseline_thematic_fit) -- see that file's own
    prior-art header for the deeper citation chain (Kintsch/vanDijk CI, Frady et al. resonator D/N).

Pre-reg: preregs/2026-07-20_settling_fix_learned_recurrent_v1.md (verbatim HARD-PASS/HARD-FAIL bands
from notes/research_brain_learned_recurrent_settling_sentence_gestalt_2026-07-20.md's "Falsifiable
predictions" section).

CELL-TEMPLATE MANDATORY: arms_differ hash-test on RAW RESIDUAL TRAJECTORIES (not just predictions);
tmp_replace atomic metrics; except SystemExit: raise BEFORE except Exception (no BaseException);
crlb_n/a declared; discriminator survives scale (smoke previews FULL richness token-count at reduced
vocab/N); cardinality gate; per-unit failure-class; deterministic seeding (fixed ints, sorted(), no
hash()/list(set())); numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@; start-marker +
heartbeat + crash-diag.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.exp_settling_parse_selector_richness_v1 import (  # noqa: E402
    load_pp_candidates, select_balanced_items, build_fixed_vocab, build_richness_codebook,
    _l2norm_rows_np, make_role_atoms, compose_candidate, settle as settle_onepass_family,
    score_baseline_thematic_fit, ROLE_NAMES, ITEM_SAMPLE_SEED,
)
from hdlab.binding import bind as hd_bind  # noqa: E402
from hdlab.binding import unbind as hd_unbind  # noqa: E402

ANCHOR_NAME = "settling_fix_learned_recurrent_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- fixed mechanism constants (G9-style: declared once, never retuned per outcome) ----
BETA_HIGH = 20.0             # variant A (reproduce) + variant B (damped, same beta)
T_MAX_A = 6                  # EXACT original variant-A iteration budget
TAIL_K = 2                   # EXACT original tail-mean window
T_MAX_FIX = 8                # variants B/C/D: longer budget so damping has room to show trajectory
ALPHA_DAMPING = 0.25         # HAND-SET damping factor (B, C, D) -- no learning, no per-run tuning
BETA_GRID = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0]   # variant C grid search (includes the ceiling)
CONV_REL_THRESH = 0.05       # "converged" once residual_t <= 0.05 * residual_1 (relative, not absolute)
MARGIN_G3 = 0.10             # HARD-PASS-2 / HARD-PASS-3 margin (10pp, same convention as source cell)
SPLIT_SEED_V = 555           # FIT/EVAL split seed, V-attach half
SPLIT_SEED_N = 556           # FIT/EVAL split seed, N-attach half
D_SEED_BASE = 707070         # variant D per-item-per-candidate deterministic RNG base (never hash())

# historical cross-check only (NOT used as the primary floor -- variant A is remeasured fresh each run)
NOISE_FLOOR_HIST_REF = 1.4789402484893799e-05
# MEASURED@d:/AI/hd-instrument/data/settling_parse_selector_richness_v1/metrics.json:
#   per_level_summary.tok17000000.mean_final_residual (pooled seeds 7+13, n_units=96)

# FULL config -- matches the source cell's RICHEST richness level exactly (where the floor was measured)
FULL_VOCAB_SIZE = 12000
FULL_N_DIM = 1024
FULL_MIN_COUNT = 5
FULL_N_TOKENS = 17_000_000
FULL_SEED = 7
FULL_N_PER_CLASS = 24   # -> 48 items

# SMOKE config -- matches the source cell's smoke preview level (reduced vocab/N, FULL token-count)
SMOKE_VOCAB_SIZE = 3000
SMOKE_N_DIM = 256
SMOKE_MIN_COUNT = 5
SMOKE_N_TOKENS = 8_000_000
SMOKE_SEED = 7
SMOKE_N_PER_CLASS = 6   # -> 12 items


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- settling variants
def settle_damped(s0, roles, codebook_normed_t, beta, alpha, t_max):
    """Same unbind -> soft-cleanup -> rebind loop as the original `settle()`, but the state update is
    DAMPED: s_next = normalize(s + alpha*(cleanup_result - s)). alpha<1 forces multi-step-by-
    construction (the diffusion-model trick), independent of beta."""
    s = s0
    residuals = []
    for _t in range(t_max):
        recon_terms = []
        for rname in ROLE_NAMES:
            est = hd_unbind(s, roles[rname])
            est_n = est / torch.clamp(est.norm(), min=1e-8)
            sims = codebook_normed_t @ est_n
            w = torch.softmax(beta * sims, dim=0)
            cleaned = w @ codebook_normed_t
            cleaned = cleaned / torch.clamp(cleaned.norm(), min=1e-8)
            recon_terms.append(hd_bind(roles[rname], cleaned))
        s_full = torch.stack(recon_terms, dim=0).sum(dim=0)
        s_full = s_full / torch.clamp(s_full.norm(), min=1e-8)
        s_next = s + alpha * (s_full - s)
        s_next = s_next / torch.clamp(s_next.norm(), min=1e-8)
        cos = torch.clamp(torch.dot(s_next, s), -1.0, 1.0)
        residuals.append(float(1.0 - cos))
        s = s_next
    return residuals


def settle_random_control(s0, roles, n_dim, alpha, t_max, rng):
    """MUST-FAIL CONTROL (D): same damped-step structure, but the per-iteration 'cleanup' direction is
    a random unit vector (deterministic per-call rng, NEVER hash()) instead of the codebook-softmax
    reconstruction. Decouples 'multi-step recurrence exists' from 'the direction is meaningful.'"""
    s = s0
    residuals = []
    for _t in range(t_max):
        recon_terms = []
        for _rname in ROLE_NAMES:
            rand_vec = torch.from_numpy(rng.normal(size=n_dim).astype(np.float32))
            rand_vec = rand_vec / torch.clamp(rand_vec.norm(), min=1e-8)
            recon_terms.append(hd_bind(roles[_rname], rand_vec))
        s_full = torch.stack(recon_terms, dim=0).sum(dim=0)
        s_full = s_full / torch.clamp(s_full.norm(), min=1e-8)
        s_next = s + alpha * (s_full - s)
        s_next = s_next / torch.clamp(s_next.norm(), min=1e-8)
        cos = torch.clamp(torch.dot(s_next, s), -1.0, 1.0)
        residuals.append(float(1.0 - cos))
        s = s_next
    return residuals


def _tail_mean(residuals, k):
    return float(np.mean(residuals[-k:]))


def _iters_to_converge(residuals, rel_thresh=CONV_REL_THRESH):
    """First 1-indexed iteration where residual_t <= rel_thresh * residual_1. len+1 = non-convergent."""
    r0 = residuals[0]
    if r0 <= 0:
        return 1
    thresh = rel_thresh * r0
    for i, r in enumerate(residuals):
        if r <= thresh:
            return i + 1
    return len(residuals) + 1


def _package(res_v, res_n, gold, tail_k):
    tail_v = _tail_mean(res_v, tail_k)
    tail_n = _tail_mean(res_n, tail_k)
    pred = 1 if tail_v < tail_n else 2
    return {
        "gold": gold, "pred": pred,
        "tail_v": tail_v, "tail_n": tail_n,
        "final_v": res_v[-1], "final_n": res_n[-1],
        "iters_v": _iters_to_converge(res_v), "iters_n": _iters_to_converge(res_n),
        "pref_score": tail_v - tail_n,   # positive => N-attach residual lower => N preferred
        "res_v": res_v, "res_n": res_n,  # raw trajectories (used by arms-differ hash + variance stats)
    }


def _spearman(x, y):
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    if len(x) < 3 or np.any(np.isnan(x)) or np.any(np.isnan(y)):
        return float("nan")
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    if np.std(rx) == 0 or np.std(ry) == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _key(item):
    return f"{item[0]}_{item[1]}_{item[2]}_{item[3]}"


def _half_split(lst, seed):
    """Deterministic 50/50 split via seeded rng + sorted() index lists (PROT-023: never hash()/
    list(set())-derived ordering)."""
    rng = np.random.default_rng(seed)
    n = len(lst)
    k = n // 2
    perm = rng.permutation(n)
    fit_idx = sorted(perm[:k].tolist())
    eval_idx = sorted(perm[k:].tolist())
    return [lst[i] for i in fit_idx], [lst[i] for i in eval_idx]


def _fit_beta(fit_items, roles, cb_normed, cb_t, w2i, alpha, t_max, tail_k, beta_grid):
    """Grid search: select the beta maximizing FIT-split accuracy. Tie-break: among betas tied for best
    accuracy, prefer the one with the LARGEST mean |tail_v - tail_n| margin on the FIT split (a proxy
    for 'still discriminating', i.e. targets the sub-critical near-beta_c graded regime), NOT blindly
    the smallest beta -- a naive smallest-beta tie-break was found at smoke to walk straight past
    beta_c into the Ramsauer et al. 'global-average' 3rd-fixed-point-class (all items converge to
    nearly the SAME point => near-zero across-item residual variance => uninformative), which is a
    DIFFERENT, equally-uninformative failure mode from the original beta=20 collapse, not the intended
    graded regime. Uses ONLY fit_items' gold labels (held-out from all EVAL-split scoring)."""
    fit_results = {}
    fit_margins = {}
    for beta_cand in beta_grid:
        correct = 0
        margins = []
        for it in fit_items:
            v, n1, p, n2, gold = it
            s0_v = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=v)
            s0_n = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=n1)
            res_v = settle_damped(s0_v, roles, cb_t, beta_cand, alpha, t_max)
            res_n = settle_damped(s0_n, roles, cb_t, beta_cand, alpha, t_max)
            tail_v = _tail_mean(res_v, tail_k); tail_n = _tail_mean(res_n, tail_k)
            pred = 1 if tail_v < tail_n else 2
            correct += int(pred == gold)
            margins.append(abs(tail_v - tail_n))
        fit_results[beta_cand] = correct / len(fit_items) if fit_items else float("nan")
        fit_margins[beta_cand] = float(np.mean(margins)) if margins else float("nan")
    best_acc = max(fit_results.values())
    candidates_at_best = [b for b, a in fit_results.items() if a == best_acc]
    best_beta = max(candidates_at_best, key=lambda b: fit_margins[b])
    return best_beta, best_acc, fit_results, fit_margins


def _aggregate(per_item, subset_items, t_max):
    keys = [_key(it) for it in subset_items]
    sub = {k: per_item[k] for k in keys}
    preds = [sub[k]["pred"] for k in keys]
    golds = [sub[k]["gold"] for k in keys]
    n = len(keys)
    acc = float(np.mean([p == g for p, g in zip(preds, golds)])) if n else float("nan")
    pref_scores = [sub[k]["pref_score"] for k in keys]
    gold_is_n = [1 if g == 2 else 0 for g in golds]
    rho = _spearman(pref_scores, gold_is_n) if n >= 3 else float("nan")

    tail_vals = []
    iters_all = []
    for k in keys:
        tail_vals.append(sub[k]["tail_v"]); tail_vals.append(sub[k]["tail_n"])
        iters_all.append(sub[k]["iters_v"]); iters_all.append(sub[k]["iters_n"])
    variance = float(np.var(tail_vals)) if tail_vals else float("nan")
    mean_residual = float(np.mean(tail_vals)) if tail_vals else float("nan")
    mean_iters = float(np.mean(iters_all)) if iters_all else float("nan")
    n_1_2_step = sum(1 for x in iters_all if x <= 2)
    n_multi_step = sum(1 for x in iters_all if 3 <= x <= t_max)
    n_nonconvergent = sum(1 for x in iters_all if x > t_max)

    breakdown = {"correct": 0, "spurious": 0, "non_convergent": 0}
    for k in keys:
        u = sub[k]
        iters_pred = u["iters_v"] if u["pred"] == 1 else u["iters_n"]
        if iters_pred > t_max:
            breakdown["non_convergent"] += 1
        elif u["pred"] == u["gold"]:
            breakdown["correct"] += 1
        else:
            breakdown["spurious"] += 1

    return {
        "n_items": n, "acc": acc, "rho": rho, "variance": variance, "mean_residual": mean_residual,
        "mean_iters": mean_iters, "n_1_2_step": n_1_2_step, "n_multi_step": n_multi_step,
        "n_nonconvergent": n_nonconvergent, "breakdown": breakdown,
    }


def _g3_acc(g3_pred, subset_items):
    return float(np.mean([g3_pred[_key(it)] == it[4] for it in subset_items])) if subset_items else float("nan")


# --------------------------------------------------------------------------- runner
def run(output_dir, run_mode, vocab_size, n_dim, n_tokens, seed, n_per_class, min_count):
    t0 = time.perf_counter()
    n_items_target = 2 * n_per_class
    expected_n_units = n_items_target
    _write_start_marker(output_dir, run_mode, expected_n_units)

    _hb(output_dir, f"loading fixed vocab vocab_size={vocab_size} n_tokens={n_tokens}")
    tokens_full, w2i = build_fixed_vocab(vocab_size, min_count, max_n_tokens=n_tokens)
    V = len(w2i)
    _hb(output_dir, f"fixed vocab V={V}")

    candidates = load_pp_candidates()
    items, item_meta = select_balanced_items(candidates, w2i, n_per_class, seed=ITEM_SAMPLE_SEED)
    n_items = len(items)
    _hb(output_dir, f"PP-attachment items: {n_items} (meta={item_meta})")
    if n_items < 8:
        raise RuntimeError(f"TOO_FEW_ITEMS: only {n_items} in-vocab balanced items (need >=8)")

    roles = make_role_atoms(n_dim, seed=999)

    _hb(output_dir, f"building codebook (n_tokens={n_tokens}, seed={seed}) -- dominant cost")
    cb = build_richness_codebook(tokens_full, w2i, n_tokens, n_dim, seed)
    cb_normed = _l2norm_rows_np(cb)
    cb_t = torch.from_numpy(np.ascontiguousarray(cb_normed, dtype=np.float32))
    _hb(output_dir, "codebook built")

    v_items = [it for it in items if it[4] == 1]
    n_items_cls = [it for it in items if it[4] == 2]
    v_fit, v_eval = _half_split(v_items, SPLIT_SEED_V)
    n_fit, n_eval = _half_split(n_items_cls, SPLIT_SEED_N)
    fit_items = v_fit + n_fit
    eval_items = v_eval + n_eval
    _hb(output_dir, f"FIT/EVAL split: fit={len(fit_items)} eval={len(eval_items)}")

    per_unit_failures = {}
    n_units_done = 0

    # ---- variant A: reproduce the original one-shot beta=20 cleanup verbatim ----
    per_item_A = {}
    for it in items:
        try:
            v, n1, p, n2, gold = it
            s0_v = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=v)
            s0_n = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=n1)
            res_v = settle_onepass_family(s0_v, roles, cb_t, BETA_HIGH, T_MAX_A)
            res_n = settle_onepass_family(s0_n, roles, cb_t, BETA_HIGH, T_MAX_A)
            per_item_A[_key(it)] = _package(res_v, res_n, gold, TAIL_K)
            n_units_done += 1
        except Exception as e:  # noqa: BLE001 -- recorded, not swallowed (META_RULE_J)
            per_unit_failures[f"A__{_key(it)}"] = f"{type(e).__name__}: {str(e)[:300]}"
            _hb(output_dir, f"A FAILED on {_key(it)}: {e}")
    _hb(output_dir, f"variant A done: {len(per_item_A)}/{n_items}")

    # ---- variant B: damped step alone, same beta=20 ----
    per_item_B = {}
    for it in items:
        try:
            v, n1, p, n2, gold = it
            s0_v = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=v)
            s0_n = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=n1)
            res_v = settle_damped(s0_v, roles, cb_t, BETA_HIGH, ALPHA_DAMPING, T_MAX_FIX)
            res_n = settle_damped(s0_n, roles, cb_t, BETA_HIGH, ALPHA_DAMPING, T_MAX_FIX)
            per_item_B[_key(it)] = _package(res_v, res_n, gold, TAIL_K)
            n_units_done += 1
        except Exception as e:  # noqa: BLE001
            per_unit_failures[f"B__{_key(it)}"] = f"{type(e).__name__}: {str(e)[:300]}"
            _hb(output_dir, f"B FAILED on {_key(it)}: {e}")
    _hb(output_dir, f"variant B done: {len(per_item_B)}/{n_items}")

    # ---- variant C: damped step + learned effective-beta (fit on FIT split) ----
    _hb(output_dir, f"fitting beta on FIT split (n={len(fit_items)}, grid={BETA_GRID})")
    fitted_beta, fit_acc, fit_grid_results, fit_grid_margins = _fit_beta(
        fit_items, roles, cb_normed, cb_t, w2i, ALPHA_DAMPING, T_MAX_FIX, TAIL_K, BETA_GRID)
    _hb(output_dir, f"fitted_beta={fitted_beta} fit_acc={fit_acc:.3f} grid_acc={fit_grid_results} "
                    f"grid_margins={fit_grid_margins}")

    per_item_C = {}
    for it in items:
        try:
            v, n1, p, n2, gold = it
            s0_v = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=v)
            s0_n = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=n1)
            res_v = settle_damped(s0_v, roles, cb_t, fitted_beta, ALPHA_DAMPING, T_MAX_FIX)
            res_n = settle_damped(s0_n, roles, cb_t, fitted_beta, ALPHA_DAMPING, T_MAX_FIX)
            per_item_C[_key(it)] = _package(res_v, res_n, gold, TAIL_K)
            n_units_done += 1
        except Exception as e:  # noqa: BLE001
            per_unit_failures[f"C__{_key(it)}"] = f"{type(e).__name__}: {str(e)[:300]}"
            _hb(output_dir, f"C FAILED on {_key(it)}: {e}")
    _hb(output_dir, f"variant C done: {len(per_item_C)}/{n_items}")

    # ---- variant D: must-fail random-recurrent control ----
    per_item_D = {}
    for idx, it in enumerate(items):
        try:
            v, n1, p, n2, gold = it
            s0_v = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=v)
            s0_n = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=n1)
            rng_v = np.random.default_rng(D_SEED_BASE + idx * 2)
            rng_n = np.random.default_rng(D_SEED_BASE + idx * 2 + 1)
            res_v = settle_random_control(s0_v, roles, n_dim, ALPHA_DAMPING, T_MAX_FIX, rng_v)
            res_n = settle_random_control(s0_n, roles, n_dim, ALPHA_DAMPING, T_MAX_FIX, rng_n)
            per_item_D[_key(it)] = _package(res_v, res_n, gold, TAIL_K)
            n_units_done += 1
        except Exception as e:  # noqa: BLE001
            per_unit_failures[f"D__{_key(it)}"] = f"{type(e).__name__}: {str(e)[:300]}"
            _hb(output_dir, f"D FAILED on {_key(it)}: {e}")
    _hb(output_dir, f"variant D done: {len(per_item_D)}/{n_items}")

    # ---- G3 baseline (informational, zero-iteration, reused from source cell) ----
    g3_pred = {_key(it): score_baseline_thematic_fit(it, w2i, cb_normed) for it in items}
    g3_acc_full = _g3_acc(g3_pred, items)
    g3_acc_eval = _g3_acc(g3_pred, eval_items)

    # ---- aggregate stats (full-set and eval-only per variant) ----
    agg_A_full = _aggregate(per_item_A, items, T_MAX_A)
    agg_A_eval = _aggregate(per_item_A, eval_items, T_MAX_A)
    agg_B_full = _aggregate(per_item_B, items, T_MAX_FIX)
    agg_B_eval = _aggregate(per_item_B, eval_items, T_MAX_FIX)
    agg_C_full = _aggregate(per_item_C, items, T_MAX_FIX)
    agg_C_eval = _aggregate(per_item_C, eval_items, T_MAX_FIX)
    agg_D_full = _aggregate(per_item_D, items, T_MAX_FIX)
    agg_D_eval = _aggregate(per_item_D, eval_items, T_MAX_FIX)

    floor_variance = agg_A_full["variance"] if agg_A_full["variance"] and agg_A_full["variance"] > 0 else 1e-30

    def _oom(v):
        vv = v if (v is not None and v > 0) else 1e-30
        return float(np.log10(vv / floor_variance))

    oom_C_full = _oom(agg_C_full["variance"])
    oom_B_full = _oom(agg_B_full["variance"])
    oom_D_full = _oom(agg_D_full["variance"])

    # ---- design-gate precondition: must-fail (D) must fire ----
    must_fail_D_fires = abs(agg_D_eval["acc"] - 0.5) <= 0.20 if not np.isnan(agg_D_eval["acc"]) else False

    # ---- cardinality (META_RULE_H) ----
    cardinality_ok = (n_units_done == 4 * n_items)  # 4 variants x n_items, each counted once above

    # ---- arms-must-differ (META_RULE_AF) on RAW RESIDUAL TRAJECTORIES ----
    def _traj_bytes(per_item):
        flat = []
        for it in items:
            k = _key(it)
            if k not in per_item:
                continue
            flat.extend(per_item[k]["res_v"])
            flat.extend(per_item[k]["res_n"])
        return np.asarray(flat, dtype=np.float64).tobytes()

    traj_hashes = {
        "A": hashlib.sha256(_traj_bytes(per_item_A)).hexdigest(),
        "B": hashlib.sha256(_traj_bytes(per_item_B)).hexdigest(),
        "C": hashlib.sha256(_traj_bytes(per_item_C)).hexdigest(),
        "D": hashlib.sha256(_traj_bytes(per_item_D)).hexdigest(),
    }
    distinct_pairs = {}
    for a in traj_hashes:
        for b in traj_hashes:
            if a < b:
                distinct_pairs[f"{a}_vs_{b}"] = traj_hashes[a] != traj_hashes[b]
    arms_differ = all(distinct_pairs.values()) if distinct_pairs else True

    # ---- HARD-PASS / HARD-FAIL gates (verbatim per pre-reg) ----
    hp1 = oom_C_full >= 3.0
    hp2 = (not np.isnan(agg_C_eval["rho"]) and agg_C_eval["rho"] >= 0.3) or \
          (not np.isnan(agg_C_eval["acc"]) and (agg_C_eval["acc"] - g3_acc_eval) >= MARGIN_G3)
    hp3 = (agg_C_eval["acc"] > agg_A_eval["acc"]) and \
          ((agg_C_eval["acc"] - agg_D_eval["acc"]) >= MARGIN_G3)
    hp4 = (fitted_beta < BETA_HIGH) and (agg_C_full["n_multi_step"] > agg_C_full["n_1_2_step"])

    hf1 = oom_C_full < 1.0
    hf2 = agg_C_eval["acc"] <= agg_D_eval["acc"]
    hf3 = (oom_C_full >= 1.0) and (np.isnan(agg_C_eval["rho"]) or abs(agg_C_eval["rho"]) < 0.15) and \
          ((agg_C_eval["acc"] - g3_acc_eval) < MARGIN_G3)
    hf4 = (fitted_beta >= BETA_HIGH)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif hf1:
        verdict = "HARD_FAIL_1_RESIDUAL_PINNED_AT_NOISE_FLOOR_CODEBOOK_GEOMETRY_FORCES_COLLAPSE"
    elif hf2:
        verdict = "HARD_FAIL_2_C_DOES_NOT_BEAT_RANDOM_RECURRENT_CONTROL"
    elif hf4:
        verdict = "HARD_FAIL_4_BETA_REFITS_BACK_TO_HIGH_GAIN_REGIME"
    elif hf3:
        verdict = "HARD_FAIL_3_GRADED_BUT_NOT_MEANINGFUL_NULL_GOLD_CORRELATION"
    elif hp1 and hp2 and hp3 and hp4:
        verdict = "HARD_PASS_LEARNED_RECURRENT_SETTLING_FIX_CONFIRMED"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_FIX"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"fitted_beta={fitted_beta} (grid={BETA_GRID}, fit_acc={fit_acc:.3f}) | "
        f"oom_above_floor: B={oom_B_full:.2f} C={oom_C_full:.2f} D={oom_D_full:.2f} "
        f"(floor_variance(A,full)={floor_variance:.3e}, hist_ref={NOISE_FLOOR_HIST_REF:.3e}) | "
        f"EVAL acc: A={agg_A_eval['acc']:.3f} B={agg_B_eval['acc']:.3f} C={agg_C_eval['acc']:.3f} "
        f"D={agg_D_eval['acc']:.3f} G3={g3_acc_eval:.3f} | "
        f"EVAL rho vs gold: A={agg_A_eval['rho']:.3f} B={agg_B_eval['rho']:.3f} "
        f"C={agg_C_eval['rho']:.3f} D={agg_D_eval['rho']:.3f} | "
        f"C convergence-class (full, pooled n={2 * agg_C_full['n_items']}): "
        f"1-2step={agg_C_full['n_1_2_step']} multi-step={agg_C_full['n_multi_step']} "
        f"nonconv={agg_C_full['n_nonconvergent']} | "
        f"must_fail_D_fires={must_fail_D_fires} | HP={{1:{hp1},2:{hp2},3:{hp3},4:{hp4}}} "
        f"HF={{1:{hf1},2:{hf2},3:{hf3},4:{hf4}}} | cardinality_ok={cardinality_ok} arms_differ={arms_differ}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": f"{verdict}: {verdict_msg[:200]}",
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "vocab_size": vocab_size, "V": V, "n_dim": n_dim, "min_count": min_count,
            "n_tokens": n_tokens, "seed": seed, "n_per_class": n_per_class, "n_items": n_items,
            "beta_high": BETA_HIGH, "t_max_a": T_MAX_A, "t_max_fix": T_MAX_FIX,
            "alpha_damping": ALPHA_DAMPING, "beta_grid": BETA_GRID, "tail_k": TAIL_K,
            "conv_rel_thresh": CONV_REL_THRESH,
        },
        "item_meta": item_meta,
        "fit_eval_split": {"n_fit": len(fit_items), "n_eval": len(eval_items),
                          "fit_keys": [_key(it) for it in fit_items],
                          "eval_keys": [_key(it) for it in eval_items]},
        "fitted_beta": fitted_beta, "fit_acc": fit_acc, "fit_grid_results": fit_grid_results,
        "fit_grid_margins": fit_grid_margins,
        "g3_baseline": {"acc_full": g3_acc_full, "acc_eval": g3_acc_eval},
        "agg_full": {"A": agg_A_full, "B": agg_B_full, "C": agg_C_full, "D": agg_D_full},
        "agg_eval": {"A": agg_A_eval, "B": agg_B_eval, "C": agg_C_eval, "D": agg_D_eval},
        "orders_of_magnitude_above_floor_full": {"B": oom_B_full, "C": oom_C_full, "D": oom_D_full},
        "floor_variance_measured_this_run": floor_variance,
        "noise_floor_historical_reference": NOISE_FLOOR_HIST_REF,
        "must_fail_D_fires": must_fail_D_fires,
        "hard_pass_gates": {"HP1_oom_ge_3": hp1, "HP2_rho_or_beats_g3": hp2,
                            "HP3_beats_A_and_D": hp3, "HP4_beta_below_ceiling_and_multistep": hp4},
        "hard_fail_gates": {"HF1_pinned_at_floor": hf1, "HF2_does_not_beat_D": hf2,
                            "HF3_graded_not_meaningful": hf3, "HF4_beta_refits_to_ceiling": hf4},
        "cardinality_ok": cardinality_ok, "expected_n_units": 4 * n_items, "n_units_done": n_units_done,
        "per_unit_failures": per_unit_failures,
        "arms_differ_verified": arms_differ, "arms_differ_detail": distinct_pairs,
        "arms_differ_hash_basis": "raw_residual_trajectories_not_predictions_only",
        "crlb_n/a": "residual/coherence discrimination test; no argmax-capacity noise floor of the "
                   "CRLB form; this cell's floor is empirically measured fresh from variant A each run.",
        "prior_art": "Rabovsky/Hansen/McClelland2018 settling residual; Ramsauer2021 inverse-temp "
                    "fixed-point-class; arXiv:2311.18434 fittable beta_c; arXiv:2506.05178 Hopfield/"
                    "EBM/diffusion zero-noise-limit unification; reuses "
                    "exp_settling_parse_selector_richness_v1 codebook/item/role/settle machinery verbatim",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Real-code-path self-test at tiny scale: exercises REAL PP-item loader, REAL codebook builder,
    REAL bind/unbind settling loops (settle_onepass_family=A, settle_damped=B/C, settle_random_control=
    D), and the REAL beta-grid-fit function, all at N_DIM=16."""
    print("[self-test] loading REAL PP-attachment candidates from disk", flush=True)
    candidates = load_pp_candidates()
    assert len(candidates) > 50, f"too few raw candidates loaded: {len(candidates)}"

    print("[self-test] building tiny FIXED vocab from a small text8 slice (real loader/builder)",
          flush=True)
    tokens_full, w2i = build_fixed_vocab(vocab_size=400, min_count=2, max_n_tokens=300_000)
    V = len(w2i)
    assert V >= 50, f"tiny vocab too small: {V}"

    items, meta = select_balanced_items(candidates, w2i, n_per_class=4, seed=ITEM_SAMPLE_SEED)
    print(f"[self-test] tiny in-vocab balanced items: {len(items)} meta={meta}", flush=True)
    if len(items) < 4:
        print("[self-test] WARNING: tiny vocab yields <4 balanced items; widening vocab", flush=True)
        tokens_full, w2i = build_fixed_vocab(vocab_size=1500, min_count=2, max_n_tokens=1_000_000)
        V = len(w2i)
        items, meta = select_balanced_items(candidates, w2i, n_per_class=4, seed=ITEM_SAMPLE_SEED)
        print(f"[self-test] widened-vocab in-vocab balanced items: {len(items)} meta={meta}", flush=True)
    assert len(items) >= 4, f"self-test cannot assemble a tiny balanced item set: {len(items)}"

    N_DIM = 16
    print(f"[self-test] building REAL tiny codebook (V={V}, N_DIM={N_DIM}) via ppmi_svd", flush=True)
    cb = build_richness_codebook(tokens_full, w2i, n_tokens=len(tokens_full), N_DIM=N_DIM, seed=7)
    assert cb.shape == (V, N_DIM), f"codebook shape {cb.shape}"
    assert np.all(np.isfinite(cb)), "codebook has non-finite values"
    cb_normed = _l2norm_rows_np(cb)
    cb_t = torch.from_numpy(np.ascontiguousarray(cb_normed, dtype=np.float32))

    roles = make_role_atoms(N_DIM, seed=999)
    assert len(roles) == 5

    v_items = [it for it in items if it[4] == 1]
    n_items_cls = [it for it in items if it[4] == 2]
    v_fit, v_eval = _half_split(v_items, SPLIT_SEED_V)
    n_fit, n_eval = _half_split(n_items_cls, SPLIT_SEED_N)
    fit_items = v_fit + n_fit
    eval_items = v_eval + n_eval
    print(f"[self-test] FIT/EVAL split: fit={len(fit_items)} eval={len(eval_items)}", flush=True)

    it = items[0]
    v, n1, p, n2, gold = it
    s0_v = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=v)
    s0_n = compose_candidate(roles, cb_normed, w2i, v, n1, p, n2, attach_word=n1)

    # variant A (reused settle())
    res_v_A = settle_onepass_family(s0_v, roles, cb_t, BETA_HIGH, t_max=3)
    res_n_A = settle_onepass_family(s0_n, roles, cb_t, BETA_HIGH, t_max=3)
    pkg_A = _package(res_v_A, res_n_A, gold, tail_k=2)
    assert pkg_A["pred"] in (1, 2) and np.isfinite(pkg_A["tail_v"]) and np.isfinite(pkg_A["tail_n"])

    # variant B (damped, same beta)
    res_v_B = settle_damped(s0_v, roles, cb_t, BETA_HIGH, ALPHA_DAMPING, t_max=4)
    res_n_B = settle_damped(s0_n, roles, cb_t, BETA_HIGH, ALPHA_DAMPING, t_max=4)
    pkg_B = _package(res_v_B, res_n_B, gold, tail_k=2)
    assert pkg_B["pred"] in (1, 2)

    # variant C (fit beta on tiny fit split, then score)
    if len(fit_items) >= 2:
        fb, facc, fgrid, fmargins = _fit_beta(fit_items, roles, cb_normed, cb_t, w2i, ALPHA_DAMPING,
                                              t_max=4, tail_k=2, beta_grid=[1.0, 5.0, 20.0])
        assert fb in [1.0, 5.0, 20.0]
        assert 0.0 <= facc <= 1.0
        print(f"[self-test] tiny beta fit: fitted_beta={fb} fit_acc={facc:.3f}", flush=True)

    # variant D (random control, deterministic rng)
    rng_v = np.random.default_rng(D_SEED_BASE)
    rng_n = np.random.default_rng(D_SEED_BASE + 1)
    res_v_D = settle_random_control(s0_v, roles, N_DIM, ALPHA_DAMPING, t_max=4, rng=rng_v)
    res_n_D = settle_random_control(s0_n, roles, N_DIM, ALPHA_DAMPING, t_max=4, rng=rng_n)
    pkg_D = _package(res_v_D, res_n_D, gold, tail_k=2)
    assert pkg_D["pred"] in (1, 2)

    # arms-must-differ sanity: A vs D raw trajectories must not be bit-identical
    assert res_v_A != res_v_D, "META_RULE_AF VIOLATION: variant A and D trajectories identical"

    pred_baseline = score_baseline_thematic_fit(it, w2i, cb_normed)
    assert pred_baseline in (1, 2)

    iters = _iters_to_converge([1.0, 0.5, 0.04, 0.001])
    assert iters == 3, f"convergence-index formula regression: got {iters}"

    print("[self-test] PASS: real PP loader + real codebook builder + real settle/settle_damped/"
          "settle_random_control + real beta-grid-fit + baseline all exercised at tiny scale",
          flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, "smoke", SMOKE_VOCAB_SIZE, SMOKE_N_DIM, SMOKE_N_TOKENS, SMOKE_SEED,
            SMOKE_N_PER_CLASS, SMOKE_MIN_COUNT)
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, "full", FULL_VOCAB_SIZE, FULL_N_DIM, FULL_N_TOKENS, FULL_SEED,
            FULL_N_PER_CLASS, FULL_MIN_COUNT)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
