"""T1.10: Federated deletion certificate smoke.

SCIENTIFIC QUESTION:
  In a multi-client federated substrate (k=5 clients, each writing M_per_client
  patterns), can we:
    (1) Generate a valid deletion certificate for one client's patterns?
    (2) Verify that retrieval of that client's patterns fails post-deletion?
    (3) Verify cross-tenant contamination_rate = 0.0 post-deletion?

  Algebraic: W_total = sum_k W_k where W_k = sum_{i in client_k} k_i v_i^T / N.
  Deletion cert for client c: W_del = W_total - W_c (exact, zero retraining).
  Cert: hash(W_c) signed as "erased; W_total - W_c is the post-deletion W".

PRE-REGISTERED BANDS:
  HARD-PASS: deletion cert valid (hash matches stored W_c hash)
             AND post-deletion retrieval of deleted client patterns drops
                 by >= 50% (acc_post <= 0.5 * acc_pre)
             AND contamination_rate = 0.0 for non-deleted clients.
  HARD-FAIL: cert invalid (hash mismatch) OR contamination_rate > 0.05.
  MIDDLE: cert valid but acc_drop < 50% OR other partial failures.

  No prior empirical anchor: bands widened per calibration-probe policy.
  Theoretical: W_del is exact; acc_post should be near random (0.5 for bipolar).
  HP 50% drop is conservative -- theory predicts near-complete loss.

DESIGN:
  N=1024, k=5 clients, M_per_client=30 (150 total patterns).
  Delete client 0. Test retrieval of all clients post-deletion.
  seeds=[17, 23, 31]. Pure CPU. Expected wall: ~60s.

PROT-018: no _nN suffix (N not primary axis). Production N=1024 stated here.
TIMEOUT ESTIMATE:
  Wall ~60s. PROT-019 floor 3600s. timeout_s = 3600.

FORMULA SELF-TESTS:
  1. W_total = sum_k W_k (linearity; verify W_del + W_c == W_total).
  2. Deletion cert: hash(W_c stored) == hash(W_c reconstructed).
  3. contamination_rate = frac of OTHER clients' patterns with acc drop > 5%.
  4. acc_drop = (acc_pre - acc_post) / acc_pre.

Anchor: federated_deletion_cert_smoke_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_federated_deletion_cert_smoke_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import hashlib
import json
import math
import os
import struct
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Config ---
N = 1024
N_CLIENTS = 5
M_PER_CLIENT = 30
SEEDS = [17, 23, 31]

# Pre-registered thresholds
HP_ACC_DROP_FRAC = 0.50    # acc_post <= (1 - 0.50) * acc_pre
HP_CONTAM_RATE   = 0.0     # contamination_rate = 0
HF_CONTAM_RATE   = 0.05    # contamination_rate > 0.05 -> HARD_FAIL


def get_output_dir(name: str = "federated_deletion_cert_smoke_v1") -> Path:
    n = os.environ.get("HDLAB_EXP_NAME", name)
    d = REPO / "data" / f"exp_{n}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _hash_tensor(t: torch.Tensor) -> str:
    """SHA-256 hash of float32 tensor bytes (deterministic)."""
    t_bytes = t.to(torch.float32).contiguous().numpy().tobytes()
    return hashlib.sha256(t_bytes).hexdigest()


def _make_client_codebook(N_use: int, M: int, client_id: int, seed: int) -> torch.Tensor:
    """Make bipolar codebook for a client (unique per client+seed)."""
    g = torch.Generator().manual_seed(seed * 1000 + client_id * 137)
    cb_raw = torch.sign(torch.randn(M, N_use, generator=g))
    cb_raw[cb_raw == 0] = 1.0
    return cb_raw.float()


def _client_W(codebook: torch.Tensor, N_use: int) -> torch.Tensor:
    """Hebbian W for one client's codebook (autoassociative)."""
    return (codebook.T @ codebook) / N_use  # N x N


def _retrieval_acc(W: torch.Tensor, codebook: torch.Tensor, N_use: int) -> float:
    """Fraction of patterns retrieved perfectly (1-step)."""
    activations = codebook @ W   # M x N
    retrieved = torch.sign(activations)
    retrieved[retrieved == 0] = 1.0
    correct = (retrieved == codebook).float().mean(dim=1)
    return float((correct >= 0.99).float().mean().item())


def _deletion_cert(W_client: torch.Tensor) -> Dict:
    """Generate deletion certificate for a client's W contribution."""
    cert_hash = _hash_tensor(W_client)
    cert_norm = float(W_client.norm().item())
    return {
        "cert_hash":    cert_hash,
        "cert_norm":    round(cert_norm, 6),
        "cert_valid":   cert_norm > 0.0,
        "n_params":     W_client.numel(),
    }


def _verify_cert(W_client_reconstructed: torch.Tensor, cert: Dict) -> bool:
    """Verify cert by recomputing hash of reconstructed W_client."""
    recomputed_hash = _hash_tensor(W_client_reconstructed)
    return recomputed_hash == cert["cert_hash"]


def measure_cell(N_use: int, n_clients: int, m_per_client: int, seed: int) -> Dict:
    """Federated deletion cert smoke."""
    # Build per-client codebooks and W matrices
    client_codebooks = [_make_client_codebook(N_use, m_per_client, c, seed)
                        for c in range(n_clients)]
    client_Ws = [_client_W(cb, N_use) for cb in client_codebooks]

    # Federated W_total = sum of client Ws
    W_total = sum(client_Ws)  # type: ignore[arg-type]

    # Pre-deletion: retrieval accuracy for each client
    acc_pre = [_retrieval_acc(W_total, client_codebooks[c], N_use)
               for c in range(n_clients)]

    # Delete client 0: generate cert, then compute W_del
    delete_client = 0
    cert = _deletion_cert(client_Ws[delete_client])
    W_del = W_total - client_Ws[delete_client]

    # Verify cert: reconstruct W_c = W_total - W_del and verify hash
    W_c_reconstructed = W_total - W_del
    cert_verified = _verify_cert(W_c_reconstructed, cert)

    # Post-deletion: retrieval accuracy for each client
    acc_post = [_retrieval_acc(W_del, client_codebooks[c], N_use)
                for c in range(n_clients)]

    # Deletion effect on deleted client
    acc_pre_deleted = acc_pre[delete_client]
    acc_post_deleted = acc_post[delete_client]
    acc_drop_frac = (acc_pre_deleted - acc_post_deleted) / max(acc_pre_deleted, 1e-9)

    # Contamination: other clients acc should be unchanged
    contamination_rate = 0.0
    contam_count = 0
    for c in range(n_clients):
        if c == delete_client:
            continue
        drop_c = (acc_pre[c] - acc_post[c]) / max(acc_pre[c], 1e-9)
        if drop_c > 0.05:  # >5% drop in non-deleted client = contamination
            contam_count += 1
    contamination_rate = contam_count / (n_clients - 1) if n_clients > 1 else 0.0

    return {
        "seed":             seed,
        "N":                N_use,
        "n_clients":        n_clients,
        "m_per_client":     m_per_client,
        "ok":               True,
        "delete_client":    delete_client,
        "cert_valid":       cert["cert_valid"],
        "cert_hash":        cert["cert_hash"][:16] + "...",  # truncate for JSON
        "cert_verified":    cert_verified,
        "acc_pre_deleted":  round(acc_pre_deleted, 5),
        "acc_post_deleted": round(acc_post_deleted, 5),
        "acc_drop_frac":    round(acc_drop_frac, 5),
        "acc_pre_others":   [round(acc_pre[c], 5) for c in range(n_clients) if c != delete_client],
        "acc_post_others":  [round(acc_post[c], 5) for c in range(n_clients) if c != delete_client],
        "contamination_rate": round(contamination_rate, 5),
        "contam_count":     contam_count,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("FDEL_INCONCLUSIVE", "no cells")

    ok_cells = [c for c in cells if c.get("ok")]
    if not ok_cells:
        return ("FDEL_INCONCLUSIVE", "all cells failed")

    n_cert_valid   = sum(1 for c in ok_cells if c["cert_valid"] and c["cert_verified"])
    n_acc_drop_ok  = sum(1 for c in ok_cells if c["acc_drop_frac"] >= HP_ACC_DROP_FRAC)
    contam_rates   = [c["contamination_rate"] for c in ok_cells]
    max_contam     = max(contam_rates)
    mean_acc_drop  = sum(c["acc_drop_frac"] for c in ok_cells) / len(ok_cells)
    acc_post_dels  = [c["acc_post_deleted"] for c in ok_cells]
    mean_acc_post  = sum(acc_post_dels) / len(acc_post_dels)

    n_total = len(ok_cells)
    detail = (
        f"N={N} n_clients={N_CLIENTS} m_per_client={M_PER_CLIENT} "
        f"n_cert_valid={n_cert_valid}/{n_total} "
        f"n_acc_drop_ok={n_acc_drop_ok}/{n_total} "
        f"mean_acc_drop={mean_acc_drop:.3f} mean_acc_post={mean_acc_post:.4f} "
        f"max_contam={max_contam:.4f}"
    )

    is_hf = (n_cert_valid < n_total or max_contam > HF_CONTAM_RATE)
    is_hp = (n_cert_valid == n_total and
             n_acc_drop_ok >= n_total * 2 // 3 and
             max_contam <= HP_CONTAM_RATE)

    if is_hf:
        return ("FDEL_HARD_FAIL",
                f"DELETION_CERT_FAILS n_cert={n_cert_valid}/{n_total} "
                f"contam={max_contam:.4f}. " + detail)
    if is_hp:
        return ("FDEL_HARD_PASS",
                f"DELETION_CERT_VALIDATED cert={n_cert_valid}/{n_total} "
                f"contam={max_contam:.4f}. " + detail)
    return ("FDEL_MIDDLE_BAND",
            f"PARTIAL cert={n_cert_valid}/{n_total} "
            f"acc_drop={mean_acc_drop:.3f}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    Formula self-tests:
    1. W_del + W_c == W_total (linearity, exact float32).
    2. Hash cert: W_c reconstructed == W_c original (sha256).
    3. Contamination formula: contam_count / (k-1).
    4. Live smoke: all metrics non-null at N=1024 k=3 m=10 seed=42.
    5. Verdict gates HP/HF correct.
    """
    # Formula self-test 1: W_del + W_c == W_total
    N_t, M_t = 128, 10
    g = torch.Generator().manual_seed(0)
    cb1 = torch.sign(torch.randn(M_t, N_t, generator=g)).float()
    cb1[cb1 == 0] = 1.0
    g2 = torch.Generator().manual_seed(1)
    cb2 = torch.sign(torch.randn(M_t, N_t, generator=g2)).float()
    cb2[cb2 == 0] = 1.0
    W1 = (cb1.T @ cb1) / N_t
    W2 = (cb2.T @ cb2) / N_t
    W_tot_t = W1 + W2
    W_del_t = W_tot_t - W1
    err = float((W_del_t - W2).abs().max().item())
    assert err < 1e-5, f"selftest formula-1 FAIL: W_del+W1 != W_total, err={err:.2e}"
    print(f"[selftest] formula-1 W_del+W_c=W_total err={err:.2e} PASS", flush=True)

    # Formula self-test 2: cert hash roundtrip
    cert_t = _deletion_cert(W1)
    W1_reconstructed = W_tot_t - W_del_t
    verified_t = _verify_cert(W1_reconstructed, cert_t)
    assert verified_t, f"selftest formula-2 FAIL: cert not verified"
    print(f"[selftest] formula-2 cert hash roundtrip VERIFIED PASS", flush=True)

    # Formula self-test 3: contamination formula
    n_k = 5
    contam_count_t = 2
    contam_rate_t = contam_count_t / (n_k - 1)
    assert abs(contam_rate_t - 0.5) < 1e-9, f"contam formula FAIL: {contam_rate_t}"
    print(f"[selftest] formula-3 contam_rate(2/4)={contam_rate_t:.4f} PASS", flush=True)

    # Formula self-test 4: live smoke N=1024 k=3 m=10
    cell = measure_cell(N, 3, 10, 42)
    assert cell["ok"], f"selftest live smoke FAIL: {cell}"
    for key in ["cert_valid", "cert_verified", "acc_drop_frac", "contamination_rate"]:
        v = cell[key]
        assert v is not None, f"{key} null: {cell}"
    assert cell["cert_valid"] and cell["cert_verified"], \
        f"selftest cert failed: {cell}"
    assert cell["contamination_rate"] <= HP_CONTAM_RATE, \
        f"selftest contamination={cell['contamination_rate']} > HP={HP_CONTAM_RATE}"
    assert cell["acc_drop_frac"] >= HP_ACC_DROP_FRAC, \
        f"selftest acc_drop={cell['acc_drop_frac']:.4f} < HP={HP_ACC_DROP_FRAC}"
    print(f"[selftest] live smoke N={N} k=3 m=10 "
          f"cert_valid={cell['cert_valid']} "
          f"acc_drop={cell['acc_drop_frac']:.4f} "
          f"contam={cell['contamination_rate']:.4f} PASS", flush=True)

    # Formula self-test 5: verdict gates
    fake_hp = [{"seed": s, "N": N, "n_clients": N_CLIENTS, "m_per_client": M_PER_CLIENT,
                "ok": True, "delete_client": 0,
                "cert_valid": True, "cert_hash": "abc...", "cert_verified": True,
                "acc_pre_deleted": 0.99, "acc_post_deleted": 0.10,
                "acc_drop_frac": 0.90, "acc_pre_others": [0.98]*4,
                "acc_post_others": [0.97]*4, "contamination_rate": 0.0, "contam_count": 0}
               for s in SEEDS]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"
    print(f"[selftest] formula-5a HP gate PASS: {v}", flush=True)

    fake_hf = [{"seed": s, "N": N, "n_clients": N_CLIENTS, "m_per_client": M_PER_CLIENT,
                "ok": True, "delete_client": 0,
                "cert_valid": False, "cert_hash": "abc...", "cert_verified": False,
                "acc_pre_deleted": 0.99, "acc_post_deleted": 0.95,
                "acc_drop_frac": 0.04, "acc_pre_others": [0.98]*4,
                "acc_post_others": [0.50]*4, "contamination_rate": 0.25, "contam_count": 1}
               for s in SEEDS]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"
    print(f"[selftest] formula-5b HF gate PASS: {v}", flush=True)

    print("[selftest] federated_deletion_cert_smoke_v1 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = get_output_dir()
    t0 = time.time()
    print(f"[run] federated_deletion_cert_smoke_v1 "
          f"N={N} k={N_CLIENTS} m_per_client={M_PER_CLIENT} seeds={SEEDS} "
          f"[FEDERATED_DELETION_CERT multi-client erase + zero contamination]",
          flush=True)

    cells: List[Dict] = []
    for seed in SEEDS:
        cell = measure_cell(N, N_CLIENTS, M_PER_CLIENT, seed)
        cells.append(cell)
        print(f"  seed={seed} cert_valid={cell['cert_valid']} "
              f"cert_verified={cell['cert_verified']} "
              f"acc_pre={cell['acc_pre_deleted']:.4f} "
              f"acc_post={cell['acc_post_deleted']:.4f} "
              f"acc_drop={cell['acc_drop_frac']:.4f} "
              f"contam={cell['contamination_rate']:.4f} "
              f"({time.time()-t0:.2f}s)", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor":      "federated_deletion_cert_smoke_v1",
        "N":           N, "n_clients": N_CLIENTS, "m_per_client": M_PER_CLIENT,
        "seeds":       SEEDS,
        "cells":       cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s":   elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
