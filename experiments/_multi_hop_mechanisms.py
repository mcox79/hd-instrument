"""Shared multi-hop path mechanisms for E1/E2/E3/E4/E6 instrumentation batch.

Used by:
  - S1 per_hop_latency_decomposition_v1_n4096
  - S2 latency_crossover_analysis_v1_n4096
  - S3 multi_hop_memory_efficiency_v1_n4096
  - S5 path_optimization_baseline_v1_n4096
  - S6 multi_hop_edit_isolation_v1_n4096
  - S7 op_timing_atlas_v1_n4096
  - S8 latency_accuracy_tradeoff_v1_n4096
  - S9 mixed_confidence_multi_hop_v1_n4096
  - S10 approximate_multi_hop_sampling_v1_n4096
  - S11 multi_hop_gpu_baseline_v1_n4096
  - S12 adversarial_multi_hop_probing_v1_n4096
  - S13 novel_query_construction_v1_n4096
  - S14 joint_path_execution_v1_n4096

Mechanisms:
  Path B (state-propagation, continuous-output): q_{d+1} = q_d @ W.T; argmax final.
  Path D (probability-domain, Bayesian likelihoods): log-posterior over K candidate paths.
  Path E (spectral coherence): top-k signature alignment across hops; AUC over coherent/incoherent.

Reuses _relation_graph for path sampling and _metric_battery::make_substrate.
Self-test included at module scope.

ASCII-only.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)


def _ns() -> int:
    return int(time.perf_counter_ns())


@dataclass
class TimingTrace:
    """Per-operation timing trace (nanosecond precision)."""
    ops: Dict[str, List[int]] = field(default_factory=dict)

    def record(self, op: str, dt_ns: int) -> None:
        self.ops.setdefault(op, []).append(int(dt_ns))

    def dominant_op(self) -> Tuple[str, float]:
        if not self.ops:
            return ("none", 0.0)
        totals = {k: sum(v) for k, v in self.ops.items()}
        total_all = sum(totals.values())
        if total_all == 0:
            return ("none", 0.0)
        dom_op = max(totals.keys(), key=lambda k: totals[k])
        return (dom_op, totals[dom_op] / total_all)

    def summary(self) -> Dict:
        out = {}
        for k, vs in self.ops.items():
            if not vs:
                continue
            vs_sorted = sorted(vs)
            n = len(vs_sorted)
            out[k] = {
                "n_calls": n,
                "mean_ns": int(sum(vs_sorted) / n),
                "median_ns": int(vs_sorted[n // 2]),
                "total_ns": int(sum(vs_sorted)),
                "p99_ns": int(vs_sorted[min(n - 1, max(0, int(n * 0.99) - 1))]),
            }
        return out


def build_shared(N_use: int, M: int, seed: int, device: torch.device):
    """Build substrate + W + codebook + relation. Single source of truth."""
    codebook, _W0, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=codebook.shape[0], M=M, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


# -------- Path B --------------------------------------------------------------

def path_b_run(codebook: torch.Tensor, W: torch.Tensor, starts: torch.Tensor,
                depth: int, N_use: int, trace: Optional[TimingTrace] = None,
                col_rate: float = 1.0) -> torch.Tensor:
    """Path B: continuous propagation. Returns argmax predictions (n_paths,).

    col_rate < 1.0 samples a subset of W columns at each retrieval (S10).
    """
    t0 = _ns()
    q = codebook[starts].clone()
    if trace: trace.record("time_construct_query", _ns() - t0)

    if col_rate < 1.0 and col_rate > 0.0:
        n_cols = max(1, int(W.shape[1] * col_rate))
        # sample once for the whole run
        idx_cols = torch.randperm(W.shape[1], device=W.device)[:n_cols]
    else:
        idx_cols = None

    for _ in range(depth):
        t1 = _ns()
        if idx_cols is not None:
            # W is (N,N); restrict by columns for retrieval (approximate)
            W_sub = W[:, idx_cols]
            q_sub = q[:, idx_cols]
            q = q_sub @ W_sub.T
        else:
            q = q @ W.T
        if trace: trace.record("time_W_kquery_per_hop", _ns() - t1)

    t2 = _ns()
    sims = (codebook @ q.T) / N_use
    if trace: trace.record("time_normalize", _ns() - t2)
    t3 = _ns()
    pred = torch.argmax(sims, dim=0)
    if trace: trace.record("time_argmax_final", _ns() - t3)
    return pred


# -------- Path D --------------------------------------------------------------

def path_d_run(codebook: torch.Tensor, W: torch.Tensor, starts: torch.Tensor,
                relation: Dict[int, int], depth: int, K_paths: int,
                seed: int, N_use: int, beta: float = 4.0,
                trace: Optional[TimingTrace] = None,
                path_sample_rate: float = 1.0,
                confidence_priors: Optional[torch.Tensor] = None) -> torch.Tensor:
    """Path D: posterior-product over K candidate paths.

    Returns: (B,) argmax-correct indicator-like score per start (1 if predicted
    path == coherent continuation, else 0).
    """
    device = codebook.device
    C = codebook.shape[0]
    B = starts.shape[0]
    correct = torch.zeros(B, device=device, dtype=torch.float32)

    K_use = max(1, int(K_paths * path_sample_rate))

    for b in range(B):
        start = int(starts[b].item())
        t0 = _ns()
        # coherent positive path
        pos = [start]
        cur = start
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                break
            pos.append(int(nxt))
            cur = int(nxt)
        if len(pos) < depth + 1:
            continue
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=K_use - 1,
            seed=seed + b + depth + start, relation=relation)
        if not decoys:
            continue
        candidates = [pos] + decoys
        if trace: trace.record("time_enumerate_paths", _ns() - t0)

        t1 = _ns()
        K = len(candidates)
        src_list = []
        dst_list = []
        for p in candidates:
            for i in range(depth):
                src_list.append(p[i])
                dst_list.append(p[i + 1])
        src = torch.tensor(src_list, dtype=torch.long, device=device)
        dst = torch.tensor(dst_list, dtype=torch.long, device=device)
        src_v = codebook[src]
        dst_v = codebook[dst]
        out_v = src_v @ W.T
        sims = (out_v * dst_v).sum(dim=1) / N_use
        logits = beta * sims
        log_lik = -torch.nn.functional.softplus(-logits)
        log_lik = log_lik.view(K, depth)
        if trace: trace.record("time_likelihood_query_per_hop", _ns() - t1)

        t2 = _ns()
        log_post = log_lik.sum(dim=1)
        if confidence_priors is not None and len(confidence_priors) == K:
            # confidence acts as log-prior
            log_post = log_post + torch.log(confidence_priors.clamp_min(1e-6))
        if trace: trace.record("time_bayesian_update", _ns() - t2)

        t3 = _ns()
        top = int(torch.argmax(log_post).item())
        if trace: trace.record("time_posterior_max", _ns() - t3)
        if top == 0:
            correct[b] = 1.0

    return correct


# -------- Path E --------------------------------------------------------------

def _spectral_signature(response: torch.Tensor, codebook: torch.Tensor,
                         N_use: int, top_k: int) -> torch.Tensor:
    sims = (codebook @ response) / N_use
    return torch.topk(sims, top_k).values


def path_e_run(codebook: torch.Tensor, W: torch.Tensor,
                paths_pos: List[List[int]], paths_neg: List[List[int]],
                N_use: int, top_k: int = 16,
                trace: Optional[TimingTrace] = None,
                spectrum_rate: float = 1.0) -> float:
    """Path E: cross-hop spectral coherence. Returns AUC of separating
    positives from negatives.

    spectrum_rate < 1.0 reduces top_k proportionally (sampling approx).
    """
    device = codebook.device
    top_k_eff = max(1, int(top_k * spectrum_rate))

    scores: List[float] = []
    labels: List[int] = []

    for which, paths in [(1, paths_pos), (0, paths_neg)]:
        for p in paths:
            depth = len(p) - 1
            if depth < 1:
                continue
            t0 = _ns()
            src = codebook[torch.tensor(p[:-1], dtype=torch.long, device=device)]
            responses = src @ W.T
            if trace: trace.record("time_substrate_query_per_hop", _ns() - t0)

            t1 = _ns()
            sigs = []
            for i in range(depth):
                s = _spectral_signature(responses[i], codebook, N_use, top_k_eff)
                sigs.append(s)
            if trace: trace.record("time_compute_spectrum", _ns() - t1)

            if len(sigs) < 2:
                # Fall back: compare to destination
                dst = codebook[int(p[-1])]
                dst_sig = _spectral_signature(dst, codebook, N_use, top_k_eff)
                t2 = _ns()
                num = (sigs[0] * dst_sig).sum()
                den = (sigs[0].norm() * dst_sig.norm()).clamp_min(1e-9)
                score = float((num / den).item())
                if trace: trace.record("time_compare_spectra", _ns() - t2)
            else:
                t2 = _ns()
                cos = []
                for i in range(len(sigs) - 1):
                    a = sigs[i]
                    b = sigs[i + 1]
                    num = (a * b).sum()
                    den = (a.norm() * b.norm()).clamp_min(1e-9)
                    cos.append(num / den)
                score = float(torch.stack(cos).mean().item())
                if trace: trace.record("time_compare_spectra", _ns() - t2)

            t3 = _ns()
            scores.append(score)
            labels.append(which)
            if trace: trace.record("time_identify", _ns() - t3)

    # AUC via Mann-Whitney
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return 0.5
    n_correct = 0
    n_ties = 0
    for sp in pos:
        for sn in neg:
            if sp > sn:
                n_correct += 1
            elif sp == sn:
                n_ties += 1
    n_pairs = len(pos) * len(neg)
    if n_pairs == 0:
        return 0.5
    return (n_correct + 0.5 * n_ties) / n_pairs


# -------- Combined runners (joint mode) --------------------------------------

def run_all_paths_sequential(codebook, W, key_idx, val_idx, relation,
                              depth: int, n_paths: int, seed: int,
                              N_use: int, K_paths: int = 100) -> Dict:
    """Run B, D, E sequentially. Returns timing + accuracy per path."""
    device = codebook.device
    starts = torch.tensor([k for k in list(relation.keys())[:n_paths]],
                          dtype=torch.long, device=device)
    pos_paths = sample_coherent_starts(relation, depth, n_paths, seed)
    neg_paths = sample_incoherent_paths(codebook.shape[0], depth, n_paths,
                                          seed, relation=relation)

    out: Dict = {}
    t0 = _ns()
    pred_b = path_b_run(codebook, W, starts, depth, N_use)
    targets = []
    for k in starts.tolist():
        cur = int(k)
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = int(nxt)
        targets.append(cur if ok else -1)
    targets_t = torch.tensor(targets, dtype=torch.long, device=device)
    valid = targets_t >= 0
    if valid.any():
        out["path_b_acc"] = float(
            (pred_b[valid] == targets_t[valid]).float().mean().item())
    else:
        out["path_b_acc"] = 0.0
    out["path_b_ns"] = _ns() - t0

    t1 = _ns()
    correct_d = path_d_run(codebook, W, starts, relation, depth, K_paths,
                            seed, N_use)
    out["path_d_acc"] = float(correct_d.mean().item())
    out["path_d_ns"] = _ns() - t1

    t2 = _ns()
    if pos_paths and neg_paths:
        auc_e = path_e_run(codebook, W, pos_paths, neg_paths, N_use)
    else:
        auc_e = 0.5
    out["path_e_auc"] = auc_e
    out["path_e_ns"] = _ns() - t2

    return out


def run_all_paths_joint(codebook, W, key_idx, val_idx, relation,
                         depth: int, n_paths: int, seed: int,
                         N_use: int, K_paths: int = 100) -> Dict:
    """Run B, D, E sharing one substrate state + one codebook in parallel.

    Joint mode: do the W-multiplies once for paths B and D where overlapping;
    Share path sampling between D and E.
    """
    device = codebook.device
    pos_paths = sample_coherent_starts(relation, depth, n_paths, seed)
    neg_paths = sample_incoherent_paths(codebook.shape[0], depth, n_paths,
                                          seed, relation=relation)

    out: Dict = {}
    t_joint = _ns()

    starts = torch.tensor([p[0] for p in pos_paths if len(p) == depth + 1],
                          dtype=torch.long, device=device)
    if starts.shape[0] == 0:
        out["path_b_acc"] = 0.0
        out["path_d_acc"] = 0.0
        out["path_e_auc"] = 0.5
        out["joint_ns"] = _ns() - t_joint
        return out

    # Single shared W-traversal for Path B
    q = codebook[starts].clone()
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    pred_b = torch.argmax(sims, dim=0)

    # Build targets
    targets = torch.tensor([p[-1] for p in pos_paths if len(p) == depth + 1],
                            dtype=torch.long, device=device)
    out["path_b_acc"] = float((pred_b == targets).float().mean().item())

    # Path D using same starts
    correct_d = path_d_run(codebook, W, starts, relation, depth, K_paths,
                            seed, N_use)
    out["path_d_acc"] = float(correct_d.mean().item())

    # Path E shares pos_paths / neg_paths sampling
    auc_e = path_e_run(codebook, W, pos_paths, neg_paths, N_use)
    out["path_e_auc"] = auc_e

    out["joint_ns"] = _ns() - t_joint
    return out


# -------- Module selftest -----------------------------------------------------

def _selftest() -> None:
    device = torch.device("cpu")
    N_use = 1024  # Kerdock requires N in {1024, 4096, 16384}
    M = 16
    seed = 17
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    assert codebook.dim() == 2
    assert W.shape == (N_use, N_use)
    assert isinstance(relation, dict) and len(relation) == M

    # Path B
    starts = torch.tensor(list(relation.keys())[:4], dtype=torch.long,
                          device=device)
    tr = TimingTrace()
    pred = path_b_run(codebook, W, starts, depth=2, N_use=N_use, trace=tr)
    assert pred.shape == (4,)
    assert "time_W_kquery_per_hop" in tr.ops

    # Path D
    tr2 = TimingTrace()
    correct = path_d_run(codebook, W, starts, relation, depth=2, K_paths=10,
                          seed=seed, N_use=N_use, trace=tr2)
    assert correct.shape == (4,)
    assert "time_likelihood_query_per_hop" in tr2.ops

    # Path E
    pos = sample_coherent_starts(relation, depth=2, n_paths=4, seed=seed)
    neg = sample_incoherent_paths(codebook.shape[0], depth=2, n_paths=4,
                                    seed=seed, relation=relation)
    tr3 = TimingTrace()
    if pos and neg:
        auc = path_e_run(codebook, W, pos, neg, N_use, trace=tr3)
        assert 0.0 <= auc <= 1.0

    # Joint vs sequential
    seq = run_all_paths_sequential(codebook, W, key_idx, val_idx, relation,
                                     depth=2, n_paths=4, seed=seed,
                                     N_use=N_use, K_paths=5)
    joint = run_all_paths_joint(codebook, W, key_idx, val_idx, relation,
                                  depth=2, n_paths=4, seed=seed,
                                  N_use=N_use, K_paths=5)
    assert "path_b_acc" in seq and "path_b_acc" in joint

    print("[selftest] _multi_hop_mechanisms PASS", flush=True)


_selftest()


__all__ = [
    "TimingTrace",
    "build_shared",
    "path_b_run",
    "path_d_run",
    "path_e_run",
    "run_all_paths_sequential",
    "run_all_paths_joint",
]
