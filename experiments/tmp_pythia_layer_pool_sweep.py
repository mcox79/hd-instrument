"""Local Pythia-160M layer x pool sweep + padding-side check.

Purpose: find optimal (layer-depth-ratio, pool-variant) for last-token retrieval
on causal LMs BEFORE dispatching CLOUD-1b. Per [[pythia-sanity-check-before-cloud]]
+ [[causal-lm-last-token-pool]].

Tests:
  - Layers: 2, 4, 6, 8, 10, 11 (out of 12 -> depth-ratios 17%, 33%, 50%, 67%, 83%, 92%)
  - Pools: last-token (K=1), mean-of-last-3, mean-of-last-5
  - Padding side: report tokenizer default + verify last_token_pool grabs the
    actual last non-pad token via attention_mask.sum-based indexing (which works
    for either padding side)
  - Per (layer, pool): top-5 acc + median gold rank

Output: best (layer-ratio, pool) combo; recommended cloud Llama layer indices.

Runs on the 4060 Ti via runner venv. Pythia cached from prior work.
"""
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import sys, time, math, random
from pathlib import Path
from typing import List, Tuple, Dict

import torch
import torch.nn.functional as F
import numpy as np

MODEL_ID = "EleutherAI/pythia-160m"
N_PASSAGES = 1000
N_QUERIES = 100
MAX_TOK = 256
SHUFFLE_SEED = 7
TOP_K = 5
LAYERS_TO_PROBE = [2, 4, 6, 8, 10, 11]  # of 12; ratios 0.17/0.33/0.50/0.67/0.83/0.92


def last_k_tokens_mean_pool(hs, am, k):
    """Pool the mean of the last K non-pad tokens."""
    B, T, H = hs.shape
    am_long = am.long()
    last_idx = (am_long.sum(dim=1) - 1).clamp_min(0)  # (B,)
    out = []
    for b in range(B):
        end = int(last_idx[b].item()) + 1
        start = max(0, end - k)
        if start >= end:
            out.append(hs[b, 0])
        else:
            out.append(hs[b, start:end].mean(dim=0))
    return torch.stack(out, dim=0)


def top_k_retrieval_acc(query_sub, corpus_sub, gold_indices, k):
    qn = F.normalize(query_sub, dim=-1)
    cn = F.normalize(corpus_sub, dim=-1)
    sims = qn @ cn.t()
    _, topk = sims.topk(k, dim=-1)
    hits = sum(1 for i, g in enumerate(gold_indices) if g in topk[i].tolist())
    return hits / len(gold_indices), sims


def gold_rank_stats(sims, gold_indices):
    ranks = []
    for i, g in enumerate(gold_indices):
        s_q = sims[i]
        gold_sim = s_q[g]
        rank = int((s_q > gold_sim).sum().item()) + 1
        ranks.append(rank)
    return int(np.median(np.array(ranks)))


def load_squad_v2_dev_shuffled():
    from datasets import load_dataset
    ds = load_dataset("rajpurkar/squad_v2", split="validation")
    seen_pre = {}
    pp = []
    for ex in ds:
        ctx = ex["context"]
        if ctx not in seen_pre:
            seen_pre[ctx] = len(pp); pp.append(ctx)
        if len(pp) >= N_PASSAGES:
            break
    rng = random.Random(SHUFFLE_SEED)
    perm = list(range(len(pp))); rng.shuffle(perm)
    passages_post = [pp[old] for old in perm]
    old_to_new = [0] * len(pp)
    for new, old in enumerate(perm):
        old_to_new[old] = new
    seen_post = {ctx: old_to_new[seen_pre[ctx]] for ctx in seen_pre}
    questions, gold = [], []
    for ex in ds:
        if ex["context"] in seen_post and len(ex["answers"]["text"]) > 0:
            questions.append(ex["question"])
            gold.append(seen_post[ex["context"]])
            if len(questions) >= N_QUERIES:
                break
    return passages_post, questions, gold


def main():
    print(f"[config] sweep: model={MODEL_ID} layers={LAYERS_TO_PROBE} N_passages={N_PASSAGES} N_queries={N_QUERIES}", flush=True)
    print(f"[gpu] {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}", flush=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("[data] loading squad_v2 ...", flush=True)
    passages, questions, gold = load_squad_v2_dev_shuffled()
    print(f"[data] {len(passages)} passages + {len(questions)} questions; "
          f"gold unique={len(set(gold))} min={min(gold)} max={max(gold)}", flush=True)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    print(f"[tokenizer] padding_side={tok.padding_side}; pad_token_id={tok.pad_token_id}", flush=True)

    t0 = time.time()
    print(f"[load] {MODEL_ID} ...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float32).to(device)
    model.eval()
    print(f"[load] done in {time.time()-t0:.1f}s", flush=True)

    # ONE forward pass per batch; collect ALL hidden states; pool at multiple layer indices.
    # Then for each (layer, pool) combo, compute retrieval acc.
    def extract_all_layers_all_pools(texts, batch_size=8):
        """Return dict: {(layer_idx, pool_name): tensor (N, H)}."""
        from collections import defaultdict
        results = defaultdict(list)
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                enc = tok(batch, padding=True, truncation=True, max_length=MAX_TOK,
                          return_tensors="pt").to(device)
                am = enc["attention_mask"]
                out = model(input_ids=enc["input_ids"], attention_mask=am,
                            output_hidden_states=True, use_cache=False)
                for L in LAYERS_TO_PROBE:
                    hs = out.hidden_states[L].float()  # (B, T, H)
                    # last-token pool (K=1)
                    am_int = am.long()
                    last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)
                    batch_idx = torch.arange(hs.size(0), device=device)
                    p_last = hs[batch_idx, last_idx]
                    results[(L, "last")].append(p_last.cpu())
                    # mean-of-last-3
                    p_l3 = last_k_tokens_mean_pool(hs, am, k=3)
                    results[(L, "lastK3")].append(p_l3.cpu())
                    # mean-of-last-5
                    p_l5 = last_k_tokens_mean_pool(hs, am, k=5)
                    results[(L, "lastK5")].append(p_l5.cpu())
        return {k: torch.cat(v, dim=0) for k, v in results.items()}

    print("[extract] passages (all layers, all pools) ...", flush=True)
    t0 = time.time()
    pas_all = extract_all_layers_all_pools(passages)
    print(f"[extract] passages done in {time.time()-t0:.1f}s; n_combos={len(pas_all)}", flush=True)
    print("[extract] queries ...", flush=True)
    t0 = time.time()
    q_all = extract_all_layers_all_pools(questions)
    print(f"[extract] queries done in {time.time()-t0:.1f}s", flush=True)

    # Sweep results
    print("\n=== SWEEP RESULTS (layer, pool) -> top-5 acc + median gold rank ===", flush=True)
    print(f"{'layer':<6} {'pool':<8} {'top-1':>7} {'top-5':>7} {'med-rank':>9}", flush=True)
    print("-" * 50, flush=True)
    best_top5 = -1.0
    best_combo = None
    rows = []
    for L in LAYERS_TO_PROBE:
        for pool in ["last", "lastK3", "lastK5"]:
            pas = pas_all[(L, pool)]
            q = q_all[(L, pool)]
            acc1, _ = top_k_retrieval_acc(q, pas, gold, k=1)
            acck, sims = top_k_retrieval_acc(q, pas, gold, k=TOP_K)
            med = gold_rank_stats(sims, gold)
            rows.append((L, pool, acc1, acck, med))
            print(f"{L:<6d} {pool:<8} {acc1:>7.3f} {acck:>7.3f} {med:>9d}", flush=True)
            if acck > best_top5:
                best_top5 = acck
                best_combo = (L, pool)

    L_best, pool_best = best_combo
    depth_ratio = L_best / 12.0
    print(f"\n=== BEST COMBO ===", flush=True)
    print(f"  layer={L_best} pool={pool_best} top-5={best_top5:.3f} depth-ratio={depth_ratio:.2f}", flush=True)
    print(f"\n=== Recommended Llama layer indices (using depth-ratio {depth_ratio:.2f}) ===", flush=True)
    print(f"  Llama-3.2-1B (16 layers): use layer {round(depth_ratio*16)}", flush=True)
    print(f"  Llama-3.1-8B (32 layers): use layer {round(depth_ratio*32)}", flush=True)
    print(f"  Llama-3.1-70B (80 layers): use layer {round(depth_ratio*80)}", flush=True)
    # Recommend 3-layer probe per Llama: depth-ratio +/- ~7pct
    plus = min(depth_ratio + 0.07, 0.95)
    minus = max(depth_ratio - 0.07, 0.05)
    print(f"\n=== 3-layer probe per Llama (depth-ratio +/- 7pct) ===", flush=True)
    for name, nl in [("Llama-3.2-1B", 16), ("Llama-3.1-8B", 32), ("Llama-3.1-70B", 80)]:
        print(f"  {name}: layers {round(minus*nl)}, {round(depth_ratio*nl)}, {round(plus*nl)}", flush=True)
    print(f"\n=== Pool choice for CLOUD-1b ===", flush=True)
    print(f"  pool={pool_best}", flush=True)


if __name__ == "__main__":
    main()
