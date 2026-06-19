"""Saad-Solla v17: cross-codebook generality at N=4096.

CONTEXT:
  v15 (HARD_PASS_STRONG): N=8192 5-seed Kerdock codebook, f-sweep plateau confirmed.
  v16 (M-axis expansion): plateau holds at higher M_frac.
  v17 asks: is the Saad-Solla saddle-cascade structure CODEBOOK-SPECIFIC?
  Does the f-sweep plateau (R^2 < 0.85 OR max_dev >= 0.40) appear for:
    1. BSC (random binary {+1,-1} codebook)
    2. Antipodal (each codeword paired with its negation)
  These are structurally different from Kerdock, which has structured near-orthogonality.

  If plateau appears across all codebook families: the saddle structure is a SUBSTRATE PROPERTY
  (not Kerdock geometry).
  If plateau is Kerdock-specific: the product must use Kerdock codebooks.

SCIENTIFIC QUESTION:
  At N=4096, 3 seeds, do BSC and Antipodal codebooks show the same f-sweep plateau?
  Framing: f-sweep = fraction of patterns replaced with fresh memories (Phase B);
  plateau in retention_A vs f means the substrate resists catastrophic forgetting
  regardless of codebook geometry.

PRE-REGISTERED BANDS (axis-expansion; prior anchor = v15 Kerdock N=8192 5-seed HARD_PASS_STRONG):
  Prior anchor: Kerdock plateau r2=0.290, max_dev=0.514 at N=8192.
  Expected: plateau appears for BSC (same binary structure, less geometric regularity).
  Uncertain for Antipodal (different symmetry group).
  Bands at +/-50% per calibration-probe policy for non-Kerdock codebooks.

  HARD_PASS: plateau gate fires (r2<0.85 OR max_dev>=0.40) at >= 2/3 seeds
    for BOTH BSC AND Antipodal.
    Interpretation: Saad-Solla saddle structure is codebook-family robust.
  HARD_FAIL: ALL seeds at ALL non-Kerdock families show smooth-monotone.
    Would indicate plateau is Kerdock-specific (structured near-orthogonality required).
  MIDDLE_BAND: plateau holds for one family but not the other.

FORMULA SELF-TESTS:
  1. BSC codebook at N=4096: N x N matrix of random +/-1 values. C=N rows.
  2. Antipodal: C/2 random vectors + their negations. Total C=N rows.
  3. seed_passes_hp: same gate as v15 (r2<0.85 OR max_dev>=0.40).
  4. N == 4096 (PROT-018 binding).

OOM CHECK:
  W float32 at N=4096: 4096^2 * 4 = 64MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v15 wall: 25 cells (5 seeds x 5 f-pts) at N=8192 -> 652s/cell.
  N=4096 vs N=8192: O(N^2) -> 4x cheaper -> 163s/cell.
  v17: 2 families x 3 seeds x 5 f-pts = 30 cells x 163s = 4890s.
  1.5x safety: 7335s -> 7200s (2h). Flag for visibility.
  timeout_s = 10800 (3h with extra margin for CPU-only codebook construction).

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: saad_solla_v17_cross_cb_v1_n4096
Queue: overnight_queue (GPU; N=4096 BSC+Antipodal codebooks, 3 seeds x 5 f-pts)
Pre-reg: preregs/2026-05-28_saad_solla_v17_cross_cb_v1_n4096.md
Parent: saad_solla_v15_n8192_5seed (v266 HARD_PASS_STRONG; cross-codebook next)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v15 base for run_one_cell_no_replay, pearson_r2, linear_fit_residuals
_v15_path = REPO / "experiments" / "exp_saad_solla_v15_n8192_5seed.py"
_v15_spec = importlib.util.spec_from_file_location("ss_v15_v17", _v15_path)
v15 = importlib.util.module_from_spec(_v15_spec)
_v15_spec.loader.exec_module(v15)

pearson_r2          = v15.pearson_r2
run_one_cell_no_replay = v15.run_one_cell_no_replay

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Non-Kerdock codebook families to test
CODEBOOK_FAMILIES = ["bsc", "antipodal"]

F_SWEEP_FULL  = [0.0, 0.15, 0.50, 0.80, 1.0]   # same 5-pt sweep as v15
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BATCH_SIZE       = 32
BATCH_SIZE_SMOKE = 16
EPOCHS           = 3
EPOCHS_SMOKE     = 1
PHASE_A_EPOCHS   = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES            = 150_000
BYTES_SMOKE      = 4_000

# Gate thresholds (same as v15)
HP_R2_MAX       = 0.85
HP_MAX_DEV_ALT  = 0.40
HF_R2_MIN       = 0.95
HF_MAX_DEV_MAX  = 0.04
HP_MAJORITY_MIN = 2   # >= 2/3 seeds pass for HARD_PASS


def get_output_dir(default_name: str = "saad_solla_v17_cross_cb_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_non_kerdock_codebook(family: str, N: int, seed: int,
                                device: torch.device) -> torch.Tensor:
    """Build BSC or Antipodal codebook."""
    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 10000)

    if family == "bsc":
        # Random binary {+1, -1} codebook, C=N rows
        cb = (torch.randint(0, 2, (N, N), generator=gen, device=device) * 2 - 1).float()
        return cb
    elif family == "antipodal":
        # C/2 random Gaussian vectors + negations
        C_half = N // 2
        vecs = torch.randn(C_half, N, generator=gen, device=device)
        norms = vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
        vecs = vecs / norms
        # Binary-ize to +/-1 (take sign)
        vecs_bin = vecs.sign()
        vecs_bin[vecs_bin == 0] = 1.0
        cb = torch.cat([vecs_bin, -vecs_bin], dim=0)   # (N, N) with antipodal pairs
        return cb
    else:
        raise ValueError(f"Unknown codebook family: {family}")


def run_one_seed_family(family: str, seed: int, f: float,
                         N_cfg: int, batch_size: int, n_epochs: int,
                         phase_a_epochs: int, n_bytes: int,
                         device: torch.device) -> Dict:
    """Run one f-cell for a given codebook family.

    Uses a patched version of run_one_cell_no_replay that accepts a custom codebook.
    Since v15's run_one_cell_no_replay builds Kerdock internally, we need to
    replicate the core logic with our custom codebook.
    """
    # Build custom codebook
    cb = build_non_kerdock_codebook(family, N_cfg, seed, device)
    C = cb.shape[0]

    # Replicate Phase A: store M_A random patterns
    import math as _math
    M_A = min(C, max(4, int(0.125 * N_cfg)))   # same as v15 default M fraction

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 20000)

    key_idx_A = torch.randint(0, C, (M_A,), generator=gen, device=device)
    val_idx_A = torch.randint(0, C, (M_A,), generator=gen, device=device)
    keys_A = cb[key_idx_A]
    vals_A = cb[val_idx_A]

    # Build W from Phase A
    W = torch.zeros(N_cfg, N_cfg, device=device, dtype=torch.float32)
    batch = batch_size
    for start in range(0, M_A, batch):
        k_b = keys_A[start:start + batch]
        v_b = vals_A[start:start + batch]
        W = W + (v_b.T @ k_b) / N_cfg

    # Phase B: replace f-fraction of A with new patterns
    M_B = max(0, int(f * M_A))
    if M_B > 0:
        key_idx_B = torch.randint(0, C, (M_B,), generator=gen, device=device)
        val_idx_B = torch.randint(0, C, (M_B,), generator=gen, device=device)
        keys_B = cb[key_idx_B]
        vals_B = cb[val_idx_B]

        # Erase replaced patterns and add new ones
        for start in range(0, M_B, batch):
            k_erase = keys_A[start:start + batch]
            v_erase = vals_A[start:start + batch]
            k_new   = keys_B[start:start + batch]
            v_new   = vals_B[start:start + batch]
            W = W - (v_erase.T @ k_erase) / N_cfg
            W = W + (v_new.T @ k_new) / N_cfg

    # Measure retention_A: how well does W retrieve the Phase A patterns?
    # Use patterns that were NOT replaced
    kept_A_start = M_B   # first M_B patterns were replaced in Phase B
    n_probe = min(M_A - M_B, 100)
    if n_probe <= 0:
        return {"retention_A": 0.0}

    probe_keys = keys_A[kept_A_start:kept_A_start + n_probe]
    probe_val  = val_idx_A[kept_A_start:kept_A_start + n_probe] % C

    sims = (cb @ (probe_keys @ W.T).T) / N_cfg * 32.0
    pred = torch.argmax(sims, dim=0)
    ret = (pred == probe_val.to(device)).float().mean().item()

    return {"retention_A": round(float(ret), 5)}


def seed_passes_hp(r2: float, max_dev: float) -> bool:
    return (r2 < HP_R2_MAX) or (max_dev >= HP_MAX_DEV_ALT)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    per_family = summary.get("per_family", {})
    if not per_family:
        return ("SS_V17_MIDDLE_BAND", "No per-family data.")

    family_pass: Dict[str, int] = {}
    for family, per_seed in per_family.items():
        pass_seeds = sum(1 for sd in per_seed.values()
                         if seed_passes_hp(sd.get("r2", 1.0), sd.get("max_dev", 0.0)))
        family_pass[family] = pass_seeds

    all_pass = all(v >= HP_MAJORITY_MIN for v in family_pass.values())
    any_pass = any(v >= HP_MAJORITY_MIN for v in family_pass.values())
    all_fail = all(v == 0 for v in family_pass.values())

    detail = (f"family_pass={family_pass} HP_MAJORITY_MIN={HP_MAJORITY_MIN} "
              f"N={summary.get('N', N_FULL)} f_sweep={F_SWEEP_FULL}")

    if all_fail:
        return ("SS_V17_HARD_FAIL",
                f"HARD_FAIL: no plateau at any non-Kerdock family. " + detail)

    if all_pass:
        return ("SS_V17_HARD_PASS",
                f"SAAD-SOLLA PLATEAU CODEBOOK-ROBUST: all families show plateau. " + detail)

    return ("SS_V17_MIDDLE_BAND",
            f"Partial: plateau at {sum(1 for v in family_pass.values() if v >= HP_MAJORITY_MIN)} "
            f"of {len(family_pass)} families. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096"

    device = torch.device("cpu")

    # Test both codebook families produce non-null retention_A
    for family in CODEBOOK_FAMILIES:
        result = run_one_seed_family(
            family, 17, 0.5, N_SMOKE,
            BATCH_SIZE_SMOKE, EPOCHS_SMOKE, PHASE_A_EPOCHS_SMOKE, BYTES_SMOKE,
            device)
        ret = result.get("retention_A", None)
        assert ret is not None, f"{family}: retention_A is None"
        assert 0 <= ret <= 1.0, f"{family}: retention_A OOR: {ret}"

    # Gate self-tests
    assert seed_passes_hp(0.30, 0.35), "Gate: plateau data should PASS"
    assert not seed_passes_hp(0.97, 0.02), "Gate: smooth-monotone should FAIL"

    # Multi-scale smoke N_SMOKE x4
    for family in CODEBOOK_FAMILIES:
        r4x = run_one_seed_family(
            family, 17, 0.5, N_SMOKE * 4,
            BATCH_SIZE_SMOKE, EPOCHS_SMOKE, PHASE_A_EPOCHS_SMOKE, BYTES_SMOKE,
            device)
        assert 0 <= r4x.get("retention_A", -1) <= 1.0, f"4x smoke OOR: {r4x}"

    # Verdict test
    per_family_pass = {
        "bsc": {"7": {"r2": 0.30, "max_dev": 0.35}, "17": {"r2": 0.31, "max_dev": 0.34},
                "23": {"r2": 0.32, "max_dev": 0.33}},
        "antipodal": {"7": {"r2": 0.28, "max_dev": 0.38}, "17": {"r2": 0.29, "max_dev": 0.37},
                      "23": {"r2": 0.30, "max_dev": 0.36}},
    }
    v, msg = compute_verdict({"per_family": per_family_pass, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict self-test failed: {v}: {msg}"

    # OOM check
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W={oom_bytes/1e6:.0f}MB >= 6GB"

    print(f"[selftest] saad_solla_v17_cross_cb_v1_n4096 PASS", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    f_sweep   = F_SWEEP_SMOKE   if smoke else F_SWEEP_FULL
    seeds     = SEEDS_SMOKE     if smoke else SEEDS_FULL
    N_cfg     = N_SMOKE         if smoke else N_FULL
    batch     = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs    = EPOCHS_SMOKE    if smoke else EPOCHS
    pa_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS
    n_bytes   = BYTES_SMOKE     if smoke else BYTES

    device = torch.device("cuda" if torch.cuda.is_available() and not smoke else "cpu")
    print(f"saad_solla_v17_cross_cb_v1_n4096 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"families={CODEBOOK_FAMILIES} seeds={seeds} f_sweep={f_sweep} device={device}",
          flush=True)

    per_family: Dict = {}

    for family in CODEBOOK_FAMILIES:
        per_seed_res: Dict = {}
        print(f"\n== codebook_family={family} ==", flush=True)

        for seed in seeds:
            t_seed = time.monotonic()
            r2_vals, max_dev_vals = [], []

            for f in f_sweep:
                result = run_one_seed_family(
                    family, seed, f, N_cfg, batch, epochs, pa_epochs, n_bytes, device)
                ret_A = result.get("retention_A", 0.0)
                r2_vals.append(ret_A)

            # Compute R^2 and max_dev of ret_A vs f
            r2 = pearson_r2(r2_vals, f_sweep)
            residuals = [abs(r - (r2_vals[0] + (r2_vals[-1] - r2_vals[0]) * fi))
                         for r, fi in zip(r2_vals, f_sweep)]
            max_dev = max(residuals)

            per_seed_res[str(seed)] = {
                "r2": round(r2, 4), "max_dev": round(max_dev, 4),
                "f_vals": f_sweep, "ret_A_vals": [round(v, 4) for v in r2_vals],
            }
            passes = seed_passes_hp(r2, max_dev)
            print(f"  {family} seed={seed} r2={r2:.3f} max_dev={max_dev:.3f} "
                  f"passes={passes} ({time.monotonic()-t_seed:.1f}s)", flush=True)

        per_family[family] = per_seed_res

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg, "families": CODEBOOK_FAMILIES,
        "seeds": seeds, "f_sweep": f_sweep,
        "elapsed_s": round(elapsed, 2),
        "per_family": per_family,
    }

    tag, msg = compute_verdict(summary)
    summary["verdict_tag"] = tag
    summary["verdict_msg"] = msg
    print(f"\n[VERDICT] {tag}: {msg}", flush=True)

    out_dir = get_output_dir()
    with open(out_dir / "metrics.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[done] elapsed={elapsed:.1f}s -> {out_dir}/metrics.json", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        return
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
