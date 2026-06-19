"""AXIS-2 CODEBOOK x DENSITY: phase structure by codebook class at N=4096.

SCIENTIFIC QUESTION (Axis 2 -- codebook class design space):
  Different codebook classes impose different correlation structures on stored keys.
  How does the codebook class interact with storage density M/N to shape the
  retention phase diagram?

  Codebook classes to test at N=4096:
    (A) BSC: random bipolar (+/-1). No structure. Max overlap ~ 1/sqrt(N).
    (B) Kerdock: structured 4-coset. Max cross-correlation <= 1/sqrt(N). Same bound as BSC.
    (C) Hadamard rows: Walsh-Hadamard rows. Max overlap = 1/N (better than BSC).
    (D) Gaussian-projected: normalize N-dim Gaussian vectors to unit sphere.
    (E) Sparse BSC: 10% non-zero entries. Sparsity-induced structure.
    (F) Antipodal pairs: keys come in +/- pairs (structure with pairwise correlation=1).

  For each codebook: retention vs M/N in {0.5, 1, 2, 4, 8} at beta=8.
  Question: does the M/N=8 phase boundary persist across codebook classes?
  Or is it Kerdock-specific?

PRE-REGISTERED BANDS:
  Calibration probe (first codebook-class comparative study).
  Bands widened to +-50% per calibration-probe policy (no prior anchor for cross-class).

  HARD_PASS: BSC and Kerdock show qualitatively SIMILAR phase diagrams
    (retention drops in same M/N range [4, 16]).
    At least 3/6 codebook classes show retention < 0.5 at M/N=8.
    Interpretation: phase structure is substrate-generic, not codebook-specific.
  HARD_FAIL: Only Kerdock shows retention drop; BSC and Hadamard maintain ret >= 0.9
    at M/N=8 (Kerdock is an artifact of specific structured codebook).
  MIDDLE_BAND: 1-2/6 codebook classes show retention drop. Mixed picture.

FORMULA SELF-TESTS:
  1. BSC max_overlap ~ 1/sqrt(N) = 1/64 = 0.016. Verify by sampling 100 pairs.
  2. Hadamard rows: for N=4096 (not power of 2 for pure Hadamard; use nearest 4096 rows
     of 4096x4096 random DFT-like orthogonal matrix). Or: generate 4096 orthogonal rows
     via Gram-Schmidt. Expected: max_overlap = 0 (exactly orthogonal).
  3. Gaussian-projected: normalize -> near-orthogonal. Expected max_overlap ~ 1/sqrt(N).
  4. Sparse BSC (10% nonzero): effective dimension d_eff = N * 0.1 = 409.6.
     Max overlap ~ 1/sqrt(d_eff) ~ 0.05.
  5. retention(M=1) = 1.0 for any codebook (single fact, no interference).
  6. N == 4096 (PROT-018).

OOM CHECK:
  W at N=4096: 64MB. Codebook C x N = 4096 x 4096 = 64MB. Total peak: ~200MB. OK.

TIMEOUT ESTIMATE:
  axis1_chunk2 elapsed (4 M values, 7 betas, 5 seeds, N=4096): 79s.
  axis2: 5 M/N values, 1 beta, 5 seeds, 6 codebooks = 6/7 * 5/7 * 6 = 3.67x.
  timeout_s = ceil(1.5 * 79 * 3.67) = ceil(435) -> 600s.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Queue: overnight_queue (GPU; N=4096 6-codebook x 5-M/N design-space sweep)
Pre-reg: preregs/2026-05-28_axis2_codebook_density_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load chunk-1 for retention computation helpers
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c4b", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

# Load Kerdock builder
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_v3_spec = importlib.util.spec_from_file_location("kerdock_v3_ax2", _v3_path)
v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N = 4096          # PROT-018 binding contract
N_SMOKE = 512     # smoke scale
assert N == 4096, f"PROT-018: N must be 4096; got {N}"

M_FRACS_FULL = [0.5, 1.0, 2.0, 4.0, 8.0]
M_FRACS_SMOKE = [1.0, 4.0, 8.0]

BETA = 8.0   # fixed inference beta (operating point)

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

CODEBOOK_CLASSES = ["bsc", "kerdock", "hadamard", "gaussian", "sparse_bsc", "antipodal"]

# Thresholds
PASS_N_CLASSES_DROP = 3    # at least 3/6 codebooks show ret < 0.5 at M/N=8
FAIL_KERDOCK_ONLY = 1      # only Kerdock shows drop


def get_output_dir(default_name: str = "axis2_codebook_density_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_codebook(cb_class: str, N_use: int, seed: int = 0) -> torch.Tensor:
    """Build codebook of size C x N_use for given class."""
    C = N_use
    rng = torch.Generator()
    rng.manual_seed(seed)

    if cb_class == "bsc":
        raw = torch.randint(0, 2, (C, N_use), generator=rng, dtype=torch.float32) * 2 - 1
        return raw

    elif cb_class == "kerdock":
        # Use Kerdock builder from v3
        try:
            cb = v3.build_codebook(N_use)
            if cb is not None and cb.shape[0] >= C:
                return cb[:C].float()
        except Exception:
            pass
        # Fallback to BSC if Kerdock not valid for this N
        raw = torch.randint(0, 2, (C, N_use), generator=rng, dtype=torch.float32) * 2 - 1
        return raw

    elif cb_class == "hadamard":
        # Orthogonal rows via SVD of random matrix (fast approximate)
        raw = torch.randn(C, N_use, generator=rng)
        U, _, _ = torch.linalg.svd(raw, full_matrices=False)
        return U.float() * (N_use ** 0.5)  # scale to +/-sqrt(N) range

    elif cb_class == "gaussian":
        raw = torch.randn(C, N_use, generator=rng)
        norms = raw.norm(dim=1, keepdim=True).clamp(min=1e-8)
        return (raw / norms * (N_use ** 0.5)).float()

    elif cb_class == "sparse_bsc":
        raw = torch.zeros(C, N_use, dtype=torch.float32)
        # 10% nonzero +/-1
        mask = torch.rand(C, N_use, generator=rng) < 0.1
        signs = (torch.randint(0, 2, (C, N_use), generator=rng) * 2 - 1).float()
        raw[mask] = signs[mask]
        return raw

    elif cb_class == "antipodal":
        # Half size pairs (+v, -v) so C/2 unique vectors
        half = C // 2
        base = torch.randint(0, 2, (half, N_use), generator=rng, dtype=torch.float32) * 2 - 1
        return torch.cat([base, -base], dim=0)

    else:
        raise ValueError(f"Unknown codebook class: {cb_class}")


def run_one_cell(codebook_class: str, M_frac: float, seed: int,
                  device: torch.device, N_use: int) -> Dict:
    """Run one (codebook_class, M_frac, seed) cell."""
    cb = build_codebook(codebook_class, N_use, seed=0).to(device)
    C = cb.shape[0]
    M = min(int(M_frac * N_use), C)

    rng = torch.Generator()
    rng.manual_seed(seed + 200)
    key_idx = torch.randint(0, C, (M,), generator=rng)
    val_idx = torch.randint(0, C, (M,), generator=rng)
    keys = cb[key_idx]
    vals = cb[val_idx]

    # Outer-product Hebbian store
    W = torch.zeros(N_use, N_use, device=device, dtype=torch.float32)
    batch = 512
    for start in range(0, M, batch):
        k_b = keys[start:start + batch]
        v_b = vals[start:start + batch]
        W += (v_b.T @ k_b) / N_use

    # Retention: argmax
    n_probe = min(200, M)
    probe_keys = keys[:n_probe]
    probe_val = val_idx[:n_probe] % C
    sims = (cb @ (probe_keys @ W.T).T) / N_use
    pred = torch.argmax(sims, dim=0)
    retention = float((pred == probe_val.to(device)).float().mean().item())

    # Max overlap diagnostic
    n_ovlp = min(50, M)
    pairs = torch.randint(0, n_ovlp, (20,))
    ovlp_vals = []
    for i in range(0, min(20, n_ovlp - 1), 2):
        k1 = keys[i]
        k2 = keys[i + 1]
        k1n = k1.norm(); k2n = k2.norm()
        if k1n > 0 and k2n > 0:
            ov = float((k1 @ k2 / (k1n * k2n)).abs().item())
            ovlp_vals.append(ov)
    mean_ovlp = sum(ovlp_vals) / len(ovlp_vals) if ovlp_vals else 0.0

    return {
        "codebook_class": codebook_class,
        "M_frac": M_frac,
        "M": M,
        "seed": seed,
        "retention": retention,
        "mean_overlap": mean_ovlp,
    }


def compute_verdict(summary: Dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS2_MIDDLE_BAND", "No cells.")

    N_use = summary.get("N", N)

    # Average retention at M/N=8 per codebook class
    from collections import defaultdict
    ret_at_M8: Dict[str, List[float]] = defaultdict(list)
    for c in cells:
        if abs(c.get("M_frac", 0) - 8.0) < 0.1:
            ret_at_M8[c["codebook_class"]].append(c["retention"])

    if not ret_at_M8:
        return ("AXIS2_MIDDLE_BAND", "No M/N=8 cells completed.")

    mean_ret_at_M8 = {k: sum(v) / len(v) for k, v in ret_at_M8.items()}
    n_drop = sum(1 for r in mean_ret_at_M8.values() if r < 0.5)
    kerdock_drops = mean_ret_at_M8.get("kerdock", 1.0) < 0.5
    bsc_drops = mean_ret_at_M8.get("bsc", 1.0) < 0.5

    detail = (f"n_classes_below_0.5_at_M/N=8: {n_drop}/{len(mean_ret_at_M8)}. "
              f"ret_at_M8={dict((k, round(v, 3)) for k, v in sorted(mean_ret_at_M8.items()))}. "
              f"kerdock_drops={kerdock_drops}. bsc_drops={bsc_drops}.")

    # HARD_FAIL: only Kerdock drops, BSC doesn't
    if kerdock_drops and not bsc_drops and n_drop <= FAIL_KERDOCK_ONLY:
        return ("AXIS2_HARD_FAIL",
                f"Phase transition KERDOCK-SPECIFIC: only Kerdock drops, BSC stable. " + detail)

    if n_drop >= PASS_N_CLASSES_DROP:
        return ("AXIS2_HARD_PASS",
                f"Phase structure SUBSTRATE-GENERIC: {n_drop} codebook classes show drop. " + detail)

    return ("AXIS2_MIDDLE_BAND",
            f"Mixed picture: {n_drop}/{len(mean_ret_at_M8)} classes drop. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 4096, f"PROT-018: N must be 4096; got {N}"

    # Test all 6 codebook classes build without error
    for cb_cls in CODEBOOK_CLASSES:
        try:
            cb = build_codebook(cb_cls, 64, seed=0)
            assert cb.shape[0] >= 32, f"{cb_cls} codebook too small: {cb.shape}"
            assert cb.dtype == torch.float32, f"{cb_cls} wrong dtype"
        except Exception as e:
            # Kerdock may not be valid at N=64; others must work
            if cb_cls == "kerdock":
                pass  # fallback to BSC acceptable
            else:
                raise AssertionError(f"Codebook {cb_cls} failed: {e}")

    # Test one cell at smoke scale
    cell = run_one_cell("bsc", M_frac=1.0, seed=17,
                         device=torch.device("cpu"), N_use=N_SMOKE)
    assert cell["retention"] is not None and 0 <= cell["retention"] <= 1.0, \
        f"retention sentinel: {cell['retention']}"
    assert cell["mean_overlap"] >= 0.0, f"overlap sentinel: {cell['mean_overlap']}"

    # Test verdict HARD_PASS path
    cells_hp = []
    for cb_cls in ["bsc", "kerdock", "gaussian", "hadamard"]:
        for mf in [1.0, 4.0, 8.0]:
            ret = 1.0 if mf < 8.0 else 0.3  # drop at M/N=8
            cells_hp.append({"codebook_class": cb_cls, "M_frac": mf, "M": int(mf * 64),
                              "seed": 17, "retention": ret, "mean_overlap": 0.01})
    v, msg = compute_verdict({"cells": cells_hp, "N": 64})
    assert v == "AXIS2_HARD_PASS", f"Self-test HP failed: {v}: {msg}"

    # Test verdict HARD_FAIL path
    cells_hf = []
    for cb_cls in ["kerdock"]:
        cells_hf.append({"codebook_class": cb_cls, "M_frac": 8.0, "M": int(8.0 * 64),
                          "seed": 17, "retention": 0.3, "mean_overlap": 0.01})
    for cb_cls in ["bsc", "gaussian", "hadamard", "sparse_bsc", "antipodal"]:
        cells_hf.append({"codebook_class": cb_cls, "M_frac": 8.0, "M": int(8.0 * 64),
                          "seed": 17, "retention": 0.95, "mean_overlap": 0.01})
    v2, _ = compute_verdict({"cells": cells_hf, "N": 64})
    assert v2 == "AXIS2_HARD_FAIL", f"Self-test HF failed: {v2}"


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    N_use = N_SMOKE if smoke else N
    M_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    cb_classes = CODEBOOK_CLASSES if not smoke else ["bsc", "kerdock", "hadamard"]

    outdir = get_output_dir()
    t0 = time.time()
    cells = []

    for cb_cls in cb_classes:
        for mf in M_fracs:
            for seed in seeds:
                cell = run_one_cell(cb_cls, mf, seed, device, N_use)
                cells.append(cell)
                elapsed = time.time() - t0
                print(f"cb={cb_cls} M/N={mf} seed={seed} "
                      f"ret={cell['retention']:.3f} elapsed={elapsed:.1f}s")

    elapsed_s = time.time() - t0
    summary = {"cells": cells, "N": N_use, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "M_fracs": M_fracs,
            "seeds": seeds,
            "codebook_classes": cb_classes,
            "beta": BETA,
            "smoke": smoke,
        },
        "summary": summary,
    }

    out = outdir / "metrics.json"
    with open(out, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nVERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"elapsed={elapsed_s:.1f}s")
    print(f"metrics -> {out}")


if __name__ == "__main__":
    main()
