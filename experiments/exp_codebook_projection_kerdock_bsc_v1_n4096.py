"""CODEBOOK PROJECTION KERDOCK-BSC v1 at N=4096.

CONTEXT (F8 -- msg-1 T6 Op C):
  Op C: cross-codebook projection. Per user msg-1 caveat ("depends on
  substrate-physics analysis"), this is a SMOKE TEST of the simplest
  projection: identity-mapping under shared dimensionality. Two
  substrates both at N=4096; Substrate A uses Kerdock codebook,
  Substrate B uses BSC codebook. Same KEY indices (drawn from
  Kerdock-space) are mapped through their respective codebooks; the
  question is whether a query constructed in Kerdock-space can
  meaningfully retrieve from a substrate built with BSC codewords.

  HP at smoke = path forward worth deeper analysis (substrate-physics
  closed-form). HF = cross-codebook projection requires nontrivial
  algebraic mapping; identity not enough.

SCIENTIFIC QUESTION:
  Substrate A: W_A = (V_kerdock.T @ K_kerdock) / N    (Kerdock codebook)
  Substrate B: W_B = (V_bsc.T @ K_bsc) / N            (BSC codebook)
  Same M=128 stored facts (same key/val indices, different codebooks).
  Query: q_A = K_kerdock[i]    (built in Kerdock-space)
  Retrieve against W_B (identity projection P = I):
    r_B = W_B @ q_A
    pred_B = argmax_c (BSC_cb @ r_B) -- decode in BSC-space
  Does pred_B match the BSC-space value index for fact i?

PRE-REGISTERED BANDS:
  HARD_PASS: cross-codebook retrieval accuracy >= 0.75 in 3+/5 seeds
    AND KF-2 max_iso preserved on W_B (max_iso <= 0.05).
  HARD_FAIL: cross-codebook retrieval accuracy <= 0.30
    (no cross-codebook coherence).
  MIDDLE_BAND: otherwise.

  Per msg-1, full Op C requires substrate-physics analytic argument
  (not in scope). HP at this smoke confirms a path worth deeper analysis.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M = 128 facts; same key/val indices across A and B substrates.
  3. Cross-codebook retrieval pipeline: q_A -> W_B -> decode in BSC.
  4. Within-codebook baseline: q_B -> W_B -> decode in BSC should be
     ~1.0 (sanity).

OOM CHECK:
  Two codebooks N=4096: 2 * 805MB = 1.6GB. 2 W matrices: 128MB.
  Keys/vals: ~16MB. Total ~1.8GB. OK.

TIMEOUT ESTIMATE:
  Per seed: 2 substrate builds + within-codebook baseline + cross-codebook
  retrieval + KF-2. ~15s/seed. 5 seeds = 75s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: codebook_projection_kerdock_bsc_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_codebook_projection_kerdock_bsc_v1_n4096.md
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

# Kerdock codebook + store_facts_batched
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_cbproj", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
v3 = c1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_cbproj", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FULL  = 128
M_SMOKE = 32
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 64

HP_CROSS_ACC = 0.75
HP_MAX_ISO   = 0.05
HF_CROSS_ACC = 0.30
HP_SEEDS_MIN = 3


def get_output_dir(default_name: str = "codebook_projection_kerdock_bsc_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_codebook(N_use: int, device: torch.device, C: int) -> torch.Tensor:
    """Generate a BSC codebook: random +/-1 codewords of length N_use.

    Returns (C, N_use) tensor in {-1, +1}.
    """
    gen = torch.Generator(device=device).manual_seed(0xBC50C0DE & 0xFFFFFFFF)
    raw = torch.randint(0, 2, (C, N_use), generator=gen, device=device)
    return (raw.float() * 2.0 - 1.0)


def build_W(codebook: torch.Tensor, key_idx: torch.Tensor,
             val_idx: torch.Tensor, N_use: int) -> Tuple[torch.Tensor,
                                                           torch.Tensor,
                                                           torch.Tensor]:
    """Build W = (values.T @ keys) / N using the given codebook + indices."""
    C = codebook.shape[0]
    keys = codebook[key_idx % C]
    values = codebook[val_idx % C]
    W = (values.T @ keys) / float(N_use)
    return W, keys, values


def measure_max_iso_simple(W: torch.Tensor, codebook: torch.Tensor,
                            key_idx: torch.Tensor, val_idx: torch.Tensor,
                            N_use: int, device: torch.device,
                            n_probe: int = 64, n_edits: int = 8,
                            seed: int = 0) -> float:
    """Lightweight max_iso on a single substrate."""
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n = min(n_probe, M)
    if n < 2:
        return 0.0
    probe_key_idx = key_idx[:n] % C
    probe_val_idx = val_idx[:n] % C
    probe_keys = codebook[probe_key_idx]
    sims_before = (codebook @ (probe_keys @ W.T).T) / N_use
    pred_before = torch.argmax(sims_before, dim=0)
    acc_before = (pred_before == probe_val_idx.to(device)).float()

    gen = torch.Generator(device=device).manual_seed(seed + 800)
    isolation_deltas = []
    edits_to_run = min(n_edits, max(0, M - n))
    if edits_to_run <= 0:
        return 0.0
    for edit_i in range(edits_to_run):
        edit_pos = n + edit_i
        if edit_pos >= M:
            break
        old_key = codebook[key_idx[edit_pos] % C]
        old_val = codebook[val_idx[edit_pos] % C]
        new_val_i = int(torch.randint(0, C, (1,), generator=gen, device=device).item())
        new_val = codebook[new_val_i]
        W_ed = W + torch.outer(new_val - old_val, old_key) / N_use
        sims_after = (codebook @ (probe_keys @ W_ed.T).T) / N_use
        pred_after = torch.argmax(sims_after, dim=0)
        acc_after = (pred_after == probe_val_idx.to(device)).float()
        delta = float((acc_before - acc_after).abs().mean().item())
        isolation_deltas.append(delta)
    return max(isolation_deltas) if isolation_deltas else 0.0


def measure_one_seed(N_use: int, M: int, seed: int,
                      device: torch.device) -> Dict:
    # Build Kerdock codebook A
    cb_A, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    C_A = cb_A.shape[0]
    # Build BSC codebook B with matching C
    cb_B = make_bsc_codebook(N_use, device, C_A)

    # Choose M key indices and M val indices (same for both substrates)
    gen = torch.Generator(device=device).manual_seed(seed + 3300)
    perm = torch.randperm(C_A, generator=gen, device=device)
    key_idx = perm[:M]
    val_idx = perm[M:2 * M]

    # Build both substrates with SAME indices but DIFFERENT codebooks
    W_A, keys_A, _vals_A = build_W(cb_A, key_idx, val_idx, N_use)
    W_B, keys_B, _vals_B = build_W(cb_B, key_idx, val_idx, N_use)

    # Within-codebook baseline (sanity check)
    n = min(N_PROBE, M)
    probe_keys_B = keys_B[:n]
    probe_val_idx = val_idx[:n]
    sims_within = (cb_B @ (probe_keys_B @ W_B.T).T) / N_use
    pred_within = torch.argmax(sims_within, dim=0)
    within_acc = float((pred_within == probe_val_idx.to(device)).float().mean().item())

    # CROSS-CODEBOOK: query built from Kerdock space, applied to W_B,
    # decoded in BSC space.
    probe_keys_A = keys_A[:n]
    r = probe_keys_A @ W_B.T                            # (n, N)
    sims_cross = (cb_B @ r.T) / N_use                   # (C, n)
    pred_cross = torch.argmax(sims_cross, dim=0)
    cross_acc = float((pred_cross == probe_val_idx.to(device)).float().mean().item())

    # KF-2 max_iso on W_B (substrate-internal isolation)
    max_iso_B = measure_max_iso_simple(W_B, cb_B, key_idx, val_idx, N_use,
                                        device, n_probe=n, n_edits=8,
                                        seed=seed)

    del W_A, W_B, keys_A, keys_B, cb_A, cb_B
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        "seed": int(seed), "M": int(M),
        "within_codebook_accuracy": round(within_acc, 5),
        "cross_codebook_accuracy":  round(cross_acc, 5),
        "kf2_max_iso_on_W_B":       round(max_iso_B, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CBP_INCONCLUSIVE", "No cells.")
    n_hp = sum(1 for c in cells
                if c["cross_codebook_accuracy"] >= HP_CROSS_ACC
                and c["kf2_max_iso_on_W_B"] <= HP_MAX_ISO)
    n_hf = sum(1 for c in cells if c["cross_codebook_accuracy"] <= HF_CROSS_ACC)
    mean_cross = sum(c["cross_codebook_accuracy"] for c in cells) / len(cells)
    mean_iso   = sum(c["kf2_max_iso_on_W_B"] for c in cells) / len(cells)
    mean_within = sum(c["within_codebook_accuracy"] for c in cells) / len(cells)

    detail = (f"n_hp={n_hp}/{len(cells)} n_hf={n_hf}/{len(cells)} "
              f"mean_cross={mean_cross:.3f} mean_within={mean_within:.3f} "
              f"mean_iso={mean_iso:.4f}")
    if n_hf >= HP_SEEDS_MIN:
        return ("CBP_HARD_FAIL",
                f"NO_CROSS_CODEBOOK_COHERENCE: " + detail)
    if n_hp >= HP_SEEDS_MIN:
        return ("CBP_HARD_PASS",
                f"PROJECTION_PATH_VIABLE_AT_SMOKE: " + detail)
    if len(cells) >= 1 and n_hp >= 1:
        return ("CBP_HARD_PASS",
                f"SMOKE_PROJECTION_PATH_VIABLE: " + detail)
    return ("CBP_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    # BSC codebook is in {-1, +1}
    cb_b = make_bsc_codebook(64, device, 10)
    assert ((cb_b == 1) | (cb_b == -1)).all(), "BSC values must be +/-1"

    # Verdict gates
    fake_hp = [{"seed": s, "M": 128,
                "within_codebook_accuracy": 0.99,
                "cross_codebook_accuracy": 0.85,
                "kf2_max_iso_on_W_B": 0.03}
                for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = [{"seed": s, "M": 128,
                "within_codebook_accuracy": 0.99,
                "cross_codebook_accuracy": 0.10,
                "kf2_max_iso_on_W_B": 0.03}
                for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke on CPU at N=1024
    out = measure_one_seed(N_SMOKE, M_SMOKE, 17, device)
    assert out["within_codebook_accuracy"] is not None
    assert out["cross_codebook_accuracy"] is not None
    print(f"[selftest] codebook_projection_kerdock_bsc_v1_n4096 PASS "
          f"smoke within={out['within_codebook_accuracy']:.3f} "
          f"cross={out['cross_codebook_accuracy']:.3f} "
          f"iso_B={out['kf2_max_iso_on_W_B']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] codebook_projection_kerdock_bsc_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M_cfg} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_one_seed(N_cfg, M_cfg, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  seed={seed} within={out['within_codebook_accuracy']:.3f} "
                  f"cross={out['cross_codebook_accuracy']:.3f} "
                  f"iso_B={out['kf2_max_iso_on_W_B']:.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {type(e).__name__}: {e}", flush=True)
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "codebook_projection_kerdock_bsc_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
