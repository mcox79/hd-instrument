"""ENC1 STRUCTURED N-LIFT v1 -- encoder-side cleanup-ceiling-break 5-arm sweep.

Post 4-family decoder cleanup HARD_FAIL (att1 v1 Hopfield, att1 v2 Krotov, OMP,
multi-bump CAN) at N=512 M=200 sigma=1.5 with argmax baseline ~0.023 (near random),
the META finding is that the cleanup ceiling is encoder-bound at this regime
(META atom CERT ledger row 673).

This cell instantiates the encoder-side branch with a DISCRIMINATING gate between
pure dimension lift (N=512 -> N=4096 dense bipolar) and structural encoding
(sparse fan-in K=5 cerebellar-GC analog), plus median-subtract preprocessing
(fly-LSH-style shift-invariance) and a composed top arm.

DESIGN (5 arms x 5 sigmas x 3 seeds):
  ARM_BASELINE_N512               dense bipolar random codebook at N=512 (parent HARD_FAIL config)
  ARM_DENSE_N4096                 dense bipolar random codebook at N=4096 (pure JL dimension lift)
  ARM_SPARSE_FANIN_K5_N4096       K=5-sparse bipolar rows at N=4096 (cerebellar GC analog)
  ARM_MEDIAN_SUB_N512             N=512 dense + median-subtract on cue+codebook (fly-LSH shift-invariance)
  ARM_MEDIAN_SUB_SPARSE_N4096     composition: median-subtract + sparse-fan-in N=4096

SIGMAS: [0.0, 0.5, 1.0, 1.5, 2.0] with discriminator sigma = 1.5.

PRE-REG (notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md):
  Per ARM (vs ARM_BASELINE_N512 ~ 0.023):
    HARD_PASS:   arm_recall >= 0.20 at sigma=1.5 AND CV <= 0.30 (~8x baseline lift)
    HARD_FAIL:   arm_recall <= 0.04 at sigma=1.5 (within 2x baseline noise; null)
    MIDDLE_BAND: arm_recall 0.04-0.20 (MEASURED_MECHANISM, characterize)

DISCRIMINATING-REGIME GATE (mandatory classification logic):
  - ARM_DENSE_N4096 >= 0.20 alone: pure dimension lift suffices; sparse-fan-in framing wrong.
    Atomize "N=512 cleanup ceiling = N under-capacity at sigma>=1.5".
  - ARM_DENSE_N4096 < 0.20 AND ARM_SPARSE_FANIN_K5_N4096 >= 0.20: sparse-fan-in load-bearing
    per rank-1-anisotropy-trap discipline.
  - Both >= 0.20 but ARM_DENSE_N4096 > ARM_SPARSE_FANIN_K5_N4096: dimension dominates.

SANITY (CONFOUND_FAIL detector):
  At sigma=0.0, ALL 5 arms must achieve recall@1 = 1.000. Failure = implementation bug,
  NOT mechanism rejection.

SUBSTRATE-ONLY: n_llm_calls = 0; numpy-only; no torch; laptop CPU.

Cites:
  - notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md (source-of-truth pre-reg)
  - notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md (parent)
  - Litwin-Kumar et al. 2017 Neuron (cerebellar K=5 fan-in theory)
  - Cayco-Gajic et al. 2017 PMC5729189 (K~4 empirical)
  - Dasgupta, Stevens, Navlakha 2017 Science (fly-LSH WTA)
  - Foldiak 1990 Biol Cybern (anti-Hebbian decorrelation)
  - Johnson-Lindenstrauss lemma (dense N-lift baseline)
  - CERT 591 dense-projected-KV (substrate's learned contrastive projection)

Skunkworks structural blockers:
  #3 _LLM_CALL_COUNTER = [0] (substrate-only; no encoder)
  #1 per_unit per seed
  #2 cv across seeds in compute_verdict
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "enc1_structured_n_lift_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config (CPU-only; numpy-only)
N_DIM_BASELINE = 512
N_DIM_LIFT = 4096
K_SPARSE = 5
M = 200
N_EVAL = 200
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
DISCRIMINATOR_SIGMA = 1.5

# Arms: (label, N_dim, encoding, preprocess)
#   encoding: "dense" | "sparse"
#   preprocess: "none" | "median_sub"
ARMS = [
    ("ARM_BASELINE_N512",             N_DIM_BASELINE, "dense",  "none"),
    ("ARM_DENSE_N4096",               N_DIM_LIFT,     "dense",  "none"),
    ("ARM_SPARSE_FANIN_K5_N4096",     N_DIM_LIFT,     "sparse", "none"),
    ("ARM_MEDIAN_SUB_N512",           N_DIM_BASELINE, "dense",  "median_sub"),
    ("ARM_MEDIAN_SUB_SPARSE_N4096",   N_DIM_LIFT,     "sparse", "median_sub"),
]
BASELINE_LABEL = "ARM_BASELINE_N512"
DENSE_LIFT_LABEL = "ARM_DENSE_N4096"
SPARSE_LIFT_LABEL = "ARM_SPARSE_FANIN_K5_N4096"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:
    SEEDS = [0]
    N_EVAL = 50

CONFIG_VERSION = ("enc1_structured_n_lift_v1; N_BASELINE=%d N_LIFT=%d K_SPARSE=%d M=%d "
                  "N_EVAL=%d sigmas=%s arms=%s discriminator_sigma=%.2f seeds=%s mode=%s") % (
                      N_DIM_BASELINE, N_DIM_LIFT, K_SPARSE, M, N_EVAL, SIGMA_SWEEP,
                      [a[0] for a in ARMS], DISCRIMINATOR_SIGMA, SEEDS, RUN_MODE)


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _build_codebook_dense_bipolar(seed, M_loc, D_loc):
    """Random bipolar (-1, +1) codebook; rows = atoms; L2-normalized."""
    g = np.random.default_rng(seed)
    cb = g.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(M_loc, D_loc))
    return _l2_normalize(cb.astype(np.float32)).astype(np.float32)


def _build_codebook_sparse_bipolar(seed, M_loc, D_loc, K_loc):
    """K-sparse bipolar codebook; each row has K nonzero entries at random positions
    drawn from {-1, +1}; remaining entries = 0. L2-normalized rows.

    Cerebellar GC analog: per-row mu-contribution variance ~ K not D; breaks rank-1
    anisotropy trap qualitatively (Litwin-Kumar 2017; Cayco-Gajic 2017).
    """
    g = np.random.default_rng(seed)
    cb = np.zeros((M_loc, D_loc), dtype=np.float32)
    for i in range(M_loc):
        positions = g.choice(D_loc, size=K_loc, replace=False)
        signs = g.choice(np.array([-1.0, 1.0], dtype=np.float32), size=K_loc)
        cb[i, positions] = signs
    return _l2_normalize(cb).astype(np.float32)


def _build_codebook(seed, M_loc, D_loc, encoding, K_loc=None):
    if encoding == "dense":
        return _build_codebook_dense_bipolar(seed, M_loc, D_loc)
    if encoding == "sparse":
        assert K_loc is not None, "sparse encoding requires K_loc"
        return _build_codebook_sparse_bipolar(seed, M_loc, D_loc, K_loc)
    raise ValueError("unknown encoding: %s" % encoding)


def _apply_preprocess(cues, codebook, preprocess):
    """Apply per-vector preprocessing to BOTH cues and codebook rows before decode.

    median_sub: subtract per-vector median from each row (fly-LSH-style shift invariance;
    kills rank-1 common-mode mu when present). On bipolar codebook the empirical row median
    is structurally near zero -- the operation should be near-no-op on the parent regime
    but is included to test the rank-1-mu-dominance hypothesis directly.
    """
    if preprocess == "none":
        return cues, codebook
    if preprocess == "median_sub":
        cues_med = np.median(cues, axis=1, keepdims=True)
        cb_med = np.median(codebook, axis=1, keepdims=True)
        return cues - cues_med, codebook - cb_med
    raise ValueError("unknown preprocess: %s" % preprocess)


def _argmax_cleanup_batch(cues, codebook, preprocess="none"):
    """Single-step argmax over <cue, codebook_row>. Returns (B,) int64 idx."""
    cues_pp, cb_pp = _apply_preprocess(cues, codebook, preprocess)
    cb_n = _l2_normalize(cb_pp)
    cu_n = _l2_normalize(cues_pp)
    scores = cu_n @ cb_n.T   # (B, M)
    return np.argmax(scores, axis=1).astype(np.int64)


def _run_arm(arm_label, D_loc, encoding, preprocess, query_indices, sigma, seed, K_loc=None):
    """Run one arm at one sigma. Returns dict with recall_at_1."""
    # Build per-seed codebook (same across sigmas within a (seed, arm) tuple).
    # Codebook construction is determined by seed + arm-derived offset for independence
    # across arms while staying deterministic per (seed, arm) pair.
    cb_seed = seed * 1000003 + (abs(hash(arm_label)) % 999983)
    codebook = _build_codebook(cb_seed, M, D_loc, encoding, K_loc=K_loc)
    # Noise: per-(arm, sigma, seed) deterministic noise stream
    noise_seed = seed * 4001 + int(sigma * 10000) + (abs(hash(arm_label)) % 977)
    g_noise = np.random.default_rng(noise_seed)
    cues_clean = codebook[query_indices]
    cues = cues_clean + sigma * g_noise.standard_normal((len(query_indices), D_loc)).astype(np.float32)
    pred = _argmax_cleanup_batch(cues, codebook, preprocess=preprocess)
    n_correct = int((pred == query_indices).sum())
    return {
        "recall_at_1": float(n_correct) / max(len(query_indices), 1),
        "N_dim": D_loc,
        "encoding": encoding,
        "preprocess": preprocess,
        "K_sparse": K_loc if encoding == "sparse" else None,
    }


def _basin_per_arm(arm_label, D_loc, encoding, preprocess, query_indices, sigmas, seed, K_loc=None):
    out = {}
    for sig in sigmas:
        r = _run_arm(arm_label, D_loc, encoding, preprocess, query_indices, sig, seed, K_loc=K_loc)
        out[float(sig)] = r["recall_at_1"]
    return out


def run_unit(seed):
    g = np.random.default_rng(seed)
    query_idx = g.choice(M, size=min(N_EVAL, M), replace=False)
    by_arm = {}
    for arm_label, D_loc, encoding, preprocess in ARMS:
        K_loc = K_SPARSE if encoding == "sparse" else None
        print("  [seed=%d arm=%s N=%d enc=%s pre=%s K=%s]" % (
            seed, arm_label, D_loc, encoding, preprocess, K_loc), flush=True)
        t_arm = time.time()
        # Discriminator: sigma = DISCRIMINATOR_SIGMA on full query set
        disc = _run_arm(arm_label, D_loc, encoding, preprocess, query_idx, DISCRIMINATOR_SIGMA,
                        seed, K_loc=K_loc)
        # Basin: full sigma sweep on smaller subset for speed
        basin_subset = query_idx[: min(50, len(query_idx))]
        basin = _basin_per_arm(arm_label, D_loc, encoding, preprocess, basin_subset, SIGMA_SWEEP,
                               seed, K_loc=K_loc)
        by_arm[arm_label] = {
            "N_dim": D_loc,
            "encoding": encoding,
            "preprocess": preprocess,
            "K_sparse": K_loc,
            "recall_at_1_discriminator": round(disc["recall_at_1"], 4),
            "basin_robustness": {str(k): round(v, 4) for k, v in basin.items()},
            "wall_s": round(time.time() - t_arm, 2),
        }
        a = by_arm[arm_label]
        print("    [seed=%d arm=%s] disc=%.3f basin_0=%.3f basin_0.5=%.3f basin_1.0=%.3f "
              "basin_1.5=%.3f basin_2.0=%.3f (wall=%.2fs)" % (
                  seed, arm_label, a["recall_at_1_discriminator"],
                  a["basin_robustness"].get("0.0", 0.0),
                  a["basin_robustness"].get("0.5", 0.0),
                  a["basin_robustness"].get("1.0", 0.0),
                  a["basin_robustness"].get("1.5", 0.0),
                  a["basin_robustness"].get("2.0", 0.0),
                  a["wall_s"]), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N": N_DIM_BASELINE,                  # PROT-021 config-guard expects "N"
        "N_DIM_BASELINE": N_DIM_BASELINE,
        "N_DIM_LIFT": N_DIM_LIFT,
        "K_SPARSE": K_SPARSE,
        "M": M,
        "N_EVAL": N_EVAL,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def _classify_arm(arm_recall, arm_cv):
    """Per-arm pre-reg band classification."""
    if arm_recall >= 0.20 and arm_cv <= 0.30:
        return "HARD_PASS"
    if arm_recall <= 0.04:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def _discriminating_regime_call(by_arm_agg):
    """Mandatory discriminating-regime gate from research note.

    Returns (label, explanation) describing which mechanism is load-bearing.
    Labels:
      "DIMENSION_DOMINATES"           dense N=4096 >= 0.20 alone (sparse framing wrong)
      "SPARSE_FANIN_LOAD_BEARING"     dense < 0.20 AND sparse N=4096 >= 0.20
      "DIMENSION_DOMINATES_BOTH"      both >= 0.20 but dense > sparse
      "SPARSE_BEATS_DENSE_BOTH"       both >= 0.20 and sparse > dense
      "BOTH_NULL"                     both < 0.20
    """
    dense = by_arm_agg[DENSE_LIFT_LABEL]["recall_discriminator_mean"]
    sparse = by_arm_agg[SPARSE_LIFT_LABEL]["recall_discriminator_mean"]
    if dense >= 0.20 and sparse < 0.20:
        return ("DIMENSION_DOMINATES",
                "pure N-lift suffices; sparse-fan-in framing wrong; "
                "atomize 'N=512 cleanup ceiling = N under-capacity at sigma>=1.5'")
    if dense < 0.20 and sparse >= 0.20:
        return ("SPARSE_FANIN_LOAD_BEARING",
                "sparse-fan-in K=5 carries; dense lift does not; "
                "rank-1-anisotropy-trap discipline confirmed")
    if dense >= 0.20 and sparse >= 0.20:
        if dense > sparse:
            return ("DIMENSION_DOMINATES_BOTH",
                    "both arms HARD_PASS but dense > sparse; "
                    "structure unnecessary at this regime")
        return ("SPARSE_BEATS_DENSE_BOTH",
                "both arms HARD_PASS but sparse > dense; "
                "structure adds beyond dimension")
    return ("BOTH_NULL",
            "neither dense lift nor sparse-fan-in clears HARD_PASS; "
            "Shannon-floor candidate at sigma=1.5 M=200")


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_arm_agg = {}
    arm_labels = list(units[0]["by_arm"].keys())
    for arm_label in arm_labels:
        disc_vals = [u["by_arm"][arm_label]["recall_at_1_discriminator"] for u in units]
        sigma_keys = list(units[0]["by_arm"][arm_label]["basin_robustness"].keys())
        basin_agg = {}
        for sk in sigma_keys:
            vals = [u["by_arm"][arm_label]["basin_robustness"].get(sk, 0.0) for u in units]
            basin_agg[sk] = round(float(np.mean(vals)), 4)
        dm = float(np.mean(disc_vals))
        ds = float(np.std(disc_vals))
        cv = ds / max(dm, 1e-6)
        arm_class = _classify_arm(dm, cv)
        by_arm_agg[arm_label] = {
            "recall_discriminator_mean": round(dm, 4),
            "recall_discriminator_std": round(ds, 4),
            "recall_discriminator_cv": round(cv, 4),
            "basin_robustness_mean": basin_agg,
            "per_arm_classification": arm_class,
        }

    # Sanity check: all 5 arms recall@1 = 1.000 at sigma=0
    sanity_failures = []
    for arm_label in arm_labels:
        basin_0 = by_arm_agg[arm_label]["basin_robustness_mean"].get("0.0", -1.0)
        if basin_0 < 0.999:
            sanity_failures.append("%s basin_0=%.4f" % (arm_label, basin_0))
    sanity_ok = len(sanity_failures) == 0

    # Per-arm verdict tally
    baseline_recall = by_arm_agg[BASELINE_LABEL]["recall_discriminator_mean"]
    n_hard_pass = sum(1 for al in arm_labels
                      if by_arm_agg[al]["per_arm_classification"] == "HARD_PASS")
    n_hard_fail_nonbaseline = sum(
        1 for al in arm_labels
        if al != BASELINE_LABEL and by_arm_agg[al]["per_arm_classification"] == "HARD_FAIL"
    )

    # Discriminating-regime call (only meaningful if dense / sparse arms present)
    regime_label, regime_explain = _discriminating_regime_call(by_arm_agg)

    detail = {
        "by_arm_agg": by_arm_agg,
        "baseline_recall_discriminator": round(baseline_recall, 4),
        "n_hard_pass_arms": n_hard_pass,
        "n_hard_fail_nonbaseline_arms": n_hard_fail_nonbaseline,
        "discriminating_regime_call": regime_label,
        "discriminating_regime_explanation": regime_explain,
        "sanity_sigma0_recall_all_1_0_ok": sanity_ok,
        "sanity_sigma0_failures": sanity_failures,
        "discriminator_sigma": DISCRIMINATOR_SIGMA,
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": ("HD-substrate-native encoder-side cleanup-ceiling drill; "
                         "5 arms x 5 sigmas x %d seeds at M=%d; baseline N=%d, lift N=%d, K=%d; "
                         "discriminating gate: dense-N-lift vs sparse-fan-in vs median-sub vs composition" % (
                             len(units), M, N_DIM_BASELINE, N_DIM_LIFT, K_SPARSE)),
        "cites": [
            "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md (source-of-truth)",
            "notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md (parent)",
            "Litwin_Kumar_2017_optimal_synaptic_connectivity",
            "Cayco_Gajic_2017_PMC5729189_cerebellar_GC",
            "Dasgupta_Stevens_Navlakha_2017_fly_LSH",
            "Foldiak_1990_anti_Hebbian_decorrelation",
            "Johnson_Lindenstrauss_lemma",
            "CERT_591_dense_projected_KV",
        ],
    }

    # Per-arm summary string
    arm_summary_parts = []
    for al in arm_labels:
        a = by_arm_agg[al]
        arm_summary_parts.append("%s=%.3f(cv%.2f,%s)" % (
            al, a["recall_discriminator_mean"], a["recall_discriminator_cv"],
            a["per_arm_classification"]))
    summary = ("DISCRIMINATOR @ sigma=%.2f: %s | regime=%s | sanity_sigma0_ok=%s" % (
        DISCRIMINATOR_SIGMA, " | ".join(arm_summary_parts), regime_label, sanity_ok))

    # CONFOUND check first
    if not sanity_ok:
        return ("CONFOUND_FAIL",
                "CONFOUND_FAIL: sigma=0 recall < 1.000 for %d arm(s) (%s); implementation bug suspected, "
                "NOT mechanism rejection. " % (len(sanity_failures), "; ".join(sanity_failures)) + summary,
                detail)

    # Cell-level verdict by aggregation of per-arm bands + regime
    # HARD_PASS at cell level = at least one non-baseline arm HARD_PASS (the experiment
    # has a positive substrate-meaningful finding to atomize).
    nonbaseline_pass = [al for al in arm_labels
                        if al != BASELINE_LABEL
                        and by_arm_agg[al]["per_arm_classification"] == "HARD_PASS"]

    if nonbaseline_pass:
        # Pick highest-recall passing arm for the headline
        nonbaseline_pass.sort(key=lambda x: by_arm_agg[x]["recall_discriminator_mean"], reverse=True)
        top = nonbaseline_pass[0]
        top_recall = by_arm_agg[top]["recall_discriminator_mean"]
        top_cv = by_arm_agg[top]["recall_discriminator_cv"]
        return ("HARD_PASS",
                "DISCRIMINATOR HARD_PASS: encoder-side intervention unblocks cleanup ceiling at sigma=%.2f; "
                "top arm %s recall=%.3f vs baseline=%.3f (lift=%+.3f); CV=%.3f <= 0.30; %d arm(s) HARD_PASS; "
                "regime=%s (%s). META primitive READY for hdlab swap-in next cycle. " % (
                    DISCRIMINATOR_SIGMA, top, top_recall, baseline_recall,
                    top_recall - baseline_recall, top_cv, len(nonbaseline_pass),
                    regime_label, regime_explain) + summary,
                detail)

    # HARD_FAIL at cell level = all non-baseline arms HARD_FAIL (encoder mechanism null at this regime)
    nonbaseline_arms = [al for al in arm_labels if al != BASELINE_LABEL]
    nonbaseline_fail = [al for al in nonbaseline_arms
                        if by_arm_agg[al]["per_arm_classification"] == "HARD_FAIL"]
    if len(nonbaseline_fail) == len(nonbaseline_arms):
        return ("HARD_FAIL",
                "DISCRIMINATOR HARD_FAIL: ALL %d non-baseline encoder arms HARD_FAIL at sigma=%.2f; "
                "cleanup ceiling at this regime is Shannon-floor candidate (decoder AND encoder both null). "
                "Pivot: descope sigma=1.5 stress regime; substrate operating envelope <= sigma=1.0; "
                "OR signal-side intervention (richer encoder upstream). regime=%s. " % (
                    len(nonbaseline_arms), DISCRIMINATOR_SIGMA, regime_label) + summary,
                detail)

    # Otherwise MIDDLE_BAND at cell level (some arms in 0.04-0.20 range; MEASURED_MECHANISM)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: encoder-side mechanism partial; non-baseline arms span HARD_FAIL/MIDDLE_BAND but no HARD_PASS; "
            "regime=%s (%s). MEASURED_MECHANISM; route to ENC2 anti-Hebb or revive 5x-DEEPER M=10k anisotropic-key cell. " % (
                regime_label, regime_explain) + summary,
            detail)


# ──────────────────────────────────────────────────────────────────────────────
# atexit synthesize metrics from partials (timeout-resilience per Skunkworks #4)
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT", "atexit synthesize: compute_verdict failed: %s" % e,
                                    {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM_BASELINE": N_DIM_BASELINE,
            "N_DIM_LIFT": N_DIM_LIFT,
            "K_SPARSE": K_SPARSE,
            "M": M,
            "N_EVAL": N_EVAL,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_enc1_structured_n_lift_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ──────────────────────────────────────────────────────────────────────────────
# Self-test: mechanism + sanity + verdict-shape coverage
def _selftest():
    g = np.random.default_rng(0)

    # T1: dense codebook is bipolar {-1, +1} (pre-normalize)
    cb_raw = g.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(8, 32))
    uniq = set(np.unique(cb_raw).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 dense codebook not bipolar: %s" % uniq

    # T2: sparse codebook has exactly K nonzero per row
    cb_sp = _build_codebook_sparse_bipolar(0, 16, 64, 5)
    nnz_per_row = np.count_nonzero(cb_sp, axis=1)
    # After L2 normalize, nonzeros stay nonzero
    assert (nnz_per_row == 5).all(), "T2 sparse row NNZ != 5: %s" % nnz_per_row

    # T3: sparse codebook nonzero values are bipolar-after-normalize (each row: K identical-magnitude entries)
    for i in range(cb_sp.shape[0]):
        nonzero_vals = cb_sp[i][cb_sp[i] != 0]
        magnitudes = np.abs(nonzero_vals)
        assert np.allclose(magnitudes, magnitudes[0], atol=1e-5), \
            "T3 row %d sparse magnitudes not equal: %s" % (i, magnitudes)

    # T4: sigma=0 sanity per arm: argmax cleanup recovers identity for all 5 arms
    qidx = np.arange(8)
    for arm_label, D_loc, encoding, preprocess in ARMS:
        K_loc = K_SPARSE if encoding == "sparse" else None
        cb_t = _build_codebook(0, 16, D_loc, encoding, K_loc=K_loc)
        cues_t = cb_t[qidx]
        pred = _argmax_cleanup_batch(cues_t, cb_t, preprocess=preprocess)
        assert (pred == qidx).all(), \
            "T4 sigma=0 identity failed for %s (N=%d enc=%s pre=%s): pred=%s" % (
                arm_label, D_loc, encoding, preprocess, pred.tolist())

    # T5: median-subtract preserves shape and yields zero per-row median (post-subtract)
    cb_t = _build_codebook(0, 16, 32, "dense")
    cues_t, cb_pp = _apply_preprocess(cb_t[:4], cb_t, "median_sub")
    cb_med_post = np.median(cb_pp, axis=1)
    cu_med_post = np.median(cues_t, axis=1)
    assert np.allclose(cb_med_post, 0.0, atol=1e-5), "T5 cb median not zero post-sub: %s" % cb_med_post
    assert np.allclose(cu_med_post, 0.0, atol=1e-5), "T5 cu median not zero post-sub: %s" % cu_med_post

    # T6: per-arm classification bands
    assert _classify_arm(0.25, 0.20) == "HARD_PASS", "T6 HARD_PASS band wrong"
    assert _classify_arm(0.25, 0.35) == "MIDDLE_BAND", "T6 CV>0.30 should kick to MIDDLE"
    assert _classify_arm(0.10, 0.20) == "MIDDLE_BAND", "T6 0.04<recall<0.20 should MIDDLE"
    assert _classify_arm(0.02, 0.10) == "HARD_FAIL", "T6 recall<=0.04 should HARD_FAIL"

    # T7: discriminating-regime gate logic
    fake_agg = {
        DENSE_LIFT_LABEL:  {"recall_discriminator_mean": 0.30},
        SPARSE_LIFT_LABEL: {"recall_discriminator_mean": 0.05},
    }
    lab, _ = _discriminating_regime_call(fake_agg)
    assert lab == "DIMENSION_DOMINATES", "T7 dense-only HARD_PASS should be DIMENSION_DOMINATES: %s" % lab
    fake_agg = {
        DENSE_LIFT_LABEL:  {"recall_discriminator_mean": 0.05},
        SPARSE_LIFT_LABEL: {"recall_discriminator_mean": 0.30},
    }
    lab, _ = _discriminating_regime_call(fake_agg)
    assert lab == "SPARSE_FANIN_LOAD_BEARING", "T7 sparse-only should be SPARSE_FANIN_LOAD_BEARING: %s" % lab
    fake_agg = {
        DENSE_LIFT_LABEL:  {"recall_discriminator_mean": 0.40},
        SPARSE_LIFT_LABEL: {"recall_discriminator_mean": 0.30},
    }
    lab, _ = _discriminating_regime_call(fake_agg)
    assert lab == "DIMENSION_DOMINATES_BOTH", "T7 both HARD_PASS dense>sparse: %s" % lab
    fake_agg = {
        DENSE_LIFT_LABEL:  {"recall_discriminator_mean": 0.30},
        SPARSE_LIFT_LABEL: {"recall_discriminator_mean": 0.40},
    }
    lab, _ = _discriminating_regime_call(fake_agg)
    assert lab == "SPARSE_BEATS_DENSE_BOTH", "T7 both HARD_PASS sparse>dense: %s" % lab
    fake_agg = {
        DENSE_LIFT_LABEL:  {"recall_discriminator_mean": 0.10},
        SPARSE_LIFT_LABEL: {"recall_discriminator_mean": 0.10},
    }
    lab, _ = _discriminating_regime_call(fake_agg)
    assert lab == "BOTH_NULL", "T7 both null should BOTH_NULL: %s" % lab

    # T8: compute_verdict CONFOUND_FAIL on broken sigma=0
    def _mk_arm(disc, basin0, basin15):
        return {
            "N_dim": 512, "encoding": "dense", "preprocess": "none", "K_sparse": None,
            "recall_at_1_discriminator": disc,
            "basin_robustness": {
                "0.0": basin0, "0.5": basin0 - 0.05, "1.0": basin0 - 0.20,
                "1.5": basin15, "2.0": basin15 - 0.10
            },
            "wall_s": 0.01,
        }
    u_bad_sanity = {
        "seed": 0,
        "by_arm": {
            "ARM_BASELINE_N512":           _mk_arm(0.02, 1.0, 0.02),
            "ARM_DENSE_N4096":             _mk_arm(0.25, 0.85, 0.25),   # sanity broken
            "ARM_SPARSE_FANIN_K5_N4096":   _mk_arm(0.30, 1.0, 0.30),
            "ARM_MEDIAN_SUB_N512":         _mk_arm(0.03, 1.0, 0.03),
            "ARM_MEDIAN_SUB_SPARSE_N4096": _mk_arm(0.32, 1.0, 0.32),
        },
        "N": 512, "N_DIM_BASELINE": 512, "N_DIM_LIFT": 4096, "K_SPARSE": 5,
        "M": 200, "N_EVAL": 50, "run_mode": "smoke", "config_version": "selftest",
    }
    v, m, _ = compute_verdict([u_bad_sanity, u_bad_sanity, u_bad_sanity])
    assert v == "CONFOUND_FAIL", "T8 expected CONFOUND_FAIL got %s msg=%s" % (v, m[:200])

    # T9: compute_verdict HARD_PASS when at least one non-baseline arm hits HARD_PASS band
    u_pass = {
        "seed": 0,
        "by_arm": {
            "ARM_BASELINE_N512":           _mk_arm(0.02, 1.0, 0.02),
            "ARM_DENSE_N4096":             _mk_arm(0.10, 1.0, 0.10),   # MIDDLE
            "ARM_SPARSE_FANIN_K5_N4096":   _mk_arm(0.35, 1.0, 0.35),   # HARD_PASS
            "ARM_MEDIAN_SUB_N512":         _mk_arm(0.03, 1.0, 0.03),
            "ARM_MEDIAN_SUB_SPARSE_N4096": _mk_arm(0.40, 1.0, 0.40),   # HARD_PASS
        },
        "N": 512, "N_DIM_BASELINE": 512, "N_DIM_LIFT": 4096, "K_SPARSE": 5,
        "M": 200, "N_EVAL": 50, "run_mode": "smoke", "config_version": "selftest",
    }
    v, m, d = compute_verdict([u_pass, u_pass, u_pass])
    assert v == "HARD_PASS", "T9 expected HARD_PASS got %s msg=%s" % (v, m[:200])
    assert d["discriminating_regime_call"] == "SPARSE_FANIN_LOAD_BEARING", \
        "T9 regime call wrong: %s" % d["discriminating_regime_call"]

    # T10: compute_verdict HARD_FAIL when ALL non-baseline arms HARD_FAIL
    u_fail = {
        "seed": 0,
        "by_arm": {
            "ARM_BASELINE_N512":           _mk_arm(0.02, 1.0, 0.02),
            "ARM_DENSE_N4096":             _mk_arm(0.03, 1.0, 0.03),
            "ARM_SPARSE_FANIN_K5_N4096":   _mk_arm(0.02, 1.0, 0.02),
            "ARM_MEDIAN_SUB_N512":         _mk_arm(0.03, 1.0, 0.03),
            "ARM_MEDIAN_SUB_SPARSE_N4096": _mk_arm(0.02, 1.0, 0.02),
        },
        "N": 512, "N_DIM_BASELINE": 512, "N_DIM_LIFT": 4096, "K_SPARSE": 5,
        "M": 200, "N_EVAL": 50, "run_mode": "smoke", "config_version": "selftest",
    }
    v, m, d = compute_verdict([u_fail, u_fail, u_fail])
    assert v == "HARD_FAIL", "T10 expected HARD_FAIL got %s msg=%s" % (v, m[:200])
    assert d["discriminating_regime_call"] == "BOTH_NULL", \
        "T10 regime call wrong: %s" % d["discriminating_regime_call"]

    # T11: dense N=4096 vs N=512 at sigma=1.5: 4096 should beat 512 in expectation (JL claim)
    # (probabilistic sanity; not a hard inequality but on 3 seeds the trend is reliable)
    deltas = []
    for sd in range(3):
        cb512 = _build_codebook(sd, 200, 512, "dense")
        cb4096 = _build_codebook(sd, 200, 4096, "dense")
        g_n = np.random.default_rng(sd + 9999)
        qi = g_n.choice(200, size=50, replace=False)
        noise512 = 1.5 * g_n.standard_normal((50, 512)).astype(np.float32)
        noise4096 = 1.5 * g_n.standard_normal((50, 4096)).astype(np.float32)
        cues512 = cb512[qi] + noise512
        cues4096 = cb4096[qi] + noise4096
        r512 = float((_argmax_cleanup_batch(cues512, cb512) == qi).sum()) / 50.0
        r4096 = float((_argmax_cleanup_batch(cues4096, cb4096) == qi).sum()) / 50.0
        deltas.append(r4096 - r512)
    mean_delta = float(np.mean(deltas))
    assert mean_delta >= 0.0, "T11 dense N-lift trend wrong: mean_delta=%.4f deltas=%s" % (
        mean_delta, deltas)

    print("[selftest] PASS: T1 bipolar + T2 sparse-NNZ + T3 sparse-magnitudes + T4 sigma0-identity x5 arms + "
          "T5 median-sub + T6 per-arm-bands + T7 regime-gate-4cases + T8 CONFOUND_FAIL + T9 HARD_PASS + "
          "T10 HARD_FAIL + T11 dense-Nlift-trend OK (mean_delta=%.3f)" % mean_delta, flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_BASELINE=%d N_LIFT=%d K=%d M=%d N_EVAL=%d sigmas=%s seeds=%s | "
          "name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM_BASELINE, N_DIM_LIFT, K_SPARSE, M, N_EVAL, SIGMA_SWEEP, SEEDS,
              _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM_BASELINE, "M": M,
               "schema": "enc1-structured-n-lift-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM_BASELINE": N_DIM_BASELINE,
        "N_DIM_LIFT": N_DIM_LIFT,
        "K_SPARSE": K_SPARSE,
        "M": M,
        "N_EVAL": N_EVAL,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_enc1_structured_n_lift_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD substrate-native encoder-side; no LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
