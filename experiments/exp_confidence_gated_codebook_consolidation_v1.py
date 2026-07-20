"""Confidence-gated codebook consolidation -- real-data validation of the reliability-gate CG.

Real-data test of atom 29376 (independent-channel reliability gate, validated only on an INJECTED
synthetic-error regime; own scope bound states "real-data untested"). Gates WHICH per-word
co-occurrence rows consolidate into the STEP1 codebook (exp_learned_codebook_generalization_gate_v1.py,
atom 29368, text8 PPMI+SVD, held-out word-similarity AUC 0.927) by a SELF-GENERATED (never
injected, never ground-truth-derived) reliability signal, then re-measures the SAME held-out
TRUE-vs-RANDOM AUC that already proved non-construction-determined for the ungated codebook.

Pre-reg: preregs/2026-07-20_confidence_gated_codebook_consolidation_v1.md (read first -- states the
deviation from the brain-drill note's suggested LCCP-S1 signal + exact bands + full rationale).
Brain drill: notes/research_brain_confidence_weighted_learning_consolidation_2026-07-20.md
  (Yu & Dayan 2005 precision-weighting; Kepecs 2008 / Lak 2014 confidence-as-byproduct;
  Lisman & Grace 2005 hippocampal-VTA salience-gated LTP; McClelland-McNaughton-O'Reilly 1995 CLS
  salience-weighted replay/consolidation).

SIGNAL (self-generated; NEVER injected, NEVER ground-truth-derived; computed strictly from corpus
co-occurrence, never touches wordsim353/simlex999): per-word SPLIT-HALF PPMI-STABILITY. Split the
token stream in half by POSITION; build cooc/PPMI independently per half over the SAME fixed
vocabulary; confidence(w) = cosine(ppmi_half_A[w,:], ppmi_half_B[w,:]) (naturally in [0,1] since
PPMI is non-negative). A genuine test-retest / distributional-consistency signal -- does this
word's co-occurrence profile replicate across two disjoint corpus slices?

GATE: multiplicative row-scale on the PPMI matrix BEFORE TruncatedSVD (diag(weights) @ ppmi), then
the identical SVD + L2-normalize STEP1 already uses for its ppmi_svd arm. Uniform weights=1 is a
mathematical no-op relative to STEP1's own arm (the `ungated` arm here IS a Gate-D positive-control
reproduction of STEP1's 0.927).

ARMS (ONE variable = the per-word weight vector; corpus/vocab/window/N/seeds/held-out pairs shared):
  ungated  : weights = 1                         (REAL baseline; Gate-D repro of STEP1's 0.927)
  gated    : weights = confidence(w)             (genuine mechanism arm)
  shuffled : weights = confidence(w) permuted across words, FIXED seed 31415 (must NOT help)
  inverted : weights = 1 - confidence(w)          (must HURT -- Ackerman-et-al miscalibration probe)
  oracle   : weights = minmax(log(1+count(w)))   (diagnostic ceiling: zero-split-noise version of
             the SAME construct via frequency; NOT a gold-label oracle; out of HARD_PASS scope)

HELD-OUT METRIC: identical STEP1 discriminator (held-out TRUE-vs-RANDOM AUC on wordsim353+simlex999
top-tercile pairs vs frequency-matched random re-pairings), reused via import (no reimplementation
drift) from experiments/exp_learned_codebook_generalization_gate_v1.py.

SIGNIFICANCE: per-seed paired bootstrap over held-out pair indices (n_boot=2000) in addition to the
3-seed sign-consistency check, since ungated sits near an operative ceiling (0.927) and the expected
win (per the drill note) is a small-but-consistent lift, not a large swing.

PRE-REGISTERED BANDS (see pre-reg for full text; NOT tuned to pass):
  HARD_PASS: gated beats ungated by >=0.01 mean AUC, positive sign all 3 seeds, bootstrap p<0.05 in
    >=2/3 seeds; shuffled collapses to ungated (|diff|<0.01); inverted underperforms ungated by
    >=0.01, negative sign all 3 seeds, bootstrap p<0.05 in >=2/3 seeds; Gate-D repro |ungated-0.927|
    <=0.02; confidence distribution non-degenerate (std>=0.05).
  HARD_FAIL: gated within noise of ungated (no consistent >=0.01 lift) -- MOST LIKELY per drill note's
    own deflated P (~0.35); OR gated underperforms ungated for real; OR shuffled ~= gated (generic
    regularization artifact, not signal content); OR confidence degenerate (std<0.02); OR Gate-D
    repro fails (|ungated-0.927|>0.05, pipeline drift not a real result).
  MIDDLE_BAND: anything else.

DISCRIMINATOR-MUST-SURVIVE-SCALE: Option B+C hybrid. Baseline is near-ceiling at FULL (less
separating room than at SMOKE where historical baseline ~0.850); smoke previews ARM ORDERING only,
not the exact HARD_PASS margin (only assessable at FULL against the near-ceiling baseline).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (TruncatedSVD has no GPU-batched equivalent here;
Stage-3 diagnostic GATE question per compute-proportionality, not a magnitude-of-mechanism claim).
FULL: 4 core arms x 3 seeds (12 fits) + oracle x 1 seed (13 fits) + 1 full-corpus + 1 half-split
cooc/PPMI build. MEASURED@scratch timing probe (V=10000,k=1024,nnz~2M synthetic): ~26s/SVD-fit ->
target wall ~8-12 min FULL. Timeout 1500s for real-world PPMI-density variance.

QUEUE: LOCAL/queue only -- NO origin push, NO remote-persist (per task contract; remote queues
require an origin push which is out of scope here). SMOKE = foreground to completion. FULL =
local_cpu_queue via queue_add.sh (deliberate, flagged deviation from the standing
"local_cpu_queue = smoke only" rule -- remote is structurally unavailable under the no-push
contract; see pre-reg).

CELL-TEMPLATE MANDATORY (declared in pre-reg): arms_differ_verified; final_metrics_atomicity=
tmp_replace; except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException);
crlb_n/a declared; cardinality_ok (EXPECTED_N_UNITS=13); per-unit failure-class; deterministic
seeding (no hash()/list(set())); real_code_path self-test (constructs REAL cooc/ppmi/weighted-SVD
at toy scale); numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@; progress_logging=
print_flush_true.

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
from datetime import datetime, timezone

import numpy as np
import scipy.sparse as sp
from sklearn.decomposition import TruncatedSVD

ANCHOR_NAME = "exp_confidence_gated_codebook_consolidation_v1"
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

SHUFFLE_SEED = 31415          # fixed; permutes confidence across words for the shuffled arm
N_BOOT = 2000
BOOT_SEED_BASE = 20260720

# Pre-registered bands (see pre-reg; declared BEFORE running, NOT tuned to pass).
HP_LIFT_GATED = 0.01          # gated - ungated mean AUC lift floor for HARD_PASS
HP_DEFICIT_INVERTED = 0.01    # ungated - inverted mean AUC deficit floor for HARD_PASS
SHUFFLED_COLLAPSE_TOL = 0.01  # |shuffled - ungated| below this = "collapsed to ungated"
SHUFFLED_VS_GATED_ARTIFACT_TOL = 0.005  # |shuffled - gated| below this at HF check = generic artifact
GATE_D_REPRO_TARGET_FULL = 0.927   # MEASURED@data/exp_learned_codebook_generalization_gate_v1/metrics.json:
                                    # arm_summary.ppmi_svd.auc_mean (STEP1 FULL, matched regime n_tokens=8M/V=10000)
GATE_D_REPRO_TARGET_SMOKE = 0.8496097560975611  # MEASURED@data/exp_learned_codebook_generalization_gate_v1_smoke/
                                    # metrics.json:arm_summary.ppmi_svd.auc_mean (STEP1 SMOKE, matched regime)
GATE_D_REPRO_TOL_PASS = 0.02
GATE_D_REPRO_TOL_FAIL = 0.05
CONF_STD_MIN_PASS = 0.05
CONF_STD_MIN_FAIL = 0.02
BOOT_P_ALPHA = 0.05
SHUFFLED_HELP_TOL = 0.005      # shuffled must not BEAT ungated by more than this (worse-than-ungated is
                                # explicitly PERMITTED per the drill note: "collapse to indistinguishable
                                # from ungated, OR WORSE" -- only "shuffled helping" is disqualifying)


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
def compute_split_half_confidence(tokens, w2i, window):
    """SELF-GENERATED reliability signal. NEVER touches wordsim/simlex or any gold label -- takes
    ONLY the corpus token stream + the fixed vocabulary. Splits by POSITION (first half / second
    half); confidence(w) = cosine(ppmi_half_A[w,:], ppmi_half_B[w,:]) via sparse row-wise dot/norm
    (never densifies V x V). Returns (conf: (V,) in [0,1], diag: dict of build stats)."""
    n = len(tokens)
    half = n // 2
    tok_a, tok_b = tokens[:half], tokens[half:]
    cooc_a = build_cooc(tok_a, w2i, window)
    cooc_b = build_cooc(tok_b, w2i, window)
    ppmi_a = build_ppmi(cooc_a)
    ppmi_b = build_ppmi(cooc_b)
    # Row-wise dot/norm via sparse ops (no V x V densification).
    dot = np.asarray(ppmi_a.multiply(ppmi_b).sum(axis=1)).ravel()
    norm_a = np.sqrt(np.asarray(ppmi_a.multiply(ppmi_a).sum(axis=1)).ravel())
    norm_b = np.sqrt(np.asarray(ppmi_b.multiply(ppmi_b).sum(axis=1)).ravel())
    denom = norm_a * norm_b
    conf = np.zeros_like(dot)
    nz = denom > 1e-12
    conf[nz] = dot[nz] / denom[nz]
    conf = np.clip(conf, 0.0, 1.0)  # numerical safety; PPMI non-negative so cosine in [0,1] already
    diag = {
        "n_half_a_tokens": len(tok_a), "n_half_b_tokens": len(tok_b),
        "ppmi_a_nnz": int(ppmi_a.nnz), "ppmi_b_nnz": int(ppmi_b.nnz),
        "n_zero_row_words": int((~nz).sum()),
    }
    return conf, diag


def oracle_weights_from_counts(counts):
    """DIAGNOSTIC-ONLY ceiling: min-max normalized log(1+count). THEORETICAL@ zero-split-sampling-
    noise version of 'this word has enough evidence to trust its co-occurrence profile' -- word
    frequency correlates with true distributional-profile reliability without the 2-way-split's own
    estimation noise. Never touches wordsim/simlex or gold labels. Out of HARD_PASS/HARD_FAIL scope."""
    logc = np.log1p(counts)
    lo, hi = float(logc.min()), float(logc.max())
    if hi - lo < 1e-12:
        return np.ones_like(logc)
    return (logc - lo) / (hi - lo)


# --------------------------------------------------------------------------- weighted codebook build
def build_codebook_weighted(ppmi, weights, N, seed):
    """PPMI rows scaled by `weights` (V,) then TruncatedSVD -> L2-normalized (V,N).
    weights=ones(V) is a mathematical no-op (Gate-D positive-control target: matches STEP1's own
    ppmi_svd arm construction exactly)."""
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
def eval_codebook(cb, true_pairs, random_pairs, ws_pairs, sl_pairs):
    cos_t = cos_pairs(cb, true_pairs)
    cos_r = cos_pairs(cb, random_pairs)
    auc = auc_true_vs_random(cos_t, cos_r)
    from scipy.stats import spearmanr
    ws_cos = cos_pairs(cb, ws_pairs)
    ws_s = np.array([p[2] for p in ws_pairs]) if ws_pairs else np.zeros(0)
    sl_cos = cos_pairs(cb, sl_pairs)
    sl_s = np.array([p[2] for p in sl_pairs]) if sl_pairs else np.zeros(0)
    ws_sp = float(spearmanr(ws_cos, ws_s).correlation) if len(ws_pairs) > 2 else 0.0
    sl_sp = float(spearmanr(sl_cos, sl_s).correlation) if len(sl_pairs) > 2 else 0.0
    return {"auc": auc, "ws_spearman": ws_sp, "sl_spearman": sl_sp,
            "cos_true": cos_t, "cos_random": cos_r}


def paired_bootstrap_auc_diff(cos_true_arm, cos_random_arm, cos_true_base, cos_random_base,
                               n_boot, seed):
    """Paired bootstrap over held-out pair indices: resample the SAME indices for arm vs base each
    draw (cancels common held-out sampling noise). Returns (mean_diff, std_diff, p_le_zero)."""
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


# --------------------------------------------------------------------------- runner
def run(output_dir, n_tokens, vocab_size, N, window, min_count, seeds, run_mode):
    t0 = time.perf_counter()
    expected_n_units = len(CORE_ARMS) * len(seeds) + 1  # +1 oracle (seed[0] only)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    _hb(output_dir, f"loading {n_tokens} tokens from text8")
    tokens = load_tokens(n_tokens)
    _hb(output_dir, f"loaded {len(tokens)} tokens; building vocab (V<={vocab_size})")
    w2i, counts = build_vocab(tokens, vocab_size, min_count)
    V = len(w2i)
    _hb(output_dir, f"vocab V={V}; building FULL cooc/ppmi (window={window})")
    cooc_full = build_cooc(tokens, w2i, window)
    ppmi_full = build_ppmi(cooc_full)
    _hb(output_dir, f"ppmi_full nnz={ppmi_full.nnz}; computing split-half self-generated confidence")

    confidence, conf_diag = compute_split_half_confidence(tokens, w2i, window)
    conf_std = float(np.std(confidence))
    conf_mean = float(np.mean(confidence))
    hist, edges = np.histogram(confidence, bins=20, range=(0.0, 1.0))
    max_bin_frac = float(hist.max() / max(1, V))
    degenerate = (conf_std < CONF_STD_MIN_FAIL) or (max_bin_frac > 0.95)
    _hb(output_dir, f"confidence: mean={conf_mean:.3f} std={conf_std:.3f} max_bin_frac={max_bin_frac:.3f} "
                    f"degenerate={degenerate}")

    count_weights = oracle_weights_from_counts(counts)

    ws_pairs = load_wordsim(w2i)
    sl_pairs = load_simlex(w2i)
    if len(ws_pairs) < 30 or len(sl_pairs) < 30:
        raise RuntimeError(
            f"REFERENCE_COVERAGE_TOO_LOW: wordsim={len(ws_pairs)} simlex={len(sl_pairs)} "
            f"(need >=30 each); raise vocab_size/n_tokens")
    combined = ws_pairs + sl_pairs
    true_pairs, random_pairs = make_true_random_sets(combined, w2i, seed=0)
    _hb(output_dir, f"held-out sets: TRUE={len(true_pairs)} RANDOM={len(random_pairs)} "
                    f"wordsim={len(ws_pairs)} simlex={len(sl_pairs)}")

    per_unit = {}
    code_hashes_by_seed = {}
    arm_agg = {arm: {"auc": [], "ws_spearman": [], "sl_spearman": []} for arm in ALL_ARMS_FULL}
    n_units_done = 0
    boot_vs_ungated = {}  # (arm, seed) -> {mean_diff, std_diff, p_le_zero}

    for si, seed in enumerate(seeds):
        code_hashes = {}
        seed_results = {}
        arms_this_seed = ALL_ARMS_FULL if si == 0 else CORE_ARMS
        for arm in arms_this_seed:
            unit_key = f"{arm}__seed{seed}"
            try:
                w = arm_weights(arm, confidence, count_weights, V)
                cb = build_codebook_weighted(ppmi_full, w, N, seed)
                code_hashes[arm] = hashlib.sha256(np.ascontiguousarray(cb).tobytes()).hexdigest()
                res = eval_codebook(cb, true_pairs, random_pairs, ws_pairs, sl_pairs)
                seed_results[arm] = res
                per_unit[unit_key] = {
                    "arm": arm, "seed": seed, "auc": res["auc"],
                    "ws_spearman": res["ws_spearman"], "sl_spearman": res["sl_spearman"],
                    "failure_class": None,
                }
                arm_agg[arm]["auc"].append(res["auc"])
                arm_agg[arm]["ws_spearman"].append(res["ws_spearman"])
                arm_agg[arm]["sl_spearman"].append(res["sl_spearman"])
                n_units_done += 1
                _hb(output_dir, f"{unit_key}: AUC={res['auc']:.4f} ws_sp={res['ws_spearman']:.3f}")
            except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
                per_unit[unit_key] = {
                    "arm": arm, "seed": seed,
                    "failure_class": f"{type(e).__name__}: {str(e)[:200]}",
                }
                _hb(output_dir, f"{unit_key}: FAILED {type(e).__name__}")
        code_hashes_by_seed[seed] = code_hashes

        # Paired bootstrap vs ungated (only if both ungated + comparison arms landed this seed).
        if "ungated" in seed_results:
            base = seed_results["ungated"]
            for arm in [a for a in arms_this_seed if a != "ungated" and a in seed_results]:
                m, s, p = paired_bootstrap_auc_diff(
                    seed_results[arm]["cos_true"], seed_results[arm]["cos_random"],
                    base["cos_true"], base["cos_random"], N_BOOT, BOOT_SEED_BASE + seed)
                boot_vs_ungated[f"{arm}__seed{seed}"] = {"mean_diff": m, "std_diff": s, "p_le_zero": p}
                _hb(output_dir, f"bootstrap {arm} vs ungated seed{seed}: diff={m:+.4f} p_le_zero={p:.4f}")

    # ARMS-MUST-DIFFER (META_RULE_AF): within each seed, all landed arm codebooks bit-distinct.
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
                         "ws_spearman_mean": _m(arm_agg[arm]["ws_spearman"]),
                         "sl_spearman_mean": _m(arm_agg[arm]["sl_spearman"]),
                         "n_seeds": len(arm_agg[arm]["auc"])}
                  for arm in ALL_ARMS_FULL}

    cardinality_ok = (n_units_done == expected_n_units)

    ungated_auc = arm_agg["ungated"]["auc"]
    gated_auc = arm_agg["gated"]["auc"]
    shuffled_auc = arm_agg["shuffled"]["auc"]
    inverted_auc = arm_agg["inverted"]["auc"]

    gate_d_target = GATE_D_REPRO_TARGET_FULL if run_mode == "full" else GATE_D_REPRO_TARGET_SMOKE
    gate_d_repro_gap = abs(arm_summary["ungated"]["auc_mean"] - gate_d_target) if ungated_auc else float("nan")

    lift_gated = [g - u for g, u in zip(gated_auc, ungated_auc)]
    deficit_inverted = [u - i for u, i in zip(ungated_auc, inverted_auc)]
    shuffled_vs_ungated = [s - u for s, u in zip(shuffled_auc, ungated_auc)]
    shuffled_vs_gated = [s - g for s, g in zip(shuffled_auc, gated_auc)]

    mean_lift_gated = _m(lift_gated)
    mean_deficit_inverted = _m(deficit_inverted)
    mean_shuffled_vs_ungated = _m(shuffled_vs_ungated)
    mean_shuffled_vs_gated = _m(shuffled_vs_gated)

    n_seeds_ran = len(ungated_auc)
    gated_all_positive = n_seeds_ran > 0 and all(x > 0 for x in lift_gated)
    inverted_all_negative_for_ungated = n_seeds_ran > 0 and all(x > 0 for x in deficit_inverted)  # ungated-inverted>0

    boot_gated_p = [boot_vs_ungated[f"gated__seed{s}"]["p_le_zero"]
                    for s in seeds if f"gated__seed{s}" in boot_vs_ungated]
    boot_inverted_p = [boot_vs_ungated[f"inverted__seed{s}"]["p_le_zero"]
                       for s in seeds if f"inverted__seed{s}" in boot_vs_ungated]
    # For inverted: bootstrap diff computed as inverted-minus-ungated; want inverted < ungated i.e.
    # diff<0 -> p_le_zero close to 1 means diff usually <=0 which is what we WANT here (inverted lower);
    # define beats-significance for inverted as P(diff>=0) small, i.e. (1-p_le_zero) small.
    n_gated_sig = sum(1 for p in boot_gated_p if p < BOOT_P_ALPHA)
    n_inverted_sig = sum(1 for p in boot_inverted_p if (1.0 - p) < BOOT_P_ALPHA)

    gate_d_ok_pass = gate_d_repro_gap <= GATE_D_REPRO_TOL_PASS if not np.isnan(gate_d_repro_gap) else False
    gate_d_ok_fail = gate_d_repro_gap > GATE_D_REPRO_TOL_FAIL if not np.isnan(gate_d_repro_gap) else True

    conf_dist_pass = conf_std >= CONF_STD_MIN_PASS and max_bin_frac <= 0.95
    conf_dist_fail = degenerate

    # Shuffled must NOT help (beat ungated); landing AT or BELOW ungated is explicitly permitted
    # (drill note: "collapse to indistinguishable from ungated, OR WORSE").
    shuffled_does_not_help = mean_shuffled_vs_ungated <= SHUFFLED_HELP_TOL

    hard_pass_conditions = (
        cardinality_ok and arms_differ and n_seeds_ran == len(seeds)
        and mean_lift_gated >= HP_LIFT_GATED and gated_all_positive and n_gated_sig >= 2
        and shuffled_does_not_help
        and mean_deficit_inverted >= HP_DEFICIT_INVERTED and inverted_all_negative_for_ungated
        and n_inverted_sig >= 2
        and gate_d_ok_pass and conf_dist_pass
    )

    hard_fail_conditions = (
        (not cardinality_ok) or (not arms_differ)
        or conf_dist_fail or gate_d_ok_fail
        or (n_seeds_ran == len(seeds) and mean_lift_gated < HP_LIFT_GATED and mean_lift_gated <= 0.0
            and not hard_pass_conditions)
        or (n_seeds_ran == len(seeds) and mean_lift_gated < 0.0)
        or (n_seeds_ran == len(seeds) and abs(mean_shuffled_vs_gated) < SHUFFLED_VS_GATED_ARTIFACT_TOL
            and mean_lift_gated > 0.0)
    )

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif conf_dist_fail:
        verdict = "HARD_FAIL_DEGENERATE_CONFIDENCE_SIGNAL"
    elif gate_d_ok_fail:
        verdict = "HARD_FAIL_GATE_D_REPRO_MISMATCH_PIPELINE_DRIFT"
    elif hard_pass_conditions:
        verdict = "HARD_PASS"
    elif (n_seeds_ran == len(seeds)
          and abs(mean_shuffled_vs_gated) < SHUFFLED_VS_GATED_ARTIFACT_TOL and mean_lift_gated > 0.0):
        verdict = "HARD_FAIL_SHUFFLED_MATCHES_GATED_GENERIC_ARTIFACT"
    elif n_seeds_ran == len(seeds) and mean_lift_gated < 0.0:
        verdict = "HARD_FAIL_GATED_UNDERPERFORMS_UNGATED"
    elif n_seeds_ran == len(seeds) and mean_lift_gated < HP_LIFT_GATED and n_gated_sig < 2:
        verdict = "HARD_FAIL_NO_CONSISTENT_LIFT"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"gated_vs_ungated_lift={mean_lift_gated:+.4f} (n_sig_boot={n_gated_sig}/{n_seeds_ran}) | "
        f"inverted_deficit={mean_deficit_inverted:+.4f} (n_sig_boot={n_inverted_sig}/{n_seeds_ran}) | "
        f"shuffled_vs_ungated={mean_shuffled_vs_ungated:+.4f} shuffled_vs_gated={mean_shuffled_vs_gated:+.4f} | "
        f"ungated_auc={arm_summary['ungated']['auc_mean']:.4f} (gate_d_gap={gate_d_repro_gap:.4f}) | "
        f"gated_auc={arm_summary['gated']['auc_mean']:.4f} shuffled_auc={arm_summary['shuffled']['auc_mean']:.4f} "
        f"inverted_auc={arm_summary['inverted']['auc_mean']:.4f} oracle_auc={arm_summary['oracle']['auc_mean']:.4f} | "
        f"confidence_std={conf_std:.3f} degenerate={degenerate} | corpus={n_tokens}tok V={V} N={N}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:180]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "n_tokens": n_tokens, "vocab_size": vocab_size, "V": V, "N": N,
            "window": window, "min_count": min_count, "seeds": seeds,
            "n_wordsim_pairs": len(ws_pairs), "n_simlex_pairs": len(sl_pairs),
            "n_true_pairs": len(true_pairs), "n_random_pairs": len(random_pairs),
        },
        "confidence_diagnostics": {
            "mean": conf_mean, "std": conf_std, "max_bin_frac": max_bin_frac,
            "degenerate": degenerate, **conf_diag,
        },
        "arm_summary": arm_summary,
        "per_unit": per_unit,
        "boot_vs_ungated": boot_vs_ungated,
        "gate_d_repro_gap": gate_d_repro_gap,
        "bands": {
            "HP_LIFT_GATED": HP_LIFT_GATED, "HP_DEFICIT_INVERTED": HP_DEFICIT_INVERTED,
            "SHUFFLED_COLLAPSE_TOL": SHUFFLED_COLLAPSE_TOL,
            "SHUFFLED_VS_GATED_ARTIFACT_TOL": SHUFFLED_VS_GATED_ARTIFACT_TOL,
            "GATE_D_REPRO_TARGET_FULL": GATE_D_REPRO_TARGET_FULL,
            "GATE_D_REPRO_TARGET_SMOKE": GATE_D_REPRO_TARGET_SMOKE,
            "GATE_D_REPRO_TARGET_USED": gate_d_target,
            "GATE_D_REPRO_TOL_PASS": GATE_D_REPRO_TOL_PASS, "GATE_D_REPRO_TOL_FAIL": GATE_D_REPRO_TOL_FAIL,
            "CONF_STD_MIN_PASS": CONF_STD_MIN_PASS, "CONF_STD_MIN_FAIL": CONF_STD_MIN_FAIL,
            "BOOT_P_ALPHA": BOOT_P_ALPHA,
        },
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ,
        "arms_differ_detail": arms_differ_detail,
        "hp_scope": {"ungated": ["gate_d_repro"], "gated": ["hard_pass_lift", "hard_fail_no_lift"],
                    "shuffled": ["must_not_help"], "inverted": ["must_hurt"], "oracle": []},
        "crlb_n/a": "distributional-geometry generalization test; no argmax/capacity noise floor",
        "self_generated_confidence_note": (
            "confidence(w) computed strictly from tokens+w2i+window (split-half PPMI cosine); "
            "never passed wordsim/simlex or any gold label; computed before held-out eval step"),
        "prior_art": "Yu&Dayan2005; Kepecs2008/Lak2014; Lisman&Grace2005; McClelland-McNaughton-OReilly1995 CLS; "
                     "STEP1 codebook (Kanerva1988/Sahlgren2005 RI; Jones-Mewhort2007 BEAGLE; Church-Hanks1990/"
                     "Levy-Goldberg2015 PPMI-SVD)",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test at toy scale: exercises the REAL split-half confidence
    computation + weighted-SVD codebook builder for ALL 5 arms (no synthetic-only branch)."""
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

    # Real code path: split-half confidence.
    confidence, conf_diag = compute_split_half_confidence(tokens, w2i, window=3)
    assert confidence.shape == (V,), f"confidence shape {confidence.shape}"
    assert np.all(np.isfinite(confidence)), "confidence has non-finite values"
    assert np.all((confidence >= 0.0) & (confidence <= 1.0)), "confidence out of [0,1]"
    assert conf_diag["ppmi_a_nnz"] > 0 and conf_diag["ppmi_b_nnz"] > 0, "split halves produced empty ppmi"
    print(f"[self-test] confidence: mean={confidence.mean():.3f} std={confidence.std():.3f}", flush=True)

    count_weights = oracle_weights_from_counts(counts)
    assert count_weights.shape == (V,)
    assert np.all((count_weights >= 0.0) & (count_weights <= 1.0 + 1e-9))

    N = 8  # toy: N < V (real run V>>N); exercises SVD cap+pad path too
    hashes = {}
    for arm in ALL_ARMS_FULL:
        w = arm_weights(arm, confidence, count_weights, V)
        assert w.shape == (V,), f"{arm} weight shape {w.shape}"
        cb = build_codebook_weighted(ppmi, w, N, seed=7)
        assert cb.shape == (V, N), f"{arm} codebook shape {cb.shape}"
        assert np.all(np.isfinite(cb)), f"{arm} produced non-finite"
        nrm = np.linalg.norm(cb, axis=1)
        assert np.allclose(nrm[nrm > 0], 1.0, atol=1e-5), f"{arm} rows not L2-normalized"
        hashes[arm] = hashlib.sha256(np.ascontiguousarray(cb).tobytes()).hexdigest()
    # ARMS-MUST-DIFFER.
    assert len(set(hashes.values())) == len(hashes), f"META_RULE_AF: arm codebooks not bit-distinct {hashes}"

    # Ungated must be a no-op relative to weights=1 direct construction (Gate-D mechanism sanity,
    # not the real STEP1 numeric target -- just verifies the diag(1)@ppmi = ppmi identity holds).
    cb_direct = build_codebook_weighted(ppmi, np.ones(V), N, seed=7)
    cb_ungated = build_codebook_weighted(ppmi, arm_weights("ungated", confidence, count_weights, V), N, seed=7)
    assert np.allclose(cb_direct, cb_ungated), "ungated arm is not the weights=1 no-op"

    # Bootstrap helper sanity: identical arm vs itself -> mean_diff ~ 0, p_le_zero ~ 0.5.
    ct = np.array([0.9, 0.8, 0.7, 0.6])
    cr = np.array([0.1, 0.2, 0.3, 0.05])
    m, s, p = paired_bootstrap_auc_diff(ct, cr, ct, cr, n_boot=200, seed=1)
    assert abs(m) < 1e-9, f"self-diff bootstrap mean should be exactly 0, got {m}"

    # References load + parse (real files) + eval_codebook real path.
    ws = load_wordsim(w2i)
    sl = load_simlex(w2i)
    assert isinstance(ws, list) and isinstance(sl, list)
    tp, rp = make_true_random_sets([(0, 1, 0.9), (2, 3, 0.8), (0, 2, 0.1), (1, 3, 0.2)], w2i, seed=0)
    res = eval_codebook(cb_direct, tp, rp, ws, sl)
    assert 0.0 <= res["auc"] <= 1.0

    print("[self-test] PASS: split-half confidence + 5-arm weighted-SVD + bootstrap + eval all exercised",
          flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, n_tokens=1_500_000, vocab_size=6000, N=1024, window=5,
            min_count=5, seeds=SEEDS, run_mode="smoke")
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, n_tokens=8_000_000, vocab_size=10000, N=1024, window=5,
            min_count=5, seeds=SEEDS, run_mode="full")
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
