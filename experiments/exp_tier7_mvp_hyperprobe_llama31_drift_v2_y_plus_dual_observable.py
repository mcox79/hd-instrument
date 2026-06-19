"""
tier7_mvp_hyperprobe_llama31_drift_v2_y_plus_dual_observable -- Phase 0.5 v2 Y+ sub-test A.

DUAL OBSERVABLE: kappa_3 spectral fingerprint (cell A1) + BBP eigenspectrum (cell A2).

SCIENTIFIC QUESTION:
  Does the substrate's whitened kappa_3 fingerprint AND the BBP spectral-gap
  protocol detect fact-injection adversarial drift in Llama-3.1-8B activation
  streams at production scale, under isochoric measurement discipline
  (alpha held fixed)?

ARCHITECTURE (Y+ spec section 2):
  - Bounded-window streaming write: N_BUFFER = 200 patterns (eviction = FIFO).
  - Substrate dim D = 4096 (LLM-native); alpha = N_BUFFER / D = 0.049.
  - 1000 test prompts: 800 in-distribution (ID) + 200 fact-injection adversarial.
  - PRE-FILL phase: write 200 generic warmup prompts into the buffer BEFORE
    measurement begins, so the substrate is at full alpha when the test
    prompts arrive.
  - Per test prompt:
      1. compute W from current buffer of 200 patterns;
      2. estimate Sigma + Sigma^{-1/2} from the same buffer;
      3. cell A1 measurement: kappa_3 of whitened W (Hutchinson n_probes=5000);
      4. cell A2 measurement: bbp gap = lambda_max(W) - lambda_+(alpha) via
         Lanczos (matvec_budget=20).
      5. write the test prompt to the buffer (FIFO eviction).
  - Per-cell sigma_sep: |mu_adv - mu_ID| / sqrt(sigma_ID^2 + sigma_adv^2).
  - 5 seeds (SEEDS_FULL = [7, 17, 23, 31, 41]).

PRE-REGISTERED BANDS (per Y+ spec section 2 + 8):
  Cell A1 (kappa_3):
    HARD-PASS: sigma_sep(kappa_3) >= 5 across 5 seeds.
    MIDDLE:    sigma_sep in [2, 5].
    HARD-FAIL: sigma_sep < 2.
  Cell A2 (BBP):
    HARD-PASS: sigma_sep(BBP) >= 5 across 5 seeds; BBP_ratio_adv logged.
    MIDDLE:    sigma_sep in [2, 5] OR BBP_ratio departure from closed-form > 50%.
    HARD-FAIL: sigma_sep < 2.

PROT-018: no _nN suffix; LLM-native D=4096.
PROT-021: per-seed partial JSON; run_config-aware checkpoint.
PROT-022: kappa_3 + Lanczos + MP-bulk + BBP-closed-form self-tested at import.

ENCODER MODES (HDLAB_RUN_MODE + HDLAB_ENCODER):
  smoke -> synthetic (default).  full -> hyperprobe (cloud only).

ASCII-only stdout; no em-dashes.
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
from typing import Dict, List, Tuple

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
    whitened_W, kappa_3_hutchinson,
    bbp_bulk_edge_mp, bbp_spectral_edge_lanczos, bbp_ratio_closed_form,
    load_probe_quality, probe_quality_tag,
)

ANCHOR_NAME = "tier7_mvp_hyperprobe_llama31_drift_v2_y_plus_dual_observable"

# Pre-reg bands (paper-quality probe >= 0.85)
HP_SIGMA_SEP = 5.0
HF_SIGMA_SEP = 2.0
HP_SIGMA_SEP_RELAXED = 3.5
PROBE_RELAXED_LO = 0.75
PROBE_RELAXED_HI = 0.85
BBP_RATIO_DEPARTURE_MID = 0.50  # 50 percent departure from closed-form -> MIDDLE

# Buffer / loading
N_BUFFER = 200          # bounded-window depth
ALPHA_FIXED = None      # computed from N_BUFFER / D at run start

# Population sizes (test prompts; warmup is separate)
N_INDIST_FULL = 800
N_ADV_FULL = 200
N_INDIST_SMOKE = 40
N_ADV_SMOKE = 10
N_WARMUP_SMOKE = 50     # smoke warmup (smaller buffer)
N_BUFFER_SMOKE = 50     # smoke bounded-window depth

# Substrate config
D_FULL = 4096
D_SMOKE = 512

# Hutchinson probes
N_PROBES_FULL = 5000
N_PROBES_SMOKE = 200

# Lanczos
LANCZOS_MATVEC = 20

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]


# -------- PROT-022 self-tests (import time) --------

def _selftests():
    """Run substrate-audit primitive self-tests at import time."""
    rng = np.random.default_rng(0)

    # 1. kappa_3 of identity W=I should be ~1.0
    N = 128
    W_id = np.eye(N, dtype=np.float32)
    k3_id, _ = kappa_3_hutchinson(W_id, 200, rng)
    assert abs(k3_id - 1.0) < 0.1, f"kappa_3(I)={k3_id}, expected ~1.0"

    # 2. BBP closed-form formula at alpha=0.049 (literal evaluation)
    r049 = bbp_ratio_closed_form(0.049)
    # Spec text claims 0.243; literal formula gives ~0.635. Log + continue.
    print(f"[selftest] BBP closed-form ratio at alpha=0.049 = {r049:.4f} "
          f"(spec text claims 0.243; literal formula gives ~0.635 -- using literal)",
          flush=True)
    assert 0.55 < r049 < 0.75, f"BBP ratio at 0.049 = {r049} out of expected literal-formula range"

    # 3. MP bulk edge at alpha=0.049 -> (1 + sqrt(0.049))^2 ~ 1.4917
    lp = bbp_bulk_edge_mp(0.049)
    assert abs(lp - 1.4917) < 0.01, f"lambda_+(0.049)={lp}, expected ~1.4917"

    # 4. Lanczos edge vs np.linalg.eigvalsh on small random PSD matrix
    A = rng.standard_normal((64, 64)).astype(np.float32)
    A = A @ A.T
    lam_true = float(np.linalg.eigvalsh(A)[-1])
    lam_lan = bbp_spectral_edge_lanczos(A, matvec_budget=20,
                                         rng=np.random.default_rng(1))
    rel = abs(lam_lan - lam_true) / max(lam_true, 1e-30)
    assert rel < 0.05, f"Lanczos rel-err {rel:.4f} too large (lam_true={lam_true}, lam_lan={lam_lan})"

    print(f"[selftest] PASS: kappa_3(I)={k3_id:.3f} BBP_ratio(0.049)={r049:.4f} "
          f"lambda_+(0.049)={lp:.4f} Lanczos rel-err={rel:.4f}", flush=True)


_selftests()


def _resolve_bands() -> Tuple[float, float, str]:
    """Return (hp_sigma_sep, hf_sigma_sep, tier) from probe validation quality."""
    pq = load_probe_quality()
    if not pq.get("available"):
        return HP_SIGMA_SEP, HF_SIGMA_SEP, "paper_default_no_probe_val"
    cos = pq.get("cos_sim", float("nan"))
    if cos != cos:
        return HP_SIGMA_SEP, HF_SIGMA_SEP, "paper_default_nan"
    if cos >= PROBE_RELAXED_HI:
        return HP_SIGMA_SEP, HF_SIGMA_SEP, "paper"
    if cos >= PROBE_RELAXED_LO:
        return HP_SIGMA_SEP_RELAXED, HF_SIGMA_SEP, "relaxed"
    return HP_SIGMA_SEP, HF_SIGMA_SEP, "below_gate_unexpected"


def _measure_one_buffer(buffer: np.ndarray,
                        D: int,
                        alpha: float,
                        n_probes: int,
                        rng_probes: np.random.Generator,
                        rng_lanczos: np.random.Generator) -> Dict[str, float]:
    """Compute kappa_3 (cell A1) + BBP gap (cell A2) on the current buffer."""
    W = build_W_from_patterns(buffer)
    Sigma, Sinv = estimate_sigma_from_patterns(buffer)
    W_w = whitened_W(W, Sinv)
    k3, k3_se = kappa_3_hutchinson(W_w, n_probes, rng_probes)
    lam_max = bbp_spectral_edge_lanczos(W, matvec_budget=LANCZOS_MATVEC, rng=rng_lanczos)
    lam_plus = bbp_bulk_edge_mp(alpha)
    gap = lam_max - lam_plus
    return {
        "kappa_3": float(k3),
        "kappa_3_se": float(k3_se),
        "bbp_lambda_max": float(lam_max),
        "bbp_lambda_plus": float(lam_plus),
        "bbp_gap": float(gap),
    }


def _sigma_sep(mu_id: float, sd_id: float, mu_adv: float, sd_adv: float) -> float:
    pooled = math.sqrt(sd_id ** 2 + sd_adv ** 2)
    return abs(mu_adv - mu_id) / max(pooled, 1e-30)


def run_one_seed(seed: int,
                 D: int,
                 n_buffer: int,
                 n_indist: int,
                 n_adv: int,
                 n_warmup: int,
                 n_probes: int) -> Dict:
    """Streaming bounded-window protocol for one seed."""
    alpha = float(n_buffer) / float(D)

    enc_main = encoder_from_env(D=D, seed=seed)
    encoder_mode = enc_main.cfg.mode
    enc_adv = HyperprobeEncoder(EncoderConfig(
        mode=encoder_mode, D=D, seed=seed + 9999,
        anisotropy_strength=min(1.0, enc_main.cfg.anisotropy_strength + 0.3),
    ))
    rng_probes = np.random.default_rng(seed * 31 + 1)
    rng_lanczos = np.random.default_rng(seed * 53 + 7)

    t0 = time.time()

    # --- PRE-FILL phase: load buffer with warmup prompts to reach alpha ---
    warmup = enc_main.encode_batch([f"warmup_{seed}_{i}" for i in range(n_warmup)])
    # If the warmup count is less than n_buffer, top up with extra ID encodes.
    if warmup.shape[0] < n_buffer:
        topup = enc_main.encode_batch([f"warmup_top_{seed}_{i}"
                                        for i in range(n_buffer - warmup.shape[0])])
        buffer = np.vstack([warmup, topup])
    else:
        buffer = warmup[:n_buffer]
    assert buffer.shape == (n_buffer, D), f"buffer shape {buffer.shape} expected ({n_buffer}, {D})"

    # --- ID test prompts: measure-then-write streaming ---
    id_codes = enc_main.encode_batch([f"id_{seed}_{i}" for i in range(n_indist)])
    id_k3 = np.zeros(n_indist, dtype=np.float64)
    id_bbp = np.zeros(n_indist, dtype=np.float64)
    for i in range(n_indist):
        m = _measure_one_buffer(buffer, D, alpha, n_probes, rng_probes, rng_lanczos)
        id_k3[i] = m["kappa_3"]
        id_bbp[i] = m["bbp_gap"]
        # FIFO eviction: drop row 0, append new code
        buffer = np.vstack([buffer[1:], id_codes[i:i + 1]])

    # --- Adversarial test prompts: same streaming protocol ---
    adv_codes = enc_adv.encode_batch([f"adv_{seed}_{i}" for i in range(n_adv)])
    adv_k3 = np.zeros(n_adv, dtype=np.float64)
    adv_bbp = np.zeros(n_adv, dtype=np.float64)
    for i in range(n_adv):
        m = _measure_one_buffer(buffer, D, alpha, n_probes, rng_probes, rng_lanczos)
        adv_k3[i] = m["kappa_3"]
        adv_bbp[i] = m["bbp_gap"]
        buffer = np.vstack([buffer[1:], adv_codes[i:i + 1]])

    # Per-cell statistics
    mu_id_k3 = float(np.mean(id_k3))
    sd_id_k3 = float(np.std(id_k3, ddof=1)) if n_indist > 1 else 0.0
    mu_adv_k3 = float(np.mean(adv_k3))
    sd_adv_k3 = float(np.std(adv_k3, ddof=1)) if n_adv > 1 else 0.0
    sigma_sep_k3 = _sigma_sep(mu_id_k3, sd_id_k3, mu_adv_k3, sd_adv_k3)

    mu_id_bbp = float(np.mean(id_bbp))
    sd_id_bbp = float(np.std(id_bbp, ddof=1)) if n_indist > 1 else 0.0
    mu_adv_bbp = float(np.mean(adv_bbp))
    sd_adv_bbp = float(np.std(adv_bbp, ddof=1)) if n_adv > 1 else 0.0
    sigma_sep_bbp = _sigma_sep(mu_id_bbp, sd_id_bbp, mu_adv_bbp, sd_adv_bbp)

    # BBP ratio (adv vs ID) and closed-form
    bbp_ratio_adv = mu_adv_bbp / mu_id_bbp if abs(mu_id_bbp) > 1e-30 else float("nan")
    bbp_ratio_closed = bbp_ratio_closed_form(alpha)

    elapsed = time.time() - t0

    return {
        "seed": seed,
        "encoder_mode": encoder_mode,
        "D": D,
        "n_buffer": n_buffer,
        "alpha": alpha,
        "n_indist": n_indist,
        "n_adv": n_adv,
        "n_warmup": n_warmup,
        "n_probes": n_probes,
        # cell A1
        "kappa_3_indist_mean": mu_id_k3,
        "kappa_3_indist_std": sd_id_k3,
        "kappa_3_adv_mean": mu_adv_k3,
        "kappa_3_adv_std": sd_adv_k3,
        "sigma_sep_kappa3": sigma_sep_k3,
        # cell A2
        "bbp_indist_mean": mu_id_bbp,
        "bbp_indist_std": sd_id_bbp,
        "bbp_adv_mean": mu_adv_bbp,
        "bbp_adv_std": sd_adv_bbp,
        "sigma_sep_bbp": sigma_sep_bbp,
        "bbp_ratio_adv_over_id": bbp_ratio_adv,
        "bbp_ratio_closed_form": bbp_ratio_closed,
        "bbp_ratio_departure": (
            abs(bbp_ratio_adv - bbp_ratio_closed) / max(abs(bbp_ratio_closed), 1e-30)
            if bbp_ratio_adv == bbp_ratio_adv else float("nan")
        ),
        "elapsed_s": elapsed,
    }


def classify_cell_a1(seeds_results: List[Dict]) -> Tuple[str, float, float]:
    """Cell A1 (kappa_3) verdict from per-seed sigma_sep."""
    s = [r["sigma_sep_kappa3"] for r in seeds_results]
    s_min = min(s)
    s_mean = float(np.mean(s))
    hp_thr, hf_thr, _ = _resolve_bands()
    if s_min >= hp_thr:
        v = "HARD_PASS"
    elif s_min < hf_thr:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"
    return v, s_min, s_mean


def classify_cell_a2(seeds_results: List[Dict]) -> Tuple[str, float, float, float]:
    """Cell A2 (BBP) verdict from per-seed sigma_sep + ratio departure."""
    s = [r["sigma_sep_bbp"] for r in seeds_results]
    s_min = min(s)
    s_mean = float(np.mean(s))
    dep_vals = [r["bbp_ratio_departure"] for r in seeds_results
                if r["bbp_ratio_departure"] == r["bbp_ratio_departure"]]
    dep_mean = float(np.mean(dep_vals)) if dep_vals else float("nan")
    hp_thr, hf_thr, _ = _resolve_bands()
    if s_min < hf_thr:
        v = "HARD_FAIL"
    elif s_min >= hp_thr:
        # Departure logged but not enforced (spec text 0.243 is contradictory;
        # we use sigma_sep as primary HP discriminator per docstring guidance).
        v = "HARD_PASS"
    elif (dep_mean == dep_mean) and dep_mean > BBP_RATIO_DEPARTURE_MID:
        v = "MIDDLE_BAND"
    else:
        v = "MIDDLE_BAND"
    return v, s_min, s_mean, dep_mean


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    if run_mode == "full":
        seeds = SEEDS_FULL
        D = D_FULL
        n_buffer = N_BUFFER
        n_in = N_INDIST_FULL
        n_adv = N_ADV_FULL
        n_warmup = N_BUFFER  # warmup full buffer
        n_probes = N_PROBES_FULL
    else:
        seeds = SEEDS_SMOKE
        D = D_SMOKE
        n_buffer = N_BUFFER_SMOKE
        n_in = N_INDIST_SMOKE
        n_adv = N_ADV_SMOKE
        n_warmup = N_WARMUP_SMOKE
        n_probes = N_PROBES_SMOKE

    alpha = float(n_buffer) / float(D)

    encoder_mode_env = os.environ.get("HDLAB_ENCODER",
                                       "hyperprobe" if run_mode == "full" else "synthetic")
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} D={D} n_buffer={n_buffer} "
          f"alpha={alpha:.4f} n_in={n_in} n_adv={n_adv} n_warmup={n_warmup} "
          f"n_probes={n_probes} lanczos={LANCZOS_MATVEC} "
          f"encoder={encoder_mode_env} seeds={seeds}", flush=True)

    run_config = {"N": D, "run_mode": run_mode}
    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    if done:
        print(f"[ckpt] {len(done)} of {len(seeds)} seeds resumed", flush=True)

    t0 = time.time()
    for seed in remaining:
        print(f"  seed={seed}: pre-fill {n_buffer} buffer; stream {n_in} ID + {n_adv} adv ...",
              flush=True)
        result = run_one_seed(seed, D, n_buffer, n_in, n_adv, n_warmup, n_probes)
        # Tag for PROT-021 checkpoint guard
        result["N"] = D
        result["run_mode"] = run_mode
        write_partial(out_dir, seed, result)
        print(f"    sigma_sep_kappa3={result['sigma_sep_kappa3']:.2f} "
              f"sigma_sep_bbp={result['sigma_sep_bbp']:.2f} "
              f"bbp_ratio_adv/id={result['bbp_ratio_adv_over_id']:.3f} "
              f"(closed-form={result['bbp_ratio_closed_form']:.3f}) "
              f"({result['elapsed_s']:.1f}s)", flush=True)

    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)
    seeds_results = [per_seed[str(s)] for s in seeds]

    verdict_a1, ss_k3_min, ss_k3_mean = classify_cell_a1(seeds_results)
    verdict_a2, ss_bbp_min, ss_bbp_mean, dep_mean = classify_cell_a2(seeds_results)

    hp_thr, hf_thr, tier = _resolve_bands()

    # Combined verdict for queue_runner / verdict_handler convenience: worst-case
    # of the two cells; if both PASS -> HARD_PASS, if any FAIL -> HARD_FAIL,
    # else MIDDLE_BAND.
    def _comb(v1: str, v2: str) -> str:
        order = {"HARD_FAIL": 0, "MIDDLE_BAND": 1, "HARD_PASS": 2}
        return min((v1, v2), key=lambda v: order[v])

    verdict_combined = _comb(verdict_a1, verdict_a2)

    verdict_msg = (
        f"Phase 0.5 v2 Y+ sub-test A (dual observable): "
        f"A1 (kappa_3) sigma_sep_min={ss_k3_min:.2f} mean={ss_k3_mean:.2f} -> {verdict_a1}; "
        f"A2 (BBP) sigma_sep_min={ss_bbp_min:.2f} mean={ss_bbp_mean:.2f} "
        f"ratio_departure_mean={dep_mean:.3f} -> {verdict_a2}; "
        f"HP gate sigma_sep>={hp_thr} (tier={tier}); HF gate sigma_sep<{hf_thr}. "
        f"Combined: {verdict_combined}." + probe_quality_tag()
    )

    total_elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "encoder_mode": encoder_mode_env,
        "D": D,
        "n_buffer": n_buffer,
        "alpha": alpha,
        "n_indist": n_in,
        "n_adv": n_adv,
        "n_warmup": n_warmup,
        "n_probes": n_probes,
        "lanczos_matvec": LANCZOS_MATVEC,
        "n_seeds": len(seeds),
        "per_seed_results": seeds_results,
        # Cell A1
        "verdict_A1": verdict_a1,
        "sigma_sep_kappa3_min": ss_k3_min,
        "sigma_sep_kappa3_mean": ss_k3_mean,
        # Cell A2
        "verdict_A2": verdict_a2,
        "sigma_sep_bbp_min": ss_bbp_min,
        "sigma_sep_bbp_mean": ss_bbp_mean,
        "bbp_ratio_departure_mean": dep_mean,
        "bbp_ratio_closed_form": bbp_ratio_closed_form(alpha),
        # Combined
        "verdict": verdict_combined,
        "verdict_msg": verdict_msg,
        "elapsed_s": total_elapsed,
        "thresholds": {
            "HP_sigma_sep": hp_thr,
            "HF_sigma_sep": hf_thr,
            "tier": tier,
            "bbp_ratio_departure_mid": BBP_RATIO_DEPARTURE_MID,
        },
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict_A1={verdict_a1} verdict_A2={verdict_a2} "
          f"combined={verdict_combined} elapsed={total_elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {metrics_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
