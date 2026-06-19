"""Quick local diagnostic: run CLOUD-1's retrieval pipeline on Pythia-160M.

Goal: disambiguate whether CLOUD-1's 0.000 retrieval on Llama-3.1-8B is a
pipeline bug or genuine "mid-layer-base-LLM embeddings can't retrieve."

Same pipeline as exp_substrate_extraction_quality_7B_vs_70B_v1.py:
  - SQuAD-v2 dev set: 1000 unique passages + 100 answerable questions
  - mean-pool hidden_states from layer ~50pct depth
  - random-project to N=4096 with seed=1729
  - top-5 cosine retrieval

PLUS diagnostics CLOUD-1 lacked:
  - Concentration of gold_indices (how many unique passages do the 100 queries point to)
  - Per-query gold-passage rank statistics (median, p25, p50, p75, p95)
  - Embedding norm + pairwise-similarity statistics
  - Last-token-pool retrieval as a baseline comparison

Runs on the local 4060 Ti via ssh marsh@home; Pythia weights cached locally.
"""
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import sys, time, math
from pathlib import Path
from typing import List, Tuple, Dict

import torch
import torch.nn.functional as F
import numpy as np

MODEL_ID = "EleutherAI/pythia-160m"
LAYER_IDX = 6   # mid-depth of 12 layers
N_SUBSTRATE = 4096
TOP_K = 5
MAX_TOK = 256
N_PASSAGES = 1000
N_QUERIES = 100
RP_SEED = 1729


def random_projection_matrix(input_dim, output_dim, seed):
    g = torch.Generator().manual_seed(seed)
    return torch.randn(input_dim, output_dim, generator=g) / math.sqrt(output_dim)


def mean_pool(hs, am):
    am = am.unsqueeze(-1).to(hs.dtype)
    summed = (hs * am).sum(dim=1)
    counts = am.sum(dim=1).clamp_min(1.0)
    return summed / counts


def last_token_pool(hs, am):
    """Pool the LAST non-pad token's hidden state. am: (B,T) 1=valid 0=pad."""
    # Find last valid index per row
    am_int = am.long()
    last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)  # (B,)
    batch_idx = torch.arange(hs.size(0), device=hs.device)
    return hs[batch_idx, last_idx]


def top_k_retrieval_acc(query_sub, corpus_sub, gold_indices, k):
    qn = F.normalize(query_sub, dim=-1)
    cn = F.normalize(corpus_sub, dim=-1)
    sims = qn @ cn.t()
    _, topk = sims.topk(k, dim=-1)
    hits = sum(1 for i, g in enumerate(gold_indices) if g in topk[i].tolist())
    return hits / len(gold_indices), sims


def gold_rank_stats(sims, gold_indices):
    """Per-query rank of the gold passage (1 = best, 1000 = worst). Returns dict."""
    ranks = []
    for i, g in enumerate(gold_indices):
        s_q = sims[i]  # (C,)
        # rank = number of passages with sim >= s_q[g], so gold's rank
        gold_sim = s_q[g]
        rank = int((s_q > gold_sim).sum().item()) + 1  # 1-based
        ranks.append(rank)
    ranks_np = np.array(ranks)
    return {
        "median_rank": int(np.median(ranks_np)),
        "p25_rank": int(np.percentile(ranks_np, 25)),
        "p75_rank": int(np.percentile(ranks_np, 75)),
        "p95_rank": int(np.percentile(ranks_np, 95)),
        "min_rank": int(ranks_np.min()),
        "max_rank": int(ranks_np.max()),
        "n_in_top_5": int((ranks_np <= 5).sum()),
        "n_in_top_50": int((ranks_np <= 50).sum()),
        "n_in_top_100": int((ranks_np <= 100).sum()),
    }


def load_squad_v2_dev():
    from datasets import load_dataset
    # rajpurkar/squad_v2 is the canonical namespace/name (datasets library
    # now requires namespace/name for HF dataset URIs).
    ds = load_dataset("rajpurkar/squad_v2", split="validation")
    seen = {}
    passages = []
    for ex in ds:
        ctx = ex["context"]
        if ctx not in seen:
            seen[ctx] = len(passages)
            passages.append(ctx)
        if len(passages) >= N_PASSAGES:
            break
    questions = []
    gold_indices = []
    for ex in ds:
        ctx = ex["context"]
        if ctx in seen and len(ex["answers"]["text"]) > 0:
            questions.append(ex["question"])
            gold_indices.append(seen[ctx])
            if len(questions) >= N_QUERIES:
                break
    return passages, questions, gold_indices


def extract_hidden_states(model, tokenizer, texts, layer_idx, batch_size=8, device="cuda"):
    model.eval()
    pooled_mean = []
    pooled_last = []
    norms = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, truncation=True, max_length=MAX_TOK,
                            return_tensors="pt").to(device)
            out = model(input_ids=enc["input_ids"],
                        attention_mask=enc["attention_mask"],
                        output_hidden_states=True,
                        use_cache=False)
            hs = out.hidden_states[layer_idx]  # (B, T, H)
            am = enc["attention_mask"].float()
            p_mean = mean_pool(hs.float(), am)
            p_last = last_token_pool(hs.float(), am.long())
            pooled_mean.append(p_mean.cpu())
            pooled_last.append(p_last.cpu())
            norms.append(p_mean.norm(dim=-1).cpu())
    return torch.cat(pooled_mean, 0), torch.cat(pooled_last, 0), torch.cat(norms, 0)


def main():
    print(f"[config] model={MODEL_ID} layer={LAYER_IDX} N_passages={N_PASSAGES} N_queries={N_QUERIES} top_k={TOP_K}", flush=True)
    print(f"[gpu] {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}", flush=True)

    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[data] loading squad_v2 dev ...", flush=True)
    passages, questions, gold_indices = load_squad_v2_dev()
    print(f"[data] {len(passages)} passages + {len(questions)} questions loaded", flush=True)

    # KEY DIAGNOSTIC: how concentrated are gold_indices?
    unique_gold = set(gold_indices)
    print(f"[diag] gold_indices: {len(unique_gold)} unique passages out of 1000", flush=True)
    print(f"[diag] gold_indices min={min(gold_indices)} max={max(gold_indices)} "
          f"first10={gold_indices[:10]}", flush=True)

    print(f"[load] {MODEL_ID} ...", flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float32).to("cuda")
    print(f"[load] done in {time.time()-t0:.1f}s", flush=True)

    print(f"[extract] passages ...", flush=True)
    t0 = time.time()
    pas_mean, pas_last, pas_norms = extract_hidden_states(model, tok, passages, LAYER_IDX)
    print(f"[extract] passages done in {time.time()-t0:.1f}s; shape={tuple(pas_mean.shape)}", flush=True)
    print(f"[extract] queries ...", flush=True)
    t0 = time.time()
    q_mean, q_last, q_norms = extract_hidden_states(model, tok, questions, LAYER_IDX)
    print(f"[extract] queries done in {time.time()-t0:.1f}s", flush=True)

    print(f"[diag] passage mean-pool norm: median={pas_norms.median():.2f} min={pas_norms.min():.2f} max={pas_norms.max():.2f}", flush=True)
    print(f"[diag] query   mean-pool norm: median={q_norms.median():.2f} min={q_norms.min():.2f} max={q_norms.max():.2f}", flush=True)

    # Random projection (same as CLOUD-1)
    hidden_dim = pas_mean.shape[1]
    P = random_projection_matrix(hidden_dim, N_SUBSTRATE, seed=RP_SEED)

    # === MEAN-POOL pipeline (CLOUD-1's choice) ===
    pas_sub_mean = pas_mean @ P
    q_sub_mean = q_mean @ P
    acc1_mean, sims_mean = top_k_retrieval_acc(q_sub_mean, pas_sub_mean, gold_indices, k=1)
    acck_mean, _ = top_k_retrieval_acc(q_sub_mean, pas_sub_mean, gold_indices, k=TOP_K)
    rank_mean = gold_rank_stats(sims_mean, gold_indices)
    print(f"\n=== MEAN-POOL retrieval (CLOUD-1's choice) ===", flush=True)
    print(f"  top-1={acc1_mean:.3f}  top-5={acck_mean:.3f}", flush=True)
    print(f"  gold-rank stats: {rank_mean}", flush=True)

    # === LAST-TOKEN pool (causal-LM-appropriate) ===
    pas_sub_last = pas_last @ P
    q_sub_last = q_last @ P
    acc1_last, sims_last = top_k_retrieval_acc(q_sub_last, pas_sub_last, gold_indices, k=1)
    acck_last, _ = top_k_retrieval_acc(q_sub_last, pas_sub_last, gold_indices, k=TOP_K)
    rank_last = gold_rank_stats(sims_last, gold_indices)
    print(f"\n=== LAST-TOKEN pool ===", flush=True)
    print(f"  top-1={acc1_last:.3f}  top-5={acck_last:.3f}", flush=True)
    print(f"  gold-rank stats: {rank_last}", flush=True)

    # === RAW hidden_states (no random projection, direct cosine) ===
    acc1_raw, sims_raw = top_k_retrieval_acc(q_mean, pas_mean, gold_indices, k=1)
    acck_raw, _ = top_k_retrieval_acc(q_mean, pas_mean, gold_indices, k=TOP_K)
    rank_raw = gold_rank_stats(sims_raw, gold_indices)
    print(f"\n=== MEAN-POOL + NO random projection (direct hidden_state cosine) ===", flush=True)
    print(f"  top-1={acc1_raw:.3f}  top-5={acck_raw:.3f}", flush=True)
    print(f"  gold-rank stats: {rank_raw}", flush=True)

    # Verdict
    print(f"\n=== VERDICT ===", flush=True)
    if max(acck_mean, acck_last, acck_raw) < 0.02:
        print(f"  PIPELINE BROKEN: all variants near-zero on Pythia-160M.", flush=True)
        print(f"  Likely cause: SQuAD-v2 gold-index concentration ({len(unique_gold)} unique) "
              f"vs ranking bias.", flush=True)
    elif acck_last > acck_mean * 1.5:
        print(f"  LAST-TOKEN pool dominates -- mean-pool is the bug in CLOUD-1.", flush=True)
    elif acck_raw > acck_mean * 1.5:
        print(f"  Random projection is destroying signal.", flush=True)
    else:
        print(f"  Pipeline functions. CLOUD-1's 0.000 on 8B is real model weakness, not pipeline bug.", flush=True)


if __name__ == "__main__":
    main()
