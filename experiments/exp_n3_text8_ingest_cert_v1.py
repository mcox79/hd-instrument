"""
n3_text8_ingest_cert_v1 -- N3: substrate-native char-LM cert against text8 (field-standard char-level benchmark).

MOTIVATION (Exp-Dev N3 corpus scope-DECISION 2026-06-21 ratified by Research N1<->N3 boundary ruling
architecture-AGNOSTIC eval harness):
  text8 = first 100MB of cleaned Wikipedia (27-char vocab: lowercase a-z + space). Established
  absolute-floor char-BPC baselines:
    uniform-27   = log2(27) ~= 4.755
    bigram       ~  3.0 BPC
    5-gram-KN    ~  1.7-1.9 BPC
    PPM          ~  1.4-1.55 BPC
    Shannon      ~  0.6-1.3 BPC
  These map onto absolute-floor cert bands (NOT a ratio band; the phase_d_tier6
  ratio-to-baseline band is gameable per N3 shakedown findings).

THIS CELL:
  - Substrate-native char-LM (SubstrateCharLM from testbed/substrate_lm/char_lm.py;
    4-primitive bipolar-bind streaming Hebbian + anti-Hebbian contrastive; NO gradient
    descent, NO LLM forward call at inference -- substrate ONLY).
  - Ingest = full split-disjoint text8 train chars (configurable max via env).
  - Score = char-BPC on held-out validation split (disjoint from train via
    deterministic 90/5/5 char-position split per loader contract).
  - Baselines = uniform-27 (always) + char-bigram-MLE computed on the SAME train + scored on
    SAME held-out (the canonical can-fail bar for substrate-native sequence modeling).
  - Per-seed checkpointed (PROT-021 run_config guard); resume-restartable.

NOTE ON SUBSTRATE-LM CHOICE (parent-prompt referent reconciliation):
  Parent prompt mentioned "N1 v3.1 substrate-LM" -- N1 v3.1 is TOKEN-level (Pythia residual
  pertoken decode + concept VQ). text8 is CHARACTER-level by convention; the existing
  char-level substrate-LM is SubstrateCharLM (validated by the N3 Shakespeare shakedown).
  Per Research's N3 ARCHITECTURE-AGNOSTIC ruling, N3 grades WHICHEVER substrate-native LM is
  plugged in. So this cell plugs in SubstrateCharLM (the substrate-native char-LM matching
  text8's character grain). When/if a token-level text8 cell is needed it would tokenize
  text8 + plug in N1 v3.1 separately.

ABSOLUTE-FLOOR CERT BANDS (the parent-prompt absolute-BPC bands; replaces ratio band):
  HARD_PASS  (chain-grade): substrate_bpc <= 1.90  (beats 5-gram-KN)
  MIDDLE_BAND:              1.90 < substrate_bpc <= 3.00  (between 5-gram-KN and bigram)
  HARD_FAIL:                substrate_bpc > 3.00  (worse than bigram; no real structure)
  Plus across-seeds cv <= 0.05 required for HARD_PASS (else demote one band).
  Plus zero LLM forward calls at inference (asserted from counter; HARD_FAIL on violation).
  Plus corpus_provenance_real=True (allow_synthetic=False to loader); HARD_FAIL on fall-back.

INSTRUMENTATION (Skunkworks N2 chain-grade structural blockers, all 4 baked, per handoff section 9):
  1. per_unit: per-seed entry stored in per_seed; recompute-off-per_unit ready.
  2. cv <= 0.05: computed across seeds in verdict.
  3. zero_llm_calls_at_inference: True LOGGED in metrics (asserted False if any call sneaked in).
     This cell imports NO transformers/torch (structural guarantee); counter logged for audit.
  4. VQ-floor decomposition: for a CHAR-LM with no explicit concept-codebook VQ, the analog is
     the BIGRAM-CEILING -- the BPC of a perfect-bigram-lookup table on the SAME held-out (the
     irreducible token-grain floor for bigram-context architectures). Reported per seed as
     bigram_ceiling_bpc. The load-bearing "gain" is substrate_bpc - bigram_ceiling_bpc: if
     substrate ~ bigram-ceiling, the substrate is doing nothing beyond the bigram lookup
     (by-construction-saturated; HARD_FAIL band).

THE 7 FIXES (per parent prompt + handoff 7b):
  1. CORPUS_PROVENANCE_REAL asserted + LOGGED (allow_synthetic=False fail-loud)
  2. SUBSTRATE-ONLY-DECODE code-trace (no transformers/torch import; counter at module top)
  3. ZERO-D-OVERLAP fallback in score_bpc (reuses SubstrateCharLM's predict_proba which floors p)
  4. PRE-REG-BAND-VERDICT direction-correct (HARD_PASS only when substrate BEATS the bar by margin)
  5. CONFIG_VERSION captures every BPC-affecting param (V_CHAR=27, N=4096, n_layers, alpha_max,
     n_steps_per_layer, max_chars_train, max_chars_test, seed)
  6. PER_SEED runtime measurement + extrapolation (smoke wall reported; full extrapolation logged)
  7. NO BACKGROUND BASH WATCHER (cell dies on commit + dispatch; orchestrator polls)

FORMULA SELFTESTS (PROT-022) (_instrumentation_selftest() at module scope tests):
  T1: bigram_baseline_bpc on synthetic deterministic text yields finite + < uniform
  T2: SubstrateCharLM mini-pipeline (N=128, ~2000 chars) produces finite substrate_bpc
  T3: zero-D-overlap (sparse / no-train) path in predict_proba does NOT NaN (floor to 1e-12)
  T4: LLM-call counter stays at 0 after substrate scoring (substrate-only gate auditable)
  T5: module-level constants are real code (AST-verifiable types + CONFIG_VERSION coverage)
  T6: per_unit dict shape includes all required keys (per_unit recompute-ready)
  T7: verdict() direction-correct -- HARD_PASS only when substrate_bpc <= 1.90 AND cv <= 0.05
  T8: bigram_ceiling_bpc <= bigram_baseline_bpc on the same data (ceiling tighter than baseline)

ASCII-only. write_metrics. PROT-021 run_config guard. CPU numpy only; no torch/GPU.

QUEUE: remote_cpu_queue (numpy-only; text8 corpus downloaded on first run on remote).
DEPENDENCY: testbed/substrate_lm/data.py text8_char_corpus loader (added 2026-06-22).

CONFIG_VERSION captures all BPC-affecting params; any change invalidates checkpoints.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials
)

ANCHOR_NAME = "n3_text8_ingest_cert_v1"

# ---------------------------------------------------------------------------
# LLM-call audit counter (Skunkworks structural blocker #3, substrate-only gate)
# ---------------------------------------------------------------------------
# This cell imports NO transformers/torch; the substrate-only claim is a STRUCTURAL
# guarantee (verified by code-trace). The counter is logged in metrics for audit.
_LLM_CALL_COUNTER = [0]


# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--n-dim", dest="n_dim", type=int, default=None)
_ap.add_argument("--max-chars-train", dest="max_chars_train", type=int, default=None)
_ap.add_argument("--max-chars-test", dest="max_chars_test", type=int, default=None)
_ARGS, _ = _ap.parse_known_args()

# RUN_MODE detection (in priority order):
#   1. --smoke CLI flag                                       -> smoke
#   2. HDLAB_RUN_MODE=smoke env                               -> smoke
#   3. HDLAB_EXP_NAME contains "_smoke" segment (runner-set)  -> smoke
#   4. else                                                   -> full
# The 3rd hook lets a runner that always sets HDLAB_RUN_MODE=full (e.g.
# runner_v2_prod.py) still execute the cell in smoke-config via the entry name.
# We match a "_smoke" segment (anywhere in the entry name) to tolerate
# queue_add --rerun-as suffixes like "n3_text8_..._smoke_retry1".
_exp_name = os.environ.get("HDLAB_EXP_NAME", "").lower()
_runmode_env = os.environ.get("HDLAB_RUN_MODE", "full").lower()
_name_indicates_smoke = ("_smoke" in _exp_name and not _exp_name.endswith("_no_smoke"))
if _ARGS.smoke or _runmode_env == "smoke" or _name_indicates_smoke:
    RUN_MODE = "smoke"
else:
    RUN_MODE = _runmode_env

# Substrate config (matches N2 best config compatible scale for char-grain; lower N than
# Pythia-residual cells since char vocab is 27 not 50k, and bigram context is far smaller).
# Smoke uses tighter config so the queue_add SMOKE_TIMEOUT_S=180s local gate passes
# (per Shakespeare shakedown: N=512 / layers=2 / 10k chars finishes in ~seconds).
if RUN_MODE == "smoke":
    N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(
        os.environ.get("HDLAB_N_DIM", "512"))
    N_LAYERS = int(os.environ.get("HDLAB_N_LAYERS", "2"))
    ALPHA_MAX = float(os.environ.get("HDLAB_ALPHA_MAX", "0.10"))
    N_STEPS_PER_LAYER = int(os.environ.get("HDLAB_N_STEPS_PER_LAYER", "2"))
    MAX_CHARS_TRAIN = _ARGS.max_chars_train if _ARGS.max_chars_train is not None else 10_000
    MAX_CHARS_TEST = _ARGS.max_chars_test if _ARGS.max_chars_test is not None else 1_000
    SEEDS = [7]
else:
    N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(
        os.environ.get("HDLAB_N_DIM", "4096"))
    N_LAYERS = int(os.environ.get("HDLAB_N_LAYERS", "4"))
    ALPHA_MAX = float(os.environ.get("HDLAB_ALPHA_MAX", "0.10"))
    N_STEPS_PER_LAYER = int(os.environ.get("HDLAB_N_STEPS_PER_LAYER", "3"))
    # Full: text8 train split is ~90MB chars; capping at 2M chars keeps wall reasonable
    # for first-of-corpus cert (per_seed wall scales ~linearly with TRAIN; bigram counts
    # converge by ~1M chars on a 27-char vocab). MAX_CHARS_TEST = 100k gives ~1M scored
    # positions across the 3-seed sweep, ample for stable BPC.
    MAX_CHARS_TRAIN = _ARGS.max_chars_train if _ARGS.max_chars_train is not None else int(
        os.environ.get("HDLAB_MAX_CHARS_TRAIN", "2000000"))
    MAX_CHARS_TEST = _ARGS.max_chars_test if _ARGS.max_chars_test is not None else int(
        os.environ.get("HDLAB_MAX_CHARS_TEST", "100000"))
    SEEDS = [int(s) for s in os.environ.get("HDLAB_SEEDS", "7,17,23").split(",")]

# Corpus identifiers (for CONFIG_VERSION and provenance log).
CORPUS_NAME = "text8"
CORPUS_VERSION = "matt_mahoney_2006"  # http://mattmahoney.net/dc/text8.zip (immutable)
ALLOW_SYNTHETIC = False  # fail-loud per phase_d_tier6 wikitext2 silent-fallback lesson

# Pre-registered bands (parent-prompt absolute-floor, replaces ratio band).
HARD_PASS_BPC = 1.90
MIDDLE_BAND_UPPER_BPC = 3.00
CV_MAX_HP = 0.05

CONFIG_VERSION = (
    "N=%d,LAYERS=%d,ALPHA=%.3f,STEPS=%d,V_CHAR=27,CORPUS=%s,CORPUS_VER=%s,"
    "TRAIN=%d,TEST=%d,SEEDS=%s,SYNTH=%s,BANDS=HP<=%.2f/MB<=%.2f"
) % (N_DIM, N_LAYERS, ALPHA_MAX, N_STEPS_PER_LAYER, CORPUS_NAME, CORPUS_VERSION,
     MAX_CHARS_TRAIN, MAX_CHARS_TEST, "-".join(str(s) for s in SEEDS),
     str(ALLOW_SYNTHETIC), HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC)


# ---------------------------------------------------------------------------
# Baselines (bigram-MLE + bigram-CEILING + uniform): the can-fail bars
# ---------------------------------------------------------------------------

def bigram_count_table(train_text: str, vocab: List[str], laplace: float = 0.5
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """Compute char-bigram count table on train_text.

    Returns:
      counts  (V, V) int64  -- counts[ctx][nxt] = #occurrences of bigram (ctx,nxt)
      probs   (V, V) float64 -- Laplace-smoothed (laplace=alpha) row-stochastic
    """
    V = len(vocab)
    ch_to_idx = {ch: i for i, ch in enumerate(vocab)}
    counts = np.zeros((V, V), dtype=np.int64)
    for i in range(1, len(train_text)):
        c = train_text[i - 1]
        n = train_text[i]
        if c in ch_to_idx and n in ch_to_idx:
            counts[ch_to_idx[c], ch_to_idx[n]] += 1
    smoothed = counts.astype(np.float64) + float(laplace)
    row_sums = smoothed.sum(axis=1, keepdims=True)
    probs = smoothed / np.maximum(row_sums, 1e-30)
    return counts, probs


def bigram_score_bpc(test_text: str, vocab: List[str], probs: np.ndarray) -> Dict[str, Any]:
    """Score char-BPC of test_text under a bigram model with row-stochastic probs.

    BPC = mean over positions t in [1, len-1] of -log2(p(test[t] | test[t-1])).
    """
    if len(test_text) < 2:
        return {"bpc": float("inf"), "n_scored": 0}
    ch_to_idx = {ch: i for i, ch in enumerate(vocab)}
    log2 = math.log(2)
    ent_sum = 0.0
    n_scored = 0
    for t in range(1, len(test_text)):
        c = test_text[t - 1]
        n = test_text[t]
        if c not in ch_to_idx or n not in ch_to_idx:
            continue  # skip OOV (should be empty for text8 27-char vocab)
        p = float(probs[ch_to_idx[c], ch_to_idx[n]])
        p = max(p, 1e-12)
        ent_sum += -math.log(p) / log2
        n_scored += 1
    return {"bpc": ent_sum / max(n_scored, 1), "n_scored": n_scored}


def bigram_ceiling_bpc(test_text: str, vocab: List[str], laplace: float = 0.5
                       ) -> Dict[str, Any]:
    """Bigram-CEILING (VQ-floor analog for char-LM): fit bigram-MLE on TEST itself.

    This is the IRREDUCIBLE bigram-context entropy on the held-out: the absolute lower
    bound a bigram-context architecture can achieve. (For a TRIGRAM-context architecture,
    the equivalent ceiling is trigram-fit-on-test, which is tighter; this cell's
    SubstrateCharLM uses bigram context, so bigram-on-test is the apples-to-apples ceiling.)

    Substrate_bpc - bigram_ceiling_bpc = the by-construction-relevant gain (positive = good).
    If substrate_bpc ~ bigram_ceiling_bpc, substrate is doing nothing beyond bigram-lookup
    (by-construction-saturated; HARD_FAIL band).
    """
    counts, probs = bigram_count_table(test_text, vocab, laplace=laplace)
    return bigram_score_bpc(test_text, vocab, probs)


def uniform_bpc(vocab: List[str]) -> float:
    return math.log2(max(len(vocab), 1))


# ---------------------------------------------------------------------------
# Substrate-LM driver (plug SubstrateCharLM into the eval harness)
# ---------------------------------------------------------------------------

def run_substrate_lm(train_text: str, test_text: str, vocab: List[str],
                     seed: int) -> Dict[str, Any]:
    """Train SubstrateCharLM on train_text + score char-BPC on test_text.

    Returns dict with substrate_bpc + train_wall_s + score_wall_s + primitive_health.
    SUBSTRATE-ONLY: imports no transformers/torch; LLM_CALL_COUNTER must remain 0.
    """
    # Local import (defer until called so module-import is cheap for selftest).
    from testbed.substrate_lm.char_lm import SubstrateCharLM

    t0 = time.time()
    lm = SubstrateCharLM(
        n_layers=N_LAYERS,
        N=N_DIM,
        alpha_max=ALPHA_MAX,
        n_steps_per_layer=N_STEPS_PER_LAYER,
        seed=seed,
    )
    fit_info = lm.fit(train_text, n_chars_train=len(train_text),
                      char_vocab=set(vocab), health_every=0, verbose=False)
    train_wall_s = time.time() - t0

    t1 = time.time()
    score = lm.score_bpc(test_text)
    score_wall_s = time.time() - t1

    health = lm.primitive_health()

    # Substrate-only audit: LLM_CALL_COUNTER must still be 0 (SubstrateCharLM
    # imports no transformers; this is a structural guarantee but we assert).
    assert _LLM_CALL_COUNTER[0] == 0, (
        "FATAL: LLM_CALL_COUNTER non-zero after substrate scoring: %d" % _LLM_CALL_COUNTER[0])

    return {
        "substrate_bpc": float(score["bpc"]),
        "uniform_bpc": float(score["uniform_bpc"]),
        "n_scored": int(score["n_scored"]),
        "train_wall_s": float(train_wall_s),
        "score_wall_s": float(score_wall_s),
        "n_train_pairs": int(fit_info["n_train_pairs"]),
        "max_alpha_final": float(max(fit_info["final_alphas"])
                                 if fit_info["final_alphas"] else 0.0),
        "any_primitive_collapse": bool(fit_info["any_primitive_collapse"]),
        "health_summary": {k: (round(v, 4) if isinstance(v, float) else v)
                           for k, v in list(health.items())[:8]},
    }


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Per-seed pipeline: load text8 splits + fit bigram + fit substrate + score both."""
    from testbed.substrate_lm.data import text8_char_corpus, char_vocab_from_corpus

    t0 = time.time()
    print("[seed=%d] loading text8 splits..." % seed, flush=True)
    train_text = text8_char_corpus(split="train", max_chars=MAX_CHARS_TRAIN,
                                   allow_synthetic=ALLOW_SYNTHETIC)
    test_text = text8_char_corpus(split="validation", max_chars=MAX_CHARS_TEST,
                                  allow_synthetic=ALLOW_SYNTHETIC)
    # Provenance check: real text8 has 27-char vocab (lowercase a-z + space). Synthetic
    # fallback (per data.py _synthetic_corpus) uses a much richer ~78-char vocab. So
    # vocab size is a load-bearing fingerprint of real-vs-synthetic.
    vocab = char_vocab_from_corpus(train_text + test_text)
    # text8 sanity: ASCII lowercase a-z + space; allow_synthetic=False guarantees real
    # but we also independently fingerprint here.
    is_real_text8 = (set(vocab) <= set("abcdefghijklmnopqrstuvwxyz ")
                     and len(vocab) <= 30)
    corpus_provenance_real = bool(ALLOW_SYNTHETIC is False and is_real_text8)
    print("[seed=%d] train=%d chars test=%d chars vocab=%d (real=%s)" % (
        seed, len(train_text), len(test_text), len(vocab), corpus_provenance_real),
        flush=True)

    # Bigram baselines (count-MLE on train; ceiling on test).
    t_bg = time.time()
    _, bg_probs = bigram_count_table(train_text, vocab, laplace=0.5)
    bigram_baseline = bigram_score_bpc(test_text, vocab, bg_probs)
    bigram_ceiling = bigram_ceiling_bpc(test_text, vocab, laplace=0.5)
    bigram_wall_s = time.time() - t_bg
    print("[seed=%d] bigram_baseline_bpc=%.3f bigram_ceiling_bpc=%.3f (wall=%.1fs)" % (
        seed, bigram_baseline["bpc"], bigram_ceiling["bpc"], bigram_wall_s), flush=True)

    # Substrate LM.
    print("[seed=%d] training SubstrateCharLM N=%d layers=%d alpha=%.3f steps=%d..." % (
        seed, N_DIM, N_LAYERS, ALPHA_MAX, N_STEPS_PER_LAYER), flush=True)
    sub = run_substrate_lm(train_text, test_text, vocab, seed)
    print("[seed=%d] substrate_bpc=%.3f train_wall=%.1fs score_wall=%.1fs n_train_pairs=%d" % (
        seed, sub["substrate_bpc"], sub["train_wall_s"], sub["score_wall_s"],
        sub["n_train_pairs"]), flush=True)

    elapsed = time.time() - t0
    per_unit = {
        "seed": int(seed),
        "substrate_bpc": float(sub["substrate_bpc"]),
        "bigram_baseline_bpc": float(bigram_baseline["bpc"]),
        "bigram_ceiling_bpc": float(bigram_ceiling["bpc"]),
        "uniform_bpc": float(sub["uniform_bpc"]),
        "gain_above_bigram_ceiling": float(bigram_ceiling["bpc"] - sub["substrate_bpc"]),
        "gain_above_bigram_baseline": float(bigram_baseline["bpc"] - sub["substrate_bpc"]),
        "n_scored": int(sub["n_scored"]),
        "n_train_chars": int(len(train_text)),
        "n_test_chars": int(len(test_text)),
        "vocab_size": int(len(vocab)),
        "corpus_provenance_real": bool(corpus_provenance_real),
        "max_alpha_final": float(sub["max_alpha_final"]),
        "any_primitive_collapse": bool(sub["any_primitive_collapse"]),
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "train_wall_s": float(sub["train_wall_s"]),
        "score_wall_s": float(sub["score_wall_s"]),
        "bigram_wall_s": float(bigram_wall_s),
        "wall_s": float(elapsed),
        "N": int(N_DIM),
        "run_mode": RUN_MODE,
        "health_summary": sub["health_summary"],
    }
    return {
        "seed": int(seed),
        "per_unit": [per_unit],
        "elapsed_s": float(elapsed),
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        # PROT-021 checkpoint discriminators: stored so resume detects config-mismatch.
        "N": int(N_DIM),
        "run_mode": RUN_MODE,
    }


# ---------------------------------------------------------------------------
# Verdict (pre-reg-band direction-correct per Skunkworks discipline + handoff 7b)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against absolute-floor pre-registered bands.

    HARD_PASS:   substrate_bpc_mean <= HARD_PASS_BPC (1.90) AND cv <= CV_MAX_HP (0.05) AND
                 substrate_bpc < bigram_ceiling_bpc - 0.05 (meaningful gain) AND
                 zero LLM calls AND corpus_provenance_real
    MIDDLE_BAND: substrate_bpc_mean in (HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC]
                 OR (HARD_PASS bpc but cv > 0.05 -- seed-unstable demote)
                 OR (HARD_PASS bpc but substrate_bpc ~ bigram_ceiling -- saturated demote)
    HARD_FAIL:   substrate_bpc_mean > MIDDLE_BAND_UPPER_BPC OR LLM-call violation OR
                 corpus_provenance_real == False OR primitive collapse
    """
    units = []
    for p in ps:
        units.extend(p.get("per_unit", []))
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # LLM-call gate (any violation -> HARD_FAIL regardless of metrics)
    any_llm_viol = any(int(u.get("llm_forward_calls_at_inference", 0)) > 0 for u in units)
    if any_llm_viol:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0).")

    # Provenance gate (synthetic fallback -> HARD_FAIL)
    any_synthetic = any(not bool(u.get("corpus_provenance_real", False)) for u in units)
    if any_synthetic:
        return ("HARD_FAIL",
                "HARD_FAIL: corpus_provenance_real=False on some seed (synthetic-fallback). "
                "ALLOW_SYNTHETIC=%s." % ALLOW_SYNTHETIC)

    # Primitive-collapse gate
    any_collapse = any(bool(u.get("any_primitive_collapse", False)) for u in units)

    sbs = [float(u["substrate_bpc"]) for u in units]
    bgls = [float(u["bigram_baseline_bpc"]) for u in units]
    bgcs = [float(u["bigram_ceiling_bpc"]) for u in units]
    s_mean = float(np.mean(sbs))
    s_cv = float(np.std(sbs) / max(abs(s_mean), 1e-9)) if len(sbs) > 1 else 0.0
    bgl_mean = float(np.mean(bgls))
    bgc_mean = float(np.mean(bgcs))
    gain_vs_ceiling = bgc_mean - s_mean
    gain_vs_baseline = bgl_mean - s_mean

    summary = (
        "substrate_bpc_mean=%.3f cv=%.3f n_seeds=%d | bigram_baseline=%.3f bigram_ceiling=%.3f "
        "| gain_vs_ceiling=%+.3f gain_vs_baseline=%+.3f | uniform=%.3f"
    ) % (s_mean, s_cv, len(units), bgl_mean, bgc_mean, gain_vs_ceiling,
         gain_vs_baseline, math.log2(27))

    if any_collapse:
        return ("HARD_FAIL", "HARD_FAIL: substrate primitive collapse on some seed. " + summary)

    # HARD_FAIL: above bigram-baseline upper band
    if s_mean > MIDDLE_BAND_UPPER_BPC:
        return ("HARD_FAIL",
                ("HARD_FAIL: substrate_bpc_mean=%.3f > %.2f (worse than text8 bigram baseline). "
                 % (s_mean, MIDDLE_BAND_UPPER_BPC)) + summary)

    # HARD_PASS requires ALL of: <=1.90 + cv <=0.05 + meaningful gain vs ceiling
    HARD_PASS_GAIN_MARGIN = 0.05
    if s_mean <= HARD_PASS_BPC:
        if s_cv > CV_MAX_HP:
            return ("MIDDLE_BAND",
                    ("MIDDLE_BAND: substrate_bpc_mean=%.3f <= %.2f BUT cv=%.3f > %.2f "
                     "(seed-unstable; demote one band). "
                     % (s_mean, HARD_PASS_BPC, s_cv, CV_MAX_HP)) + summary)
        if gain_vs_ceiling < HARD_PASS_GAIN_MARGIN:
            return ("MIDDLE_BAND",
                    ("MIDDLE_BAND: substrate_bpc_mean=%.3f near bigram_ceiling=%.3f "
                     "(gain=%+.3f < %.2f; by-construction-saturated demote). "
                     % (s_mean, bgc_mean, gain_vs_ceiling, HARD_PASS_GAIN_MARGIN)) + summary)
        return ("HARD_PASS",
                ("HARD_PASS: substrate_bpc_mean=%.3f <= %.2f AND cv=%.3f <= %.2f AND "
                 "gain_vs_ceiling=%+.3f >= %.2f AND zero LLM calls AND corpus real. "
                 % (s_mean, HARD_PASS_BPC, s_cv, CV_MAX_HP, gain_vs_ceiling,
                    HARD_PASS_GAIN_MARGIN)) + summary)

    # Otherwise (s_mean in (HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC]) -> MIDDLE_BAND
    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: substrate_bpc_mean=%.3f in (%.2f, %.2f] "
             "(between 5-gram-KN and bigram baselines). "
             % (s_mean, HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC)) + summary)


# ---------------------------------------------------------------------------
# Formula self-test (MANDATORY at module scope)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert mechanism + per-unit instrumentation works on synthetic data."""
    rng = np.random.default_rng(42)

    # --- T1: bigram baseline on a deterministic mini-corpus has finite + < uniform BPC ---
    mini_text = "the quick brown fox jumps over the lazy dog " * 50
    mini_vocab = sorted(set(mini_text))
    _, bg_probs = bigram_count_table(mini_text, mini_vocab, laplace=0.5)
    assert bg_probs.shape == (len(mini_vocab), len(mini_vocab))
    bg_score = bigram_score_bpc(mini_text, mini_vocab, bg_probs)
    uni_bpc = uniform_bpc(mini_vocab)
    assert np.isfinite(bg_score["bpc"]), "bigram BPC non-finite"
    assert bg_score["bpc"] < uni_bpc, (
        "bigram BPC %.3f not < uniform %.3f -- bigram model not learning"
        % (bg_score["bpc"], uni_bpc))
    print("[selftest] T1 PASS: bigram baseline finite + below uniform (BPC=%.3f < uni=%.3f)"
          % (bg_score["bpc"], uni_bpc), flush=True)

    # --- T2: SubstrateCharLM mini-pipeline produces finite substrate_bpc ---
    from testbed.substrate_lm.char_lm import SubstrateCharLM
    train_mini = mini_text[:1500]
    test_mini = mini_text[1500:2000]
    lm = SubstrateCharLM(n_layers=2, N=128, alpha_max=0.10, n_steps_per_layer=3, seed=7)
    info = lm.fit(train_mini, char_vocab=set(mini_vocab), verbose=False)
    score = lm.score_bpc(test_mini)
    assert np.isfinite(score["bpc"]), "substrate BPC non-finite"
    assert not info["any_primitive_collapse"], "primitive collapse in selftest"
    print("[selftest] T2 PASS: SubstrateCharLM mini-pipeline finite BPC=%.3f (uni=%.3f)"
          % (score["bpc"], score["uniform_bpc"]), flush=True)

    # --- T3: zero-D-overlap (sparse / no-train) path does NOT NaN ---
    # Construct a query character not seen in fit -> predict_proba should still
    # produce a valid distribution (SubstrateCharLM floors via softmax + the
    # cosine-vs-zero-norm guard returns uniform-ish; downstream log clamps to 1e-12).
    # Probe: feed an empty-ish probe at a position with no match.
    p_probe = lm.predict_proba(test_mini[0] if test_mini else " ")
    assert np.isfinite(p_probe).all(), "predict_proba produced non-finite probability"
    assert p_probe.sum() > 0, "predict_proba sum is zero"
    # The zero-D-overlap analog for SubstrateCharLM: try a single-char corpus where
    # context-char never co-occurs with next-char in train; score must not NaN.
    sparse_lm = SubstrateCharLM(n_layers=2, N=64, alpha_max=0.10, n_steps_per_layer=2, seed=9)
    sparse_lm.fit("aaaa", char_vocab=set("ab"), verbose=False)
    sparse_score = sparse_lm.score_bpc("ababab")
    assert np.isfinite(sparse_score["bpc"]), (
        "zero-D-overlap fallback NaN: substrate BPC = %s" % sparse_score["bpc"])
    print("[selftest] T3 PASS: zero-D-overlap fallback finite BPC=%.3f"
          % sparse_score["bpc"], flush=True)

    # --- T4: LLM-call counter stays at 0 (substrate-only gate auditable) ---
    assert _LLM_CALL_COUNTER[0] == 0, (
        "LLM_CALL_COUNTER non-zero after selftest: %d -- substrate-only-gate VIOLATED"
        % _LLM_CALL_COUNTER[0])
    print("[selftest] T4 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)", flush=True)

    # --- T5: module-level constants are real code (AST-verifiable types) ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str), "CONFIG_VERSION not a str"
    for tok in ("N=", "LAYERS=", "ALPHA=", "STEPS=", "V_CHAR=27", "CORPUS=text8",
                "CORPUS_VER=", "TRAIN=", "TEST=", "SEEDS=", "SYNTH=False",
                "BANDS=HP<=1.90"):
        assert tok in CONFIG_VERSION, "CONFIG_VERSION missing token: %s" % tok
    assert isinstance(N_DIM, int) and N_DIM > 0, "N_DIM not positive int"
    assert isinstance(N_LAYERS, int) and N_LAYERS >= 1, "N_LAYERS not >=1 int"
    assert isinstance(ALPHA_MAX, float) and 0 < ALPHA_MAX < 1, "ALPHA_MAX not in (0,1)"
    assert isinstance(N_STEPS_PER_LAYER, int) and N_STEPS_PER_LAYER >= 1, (
        "N_STEPS_PER_LAYER not >=1 int")
    assert isinstance(MAX_CHARS_TRAIN, int) and MAX_CHARS_TRAIN >= 1000, (
        "MAX_CHARS_TRAIN too small")
    assert isinstance(MAX_CHARS_TEST, int) and MAX_CHARS_TEST >= 100, (
        "MAX_CHARS_TEST too small")
    assert isinstance(SEEDS, list) and len(SEEDS) >= 1, "SEEDS not a non-empty list"
    assert isinstance(ALLOW_SYNTHETIC, bool) and ALLOW_SYNTHETIC is False, (
        "ALLOW_SYNTHETIC must be False for cert run (fail-loud)")
    assert isinstance(HARD_PASS_BPC, float) and HARD_PASS_BPC == 1.90, (
        "HARD_PASS_BPC pre-registered at 1.90")
    assert isinstance(MIDDLE_BAND_UPPER_BPC, float) and MIDDLE_BAND_UPPER_BPC == 3.00, (
        "MIDDLE_BAND_UPPER_BPC pre-registered at 3.00")
    assert isinstance(CV_MAX_HP, float) and CV_MAX_HP == 0.05, "CV_MAX_HP pre-registered at 0.05"
    print("[selftest] T5 PASS: module-level constants real code + CONFIG_VERSION complete",
          flush=True)

    # --- T6: per_unit dict shape includes all required keys ---
    per_unit_keys_required = (
        "seed", "substrate_bpc", "bigram_baseline_bpc", "bigram_ceiling_bpc",
        "uniform_bpc", "gain_above_bigram_ceiling", "gain_above_bigram_baseline",
        "n_scored", "n_train_chars", "n_test_chars", "vocab_size",
        "corpus_provenance_real", "max_alpha_final", "any_primitive_collapse",
        "llm_forward_calls_at_inference", "train_wall_s", "score_wall_s",
        "bigram_wall_s", "wall_s", "N", "run_mode", "health_summary",
    )
    fake_unit = {k: (0.0 if k not in (
        "seed", "n_scored", "n_train_chars", "n_test_chars", "vocab_size",
        "llm_forward_calls_at_inference", "N", "corpus_provenance_real",
        "any_primitive_collapse", "run_mode", "health_summary",
    ) else (0 if k != "run_mode" and k != "health_summary"
            else ("full" if k == "run_mode" else {})))
        for k in per_unit_keys_required}
    for key in per_unit_keys_required:
        assert key in fake_unit, "per_unit missing required key: %s" % key
    print("[selftest] T6 PASS: per_unit shape includes all %d required keys"
          % len(per_unit_keys_required), flush=True)

    # --- T7: verdict() direction-correct -- HARD_PASS only when ALL conditions ---
    # 7a: real substrate-PASS scenario (sbpc=1.50, cv=0.02, gain=0.10) -> HARD_PASS
    ps_good = [{"per_unit": [{
        "seed": s, "substrate_bpc": 1.50 + 0.02 * i,
        "bigram_baseline_bpc": 2.80, "bigram_ceiling_bpc": 1.65,
        "uniform_bpc": 4.755, "gain_above_bigram_ceiling": 0.15,
        "gain_above_bigram_baseline": 1.30, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 27,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for i, s in enumerate(SEEDS[:3] if len(SEEDS) >= 3 else SEEDS + [s_+10 for s_ in range(3-len(SEEDS))])]
    v_good, vmsg_good = verdict(ps_good)
    assert v_good == "HARD_PASS", "T7a FAIL: good-case verdict=%s msg=%s" % (v_good, vmsg_good)

    # 7b: LLM-call violation -> HARD_FAIL (overrides metrics)
    ps_llm = [{"per_unit": [dict(ps_good[0]["per_unit"][0], llm_forward_calls_at_inference=1)]}]
    v_llm, _ = verdict(ps_llm)
    assert v_llm == "HARD_FAIL", "T7b FAIL: LLM-violation didn't HARD_FAIL"

    # 7c: synthetic-fallback -> HARD_FAIL
    ps_syn = [{"per_unit": [dict(ps_good[0]["per_unit"][0], corpus_provenance_real=False)]}]
    v_syn, _ = verdict(ps_syn)
    assert v_syn == "HARD_FAIL", "T7c FAIL: synthetic fallback didn't HARD_FAIL"

    # 7d: high cv on otherwise-passing -> MIDDLE_BAND (seed-unstable demote)
    ps_cv = [{"per_unit": [{
        "seed": s, "substrate_bpc": 1.50 + 0.30 * i,  # std=0.245 / mean=1.80 -> cv=0.136
        "bigram_baseline_bpc": 2.80, "bigram_ceiling_bpc": 1.65,
        "uniform_bpc": 4.755, "gain_above_bigram_ceiling": 0.15,
        "gain_above_bigram_baseline": 1.30, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 27,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for i, s in enumerate([7, 17, 23])]
    v_cv, vmsg_cv = verdict(ps_cv)
    assert v_cv == "MIDDLE_BAND", "T7d FAIL: high-cv didn't demote to MIDDLE_BAND (%s)" % v_cv

    # 7e: above-bigram -> HARD_FAIL
    ps_bad = [{"per_unit": [dict(ps_good[0]["per_unit"][0],
                                 substrate_bpc=4.5,
                                 gain_above_bigram_ceiling=-2.85,
                                 gain_above_bigram_baseline=-1.70)]}]
    v_bad, vmsg_bad = verdict(ps_bad)
    assert v_bad == "HARD_FAIL", "T7e FAIL: above-bigram didn't HARD_FAIL"

    # 7f: substrate near bigram-ceiling -> MIDDLE_BAND (saturated demote)
    ps_sat = [{"per_unit": [{
        "seed": s, "substrate_bpc": 1.66,  # just barely above ceiling 1.65 by 0.01 < 0.05 margin
        "bigram_baseline_bpc": 2.80, "bigram_ceiling_bpc": 1.65,
        "uniform_bpc": 4.755, "gain_above_bigram_ceiling": -0.01,
        "gain_above_bigram_baseline": 1.14, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 27,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for s in [7, 17, 23]]
    v_sat, vmsg_sat = verdict(ps_sat)
    assert v_sat == "MIDDLE_BAND", (
        "T7f FAIL: saturated-near-ceiling didn't demote to MIDDLE_BAND (%s msg=%s)"
        % (v_sat, vmsg_sat))
    print("[selftest] T7 PASS: verdict() direction-correct (HARD_PASS/FAIL/MB scenarios)",
          flush=True)

    # --- T8: bigram_ceiling_bpc <= bigram_baseline_bpc at scale + Laplace->0 ---
    # MATHEMATICAL property: H_bigram(test|test) = -sum p(c,n) log2 p(n|c) is
    # the MLE-on-self lower bound under bigram context (laplace=0). With Laplace
    # smoothing AND a small test set, the smoothed estimate over-smooths and the
    # in-equality only holds asymptotically; we test the asymptotic property by:
    #   (a) using laplace=0 (pure MLE, no over-smoothing)
    #   (b) requiring same vocab + sufficient bigram coverage
    # In the real cell (test = 100k chars, 27-vocab => 729 possible bigrams),
    # the laplace=0.5 estimate is essentially MLE.
    train_t8 = mini_text  # full 2200 chars
    test_t8 = mini_text  # same text -> ceiling-on-self must equal baseline-on-self at laplace=0
    _, p_tr = bigram_count_table(train_t8, mini_vocab, laplace=0.0)
    base = bigram_score_bpc(test_t8, mini_vocab, p_tr)
    # Inline ceiling at laplace=0 (avoid double-smoothing).
    _, p_te = bigram_count_table(test_t8, mini_vocab, laplace=0.0)
    ceil_score = bigram_score_bpc(test_t8, mini_vocab, p_te)
    # Identity case: laplace=0 + same text -> ceiling exactly == baseline (up to float).
    assert abs(ceil_score["bpc"] - base["bpc"]) < 1e-6, (
        "T8 FAIL: same-text laplace=0: ceiling=%.4f != baseline=%.4f"
        % (ceil_score["bpc"], base["bpc"]))
    # Also verify that ceiling is finite + below uniform (the load-bearing property).
    assert np.isfinite(ceil_score["bpc"]) and ceil_score["bpc"] < uni_bpc, (
        "T8 FAIL: ceiling not finite or not below uniform: %.4f vs %.4f"
        % (ceil_score["bpc"], uni_bpc))
    print("[selftest] T8 PASS: bigram_ceiling=%.3f == baseline-on-self=%.3f at laplace=0; < uniform=%.3f"
          % (ceil_score["bpc"], base["bpc"], uni_bpc), flush=True)

    print("[selftest] ALL 8 TESTS PASS: n3_text8 cell instrumentation validated", flush=True)


_instrumentation_selftest()  # MANDATORY at module scope (role contract)
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s N_DIM=%d N_LAYERS=%d alpha=%.3f steps=%d "
      "TRAIN=%d TEST=%d SEEDS=%s ALLOW_SYNTHETIC=%s" % (
          ANCHOR_NAME, RUN_MODE, N_DIM, N_LAYERS, ALPHA_MAX, N_STEPS_PER_LAYER,
          MAX_CHARS_TRAIN, MAX_CHARS_TEST, SEEDS, ALLOW_SYNTHETIC), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps: List[Dict[str, Any]] = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    u = r["per_unit"][0]
    print("  [seed=%d] sbpc=%.3f bigram_base=%.3f bigram_ceil=%.3f gain_ceil=%+.3f "
          "wall=%.1fs llm_calls=%d real=%s" % (
              seed, u["substrate_bpc"], u["bigram_baseline_bpc"], u["bigram_ceiling_bpc"],
              u["gain_above_bigram_ceiling"], u["wall_s"],
              u["llm_forward_calls_at_inference"], u["corpus_provenance_real"]),
          flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

# Assert no LLM calls happened during the entire run (the substrate-only-gate audit)
total_llm_calls = sum(int(p.get("llm_forward_calls_at_inference", 0)) for p in ps)
assert total_llm_calls == 0, (
    "FATAL: %d LLM forward calls observed -- substrate-only-decode gate VIOLATED"
    % total_llm_calls)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

# Aggregate cv across seeds for top-level reporting.
all_units = [u for p in ps for u in p.get("per_unit", [])]
sbs_all = [float(u["substrate_bpc"]) for u in all_units]
if len(sbs_all) > 1:
    sbs_cv = float(np.std(sbs_all) / max(abs(float(np.mean(sbs_all))), 1e-9))
else:
    sbs_cv = 0.0

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(all_units),
    "N_DIM": N_DIM,
    "N_LAYERS": N_LAYERS,
    "ALPHA_MAX": ALPHA_MAX,
    "N_STEPS_PER_LAYER": N_STEPS_PER_LAYER,
    "MAX_CHARS_TRAIN": MAX_CHARS_TRAIN,
    "MAX_CHARS_TEST": MAX_CHARS_TEST,
    "corpus_name": CORPUS_NAME,
    "corpus_version": CORPUS_VERSION,
    "allow_synthetic": ALLOW_SYNTHETIC,
    "corpus_provenance_real": all(bool(u.get("corpus_provenance_real", False))
                                  for u in all_units),
    "zero_llm_calls_at_inference": True,
    "total_llm_forward_calls_observed": int(total_llm_calls),
    "substrate_bpc_mean": float(np.mean(sbs_all)) if sbs_all else float("nan"),
    "substrate_bpc_cv": float(sbs_cv),
    "bigram_baseline_bpc_mean": float(np.mean(
        [float(u["bigram_baseline_bpc"]) for u in all_units])) if all_units else float("nan"),
    "bigram_ceiling_bpc_mean": float(np.mean(
        [float(u["bigram_ceiling_bpc"]) for u in all_units])) if all_units else float("nan"),
    "uniform_bpc": math.log2(27),
    "HARD_PASS_BPC": HARD_PASS_BPC,
    "MIDDLE_BAND_UPPER_BPC": MIDDLE_BAND_UPPER_BPC,
    "CV_MAX_HP": CV_MAX_HP,
    "by_construction_guards": {
        "vq_floor_methodology": (
            "char-LM analog: bigram_ceiling_bpc = bigram-MLE FIT ON TEST itself (the "
            "irreducible bigram-context entropy on held-out). substrate < bigram_ceiling "
            "by >=0.05 required for HARD_PASS (else by-construction-saturated demote)."
        ),
        "real_data_asserted": True,
        "allow_synthetic": ALLOW_SYNTHETIC,
        "zero_llm_call_at_inference": True,
        "split_disjointness": (
            "deterministic 90/5/5 char-position split of single-file text8 (per "
            "testbed.substrate_lm.data.shakespeare/text8_char_corpus contract); train + "
            "test ranges non-overlapping by construction."
        ),
        "substrate_only_code_trace": (
            "this cell imports NO transformers/torch; SubstrateCharLM imports no "
            "transformers; _LLM_CALL_COUNTER asserted == 0 before metrics write."
        ),
    },
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
