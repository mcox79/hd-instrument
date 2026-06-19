"""TENSOR BINDING TWO-SHARD v1 at N=4096.

CONTEXT:
  Track-B Phase 1 gate test (user msg 1, 2026-05-30): does cross-shard
  relational query via tensor product binding produce results matching
  the sequential per-shard composition baseline? This is THE gate test
  for Operation B cross-shard relational query capability. HARD_PASS
  -> ship T2.P2 (3-shard). HARD_FAIL -> tensor-bound multi-shard does
  not work; sequential composition remains the only path.

SCIENTIFIC QUESTION:
  Two substrate shards W_A (customer -> email) and W_B (customer -> phone)
  share a key space. Two query modes are compared:

  - Sequential baseline: r_email = W_A k_X; r_phone = W_B k_X.
       Return tuple (decode(r_email), decode(r_phone)).
  - Tensor-bound: form q = k_X (tensor-with) k_contact_type, where
       k_contact_type is one of {k_email, k_phone}. Distribute to the
       relevant shard; the substrate's tensor-binding response should
       isolate the contact's value of the requested type.

  Concrete tensor-binding form (canonical per user msg 1 spec):
       For "give me X's email":
          q_email = k_X (*) k_email      (where (*) is element-wise multiply,
                                          the BSC/HRR analog of tensor binding)
          r_relational_A = W_A q_email
       For "give me X's phone":
          q_phone = k_X (*) k_phone
          r_relational_B = W_B q_phone

  The tensor mode tests whether bind(k_X, k_email) ROUTES through W_A
  cleanly (since W_A stores customer->email associations). If the
  substrate maintains the bind structure, tensor_acc should equal
  sequential_acc on the same 50 test queries.

DESIGN:
  - N=4096, BSC-equivalent Kerdock codebook (PROT-018 _n4096 binding).
  - 2 shards: W_A (customer -> email) and W_B (customer -> phone).
  - 50 customers per seed; each customer has a stored (email, phone) pair.
  - 5 seeds [7, 17, 23, 31, 41] for fact selection.
  - 100 test queries per seed (50 email + 50 phone).
  - 5 cell-seeds total at FULL (one cell-seed = one full 100-query session).

METRICS:
  - sequential_acc: fraction of 100 test queries where the sequential
       result (decode(W_A k_X) == v_email_X) AND (decode(W_B k_X) == v_phone_X).
  - tensor_acc: fraction of 100 test queries where the tensor-bound result
       (decode(W_A * bind(k_X, k_email)) == v_email_X) for email queries,
       and similarly for phone queries.
  - tensor_vs_sequential_match: fraction where tensor decoded result ==
       sequential decoded result EXACTLY (per query).
  - latency_ratio: (tensor_total_time) / (sequential_total_time);
       single-query wall-clock comparison.

PRE-REGISTERED BANDS (matches user msg 1 spec):
  HARD_PASS: tensor_acc >= 0.85 AND tensor_vs_sequential_match >= 0.90
       in >= 3/5 seeds.
  HARD_FAIL: tensor_acc <= 0.50 OR tensor_vs_sequential_match <= 0.50
       (tensor binding does not yield comparable results to sequential).
  MIDDLE_BAND: 0.50 < tensor_acc < 0.85.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. K=2 shards; 50 customers; 100 test queries per seed (50 email + 50 phone).
  3. 5 seeds -> 5 cell-seeds at FULL.
  4. Codebook: Kerdock_4coset_codebook(N=4096) yields C codewords with
     k.k/N = 1 (unit-norm rows).
  5. Bind operator: BSC element-wise multiply (k_X * k_contact); inverse
     = element-wise multiply again (involutive); test that
     bind(k_X, k_email) (*) k_email = k_X (involutive unbind).

OOM CHECK:
  W_A + W_B each 4096*4096*4 = 64MB; codebook 4096*4096*4 = 64MB.
  Plus 100 query buffers each 4096*4. Total < 1GB. Well under 6GB ceiling.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: tensor_binding_two_shard_v1_n4096
Queue: overnight_queue (GPU; N=4096; 5 cell-seeds; 100 queries/cell)
Pre-reg: preregs/2026-05-30_tensor_binding_two_shard_v1_n4096.md
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

# Load substrate primitives (Kerdock codebook + store_facts_batched)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_tbind", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

v3 = c1.v3

# Per-cell-seed checkpoint
_ckpt_path = REPO / "experiments" / "_seed_checkpoint.py"
_ckpt_spec = importlib.util.spec_from_file_location("_seed_checkpoint_tbind", _ckpt_path)
_ckpt = importlib.util.module_from_spec(_ckpt_spec)
_ckpt_spec.loader.exec_module(_ckpt)
list_completed_keys = _ckpt.list_completed_keys
write_partial_key   = _ckpt.write_partial_key
load_partial_key    = _ckpt.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds to N = 4096
N = 4096        # PROT-018 production-N anchor line
N_FULL  = N
N_SMOKE = 1024   # Kerdock requires even log2(N); 1024=2^10 OK, 512=2^9 not.
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K_SHARDS = 2                # W_A (email), W_B (phone)
N_CUSTOMERS_FULL  = 50
N_CUSTOMERS_SMOKE = 8

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (matches user msg 1)
HP_TENSOR_ACC_MIN     = 0.85
HP_MATCH_MIN          = 0.90
HP_SEEDS_MIN          = 3
HF_TENSOR_ACC_MAX     = 0.50
HF_MATCH_MAX          = 0.50


def get_output_dir(default_name: str = "tensor_binding_two_shard_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cell_key(seed: int) -> str:
    return f"seed{int(seed)}"


def bsc_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """BSC bind = element-wise multiply (involutive analog of tensor binding)."""
    return a * b


def build_two_shard_substrate(codebook: torch.Tensor, n_customers: int,
                                seed: int, N_use: int, device: torch.device
                                ) -> Tuple[torch.Tensor, torch.Tensor,
                                            torch.Tensor, torch.Tensor,
                                            torch.Tensor, torch.Tensor,
                                            int, int]:
    """Build the two-shard substrate.

    Returns (W_A, W_B, k_customers, v_emails, v_phones,
             customer_idx, email_role_idx, phone_role_idx).
    Reserves 2 codewords for the email/phone ROLE keys (used by tensor mode).
    """
    C = codebook.shape[0]
    assert C >= n_customers * 3 + 2, (
        f"codebook too small: C={C} need {n_customers*3+2}")

    gen = torch.Generator(device=device).manual_seed(seed)
    perm = torch.randperm(C, generator=gen, device=device)
    # First 2 codewords reserved for role keys (email_role, phone_role)
    email_role_idx = int(perm[0].item())
    phone_role_idx = int(perm[1].item())
    # Next n_customers for customer keys
    cust_idx = perm[2:2 + n_customers]
    # Next n_customers for emails
    email_idx = perm[2 + n_customers:2 + 2 * n_customers]
    # Next n_customers for phones
    phone_idx = perm[2 + 2 * n_customers:2 + 3 * n_customers]

    k_customers = codebook[cust_idx]              # (M, N)
    v_emails = codebook[email_idx]                 # (M, N)
    v_phones = codebook[phone_idx]                 # (M, N)

    # Build W_A (customer -> email) and W_B (customer -> phone) via outer-sum.
    W_A = (v_emails.T @ k_customers) / float(N_use)
    W_B = (v_phones.T @ k_customers) / float(N_use)

    return (W_A, W_B, k_customers, v_emails, v_phones,
            cust_idx, email_role_idx, phone_role_idx)


def decode_to_codeword(r: torch.Tensor, codebook: torch.Tensor,
                        N_use: int) -> int:
    """Decode raw response r in (N,) to a codeword index via argmax cosine."""
    # cosine ~ codebook @ r / N when codebook rows are unit-norm (Kerdock).
    sims = codebook @ r / float(N_use)             # (C,)
    return int(sims.argmax().item())


def run_one_cell(seed: int, N_use: int, n_customers: int,
                  device: torch.device) -> Dict:
    """One seed: build substrate, run all queries sequential vs tensor."""
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    (W_A, W_B, k_customers, v_emails, v_phones,
     cust_idx, email_role_idx, phone_role_idx) = (
        build_two_shard_substrate(codebook, n_customers, seed, N_use, device)
    )

    k_email_role = codebook[email_role_idx]        # (N,)
    k_phone_role = codebook[phone_role_idx]        # (N,)

    n = n_customers

    # ------- Sequential baseline -------
    t_seq0 = time.perf_counter()
    seq_email_pred = []
    seq_phone_pred = []
    for i in range(n):
        k_X = k_customers[i]
        r_email = W_A @ k_X
        r_phone = W_B @ k_X
        seq_email_pred.append(decode_to_codeword(r_email, codebook, N_use))
        seq_phone_pred.append(decode_to_codeword(r_phone, codebook, N_use))
    seq_time = time.perf_counter() - t_seq0

    # Sequential acc: BOTH email and phone must match
    seq_email_target = [int(codebook.shape[0]) for _ in range(n)]  # placeholder
    # The true target index is the codebook index of v_emails[i] / v_phones[i].
    # We get that from build_two_shard_substrate's permutation: it's the
    # corresponding entry in (perm[2+n_customers ..]) etc. But easier: since
    # we have v_emails[i] in hand, just argmax-cosine against codebook to
    # recover the index it came from.
    # (Identical to decode_to_codeword applied to v_emails[i] itself.)
    email_target_idx = [decode_to_codeword(v_emails[i], codebook, N_use)
                         for i in range(n)]
    phone_target_idx = [decode_to_codeword(v_phones[i], codebook, N_use)
                         for i in range(n)]

    seq_email_correct = sum(1 for i in range(n)
                              if seq_email_pred[i] == email_target_idx[i])
    seq_phone_correct = sum(1 for i in range(n)
                              if seq_phone_pred[i] == phone_target_idx[i])
    # Combined: both must match
    seq_both_correct = sum(1 for i in range(n)
                             if seq_email_pred[i] == email_target_idx[i]
                             and seq_phone_pred[i] == phone_target_idx[i])
    sequential_acc = seq_both_correct / float(n)
    sequential_acc_email = seq_email_correct / float(n)
    sequential_acc_phone = seq_phone_correct / float(n)

    # ------- Tensor-bound mode -------
    # For an email query: q = k_X (*) k_email_role; route to W_A;
    # the substrate's response should be ~ v_email_i if the bind structure is
    # preserved by the W matmul (i.e., W_A operates on the customer-component
    # of the bound key; the role-key acts as a scalar mask under BSC bind).
    #
    # We measure tensor_email_pred = decode(W_A @ q_email_i) and
    #            tensor_phone_pred = decode(W_B @ q_phone_i).
    # tensor_acc = average of email_correct + phone_correct.
    t_ten0 = time.perf_counter()
    tensor_email_pred = []
    tensor_phone_pred = []
    for i in range(n):
        k_X = k_customers[i]
        q_email = bsc_bind(k_X, k_email_role)
        q_phone = bsc_bind(k_X, k_phone_role)
        r_email_ten = W_A @ q_email
        r_phone_ten = W_B @ q_phone
        tensor_email_pred.append(decode_to_codeword(r_email_ten, codebook, N_use))
        tensor_phone_pred.append(decode_to_codeword(r_phone_ten, codebook, N_use))
    tensor_time = time.perf_counter() - t_ten0

    ten_email_correct = sum(1 for i in range(n)
                              if tensor_email_pred[i] == email_target_idx[i])
    ten_phone_correct = sum(1 for i in range(n)
                              if tensor_phone_pred[i] == phone_target_idx[i])
    # tensor_acc is the per-query accuracy across BOTH email and phone queries
    # (100 queries for n=50).
    tensor_acc = (ten_email_correct + ten_phone_correct) / float(2 * n)

    # Match: same decoded index sequential vs tensor, per query.
    match_email = sum(1 for i in range(n)
                        if seq_email_pred[i] == tensor_email_pred[i])
    match_phone = sum(1 for i in range(n)
                        if seq_phone_pred[i] == tensor_phone_pred[i])
    tensor_vs_sequential_match = (match_email + match_phone) / float(2 * n)

    latency_ratio = tensor_time / max(seq_time, 1e-9)

    return {
        "seed": int(seed),
        "N": int(N_use),
        "n_customers": int(n),
        "sequential_acc": round(sequential_acc, 5),
        "sequential_acc_email": round(sequential_acc_email, 5),
        "sequential_acc_phone": round(sequential_acc_phone, 5),
        "tensor_acc": round(tensor_acc, 5),
        "tensor_vs_sequential_match": round(tensor_vs_sequential_match, 5),
        "sequential_time_s": round(seq_time, 5),
        "tensor_time_s": round(tensor_time, 5),
        "latency_ratio": round(latency_ratio, 5),
        "n_queries": int(2 * n),
    }


def cell_passes_hp(cell: Dict) -> bool:
    return (cell["tensor_acc"] >= HP_TENSOR_ACC_MIN
            and cell["tensor_vs_sequential_match"] >= HP_MATCH_MIN)


def cell_is_hf(cell: Dict) -> bool:
    return (cell["tensor_acc"] <= HF_TENSOR_ACC_MAX
            or cell["tensor_vs_sequential_match"] <= HF_MATCH_MAX)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("TBIND_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if cell_passes_hp(c))
    hf_seeds = sum(1 for c in cells if cell_is_hf(c))

    mean_tens = sum(c["tensor_acc"] for c in cells) / len(cells)
    mean_match = sum(c["tensor_vs_sequential_match"] for c in cells) / len(cells)
    mean_seq  = sum(c["sequential_acc"] for c in cells) / len(cells)

    detail = (f"pass_seeds={pass_seeds}/{len(cells)} hf_seeds={hf_seeds} "
              f"mean_tensor_acc={mean_tens:.3f} mean_match={mean_match:.3f} "
              f"mean_seq_acc={mean_seq:.3f} N={summary.get('N', N_FULL)}")

    # HARD_FAIL: majority of seeds are HF
    if hf_seeds >= len(cells) / 2:
        return ("TBIND_HARD_FAIL",
                f"TENSOR_BIND_BROKEN: {hf_seeds}/{len(cells)} HF. " + detail)

    if pass_seeds >= HP_SEEDS_MIN or (summary.get("smoke") and pass_seeds >= 1):
        return ("TBIND_HARD_PASS",
                f"TENSOR_BIND_OK: {pass_seeds}/{len(cells)} pass HP "
                f"(>= {HP_SEEDS_MIN} required for FULL). " + detail)

    return ("TBIND_MIDDLE_BAND",
            f"PARTIAL: pass={pass_seeds}/{len(cells)}, hf={hf_seeds}/{len(cells)}. "
            + detail)


def _instrumentation_selftest() -> None:
    """Mandatory: assert all metrics non-null + verdict gates + bind algebra."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert K_SHARDS == 2, f"K_SHARDS: {K_SHARDS}"

    # Cell count
    assert len(SEEDS_FULL) == 5, f"seeds: {SEEDS_FULL}"
    assert N_CUSTOMERS_FULL == 50, f"n_customers FULL: {N_CUSTOMERS_FULL}"

    # Bind algebra: involutive under BSC element-wise multiply for
    # values in {+1, -1}. Kerdock codewords are sign vectors so this holds.
    device = torch.device("cpu")
    a = torch.tensor([1.0, -1.0, 1.0, -1.0], device=device)
    b = torch.tensor([-1.0, -1.0, 1.0, 1.0], device=device)
    bound = bsc_bind(a, b)
    unbound = bsc_bind(bound, b)
    assert torch.allclose(unbound, a), f"bind involution failed: {unbound} vs {a}"

    # Smoke: 1 cell at small N (N_SMOKE) on CPU
    out = run_one_cell(17, N_SMOKE, N_CUSTOMERS_SMOKE, device)
    for k in ("sequential_acc", "tensor_acc", "tensor_vs_sequential_match",
              "sequential_time_s", "tensor_time_s", "latency_ratio"):
        v_ = out.get(k)
        assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_)), (
            f"selftest: metric {k} null/NaN in {out}")
    assert 0.0 <= out["sequential_acc"] <= 1.0
    assert 0.0 <= out["tensor_acc"] <= 1.0
    assert 0.0 <= out["tensor_vs_sequential_match"] <= 1.0

    # Verdict self-tests
    fake_hf_cells = [
        {"seed": s, "sequential_acc": 0.95, "tensor_acc": 0.2,
         "tensor_vs_sequential_match": 0.2, "sequential_time_s": 0.001,
         "tensor_time_s": 0.001, "latency_ratio": 1.0,
         "n_customers": 50, "n_queries": 100, "N": N_FULL,
         "sequential_acc_email": 0.95, "sequential_acc_phone": 0.95}
        for s in SEEDS_FULL
    ]
    vf, mf = compute_verdict({"cells": fake_hf_cells, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf} {mf}"

    fake_hp_cells = [
        {"seed": s, "sequential_acc": 0.95, "tensor_acc": 0.92,
         "tensor_vs_sequential_match": 0.95, "sequential_time_s": 0.001,
         "tensor_time_s": 0.001, "latency_ratio": 1.0,
         "n_customers": 50, "n_queries": 100, "N": N_FULL,
         "sequential_acc_email": 0.95, "sequential_acc_phone": 0.95}
        for s in SEEDS_FULL
    ]
    vp, mp = compute_verdict({"cells": fake_hp_cells, "N": N_FULL})
    assert "HARD_PASS" in vp, f"HARD_PASS gate: {vp} {mp}"

    # MIDDLE_BAND: some pass, some not, none HF
    fake_mb_cells = (
        [
            {"seed": s, "sequential_acc": 0.95, "tensor_acc": 0.92,
             "tensor_vs_sequential_match": 0.95, "sequential_time_s": 0.001,
             "tensor_time_s": 0.001, "latency_ratio": 1.0,
             "n_customers": 50, "n_queries": 100, "N": N_FULL,
             "sequential_acc_email": 0.95, "sequential_acc_phone": 0.95}
            for s in SEEDS_FULL[:2]
        ] + [
            {"seed": s, "sequential_acc": 0.95, "tensor_acc": 0.7,
             "tensor_vs_sequential_match": 0.7, "sequential_time_s": 0.001,
             "tensor_time_s": 0.001, "latency_ratio": 1.0,
             "n_customers": 50, "n_queries": 100, "N": N_FULL,
             "sequential_acc_email": 0.95, "sequential_acc_phone": 0.95}
            for s in SEEDS_FULL[2:]
        ]
    )
    vmb, mmb = compute_verdict({"cells": fake_mb_cells, "N": N_FULL})
    assert ("MIDDLE_BAND" in vmb) or ("HARD_FAIL" not in vmb and "HARD_PASS" not in vmb), (
        f"MIDDLE_BAND gate: {vmb} {mmb}")

    print(
        f"[selftest] tensor_binding_two_shard_v1_n4096 PASS "
        f"smoke seq_acc={out['sequential_acc']:.3f} "
        f"tensor_acc={out['tensor_acc']:.3f} "
        f"match={out['tensor_vs_sequential_match']:.3f} "
        f"lat_ratio={out['latency_ratio']:.3f}",
        flush=True,
    )


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    n_cust = N_CUSTOMERS_SMOKE if smoke else N_CUSTOMERS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    total_expected = len(seeds)
    out_dir = get_output_dir()
    done_keys = set(list_completed_keys(out_dir))

    print(f"[run] tensor_binding_two_shard_v1_n4096 smoke={smoke} N={N_cfg} "
          f"n_customers={n_cust} seeds={seeds} "
          f"total_expected={total_expected} already_done={len(done_keys)} "
          f"device={device_str}", flush=True)
    t0 = time.time()

    for seed in seeds:
        ck = cell_key(seed)
        if ck in done_keys:
            continue
        try:
            out = run_one_cell(seed, N_cfg, n_cust, device)
            out["seed_int"] = out["seed"]
            out["seed"] = ck
            write_partial_key(out_dir, ck, out)
            print(f"  {ck} seq_acc={out['sequential_acc']:.3f} "
                  f"tensor_acc={out['tensor_acc']:.3f} "
                  f"match={out['tensor_vs_sequential_match']:.3f} "
                  f"lat_ratio={out['latency_ratio']:.3f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  {ck} CELL_FAILED: {type(e).__name__}: {e}", flush=True)
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    all_cells = []
    for ck in list_completed_keys(out_dir):
        body = load_partial_key(out_dir, ck)
        if body is None:
            continue
        all_cells.append(body)

    summary = {
        "anchor": "tensor_binding_two_shard_v1_n4096",
        "N": N_cfg,
        "smoke": smoke,
        "seeds": seeds,
        "n_customers": n_cust,
        "total_expected": total_expected,
        "n_completed": len(all_cells),
        "cells": all_cells,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = round(time.time() - t0, 2)
    summary["verdict"] = verdict
    summary["verdict_msg"] = verdict_msg
    summary["elapsed_s"] = elapsed

    out_path = out_dir / "metrics.json"
    payload = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[completed] {len(all_cells)}/{total_expected}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
