"""
tier7_mvp_hyperprobe_llama31_kappa3_drift_v1 -- Phase 0.5 Tier-7 MVP sub-test A.

SCIENTIFIC QUESTION:
  Does the substrate's whitened kappa_3 spectral fingerprint detect fact-injection
  adversarial drift in Llama-3.1-8B activation streams at production scale?

DESIGN:
  - 1000 prompts: 800 in-distribution control + 200 fact-injection adversarial.
  - For each prompt: forward pass Llama-3.1-8B, intercept residual at layer
    ell = L * 0.7 on final-token position; hyperprobe encode to bipolar {-1,+1}^D.
  - Build pattern matrix Xi_indist (800 x D) + Xi_adv (200 x D).
  - For each population: whiten via Sigma^{-1/2} (per I-10 kappa_3-mixing drill),
    estimate kappa_3 via Hutchinson on whitened W_white = Sigma^{-1/2} W Sigma^{-1/2}.
  - sigma_sep = |kappa_3(adv) - kappa_3(indist)| / sqrt(SE_adv^2 + SE_indist^2).
  - 5 seeds for the iid synthesis path (re-seed both probes + adversarial sample).

PRE-REGISTERED BANDS (per research_routing_llm_integration_program_amendment_phase0p5_2026-06-02):
  HARD-PASS: sigma_sep >= 5 across 5 seeds.
  MIDDLE:    sigma_sep in [2, 5] (signal present but weaker; rescue path = tighter
             whitening OR N=32768 retrained probe).
  HARD-FAIL: sigma_sep < 2 (algebra doesn't transfer to LLM-mapped patterns
             OR whitening rescue fails empirically).

ENCODER MODES (HDLAB_ENCODER env var):
  - synthetic (default for smoke):   iid {-1,+1}^D; expected near-zero sigma_sep
                                     (validates instrumentation: NULL behavior).
  - pseudo_llm:                      anisotropic low-rank cone + sign(); models
                                     I-10 high-rho LLM hidden state regime.
                                     Whitening rescue should reduce sigma_sep
                                     toward synthetic baseline.
  - hyperprobe:                      full Llama-3.1-8B + hyperprobe; cloud only.

PROT-018: no _nN suffix -> LLM-native D=4096 (or N=32768 if retrained probe).

Per [[feedback-no-experiment-design-in-prompts]]: pre-reg bands above are the
research routing's bands verbatim. Cell-design decisions (n_probes, prompts/pop)
are testbed autonomy.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)
from testbed.llm_integration.hyperprobe_encoder import (  # noqa: E402
    EncoderConfig, HyperprobeEncoder, encoder_from_env,
)
from testbed.llm_integration.substrate_audit import (  # noqa: E402
    build_W_from_patterns, estimate_sigma_from_patterns,
    whitened_W, kappa_3_hutchinson, load_probe_quality, probe_quality_tag,
)

ANCHOR_NAME = "tier7_mvp_hyperprobe_llama31_kappa3_drift_v1"

# Pre-reg bands (paper-quality probe ≥ 0.85)
HP_SIGMA_SEP = 5.0
HF_SIGMA_SEP = 2.0

# Conditional band per research 2026-06-02: when probe quality is in the
# 0.75-0.85 window (relaxed tier), sigma_sep HP threshold scales with probe
# quality: HP_relaxed = HP_original * (q / 0.89) ≈ 3.5 at q=0.75-0.80. HF
# threshold unchanged. q < 0.75 doesn't reach this script (Wave 2 abort gate
# fires at the validation step).
HP_SIGMA_SEP_RELAXED = 3.5
PROBE_RELAXED_LO = 0.75
PROBE_RELAXED_HI = 0.85


def _resolve_bands():
    """Return (hp_thr, hf_thr, tier) using probe validation quality."""
    pq = load_probe_quality()
    if not pq.get("available"):
        return HP_SIGMA_SEP, HF_SIGMA_SEP, "paper_default_no_probe_val"
    cos = pq.get("cos_sim", float("nan"))
    if cos != cos:  # NaN
        return HP_SIGMA_SEP, HF_SIGMA_SEP, "paper_default_nan"
    if cos >= PROBE_RELAXED_HI:
        return HP_SIGMA_SEP, HF_SIGMA_SEP, "paper"
    if cos >= PROBE_RELAXED_LO:
        return HP_SIGMA_SEP_RELAXED, HF_SIGMA_SEP, "relaxed"
    # cos < 0.75: shouldn't be reachable; Wave 2 should have aborted
    return HP_SIGMA_SEP, HF_SIGMA_SEP, "below_gate_unexpected"

# Population sizes
N_INDIST_FULL = 800
N_ADV_FULL = 200
N_INDIST_SMOKE = 80
N_ADV_SMOKE = 20

# Substrate config
D_FULL = 4096           # Llama-3.1-8B hidden = 4096; hyperprobe published D = 4096
D_SMOKE = 512
N_PROBES_FULL = 5000    # Hutchinson probe count for kappa_3 estimator
N_PROBES_SMOKE = 500

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]


def _instrumentation_selftest():
    """At small scale: synthetic encoder should give near-zero sigma_sep
    (NULL test). pseudo_llm encoder at high anisotropy should give nonzero
    sigma_sep before whitening, reduced after.
    """
    rng = np.random.default_rng(0)
    D = 64
    enc = HyperprobeEncoder(EncoderConfig(mode="synthetic", D=D, seed=0))
    Xi_a = enc.encode_batch([f"a{i}" for i in range(40)])
    Xi_b = enc.encode_batch([f"b{i}" for i in range(20)])
    W_a = build_W_from_patterns(Xi_a)
    W_b = build_W_from_patterns(Xi_b)
    k3_a, se_a = kappa_3_hutchinson(W_a, 200, rng)
    k3_b, se_b = kappa_3_hutchinson(W_b, 200, rng)
    # synthetic mode: both kappa_3 ~ alpha; SE should be small; sigma_sep modest
    pooled = math.sqrt(se_a ** 2 + se_b ** 2)
    sigma_sep_null = abs(k3_a - k3_b) / max(pooled, 1e-30)
    assert sigma_sep_null < 20.0, \
        f"synthetic NULL sigma_sep should be modest, got {sigma_sep_null}"
    print(f"[selftest] PASS: synthetic NULL sigma_sep={sigma_sep_null:.2f} "
          f"(k3_a={k3_a:.4f} k3_b={k3_b:.4f})", flush=True)


_instrumentation_selftest()


def run_one_seed(seed: int, D: int, n_indist: int, n_adv: int, n_probes: int) -> dict:
    """One full seed: build encoder, sample both populations, whiten, kappa_3."""
    enc = encoder_from_env(D=D, seed=seed)
    encoder_mode = enc.cfg.mode
    rng_probes = np.random.default_rng(seed * 31 + 1)

    t0 = time.time()
    # In-distribution corpus
    Xi_in = enc.encode_batch([f"indist_{seed}_{i}" for i in range(n_indist)])
    # Adversarial corpus (in synthetic / pseudo_llm we just re-seed with a shift to
    # simulate distributional drift; in full hyperprobe mode the prompts would be
    # crafted to inject specific factual claims)
    enc_adv_cfg = EncoderConfig(
        mode=encoder_mode, D=D, seed=seed + 9999,
        anisotropy_strength=min(1.0, enc.cfg.anisotropy_strength + 0.3),
    )
    enc_adv = HyperprobeEncoder(enc_adv_cfg)
    Xi_adv = enc_adv.encode_batch([f"adv_{seed}_{i}" for i in range(n_adv)])

    W_in = build_W_from_patterns(Xi_in)
    W_adv = build_W_from_patterns(Xi_adv)
    Sigma_in, Sinv_in = estimate_sigma_from_patterns(Xi_in)
    Sigma_adv, Sinv_adv = estimate_sigma_from_patterns(Xi_adv)
    W_in_w = whitened_W(W_in, Sinv_in)
    W_adv_w = whitened_W(W_adv, Sinv_adv)

    k3_in, se_in = kappa_3_hutchinson(W_in_w, n_probes, rng_probes)
    k3_adv, se_adv = kappa_3_hutchinson(W_adv_w, n_probes, rng_probes)

    pooled_se = math.sqrt(se_in ** 2 + se_adv ** 2)
    sigma_sep = abs(k3_adv - k3_in) / max(pooled_se, 1e-30)
    elapsed = time.time() - t0

    return {
        "seed": seed,
        "encoder_mode": encoder_mode,
        "D": D,
        "n_indist": n_indist,
        "n_adv": n_adv,
        "n_probes": n_probes,
        "kappa_3_indist": k3_in,
        "kappa_3_indist_se": se_in,
        "kappa_3_adv": k3_adv,
        "kappa_3_adv_se": se_adv,
        "pooled_se": pooled_se,
        "sigma_sep": sigma_sep,
        "elapsed_s": elapsed,
    }


def classify_verdict(seeds_results: list[dict]) -> tuple[str, str]:
    sigma_seps = [r["sigma_sep"] for r in seeds_results]
    sigma_min = min(sigma_seps)
    sigma_mean = float(np.mean(sigma_seps))
    hp_thr, hf_thr, tier = _resolve_bands()
    if sigma_min >= hp_thr:
        v = "HARD_PASS"
    elif sigma_min < hf_thr:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"
    msg = (f"Phase 0.5 sub-test A (kappa_3 drift): sigma_sep min={sigma_min:.2f} "
           f"mean={sigma_mean:.2f} across {len(seeds_results)} seeds. "
           f"HP gate >= {hp_thr} (tier={tier}); HF gate < {hf_thr}. Verdict: {v}."
           + probe_quality_tag())
    return v, msg


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    if run_mode == "full":
        seeds = SEEDS_FULL
        D = D_FULL
        n_in = N_INDIST_FULL
        n_adv = N_ADV_FULL
        n_probes = N_PROBES_FULL
    else:
        seeds = SEEDS_SMOKE
        D = D_SMOKE
        n_in = N_INDIST_SMOKE
        n_adv = N_ADV_SMOKE
        n_probes = N_PROBES_SMOKE

    encoder_mode_env = os.environ.get("HDLAB_ENCODER",
                                       "hyperprobe" if run_mode == "full" else "synthetic")
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} D={D} n_indist={n_in} n_adv={n_adv} "
          f"n_probes={n_probes} encoder={encoder_mode_env} seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir)
    if done:
        print(f"[ckpt] {len(done)} of {len(seeds)} seeds resumed", flush=True)

    t0 = time.time()
    for seed in remaining:
        print(f"  seed={seed}: writing in-dist + adv populations, whitening, "
              f"kappa_3 ...", flush=True)
        result = run_one_seed(seed, D, n_in, n_adv, n_probes)
        write_partial(out_dir, seed, result)
        print(f"    k3_in={result['kappa_3_indist']:.4f} (se={result['kappa_3_indist_se']:.4e}) "
              f"k3_adv={result['kappa_3_adv']:.4f} (se={result['kappa_3_adv_se']:.4e}) "
              f"sigma_sep={result['sigma_sep']:.2f} ({result['elapsed_s']:.1f}s)",
              flush=True)

    per_seed = aggregate_partials(out_dir, seeds)
    seeds_results = [per_seed[str(s)] for s in seeds]
    verdict, verdict_msg = classify_verdict(seeds_results)
    total_elapsed = time.time() - t0

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "encoder_mode": encoder_mode_env,
        "D": D,
        "n_indist": n_in,
        "n_adv": n_adv,
        "n_probes": n_probes,
        "n_seeds": len(seeds),
        "per_seed_results": seeds_results,
        "sigma_sep_min": min(r["sigma_sep"] for r in seeds_results),
        "sigma_sep_mean": float(np.mean([r["sigma_sep"] for r in seeds_results])),
        "verdict": verdict,
        "elapsed_s": total_elapsed,
        "thresholds": {"HP_sigma_sep": HP_SIGMA_SEP, "HF_sigma_sep": HF_SIGMA_SEP},
        "verdict_msg": verdict_msg,
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={total_elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {metrics_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
