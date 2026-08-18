"""Higher-SNR self-generated reliability estimator for codebook consolidation -- SCARCE regime.

Named revival of atom `math::HARD_FAIL_confidence_gated_codebook_consolidation_v1...`
(cell_commit cfb35a854, 2026-07-20). That cell real-data-tested atom 29376 (independent-channel
reliability gate) on the STEP1 codebook build (atom 29368, text8 PPMI+SVD, held-out AUC 0.927)
using a SELF-GENERATED split-half PPMI-stability confidence: HARD_FAIL at abundant data (8M
tokens, gated -0.0218 vs ungated, 3/3 seeds). BUT the atom's own auditor fixed-V=8000 data-scale
sweep showed the MECHANISM is real and brain-consistent (CLS/Yu-Dayan uncertainty-weighting): a
noise-free ORACLE (frequency) proxy shows a clean crossover, +0.018/+0.016/+0.016 AUC at
1M/2M/4M tokens -> -0.020 at 8M. The self-generated split-half signal never achieves a bootstrap-
significant positive lift at any tested scale. The atom's `revival_criterion`: "Revive ONLY with
a HIGHER-SNR self-generated reliability estimator ... tested SPECIFICALLY in the scarce/
intermediate-data regime (~1-4M tokens ...) with per-seed paired bootstrap. Do NOT revive at
abundant data (8M+)."

Pre-reg: preregs/2026-07-20_confidence_gated_codebook_bootstrap_snr_scarce_v1.md (read first).

NEW ESTIMATOR (self-generated; NEVER injected, NEVER ground-truth-derived): bootstrap-averaged
block-shuffled split-half PPMI stability. Split the corpus into ~40 contiguous blocks; draw
B=8 independent RANDOM bipartitions of the blocks into two halves (permute block order with a
fixed integer seed per draw); compute cosine(ppmi_A[w], ppmi_B[w]) per draw; AVERAGE over the B
draws. THEORETICAL@bagging/bootstrap-variance-reduction (Efron & Tibshirani 1993; Breiman 1996
bagging): averaging B partially-independent noisy estimates reduces variance, AND randomizing
which blocks land in which half (vs. a single fixed first/second positional split) removes the
single-split topical/positional confound specific to a concatenated-Wikipedia corpus like text8.

MANDATORY SELF-CHECK (not assumed): this cell ALSO recomputes the ORIGINAL split-half confidence
(identical algorithm, atom 29383's cell) at each scale on the SAME fixed vocabulary/token slice,
and compares spearman-correlation-to-the-noise-free-oracle for both signals
(`snr_improved_by_scale`). The "this estimator IS higher-SNR" premise is a can-fail check, not an
assumption.

FIXED-VOCABULARY / MATCHED-HELD-OUT DESIGN (reuses atom 29383's own auditor discipline, per its
`over_reads_corrected` #2 on the vocab-size confound): `w2i` built ONCE from the LARGEST scale's
token prefix (4,000,000 tokens); held-out TRUE/RANDOM pairs built ONCE from this fixed `w2i`.
ONLY the token count used for cooc/ppmi (and hence both confidence signals + oracle weights)
varies per scale point.

SCALES (scarce regime only; 8M+ explicitly excluded per revival_criterion):
  SCALES = [1_000_000, 2_000_000, 4_000_000]

ARMS (per scale; ONE variable = the per-word weight vector):
  ungated  : weights = 1                              (REAL baseline; mathematical no-op)
  gated    : weights = bootstrap_averaged_confidence(w) (genuine mechanism arm under test)
  shuffled : weights = bootstrap_averaged_confidence(w) permuted across words, FIXED seed 31415
  inverted : weights = 1 - bootstrap_averaged_confidence(w)
  oracle   : weights = minmax(log(1+count(w)))          (diagnostic ceiling; 1 seed; HP-excluded)

HELD-OUT METRIC: identical STEP1 discriminator (held-out TRUE-vs-RANDOM AUC), reused via import
(no reimplementation drift) from experiments/exp_learned_codebook_generalization_gate_v1.py.

SIGNIFICANCE: per-seed paired bootstrap over held-out pair indices (n_boot=2000), identical
method to atom 29383's cell.

PRE-REGISTERED BANDS (see pre-reg for full text; NOT tuned to pass): HP_LIFT_MIN=0.008
CITED@atom-29383 (datascale_sweep_auditor.oracle_minus_ungated: +0.018/+0.016/+0.016 at
1M/2M/4M -- set at ~50% of the noise-free oracle's own measured lift, non-arbitrary).
  HARD_PASS: snr_improved_by_scale True at all 3 scales AND gated beats ungated (lift>=0.008,
    all-seed-positive, boot p<0.05 in >=2/3 seeds) at all 3 scales AND shuffled does not help AND
    inverted significantly underperforms at all 3 scales AND confidence non-degenerate.
  HARD_FAIL_ESTIMATOR_NOT_HIGHER_SNR: snr_improved_by_scale False at >=2/3 scales (checked FIRST;
    distinct from the mechanism question).
  HARD_FAIL_SELF_GENERATED_SNR_BOUND_CONFIRMED: snr genuinely improved but gated still fails to
    beat ungated with significance at all 3 scales (the literal contract HARD-FAIL).
  MIDDLE_BAND: mixed pattern across scales.

DISCRIMINATOR-MUST-SURVIVE-SCALE: Option A -- this cell's FULL scope (1-4M tokens) IS the scarce
regime the mechanism is hypothesized to help in; there is no larger in-scope scale to preview at
(8M+ explicitly excluded per revival_criterion). A fast single-scale/single-seed SMOKE (300k
tokens) precedes FULL to verify the mechanism fires + measure wall-clock.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (TruncatedSVD has no GPU-batched equivalent here).
MEASURED@local .venv timing probe (2026-07-20, this session): build_cooc+build_ppmi at V=6000
over 4M tokens ~2.2s total; single TruncatedSVD(V=6000,N=1024) fit ~29.5s. FULL: 3 scales x
13 units (12 core + 1 oracle) = 39 SVD fits ~ 1170s (~19.5min) + cheap build overhead. Timeout
2400s (40min) for real-world variance margin.

QUEUE: LOCAL/FOREGROUND ONLY -- the local_cpu_queue runner is DEAD per task contract; do NOT
queue via queue_add.sh. Run to completion in the foreground. NO origin push, NO remote-persist.

CELL-TEMPLATE MANDATORY (declared in pre-reg): arms_differ_verified; final_metrics_atomicity=
tmp_replace; except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException);
crlb_n/a declared; cardinality_ok (EXPECTED_N_UNITS=39 FULL / 5 smoke); per-unit failure-class;
deterministic seeding (no hash()/list(set())); real_code_path self-test (constructs REAL
cooc/ppmi/bootstrap-confidence/weighted-SVD at toy scale); numbers tagged MEASURED@/HYPOTHESIZED@/
THEORETICAL@/CITED@; progress_logging=print_flush_true.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

# OMP/OpenBLAS single-thread BEFORE numpy import (bit-repro; OpenBLAS DYNAMIC_ARCH non-determinism)
import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_os.environ.setdefault("MKL_NUM_THREADS", "1")
_os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import scipy.sparse as sp
from scipy.stats import spearmanr
from sklearn.decomposition import TruncatedSVD

ANCHOR_NAME = "exp_confidence_gated_codebook_bootstrap_snr_scarce_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO, "experiments")
if EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENTS_DIR)

# Reuse STEP1 machinery verbatim (no reimplementation drift). CITED@exp_learned_codebook_generalization_gate_v1.py
from exp_learned_codebook_generalization_gate_v1 import (  # noqa: E402
    load_tokens, build_vocab, build_cooc, build_ppmi, _l2norm_rows,
    load_wordsim, load_simlex, cos_pairs, auc_true_vs_random, make_true_random_sets,
)

SEEDS = [7, 13, 19]
CORE_ARMS = ["ungated", "gated", "shuffled", "inverted"]
ALL_ARMS_FULL = CORE_ARMS + ["oracle"]  # oracle runs at seed[0] only (diagnostic, HP_SCOPE-excluded)

SCALES_FULL = [1_000_000, 2_000_000, 4_000_000]     # MEASURED@atom-29383: oracle positive zone
SCALES_SMOKE = [300_000]                             # fast single-scale mechanism-fire check
VOCAB_SIZE = 6000
MIN_COUNT = 5
WINDOW = 5
N_DIM = 1024

B_BOOTSTRAP = 8                # number of independent block-shuffled draws to average
N_BLOCKS_TARGET = 40           # ~corpus split into this many contiguous blocks before bipartition
CONF_BOOT_SEED_BASE = 90210    # fixed; per-draw seed = CONF_BOOT_SEED_BASE + b (deterministic)
SHUFFLE_SEED = 31415           # fixed; permutes confidence across words for the shuffled arm
N_BOOT = 2000
BOOT_SEED_BASE = 20260720

# Pre-registered bands (see pre-reg; declared BEFORE running, NOT tuned to pass).
# CITED@atom-29383 datascale_sweep_auditor.oracle_minus_ungated: +0.018/+0.016/+0.016 at 1M/2M/4M.
HP_LIFT_MIN = 0.008             # ~50% of the noise-free oracle's own measured lift at these scales
HP_DEFICIT_INVERTED_MIN = 0.005
SHUFFLED_HELP_TOL = 0.005       # shuffled must not beat ungated by more than this
BOOT_P_ALPHA = 0.05
CONF_STD_MIN_FAIL = 0.02        # below this (either signal) = degenerate


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
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
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- self-generated confidence
def _cosine_confidence_from_ppmi_halves(ppmi_a, ppmi_b):
    """Shared math: row-wise cosine(ppmi_a[w,:], ppmi_b[w,:]) via sparse dot/norm (no V x V
    densification). PPMI is non-negative so cosine is naturally in [0,1]."""
    dot = np.asarray(ppmi_a.multiply(ppmi_b).sum(axis=1)).ravel()
    norm_a = np.sqrt(np.asarray(ppmi_a.multiply(ppmi_a).sum(axis=1)).ravel())
    norm_b = np.sqrt(np.asarray(ppmi_b.multiply(ppmi_b).sum(axis=1)).ravel())
    denom = norm_a * norm_b
    conf = np.zeros_like(dot)
    nz = denom > 1e-12
    conf[nz] = dot[nz] / denom[nz]
    return np.clip(conf, 0.0, 1.0)


def compute_split_half_confidence(tokens, w2i, window):
    """ORIGINAL (atom 29383) signal, recomputed here for the mandatory higher-SNR comparison.
    Split by POSITION (first half / second half); confidence(w) = cosine(ppmi_A[w,:], ppmi_B[w,:])."""
    n = len(tokens)
    half = n // 2
    tok_a, tok_b = tokens[:half], tokens[half:]
    ppmi_a = build_ppmi(build_cooc(tok_a, w2i, window))
    ppmi_b = build_ppmi(build_cooc(tok_b, w2i, window))
    conf = _cosine_confidence_from_ppmi_halves(ppmi_a, ppmi_b)
    diag = {"n_half_a_tokens": len(tok_a), "n_half_b_tokens": len(tok_b)}
    return conf, diag


def compute_bootstrap_averaged_confidence(tokens, w2i, window, B, n_blocks_target, seed_base):
    """NEW higher-SNR self-generated signal. Split corpus into ~n_blocks_target contiguous
    blocks; draw B independent random bipartitions of the blocks (permute block order with a
    FIXED per-draw seed, no hash()); confidence(w) = MEAN over the B draws of
    cosine(ppmi_A_b[w,:], ppmi_B_b[w,:]). Reduces variance (bagging) and removes the single-split
    positional/topical confound. Deterministic (PROT-023): seed per draw = seed_base + b."""
    n = len(tokens)
    block_size = max(1, n // n_blocks_target)
    n_blocks = n // block_size
    if n_blocks < 4:
        n_blocks = min(4, max(1, n // 2))
        block_size = n // max(1, n_blocks)
    blocks = [tokens[i * block_size:(i + 1) * block_size] for i in range(n_blocks)]
    half_blocks = n_blocks // 2
    if half_blocks < 1:
        half_blocks = 1

    V = len(w2i)
    conf_acc = np.zeros(V, dtype=np.float64)
    per_draw_mean = []
    per_draw_std = []
    for b in range(B):
        rng = np.random.default_rng(seed_base + b)  # deterministic per-draw seed, no hash()
        order = rng.permutation(n_blocks)
        a_idx = sorted(order[:half_blocks].tolist())
        b_idx = sorted(order[half_blocks:].tolist())
        tok_a = [t for i in a_idx for t in blocks[i]]
        tok_b = [t for i in b_idx for t in blocks[i]]
        ppmi_a = build_ppmi(build_cooc(tok_a, w2i, window))
        ppmi_b = build_ppmi(build_cooc(tok_b, w2i, window))
        conf_b = _cosine_confidence_from_ppmi_halves(ppmi_a, ppmi_b)
        conf_acc += conf_b
        per_draw_mean.append(float(conf_b.mean()))
        per_draw_std.append(float(conf_b.std()))
    conf = conf_acc / B
    diag = {
        "B": B, "n_blocks": n_blocks, "block_size": block_size, "half_blocks": half_blocks,
        "per_draw_mean": per_draw_mean, "per_draw_std": per_draw_std,
    }
    return conf, diag


def counts_for_tokens(tokens, w2i):
    """Per-word occurrence counts within `tokens`, restricted to the FIXED vocabulary `w2i`
    (words not in w2i are ignored). Used for the per-scale oracle weight + SNR-comparison."""
    V = len(w2i)
    c = Counter(t for t in tokens if t in w2i)
    counts = np.zeros(V, dtype=np.float64)
    for w, n in c.items():
        counts[w2i[w]] = n
    return counts


def oracle_weights_from_counts(counts):
    """DIAGNOSTIC-ONLY ceiling: min-max normalized log(1+count). THEORETICAL@ zero-split-sampling-
    noise version of word-row reliability. Never touches wordsim/simlex or gold labels. Out of
    HARD_PASS/HARD_FAIL scope (mirrors atom 29383's cell construction exactly)."""
    logc = np.log1p(counts)
    lo, hi = float(logc.min()), float(logc.max())
    if hi - lo < 1e-12:
        return np.ones_like(logc)
    return (logc - lo) / (hi - lo)


# --------------------------------------------------------------------------- weighted codebook build
def build_codebook_weighted(ppmi, weights, N, seed):
    """PPMI rows scaled by `weights` (V,) then TruncatedSVD -> L2-normalized (V,N).
    weights=ones(V) is a mathematical no-op (matches atom 29383's ppmi_svd construction)."""
    V = ppmi.shape[0]
    W = sp.diags(weights)
    ppmi_w = (W @ ppmi).tocsr()
    k = min(N, V - 1)
    svd = TruncatedSVD(n_components=k, algorithm="randomized", n_iter=5, random_state=seed)
    M = svd.fit_transform(ppmi_w).astype(np.float64)
    if k < N:
        M = np.concatenate([M, np.zeros((V, N - k), dtype=np.float64)], axis=1)
    return _l2norm_rows(M)


def arm_weights(arm, confidence, count_weights, V):
    if arm == "ungated":
        return np.ones(V, dtype=np.float64)
    if arm == "gated":
        return confidence
    if arm == "shuffled":
        perm = np.random.default_rng(SHUFFLE_SEED).permutation(V)
        return confidence[perm]
    if arm == "inverted":
        return 1.0 - confidence
    if arm == "oracle":
        return count_weights
    raise ValueError(f"unknown arm {arm!r}")


# --------------------------------------------------------------------------- eval + bootstrap
def eval_codebook(cb, true_pairs, random_pairs):
    cos_t = cos_pairs(cb, true_pairs)
    cos_r = cos_pairs(cb, random_pairs)
    auc = auc_true_vs_random(cos_t, cos_r)
    return {"auc": auc, "cos_true": cos_t, "cos_random": cos_r}


def paired_bootstrap_auc_diff(cos_true_arm, cos_random_arm, cos_true_base, cos_random_base,
                               n_boot, seed):
    """Paired bootstrap over held-out pair indices (cancels common held-out sampling noise)."""
    rng = np.random.default_rng(seed)
    n_t, n_r = len(cos_true_arm), len(cos_random_arm)
    diffs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx_t = rng.integers(0, n_t, n_t)
        idx_r = rng.integers(0, n_r, n_r)
        auc_arm = auc_true_vs_random(cos_true_arm[idx_t], cos_random_arm[idx_r])
        auc_base = auc_true_vs_random(cos_true_base[idx_t], cos_random_base[idx_r])
        diffs[b] = auc_arm - auc_base
    return float(diffs.mean()), float(diffs.std()), float(np.mean(diffs <= 0.0))


# --------------------------------------------------------------------------- per-scale unit
def run_one_scale(output_dir, tokens_scale, w2i, true_pairs, random_pairs, seeds, run_mode, scale_n):
    V = len(w2i)
    ppmi_full = build_ppmi(build_cooc(tokens_scale, w2i, WINDOW))

    splithalf_conf, sh_diag = compute_split_half_confidence(tokens_scale, w2i, WINDOW)
    bootstrap_conf, bs_diag = compute_bootstrap_averaged_confidence(
        tokens_scale, w2i, WINDOW, B_BOOTSTRAP, N_BLOCKS_TARGET, CONF_BOOT_SEED_BASE)
    counts_scale = counts_for_tokens(tokens_scale, w2i)
    count_weights = oracle_weights_from_counts(counts_scale)

    sh_std = float(np.std(splithalf_conf))
    bs_std = float(np.std(bootstrap_conf))
    sh_degenerate = sh_std < CONF_STD_MIN_FAIL
    bs_degenerate = bs_std < CONF_STD_MIN_FAIL

    # MANDATORY higher-SNR check, computed BEFORE any downstream gating result is examined.
    corr_splithalf_oracle = float(spearmanr(splithalf_conf, count_weights).correlation)
    corr_bootstrap_oracle = float(spearmanr(bootstrap_conf, count_weights).correlation)
    snr_improved = abs(corr_bootstrap_oracle) > abs(corr_splithalf_oracle)

    _hb(output_dir, f"scale={scale_n}: splithalf(std={sh_std:.3f}, corr_oracle={corr_splithalf_oracle:.3f}) "
                    f"bootstrap(std={bs_std:.3f}, corr_oracle={corr_bootstrap_oracle:.3f}) "
                    f"snr_improved={snr_improved}")

    per_unit = {}
    code_hashes_by_seed = {}
    arm_agg = {arm: {"auc": []} for arm in ALL_ARMS_FULL}
    n_units_done = 0
    boot_vs_ungated = {}
    expected_n_units_scale = len(CORE_ARMS) * len(seeds) + 1  # +1 oracle (seed[0] only)

    for si, seed in enumerate(seeds):
        code_hashes = {}
        seed_results = {}
        arms_this_seed = ALL_ARMS_FULL if si == 0 else CORE_ARMS
        for arm in arms_this_seed:
            unit_key = f"{arm}__seed{seed}"
            try:
                w = arm_weights(arm, bootstrap_conf, count_weights, V)
                cb = build_codebook_weighted(ppmi_full, w, N_DIM, seed)
                code_hashes[arm] = hashlib.sha256(np.ascontiguousarray(cb).tobytes()).hexdigest()
                res = eval_codebook(cb, true_pairs, random_pairs)
                seed_results[arm] = res
                per_unit[unit_key] = {"arm": arm, "seed": seed, "auc": res["auc"], "failure_class": None}
                arm_agg[arm]["auc"].append(res["auc"])
                n_units_done += 1
                _hb(output_dir, f"scale={scale_n} {unit_key}: AUC={res['auc']:.4f}")
            except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
                per_unit[unit_key] = {"arm": arm, "seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}
                _hb(output_dir, f"scale={scale_n} {unit_key}: FAILED {type(e).__name__}")
        code_hashes_by_seed[seed] = code_hashes

        if "ungated" in seed_results:
            base = seed_results["ungated"]
            for arm in [a for a in arms_this_seed if a != "ungated" and a in seed_results]:
                m, s, p = paired_bootstrap_auc_diff(
                    seed_results[arm]["cos_true"], seed_results[arm]["cos_random"],
                    base["cos_true"], base["cos_random"], N_BOOT, BOOT_SEED_BASE + seed)
                boot_vs_ungated[f"{arm}__seed{seed}"] = {"mean_diff": m, "std_diff": s, "p_le_zero": p}

    arms_differ = True
    arms_differ_detail = {}
    for seed, hd in code_hashes_by_seed.items():
        vals = list(hd.values())
        distinct = len(set(vals)) == len(vals)
        arms_differ_detail[str(seed)] = distinct
        if not distinct:
            arms_differ = False

    def _m(a):
        return float(np.mean(a)) if a else float("nan")

    arm_summary = {arm: {"auc_mean": _m(arm_agg[arm]["auc"]),
                         "auc_std": float(np.std(arm_agg[arm]["auc"])) if len(arm_agg[arm]["auc"]) > 1 else 0.0,
                         "n_seeds": len(arm_agg[arm]["auc"])}
                  for arm in ALL_ARMS_FULL}

    cardinality_ok_scale = (n_units_done == expected_n_units_scale)

    ungated_auc = arm_agg["ungated"]["auc"]
    gated_auc = arm_agg["gated"]["auc"]
    shuffled_auc = arm_agg["shuffled"]["auc"]
    inverted_auc = arm_agg["inverted"]["auc"]

    lift_gated = [g - u for g, u in zip(gated_auc, ungated_auc)]
    deficit_inverted = [u - i for u, i in zip(ungated_auc, inverted_auc)]
    shuffled_vs_ungated = [s - u for s, u in zip(shuffled_auc, ungated_auc)]

    mean_lift_gated = _m(lift_gated)
    mean_deficit_inverted = _m(deficit_inverted)
    mean_shuffled_vs_ungated = _m(shuffled_vs_ungated)

    n_seeds_ran = len(ungated_auc)
    gated_all_positive = n_seeds_ran > 0 and all(x > 0 for x in lift_gated)
    inverted_all_negative_for_ungated = n_seeds_ran > 0 and all(x > 0 for x in deficit_inverted)

    boot_gated_p = [boot_vs_ungated[f"gated__seed{s}"]["p_le_zero"] for s in seeds if f"gated__seed{s}" in boot_vs_ungated]
    boot_inverted_p = [boot_vs_ungated[f"inverted__seed{s}"]["p_le_zero"] for s in seeds if f"inverted__seed{s}" in boot_vs_ungated]
    n_gated_sig = sum(1 for p in boot_gated_p if p < BOOT_P_ALPHA)
    n_inverted_sig = sum(1 for p in boot_inverted_p if (1.0 - p) < BOOT_P_ALPHA)

    return {
        "scale_n": scale_n,
        "V": V,
        "confidence_diagnostics": {
            "splithalf": {"mean": float(np.mean(splithalf_conf)), "std": sh_std, "degenerate": sh_degenerate, **sh_diag},
            "bootstrap": {"mean": float(np.mean(bootstrap_conf)), "std": bs_std, "degenerate": bs_degenerate, **bs_diag},
        },
        "corr_splithalf_oracle": corr_splithalf_oracle,
        "corr_bootstrap_oracle": corr_bootstrap_oracle,
        "snr_improved": snr_improved,
        "arm_summary": arm_summary,
        "per_unit": per_unit,
        "boot_vs_ungated": boot_vs_ungated,
        "arms_differ_verified": arms_differ,
        "arms_differ_detail": arms_differ_detail,
        "cardinality_ok": cardinality_ok_scale,
        "expected_n_units": expected_n_units_scale,
        "n_units_done": n_units_done,
        "mean_lift_gated": mean_lift_gated,
        "mean_deficit_inverted": mean_deficit_inverted,
        "mean_shuffled_vs_ungated": mean_shuffled_vs_ungated,
        "gated_all_positive": gated_all_positive,
        "inverted_all_negative_for_ungated": inverted_all_negative_for_ungated,
        "n_gated_sig": n_gated_sig,
        "n_inverted_sig": n_inverted_sig,
        "n_seeds_ran": n_seeds_ran,
    }


# --------------------------------------------------------------------------- runner
def run(output_dir, scales, seeds, run_mode):
    t0 = time.perf_counter()
    expected_n_units = len(scales) * (len(CORE_ARMS) * len(seeds) + 1)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    max_scale = max(scales)
    _hb(output_dir, f"loading {max_scale} tokens from text8 (fixed-vocab source)")
    tokens_max = load_tokens(max_scale)
    _hb(output_dir, f"loaded {len(tokens_max)} tokens; building FIXED vocab (V<={VOCAB_SIZE})")
    w2i, _global_counts = build_vocab(tokens_max, VOCAB_SIZE, MIN_COUNT)
    V = len(w2i)
    _hb(output_dir, f"fixed vocab V={V}")

    ws_pairs = load_wordsim(w2i)
    sl_pairs = load_simlex(w2i)
    if len(ws_pairs) < 30 or len(sl_pairs) < 30:
        raise RuntimeError(
            f"REFERENCE_COVERAGE_TOO_LOW: wordsim={len(ws_pairs)} simlex={len(sl_pairs)} (need >=30 each)")
    combined = ws_pairs + sl_pairs
    true_pairs, random_pairs = make_true_random_sets(combined, w2i, seed=0)
    _hb(output_dir, f"FIXED held-out sets: TRUE={len(true_pairs)} RANDOM={len(random_pairs)} "
                    f"wordsim={len(ws_pairs)} simlex={len(sl_pairs)}")

    per_scale = {}
    n_units_done_total = 0
    for scale_n in scales:
        _hb(output_dir, f"=== scale={scale_n} tokens ===")
        tokens_scale = tokens_max[:scale_n]
        res = run_one_scale(output_dir, tokens_scale, w2i, true_pairs, random_pairs, seeds, run_mode, scale_n)
        per_scale[str(scale_n)] = res
        n_units_done_total += res["n_units_done"]

    cardinality_ok = all(per_scale[str(s)]["cardinality_ok"] for s in scales) and (
        n_units_done_total == expected_n_units)
    arms_differ = all(per_scale[str(s)]["arms_differ_verified"] for s in scales)

    n_scales = len(scales)
    snr_improved_scales = [per_scale[str(s)]["snr_improved"] for s in scales]
    n_snr_improved = sum(1 for x in snr_improved_scales if x)
    snr_improved_majority = n_snr_improved >= (2 * n_scales + 2) // 3 if n_scales == 3 else n_snr_improved >= (n_scales + 1) // 2

    lift_ok_scales = [per_scale[str(s)]["mean_lift_gated"] >= HP_LIFT_MIN
                      and per_scale[str(s)]["gated_all_positive"]
                      and per_scale[str(s)]["n_gated_sig"] >= 2
                      for s in scales]
    all_lift_ok = all(lift_ok_scales)

    shuffled_ok_scales = [per_scale[str(s)]["mean_shuffled_vs_ungated"] <= SHUFFLED_HELP_TOL for s in scales]
    all_shuffled_ok = all(shuffled_ok_scales)

    inverted_ok_scales = [per_scale[str(s)]["mean_deficit_inverted"] >= HP_DEFICIT_INVERTED_MIN
                          and per_scale[str(s)]["inverted_all_negative_for_ungated"]
                          and per_scale[str(s)]["n_inverted_sig"] >= 2
                          for s in scales]
    all_inverted_ok = all(inverted_ok_scales)

    conf_ok_scales = [(not per_scale[str(s)]["confidence_diagnostics"]["splithalf"]["degenerate"])
                      and (not per_scale[str(s)]["confidence_diagnostics"]["bootstrap"]["degenerate"])
                      for s in scales]
    all_conf_ok = all(conf_ok_scales)

    # Any-scale total lift failure (for the literal HARD-FAIL contract wording): gated fails
    # to beat ungated with significance at EVERY scale (the "even higher-SNR still fails
    # everywhere" outcome).
    lift_fails_everywhere = all(not x for x in lift_ok_scales)

    ungated_by_scale = [per_scale[str(s)]["arm_summary"]["ungated"]["auc_mean"] for s in scales]
    ungated_auc_monotone_with_scale = all(
        ungated_by_scale[i] <= ungated_by_scale[i + 1] + 1e-9 for i in range(len(ungated_by_scale) - 1))

    hard_pass_conditions = (
        cardinality_ok and arms_differ and all_conf_ok and snr_improved_majority
        and all_lift_ok and all_shuffled_ok and all_inverted_ok
    )

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not all_conf_ok:
        verdict = "HARD_FAIL_DEGENERATE_CONFIDENCE_SIGNAL"
    elif not snr_improved_majority:
        verdict = "HARD_FAIL_ESTIMATOR_NOT_HIGHER_SNR"
    elif hard_pass_conditions:
        verdict = "HARD_PASS"
    elif snr_improved_majority and lift_fails_everywhere:
        verdict = "HARD_FAIL_SELF_GENERATED_SNR_BOUND_CONFIRMED"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    per_scale_summary_str = " | ".join(
        f"{s}tok: lift={per_scale[str(s)]['mean_lift_gated']:+.4f}(sig={per_scale[str(s)]['n_gated_sig']}/{per_scale[str(s)]['n_seeds_ran']}) "
        f"snr_imp={per_scale[str(s)]['snr_improved']} corr_bs={per_scale[str(s)]['corr_bootstrap_oracle']:.3f} "
        f"corr_sh={per_scale[str(s)]['corr_splithalf_oracle']:.3f}"
        for s in scales
    )
    verdict_msg = f"{verdict} | {per_scale_summary_str} | ungated_monotone={ungated_auc_monotone_with_scale}"

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:180]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "scales": scales, "vocab_size": VOCAB_SIZE, "V": V, "N": N_DIM, "window": WINDOW,
            "min_count": MIN_COUNT, "seeds": seeds, "B_bootstrap": B_BOOTSTRAP,
            "n_blocks_target": N_BLOCKS_TARGET,
            "n_wordsim_pairs": len(ws_pairs), "n_simlex_pairs": len(sl_pairs),
            "n_true_pairs": len(true_pairs), "n_random_pairs": len(random_pairs),
        },
        "per_scale": per_scale,
        "bands": {
            "HP_LIFT_MIN": HP_LIFT_MIN, "HP_DEFICIT_INVERTED_MIN": HP_DEFICIT_INVERTED_MIN,
            "SHUFFLED_HELP_TOL": SHUFFLED_HELP_TOL, "BOOT_P_ALPHA": BOOT_P_ALPHA,
            "CONF_STD_MIN_FAIL": CONF_STD_MIN_FAIL,
        },
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "n_units_done": n_units_done_total,
        "arms_differ_verified": arms_differ,
        "snr_improved_by_scale": {str(s): per_scale[str(s)]["snr_improved"] for s in scales},
        "snr_improved_majority": snr_improved_majority,
        "ungated_auc_monotone_with_scale": ungated_auc_monotone_with_scale,
        "hp_scope": {"ungated": [], "gated": ["hard_pass_lift", "hard_fail_no_lift"],
                    "shuffled": ["must_not_help"], "inverted": ["must_hurt"], "oracle": []},
        "crlb_n/a": "distributional-geometry generalization test; no argmax/capacity noise floor",
        "self_generated_confidence_note": (
            "both splithalf and bootstrap confidence computed strictly from tokens+w2i+window; "
            "never passed wordsim/simlex or any gold label; computed before held-out eval step"),
        "prior_art": "atom-29383 (split-half predecessor, HARD_FAIL, revival_criterion source); "
                     "Efron&Tibshirani1993 bootstrap; Breiman1996 bagging; Yu&Dayan2005; "
                     "Kepecs2008/Lak2014; Lisman&Grace2005; McClelland-McNaughton-OReilly1995 CLS",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test at toy scale: exercises the REAL bootstrap-averaged
    confidence computation + split-half comparison + weighted-SVD codebook builder for ALL 5
    arms (no synthetic-only branch)."""
    print("[self-test] building tiny toy corpus", flush=True)
    base = (["cat", "pet", "feline", "purr", "whiskers"] * 8
            + ["dog", "pet", "canine", "bark", "loyal"] * 8
            + ["car", "road", "engine", "wheel", "drive"] * 8
            + ["king", "queen", "royal", "crown", "throne"] * 8)
    rng = np.random.default_rng(0)
    tokens = list(rng.permutation(base * 6))
    w2i, counts = build_vocab(tokens, vocab_size=50, min_count=1)
    V = len(w2i)
    assert V >= 12, f"toy vocab too small V={V}"
    cooc = build_cooc(tokens, w2i, window=3)
    ppmi = build_ppmi(cooc)
    assert ppmi.nnz > 0, "empty ppmi"

    # Real code path: both confidence signals.
    sh_conf, sh_diag = compute_split_half_confidence(tokens, w2i, window=3)
    assert sh_conf.shape == (V,) and np.all(np.isfinite(sh_conf))
    assert np.all((sh_conf >= 0.0) & (sh_conf <= 1.0))

    bs_conf, bs_diag = compute_bootstrap_averaged_confidence(
        tokens, w2i, window=3, B=4, n_blocks_target=8, seed_base=CONF_BOOT_SEED_BASE)
    assert bs_conf.shape == (V,), f"bootstrap confidence shape {bs_conf.shape}"
    assert np.all(np.isfinite(bs_conf)), "bootstrap confidence has non-finite values"
    assert np.all((bs_conf >= 0.0) & (bs_conf <= 1.0)), "bootstrap confidence out of [0,1]"
    assert bs_diag["B"] == 4 and bs_diag["n_blocks"] >= 4
    print(f"[self-test] splithalf: mean={sh_conf.mean():.3f} std={sh_conf.std():.3f} | "
          f"bootstrap: mean={bs_conf.mean():.3f} std={bs_conf.std():.3f}", flush=True)

    # Determinism check: same seed_base -> identical bootstrap confidence (no hash()-derived RNG).
    bs_conf2, _ = compute_bootstrap_averaged_confidence(
        tokens, w2i, window=3, B=4, n_blocks_target=8, seed_base=CONF_BOOT_SEED_BASE)
    assert np.allclose(bs_conf, bs_conf2), "bootstrap confidence not deterministic across identical calls"

    counts_scale = counts_for_tokens(tokens, w2i)
    count_weights = oracle_weights_from_counts(counts_scale)
    assert count_weights.shape == (V,)
    assert np.all((count_weights >= 0.0) & (count_weights <= 1.0 + 1e-9))

    # SNR-comparison machinery (real code path, toy scale; not asserting direction here -- toy
    # corpus is too small for a meaningful SNR claim, only exercising that it runs & is finite).
    corr_sh = spearmanr(sh_conf, count_weights).correlation
    corr_bs = spearmanr(bs_conf, count_weights).correlation
    assert np.isfinite(corr_sh) and np.isfinite(corr_bs), "correlation computation produced non-finite"

    N = 8  # toy: N < V (real run V>>N); exercises SVD cap+pad path too
    hashes = {}
    for arm in ALL_ARMS_FULL:
        w = arm_weights(arm, bs_conf, count_weights, V)
        assert w.shape == (V,), f"{arm} weight shape {w.shape}"
        cb = build_codebook_weighted(ppmi, w, N, seed=7)
        assert cb.shape == (V, N), f"{arm} codebook shape {cb.shape}"
        assert np.all(np.isfinite(cb)), f"{arm} produced non-finite"
        nrm = np.linalg.norm(cb, axis=1)
        assert np.allclose(nrm[nrm > 0], 1.0, atol=1e-5), f"{arm} rows not L2-normalized"
        hashes[arm] = hashlib.sha256(np.ascontiguousarray(cb).tobytes()).hexdigest()
    assert len(set(hashes.values())) == len(hashes), f"META_RULE_AF: arm codebooks not bit-distinct {hashes}"

    cb_direct = build_codebook_weighted(ppmi, np.ones(V), N, seed=7)
    cb_ungated = build_codebook_weighted(ppmi, arm_weights("ungated", bs_conf, count_weights, V), N, seed=7)
    assert np.allclose(cb_direct, cb_ungated), "ungated arm is not the weights=1 no-op"

    ct = np.array([0.9, 0.8, 0.7, 0.6])
    cr = np.array([0.1, 0.2, 0.3, 0.05])
    m, s, p = paired_bootstrap_auc_diff(ct, cr, ct, cr, n_boot=200, seed=1)
    assert abs(m) < 1e-9, f"self-diff bootstrap mean should be exactly 0, got {m}"

    ws = load_wordsim(w2i)
    sl = load_simlex(w2i)
    assert isinstance(ws, list) and isinstance(sl, list)
    tp, rp = make_true_random_sets([(0, 1, 0.9), (2, 3, 0.8), (0, 2, 0.1), (1, 3, 0.2)], w2i, seed=0)
    res = eval_codebook(cb_direct, tp, rp)
    assert 0.0 <= res["auc"] <= 1.0

    print("[self-test] PASS: bootstrap-averaged confidence + splithalf comparison + 5-arm "
          "weighted-SVD + bootstrap + eval + determinism all exercised", flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, scales=SCALES_SMOKE, seeds=[SEEDS[0]], run_mode="smoke")
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, scales=SCALES_FULL, seeds=SEEDS, run_mode="full")
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
