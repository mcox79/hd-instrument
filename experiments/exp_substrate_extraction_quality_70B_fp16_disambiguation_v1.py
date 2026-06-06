"""substrate_extraction_quality_70B_fp16_disambiguation_v1 -- CELL-1 follow-up to CLOUD-1b.

ROUTING: research_to_testbed_CLOUD1b_HP_ack_fp16_70B_followup_authorized_2026-06-06.
QUESTION: was CLOUD-1b's 70B late-layer retrieval CRASH (L=40 -> L=74: 0.146 -> 0.054)
  caused by bitsandbytes NF4 4-bit quantization noise compounding with depth, OR is it
  a real architectural / training artifact of Llama-3.1-70B (information compression
  collapses for retrieval in late layers regardless of precision)?

DESIGN:
  - Same pipeline as v2 (last-token pool, 5-layer probe, 500 queries, shuffled gold)
  - Test 70B at FP16 (no quantization) AND NF4 (CLOUD-1b's setting -- as baseline)
  - Optional: Llama-3.1-70B-Instruct at NF4 -- binds base-vs-Instruct retrieval quality
  - fp16 70B = ~140 GB; needs H100:2 SXM5 (160 GB) or device_map='auto' offload

INTERPRETATION:
  - If fp16 70B late-layer top-5 stays > 0.10:
      NF4 quantization noise was the late-layer crash cause.
      Cheap-fleet thesis holds: NF4 70B is the artifact, not architectural.
  - If fp16 70B late-layer top-5 ALSO crashes < 0.10:
      Architectural / training artifact in Llama-3.1-70B late layers.
      Genuinely interesting finding about how 70B compresses information.

PRE-REG bands (informational; not binding-test since CLOUD-1b already HP'd):
  CLEAR-FP16-EFFECT: fp16 L=74 top-5 > 2 * NF4 L=74 top-5 (i.e., > 0.108)
  MARGINAL:          fp16 L=74 top-5 in [1.5x, 2x] NF4
  NF4-NOT-CAUSE:     fp16 L=74 top-5 <= 1.5x NF4 (architectural confirmed)

INFRA defenses (carries forward from CLOUD-1b proven):
  - TOKENIZERS_PARALLELISM=false BEFORE transformers import
  - PROT-022 import-time self-tests + --self-test gate
  - File-first HF token (Llama gated)
  - ASCII-only stdout (no em-dash, no emoji)
  - tokenizer.padding_side = 'right' forced (Llama defaults to left)
  - last-token pool (causal-LM-correct; NOT mean-pool)
  - Pythia local sanity check via --local-pythia
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse, time, math, random
from pathlib import Path
from typing import List, Tuple, Dict

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.nn.functional as F
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)
import numpy as np

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "substrate_extraction_quality_70B_fp16_disambiguation_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--local-pythia", action="store_true")
_ap.add_argument("--include-instruct", action="store_true",
                  help="Also test Llama-3.1-70B-Instruct NF4 (+~$0.65 cloud)")
_ARGS, _ = _ap.parse_known_args()

LOCAL_PYTHIA = _ARGS.local_pythia
INCLUDE_INSTRUCT = _ARGS.include_instruct

# Models
LLAMA_70B_BASE = "meta-llama/Llama-3.1-70B"
LLAMA_70B_INSTRUCT = "meta-llama/Llama-3.1-70B-Instruct"
PYTHIA = "EleutherAI/pythia-160m"  # local sanity rung

# Layer indices (SAME as CLOUD-1b 70B; 80 layers; depth-ratios 0.50/0.625/0.75/0.85/0.92)
LAYERS_70B = [40, 50, 60, 68, 74]
N_LAYERS_PYTHIA = 12
LAYERS_PYTHIA = [6, 8, 9, 10, 11]   # SAME depth ratios as v2

N_SUBSTRATE = 4096
TOP_K = 5
MAX_TOK = 256
SHUFFLE_SEED = 7      # SAME as CLOUD-1b v2 (deterministic; same passage shuffle)
RP_SEED = 1729

if RUN_MODE == "smoke":
    N_PASSAGES = 50
    N_QUERIES = 10
else:
    N_PASSAGES = 1000
    N_QUERIES = 500    # SAME as CLOUD-1b v2 for direct comparison


def _load_hf_token() -> str:
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    env_tok = os.environ.get("HF_TOKEN", "").strip()
    if env_tok:
        return env_tok
    raise RuntimeError("HF token not found at <repo>/.hf_token or $HF_TOKEN.")


def random_projection_matrix(input_dim, output_dim, seed):
    g = torch.Generator().manual_seed(seed)
    return torch.randn(input_dim, output_dim, generator=g) / math.sqrt(output_dim)


def last_token_pool(hs, am):
    """Pool the LAST non-pad token. CROSS-DEVICE SAFE: hs may be on cuda:1 under
    device_map='auto' sharding while am is on cuda:0 -- move indices to hs.device."""
    am_int = am.long()
    last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)
    # CRITICAL FIX (pressure-test 2026-06-06): under device_map='auto' the model
    # shards across GPUs and hidden_states for a given layer may live on cuda:1
    # while attention_mask lives on cuda:0. Cross-device indexing errors here.
    last_idx = last_idx.to(hs.device)
    batch_idx = torch.arange(hs.size(0), device=hs.device)
    return hs[batch_idx, last_idx]


def top_k_retrieval_acc(query_sub, corpus_sub, gold_indices, k):
    qn = F.normalize(query_sub, dim=-1)
    cn = F.normalize(corpus_sub, dim=-1)
    sims = qn @ cn.t()
    _, topk = sims.topk(k, dim=-1)
    hits = sum(1 for i, g in enumerate(gold_indices) if g in topk[i].tolist())
    return hits / len(gold_indices), sims


def gold_rank_stats(sims, gold_indices) -> Dict:
    ranks = []
    for i, g in enumerate(gold_indices):
        s_q = sims[i]
        gold_sim = s_q[g]
        rank = int((s_q > gold_sim).sum().item()) + 1
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


def _selftest():
    """PROT-022 selftests; identical to v2 + Pythia diagnostic."""
    hs = torch.tensor([[[1.0], [2.0], [3.0], [4.0]]])
    am = torch.tensor([[1, 1, 1, 0]])
    lt = last_token_pool(hs, am)
    assert lt.shape == (1, 1) and abs(float(lt[0, 0]) - 3.0) < 1e-5, f"last_token_pool got {lt}"

    sims = torch.tensor([[0.1, 0.5, 0.9], [0.9, 0.5, 0.1]])
    gs = gold_rank_stats(sims, [2, 0])
    assert gs["median_rank"] == 1

    P1 = random_projection_matrix(8, 16, seed=7)
    P2 = random_projection_matrix(8, 16, seed=7)
    assert torch.allclose(P1, P2)

    corpus = torch.randn(10, 32)
    acc, _ = top_k_retrieval_acc(corpus.clone(), corpus, list(range(10)), k=1)
    assert acc == 1.0

    print("[selftest] PASS: last_token_pool + gold_rank_stats + RP + top_k", flush=True)


_selftest()
if _ARGS.self_test:
    print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
    sys.exit(0)


if not torch.cuda.is_available():
    print("[FATAL] CUDA not available; this script is GPU-only.", flush=True)
    sys.exit(1)
DEVICE = torch.device("cuda")
print(f"[GPU] {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)", flush=True)
print(f"[GPU count] {torch.cuda.device_count()}", flush=True)


def load_squad_v2_dev_shuffled():
    """SAME as CLOUD-1b v2: load 1000 unique passages + 500 answerable questions;
    shuffle passages by SHUFFLE_SEED so gold_indices spread across full corpus."""
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
    perm = list(range(len(pp)))
    rng.shuffle(perm)
    passages_post = [pp[old] for old in perm]
    old_to_new = [0] * len(pp)
    for new, old in enumerate(perm):
        old_to_new[old] = new
    seen_post = {ctx: old_to_new[seen_pre[ctx]] for ctx in seen_pre}
    questions, gold_indices = [], []
    for ex in ds:
        ctx = ex["context"]
        if ctx in seen_post and len(ex["answers"]["text"]) > 0:
            questions.append(ex["question"])
            gold_indices.append(seen_post[ctx])
            if len(questions) >= N_QUERIES:
                break
    print(f"[data] {len(passages_post)} passages + {len(questions)} questions; "
          f"gold unique={len(set(gold_indices))} min={min(gold_indices)} max={max(gold_indices)} median={int(np.median(gold_indices))}",
          flush=True)
    return passages_post, questions, gold_indices


def extract_lasttoken_hidden_states_multi_layer(model, tokenizer, texts, layer_indices, batch_size=4):
    """ONE forward pass per batch; pool LAST non-pad token at MULTIPLE layer indices.
    batch_size=4 (smaller than v2's 8) because fp16 70B is huge."""
    model.eval()
    pooled = {L: [] for L in layer_indices}
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, truncation=True, max_length=MAX_TOK,
                            return_tensors="pt").to(DEVICE)
            out = model(input_ids=enc["input_ids"],
                        attention_mask=enc["attention_mask"],
                        output_hidden_states=True,
                        use_cache=False)
            am = enc["attention_mask"].long()
            for L in layer_indices:
                hs = out.hidden_states[L]
                p = last_token_pool(hs.float(), am)
                pooled[L].append(p.cpu())
    return {L: torch.cat(v, dim=0) for L, v in pooled.items()}


def run_70b(model_id: str, mode: str, passages, questions, gold_indices, hf_token: str) -> Dict:
    """Load 70B at fp16 OR NF4; extract last-token at 5 layers; compute retrieval per layer.
    mode in {'fp16', 'nf4'}. fp16 needs device_map='auto' + multi-GPU OR offload."""
    import gc
    from transformers import AutoModelForCausalLM, AutoTokenizer
    # CRITICAL (pressure-test fix): reset peak memory stats BEFORE this run so the
    # reported peak isn't carried over from a prior model in the same process.
    for d in range(torch.cuda.device_count()):
        torch.cuda.reset_peak_memory_stats(d)
    gc.collect()
    torch.cuda.empty_cache()
    t0 = time.time()
    print(f"[load] {model_id} mode={mode} probing layers={LAYERS_70B}", flush=True)
    if mode == "nf4":
        from transformers import BitsAndBytesConfig
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                  bnb_4bit_compute_dtype=torch.bfloat16,
                                  bnb_4bit_use_double_quant=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, token=hf_token, quantization_config=bnb,
            device_map="auto", torch_dtype=torch.bfloat16,
        )
    elif mode == "fp16":
        # CRITICAL (pressure-test fix): explicit max_memory caps so device_map doesn't
        # OOM. Detect per-GPU VRAM at runtime so the script runs on ANY of:
        #   - H100:2 SXM5 (2x 80 GB):  multi-GPU sharding, no offload needed (160 GB > 140 GB)
        #   - B200:1 SXM6 (1x 180 GB): single-GPU native fit, no offload needed
        #   - GH200:1 (1x 96 GB):      single-GPU + CPU offload (~44 GB to host)
        #   - 4xA100 40GB (4x 40 GB):  multi-GPU sharding
        #   - any future 1x or Nx GPU SKU with >=140 GB total fp16-fits
        n_gpus = torch.cuda.device_count()
        per_gpu_vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        # Leave 6-7pct headroom on each device for activations, CUDA context, KV cache.
        per_gpu_cap = max(20, int(per_gpu_vram_gb * 0.93))
        if n_gpus >= 2:
            # Multi-GPU shard across all GPUs; CPU as last-resort spill
            max_memory = {i: f"{per_gpu_cap}GiB" for i in range(n_gpus)}
            max_memory["cpu"] = "100GiB"
            scenario = f"multi-GPU shard (n={n_gpus}, per_gpu_vram={per_gpu_vram_gb:.0f}GB)"
        elif per_gpu_vram_gb >= 140:
            # Single-GPU native fit (B200 180GB; future H200 141GB; etc.)
            max_memory = {0: f"{per_gpu_cap}GiB"}  # no offload
            scenario = f"single-GPU native fit (per_gpu_vram={per_gpu_vram_gb:.0f}GB)"
        else:
            # Single-GPU + CPU offload (GH200 96GB; A100 40GB; H100 80GB)
            max_memory = {0: f"{per_gpu_cap}GiB", "cpu": "200GiB"}
            scenario = f"single-GPU + CPU offload (per_gpu_vram={per_gpu_vram_gb:.0f}GB)"
        print(f"  [fp16] {scenario}; max_memory={max_memory}", flush=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, token=hf_token, torch_dtype=torch.float16,
            device_map="auto", max_memory=max_memory,
        )
    else:
        raise ValueError(f"unknown mode: {mode}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"  # CRITICAL: Llama defaults to left
    t_load = time.time() - t0
    peak = torch.cuda.max_memory_allocated(0) / 1e9 if torch.cuda.device_count() == 1 else \
           sum(torch.cuda.max_memory_allocated(i) for i in range(torch.cuda.device_count())) / 1e9
    print(f"  [load] {t_load:.1f}s; combined GPU peak {peak:.2f} GB", flush=True)

    # Conservative batch sizes (pressure-test fix): fp16 70B at bs=1 to avoid
    # OOM on edge-case input lengths; NF4 70B at bs=2 (CLOUD-1b used bs=4 NF4
    # successfully on GH200 96 GB, but we're now on H100 80 GB GPUs so reduce).
    bs = 1 if mode == "fp16" else 2

    t0 = time.time()
    pas_by_L = extract_lasttoken_hidden_states_multi_layer(model, tokenizer, passages, LAYERS_70B, batch_size=bs)
    t_pass = time.time() - t0
    t0 = time.time()
    q_by_L = extract_lasttoken_hidden_states_multi_layer(model, tokenizer, questions, LAYERS_70B, batch_size=bs)
    t_q = time.time() - t0

    per_layer = {}
    best_L = LAYERS_70B[0]
    best_acck_rp = -1.0
    for L in LAYERS_70B:
        pas_hs = pas_by_L[L]
        q_hs = q_by_L[L]
        hidden_dim = pas_hs.shape[1]
        P = random_projection_matrix(hidden_dim, N_SUBSTRATE, seed=RP_SEED)
        pas_sub = pas_hs @ P
        q_sub = q_hs @ P
        acc1_raw, sims_raw = top_k_retrieval_acc(q_hs, pas_hs, gold_indices, k=1)
        acck_raw, _ = top_k_retrieval_acc(q_hs, pas_hs, gold_indices, k=TOP_K)
        acc1_rp, sims_rp = top_k_retrieval_acc(q_sub, pas_sub, gold_indices, k=1)
        acck_rp, _ = top_k_retrieval_acc(q_sub, pas_sub, gold_indices, k=TOP_K)
        rank_raw = gold_rank_stats(sims_raw, gold_indices)
        rank_rp = gold_rank_stats(sims_rp, gold_indices)
        per_layer[str(L)] = {
            "layer_idx": L, "hidden_dim": hidden_dim,
            "acc_top1_raw": acc1_raw, "acc_topk_raw": acck_raw,
            "acc_top1_rp": acc1_rp, "acc_topk_rp": acck_rp,
            "rank_raw": rank_raw, "rank_rp": rank_rp,
        }
        print(f"  [L={L}] raw top-5={acck_raw:.3f} med-rank={rank_raw['median_rank']} | "
              f"RP top-5={acck_rp:.3f} med-rank={rank_rp['median_rank']}", flush=True)
        if acck_rp > best_acck_rp:
            best_acck_rp = acck_rp; best_L = L

    print(f"  [{model_id} {mode} BEST] layer={best_L} top-5-RP={per_layer[str(best_L)]['acc_topk_rp']:.3f}", flush=True)
    # CRITICAL (pressure-test fix): aggressive cleanup so subsequent model load
    # gets a clean VRAM slate. del + gc.collect + empty_cache on all devices.
    del model, tokenizer
    gc.collect()
    for d in range(torch.cuda.device_count()):
        with torch.cuda.device(d):
            torch.cuda.empty_cache()
    print(f"  [cleanup] post-del GPU mem: " +
          ", ".join(f"cuda:{d}={torch.cuda.memory_allocated(d)/1e9:.1f}GB" for d in range(torch.cuda.device_count())),
          flush=True)
    best = per_layer[str(best_L)]
    return {
        "model_id": model_id, "mode": mode,
        "layers_probed": LAYERS_70B, "best_layer": best_L,
        "load_wall_s": t_load,
        "passage_extract_wall_s": t_pass, "query_extract_wall_s": t_q,
        "per_layer": per_layer,
        "acc_top1_raw": best["acc_top1_raw"], "acc_topk_raw": best["acc_topk_raw"],
        "acc_top1_rp": best["acc_top1_rp"], "acc_topk_rp": best["acc_topk_rp"],
        "rank_raw": best["rank_raw"], "rank_rp": best["rank_rp"],
        "hidden_dim": best["hidden_dim"],
    }


def compute_verdict(r_fp16, r_nf4, r_instruct=None) -> Tuple[str, str]:
    """Disambiguate the late-layer crash: was it NF4 quant or architectural?"""
    L74_fp16 = r_fp16["per_layer"]["74"]["acc_topk_rp"]
    L74_nf4 = r_nf4["per_layer"]["74"]["acc_topk_rp"]
    L40_fp16 = r_fp16["per_layer"]["40"]["acc_topk_rp"]
    L40_nf4 = r_nf4["per_layer"]["40"]["acc_topk_rp"]
    fp16_best = r_fp16["acc_topk_rp"]
    nf4_best = r_nf4["acc_topk_rp"]

    instruct_summary = ""
    if r_instruct is not None:
        instruct_best = r_instruct["acc_topk_rp"]
        instruct_summary = f" | Instruct NF4 best={instruct_best:.3f} (vs base NF4 {nf4_best:.3f})"

    summary = (f"L=74 (late): fp16={L74_fp16:.3f} nf4={L74_nf4:.3f} ratio={L74_fp16/max(L74_nf4,1e-9):.2f} | "
               f"L=40 (mid): fp16={L40_fp16:.3f} nf4={L40_nf4:.3f} | "
               f"BEST: fp16={fp16_best:.3f} nf4={nf4_best:.3f}" + instruct_summary)

    if L74_fp16 >= 2.0 * max(L74_nf4, 0.01):
        return ("CLEAR_NF4_EFFECT",
                f"CLEAR_NF4_EFFECT: fp16 late-layer retrieval >= 2x NF4 late-layer. "
                f"NF4 quant noise was the late-layer crash cause; architectural artifact ruled out. "
                f"Cheap-fleet thesis holds for ANY precision. {summary}")
    if L74_fp16 >= 1.5 * max(L74_nf4, 0.01):
        return ("MARGINAL_NF4_EFFECT",
                f"MARGINAL_NF4_EFFECT: fp16 late-layer is 1.5-2x NF4. Partial quant effect; some "
                f"architectural component too. {summary}")
    return ("ARCHITECTURAL_CONFIRMED",
            f"ARCHITECTURAL_CONFIRMED: fp16 late-layer is <= 1.5x NF4 late-layer. Late-layer crash "
            f"is largely architectural (Llama-3.1-70B late layers collapse for retrieval regardless "
            f"of precision). Interesting finding about how 70B compresses information. {summary}")


def main_local_pythia():
    """Run on Pythia-160M with multi-layer probe (PROVES same pipeline as cloud) BEFORE cloud spend."""
    print(f"[config] anchor={ANCHOR_NAME} mode=LOCAL-PYTHIA-SANITY layers={LAYERS_PYTHIA}", flush=True)
    passages, questions, gold_indices = load_squad_v2_dev_shuffled()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    print(f"[load] {PYTHIA} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(PYTHIA)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    model = AutoModelForCausalLM.from_pretrained(PYTHIA, torch_dtype=torch.float32).to(DEVICE)
    print(f"[load] done in {time.time()-t0:.1f}s; tokenizer padding_side={tok.padding_side}", flush=True)
    pas_by_L = extract_lasttoken_hidden_states_multi_layer(model, tok, passages, LAYERS_PYTHIA, batch_size=8)
    q_by_L = extract_lasttoken_hidden_states_multi_layer(model, tok, questions, LAYERS_PYTHIA, batch_size=8)
    best_acck = -1.0
    best_L = None
    print(f"\n[per-layer]", flush=True)
    for L in LAYERS_PYTHIA:
        pas_hs = pas_by_L[L]; q_hs = q_by_L[L]
        hidden_dim = pas_hs.shape[1]
        P = random_projection_matrix(hidden_dim, N_SUBSTRATE, seed=RP_SEED)
        pas_sub = pas_hs @ P; q_sub = q_hs @ P
        acck_raw, sims_raw = top_k_retrieval_acc(q_hs, pas_hs, gold_indices, k=TOP_K)
        acck_rp, sims_rp = top_k_retrieval_acc(q_sub, pas_sub, gold_indices, k=TOP_K)
        rank_raw = gold_rank_stats(sims_raw, gold_indices)
        rank_rp = gold_rank_stats(sims_rp, gold_indices)
        print(f"  L={L}: raw top-5={acck_raw:.3f} med={rank_raw['median_rank']} | RP top-5={acck_rp:.3f} med={rank_rp['median_rank']}", flush=True)
        if acck_rp > best_acck: best_acck = acck_rp; best_L = L
    print(f"\n[PYTHIA-SANITY-VERDICT]", flush=True)
    if best_acck > 0.03:
        print(f"  PASS: best layer {best_L} top-5-RP={best_acck:.3f}. Pipeline functional. Safe to cloud.", flush=True)
    else:
        print(f"  FAIL: max top-5={best_acck:.3f}. Do NOT cloud-dispatch; fix pipeline first.", flush=True)


def main_cloud():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} include_instruct={INCLUDE_INSTRUCT} "
          f"N_passages={N_PASSAGES} N_queries={N_QUERIES} top-k={TOP_K}",
          flush=True)
    hf_token = _load_hf_token()
    passages, questions, gold_indices = load_squad_v2_dev_shuffled()
    out_dir = get_output_dir(ANCHOR_NAME)

    t0 = time.time()

    # ORDER: NF4 baseline first (proves repro of CLOUD-1b 70B NF4 numbers),
    # then fp16 (the disambiguation question), then optional Instruct.
    print("\n=== Llama-3.1-70B NF4 baseline (repro of CLOUD-1b) ===", flush=True)
    r_nf4 = run_70b(LLAMA_70B_BASE, "nf4", passages, questions, gold_indices, hf_token)

    print("\n=== Llama-3.1-70B fp16 (the disambiguation question) ===", flush=True)
    r_fp16 = run_70b(LLAMA_70B_BASE, "fp16", passages, questions, gold_indices, hf_token)

    r_instruct = None
    if INCLUDE_INSTRUCT:
        print("\n=== Llama-3.1-70B-Instruct NF4 (optional add-on) ===", flush=True)
        r_instruct = run_70b(LLAMA_70B_INSTRUCT, "nf4", passages, questions, gold_indices, hf_token)

    elapsed = time.time() - t0
    verdict, vmsg = compute_verdict(r_fp16, r_nf4, r_instruct)
    print(f"\n[VERDICT] {vmsg}", flush=True)
    peak = sum(torch.cuda.max_memory_allocated(i) for i in range(torch.cuda.device_count())) / 1e9
    print(f"[GPU combined peak] {peak:.2f} GB", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict, "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_passages": len(passages), "n_queries": len(questions),
        "top_k": TOP_K, "n_substrate": N_SUBSTRATE,
        "shuffle_seed": SHUFFLE_SEED, "rp_seed": RP_SEED,
        "per_model": {"70B_nf4": r_nf4, "70B_fp16": r_fp16},
        "elapsed_s": elapsed,
        "gpu_peak_gb": peak,
        "summary": vmsg,
        "cloud1b_70B_nf4_reference": {
            "L40_topk_rp": 0.146, "L50_topk_rp": 0.174, "L60_topk_rp": 0.084,
            "L68_topk_rp": 0.064, "L74_topk_rp": 0.054,
        },
    }
    if r_instruct is not None:
        metrics["per_model"]["70B_instruct_nf4"] = r_instruct
    write_metrics(out_dir, metrics, [r_nf4, r_fp16] + ([r_instruct] if r_instruct else []))
    print("[metrics] written", flush=True)


def main():
    if LOCAL_PYTHIA:
        main_local_pythia()
    else:
        main_cloud()


if __name__ == "__main__":
    main()
