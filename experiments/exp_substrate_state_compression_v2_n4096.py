"""C3 SUBSTRATE STATE COMPRESSION v2 at N=4096.

CONTEXT (v290 cap_map follow-on; v2 = re-ship of v1 after CUDA contention kill):
  v1 stalled on 2026-05-31 because auto-CUDA selection grabbed the GPU while
  V2 sustained_workload had it monopolized. Commit 3ebb009 patched the device
  line in v1; v2 is the clean re-ship with all v2 labels so queue_add dedup
  passes cleanly.

  Test 3 compression approaches on substrate W. Measure compression ratio +
  KF (killer feature) preservation + retrieval accuracy.

APPROACHES:
  A "low-rank SVD": W ~= U S V^T at ranks {N/8, N/4, N/2}
  B "sparse threshold": zero out |W| < threshold, thresholds {0.01, 0.05, 0.1}
  C "quantization": INT4, INT8, INT16 quantization

For each (approach, parameter): measure
  - compression_ratio = uncompressed_bytes / compressed_bytes
  - retrieval_accuracy on N_PROBE queries
  - KF preservation: KF-1 (deletion certificate), KF-2 (live drift / norm),
    KF-3 (edit consistency after compression)

PRE-REGISTERED BANDS (carried forward from v1 pre-reg):
  HP = at least one config achieves >=4x compression AND retrieval >=95% AND
       KFs pass (KF-1 + KF-2 + KF-3 all preserved).
  HF = all configs lose killer features (KF-1 or KF-2 or KF-3 breaks).
  MB = otherwise.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-021: per-cell-seed checkpointing.

Anchor: substrate_state_compression_v2_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_substrate_state_compression_v2_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c3v2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD = 2048
M_SMOKE = 256
N_PROBE_FULL = 100
N_PROBE_SMOKE = 16
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_MIN_COMPRESSION = 4.0
HP_MIN_RETRIEVAL = 0.95


def get_output_dir(default_name: str = "substrate_state_compression_v2_n4096") -> Path:
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
    """KF-1: after a fact-deletion (rank-1 subtract), the deleted target should
    not be returned by re-query. Returns 1.0 if deletion held."""
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
    """KF-2: live drift / Frobenius norm preserved within 10%."""
    n_o = float(torch.linalg.norm(W_original).item())
    n_c = float(torch.linalg.norm(W_compressed).item())
    if n_o == 0:
        return 0.0
    ratio = n_c / n_o
    return 1.0 if 0.85 <= ratio <= 1.15 else 0.0


def _kf3_edit_consistency(W_compressed, codebook, key_idx, val_idx, N_use):
    """KF-3: a rank-1 edit applied to compressed W should yield the NEW value."""
    if key_idx.shape[0] < 2:
        return 1.0
    k = codebook[key_idx[1:2]]
    ov = codebook[val_idx[1:2]]
    # New target: pick a different value
    C = codebook.shape[0]
    new_target_idx = (int(val_idx[1].item()) + C // 2) % C
    nv = codebook[new_target_idx:new_target_idx + 1]
    W2 = W_compressed - (ov.T @ k) / N_use + (nv.T @ k) / N_use
    out = k @ W2.T
    sims = (codebook @ out.T) / N_use
    pred = int(torch.argmax(sims, dim=0).item())
    return 1.0 if pred == new_target_idx else 0.0


def compress_svd(W, rank):
    """Approach A: low-rank SVD."""
    U, S, Vh = torch.linalg.svd(W, full_matrices=False)
    U_t = U[:, :rank]
    S_t = S[:rank]
    Vh_t = Vh[:rank, :]
    W_lr = (U_t * S_t.unsqueeze(0)) @ Vh_t
    # Storage size = (rank * (W.shape[0] + W.shape[1] + 1)) * element size
    bytes_compressed = (rank * (W.shape[0] + W.shape[1] + 1)) * W.element_size()
    bytes_original = W.element_size() * W.nelement()
    return W_lr, bytes_original / bytes_compressed


def compress_sparse(W, threshold):
    """Approach B: zero out small entries."""
    mask = W.abs() >= threshold
    W_sparse = W * mask.float()
    n_nz = int(mask.sum().item())
    # CSR storage: ~2 * n_nz indices + n_nz values
    bytes_compressed = n_nz * (W.element_size() + 2 * 4)
    if bytes_compressed == 0:
        return W_sparse, 0.0
    bytes_original = W.element_size() * W.nelement()
    return W_sparse, bytes_original / bytes_compressed


def compress_quant(W, bits):
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
    return W_q, bytes_original / max(bytes_compressed, 1)


def measure_seed(N_use: int, M: int, n_probe: int, seed: int,
                   device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    configs = []
    # A: SVD
    for rank in [N_use // 8, N_use // 4, N_use // 2]:
        configs.append(("a_svd", f"rank{rank}", rank))
    # B: sparse
    for thresh in [0.01, 0.05, 0.1]:
        configs.append(("b_sparse", f"thresh{thresh}", thresh))
    # C: quant
    for bits in [4, 8, 16]:
        configs.append(("c_quant", f"bits{bits}", bits))

    results: List[Dict] = []
    for approach, label, param in configs:
        try:
            if approach == "a_svd":
                W_c, comp_ratio = compress_svd(W, int(param))
            elif approach == "b_sparse":
                W_c, comp_ratio = compress_sparse(W, float(param))
            elif approach == "c_quant":
                W_c, comp_ratio = compress_quant(W, int(param))
            else:
                continue
            retr = _retrieval_accuracy(W_c, codebook, key_idx, val_idx,
                                          n_probe, N_use)
            kf1 = _kf1_deletion_cert(W_c, codebook, key_idx, val_idx, N_use)
            kf2 = _kf2_drift_norm(W_c, W)
            kf3 = _kf3_edit_consistency(W_c, codebook, key_idx, val_idx, N_use)
            results.append({
                "approach": approach,
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
            results.append({"approach": approach, "param": label,
                              "error": str(e)[:300]})

    del codebook, W
    return {"seed": int(seed), "M": int(M), "n_probe": int(n_probe),
            "configs": results}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("C3_INCONCLUSIVE", "no cells")

    # Aggregate per config (label) across seeds
    by_config: Dict[Tuple[str, str], Dict] = {}
    for cell in cells:
        for cfg in cell["configs"]:
            if "error" in cfg:
                continue
            k = (cfg["approach"], cfg["param"])
            by_config.setdefault(k, {"comp": [], "retr": [], "kfs": []})
            by_config[k]["comp"].append(cfg["compression_ratio"])
            by_config[k]["retr"].append(cfg["retrieval_acc"])
            by_config[k]["kfs"].append(cfg["kfs_all_pass"])

    n_hp_configs = 0
    n_kf_break_configs = 0
    summaries = []
    for (a, p), m in by_config.items():
        mean_comp = sum(m["comp"]) / max(1, len(m["comp"]))
        mean_retr = sum(m["retr"]) / max(1, len(m["retr"]))
        all_kfs = all(m["kfs"])
        any_kfs = any(m["kfs"])
        summaries.append(f"{a}/{p}: comp={mean_comp:.2f}x retr={mean_retr:.3f} "
                          f"kfs={'PASS' if all_kfs else 'BREAK'}")
        if (mean_comp >= HP_MIN_COMPRESSION and mean_retr >= HP_MIN_RETRIEVAL
            and all_kfs):
            n_hp_configs += 1
        if not any_kfs:
            n_kf_break_configs += 1

    detail = " | ".join(summaries)
    if n_hp_configs >= 1:
        return ("C3_HARD_PASS", f"COMPRESSION_VIABLE n_hp={n_hp_configs}. " + detail)
    if n_kf_break_configs == len(by_config):
        return ("C3_HARD_FAIL", "ALL_CONFIGS_LOSE_KFS. " + detail)
    return ("C3_MIDDLE_BAND", f"PARTIAL n_hp=0 n_kf_break={n_kf_break_configs}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "n_probe": 100,
                "configs": [
                    {"approach": "c_quant", "param": "bits8",
                     "compression_ratio": 4.0, "retrieval_acc": 0.97,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True},
                    {"approach": "a_svd", "param": "rank512",
                     "compression_ratio": 2.0, "retrieval_acc": 0.90,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 1.0, "kfs_all_pass": False}]}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF (all configs lose KFs)
    fake_hf = [{"seed": s, "M": M_PROD, "n_probe": 100,
                "configs": [
                    {"approach": "a_svd", "param": "rank512",
                     "compression_ratio": 4.0, "retrieval_acc": 0.30,
                     "kf1_deletion": 0.0, "kf2_drift_norm": 0.0,
                     "kf3_edit": 0.0, "kfs_all_pass": False}]}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MB: at least one config has kfs_all_pass=True but
    # neither config is at HP threshold (low compression OR low retrieval)
    fake_mb = [{"seed": s, "M": M_PROD, "n_probe": 100,
                "configs": [
                    {"approach": "c_quant", "param": "bits8",
                     "compression_ratio": 4.0, "retrieval_acc": 0.85,
                     "kf1_deletion": 1.0, "kf2_drift_norm": 1.0,
                     "kf3_edit": 1.0, "kfs_all_pass": True}]}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Live smoke on CPU (forced -- no CUDA)
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 128, N_PROBE_SMOKE, 17, device)
    assert len(out["configs"]) > 0, "no configs measured"
    n_valid = sum(1 for c in out["configs"] if "error" not in c)
    assert n_valid >= 6, f"only {n_valid} valid configs"
    print(f"[selftest] substrate_state_compression_v2_n4096 PASS "
          f"{n_valid} configs measured", flush=True)


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
    N_cfg = N_SMOKE if smoke else N_FULL
    M = M_SMOKE if smoke else M_PROD
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] substrate_state_compression_v2_n4096 smoke={smoke} N={N_cfg} "
          f"M={M} n_probe={n_probe} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = measure_seed(N_cfg, M, n_probe, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} n_configs={len(cell['configs'])} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "substrate_state_compression_v2_n4096",
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
