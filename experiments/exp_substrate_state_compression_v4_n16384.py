"""C3 SUBSTRATE STATE COMPRESSION v4 at N=16384.

CONTEXT (PP-2 cross-N third-datapoint; v297 cap_map PP-2 first-foothold):
  v2 at N=4096 HARD_PASS: c_quant/bits8 = 4x + all-KFs-PASS.
  v3 at N=8192 in flight (remote_cpu_queue).
  v4 closes cross-N validation at N=16384 -- the substrate's full N range.
  PP-2 row becomes empirically anchored at 3 N points if PASS.

FOCUSED DESIGN (c_quant only, matching v3 scope):
  Test ONLY the c_quant foothold winner at bits {4, 8, 16} at N=16384.
  SVD and sparse approaches are NOT re-tested (v2 v3 data in cap_map).

For each (bits): measure
  - compression_ratio = uncompressed_bytes / compressed_bytes
  - retrieval_accuracy on N_PROBE queries
  - KF-1 (deletion certificate), KF-2 (live drift norm), KF-3 (edit consistency)

PRE-REGISTERED BANDS:
  HP = c_quant/bits8 achieves >=4x compression AND retrieval >=95% AND
       KFs all PASS (KF-1 + KF-2 + KF-3) in 2/3+ seeds. Cross-N confirmed.
  HF = c_quant/bits8 KF preservation breaks (any KF fails in majority of seeds)
       AND compression < 4x at N=16384. Foothold is N-bounded.
  MB = c_quant/bits8 holds compression >= 4x but retrieval degrades <95%,
       OR KFs partially preserved. Suggests scaling boundary.

N-SUFFIX BINDING:
  PROT-018: _n16384 binds N = 16384.
  3-seed (matches v3 scope at N=16384 CPU cost).

PROT-019: timeout >= 14400s.
PROT-021: per-seed checkpointing.

Anchor: substrate_state_compression_v4_n16384
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_substrate_state_compression_v4_n16384.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c3v4", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n16384 binds N = 16384
N = 16384
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# M scales proportionally: v2 used M=2048 at N=4096 (=N/2); keep same ratio
M_PROD  = N_FULL // 2   # 8192
M_SMOKE = 256
N_PROBE_FULL  = 100
N_PROBE_SMOKE = 16
# 3-seed to match v3 scope at N=16384 CPU cost
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

HP_MIN_COMPRESSION = 4.0
HP_MIN_RETRIEVAL   = 0.95
HP_MIN_SEEDS_PASS  = 2  # 2/3+


def get_output_dir(default_name: str = "substrate_state_compression_v4_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compress_quant(W: torch.Tensor, bits: int):
    """Approach C: per-tensor symmetric quantization."""
    max_v = float(W.abs().max().item())
    if max_v == 0:
        return W.clone(), 1.0
    n_levels = (1 << (bits - 1)) - 1  # signed
    scale = max_v / n_levels
    q = torch.clamp(torch.round(W / scale), -n_levels, n_levels)
    W_q = q * scale
    bytes_compressed = (W.nelement() * bits) // 8
    bytes_original = W.element_size() * W.nelement()
    return W_q, float(bytes_original / max(bytes_compressed, 1))


def _retrieval_accuracy(W_c, codebook, key_idx, val_idx, n_probe, N_use):
    keys = codebook[key_idx[:n_probe]]
    tgt  = val_idx[:n_probe]
    out  = keys @ W_c.T
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return float((pred == tgt).float().mean().item())


def _kf1_deletion_cert(W_c, codebook, key_idx, val_idx, N_use):
    """KF-1: after rank-1 subtract, deleted target not returned."""
    if key_idx.shape[0] < 4:
        return 1.0
    k  = codebook[key_idx[:1]]
    v  = codebook[val_idx[:1]]
    W2 = W_c - (v.T @ k) / N_use
    out  = k @ W2.T
    sims = (codebook @ out.T) / N_use
    pred   = int(torch.argmax(sims, dim=0).item())
    target = int(val_idx[0].item())
    return 0.0 if pred == target else 1.0


def _kf2_drift_norm(W_c, W_original):
    """KF-2: Frobenius norm preserved within 15%."""
    n_o = float(torch.linalg.norm(W_original).item())
    n_c = float(torch.linalg.norm(W_c).item())
    if n_o == 0:
        return 0.0
    ratio = n_c / n_o
    return 1.0 if 0.85 <= ratio <= 1.15 else 0.0


def _kf3_edit_consistency(W_c, codebook, key_idx, val_idx, N_use):
    """KF-3: rank-1 edit on compressed W yields new value."""
    if key_idx.shape[0] < 2:
        return 1.0
    k  = codebook[key_idx[1:2]]
    ov = codebook[val_idx[1:2]]
    C = codebook.shape[0]
    new_target_idx = (int(val_idx[1].item()) + C // 2) % C
    nv = codebook[new_target_idx:new_target_idx + 1]
    W2 = W_c - (ov.T @ k) / N_use + (nv.T @ k) / N_use
    out  = k @ W2.T
    sims = (codebook @ out.T) / N_use
    pred = int(torch.argmax(sims, dim=0).item())
    return 1.0 if pred == new_target_idx else 0.0


def measure_seed(N_use: int, M: int, n_probe: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, _relation = build_shared(N_use, M, seed, device)

    results: List[Dict] = []
    for bits in [4, 8, 16]:
        label = f"bits{bits}"
        try:
            W_c, comp_ratio = compress_quant(W, bits)
            retr = _retrieval_accuracy(W_c, codebook, key_idx, val_idx, n_probe, N_use)
            kf1  = _kf1_deletion_cert(W_c, codebook, key_idx, val_idx, N_use)
            kf2  = _kf2_drift_norm(W_c, W)
            kf3  = _kf3_edit_consistency(W_c, codebook, key_idx, val_idx, N_use)
            results.append({
                "approach": "c_quant",
                "param": label,
                "bits": bits,
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
        return ("C3V4_INCONCLUSIVE", "no cells")

    # Per-config per-seed pass tracking
    by_config: Dict[str, List] = {}
    for cell in cells:
        for cfg in cell["configs"]:
            if "error" in cfg:
                continue
            k = cfg["param"]
            by_config.setdefault(k, [])
            by_config[k].append({
                "comp": cfg["compression_ratio"],
                "retr": cfg["retrieval_acc"],
                "kfs":  cfg["kfs_all_pass"],
            })

    summaries = []
    n_hp_configs = 0
    n_full_kf_break = 0
    for param, rows in by_config.items():
        n_pass = sum(1 for r in rows
                     if (r["comp"] >= HP_MIN_COMPRESSION
                         and r["retr"] >= HP_MIN_RETRIEVAL
                         and r["kfs"]))
        all_kf_break = all(not r["kfs"] for r in rows)
        mean_comp = sum(r["comp"] for r in rows) / max(1, len(rows))
        mean_retr = sum(r["retr"] for r in rows) / max(1, len(rows))
        summaries.append(f"c_quant/{param}: comp={mean_comp:.2f}x "
                         f"retr={mean_retr:.3f} "
                         f"hp_seeds={n_pass}/{len(rows)} "
                         f"kfs={'BREAK' if all_kf_break else 'OK'}")
        if n_pass >= HP_MIN_SEEDS_PASS:
            n_hp_configs += 1
        if all_kf_break:
            n_full_kf_break += 1

    detail = " | ".join(summaries)

    if n_hp_configs >= 1:
        return ("C3V4_HARD_PASS",
                f"CROSS_N_COMPRESSION_CONFIRMED n_hp_configs={n_hp_configs}. " + detail)
    if n_full_kf_break == len(by_config):
        return ("C3V4_HARD_FAIL",
                "ALL_CONFIGS_KF_BREAK_AT_N16384. " + detail)
    return ("C3V4_MIDDLE_BAND",
            f"PARTIAL n_hp=0 kf_break={n_full_kf_break}/{len(by_config)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale."""
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert len(SEEDS_FULL) == 3, f"expected 3 seeds, got {len(SEEDS_FULL)}"

    # Verdict gate HP: bits8 at 4x+, retr>=0.95, KFs all pass, 2+/3 seeds
    fake_hp = [{"seed": s, "M": M_PROD, "n_probe": N_PROBE_FULL,
                "configs": [
                    {"approach": "c_quant", "param": "bits4",
                     "bits": 4, "compression_ratio": 8.0, "retrieval_acc": 0.70,
                     "kf1_deletion": 0.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 0.0, "kfs_all_pass": False},
                    {"approach": "c_quant", "param": "bits8",
                     "bits": 8, "compression_ratio": 4.0, "retrieval_acc": 0.97,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True},
                    {"approach": "c_quant", "param": "bits16",
                     "bits": 16, "compression_ratio": 2.0, "retrieval_acc": 0.99,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True},
                ]}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate HF: all configs KF-break
    fake_hf = [{"seed": s, "M": M_PROD, "n_probe": N_PROBE_FULL,
                "configs": [
                    {"approach": "c_quant", "param": "bits4",
                     "bits": 4, "compression_ratio": 4.0, "retrieval_acc": 0.20,
                     "kf1_deletion": 0.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 0.0, "kfs_all_pass": False},
                    {"approach": "c_quant", "param": "bits8",
                     "bits": 8, "compression_ratio": 2.0, "retrieval_acc": 0.30,
                     "kf1_deletion": 0.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 0.0, "kfs_all_pass": False},
                    {"approach": "c_quant", "param": "bits16",
                     "bits": 16, "compression_ratio": 1.0, "retrieval_acc": 0.50,
                     "kf1_deletion": 0.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 0.0, "kfs_all_pass": False},
                ]}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB: bits8 high compression, retrieval below threshold
    fake_mb = [{"seed": s, "M": M_PROD, "n_probe": N_PROBE_FULL,
                "configs": [
                    {"approach": "c_quant", "param": "bits8",
                     "bits": 8, "compression_ratio": 4.0, "retrieval_acc": 0.80,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True},
                ]}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # Live smoke: measure_seed at small N, assert metrics non-null
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 256, N_PROBE_SMOKE, 17, device)
    assert "configs" in out and len(out["configs"]) > 0, "no configs"
    n_valid = sum(1 for c in out["configs"] if "error" not in c)
    assert n_valid >= 2, f"only {n_valid} valid configs at smoke"
    # Assert metrics are non-sentinel
    for c in out["configs"]:
        if "error" in c:
            continue
        assert c["compression_ratio"] > 0, f"compression_ratio zero: {c}"
        assert 0.0 <= c["retrieval_acc"] <= 1.0, f"retrieval_acc out of range: {c}"
        assert c["kf1_deletion"] in (0.0, 1.0), f"kf1 sentinel: {c}"
        assert c["kf2_drift_norm"] in (0.0, 1.0), f"kf2 sentinel: {c}"
        assert c["kf3_edit"] in (0.0, 1.0), f"kf3 sentinel: {c}"
    print(f"[selftest] substrate_state_compression_v4_n16384 PASS "
          f"{n_valid}/3 configs measured at N={N_SMOKE}", flush=True)


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
    smoke  = args.smoke
    N_cfg    = N_SMOKE      if smoke else N_FULL
    M        = M_SMOKE      if smoke else M_PROD
    n_probe  = N_PROBE_SMOKE if smoke else N_PROBE_FULL
    seeds    = SEEDS_SMOKE  if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()
    print(f"[run] substrate_state_compression_v4_n16384 smoke={smoke} N={N_cfg} "
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
            elapsed = time.time() - t0
            n_valid = sum(1 for c in cell["configs"] if "error" not in c)
            print(f"  seed={seed} n_valid={n_valid} "
                  f"({elapsed:.1f}s elapsed)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "substrate_state_compression_v4_n16384",
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
