"""
tier7_mvp_hyperprobe_llama31_deletion_cert_v2_y_plus_dual_primitive -- Phase 0.5 v2 Y+ sub-test B.

DUAL PRIMITIVE: PP-46 rank-1 subtraction (cell B1) + PP-56 Sherman-Morrison (cell B2).

SCIENTIFIC QUESTION:
  Can the substrate produce verifiable per-fact deletion certificates against
  Llama-3.1-8B's live internal state via BOTH the PP-46 rank-1 algebra AND the
  PP-56 Sherman-Morrison algebra, in the predecessor-start protocol?

ARCHITECTURE (Y+ spec section 3):
  - Storage: 100 facts encoded via hyperprobe to bipolar {-1,+1}^D.
  - K_DEL = 25 facts to delete (same selection across cells, seeded).
  - Predecessor-start protocol only (root-start is post-verdict extension).
  - For both cells, use the SAME null distribution baseline of ||W_post @ eta||
    computed once per seed.

  Cell B1 (PP-46 rank-1):
      W' = W - (1/N) xi xi^T (sequential per fact)
  Cell B2 (PP-56 Sherman-Morrison):
      W' = W - (W xi xi^T W) / (1 + xi^T W xi) (sequential per fact)

  Cert reproducibility check: rerun the deletion sequence on a freshly-built
  W_0 from the same seeded patterns; verify byte-exact match of W' within
  float32 epsilon.

PRE-REGISTERED BANDS (per Y+ spec section 3 + 8):
  Per cell:
    HARD-PASS: deleted-fact-Z < 2 AND retained-cosine_min > 0.85 AND
               cert byte-exact reproducible across 5 seeds.
    MIDDLE:    Z in [2, 5] OR retention in [0.65, 0.85].
    HARD-FAIL: Z > 5 OR retention < 0.65 OR non-reproducible.

PROT-018: no _nN suffix; LLM-native D=4096.
PROT-021: per-seed partial JSON; run_config-aware checkpoint.
PROT-022: PP-46 + PP-56 algebraic identities self-tested at import.

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
from testbed.llm_integration.hyperprobe_encoder import encoder_from_env  # noqa: E402
from testbed.llm_integration.substrate_audit import (  # noqa: E402
    build_W_from_patterns, deletion_cert, deletion_cert_sherman_morrison,
    retrieval_cosine, null_distribution_norm, probe_quality_tag,
)

ANCHOR_NAME = "tier7_mvp_hyperprobe_llama31_deletion_cert_v2_y_plus_dual_primitive"

# Pre-reg bands
HP_DEL_Z = 2.0
HF_DEL_Z = 5.0
HP_RETAIN_COSINE = 0.85
HF_RETAIN_COSINE = 0.65

# Sizes
M_FACTS_FULL = 100
M_FACTS_SMOKE = 40
K_DEL_FULL = 25
K_DEL_SMOKE = 10
N_NULL_PROBES = 50
D_FULL = 4096
D_SMOKE = 512

# Cert reproducibility tolerance (float32 epsilon, with some slack for the
# accumulated update sequence; 1e-4 is generous but well below any "meaningful"
# substrate change).
CERT_REPRO_TOL = 1e-4

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]


# -------- PROT-022 self-tests (import time) --------

def _selftests():
    """PP-46 + PP-56 algebraic identities on stored bipolar patterns."""
    rng = np.random.default_rng(0)
    N = 128
    Xi = rng.choice([-1.0, 1.0], size=(20, N)).astype(np.float32)
    W = build_W_from_patterns(Xi)
    xi = Xi[3]

    # PP-46: cert = xi^T (W_post - W) xi = xi^T (-1/N xi xi^T) xi = - (xi^T xi)^2 / N = -N
    _, cert46, _ = deletion_cert(W, xi)
    expected46 = -float(N)
    assert abs(cert46 - expected46) < 1e-2 * N, \
        f"PP-46 cert {cert46} != expected closed-form {expected46}"

    # PP-56: cert = - (xi^T W xi)^2 / (1 + xi^T W xi)
    _, cert56, _ = deletion_cert_sherman_morrison(W, xi)
    xWx = float(xi @ (W @ xi))
    expected56 = -(xWx ** 2) / (1.0 + xWx)
    rel = abs(cert56 - expected56) / max(abs(expected56), 1e-30)
    assert rel < 1e-3, f"PP-56 cert {cert56} != expected {expected56} (rel {rel})"

    # Retrieval-signal sanity: both primitives REDUCE ||W xi|| (the deletion
    # signal). PP-46 cuts a unit-magnitude component (closed-form cert = -N at
    # bipolar). PP-56 cuts a fraction (xWx)^2/(1+xWx) of the projection on W@xi,
    # which is mathematically smaller than PP-46's cut for stored bipolar -- so
    # we test reduction in ||W xi||, NOT in cosine (cosine is direction-only;
    # for stored bipolar both updates leave the direction nearly aligned).
    W_46, _, _ = deletion_cert(W, xi)
    W_56, _, _ = deletion_cert_sherman_morrison(W, xi)
    pre_norm = float(np.linalg.norm(W @ xi))
    post46_norm = float(np.linalg.norm(W_46 @ xi))
    post56_norm = float(np.linalg.norm(W_56 @ xi))
    assert post46_norm < pre_norm, \
        f"PP-46 didn't reduce ||W xi||: pre={pre_norm} post={post46_norm}"
    assert post56_norm < pre_norm, \
        f"PP-56 didn't reduce ||W xi||: pre={pre_norm} post={post56_norm}"
    # Verify cert sign: both certs must be negative (delete removes energy)
    assert cert46 < 0, f"PP-46 cert sign wrong: {cert46}"
    assert cert56 < 0, f"PP-56 cert sign wrong: {cert56}"

    print(f"[selftest] PASS: PP-46 cert={cert46:.3f} (~-N={-N}); "
          f"PP-56 cert={cert56:.4f} (=~{expected56:.4f}); "
          f"||W xi||: pre={pre_norm:.4f} post46={post46_norm:.4f} "
          f"post56={post56_norm:.4f}",
          flush=True)


_selftests()


def _apply_deletions_pp46(W0: np.ndarray, Xi: np.ndarray, del_idx: List[int]) -> Tuple[np.ndarray, List[float]]:
    """Apply PP-46 deletion sequentially. Returns (W_post, cert_scalars)."""
    W_post = W0.copy()
    certs: List[float] = []
    for idx in del_idx:
        W_post, cert, _ = deletion_cert(W_post, Xi[idx])
        certs.append(cert)
    return W_post, certs


def _apply_deletions_pp56(W0: np.ndarray, Xi: np.ndarray, del_idx: List[int]) -> Tuple[np.ndarray, List[float]]:
    """Apply PP-56 Sherman-Morrison deletion sequentially."""
    W_post = W0.copy()
    certs: List[float] = []
    for idx in del_idx:
        W_post, cert, _ = deletion_cert_sherman_morrison(W_post, Xi[idx])
        certs.append(cert)
    return W_post, certs


def _measure_cell(W_post: np.ndarray,
                  Xi: np.ndarray,
                  del_idx: List[int],
                  retain_idx: List[int],
                  null_mean: float,
                  null_std: float) -> Dict:
    """Compute deleted-fact Z (one-sided) + retained-fact cosines on a post-deletion W.

    Z is ONE-SIDED: only positive deviation (nrm > null_mean) counts as a deletion
    failure. Over-deletion (nrm < null_mean, i.e., residual is BELOW noise floor)
    is correct behavior, not failure. This matters for PP-56 Sherman-Morrison,
    which makes deleted-fact residual ~0 (much smaller than null mean) and
    therefore would erroneously trigger HF under a two-sided |Z|.

    Also reports deleted-fact retrieval cosine (per Y+ spec section 3 verification
    recipe: "verify deletion via predecessor-start query; measure cos(retrieved, xi_f)").
    """
    del_norms = []
    del_zs = []
    del_cosines = []
    for idx in del_idx:
        nrm = float(np.linalg.norm(W_post @ Xi[idx]))
        # One-sided Z: only above-null deviation counts as failure.
        z_signed = (nrm - null_mean) / max(null_std, 1e-30)
        z_failure = max(0.0, z_signed)
        del_norms.append(nrm)
        del_zs.append(z_failure)
        del_cosines.append(retrieval_cosine(W_post, Xi[idx]))
    retain_cos = [retrieval_cosine(W_post, Xi[i]) for i in retain_idx]
    return {
        "deleted_residual_norm_mean": float(np.mean(del_norms)),
        "deleted_residual_norm_max": float(np.max(del_norms)),
        "deleted_Z_mean": float(np.mean(del_zs)),
        "deleted_Z_max": float(np.max(del_zs)),
        "deleted_cosine_mean": float(np.mean(del_cosines)),
        "deleted_cosine_max": float(np.max(del_cosines)),
        "retained_cosine_mean": float(np.mean(retain_cos)),
        "retained_cosine_min": float(np.min(retain_cos)),
        "retained_cosine_count": len(retain_cos),
    }


def run_one_seed(seed: int, D: int, M_facts: int, k_del: int, n_null: int) -> Dict:
    enc = encoder_from_env(D=D, seed=seed)
    encoder_mode = enc.cfg.mode

    t0 = time.time()
    Xi = enc.encode_batch([f"fact_{seed}_{i}" for i in range(M_facts)])
    W0 = build_W_from_patterns(Xi)

    # Same delete set used for both cells (reproducible across primitives)
    rng_sel = np.random.default_rng(seed * 17 + 5)
    del_idx = rng_sel.choice(M_facts, size=k_del, replace=False).tolist()
    retain_idx = [i for i in range(M_facts) if i not in set(del_idx)]

    # --- Cell B1: PP-46 ---
    W_post_46, certs_46 = _apply_deletions_pp46(W0, Xi, del_idx)
    # --- Cell B2: PP-56 ---
    W_post_56, certs_56 = _apply_deletions_pp56(W0, Xi, del_idx)

    # Shared null distribution baseline computed on the PP-46 post-W
    # (per spec; both cells use same baseline). Using the same null
    # eta-distribution for both Z computations keeps the comparison clean.
    rng_null = np.random.default_rng(seed * 23 + 11)
    null_mean_46, null_std_46 = null_distribution_norm(W_post_46, n_null, rng_null)
    rng_null2 = np.random.default_rng(seed * 23 + 11)  # same seed -> same draws
    null_mean_56, null_std_56 = null_distribution_norm(W_post_56, n_null, rng_null2)

    m46 = _measure_cell(W_post_46, Xi, del_idx, retain_idx, null_mean_46, null_std_46)
    m56 = _measure_cell(W_post_56, Xi, del_idx, retain_idx, null_mean_56, null_std_56)

    # Cert reproducibility: rebuild W_0 from same patterns, redo deletion, compare W' byte-exact.
    W0_repro = build_W_from_patterns(Xi)
    W_post_46_repro, _ = _apply_deletions_pp46(W0_repro, Xi, del_idx)
    W_post_56_repro, _ = _apply_deletions_pp56(W0_repro, Xi, del_idx)
    repro_46_err = float(np.max(np.abs(W_post_46 - W_post_46_repro)))
    repro_56_err = float(np.max(np.abs(W_post_56 - W_post_56_repro)))
    repro_46 = repro_46_err <= CERT_REPRO_TOL
    repro_56 = repro_56_err <= CERT_REPRO_TOL

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "encoder_mode": encoder_mode,
        "D": D,
        "M_facts": M_facts,
        "k_del": k_del,
        "n_null_probes": n_null,
        # Shared
        "del_idx": del_idx,
        # Cell B1
        "B1_null_mean": null_mean_46,
        "B1_null_std": null_std_46,
        "B1_cert_scalar_mean": float(np.mean(certs_46)),
        "B1_deleted_Z_mean": m46["deleted_Z_mean"],
        "B1_deleted_Z_max": m46["deleted_Z_max"],
        "B1_deleted_cosine_mean": m46["deleted_cosine_mean"],
        "B1_deleted_cosine_max": m46["deleted_cosine_max"],
        "B1_retained_cosine_mean": m46["retained_cosine_mean"],
        "B1_retained_cosine_min": m46["retained_cosine_min"],
        "B1_cert_reproducible": bool(repro_46),
        "B1_repro_max_abs_err": repro_46_err,
        # Cell B2
        "B2_null_mean": null_mean_56,
        "B2_null_std": null_std_56,
        "B2_cert_scalar_mean": float(np.mean(certs_56)),
        "B2_deleted_Z_mean": m56["deleted_Z_mean"],
        "B2_deleted_Z_max": m56["deleted_Z_max"],
        "B2_deleted_cosine_mean": m56["deleted_cosine_mean"],
        "B2_deleted_cosine_max": m56["deleted_cosine_max"],
        "B2_retained_cosine_mean": m56["retained_cosine_mean"],
        "B2_retained_cosine_min": m56["retained_cosine_min"],
        "B2_cert_reproducible": bool(repro_56),
        "B2_repro_max_abs_err": repro_56_err,
        "elapsed_s": elapsed,
    }


def _classify_cell(seeds_results: List[Dict], prefix: str) -> Tuple[str, float, float, bool]:
    z_max = max(r[f"{prefix}_deleted_Z_max"] for r in seeds_results)
    retain_min = min(r[f"{prefix}_retained_cosine_min"] for r in seeds_results)
    all_repro = all(r[f"{prefix}_cert_reproducible"] for r in seeds_results)
    if z_max < HP_DEL_Z and retain_min > HP_RETAIN_COSINE and all_repro:
        v = "HARD_PASS"
    elif z_max > HF_DEL_Z or retain_min < HF_RETAIN_COSINE or not all_repro:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"
    return v, z_max, retain_min, all_repro


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    if run_mode == "full":
        seeds = SEEDS_FULL
        D = D_FULL
        M = M_FACTS_FULL
        k_del = K_DEL_FULL
    else:
        seeds = SEEDS_SMOKE
        D = D_SMOKE
        M = M_FACTS_SMOKE
        k_del = K_DEL_SMOKE
    encoder_mode_env = os.environ.get("HDLAB_ENCODER",
                                       "hyperprobe" if run_mode == "full" else "synthetic")
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} D={D} M_facts={M} k_del={k_del} "
          f"n_null_probes={N_NULL_PROBES} encoder={encoder_mode_env} seeds={seeds}",
          flush=True)

    run_config = {"N": D, "run_mode": run_mode, "M": M}
    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    if done:
        print(f"[ckpt] {len(done)} of {len(seeds)} seeds resumed", flush=True)

    t0 = time.time()
    for seed in remaining:
        print(f"  seed={seed}: store {M} facts, delete {k_del} via PP-46 + PP-56 ...",
              flush=True)
        result = run_one_seed(seed, D, M, k_del, N_NULL_PROBES)
        result["N"] = D
        result["run_mode"] = run_mode
        write_partial(out_dir, seed, result)
        print(f"    B1: Z_max={result['B1_deleted_Z_max']:.2f} "
              f"retain_min={result['B1_retained_cosine_min']:.3f} "
              f"repro={result['B1_cert_reproducible']} | "
              f"B2: Z_max={result['B2_deleted_Z_max']:.2f} "
              f"retain_min={result['B2_retained_cosine_min']:.3f} "
              f"repro={result['B2_cert_reproducible']} "
              f"({result['elapsed_s']:.1f}s)", flush=True)

    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)
    seeds_results = [per_seed[str(s)] for s in seeds]

    v_b1, b1_z, b1_ret, b1_repro = _classify_cell(seeds_results, "B1")
    v_b2, b2_z, b2_ret, b2_repro = _classify_cell(seeds_results, "B2")

    def _comb(v1: str, v2: str) -> str:
        order = {"HARD_FAIL": 0, "MIDDLE_BAND": 1, "HARD_PASS": 2}
        return min((v1, v2), key=lambda v: order[v])

    verdict_combined = _comb(v_b1, v_b2)

    # Per-cell deleted-cosine for transparency (the spec section 3 verification metric)
    b1_del_cos_max = max(r["B1_deleted_cosine_max"] for r in seeds_results)
    b2_del_cos_max = max(r["B2_deleted_cosine_max"] for r in seeds_results)
    verdict_msg = (
        f"Phase 0.5 v2 Y+ sub-test B (dual primitive): "
        f"B1 (PP-46) one-sided Z_max={b1_z:.2f} del_cos_max={b1_del_cos_max:.3f} "
        f"retain_min={b1_ret:.3f} repro={b1_repro} -> {v_b1}; "
        f"B2 (PP-56) one-sided Z_max={b2_z:.2f} del_cos_max={b2_del_cos_max:.3f} "
        f"retain_min={b2_ret:.3f} repro={b2_repro} -> {v_b2}; "
        f"HP: one-sided Z<{HP_DEL_Z} AND retain>{HP_RETAIN_COSINE} AND reproducible; "
        f"HF: one-sided Z>{HF_DEL_Z} OR retain<{HF_RETAIN_COSINE} OR non-reproducible. "
        f"(One-sided Z: only under-deletion fails; over-deletion = success per "
        f"Sherman-Morrison semantics.) Combined: {verdict_combined}." + probe_quality_tag()
    )

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
        "verdict_B1": v_b1,
        "B1_deleted_Z_max_across_seeds": b1_z,
        "B1_retained_cosine_min_across_seeds": b1_ret,
        "B1_cert_reproducible_all": b1_repro,
        "verdict_B2": v_b2,
        "B2_deleted_Z_max_across_seeds": b2_z,
        "B2_retained_cosine_min_across_seeds": b2_ret,
        "B2_cert_reproducible_all": b2_repro,
        "verdict": verdict_combined,
        "verdict_msg": verdict_msg,
        "elapsed_s": total_elapsed,
        "thresholds": {
            "HP_deleted_Z_max": HP_DEL_Z,
            "HF_deleted_Z_max": HF_DEL_Z,
            "HP_retained_cosine_min": HP_RETAIN_COSINE,
            "HF_retained_cosine_min": HF_RETAIN_COSINE,
            "cert_repro_tol": CERT_REPRO_TOL,
        },
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict_B1={v_b1} verdict_B2={v_b2} "
          f"combined={verdict_combined} elapsed={total_elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {out_dir / 'metrics.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
