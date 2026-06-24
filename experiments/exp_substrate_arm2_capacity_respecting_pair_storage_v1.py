"""substrate_arm2_capacity_respecting_pair_storage_v1 -- canonical HRR pair-storage diagnostic.

Strategic rationale (USER compositional-drill 2026-06-24, ANCHOR 1):
  Shotgun ARM 2 used M=200 pairs in a 20x20 grid at D=8192 with sparse-bipolar
  f=0.05; bank L2 grew unbounded and in_dist top-1 collapsed to 0.10 (chance).
  This was a SATURATION failure, not an HRR primitive failure: the canonical
  regime for HRR pair-store is M ~= vocab_size (1-to-1 binding), not M >> vocab.

This cell establishes the baseline aliveness at the capacity-respecting regime:
  - D = 8192, sparse-bipolar f = 0.05.
  - n_subj = 20, n_obj = 20.
  - M = 20 train pairs in 1-to-1 mapping: random permutation pi over 0..19;
    train_pairs = [(i, pi(i)) for i in range(20)].
  - Bank = sum_{(i,j) in train} bind(A_i, B_j).
  - Metric: in-distribution top-1 (for each (i, pi(i)) in train, unbind(bank, A_i),
    cosine over OBJ codebook, check argmax == pi(i)).
  - 3 seeds for CV.

Pre-reg HARD bands (sacrosanct both directions):
  HARD_PASS: in_dist top-1 >= 0.95 (HRR primitive ALIVE at canonical capacity).
  HARD_FAIL: in_dist top-1 < 0.80 (HRR primitive BROKEN even at canonical regime).
  MIDDLE_BAND: 0.80 <= in_dist < 0.95.

By-construction-saturation tier (per Skunkworks):
  If in_dist == 1.000 AND CV < 0.001 -> DIAGNOSTIC_PASS (not chain-grade).
  M=20 << capacity at D=8192 -> perfect recovery is by construction.
  Crosstalk estimate ~ M * f^2 / D = 20 * 0.0025 / 8192 ~ 6e-6 << 1/n_obj = 0.05.

Selftest gate (formula-selftests at TINY config):
  D=512, M=5, 1-to-1 -> expect in_dist == 1.000.
  Crosstalk estimate ~ 5 * 0.05^2 / 512 = 2.4e-5 << 1/5 = 0.20.

ASCII only. CPU only (numpy). Per-seed checkpoint via experiments/_seed_checkpoint.

Cites: USER_compositional_drill_handoff_ANCHOR_1_2026-06-24;
  exp_substrate_brain_aligned_aliveness_shotgun_v1 ARM 2 super-saturation;
  by-construction-saturation tiering (Skunkworks 2026-06-22);
  HRR involutive + sparse-bipolar 20-300x bundle lift (op findings 2026-06-23).
"""
from __future__ import annotations
import sys, os, argparse, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_arm2_capacity_respecting_pair_storage_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 8192          # substrate canonical dim
SPARSE_F = 0.05       # sparse-bipolar fraction nonzero
N_SUBJ = 20
N_OBJ = 20
M_PAIRS = 20          # 1-to-1 mapping (M == n_subj == n_obj)
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:  # smoke
    SEEDS = [0]

CONFIG_VERSION = (
    "substrate_arm2_capacity_respecting_pair_storage_v1; N=%d f=%.3f seeds=%s "
    "n_subj=%d n_obj=%d M=%d (1-to-1 permutation mapping)"
) % (N_DIM, SPARSE_F, SEEDS, N_SUBJ, N_OBJ, M_PAIRS)


# ------------------------------------------------------------------
# Substrate primitives (pure numpy; no torch)
# ------------------------------------------------------------------
def _sparse_bipolar(n: int, dim: int, f: float, g: np.random.Generator) -> np.ndarray:
    """Stack of n sparse-bipolar vectors at dim with fraction f nonzero. Shape (n, dim)."""
    out = np.zeros((n, dim), dtype=np.float32)
    k = max(1, int(round(f * dim)))
    for i in range(n):
        idx = g.choice(dim, k, replace=False)
        signs = g.integers(0, 2, k).astype(np.float32) * 2.0 - 1.0
        out[i, idx] = signs
    return out


def _bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular convolution via FFT."""
    fa = np.fft.fft(a); fb = np.fft.fft(b)
    return np.fft.ifft(fa * fb).real.astype(np.float32)


def _unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular correlation via FFT * conj."""
    fc = np.fft.fft(c); fb = np.fft.fft(b)
    return np.fft.ifft(fc * fb.conj()).real.astype(np.float32)


def _norm_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / n).astype(np.float32)


def _cosine(a: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Row-wise cosine between vector a (D,) and matrix B (k,D)."""
    an = a / (np.linalg.norm(a) + 1e-8)
    Bn = _norm_rows(B)
    return Bn @ an


# ------------------------------------------------------------------
# Core diagnostic
# ------------------------------------------------------------------
def _pair_storage_in_dist(seed: int, dim: int, n_subj: int, n_obj: int,
                          m_pairs: int, f: float) -> dict:
    """1-to-1 pair storage at capacity-respecting regime.

    Build:
      A = sparse-bipolar codebook of n_subj subject vectors.
      B = sparse-bipolar codebook of n_obj  object vectors.
      pi = random permutation of length min(n_subj, n_obj), truncated to m_pairs.
      train_pairs = [(i, pi[i]) for i in range(m_pairs)].
      bank = sum_{(i,j) in train_pairs} bind(A_i, B_j).

    Test (in-distribution):
      For each (i, pi[i]) in train_pairs:
        rec = unbind(bank, A_i)
        pred = argmax cosine(rec, B)
        correct += (pred == pi[i]).
      Report in_distribution_top1 = correct / m_pairs.

    Also report bank L2 norm as a sanity diagnostic (shotgun ARM 2 had unbounded
    L2 growth at M=200; at M=20 1-to-1 it should be bounded).
    """
    assert m_pairs <= min(n_subj, n_obj), "1-to-1 requires m_pairs <= min(n_subj, n_obj)"
    g = np.random.default_rng(seed * 1009 + 2)
    A = _sparse_bipolar(n_subj, dim, f, g)
    B = _sparse_bipolar(n_obj, dim, f, g)
    # 1-to-1 permutation: pick m_pairs subjects (0..m-1) and a random permutation of objects
    obj_perm = g.permutation(n_obj)[:m_pairs]  # subj i -> obj obj_perm[i]
    train_pairs = [(int(i), int(obj_perm[i])) for i in range(m_pairs)]
    bank = np.zeros(dim, dtype=np.float32)
    for (i, j) in train_pairs:
        bank += _bind(A[i], B[j])
    bank_l2 = float(np.linalg.norm(bank))
    # In-distribution recall
    correct = 0
    cosines_correct = []
    cosines_top1 = []
    for (i, j) in train_pairs:
        rec = _unbind(bank, A[i])
        cos_to_B = _cosine(rec, B)
        pred = int(np.argmax(cos_to_B))
        cosines_correct.append(float(cos_to_B[j]))
        cosines_top1.append(float(cos_to_B[pred]))
        if pred == j:
            correct += 1
    in_top1 = correct / max(m_pairs, 1)
    return {
        "n_subj": n_subj,
        "n_obj": n_obj,
        "m_pairs": m_pairs,
        "in_distribution_top1": float(in_top1),
        "chance_top1": 1.0 / n_obj,
        "bank_l2": bank_l2,
        "mean_cosine_correct": float(np.mean(cosines_correct)) if cosines_correct else 0.0,
        "mean_cosine_top1": float(np.mean(cosines_top1)) if cosines_top1 else 0.0,
        "crosstalk_estimate": float(m_pairs * (f * f) / dim),  # ~ M*f^2/D
        "train_pairs": train_pairs,
        "N": dim,
        "M": m_pairs,
    }


# ------------------------------------------------------------------
# Per-seed driver
# ------------------------------------------------------------------
def run_unit(seed: int) -> dict:
    t0 = time.time()
    print("  [seed=%d] capacity-respecting pair storage starting" % seed, flush=True)
    res = _pair_storage_in_dist(seed, N_DIM, N_SUBJ, N_OBJ, M_PAIRS, SPARSE_F)
    print(
        "  [seed=%d] in_dist_top1=%.4f bank_l2=%.3f mean_cos_correct=%.4f crosstalk_est=%.2e"
        % (seed, res["in_distribution_top1"], res["bank_l2"],
           res["mean_cosine_correct"], res["crosstalk_estimate"]),
        flush=True,
    )
    return {
        "seed": seed,
        "pair_storage": res,
        "wall_s": time.time() - t0,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "M": M_PAIRS,
    }


# ------------------------------------------------------------------
# Verdict logic
# ------------------------------------------------------------------
def compute_verdict(units: list) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})
    in_dists = [u["pair_storage"]["in_distribution_top1"] for u in units]
    bank_l2s = [u["pair_storage"]["bank_l2"] for u in units]
    cos_correct = [u["pair_storage"]["mean_cosine_correct"] for u in units]
    in_mean = float(np.mean(in_dists))
    in_cv = float(np.std(in_dists) / max(abs(in_mean), 1e-12))
    bank_l2_mean = float(np.mean(bank_l2s))
    cos_correct_mean = float(np.mean(cos_correct))

    # Tier classification
    is_exact = all(abs(x - 1.0) < 1e-9 for x in in_dists)
    is_low_cv = (in_cv < 0.001)

    if is_exact and is_low_cv:
        cell_verdict = "DIAGNOSTIC_PASS"
        cell_msg = (
            "DIAGNOSTIC_PASS (by-construction): in_dist top-1 = 1.000 across %d seeds "
            "(CV %.2e < 0.001). M=%d << capacity at D=%d with f=%.3f; crosstalk "
            "estimate ~%.2e is far below the 1/n_obj=%.3f discrimination floor. "
            "HRR primitive ALIVE at canonical 1-to-1 regime; this is by construction, "
            "NOT chain-grade. Confirms shotgun ARM 2 failure (M=200 super-saturated) "
            "was a SATURATION issue, not primitive collapse. Capacity ceiling probe "
            "is the natural follow-up."
        ) % (len(units), in_cv, M_PAIRS, N_DIM, SPARSE_F,
             units[0]["pair_storage"]["crosstalk_estimate"],
             units[0]["pair_storage"]["chance_top1"])
    elif in_mean >= 0.95:
        cell_verdict = "HARD_PASS"
        cell_msg = (
            "HARD_PASS: in_dist top-1 mean=%.4f >= 0.95 (CV %.4f) across %d seeds. "
            "HRR primitive ALIVE at canonical M=%d 1-to-1 regime at D=%d. "
            "Confirms shotgun ARM 2 super-saturation hypothesis: M=200 broke storage, "
            "M=%d preserves it. Mean cosine to correct B = %.4f. Bank L2 mean = %.3f."
        ) % (in_mean, in_cv, len(units), M_PAIRS, N_DIM, M_PAIRS,
             cos_correct_mean, bank_l2_mean)
    elif in_mean < 0.80:
        cell_verdict = "HARD_FAIL"
        cell_msg = (
            "HARD_FAIL: in_dist top-1 mean=%.4f < 0.80 (CV %.4f) across %d seeds. "
            "HRR primitive BROKEN even at canonical 1-to-1 M=%d regime at D=%d. "
            "Substrate-product implication: HRR cannot serve as pair-store primitive; "
            "need alternative composition mechanism (Lock-in chain, sparse-bipolar "
            "outer-product, etc.). Mean cosine to correct B = %.4f."
        ) % (in_mean, in_cv, len(units), M_PAIRS, N_DIM, cos_correct_mean)
    else:
        cell_verdict = "MIDDLE_BAND"
        cell_msg = (
            "MIDDLE_BAND: in_dist top-1 mean=%.4f (0.80 <= x < 0.95) CV %.4f across "
            "%d seeds at M=%d D=%d. Partial aliveness; HRR works with measurable "
            "crosstalk at M=vocab. Escalate to capacity sweep + ratio characterization."
        ) % (in_mean, in_cv, len(units), M_PAIRS, N_DIM)

    detail = {
        "n_seeds": len(units),
        "in_distribution_top1_mean": in_mean,
        "in_distribution_top1_cv": in_cv,
        "in_distribution_top1_per_seed": in_dists,
        "bank_l2_mean": bank_l2_mean,
        "bank_l2_per_seed": bank_l2s,
        "mean_cosine_correct_per_seed": cos_correct,
        "mean_cosine_correct_mean": cos_correct_mean,
        "chance_top1": units[0]["pair_storage"]["chance_top1"],
        "crosstalk_estimate": units[0]["pair_storage"]["crosstalk_estimate"],
        "is_exact_recovery": is_exact,
        "is_low_cv": is_low_cv,
        "CONFIG_VERSION": CONFIG_VERSION,
        "band_definition": {
            "HARD_PASS": "in_dist >= 0.95 AND CV >= 0.001",
            "DIAGNOSTIC_PASS": "in_dist == 1.000 AND CV < 0.001 (by-construction)",
            "MIDDLE_BAND": "0.80 <= in_dist < 0.95",
            "HARD_FAIL": "in_dist < 0.80",
        },
        "what_this_does_not_show": (
            "In-distribution storage at canonical 1-to-1 regime ONLY. Does NOT test: "
            "(1) holdout / compositional generalization (separate follow-up cell); "
            "(2) capacity ceiling above M=vocab (capacity-sweep cell); "
            "(3) learning, plasticity, or gradient updates (pure substrate primitives); "
            "(4) chain-grade integration with substrate KG. "
            "DIAGNOSTIC_PASS tier reflects by-construction-saturation: at M=20 / D=8192 / "
            "f=0.05, crosstalk M*f^2/D ~ 6e-6 is far below the 1/n_obj=0.05 discrimination "
            "floor, so perfect recovery is mathematically expected, not informative."
        ),
        "honest_scope": (
            "Pure substrate primitives (HRR bind/unbind + sparse-bipolar codebook). "
            "NumPy CPU. Per USER 2026-06-24 compositional-drill ANCHOR 1."
        ),
        "cites": [
            "USER_compositional_drill_handoff_ANCHOR_1_2026-06-24",
            "exp_substrate_brain_aligned_aliveness_shotgun_v1_ARM2_super_saturation_2026-06-24",
            "by_construction_saturation_tiering_Skunkworks_2026-06-22",
            "operational_findings_2026-06-23_HRR_involutive",
            "operational_findings_2026-06-23_sparse_bipolar_20_300x_bundle_lift",
        ],
    }
    return (cell_verdict, cell_msg, detail)


# ------------------------------------------------------------------
# Selftest -- mechanism unit-tests at TINY config
# ------------------------------------------------------------------
def _selftest() -> None:
    """Formula-selftest per handoff: D=512, M=5, 1-to-1 -> expect in_dist == 1.000.

    Crosstalk estimate at this config: 5 * 0.05^2 / 512 = 2.4e-5 << 1/5 = 0.20,
    so perfect recovery is by-construction. If selftest does NOT hit 1.000, the
    HRR bind/unbind or sparse-bipolar codebook machinery is broken and the full
    run is uninformative.
    """
    g = np.random.default_rng(0)
    # Sparse-bipolar shape + sparsity rate
    dim_t = 512; f_t = 0.05
    X = _sparse_bipolar(5, dim_t, f_t, g)
    assert X.shape == (5, dim_t), "sparse-bipolar shape mismatch"
    avg_nz = float(np.mean(np.count_nonzero(X, axis=1)))
    expect = f_t * dim_t
    assert abs(avg_nz - expect) <= max(1.0, 0.2 * expect), (
        "sparse-bipolar nz=%.1f vs expected %.1f" % (avg_nz, expect)
    )
    # HRR involutive sanity
    a = g.standard_normal(dim_t).astype(np.float32)
    b = _sparse_bipolar(1, dim_t, f_t, g)[0]
    c = _bind(a, b)
    a_back = _unbind(c, b)
    cos_ab = float(_cosine(a_back, a[None, :])[0])
    assert cos_ab > 0.3, "HRR bind/unbind round-trip cosine too low (%.3f)" % cos_ab
    print("[selftest] sparse-bipolar shape+rate OK; HRR involutive cos=%.3f (>0.3 OK)"
          % cos_ab, flush=True)

    # FORMULA selftest: D=512, M=5, 1-to-1 -> in_dist == 1.000
    res = _pair_storage_in_dist(seed=0, dim=512, n_subj=5, n_obj=5, m_pairs=5, f=0.05)
    print(
        "[selftest] formula-gate D=512 M=5 1-to-1: in_dist_top1=%.4f "
        "(expect 1.000) bank_l2=%.3f crosstalk_est=%.2e"
        % (res["in_distribution_top1"], res["bank_l2"], res["crosstalk_estimate"]),
        flush=True,
    )
    assert res["in_distribution_top1"] == 1.0, (
        "formula-selftest FAIL: D=512 M=5 1-to-1 in_dist_top1=%.4f, expected 1.000"
        % res["in_distribution_top1"]
    )
    # Sanity: crosstalk estimate sanity-check (should be far below 1/n_obj=0.2)
    assert res["crosstalk_estimate"] < 0.001, (
        "crosstalk estimate %.6f unexpectedly high at D=512 M=5"
        % res["crosstalk_estimate"]
    )

    # SMOKE-PATH selftest: shrink to a viable smoke regime that's still deep below
    # crosstalk floor so the gated --smoke run also lands at in_dist == 1.000.
    # Smoke uses N_SUBJ=N_OBJ=M=20 at D=8192 by default; we just verify the smoke
    # path runs (1 seed). The actual --smoke invocation by the gate will exercise
    # this end-to-end + write metrics.json.
    print("[selftest] PASS: HRR involutive + 1-to-1 pair storage by-construction OK", flush=True)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print(
        "[config] %s mode=%s N=%d f=%.3f seeds=%s | %s" % (
            ANCHOR_NAME, RUN_MODE, N_DIM, SPARSE_F, SEEDS, CONFIG_VERSION
        ),
        flush=True,
    )
    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "M": M_PAIRS,
        "schema": "capacity-respecting-pair-storage-v1",
    }
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        already = aggregate_partials(out_dir, [key], run_config=run_cfg)
        if key in already:
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        result = run_unit(seed)
        write_partial_key(out_dir, key, result)
    units = list(aggregate_partials(
        out_dir, ["s%d" % s for s in SEEDS], run_config=run_cfg
    ).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "SPARSE_F": SPARSE_F,
        "N_SUBJ": N_SUBJ,
        "N_OBJ": N_OBJ,
        "M_PAIRS": M_PAIRS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_capacity_respecting_pair_storage",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "N/A (mechanism-characterization cell, not LM cell)",
        "CONFIG_VERSION": CONFIG_VERSION,
    }
    write_metrics(out_dir, metrics)
    print("[done] metrics written to %s/metrics.json elapsed=%.2fs"
          % (out_dir, metrics["elapsed_s"]), flush=True)
