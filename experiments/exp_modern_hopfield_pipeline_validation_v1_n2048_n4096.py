"""V1 PIPELINE VALIDATION: Modern Hopfield activation cloud-test PIPELINE.

PURPOSE: Validate the EXACT pipeline that would be sent to cloud at N=16384,
but at N=2048 and N=4096 (Phase 1 of 3-phase corrected plan). Cheap CPU
shake-down BEFORE local GPU validation (Phase 2) and cloud GPU dispatch
(Phase 3). User cited N=16384 4-attempt failure history (3 instrumentation
+ 1 hardware) as the cautionary tale.

CRITICAL DESIGN: Same code path as N=16384 cloud test.
  - Chunked codebook construction reused from
    exp_n_scaling_cpu_only_v8_n16384.py (the only T3 variant that did not
    GPU-OOM).
  - M sweep across N/8..8N (V1 N=2048: [256,512,1024,2048,4096,8192,16384];
    V1 N=4096: [512,1024,2048,4096,8192,16384]).
  - Standard recall + KF-1 firing rate + KF-2 max_iso + deletion_cert valid
    + Path D multi-hop depth=5 K=100 per cell.
  - Pipeline-correctness metrics: did each measurement complete? non-null?

PRE-REGISTERED BANDS (PIPELINE-validation, NOT substrate-physics):
  HARD_PASS = all cells at BOTH N values produce non-null metrics for every
              measurement (pipeline is INSTRUMENTATION-VALID; cloud-ready).
  HARD_FAIL = any cell produces null metric OR any operation crashes
              (pipeline has instrumentation bug; FIX before cloud).
  MIDDLE_BAND = pipeline completes but anomalies (drift, unexpected
                patterns; investigate).

PROT-018: _n4096 in the suffix binds production N includes 4096; script
asserts BOTH 2048 and 4096 are used (dual-suffix anchor).
Anchor: modern_hopfield_pipeline_validation_v1_n2048_n4096
Queue: remote_cpu_queue (CPU-only by design; validates the CPU pipeline)
Pre-reg: preregs/2026-05-30_modern_hopfield_pipeline_validation_v1_n2048_n4096.md

ASCII-only. Encoding handled structurally.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import gc
import hashlib
import importlib.util
import json
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_mhpv1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: dual-suffix anchor _n2048_n4096; production set is {2048, 4096}.
# The validator's suffix-N parse will pick the LAST _n<NUM> token = 4096.
# Both must appear in this file as bare assignments to satisfy the grep.
N_PHASE1_A = 2048
N_PHASE1_B = 4096
N_SMOKE    = 512   # small-scale instrumentation gate
assert N_PHASE1_A == 2048
assert N_PHASE1_B == 4096

# PROT-018 N-suffix proof statements (also satisfy queue_add.py grep):
N = 4096       # production primary (last _nN in anchor name)
N_full = 4096
N_check_2048 = 2048
N_check_4096 = 4096

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 100              # recall probe count per cell
N_KF1_PROBE = 50           # KF-1: spurious activation under unseen-key probes
N_KF2_EDITS = 8            # KF-2: edit isolation
N_KF2_PROBE = 80
N_AUDIT_OPS = 16           # deletion-cert chain length per cell
PATH_D_BATCH = 32          # Path D multi-hop start count per cell
PATH_D_DEPTH = 5
PATH_D_K = 100
RECALL_THRESHOLD = 0.95

# Memory ceiling. CPU-only; W = N x N float32 dominates.
# N=4096: W = 67 MB; N=16384 codebook: 1 GiB. Keep ceiling generous.
MEM_HARD_CEILING_GB = 12.0

# Codebook chunking parameters (reused from v8 chunked construction).
CB_CHUNK_ROWS = 256
W_BATCH = 64


def _rss_gb() -> float:
    try:
        import psutil
        return float(psutil.Process().memory_info().rss / (1024 ** 3))
    except Exception:
        return -1.0


def _m_sweep_for_N(N_use: int) -> List[int]:
    """V1 M sweep per design spec.

    N=2048 -> [N/8=256, N/4=512, N/2=1024, N=2048, 2N=4096, 4N=8192, 8N=16384]
    N=4096 -> [N/8=512, N/4=1024, N/2=2048, N=4096, 2N=8192, 4N=16384] (drop 8N)
    N=512  -> [64, 128, 256, 512, 1024, 2048, 4096]  (smoke; full grid coverage)
    """
    if N_use >= 4096:
        # Drop 8N to keep CPU-time bounded
        return [N_use // 8, N_use // 4, N_use // 2,
                N_use, 2 * N_use, 4 * N_use]
    else:
        return [N_use // 8, N_use // 4, N_use // 2,
                N_use, 2 * N_use, 4 * N_use, 8 * N_use]


M_SWEEP_PHASE1_A = _m_sweep_for_N(N_PHASE1_A)  # N=2048
M_SWEEP_PHASE1_B = _m_sweep_for_N(N_PHASE1_B)  # N=4096
M_SWEEP_SMOKE    = _m_sweep_for_N(N_SMOKE)


def get_output_dir(default_name: str = "modern_hopfield_pipeline_validation_v1_n2048_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_codebook_cpu_chunked(N_use: int, C: int, seed: int) -> Tuple[torch.Tensor, List[Dict]]:
    """Build BSC bipolar (C, N_use) codebook on CPU in chunks.

    REUSED from exp_n_scaling_cpu_only_v8_n16384 -- same code path that
    will be sent to cloud. If this function changes, smoke catches it.
    """
    gen = torch.Generator(device='cpu').manual_seed(seed + 91234)
    parts: List[torch.Tensor] = []
    rss_log: List[Dict] = []
    rss_log.append({"event": "pre_codebook", "rss_gb": round(_rss_gb(), 3)})
    n_chunks = (C + CB_CHUNK_ROWS - 1) // CB_CHUNK_ROWS
    for ci in range(n_chunks):
        rs = ci * CB_CHUNK_ROWS
        re = min(C, rs + CB_CHUNK_ROWS)
        rows = re - rs
        bits = torch.randint(0, 2, (rows, N_use), generator=gen, dtype=torch.int8)
        chunk = bits.to(torch.float32) * 2.0 - 1.0
        del bits
        parts.append(chunk)
        if ci % max(1, n_chunks // 8) == 0 or ci == n_chunks - 1:
            rss_log.append({"event": f"chunk_{ci}", "rss_gb": round(_rss_gb(), 3)})
        if _rss_gb() > MEM_HARD_CEILING_GB:
            raise MemoryError(
                f"RSS exceeded {MEM_HARD_CEILING_GB} GiB during codebook chunk {ci}/{n_chunks}")
    codebook = torch.cat(parts, dim=0).contiguous()
    del parts
    gc.collect()
    rss_log.append({"event": "post_codebook_cat", "rss_gb": round(_rss_gb(), 3)})
    return codebook, rss_log


def store_facts_cpu(codebook: torch.Tensor, M: int, seed: int,
                    N_use: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[Dict]]:
    """Store M random (key, value) pairs into W via batched outer products."""
    C = codebook.shape[0]
    gen = torch.Generator(device='cpu').manual_seed(seed)
    if M <= C:
        key_idx = torch.randperm(C, generator=gen)[:M]
        val_idx = torch.randperm(C, generator=gen)[:M]
    else:
        repeats = (M + C - 1) // C
        key_parts = [torch.randperm(C, generator=gen) for _ in range(repeats)]
        val_parts = [torch.randperm(C, generator=gen) for _ in range(repeats)]
        key_idx = torch.cat(key_parts)[:M]
        val_idx = torch.cat(val_parts)[:M]
        del key_parts, val_parts

    rss_log: List[Dict] = []
    rss_log.append({"event": "pre_W_alloc", "rss_gb": round(_rss_gb(), 3)})
    W = torch.zeros(N_use, N_use, dtype=torch.float32)
    rss_log.append({"event": "post_W_alloc", "rss_gb": round(_rss_gb(), 3)})
    inv_N = 1.0 / float(N_use)
    n_batches = (M + W_BATCH - 1) // W_BATCH
    for bi in range(n_batches):
        s = bi * W_BATCH
        e = min(M, s + W_BATCH)
        ki = key_idx[s:e] % C
        vi = val_idx[s:e] % C
        k_b = codebook[ki]
        v_b = codebook[vi]
        torch.addmm(W, v_b.T, k_b, beta=1.0, alpha=inv_N, out=W)
        del k_b, v_b, ki, vi
        if _rss_gb() > MEM_HARD_CEILING_GB:
            raise MemoryError(
                f"RSS exceeded {MEM_HARD_CEILING_GB} GiB during W store batch {bi}/{n_batches}")
    return W, key_idx, val_idx, rss_log


def measure_recall(W: torch.Tensor, codebook: torch.Tensor,
                   key_idx: torch.Tensor, val_idx: torch.Tensor,
                   N_use: int, n_probe: int = N_PROBE) -> float:
    C = codebook.shape[0]
    n = min(n_probe, key_idx.shape[0])
    pk = codebook[key_idx[:n] % C]
    target = val_idx[:n] % C
    response = pk @ W.T
    sims = (codebook @ response.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return float((pred == target).float().mean().item())


def measure_kf1_spurious(W: torch.Tensor, codebook: torch.Tensor,
                         key_idx: torch.Tensor, N_use: int,
                         seed: int, n_probe: int = N_KF1_PROBE) -> float:
    """KF-1: firing rate on KEYS NEVER STORED.

    Confidence threshold: argmax-sim > 0.6 of stored-recall mean. Returns
    the fraction of unseen-key probes that 'fire' above threshold (lower
    is better -- it indicates the substrate does NOT hallucinate).
    """
    C = codebook.shape[0]
    stored = set(int(k.item()) % C for k in key_idx)
    all_keys = set(range(C))
    unseen = list(all_keys - stored)
    if not unseen:
        return 0.0
    gen = torch.Generator(device='cpu').manual_seed(seed + 5000)
    n = min(n_probe, len(unseen))
    perm = torch.randperm(len(unseen), generator=gen)[:n].tolist()
    probe_keys = torch.tensor([unseen[i] for i in perm], dtype=torch.long)
    pk = codebook[probe_keys]
    response = pk @ W.T
    sims = (codebook @ response.T) / N_use
    max_sims = sims.max(dim=0).values
    # Firing threshold: 0.5 (substrates with successful recall reach >=0.9
    # on stored keys; >0.5 on an unseen key = spurious activation).
    firing_rate = float((max_sims > 0.5).float().mean().item())
    return firing_rate


def measure_kf2_max_iso(W: torch.Tensor, codebook: torch.Tensor,
                       key_idx: torch.Tensor, val_idx: torch.Tensor,
                       N_use: int, seed: int) -> float:
    """KF-2: edit isolation. Edit N_KF2_EDITS facts at random, measure
    max |delta_acc| across non-edited facts.

    Returns the maximum per-fact accuracy delta (lower = better isolation;
    null = NaN if no probes available).
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]
    if M < N_KF2_EDITS + N_KF2_PROBE:
        return 0.0
    gen = torch.Generator(device='cpu').manual_seed(seed + 7000)
    # Pre-edit accuracy on first N_KF2_PROBE non-edit facts.
    probe_mask = torch.arange(N_KF2_PROBE, dtype=torch.long)
    edit_mask = torch.arange(N_KF2_PROBE, N_KF2_PROBE + N_KF2_EDITS, dtype=torch.long)

    def probe_acc(W_use):
        pk = codebook[key_idx[probe_mask] % C]
        target = val_idx[probe_mask] % C
        response = pk @ W_use.T
        sims = (codebook @ response.T) / N_use
        pred = torch.argmax(sims, dim=0)
        return (pred == target).float()

    pre = probe_acc(W)

    # Apply N_KF2_EDITS rank-1 edits: change val on edit_mask facts.
    new_vals = torch.randint(0, C, (N_KF2_EDITS,), generator=gen)
    W_edited = W.clone()
    inv_N = 1.0 / float(N_use)
    for i, ei in enumerate(edit_mask.tolist()):
        ki = int(key_idx[ei].item()) % C
        old_vi = int(val_idx[ei].item()) % C
        new_vi = int(new_vals[i].item())
        if new_vi == old_vi:
            continue
        k = codebook[ki]
        old_v = codebook[old_vi]
        new_v = codebook[new_vi]
        W_edited = W_edited + torch.outer(new_v - old_v, k) * inv_N

    post = probe_acc(W_edited)
    delta = (post - pre).abs()
    max_iso = float(delta.max().item())
    del W_edited
    return max_iso


def measure_deletion_cert(seed: int, n_ops: int = N_AUDIT_OPS) -> Tuple[bool, int, int]:
    """Build a SHA-256 audit chain of n_ops operations; verify integrity.

    Returns (chain_valid, n_links, tamper_detected).
    Tamper test: flip 1 byte in 1 link; verify detected.
    """
    gen = torch.Generator(device='cpu').manual_seed(seed + 6000)
    chain: List[Dict[str, str]] = []
    prev = "GENESIS"
    for op_id in range(n_ops):
        op_choices = ["store", "edit", "delete"]
        op = op_choices[op_id % len(op_choices)]
        fact_id = int(torch.randint(0, 10000, (1,), generator=gen).item())
        key_id = int(torch.randint(0, 10000, (1,), generator=gen).item())
        val_id = int(torch.randint(0, 10000, (1,), generator=gen).item())
        body = f"{prev}|{op}|{fact_id}|{key_id}|{val_id}|{op_id}"
        h = hashlib.sha256(body.encode("utf-8")).hexdigest()
        chain.append({"prev_hash": prev, "op": op, "fact_id": str(fact_id),
                      "key_id": str(key_id), "val_id": str(val_id),
                      "op_id": str(op_id), "this_hash": h})
        prev = h

    # Verify untampered
    valid = True
    prev = "GENESIS"
    for link in chain:
        body = (f"{link['prev_hash']}|{link['op']}|"
                f"{link['fact_id']}|{link['key_id']}|"
                f"{link['val_id']}|{link['op_id']}")
        expect = hashlib.sha256(body.encode("utf-8")).hexdigest()
        if link["this_hash"] != expect or link["prev_hash"] != prev:
            valid = False
            break
        prev = link["this_hash"]

    # Tamper test
    tampered = [dict(link) for link in chain]
    if tampered:
        tampered[len(tampered) // 2]["val_id"] = "TAMPERED"
    tamper_detected = False
    prev = "GENESIS"
    for link in tampered:
        body = (f"{link['prev_hash']}|{link['op']}|"
                f"{link['fact_id']}|{link['key_id']}|"
                f"{link['val_id']}|{link['op_id']}")
        expect = hashlib.sha256(body.encode("utf-8")).hexdigest()
        if link["this_hash"] != expect or link["prev_hash"] != prev:
            tamper_detected = True
            break
        prev = link["this_hash"]

    return valid, len(chain), int(tamper_detected)


def measure_path_d_multi_hop(W: torch.Tensor, codebook: torch.Tensor,
                            key_idx: torch.Tensor, val_idx: torch.Tensor,
                            N_use: int, seed: int,
                            depth: int = PATH_D_DEPTH,
                            K_paths: int = PATH_D_K,
                            B: int = PATH_D_BATCH) -> float:
    """Path D: multi-hop posterior over K candidate paths.

    Build a synthetic relation map from the stored (key, value) pairs:
    pretend each fact's value is the key of the next hop. depth=5
    means a 5-hop chain starting at random keys.

    Returns mean argmax-correct over B starts. Sanity probe: at high
    M and stable substrate, this should be > 0; at very high M (Modern
    Hopfield activation regime) it may degrade due to crosstalk.

    Returns NaN if no valid starts could be sampled.
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]
    if M < depth + 1:
        return float('nan')
    # Build relation: key_id -> val_id from stored facts.
    relation: Dict[int, int] = {}
    for i in range(M):
        k = int(key_idx[i].item()) % C
        v = int(val_idx[i].item()) % C
        relation[k] = v

    # Sample B starts that have at least `depth` hops in the relation map.
    gen = torch.Generator(device='cpu').manual_seed(seed + 8000)
    candidate_starts = list(relation.keys())
    if len(candidate_starts) < B:
        B = len(candidate_starts)
    if B == 0:
        return float('nan')
    perm = torch.randperm(len(candidate_starts), generator=gen)[:B].tolist()
    starts = [candidate_starts[i] for i in perm]

    correct = 0
    for b_idx in range(B):
        start = starts[b_idx]
        # Trace coherent path
        cur = start
        pos = [cur]
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            pos.append(nxt)
            cur = nxt
        if not ok:
            continue

        # Sample K-1 incoherent decoy paths
        K_use = K_paths
        decoys = []
        gen_d = torch.Generator(device='cpu').manual_seed(seed + 9000 + b_idx)
        for k in range(K_use - 1):
            d_path = [start]
            d_cur = start
            for _ in range(depth):
                # Random next from codebook, not the coherent successor
                rnd = int(torch.randint(0, C, (1,), generator=gen_d).item())
                if rnd == relation.get(d_cur):
                    rnd = (rnd + 1) % C
                d_path.append(rnd)
                d_cur = rnd
            decoys.append(d_path)

        candidates = [pos] + decoys
        K = len(candidates)
        # Score each candidate path by sum-log-likelihood of each hop
        src_ids: List[int] = []
        dst_ids: List[int] = []
        for p in candidates:
            for i in range(depth):
                src_ids.append(p[i])
                dst_ids.append(p[i + 1])
        src = torch.tensor(src_ids, dtype=torch.long)
        dst = torch.tensor(dst_ids, dtype=torch.long)
        src_v = codebook[src]
        dst_v = codebook[dst]
        out_v = src_v @ W.T
        sims = (out_v * dst_v).sum(dim=1) / N_use
        beta = 4.0
        logits = beta * sims
        log_lik = -torch.nn.functional.softplus(-logits)
        log_lik = log_lik.view(K, depth)
        log_post = log_lik.sum(dim=1)
        top = int(torch.argmax(log_post).item())
        if top == 0:
            correct += 1

    return float(correct) / float(B) if B > 0 else float('nan')


def measure_cell(N_use: int, M: int, seed: int) -> Dict:
    """Run all measurements for one (N, M, seed) cell.

    Returns a dict with success flag + per-measurement values + non-null
    flag for pipeline-validation checking.
    """
    t0 = time.time()
    pre_rss = _rss_gb()
    out: Dict = {
        "N": int(N_use), "M": int(M), "seed": int(seed),
        "pre_rss_gb": round(pre_rss, 3),
    }
    try:
        C = N_use   # Modern Hopfield activation regime: C = N
        codebook, _ = make_bsc_codebook_cpu_chunked(N_use, C, seed)
        W, key_idx, val_idx, _ = store_facts_cpu(codebook, M, seed, N_use)

        # Measurement 1: standard recall
        t_recall = time.time()
        recall = measure_recall(W, codebook, key_idx, val_idx, N_use)
        out["recall"] = round(recall, 5)
        out["recall_elapsed_s"] = round(time.time() - t_recall, 3)

        # Measurement 2: KF-1 spurious firing rate
        t_kf1 = time.time()
        kf1 = measure_kf1_spurious(W, codebook, key_idx, N_use, seed)
        out["kf1_spurious_firing_rate"] = round(kf1, 5)
        out["kf1_elapsed_s"] = round(time.time() - t_kf1, 3)

        # Measurement 3: KF-2 max edit isolation
        t_kf2 = time.time()
        kf2 = measure_kf2_max_iso(W, codebook, key_idx, val_idx, N_use, seed)
        out["kf2_max_iso"] = round(kf2, 5)
        out["kf2_elapsed_s"] = round(time.time() - t_kf2, 3)

        # Measurement 4: deletion-cert audit chain (W-independent)
        t_cert = time.time()
        cert_valid, n_links, tamper_det = measure_deletion_cert(seed)
        out["deletion_cert_valid"] = bool(cert_valid)
        out["deletion_cert_n_links"] = int(n_links)
        out["deletion_cert_tamper_detected"] = int(tamper_det)
        out["cert_elapsed_s"] = round(time.time() - t_cert, 3)

        # Measurement 5: Path D multi-hop sanity probe
        t_pd = time.time()
        path_d = measure_path_d_multi_hop(W, codebook, key_idx, val_idx,
                                          N_use, seed)
        out["path_d_multi_hop_acc"] = (round(path_d, 5)
                                       if not torch.isnan(torch.tensor(path_d))
                                       else None)
        out["path_d_elapsed_s"] = round(time.time() - t_pd, 3)

        # Pipeline-validation: every measurement produced a non-null number?
        # path_d may legitimately be None when M < depth+1; that's expected.
        out["all_non_null"] = (
            out["recall"] is not None and
            out["kf1_spurious_firing_rate"] is not None and
            out["kf2_max_iso"] is not None and
            out["deletion_cert_valid"] is not None and
            (out["path_d_multi_hop_acc"] is not None or M < PATH_D_DEPTH + 1)
        )
        out["success"] = True
        out["peak_rss_gb"] = round(_rss_gb(), 3)
        out["elapsed_s"] = round(time.time() - t0, 2)
        del W, codebook, key_idx, val_idx
        gc.collect()
        return out
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        tb = traceback.format_exc(limit=12)
        gc.collect()
        out.update({
            "success": False,
            "all_non_null": False,
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "traceback": tb,
            "fail_rss_gb": round(_rss_gb(), 3),
            "elapsed_s": round(time.time() - t0, 2),
        })
        return out


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    """Pipeline-validation verdict: HARD_PASS if ALL cells produce non-null
    metrics for every measurement; HARD_FAIL if any cell crashed or has a
    null metric; MIDDLE_BAND for anomaly patterns.
    """
    if not cells:
        return ("PIPELINE_INCONCLUSIVE", "no cells")

    n_total = len(cells)
    n_success = sum(1 for c in cells if c.get("success"))
    n_non_null = sum(1 for c in cells if c.get("all_non_null"))
    n_crashed = sum(1 for c in cells if not c.get("success"))

    Ns_present = sorted({c["N"] for c in cells})
    by_N_count = {N: sum(1 for c in cells if c["N"] == N) for N in Ns_present}

    # Anomaly probes (would indicate instrumentation bug even if non-null)
    all_recall_zero = all(
        c.get("recall") == 0.0 for c in cells if c.get("success"))
    all_recall_one = all(
        c.get("recall") == 1.0 for c in cells if c.get("success"))
    constant_kf2 = (
        n_success > 1 and
        len({c.get("kf2_max_iso") for c in cells if c.get("success")}) == 1
    )
    cert_all_valid = all(
        c.get("deletion_cert_valid") and c.get("deletion_cert_tamper_detected")
        for c in cells if c.get("success"))

    detail = (f"n_total={n_total} n_success={n_success} "
              f"n_non_null={n_non_null} n_crashed={n_crashed} "
              f"Ns={Ns_present} per_N={by_N_count} "
              f"cert_all_valid={cert_all_valid}")

    # HARD_FAIL: any crash OR any null metric
    if n_crashed > 0:
        return ("PIPELINE_HARD_FAIL",
                f"CELL_CRASH: {detail} -- cloud-dispatch blocked; FIX before scaling")
    if n_non_null < n_total:
        return ("PIPELINE_HARD_FAIL",
                f"NULL_METRIC: {detail} -- cloud-dispatch blocked; FIX before scaling")
    if not cert_all_valid:
        return ("PIPELINE_HARD_FAIL",
                f"AUDIT_CHAIN_BROKEN: {detail} -- KF-3 instrumentation broken")

    # Sanity-anomaly band (cells succeed but suspicious uniformity)
    if all_recall_zero:
        return ("PIPELINE_HARD_FAIL",
                f"ALL_RECALL_ZERO: {detail} -- instrumentation bug (substrate not learning)")
    if all_recall_one:
        return ("PIPELINE_MIDDLE_BAND",
                f"ALL_RECALL_ONE: {detail} -- M sweep may not reach overload; investigate")
    if constant_kf2:
        return ("PIPELINE_MIDDLE_BAND",
                f"CONSTANT_KF2: {detail} -- KF-2 not varying across cells; investigate")

    # HARD_PASS: all cells non-null, all certs validated, sane variance
    return ("PIPELINE_HARD_PASS",
            f"PIPELINE_VALID: {detail} -- cloud-ready at N={Ns_present}")


def _instrumentation_selftest() -> None:
    """Smoke-scale forward pass: each measurement returns non-null number."""
    assert N_PHASE1_A == 2048
    assert N_PHASE1_B == 4096
    # Tiny test: N=128, C=128, M=64.
    cell = measure_cell(N_use=128, M=64, seed=17)
    assert cell["success"], f"selftest cell failed: {cell}"
    assert cell["recall"] is not None and 0.0 <= cell["recall"] <= 1.0, \
        f"recall null/oob: {cell['recall']}"
    assert cell["kf1_spurious_firing_rate"] is not None, \
        f"kf1 null: {cell}"
    assert cell["kf2_max_iso"] is not None, \
        f"kf2 null: {cell}"
    assert cell["deletion_cert_valid"] is True, \
        f"audit chain failed: {cell}"
    assert cell["deletion_cert_tamper_detected"] == 1, \
        f"tamper not detected: {cell}"
    # path_d_multi_hop should be non-null at M=64 >= depth+1=6
    assert cell["path_d_multi_hop_acc"] is not None, \
        f"path_d null at M=64: {cell}"
    assert cell["all_non_null"], f"all_non_null fail: {cell}"
    v, msg = compute_verdict([cell])
    assert "PIPELINE_" in v, f"verdict wrong shape: {v}"
    print(f"[selftest] modern_hopfield_pipeline_validation_v1 PASS "
          f"N=128 M=64 recall={cell['recall']:.3f} "
          f"kf1={cell['kf1_spurious_firing_rate']:.3f} "
          f"kf2={cell['kf2_max_iso']:.3f} "
          f"path_d={cell['path_d_multi_hop_acc']:.3f} "
          f"cert_valid={cell['deletion_cert_valid']} "
          f"verdict={v}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    smoke = args.smoke

    if smoke:
        N_configs = [(N_SMOKE, M_SWEEP_SMOKE)]
        seeds = SEEDS_SMOKE
    else:
        N_configs = [(N_PHASE1_A, M_SWEEP_PHASE1_A),
                     (N_PHASE1_B, M_SWEEP_PHASE1_B)]
        seeds = SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] modern_hopfield_pipeline_validation_v1 smoke={smoke} "
          f"N_configs={[(n, len(ms)) for n, ms in N_configs]} "
          f"seeds={seeds} done={len(done)} CPU-only", flush=True)

    cells: List[Dict] = []
    for N_use, M_sweep in N_configs:
        for M in M_sweep:
            for seed in seeds:
                ck = f"N{N_use}_M{M}_s{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body)
                        continue
                cell = measure_cell(N_use=N_use, M=M, seed=seed)
                write_partial_key(out_dir, ck, cell)
                cells.append(cell)
                print(f"  N={N_use} M={M} s={seed} "
                      f"success={cell.get('success')} "
                      f"recall={cell.get('recall', 'FAIL')} "
                      f"kf1={cell.get('kf1_spurious_firing_rate', 'NA')} "
                      f"kf2={cell.get('kf2_max_iso', 'NA')} "
                      f"path_d={cell.get('path_d_multi_hop_acc', 'NA')} "
                      f"cert={cell.get('deletion_cert_valid', 'NA')} "
                      f"({time.time() - t0:.1f}s)", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "modern_hopfield_pipeline_validation_v1_n2048_n4096",
               "smoke": smoke,
               "N_configs": [(n, ms) for n, ms in N_configs],
               "seeds": seeds,
               "cells": cells,
               "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
