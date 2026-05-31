"""C3 SUBSTRATE STATE COMPRESSION v3 at N=8192.

CONTEXT (v295 cap_map cross-N validation of PP-2 first-foothold):
  v2 at N=4096 HARD_PASS'd: c_quant/bits8 achieved 4x compression + retrieval
  >= 95% + KF-1/KF-2/KF-3 all PASS across 5 seeds. Cap_map v295 added PP-2
  first-foothold annotation.
  v3 asks: does c_quant/bits8 hold at N=8192? Cross-N validation is the natural
  strengthener for a first-foothold -- one data point at one N is a hint;
  two N values is the start of a pattern.

FOCUSED DESIGN (c_quant only):
  We test ONLY the c_quant foothold winner at bits {4, 8, 16} at N=8192.
  SVD and sparse approaches are NOT re-tested (v2 data is already in cap_map;
  the cross-N question is specifically about quantization holding).

For each (bits): measure
  - compression_ratio = uncompressed_bytes / compressed_bytes
  - retrieval_accuracy on N_PROBE queries
  - KF-1 (deletion certificate), KF-2 (live drift norm), KF-3 (edit consistency)

PRE-REGISTERED BANDS:
  HP = c_quant/bits8 achieves >=4x compression AND retrieval >=95% AND
       KFs all PASS (KF-1 + KF-2 + KF-3) in 4/5+ seeds. Cross-N confirmed.
  HF = c_quant/bits8 KF preservation breaks (any KF fails in majority of seeds)
       AND compression < 4x. Foothold is N-specific.
  MB = c_quant/bits8 holds compression >= 4x but retrieval degrades <95% at N=8192,
       OR KFs partially preserved. Suggests scaling boundary.

PROT-018: _n8192 binds N = 8192.
PROT-019: timeout >= 14400s.
PROT-021: per-seed checkpointing.

Anchor: substrate_state_compression_v3_n8192
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_substrate_state_compression_v3_n8192.md
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c3v3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n8192 binds N = 8192
N = 8192
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# M scales proportionally: v2 used M=2048 at N=4096 (=N/2); keep same ratio
M_PROD  = N_FULL // 2   # 4096
M_SMOKE = 256
N_PROBE_FULL  = 100
N_PROBE_SMOKE = 16
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_MIN_COMPRESSION = 4.0
HP_MIN_RETRIEVAL   = 0.95

# c_quant only -- bits grid
BITS_GRID = [4, 8, 16]


def get_output_dir(default_name: str = "substrate_state_compression_v3_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _retrieval_accuracy(W_compressed, codebook, key_idx, val_idx, n_probe, N_use):
    keys = codebook[key_idx[:n_probe]]
    tgt = val_idx[:n_probe]
    out = keys @ W_compressed.T
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return float((pred == tgt).float().mean().item())


def _kf1_deletion_cert(W_compressed, codebook, key_idx, val_idx, N_use):
    """KF-1: rank-1 delete; deleted target no longer retrieved."""
    if key_idx.shape[0] < 4:
        return 1.0
    k = codebook[key_idx[:1]]
    v = codebook[val_idx[:1]]
    W2 = W_compressed - (v.T @ k) / N_use
    out = k @ W2.T
    sims = (codebook @ out.T) / N_use
    pred = int(torch.argmax(sims, dim=0).item())
    target = int(val_idx[0].item())
    return 0.0 if pred == target else 1.0


def _kf2_drift_norm(W_compressed, W_original):
    """KF-2: Frobenius norm ratio within 15% of original."""
    n_o = float(torch.linalg.norm(W_original).item())
    n_c = float(torch.linalg.norm(W_compressed).item())
    if n_o == 0:
        return 0.0
    ratio = n_c / n_o
    return 1.0 if 0.85 <= ratio <= 1.15 else 0.0


def _kf3_edit_consistency(W_compressed, codebook, key_idx, val_idx, N_use):
    """KF-3: rank-1 edit on compressed W yields the new value."""
    if key_idx.shape[0] < 2:
        return 1.0
    k = codebook[key_idx[1:2]]
    ov = codebook[val_idx[1:2]]
    C = codebook.shape[0]
    new_target_idx = (int(val_idx[1].item()) + C // 2) % C
    nv = codebook[new_target_idx:new_target_idx + 1]
    W2 = W_compressed - (ov.T @ k) / N_use + (nv.T @ k) / N_use
    out = k @ W2.T
    sims = (codebook @ out.T) / N_use
    pred = int(torch.argmax(sims, dim=0).item())
    return 1.0 if pred == new_target_idx else 0.0


def compress_quant(W, bits):
    """Per-tensor symmetric quantization."""
    max_v = float(W.abs().max().item())
    if max_v == 0:
        return W.clone(), 1.0
    n_levels = (1 << (bits - 1)) - 1  # signed
    scale = max_v / n_levels
    q = torch.clamp(torch.round(W / scale), -n_levels, n_levels)
    W_q = q * scale
    bytes_compressed = (W.nelement() * bits) // 8
    bytes_original = W.element_size() * W.nelement()
    return W_q, bytes_original / max(bytes_compressed, 1)


def measure_seed(N_use: int, M: int, n_probe: int, seed: int,
                   device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    results: List[Dict] = []
    for bits in BITS_GRID:
        label = f"bits{bits}"
        try:
            W_c, comp_ratio = compress_quant(W, bits)
            retr = _retrieval_accuracy(W_c, codebook, key_idx, val_idx, n_probe, N_use)
            kf1 = _kf1_deletion_cert(W_c, codebook, key_idx, val_idx, N_use)
            kf2 = _kf2_drift_norm(W_c, W)
            kf3 = _kf3_edit_consistency(W_c, codebook, key_idx, val_idx, N_use)
            results.append({
                "approach": "c_quant",
                "param": label,
                "compression_ratio": round(float(comp_ratio), 4),
                "retrieval_acc": round(retr, 5),
                "kf1_deletion": round(kf1, 4),
                "kf2_drift_norm": round(kf2, 4),
                "kf3_edit": round(kf3, 4),
                "kfs_all_pass": bool(kf1 >= 1.0 and kf2 >= 1.0 and kf3 >= 1.0),
            })
            del W_c
        except Exception as e:  # noqa: BLE001
            results.append({"approach": "c_quant", "param": label,
                              "error": str(e)[:300]})

    del codebook, W
    return {"seed": int(seed), "M": int(M), "n_probe": int(n_probe),
            "configs": results}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("C3V3_INCONCLUSIVE", "no cells")

    # Focus on bits8 as the primary foothold config
    bits8_pass_count = 0   # seeds where bits8 achieves HP criteria
    bits8_kf_break   = 0   # seeds where bits8 breaks KFs
    bits8_cells = 0
    summaries = []

    for cell in cells:
        for cfg in cell["configs"]:
            if "error" in cfg:
                summaries.append(f"bits{cfg.get('param','?')}: ERROR {cfg['error'][:60]}")
                continue
            p = cfg["param"]
            comp = cfg["compression_ratio"]
            retr = cfg["retrieval_acc"]
            kfs  = cfg["kfs_all_pass"]
            summaries.append(
                f"{p}: comp={comp:.2f}x retr={retr:.3f} "
                f"kfs={'PASS' if kfs else 'BREAK'}")
            if p == "bits8":
                bits8_cells += 1
                if comp >= HP_MIN_COMPRESSION and retr >= HP_MIN_RETRIEVAL and kfs:
                    bits8_pass_count += 1
                if not kfs:
                    bits8_kf_break += 1

    detail = " | ".join(summaries)
    n_seeds = len(cells)
    hp_threshold = max(4, (n_seeds * 4 + 4) // 5)   # 4/5 majority

    if bits8_pass_count >= hp_threshold:
        return ("C3V3_HARD_PASS",
                f"CROSS_N_CONFIRMED bits8_pass={bits8_pass_count}/{bits8_cells} "
                f"N={N_FULL}. " + detail)

    # HF: bits8 breaks KFs in majority of seeds AND compression fails
    bits8_comp_fail = sum(
        1 for cell in cells for cfg in cell["configs"]
        if cfg.get("param") == "bits8" and "error" not in cfg
        and cfg["compression_ratio"] < HP_MIN_COMPRESSION
    )
    if bits8_kf_break >= hp_threshold and bits8_comp_fail >= hp_threshold:
        return ("C3V3_HARD_FAIL",
                f"BITS8_KF_BREAK kf_break={bits8_kf_break} comp_fail={bits8_comp_fail}. "
                + detail)

    return ("C3V3_MIDDLE_BAND",
            f"PARTIAL bits8_pass={bits8_pass_count}/{bits8_cells} N={N_FULL}. "
            + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, "PROT-018: _n8192"
    assert len(SEEDS_FULL) == 5
    assert BITS_GRID == [4, 8, 16]

    # Verdict gate HP (4+/5 seeds bits8 at full HP criteria)
    fake_hp_cells = [{"seed": s, "M": M_PROD, "n_probe": 100,
                "configs": [
                    {"approach": "c_quant", "param": "bits8",
                     "compression_ratio": 4.0, "retrieval_acc": 0.97,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True},
                    {"approach": "c_quant", "param": "bits4",
                     "compression_ratio": 8.0, "retrieval_acc": 0.60,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 1.0, "kfs_all_pass": False},
                    {"approach": "c_quant", "param": "bits16",
                     "compression_ratio": 2.0, "retrieval_acc": 0.99,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True},
                ]} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp_cells)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # Verdict gate HF (bits8 breaks KFs + fails compression in 4/5)
    fake_hf_cells = [{"seed": s, "M": M_PROD, "n_probe": 100,
                "configs": [
                    {"approach": "c_quant", "param": "bits8",
                     "compression_ratio": 1.5, "retrieval_acc": 0.30,
                     "kf1_deletion": 0.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 0.0, "kfs_all_pass": False}
                ]} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf_cells)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # Verdict gate MB (bits8 passes comp but retrieval < 95%)
    fake_mb_cells = [{"seed": s, "M": M_PROD, "n_probe": 100,
                "configs": [
                    {"approach": "c_quant", "param": "bits8",
                     "compression_ratio": 4.0, "retrieval_acc": 0.85,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True}
                ]} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb_cells)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v}"

    # Live smoke on CPU (forced -- no CUDA)
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, N_PROBE_SMOKE, 17, device)
    assert len(out["configs"]) > 0, "no configs measured"
    n_valid = sum(1 for c in out["configs"] if "error" not in c)
    assert n_valid >= len(BITS_GRID), \
        f"expected {len(BITS_GRID)} valid quant configs, got {n_valid}"
    # Verify bits8 is non-null
    bits8 = next((c for c in out["configs"] if c.get("param") == "bits8"), None)
    assert bits8 is not None and "error" not in bits8, "bits8 config missing or errored"
    assert bits8["compression_ratio"] > 0.0, "bits8 compression_ratio is zero"
    assert bits8["retrieval_acc"] is not None, "bits8 retrieval_acc is None"
    print(f"[selftest] substrate_state_compression_v3_n8192 PASS "
          f"bits8: comp={bits8['compression_ratio']:.2f}x "
          f"retr={bits8['retrieval_acc']:.3f} kfs={bits8['kfs_all_pass']}",
          flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    # PROT: force CPU -- this anchor lives in remote_cpu_queue; must never touch CUDA
    device = torch.device("cpu")
    smoke = args.smoke
    N_cfg  = N_SMOKE if smoke else N_FULL
    M      = M_SMOKE if smoke else M_PROD
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] substrate_state_compression_v3_n8192 smoke={smoke} N={N_cfg} "
          f"M={M} n_probe={n_probe} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
        try:
            cell = measure_seed(N_cfg, M, n_probe, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            # Print per-config summary for this seed
            for cfg in cell["configs"]:
                if "error" not in cfg:
                    print(f"  seed={seed} {cfg['param']}: "
                          f"comp={cfg['compression_ratio']:.2f}x "
                          f"retr={cfg['retrieval_acc']:.3f} "
                          f"kfs={cfg['kfs_all_pass']} "
                          f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "substrate_state_compression_v3_n8192",
               "N": N_cfg, "smoke": smoke, "M": M, "n_probe": n_probe,
               "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
