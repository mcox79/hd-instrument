"""SPECTRAL PATH IDENTIFICATION v1 at N=4096 (Path E).

CONTEXT (Multi-hop Path E):
  KF-45 spectral channel passed 1/3 at commit 919a901. Hypothesis: spectral
  COHERENCE across hops (alignment of substrate-response spectra) carries
  multi-hop path information even when state-domain readout degrades.

  Per [[feedback-lit-scan-calibration-penalty]] this is a research-quality
  test (P=0.30-0.40); HP would be a substantive surprise.

SCIENTIFIC QUESTION:
  At N=4096, M=256, depth in {2, 3}: does cross-hop spectral coherence
  yield an AUC >= 0.80 for separating coherent paths from incoherent ones
  in >= 3/5 seeds?

PRE-REGISTERED BANDS:
  HP = spectral-coherence AUC >= 0.80 at depth 3 in >= 3/5 seeds.
  HF = AUC <= 0.55 at every depth in {2,3} in >= 3/5 seeds. (no spectral
       signal beyond chance.)
  MIDDLE_BAND = otherwise.

UNCERTAINTY: this is exploratory; P(HP)=0.30-0.40. Annotated in prereg.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. depths = [2, 3].
  3. spectral signature of a substrate response r = (codebook @ r) / N.
     Top-K eigenvalue alignment across hops = cosine of top-K signatures.
  4. coherence score = mean cosine of consecutive-hop signature pairs.
  5. AUC: roc_auc_score(labels, coherence_scores) where label=1 coherent.

OOM CHECK:
  M=256: same envelope as N2, N3. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 30s. FULL: 2 depths x 5 seeds = 10 cells x ~120s = 1200s. 21600s budget.

N-suffix: _n4096 (PROT-018).
Anchor: spectral_path_identification_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_spectral_path_identification_v1_n4096.md
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

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n4", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 256
M_SMOKE = 32
DEPTHS_FULL  = [2, 3]
DEPTHS_SMOKE = [2]
N_POS_FULL  = 80
N_NEG_FULL  = 80
N_POS_SMOKE = 16
N_NEG_SMOKE = 16
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
TOP_K_SIG = 16

HP_AUC = 0.80
HP_DEPTH = 3
HF_AUC = 0.55
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def get_output_dir(default_name: str = "spectral_path_identification_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=codebook.shape[0], M=M, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def spectral_signature(response: torch.Tensor, codebook: torch.Tensor,
                        N_use: int, top_k: int) -> torch.Tensor:
    """Take a substrate response vector (N,), project to codebook similarity,
    return the top_k similarity values as a fingerprint (top_k,)."""
    sims = (codebook @ response) / N_use     # (C,)
    top = torch.topk(sims, top_k).values
    return top


def coherence_score(codebook: torch.Tensor, W: torch.Tensor,
                     path: List[int], N_use: int, top_k: int) -> float:
    """Walk a path and compute mean cos-similarity of consecutive signatures.

    Hop i: response_i = codebook[path[i]] @ W.T = (N,)
    signature_i = top-k projection of response_i.
    coherence = mean over consecutive i of cos(sig_i, sig_{i+1}).
    """
    depth = len(path) - 1
    if depth < 1:
        return 0.0
    # All hop responses as a single batched matmul
    src = codebook[torch.tensor(path[:-1], dtype=torch.long,
                                 device=codebook.device)]   # (depth, N)
    responses = src @ W.T                                    # (depth, N)
    # Per-row signatures
    sigs = []
    for i in range(depth):
        s = spectral_signature(responses[i], codebook, N_use, top_k)
        sigs.append(s)
    if len(sigs) < 2:
        # depth=1: there is only one signature; compare to the destination
        dst = codebook[path[-1]]
        s_dst = spectral_signature(dst, codebook, N_use, top_k)
        v0 = sigs[0]
        c = torch.nn.functional.cosine_similarity(
            v0.unsqueeze(0), s_dst.unsqueeze(0)).item()
        return float(c)
    coh = []
    for i in range(len(sigs) - 1):
        c = torch.nn.functional.cosine_similarity(
            sigs[i].unsqueeze(0), sigs[i + 1].unsqueeze(0)).item()
        coh.append(c)
    return float(sum(coh) / len(coh))


def roc_auc(labels: List[int], scores: List[float]) -> float:
    """Compute AUC without sklearn. Returns 0.5 if degenerate.

    Mann-Whitney U formulation: sort scores ASCENDING, sum the ranks of
    positives, then AUC = (sum_pos_ranks - n_pos*(n_pos+1)/2) / (n_pos*n_neg).
    Higher score -> positive label increases AUC.
    """
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    # Sort ascending so that high-score items get high ranks
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    sum_pos_ranks = 0
    for rank, (score, lab) in enumerate(pairs, start=1):
        if lab == 1:
            sum_pos_ranks += rank
    u = sum_pos_ranks - n_pos * (n_pos + 1) / 2
    auc = u / (n_pos * n_neg)
    return float(auc)


def measure_cell(N_use: int, M: int, depth: int, n_pos: int, n_neg: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_pos, seed=seed + depth)
    if not pos_paths:
        return {"depth": int(depth), "M": int(M), "seed": int(seed),
                "n_pos": 0, "n_neg": 0, "auc": 0.5}
    n_pos_have = len(pos_paths)
    neg_paths = sample_incoherent_paths(codebook.shape[0], depth=depth,
                                          n_paths=n_neg, seed=seed + depth,
                                          relation=relation)
    if not neg_paths:
        return {"depth": int(depth), "M": int(M), "seed": int(seed),
                "n_pos": n_pos_have, "n_neg": 0, "auc": 0.5}

    scores: List[float] = []
    labels: List[int] = []
    for p in pos_paths:
        scores.append(coherence_score(codebook, W, p, N_use, TOP_K_SIG))
        labels.append(1)
    for p in neg_paths:
        scores.append(coherence_score(codebook, W, p, N_use, TOP_K_SIG))
        labels.append(0)
    auc = roc_auc(labels, scores)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"depth": int(depth), "M": int(M), "seed": int(seed),
            "n_pos": n_pos_have, "n_neg": len(neg_paths),
            "auc": round(auc, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SPEC_PATH_INCONCLUSIVE", "No cells.")

    by_depth: Dict[int, List[Dict]] = {}
    for c in cells:
        by_depth.setdefault(c["depth"], []).append(c)
    # HP: at HP_DEPTH, AUC>=HP_AUC in >=HP_SEEDS_MIN seeds.
    eligible = [c for c in cells if c["depth"] == HP_DEPTH]
    hp_pass = sum(1 for c in eligible if c["auc"] >= HP_AUC)
    # HF: at EVERY depth, AUC<=HF in >=HF_SEEDS_MIN seeds.
    hf_depths = 0
    for d, cs in by_depth.items():
        n_fail = sum(1 for c in cs if c["auc"] <= HF_AUC)
        if n_fail >= HF_SEEDS_MIN:
            hf_depths += 1

    means = {d: round(sum(c["auc"] for c in cs) / max(1, len(cs)), 4)
             for d, cs in by_depth.items()}
    detail = (f"depth_means={means} hp_pass={hp_pass}/{len(eligible)} "
              f"hf_depths={hf_depths}/{len(by_depth)}")

    if hf_depths >= len(by_depth):
        return ("SPEC_PATH_HARD_FAIL", "NO_SPECTRAL_SIGNAL: " + detail)
    if hp_pass >= HP_SEEDS_MIN:
        return ("SPEC_PATH_HARD_PASS", "SPECTRAL_COHERENCE_DETECTED: " + detail)
    return ("SPEC_PATH_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # AUC self-test
    auc = roc_auc([1, 1, 0, 0], [0.9, 0.8, 0.4, 0.2])
    assert auc == 1.0, f"AUC sanity: {auc}"
    auc = roc_auc([1, 0, 1, 0], [0.4, 0.9, 0.2, 0.8])
    assert auc < 0.5, f"AUC reversed: {auc}"

    # Verdict gates
    fake_hp = [{"depth": HP_DEPTH, "M": M_FULL, "seed": s,
                 "n_pos": N_POS_FULL, "n_neg": N_NEG_FULL,
                 "auc": 0.90} for s in SEEDS_FULL]
    fake_hp += [{"depth": 2, "M": M_FULL, "seed": s,
                  "n_pos": N_POS_FULL, "n_neg": N_NEG_FULL,
                  "auc": 0.60} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for d in DEPTHS_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({"depth": d, "M": M_FULL, "seed": s,
                              "n_pos": N_POS_FULL, "n_neg": N_NEG_FULL,
                              "auc": 0.50})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, depth=2, n_pos=8, n_neg=8,
                        seed=17, device=device)
    assert out["auc"] is not None and 0.0 <= out["auc"] <= 1.0
    print(f"[selftest] spectral_path_identification_v1_n4096 PASS "
          f"smoke d=2 AUC={out['auc']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_pos  = N_POS_SMOKE if smoke else N_POS_FULL
    n_neg  = N_NEG_SMOKE if smoke else N_NEG_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] spectral_path_identification_v1 smoke={smoke} N={N_cfg} "
          f"M={M_cfg} depths={depths} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for d in depths:
        for seed in seeds:
            ck = f"d{d}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M_cfg, d, n_pos, n_neg, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  d={d} seed={seed} AUC={out['auc']:.3f} "
                      f"n_pos={out['n_pos']} n_neg={out['n_neg']} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  d={d} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "spectral_path_identification_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "depths": depths, "seeds": seeds,
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
