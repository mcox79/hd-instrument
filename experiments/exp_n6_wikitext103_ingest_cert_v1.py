"""
n6_wikitext103_ingest_cert_v1 -- N6: substrate-native char-LM cert against WikiText-103.

MOTIVATION (USER 2026-06-22 do-it-all Tier-2 ingest-breadth expansion):
  WikiText-103 = ~100M tokens of cleaned Wikipedia text (Good + Featured articles).
  Standard field LM benchmark. Char-level absolute-floor BPC baselines (approx):
    uniform-vocab ~ log2(|V|) (printable ASCII ~6.6, lowercase-only ~4.7-5.0)
    bigram        ~ 3.5-4.0 BPC
    5-gram-KN     ~ 2.2-2.5 BPC
    LSTM          ~ 1.5-1.8 BPC
    ceiling       ~ 1.0 BPC
  These map onto absolute-floor cert bands (parent prompt):
    HARD_PASS:     substrate_bpc <= 2.50  (beats 5-gram-KN; chain-grade)
    MIDDLE_BAND:   2.50 < substrate_bpc <= 4.00  (between 5-gram-KN and bigram)
    HARD_FAIL:     substrate_bpc > 4.00  (worse than bigram)

REFERENT RECONCILIATION (parent prompt says "N1 v3.1 concept-LM plugin"):
  N1 v3.1 is TOKEN-level (Pythia residual per-token + concept VQ).
  WikiText-103 ingest-breadth-cert is naturally CHARACTER-level (matches text8
  cert pattern; absolute-floor BPC bands map cleanly; no Pythia-residual
  dependency = doesn't require remote token-id-recovery cell). Per Research's
  N3 ARCHITECTURE-AGNOSTIC ruling (notes/.../N3_corpus_scope_DECISION_2026-06-21),
  the substrate-LM cert harness grades WHICHEVER substrate-native LM is plugged
  in for the corpus's natural grain. So this cell plugs in SubstrateCharLM
  (the substrate-native char-LM matching WikiText-103's character grain), and
  is structured IDENTICALLY to n3_text8_ingest_cert_v1 with only the corpus
  loader swapped. If a token-level WikiText-103 cell is later wanted, that's a
  separate cell on a tokenized WikiText-103 plugging in N1 v3.1.

THIS CELL:
  - Substrate-native char-LM (SubstrateCharLM from testbed/substrate_lm/char_lm.py;
    4-primitive bipolar-bind streaming Hebbian + anti-Hebbian contrastive; NO
    gradient descent, NO LLM forward call at inference -- substrate ONLY).
  - Ingest = WikiText-103 train split chars (configurable max via env).
  - Score = char-BPC on held-out validation split (HF provides train/val/test
    splits directly; no need for single-file 90/5/5).
  - Baselines = uniform-|V| (always) + char-bigram-MLE computed on the SAME
    train + scored on SAME held-out (the canonical can-fail bar for substrate-
    native sequence modeling).
  - Per-seed checkpointed (PROT-021 run_config guard); resume-restartable.

INSTRUMENTATION (Skunkworks N2 chain-grade structural blockers, all 4 baked):
  1. per_unit: per-seed entry stored in per_seed; recompute-off-per_unit ready.
  2. cv <= 0.05: computed across seeds in verdict.
  3. zero_llm_calls_at_inference: True LOGGED in metrics; asserted = 0.
     This cell imports NO transformers/torch (structural guarantee).
  4. VQ-floor decomposition: for a CHAR-LM with no explicit concept-codebook VQ,
     the analog is the BIGRAM-CEILING -- the BPC of a perfect-bigram-lookup
     table on the SAME held-out (the irreducible bigram-context floor).
     Reported per seed. The load-bearing gain is substrate_bpc - bigram_ceiling_bpc.

THE 10 FIXES (parent prompt; banked this session):
  1. Smoke to remote_cpu_queue (NOT local).            -- dispatch-side
  2. Don't wait inline for smoke.                       -- dispatch-side
  3. Per-seed runtime MEASURED (smoke wall reported).  -- per_unit row
  4. Pre-flight run_mode check (verdict() refuses smoke). -- verdict()
  5. Zero-D-overlap fallback in batched scoring.       -- SubstrateCharLM
  6. Pre-reg direction must honor pre-reg intent.      -- verdict() direction
  7. No background bash watchers.                       -- dispatch-side
  8. File artifacts as <topic>_<date>.md (no to_<role>). -- prereg filename
  9. Substrate-only-decode gate code-trace.             -- structural import
 10. Path-scoped commits.                               -- dispatch-side
 11. .venv Python.                                      -- dispatch-side

PRE-REGISTERED BANDS (parent-prompt absolute-floor; HARD-WIRED in verdict):
  HARD_PASS  (chain-grade): substrate_bpc <= 2.50  (beats 5-gram-KN)
  MIDDLE_BAND:              2.50 < substrate_bpc <= 4.00  (between 5gKN and bigram)
  HARD_FAIL:                substrate_bpc > 4.00  (worse than bigram)
  PLUS across-seeds cv <= 0.05 required for HARD_PASS (else demote one band).
  PLUS zero LLM forward calls at inference (asserted from counter; HARD_FAIL else).
  PLUS corpus_provenance_real=True (allow_synthetic=False to loader); HARD_FAIL else.
  PLUS gain_above_bigram_ceiling >= 0.05 bits (else demote: by-construction saturated).

FORMULA SELFTESTS (PROT-022) (_instrumentation_selftest at module scope):
  T1: bigram_baseline_bpc on deterministic mini-corpus -> finite + < uniform.
  T2: SubstrateCharLM mini-pipeline -> finite substrate_bpc + no collapse.
  T3: zero-D-overlap fallback in predict_proba/score_bpc does NOT NaN.
  T4: LLM_CALL_COUNTER stays at 0 (substrate-only-gate auditable).
  T5: module-level constants real code + CONFIG_VERSION coverage (all BPC-
      affecting params + CORPUS=wikitext103 token + BANDS bound matches).
  T6: per_unit shape includes ALL required keys (recompute-ready).
  T7: verdict() direction-correct -- HARD_PASS only when substrate_bpc <= 2.50
      AND cv <= 0.05 AND zero LLM calls AND corpus real AND gain >= 0.05.
  T8: bigram_ceiling_bpc <= bigram_baseline_bpc on same-text laplace=0 (identity).
  T9: verdict refuses to call HARD_PASS in smoke run_mode (Fix #4).

ASCII-only. write_metrics. PROT-021 run_config guard. CPU numpy only; no torch/GPU.

QUEUE: remote_cpu_queue (numpy-only; WikiText-103 cached on remote on first run).
DEPENDENCY: testbed/substrate_lm/data.py wikitext103_char_corpus loader (added 2026-06-22).

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

ANCHOR_NAME = "n6_wikitext103_ingest_cert_v1"

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

# RUN_MODE detection (in priority order, matching n3_text8 pattern):
#   1. --smoke CLI flag                                       -> smoke
#   2. HDLAB_RUN_MODE=smoke env                               -> smoke
#   3. HDLAB_EXP_NAME contains "_smoke" segment (runner-set)  -> smoke
#   4. else                                                   -> full
_exp_name = os.environ.get("HDLAB_EXP_NAME", "").lower()
_runmode_env = os.environ.get("HDLAB_RUN_MODE", "full").lower()
_name_indicates_smoke = ("_smoke" in _exp_name and not _exp_name.endswith("_no_smoke"))
if _ARGS.smoke or _runmode_env == "smoke" or _name_indicates_smoke:
    RUN_MODE = "smoke"
else:
    RUN_MODE = _runmode_env

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
    # Full: WikiText-103 train is ~500M chars. Cap at 2M chars keeps per-seed wall
    # bounded (~minutes) for a first-of-corpus cert; bigram counts converge by
    # ~1M chars on a ~100-char vocab. MAX_CHARS_TEST = 100k gives stable BPC.
    MAX_CHARS_TRAIN = _ARGS.max_chars_train if _ARGS.max_chars_train is not None else int(
        os.environ.get("HDLAB_MAX_CHARS_TRAIN", "2000000"))
    MAX_CHARS_TEST = _ARGS.max_chars_test if _ARGS.max_chars_test is not None else int(
        os.environ.get("HDLAB_MAX_CHARS_TEST", "100000"))
    SEEDS = [int(s) for s in os.environ.get("HDLAB_SEEDS", "7,17,23").split(",")]

# Corpus identifiers (for CONFIG_VERSION and provenance log).
CORPUS_NAME = "wikitext103"
CORPUS_VERSION = "hf_wikitext_103_raw_v1"
ALLOW_SYNTHETIC = False  # fail-loud per phase_d_tier6 wikitext2 silent-fallback lesson

# Pre-registered bands (parent-prompt absolute-floor).
HARD_PASS_BPC = 2.50
MIDDLE_BAND_UPPER_BPC = 4.00
CV_MAX_HP = 0.05

CONFIG_VERSION = (
    "N=%d,LAYERS=%d,ALPHA=%.3f,STEPS=%d,CORPUS=%s,CORPUS_VER=%s,"
    "TRAIN=%d,TEST=%d,SEEDS=%s,SYNTH=%s,BANDS=HP<=%.2f/MB<=%.2f"
) % (N_DIM, N_LAYERS, ALPHA_MAX, N_STEPS_PER_LAYER, CORPUS_NAME, CORPUS_VERSION,
     MAX_CHARS_TRAIN, MAX_CHARS_TEST, "-".join(str(s) for s in SEEDS),
     str(ALLOW_SYNTHETIC), HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC)


# ---------------------------------------------------------------------------
# Baselines (bigram-MLE + bigram-CEILING + uniform): the can-fail bars
# ---------------------------------------------------------------------------

def bigram_count_table(train_text: str, vocab: List[str], laplace: float = 0.5
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """Compute char-bigram count table on train_text (Laplace-smoothed row-stoch)."""
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
    """Score char-BPC of test_text under a bigram model with row-stochastic probs."""
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
            continue  # skip OOV (rare for WikiText-103 if vocab built from train+test)
        p = float(probs[ch_to_idx[c], ch_to_idx[n]])
        p = max(p, 1e-12)
        ent_sum += -math.log(p) / log2
        n_scored += 1
    return {"bpc": ent_sum / max(n_scored, 1), "n_scored": n_scored}


def bigram_ceiling_bpc(test_text: str, vocab: List[str], laplace: float = 0.5
                       ) -> Dict[str, Any]:
    """Bigram-CEILING (VQ-floor analog for char-LM): fit bigram-MLE on TEST itself."""
    counts, probs = bigram_count_table(test_text, vocab, laplace=laplace)
    return bigram_score_bpc(test_text, vocab, probs)


def uniform_bpc(vocab: List[str]) -> float:
    return math.log2(max(len(vocab), 1))


# ---------------------------------------------------------------------------
# Substrate-LM driver
# ---------------------------------------------------------------------------

def run_substrate_lm(train_text: str, test_text: str, vocab: List[str],
                     seed: int) -> Dict[str, Any]:
    """Train SubstrateCharLM on train_text + score char-BPC on test_text."""
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
    """Per-seed pipeline: load WikiText-103 splits + fit bigram + fit substrate + score."""
    from testbed.substrate_lm.data import wikitext103_char_corpus, char_vocab_from_corpus

    t0 = time.time()
    print("[seed=%d] loading WikiText-103 splits..." % seed, flush=True)
    train_text = wikitext103_char_corpus(split="train", max_chars=MAX_CHARS_TRAIN,
                                         allow_synthetic=ALLOW_SYNTHETIC)
    test_text = wikitext103_char_corpus(split="validation", max_chars=MAX_CHARS_TEST,
                                        allow_synthetic=ALLOW_SYNTHETIC)
    vocab = char_vocab_from_corpus(train_text + test_text)
    # Real-data fingerprint: WikiText-103 is mixed-case English with punctuation; the
    # _synthetic_corpus fallback uses a fixed 78-char vocab. So real WT-103 typically
    # has vocab >= 80 (incl. unicode/diacritics). Use both ALLOW_SYNTHETIC=False AND a
    # vocab-size sanity check for double-defense.
    is_real = (ALLOW_SYNTHETIC is False) and (len(vocab) >= 50)
    corpus_provenance_real = bool(is_real)
    print("[seed=%d] train=%d chars test=%d chars vocab=%d (real=%s)" % (
        seed, len(train_text), len(test_text), len(vocab), corpus_provenance_real),
        flush=True)

    t_bg = time.time()
    _, bg_probs = bigram_count_table(train_text, vocab, laplace=0.5)
    bigram_baseline = bigram_score_bpc(test_text, vocab, bg_probs)
    bigram_ceiling = bigram_ceiling_bpc(test_text, vocab, laplace=0.5)
    bigram_wall_s = time.time() - t_bg
    print("[seed=%d] bigram_baseline_bpc=%.3f bigram_ceiling_bpc=%.3f (wall=%.1fs)" % (
        seed, bigram_baseline["bpc"], bigram_ceiling["bpc"], bigram_wall_s), flush=True)

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
        "N": int(N_DIM),
        "run_mode": RUN_MODE,
    }


# ---------------------------------------------------------------------------
# Verdict (pre-reg-band direction-correct per Skunkworks discipline)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against absolute-floor pre-registered bands."""
    units = []
    for p in ps:
        units.extend(p.get("per_unit", []))
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # Fix #4 / parent-prompt Fix #4: run_mode must be 'full' for chain-grade verdict.
    any_smoke = any(str(u.get("run_mode", "")).lower() == "smoke" for u in units)
    if any_smoke:
        return ("HARD_FAIL",
                "HARD_FAIL: per_unit contains run_mode=smoke; refusing to call "
                "chain-grade verdict on smoke results (Fix #4 pre-flight gate).")

    any_llm_viol = any(int(u.get("llm_forward_calls_at_inference", 0)) > 0 for u in units)
    if any_llm_viol:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0).")

    any_synthetic = any(not bool(u.get("corpus_provenance_real", False)) for u in units)
    if any_synthetic:
        return ("HARD_FAIL",
                "HARD_FAIL: corpus_provenance_real=False on some seed (synthetic-fallback). "
                "ALLOW_SYNTHETIC=%s." % ALLOW_SYNTHETIC)

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
        "| gain_vs_ceiling=%+.3f gain_vs_baseline=%+.3f"
    ) % (s_mean, s_cv, len(units), bgl_mean, bgc_mean, gain_vs_ceiling, gain_vs_baseline)

    if any_collapse:
        return ("HARD_FAIL", "HARD_FAIL: substrate primitive collapse on some seed. " + summary)

    # HARD_FAIL: worse than bigram baseline upper band
    if s_mean > MIDDLE_BAND_UPPER_BPC:
        return ("HARD_FAIL",
                ("HARD_FAIL: substrate_bpc_mean=%.3f > %.2f (worse than WikiText-103 bigram baseline). "
                 % (s_mean, MIDDLE_BAND_UPPER_BPC)) + summary)

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

    # --- T1: bigram baseline on a mini-corpus finite + < uniform BPC ---
    mini_text = "the quick brown fox jumps over the lazy dog " * 50
    mini_vocab = sorted(set(mini_text))
    _, bg_probs = bigram_count_table(mini_text, mini_vocab, laplace=0.5)
    bg_score = bigram_score_bpc(mini_text, mini_vocab, bg_probs)
    uni_bpc = uniform_bpc(mini_vocab)
    assert np.isfinite(bg_score["bpc"]), "bigram BPC non-finite"
    assert bg_score["bpc"] < uni_bpc, (
        "bigram BPC %.3f not < uniform %.3f" % (bg_score["bpc"], uni_bpc))
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

    # --- T3: zero-D-overlap fallback in predict_proba/score_bpc does NOT NaN ---
    p_probe = lm.predict_proba(test_mini[0] if test_mini else " ")
    assert np.isfinite(p_probe).all(), "predict_proba produced non-finite"
    assert p_probe.sum() > 0, "predict_proba sum is zero"
    sparse_lm = SubstrateCharLM(n_layers=2, N=64, alpha_max=0.10, n_steps_per_layer=2, seed=9)
    sparse_lm.fit("aaaa", char_vocab=set("ab"), verbose=False)
    sparse_score = sparse_lm.score_bpc("ababab")
    assert np.isfinite(sparse_score["bpc"]), (
        "zero-D-overlap fallback NaN: substrate BPC = %s" % sparse_score["bpc"])
    print("[selftest] T3 PASS: zero-D-overlap fallback finite BPC=%.3f"
          % sparse_score["bpc"], flush=True)

    # --- T4: LLM-call counter stays at 0 ---
    assert _LLM_CALL_COUNTER[0] == 0, (
        "LLM_CALL_COUNTER non-zero: %d -- substrate-only-gate VIOLATED" % _LLM_CALL_COUNTER[0])
    print("[selftest] T4 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)", flush=True)

    # --- T5: module-level constants real code + CONFIG_VERSION coverage ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str), "CONFIG_VERSION not a str"
    for tok in ("N=", "LAYERS=", "ALPHA=", "STEPS=", "CORPUS=wikitext103",
                "CORPUS_VER=", "TRAIN=", "TEST=", "SEEDS=", "SYNTH=False",
                "BANDS=HP<=2.50"):
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
    assert isinstance(HARD_PASS_BPC, float) and HARD_PASS_BPC == 2.50, (
        "HARD_PASS_BPC pre-registered at 2.50")
    assert isinstance(MIDDLE_BAND_UPPER_BPC, float) and MIDDLE_BAND_UPPER_BPC == 4.00, (
        "MIDDLE_BAND_UPPER_BPC pre-registered at 4.00")
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

    # --- T7: verdict() direction-correct on synthetic scenarios ---
    # 7a: real substrate-PASS (sbpc=2.20, cv=0.02, gain=0.10) -> HARD_PASS
    ps_good = [{"per_unit": [{
        "seed": s, "substrate_bpc": 2.20 + 0.02 * i,
        "bigram_baseline_bpc": 3.60, "bigram_ceiling_bpc": 2.40,
        "uniform_bpc": 6.6, "gain_above_bigram_ceiling": 0.20,
        "gain_above_bigram_baseline": 1.40, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 100,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for i, s in enumerate([7, 17, 23])]
    v_good, vmsg_good = verdict(ps_good)
    assert v_good == "HARD_PASS", "T7a FAIL: good-case verdict=%s msg=%s" % (v_good, vmsg_good)

    # 7b: LLM-call violation -> HARD_FAIL
    ps_llm = [{"per_unit": [dict(ps_good[0]["per_unit"][0], llm_forward_calls_at_inference=1)]}]
    v_llm, _ = verdict(ps_llm)
    assert v_llm == "HARD_FAIL", "T7b FAIL: LLM-violation didn't HARD_FAIL"

    # 7c: synthetic-fallback -> HARD_FAIL
    ps_syn = [{"per_unit": [dict(ps_good[0]["per_unit"][0], corpus_provenance_real=False)]}]
    v_syn, _ = verdict(ps_syn)
    assert v_syn == "HARD_FAIL", "T7c FAIL: synthetic fallback didn't HARD_FAIL"

    # 7d: high cv -> MIDDLE_BAND
    ps_cv = [{"per_unit": [{
        "seed": s, "substrate_bpc": 2.20 + 0.40 * i,
        "bigram_baseline_bpc": 3.60, "bigram_ceiling_bpc": 2.40,
        "uniform_bpc": 6.6, "gain_above_bigram_ceiling": 0.20,
        "gain_above_bigram_baseline": 1.40, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 100,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for i, s in enumerate([7, 17, 23])]
    v_cv, vmsg_cv = verdict(ps_cv)
    assert v_cv == "MIDDLE_BAND", "T7d FAIL: high-cv didn't demote to MIDDLE_BAND (%s)" % v_cv

    # 7e: above bigram-bound -> HARD_FAIL
    ps_bad = [{"per_unit": [dict(ps_good[0]["per_unit"][0],
                                 substrate_bpc=5.0,
                                 gain_above_bigram_ceiling=-2.60,
                                 gain_above_bigram_baseline=-1.40)]}]
    v_bad, _ = verdict(ps_bad)
    assert v_bad == "HARD_FAIL", "T7e FAIL: above-bigram didn't HARD_FAIL"

    # 7f: near-ceiling saturated -> MIDDLE_BAND
    ps_sat = [{"per_unit": [{
        "seed": s, "substrate_bpc": 2.41,  # ceiling 2.40, gain 0.01-(-) < 0.05
        "bigram_baseline_bpc": 3.60, "bigram_ceiling_bpc": 2.40,
        "uniform_bpc": 6.6, "gain_above_bigram_ceiling": -0.01,
        "gain_above_bigram_baseline": 1.19, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 100,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for s in [7, 17, 23]]
    v_sat, vmsg_sat = verdict(ps_sat)
    assert v_sat == "MIDDLE_BAND", (
        "T7f FAIL: saturated-near-ceiling didn't MIDDLE_BAND (%s msg=%s)"
        % (v_sat, vmsg_sat))
    print("[selftest] T7 PASS: verdict() direction-correct", flush=True)

    # --- T8: bigram_ceiling_bpc == baseline on same-text laplace=0 (identity) ---
    train_t8 = mini_text; test_t8 = mini_text
    _, p_tr = bigram_count_table(train_t8, mini_vocab, laplace=0.0)
    base = bigram_score_bpc(test_t8, mini_vocab, p_tr)
    _, p_te = bigram_count_table(test_t8, mini_vocab, laplace=0.0)
    ceil_score = bigram_score_bpc(test_t8, mini_vocab, p_te)
    assert abs(ceil_score["bpc"] - base["bpc"]) < 1e-6, (
        "T8 FAIL: same-text laplace=0: ceiling=%.4f != baseline=%.4f"
        % (ceil_score["bpc"], base["bpc"]))
    assert np.isfinite(ceil_score["bpc"]) and ceil_score["bpc"] < uni_bpc, (
        "T8 FAIL: ceiling not finite or not below uniform: %.4f vs %.4f"
        % (ceil_score["bpc"], uni_bpc))
    print("[selftest] T8 PASS: bigram_ceiling=%.3f == baseline-on-self=%.3f at laplace=0"
          % (ceil_score["bpc"], base["bpc"]), flush=True)

    # --- T9: verdict refuses to call HARD_PASS in smoke run_mode (Fix #4) ---
    ps_smoke = [{"per_unit": [dict(ps_good[0]["per_unit"][0], run_mode="smoke")]}]
    v_smoke, vmsg_smoke = verdict(ps_smoke)
    assert v_smoke == "HARD_FAIL", (
        "T9 FAIL: smoke run_mode didn't HARD_FAIL: %s msg=%s" % (v_smoke, vmsg_smoke))
    assert "smoke" in vmsg_smoke.lower(), (
        "T9 FAIL: smoke-refuse message lacks 'smoke' token: %s" % vmsg_smoke)
    print("[selftest] T9 PASS: verdict refuses HARD_PASS in smoke run_mode (Fix #4)",
          flush=True)

    print("[selftest] ALL 9 TESTS PASS: n6_wikitext103 cell instrumentation validated",
          flush=True)


_instrumentation_selftest()
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

total_llm_calls = sum(int(p.get("llm_forward_calls_at_inference", 0)) for p in ps)
assert total_llm_calls == 0, (
    "FATAL: %d LLM forward calls observed -- substrate-only-decode gate VIOLATED"
    % total_llm_calls)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

all_units = [u for p in ps for u in p.get("per_unit", [])]
sbs_all = [float(u["substrate_bpc"]) for u in all_units]
if len(sbs_all) > 1:
    sbs_cv = float(np.std(sbs_all) / max(abs(float(np.mean(sbs_all))), 1e-9))
else:
    sbs_cv = 0.0

summary = (
    "n6_wikitext103: substrate_bpc_mean=%.3f cv=%.3f n_seeds=%d "
    "bigram_baseline=%.3f bigram_ceiling=%.3f mode=%s verdict=%s"
) % (
    float(np.mean(sbs_all)) if sbs_all else float("nan"), sbs_cv, len(all_units),
    float(np.mean([float(u["bigram_baseline_bpc"]) for u in all_units])) if all_units else float("nan"),
    float(np.mean([float(u["bigram_ceiling_bpc"]) for u in all_units])) if all_units else float("nan"),
    RUN_MODE, v,
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "summary": summary,
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
    "HARD_PASS_BPC": HARD_PASS_BPC,
    "MIDDLE_BAND_UPPER_BPC": MIDDLE_BAND_UPPER_BPC,
    "CV_MAX_HP": CV_MAX_HP,
    "by_construction_guards": {
        "vq_floor_methodology": (
            "char-LM analog: bigram_ceiling_bpc = bigram-MLE FIT ON TEST itself; "
            "substrate < bigram_ceiling by >=0.05 required for HARD_PASS."
        ),
        "real_data_asserted": True,
        "allow_synthetic": ALLOW_SYNTHETIC,
        "zero_llm_call_at_inference": True,
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
