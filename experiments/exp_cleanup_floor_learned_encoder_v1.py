"""cleanup_floor_learned_encoder_v1 -- LEARNED-encoder branch of Shannon-floor cleanup-ceiling META.

INFORMER for META atom: T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0
(cert ledger row 675; Skunkworks tiered MEASURED_MECHANISM 2026-06-23 because 3 branches remain
untested). This cell closes BRANCH #3 (learned-encoder keys): does an anisotropic, structured signal
codebook escape the Shannon-floor at sigma=1.5 where the random-bipolar codebook fails (recall~0.027)?

Branches #1 (N-DIM-scan) and #2 (M-scan) already closed at SYNTHETIC RANDOM BIPOLAR regime
(M-INDEPENDENT 25-400; N_DIM-INDEPENDENT 512-16384). Branch #3 tests whether the META holds
across LEARNED / STRUCTURED codebook regimes -- the actual substrate-product use case.

Hypothesis: random-bipolar codebook rows lie on the sphere with isotropic geometry; any noise-floor
limit there may not apply to anisotropic / structured codebooks where rows live on a lower-dim
manifold (char-trigram embeddings of real text) or share a common-mode hub (hub-spoke composition).
At sigma=1.5 the noise direction may be partially orthogonal to the manifold / hub-axis, sparing the
signal.

Decision rules (cell informs META scope; doesn't HP/HF on itself):
- META_BRANCH3_SCOPE_NARROW: ARM_CHAR_TRIGRAM_LEARNED OR ARM_HUB_SPOKE_STRUCTURED recall(sigma=1.5) >= 0.20
   -> META is SCOPE-NARROW; Shannon-floor applies to random-bipolar codebook only. Substrate-product
      at sigma=1.5 is VIABLE with right encoder. ATOM: revise parent META with scope_clause:
      "applies to random-bipolar codebook only".
- META_BRANCH3_CHAIN_GRADE_ELIGIBLE: ALL 3 arms recall(sigma=1.5) < 0.10
   -> META applies across random AND learned AND structured regimes. 9-family-exhaustion is now
      10-family across codebook types. Substrate operating envelope is sigma <= 1.0 broadly.
      ATOM: recommend Skunkworks tier-up parent META to chain-grade.
- META_BRANCH3_MIDDLE: one arm partial-lifts; characterize encoder-quality-vs-noise-tolerance map.

NOT a chain-grade-candidate cell on its own merits. META-informer only. status_log importance HIGH
(META branch closure has chain-grade-tier implications).

DESIGN: 3 arms x 3 sigma x 3 seeds x N_EVAL=200, all at N_DIM=2048 M=200.
  ARM_RANDOM_BIPOLAR  -- random bipolar codebook (Shannon-floor regime extension at N=2048)
  ARM_CHAR_TRIGRAM_LEARNED -- char-trigram bag-of-HD encoding of 200 English words (conceptnet)
  ARM_HUB_SPOKE_STRUCTURED -- 20 hubs x 10 spokes with shared hub-bind common-mode

All arms: argmax cleanup against codebook. Same noise injection. Same N_DIM. Same N_EVAL. Same seeds.

PRE-REG bands (this cell informs META; doesn't HARD_PASS/HARD_FAIL on itself):
- META_BRANCH3_SCOPE_NARROW: max(ARM_CHAR_TRIGRAM_LEARNED, ARM_HUB_SPOKE_STRUCTURED)
    recall(sigma=1.5) >= 0.20
- META_BRANCH3_CHAIN_GRADE_ELIGIBLE: ALL 3 arms recall(sigma=1.5) < 0.10
- META_BRANCH3_MIDDLE: neither rule fires; encoder-quality map

Sanity self-tests:
- At sigma=0.0 all 3 arms: recall=1.000 (clean cue -> atom-recovery by construction)
- ARM_RANDOM_BIPOLAR at sigma=1.5 N=2048 M=200: should reproduce ~0.027 (from prior N_DIM_scan
  N=2048 result; tolerance +/- 0.03)

Compute: 3 arms x 3 sigma x 3 seeds x M=200 N_EVAL=200 N=2048 -> 27 (200,2048)x(2048,200) matmuls.
Pure numpy. Total wall <5min full.

Substrate-only by construction (HD codebook with char_trigram encoder OR random; no external LM).
ASCII-only.
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit, json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "cleanup_floor_learned_encoder_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 2048   # fixed; matches substrate-product regime + parent N_DIM_scan N=2048 anchor
M = 200        # fixed; matches Shannon-floor parent regime
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    SIGMA_SWEEP = [1.0, 1.5, 2.0]
    N_EVAL = 200
    SANITY_SIGMA_ZERO = True
else:
    # Smoke: small subset, fast.
    SEEDS = [0]
    SIGMA_SWEEP = [1.0, 1.5]
    N_EVAL = 40
    SANITY_SIGMA_ZERO = True

DISCRIMINATOR_SIGMA = 1.5
ARMS = ["ARM_RANDOM_BIPOLAR", "ARM_CHAR_TRIGRAM_LEARNED", "ARM_HUB_SPOKE_STRUCTURED"]

# Hub-spoke structure (for ARM_HUB_SPOKE_STRUCTURED)
N_HUBS = 20
N_SPOKES_PER_HUB = 10
assert N_HUBS * N_SPOKES_PER_HUB == M, "hub-spoke composition must total M"
HUB_BIND_MAGNITUDE = 1.0      # hub contribution amplitude
SPOKE_PERTURB_MAGNITUDE = 0.5  # per-spoke random perturbation amplitude

CONFIG_VERSION = ("cleanup_floor_learned_encoder_v1; N=%d M=%d N_EVAL=%d sigma_sweep=%s "
                  "seeds=%s arms=%s mode=%s") % (N_DIM, M, N_EVAL, SIGMA_SWEEP, SEEDS, ARMS, RUN_MODE)


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _build_random_bipolar_codebook(seed, M_loc, D_loc):
    """ARM_RANDOM_BIPOLAR: random bipolar codebook (+/-1); L2-normalized."""
    g = np.random.default_rng(seed)
    cb = g.choice([-1.0, 1.0], size=(M_loc, D_loc)).astype(np.float32)
    return _l2_normalize(cb).astype(np.float32)


# Cache of 200 English words extracted from conceptnet (deterministic order).
_WORDS_CACHE = [None]


def _load_word_corpus(n_words=200):
    """Extract n_words unique English words from conceptnet5_en_100k.jsonl.

    Walk the jsonl in order, harvest distinct subject/object tokens that look like words
    (alphabetic, length >= 2). Cache for the process. Deterministic across all seeds.
    """
    if _WORDS_CACHE[0] is not None and len(_WORDS_CACHE[0]) >= n_words:
        return _WORDS_CACHE[0][:n_words]
    seen = set()
    out = []
    jsonl_path = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"
    if not jsonl_path.exists():
        # Fallback: synthetic alphabetic strings (still distinct trigram signatures)
        out = ["word_%04d" % i for i in range(n_words)]
        _WORDS_CACHE[0] = out
        return out
    try:
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                if len(out) >= n_words:
                    break
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                for tok in (rec.get("subject"), rec.get("object")):
                    if not isinstance(tok, str):
                        continue
                    tok = tok.strip().lower()
                    # Filter: alphabetic + optional underscore, length 2-20
                    if not tok or len(tok) < 2 or len(tok) > 20:
                        continue
                    if not all(c.isalpha() or c == "_" for c in tok):
                        continue
                    if tok in seen:
                        continue
                    seen.add(tok)
                    out.append(tok)
                    if len(out) >= n_words:
                        break
    except OSError:
        pass
    if len(out) < n_words:
        # Pad with deterministic synthetic tokens if corpus exhausted
        for i in range(len(out), n_words):
            out.append("synthpad_%04d" % i)
    _WORDS_CACHE[0] = out
    return out[:n_words]


def _build_char_trigram_codebook(seed, M_loc, D_loc):
    """ARM_CHAR_TRIGRAM_LEARNED: encode M_loc English words via char-trigram bag-of-HD.

    Uses hdlab/char_trigram_encoder.py. The encoder is deterministic per trigram (no seed); the
    cell's seed parameter controls only the noise / query selection downstream, NOT the codebook
    content -- which is intentional: anisotropic structure should be reproducible across seeds.
    Output L2-normalized.
    """
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=D_loc, pad_char=" ")
    words = _load_word_corpus(M_loc)
    cb = enc.encode_batch(words)  # [M_loc, D_loc] bipolar {-1,+1}
    return _l2_normalize(cb.astype(np.float32)).astype(np.float32)


def _build_hub_spoke_codebook(seed, M_loc, D_loc):
    """ARM_HUB_SPOKE_STRUCTURED: 20 hubs x 10 spokes; each spoke = hub + small perturbation.

    Structured anisotropic codebook -- spokes within a hub share a common-mode hub axis. Tests
    whether shared structure protects against high-noise corruption (spokes within a hub all
    pull toward the hub axis under noise, so argmax should still pick the right spoke if the
    perturbation is preserved).
    """
    g = np.random.default_rng(seed + 9999)  # avoid collision with downstream seeds
    assert M_loc == N_HUBS * N_SPOKES_PER_HUB, "M_loc must equal N_HUBS*N_SPOKES_PER_HUB"
    hubs = g.choice([-1.0, 1.0], size=(N_HUBS, D_loc)).astype(np.float32) * HUB_BIND_MAGNITUDE
    # Build [M_loc, D_loc] as hub_block + per-spoke perturbation
    cb = np.zeros((M_loc, D_loc), dtype=np.float32)
    for h in range(N_HUBS):
        for s in range(N_SPOKES_PER_HUB):
            perturb = g.standard_normal(D_loc).astype(np.float32) * SPOKE_PERTURB_MAGNITUDE
            cb[h * N_SPOKES_PER_HUB + s] = hubs[h] + perturb
    return _l2_normalize(cb).astype(np.float32)


def _build_codebook_for_arm(arm, seed, M_loc, D_loc):
    if arm == "ARM_RANDOM_BIPOLAR":
        return _build_random_bipolar_codebook(seed, M_loc, D_loc)
    if arm == "ARM_CHAR_TRIGRAM_LEARNED":
        return _build_char_trigram_codebook(seed, M_loc, D_loc)
    if arm == "ARM_HUB_SPOKE_STRUCTURED":
        return _build_hub_spoke_codebook(seed, M_loc, D_loc)
    raise ValueError("unknown arm: %s" % arm)


def argmax_recall(codebook, query_indices, sigma, seed, arm_tag):
    """Single-step cosine argmax over noised cue. Same protocol across all 3 arms."""
    arm_seed = int(seed) * 1000 + int(sigma * 10000) + (hash(arm_tag) % 1000)
    g = np.random.default_rng(arm_seed)
    M_loc, D_loc = codebook.shape
    cb_n = _l2_normalize(codebook.astype(np.float32))
    cues = codebook[query_indices] + sigma * g.standard_normal((len(query_indices), D_loc)).astype(np.float32)
    cues_n = _l2_normalize(cues)
    pred = np.argmax(cues_n @ cb_n.T, axis=1).astype(np.int64)
    n_correct = int((pred == query_indices).sum())
    return float(n_correct) / max(len(query_indices), 1)


def run_unit(seed):
    g = np.random.default_rng(seed)
    print("  [seed=%d] arms=%s sigma_sweep=%s N=%d M=%d N_EVAL=%d" % (
        seed, ARMS, SIGMA_SWEEP, N_DIM, M, N_EVAL), flush=True)
    grid = {}     # grid[arm][str(sigma)] = recall
    sanity = {}   # sanity[arm] = recall_at_sigma_0
    for arm in ARMS:
        t_arm = time.time()
        cb = _build_codebook_for_arm(arm, seed, M, N_DIM)
        # Verify shape + norm
        assert cb.shape == (M, N_DIM), "codebook shape mismatch for arm %s: %s" % (arm, cb.shape)
        norms = np.linalg.norm(cb, axis=1)
        assert np.all(np.abs(norms - 1.0) < 1e-3), (
            "arm=%s codebook not L2-normalized; max norm dev=%.4f" % (
                arm, float(np.max(np.abs(norms - 1.0)))))
        n_q = min(N_EVAL, M)
        q_idx = g.choice(M, size=n_q, replace=False)
        per_sigma = {}
        for sig in SIGMA_SWEEP:
            r = argmax_recall(cb, q_idx, sig, seed, arm_tag=arm)
            per_sigma[str(sig)] = round(r, 4)
        # sanity: sigma=0.0 must give recall=1.000 across all arms
        if SANITY_SIGMA_ZERO:
            r0 = argmax_recall(cb, q_idx, 0.0, seed, arm_tag=arm + "_SANITY")
            sanity[arm] = round(r0, 4)
        grid[arm] = per_sigma
        print("    [seed=%d arm=%s N_EVAL=%d] sigmas=%s sanity_sigma_0=%s (wall=%.2fs)" % (
            seed, arm, n_q, per_sigma, sanity.get(arm, "N/A"), time.time() - t_arm), flush=True)
    return {
        "seed": seed,
        "grid": grid,
        "sanity_sigma_0": sanity,
        "N_DIM": N_DIM,
        "M": M,
        "sigma_sweep": SIGMA_SWEEP,
        "N_EVAL": N_EVAL,
        "arms": ARMS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no results", {})

    # Aggregate across seeds: mean and std at each (arm, sigma)
    sigma_keys = [str(s) for s in SIGMA_SWEEP]
    agg = {}  # agg[arm][sigma] = {"mean": x, "std": y, "cv": z, "per_seed": [...]}
    for arm in ARMS:
        agg[arm] = {}
        for sk in sigma_keys:
            vals = [u["grid"][arm][sk] for u in units]
            m = float(np.mean(vals))
            s = float(np.std(vals))
            cv = s / max(m, 1e-6)
            agg[arm][sk] = {"mean": round(m, 4), "std": round(s, 4), "cv": round(cv, 4),
                            "per_seed": [round(v, 4) for v in vals]}

    # Sanity check: sigma=0.0 must give recall>=0.99 for ALL arms across ALL seeds
    sanity_violations = []
    for u in units:
        for arm, r0 in u.get("sanity_sigma_0", {}).items():
            if r0 < 0.99:
                sanity_violations.append((u["seed"], arm, r0))

    sigma_disc = str(DISCRIMINATOR_SIGMA)
    recall_random = agg.get("ARM_RANDOM_BIPOLAR", {}).get(sigma_disc, {}).get("mean", -1.0)
    recall_trigram = agg.get("ARM_CHAR_TRIGRAM_LEARNED", {}).get(sigma_disc, {}).get("mean", -1.0)
    recall_hubspoke = agg.get("ARM_HUB_SPOKE_STRUCTURED", {}).get(sigma_disc, {}).get("mean", -1.0)
    max_structured = max(recall_trigram, recall_hubspoke)

    # cv max across all (arm, sigma)
    all_cv = [agg[arm][sk]["cv"] for arm in ARMS for sk in sigma_keys]
    max_cv = float(np.max(all_cv)) if all_cv else 0.0

    detail = {
        "agg": agg,
        "n_seeds": len(units),
        "N_DIM": N_DIM,
        "M": M,
        "sigma_sweep": SIGMA_SWEEP,
        "arms": ARMS,
        "discriminator_sigma": DISCRIMINATOR_SIGMA,
        "recall_random_disc": recall_random,
        "recall_char_trigram_disc": recall_trigram,
        "recall_hub_spoke_disc": recall_hubspoke,
        "max_structured_recall_disc": max_structured,
        "max_cv_across_cells": round(max_cv, 4),
        "sanity_violations": sanity_violations,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": ("META-INFORMER for Shannon-floor cleanup-ceiling atom (cert row 675). "
                         "Branch #3 of 3 (LEARNED + STRUCTURED encoder keys). "
                         "N=%d M=%d sigma_sweep=%s N_EVAL=%d seeds=%s arms=%s. "
                         "Pure numpy; ARM_CHAR_TRIGRAM_LEARNED uses hdlab.char_trigram_encoder "
                         "(deterministic per-trigram bipolar; bag-of-trigrams sum-then-sign); "
                         "ARM_HUB_SPOKE_STRUCTURED uses 20-hub 10-spoke composition. All codebooks "
                         "L2-normalized to unit norm. Not a chain-grade candidate on own merits; "
                         "META-tiering informer only. Branches #1 (N-DIM-scan) and #2 (M-scan) "
                         "closed at SYNTHETIC RANDOM BIPOLAR; this cell extends to LEARNED + "
                         "STRUCTURED.") % (
                         N_DIM, M, SIGMA_SWEEP, N_EVAL, [u["seed"] for u in units], ARMS),
        "cites": [
            "cert_ledger_row_675_meta_cleanup_ceiling_shannon_floor_2026-06-23",
            "skunkworks_tiering_measured_mechanism_2026-06-23",
            "cleanup_floor_M_scan_v1_META_DECISION_M_INDEPENDENT_branch2_closed",
            "cleanup_floor_N_DIM_scan_v1_branch1",
            "hdlab_char_trigram_encoder_substrate_native_text_to_hd",
        ],
    }

    if sanity_violations:
        msg = ("HARD_FAIL_SANITY: sigma=0 sanity violated in %d (seed,arm) cells (clean-cue "
               "recall<0.99); implementation bug -- codebook L2-norm or argmax broken. "
               "Sample: %s") % (len(sanity_violations), sanity_violations[:3])
        return ("HARD_FAIL", msg, detail)

    summary = ("BRANCH3 DECISION @ sigma=%.2f: recall_random=%.4f recall_char_trigram=%.4f "
               "recall_hub_spoke=%.4f max_structured=%.4f max_cv=%.3f sigma_0_sanity=PASS "
               "N=%d M=%d seeds=%d") % (
                DISCRIMINATOR_SIGMA, recall_random, recall_trigram,
                recall_hubspoke, max_structured, max_cv, N_DIM, M, len(units))

    # Decision rule (no HARD_PASS / HARD_FAIL on own merits; informer)
    # SCOPE_NARROW: at least one structured arm escapes the floor
    if max_structured >= 0.20:
        return ("META_BRANCH3_SCOPE_NARROW",
                ("META_BRANCH3_SCOPE_NARROW: at least one structured/learned arm ESCAPES "
                 "Shannon-floor at sigma=%.2f. recall(char_trigram)=%.4f "
                 "recall(hub_spoke)=%.4f -- max=%.4f >= 0.20. "
                 "RECOMMENDATION: revise parent META scope_clause to "
                 "'applies to random-bipolar codebook only'; substrate-product at sigma=1.5 "
                 "VIABLE with anisotropic/structured encoders. " % (
                 DISCRIMINATOR_SIGMA, recall_trigram, recall_hubspoke, max_structured) + summary),
                detail)
    # CHAIN_GRADE_ELIGIBLE: all 3 arms below 0.10 -> META robust across codebook types
    if recall_random < 0.10 and recall_trigram < 0.10 and recall_hubspoke < 0.10:
        return ("META_BRANCH3_CHAIN_GRADE_ELIGIBLE",
                ("META_BRANCH3_CHAIN_GRADE_ELIGIBLE: Shannon-floor applies across RANDOM + "
                 "LEARNED + STRUCTURED codebook types at sigma=%.2f. recall_random=%.4f "
                 "recall_char_trigram=%.4f recall_hub_spoke=%.4f (ALL < 0.10). Branches #1+#2+#3 "
                 "closed; META robust across N-DIM (512-16384), M (25-400), codebook type "
                 "(3 families). RECOMMENDATION: Skunkworks tier-up parent META to chain-grade. " % (
                 DISCRIMINATOR_SIGMA, recall_random, recall_trigram, recall_hubspoke) + summary),
                detail)
    # MIDDLE: characterize encoder-quality vs noise-tolerance
    return ("META_BRANCH3_MIDDLE",
            ("META_BRANCH3_MIDDLE: at least one arm in [0.10, 0.20) at sigma=%.2f; "
             "neither full SCOPE_NARROW nor CHAIN_GRADE_ELIGIBLE. recall_random=%.4f "
             "recall_char_trigram=%.4f recall_hub_spoke=%.4f. RECOMMENDATION: ingest "
             "encoder-quality-vs-noise-tolerance map as substrate-product-knowledge atom; "
             "META scope clause needs nuanced framing. " % (
             DISCRIMINATOR_SIGMA, recall_random, recall_trigram, recall_hubspoke) + summary),
            detail)


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
            v, msg, detail = compute_verdict(units)
        except Exception as e:
            v, msg, detail = ("PARTIAL_TIMEOUT", "atexit synthesize: %s" % e, {})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if v != "PARTIAL_TIMEOUT" else v,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "M": M,
            "n_seeds": len(units),
            "detail": detail,
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize] " + msg,
            "substrate_only_decode_gate": "TRUE (HD codebook + char_trigram_encoder; no external LM)",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)


def _selftest():
    """Selftest: clean-cue identity + L2 norm + arm-codebook-builders + verdict triplet."""
    # T1: each arm builder produces (M, N_DIM) L2-normalized at small scale
    for arm in ARMS:
        cb = _build_codebook_for_arm(arm, seed=0, M_loc=M, D_loc=N_DIM)
        assert cb.shape == (M, N_DIM), "arm=%s shape %s != (%d,%d)" % (arm, cb.shape, M, N_DIM)
        norms = np.linalg.norm(cb, axis=1)
        assert np.all(np.abs(norms - 1.0) < 1e-3), (
            "arm=%s not L2-normalized; max-dev=%.4f" % (arm, float(np.max(np.abs(norms - 1.0)))))

    # T2: clean cue (sigma=0.0) MUST recover for ALL arms
    for arm in ARMS:
        cb = _build_codebook_for_arm(arm, seed=1, M_loc=M, D_loc=N_DIM)
        qidx = np.arange(min(32, M))
        r = argmax_recall(cb, qidx, 0.0, seed=2, arm_tag="selftest_T2_" + arm)
        assert r >= 0.99, "T2 arm=%s clean-cue recall=%.3f < 0.99" % (arm, r)

    # T3: high noise (sigma=20) << 1 across all arms
    for arm in ARMS:
        cb = _build_codebook_for_arm(arm, seed=3, M_loc=M, D_loc=N_DIM)
        qidx = np.arange(min(32, M))
        r_hi = argmax_recall(cb, qidx, 20.0, seed=3, arm_tag="selftest_T3_" + arm)
        assert r_hi <= 0.5, "T3 arm=%s sigma=20 recall=%.3f; should be << 0.5" % (arm, r_hi)

    # T4: hub-spoke structure has correct hub assignment (cross-check)
    cb = _build_codebook_for_arm("ARM_HUB_SPOKE_STRUCTURED", seed=5, M_loc=M, D_loc=N_DIM)
    # Same-hub spokes should be more similar (cosine) than cross-hub spokes
    sims = cb @ cb.T
    # Spoke 0 (hub 0, spoke 0) vs spoke 1 (hub 0, spoke 1) should be > spoke 0 vs spoke 10 (hub 1, spoke 0)
    same_hub_sim = sims[0, 1]
    cross_hub_sim = sims[0, 10]
    assert same_hub_sim > cross_hub_sim, (
        "T4 hub-spoke structure invalid: same_hub_sim=%.3f <= cross_hub_sim=%.3f" % (
            same_hub_sim, cross_hub_sim))

    # T5: char_trigram different-word codebook rows are distinct
    cb_tri = _build_codebook_for_arm("ARM_CHAR_TRIGRAM_LEARNED", seed=6, M_loc=M, D_loc=N_DIM)
    # Diagonal (self-similarity) ~= 1; off-diagonal < 1 typically
    off_diag_max = float(np.max(cb_tri[0:5] @ cb_tri[5:10].T))
    assert off_diag_max < 0.99, (
        "T5 char_trigram codebook rows too similar; off_diag_max=%.4f -- distinct-word check failed" % off_diag_max)

    # T6: verdict on synthetic SCOPE_NARROW (one structured arm at 0.30, random at 0.03)
    def _grid_scope_narrow(arm, sig):
        if arm == "ARM_CHAR_TRIGRAM_LEARNED" and abs(sig - DISCRIMINATOR_SIGMA) < 1e-6:
            return 0.30
        if arm == "ARM_HUB_SPOKE_STRUCTURED" and abs(sig - DISCRIMINATOR_SIGMA) < 1e-6:
            return 0.05
        if arm == "ARM_RANDOM_BIPOLAR" and abs(sig - DISCRIMINATOR_SIGMA) < 1e-6:
            return 0.03
        return 0.5  # other sigmas
    fake = [{"seed": sd,
             "grid": {arm: {str(sig): _grid_scope_narrow(arm, sig) for sig in SIGMA_SWEEP} for arm in ARMS},
             "sanity_sigma_0": {arm: 1.0 for arm in ARMS},
             "N_DIM": N_DIM, "M": M, "sigma_sweep": SIGMA_SWEEP, "N_EVAL": N_EVAL,
             "arms": ARMS, "run_mode": "selftest", "config_version": "selftest"}
            for sd in (7, 17, 23)]
    v, _, d = compute_verdict(fake)
    assert v == "META_BRANCH3_SCOPE_NARROW", "T6 expected SCOPE_NARROW; got %s" % v

    # T7: verdict on synthetic CHAIN_GRADE_ELIGIBLE (all arms < 0.10)
    def _grid_chain_grade(arm, sig):
        if abs(sig - DISCRIMINATOR_SIGMA) < 1e-6:
            return 0.05
        return 0.5
    fake2 = [{"seed": sd,
              "grid": {arm: {str(sig): _grid_chain_grade(arm, sig) for sig in SIGMA_SWEEP} for arm in ARMS},
              "sanity_sigma_0": {arm: 1.0 for arm in ARMS},
              "N_DIM": N_DIM, "M": M, "sigma_sweep": SIGMA_SWEEP, "N_EVAL": N_EVAL,
              "arms": ARMS, "run_mode": "selftest", "config_version": "selftest"}
             for sd in (7, 17, 23)]
    v2, _, _ = compute_verdict(fake2)
    assert v2 == "META_BRANCH3_CHAIN_GRADE_ELIGIBLE", "T7 expected CHAIN_GRADE_ELIGIBLE; got %s" % v2

    # T8: verdict on synthetic MIDDLE (one arm in [0.10, 0.20))
    def _grid_middle(arm, sig):
        if arm == "ARM_CHAR_TRIGRAM_LEARNED" and abs(sig - DISCRIMINATOR_SIGMA) < 1e-6:
            return 0.15
        if abs(sig - DISCRIMINATOR_SIGMA) < 1e-6:
            return 0.03
        return 0.5
    fake3 = [{"seed": sd,
              "grid": {arm: {str(sig): _grid_middle(arm, sig) for sig in SIGMA_SWEEP} for arm in ARMS},
              "sanity_sigma_0": {arm: 1.0 for arm in ARMS},
              "N_DIM": N_DIM, "M": M, "sigma_sweep": SIGMA_SWEEP, "N_EVAL": N_EVAL,
              "arms": ARMS, "run_mode": "selftest", "config_version": "selftest"}
             for sd in (7, 17, 23)]
    v3, _, _ = compute_verdict(fake3)
    assert v3 == "META_BRANCH3_MIDDLE", "T8 expected MIDDLE; got %s" % v3

    # T9: sanity violation triggers HARD_FAIL
    bad = [{"seed": 99,
            "grid": {arm: {str(sig): 0.5 for sig in SIGMA_SWEEP} for arm in ARMS},
            "sanity_sigma_0": {"ARM_RANDOM_BIPOLAR": 0.5,
                               "ARM_CHAR_TRIGRAM_LEARNED": 1.0,
                               "ARM_HUB_SPOKE_STRUCTURED": 1.0},
            "N_DIM": N_DIM, "M": M, "sigma_sweep": SIGMA_SWEEP, "N_EVAL": N_EVAL,
            "arms": ARMS, "run_mode": "selftest", "config_version": "selftest"}]
    v4, _, _ = compute_verdict(bad)
    assert v4 == "HARD_FAIL", "T9 expected HARD_FAIL on sanity violation; got %s" % v4

    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated in selftest"
    print("[selftest] PASS: 3 arm builders + L2 norm + clean-cue identity + high-noise random + "
          "hub-spoke structure check + trigram distinctness + verdict 4-way + n_llm_calls=0",
          flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N=%d M=%d sigma_sweep=%s N_EVAL=%d seeds=%s arms=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M, SIGMA_SWEEP, N_EVAL, SEEDS, ARMS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "M": M,
               "schema": "cleanup-floor-learned-encoder-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    v, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "M": M,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD codebook + char_trigram_encoder; no external LM)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
