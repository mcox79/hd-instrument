"""
tier7_mvp_hyperprobe_llama31_deletion_cert_v1 -- Phase 0.5 Tier-7 MVP sub-test B.

SCIENTIFIC QUESTION:
  Can the substrate produce verifiable per-fact deletion certificates against
  Llama-3.1-8B's live internal state, such that deleted facts go below noise
  floor while retained facts remain retrievable above threshold?

DESIGN:
  - Store M_facts=100 facts as Llama-3.1-8B residual at fact-mention token,
    hyperprobe-encoded to bipolar {-1,+1}^D.
  - Issue deletion cert for K_del=25 randomly-selected facts via rank-1
    subtraction W' = W - (1/N) xi_f xi_f^T.
  - Verify (per seed):
    (a) Deleted-fact residual norm ||W' @ xi_f|| relative to null distribution
        (random eta) Z-score < 2 (deleted goes below noise floor).
    (b) Retained-fact retrieval cosine cos(W' @ xi_g, xi_g) > 0.85 across
        all g in retained set.

PRE-REGISTERED BANDS (per research_routing_llm_integration_program_amendment_phase0p5):
  HARD-PASS:  deleted-fact-Z < 2 AND retained-cosine_min > 0.85 across 5 seeds.
  MIDDLE:     deleted-Z in [2, 5] OR retained-cosine_min in [0.65, 0.85].
  HARD-FAIL:  deleted-Z > 5 (substrate cannot algebraically erase from LLM-mapped
              patterns) OR retained-cosine_min < 0.65.

PROT-018: no _nN suffix -> LLM-native D=4096 (or N=32768 if retrained probe).
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
from testbed.llm_integration.hyperprobe_encoder import encoder_from_env  # noqa: E402
from testbed.llm_integration.substrate_audit import (  # noqa: E402
    build_W_from_patterns, deletion_cert, retrieval_cosine,
    null_distribution_norm, probe_quality_tag,
)

ANCHOR_NAME = "tier7_mvp_hyperprobe_llama31_deletion_cert_v1"

# Pre-reg bands
HP_DEL_Z = 2.0
MID_DEL_Z_HI = 5.0
HF_DEL_Z = 5.0
HP_RETAIN_COSINE = 0.85
MID_RETAIN_COSINE = 0.65
HF_RETAIN_COSINE = 0.65

# Sizes
M_FACTS_FULL = 100
M_FACTS_SMOKE = 40
K_DEL_FRAC = 0.25       # fraction of facts to delete (25 of 100 full)
N_NULL_PROBES = 50
D_FULL = 4096
D_SMOKE = 512

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]


def _instrumentation_selftest():
    """Synthetic at small D: deletion of stored fact drops cosine; retained
    facts keep cosine; cert closed-form holds.
    """
    rng = np.random.default_rng(0)
    D = 64
    M = 30
    Xi = rng.choice([-1.0, 1.0], size=(M, D)).astype(np.float32)
    W = build_W_from_patterns(Xi)
    # Cosine before deletion: should be high for stored
    cos_pre = retrieval_cosine(W, Xi[5])
    # Delete fact 5
    W_post, cert, sig_norm = deletion_cert(W, Xi[5])
    cos_post = retrieval_cosine(W_post, Xi[5])
    # Retained fact 7
    cos_retain = retrieval_cosine(W_post, Xi[7])
    assert cos_pre > cos_post, f"deletion didn't drop cosine: pre={cos_pre} post={cos_post}"
    assert cos_retain > 0.5, f"retained fact dropped too much: {cos_retain}"
    print(f"[selftest] PASS: cosine_pre={cos_pre:.3f} cosine_post={cos_post:.3f} "
          f"retained={cos_retain:.3f}", flush=True)


_instrumentation_selftest()


def run_one_seed(seed: int, D: int, M_facts: int, k_del: int, n_null: int) -> dict:
    enc = encoder_from_env(D=D, seed=seed)
    encoder_mode = enc.cfg.mode

    t0 = time.time()
    Xi = enc.encode_batch([f"fact_{seed}_{i}" for i in range(M_facts)])
    W = build_W_from_patterns(Xi)

    # Pre-deletion retrieval cosines (sanity baseline)
    cos_pre = [retrieval_cosine(W, Xi[i]) for i in range(M_facts)]

    # Random subset of K_del to delete
    rng_sel = np.random.default_rng(seed * 17 + 5)
    del_idx = rng_sel.choice(M_facts, size=k_del, replace=False).tolist()
    retain_idx = [i for i in range(M_facts) if i not in set(del_idx)]

    # Sequential deletion (rank-1 each)
    W_post = W.copy()
    cert_scalars = []
    for idx in del_idx:
        W_post, cert, _ = deletion_cert(W_post, Xi[idx])
        cert_scalars.append(cert)

    # Null distribution of ||W_post @ eta|| for random eta
    rng_null = np.random.default_rng(seed * 23 + 11)
    null_mean, null_std = null_distribution_norm(W_post, n_null, rng_null)

    # Deleted-fact residual norms and Z-scores
    del_norms = []
    del_zs = []
    for idx in del_idx:
        nrm = float(np.linalg.norm(W_post @ Xi[idx]))
        z = abs(nrm - null_mean) / max(null_std, 1e-30)
        del_norms.append(nrm)
        del_zs.append(z)

    # Retained-fact cosines
    retain_cos = [retrieval_cosine(W_post, Xi[i]) for i in retain_idx]

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "encoder_mode": encoder_mode,
        "D": D,
        "M_facts": M_facts,
        "k_del": k_del,
        "n_null_probes": n_null,
        "null_mean": null_mean,
        "null_std": null_std,
        "cert_scalar_mean": float(np.mean(cert_scalars)),
        "deleted_residual_norm_mean": float(np.mean(del_norms)),
        "deleted_residual_norm_max": float(np.max(del_norms)),
        "deleted_Z_mean": float(np.mean(del_zs)),
        "deleted_Z_max": float(np.max(del_zs)),
        "retained_cosine_mean": float(np.mean(retain_cos)),
        "retained_cosine_min": float(np.min(retain_cos)),
        "retained_cosine_count": len(retain_cos),
        "pre_deletion_cosine_mean": float(np.mean(cos_pre)),
        "elapsed_s": elapsed,
    }


def classify_verdict(seeds_results: list[dict]) -> tuple[str, str]:
    del_z_max = max(r["deleted_Z_max"] for r in seeds_results)
    retain_min = min(r["retained_cosine_min"] for r in seeds_results)
    if del_z_max < HP_DEL_Z and retain_min > HP_RETAIN_COSINE:
        v = "HARD_PASS"
    elif del_z_max > HF_DEL_Z or retain_min < HF_RETAIN_COSINE:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"
    msg = (f"Phase 0.5 sub-test B (deletion cert): deleted-Z_max={del_z_max:.2f} "
           f"(HP < {HP_DEL_Z}; HF > {HF_DEL_Z}); retained-cosine_min={retain_min:.3f} "
           f"(HP > {HP_RETAIN_COSINE}; HF < {HF_RETAIN_COSINE}). Verdict: {v}."
           + probe_quality_tag())
    return v, msg


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    if run_mode == "full":
        seeds = SEEDS_FULL
        D = D_FULL
        M = M_FACTS_FULL
    else:
        seeds = SEEDS_SMOKE
        D = D_SMOKE
        M = M_FACTS_SMOKE
    k_del = max(1, int(K_DEL_FRAC * M))
    encoder_mode_env = os.environ.get("HDLAB_ENCODER",
                                       "hyperprobe" if run_mode == "full" else "synthetic")
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} D={D} M_facts={M} k_del={k_del} "
          f"n_null_probes={N_NULL_PROBES} encoder={encoder_mode_env} seeds={seeds}",
          flush=True)

    done, remaining = resumable_seeds(seeds, out_dir)
    t0 = time.time()
    for seed in remaining:
        print(f"  seed={seed}: storing M={M} facts, deleting k={k_del}, "
              f"null+retained eval ...", flush=True)
        result = run_one_seed(seed, D, M, k_del, N_NULL_PROBES)
        write_partial(out_dir, seed, result)
        print(f"    del_Z_max={result['deleted_Z_max']:.2f} "
              f"retained_cos_min={result['retained_cosine_min']:.3f} "
              f"({result['elapsed_s']:.1f}s)", flush=True)

    per_seed = aggregate_partials(out_dir, seeds)
    seeds_results = [per_seed[str(s)] for s in seeds]
    verdict, verdict_msg = classify_verdict(seeds_results)
    total_elapsed = time.time() - t0

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "encoder_mode": encoder_mode_env,
        "D": D,
        "M_facts": M,
        "k_del": k_del,
        "n_null_probes": N_NULL_PROBES,
        "n_seeds": len(seeds),
        "per_seed_results": seeds_results,
        "deleted_Z_max_across_seeds": max(r["deleted_Z_max"] for r in seeds_results),
        "retained_cosine_min_across_seeds": min(r["retained_cosine_min"] for r in seeds_results),
        "verdict": verdict,
        "elapsed_s": total_elapsed,
        "thresholds": {
            "HP_deleted_Z_max": HP_DEL_Z,
            "HF_deleted_Z_max": HF_DEL_Z,
            "HP_retained_cosine_min": HP_RETAIN_COSINE,
            "HF_retained_cosine_min": HF_RETAIN_COSINE,
        },
        "verdict_msg": verdict_msg,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={total_elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {out_dir / 'metrics.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
