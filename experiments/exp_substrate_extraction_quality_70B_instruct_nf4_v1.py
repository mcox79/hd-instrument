"""substrate_extraction_quality_70B_instruct_nf4_v1 -- 70B-Instruct follow-up to CELL-1.

ROUTING: research_to_testbed_CLOUD1b_HP_ack_fp16_70B_followup_authorized + brief at
  research_POST_COMPACTION_BRIEF_2026-06-06.md
  (70B-Instruct NF4 follow-up; AUTHORIZED at ~$0.65; standing for Testbed dispatch.)

QUESTION: Does instruction-tuning rescue Llama-3.1-70B's late-layer retrieval crash?
  CELL-1 showed Base 70B (both NF4 and fp16) collapses at L=74 to ~0.056. The
  late-layer specialization for next-token prediction is the leading explanation.
  If Instruct's RLHF/SFT changes that specialization, late-layer retrieval may
  improve. If not, the crash is even more architecturally entrenched.

DESIGN:
  Same pipeline as CELL-1 (last-token pool, 5-layer probe at depth-ratios 0.50/
  0.625/0.75/0.85/0.92, 500 queries, shuffled gold, RP to N=4096, top-5 cosine).
  ONE model: meta-llama/Llama-3.1-70B-Instruct at NF4 4-bit (matches CELL-1
  baseline mode for direct comparison).

INTERPRETATION:
  - If L=74 Instruct top-5-RP >= 2x Base 70B NF4 (0.056 -> 0.112+): instruction-
    tuning meaningfully rescues late-layer retrieval. Surprising finding.
  - If L=74 Instruct top-5-RP <= 1.5x Base NF4: late-layer crash is robust to
    fine-tuning. Architecture-level finding confirmed across base AND instruct.
  - At MID-depth (L=50), compare Instruct vs Base NF4 (0.174) and Base fp16
    (0.244). Quantization-cost-rescue via Instruct features?

PRE-REG bands (informational; not a binding test):
  CLEAR_INSTRUCT_RESCUE:  L=74 Instruct >= 2x Base NF4 (0.112+)
  MARGINAL:               L=74 Instruct in [1.5x, 2x] Base NF4
  ARCHITECTURE_ROBUST:    L=74 Instruct < 1.5x Base NF4 (crash persists)

INFRA defenses (carries forward from CELL-1 proven):
  - TOKENIZERS_PARALLELISM=false BEFORE transformers import
  - PROT-022 import-time self-tests + --self-test gate
  - File-first HF token (Llama gated; Instruct gated separately)
  - ASCII-only stdout (no em-dash, no emoji)
  - tokenizer.padding_side = 'right' forced (Llama defaults to left)
  - last-token pool (causal-LM-correct; NOT mean-pool)
  - Cross-device hidden_states indexing under device_map='auto' (last_idx.to)
  - torch.cuda.reset_peak_memory_stats before model load
  - gc.collect + per-device empty_cache after del model
  - device_map='auto' with adaptive max_memory by per-GPU VRAM probe
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

import argparse, time, math, random, gc
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

ANCHOR_NAME = "substrate_extraction_quality_70B_instruct_nf4_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--local-pythia", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LOCAL_PYTHIA = _ARGS.local_pythia

MODEL_70B_INSTRUCT = "meta-llama/Llama-3.1-70B-Instruct"
PYTHIA = "EleutherAI/pythia-160m"

# Layer indices match CELL-1's 70B probe for direct comparison
LAYERS_70B = [40, 50, 60, 68, 74]
LAYERS_PYTHIA = [6, 8, 9, 10, 11]   # SAME depth ratios as CELL-1

# Hardcoded CELL-1 reference numbers (Base 70B NF4 top-5-RP) for verdict diffing
CELL1_BASE_70B_NF4_TOPK_RP = {
    40: 0.146,
    50: 0.174,
    60: 0.084,
    68: 0.064,
    74: 0.056,
}
CELL1_BASE_70B_FP16_TOPK_RP = {
    40: 0.192,
    50: 0.244,
    60: 0.174,
    68: 0.080,
    74: 0.056,
}

N_SUBSTRATE = 4096
TOP_K = 5
MAX_TOK = 256
SHUFFLE_SEED = 7      # SAME as CELL-1 v1 (deterministic; same passage shuffle)
RP_SEED = 1729

if RUN_MODE == "smoke":
    N_PASSAGES = 50
    N_QUERIES = 10
else:
    N_PASSAGES = 1000
    N_QUERIES = 500    # SAME as CELL-1 for direct comparison


def _load_hf_token() -> str:
    """File-first HF token precedence. Raises if missing (Llama is gated)."""
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
    """Pool the LAST non-pad token. CROSS-DEVICE SAFE."""
    am_int = am.long()
    last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)
    # Under device_map='auto' hs may be on cuda:1 while am is on cuda:0; move indices
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
    """PROT-022 self-tests; mirrors CELL-1."""
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
    """SAME as CELL-1: 1000 unique passages + 500 answerable questions; shuffled."""
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
          f"gold unique={len(set(gold_indices))} min={min(gold_indices)} max={max(gold_indices)} "
          f"median={int(np.median(gold_indices))}",
          flush=True)
    return passages_post, questions, gold_indices


def extract_lasttoken_hidden_states_multi_layer(model, tokenizer, texts, layer_indices, batch_size=2):
    """ONE forward pass per batch; pool LAST non-pad token at MULTIPLE layer indices."""
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


def run_70b_instruct_nf4(passages, questions, gold_indices, hf_token: str) -> Dict:
    """Load Llama-3.1-70B-Instruct at NF4; extract last-token at 5 layers; compute retrieval."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    # CRITICAL: reset peak memory stats before this run (no carryover from any prior model)
    for d in range(torch.cuda.device_count()):
        torch.cuda.reset_peak_memory_stats(d)
    gc.collect()
    torch.cuda.empty_cache()

    t0 = time.time()
    print(f"[load] {MODEL_70B_INSTRUCT} NF4 4-bit; probing layers={LAYERS_70B}", flush=True)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                              bnb_4bit_compute_dtype=torch.bfloat16,
                              bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_70B_INSTRUCT, token=hf_token, quantization_config=bnb,
        device_map="auto", torch_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_70B_INSTRUCT, token=hf_token)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"  # CRITICAL: Llama defaults to left
    t_load = time.time() - t0
    peak = sum(torch.cuda.max_memory_allocated(i) for i in range(torch.cuda.device_count())) / 1e9
    print(f"  [load] {t_load:.1f}s; combined GPU peak {peak:.2f} GB", flush=True)
    print(f"  [tokenizer] padding_side forced to 'right'", flush=True)

    t0 = time.time()
    pas_by_L = extract_lasttoken_hidden_states_multi_layer(model, tokenizer, passages, LAYERS_70B)
    t_pass = time.time() - t0
    t0 = time.time()
    q_by_L = extract_lasttoken_hidden_states_multi_layer(model, tokenizer, questions, LAYERS_70B)
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
        cell1_base_nf4 = CELL1_BASE_70B_NF4_TOPK_RP[L]
        diff_vs_base_nf4 = acck_rp - cell1_base_nf4
        print(f"  [L={L}] raw top-5={acck_raw:.3f} med={rank_raw['median_rank']} | "
              f"RP top-5={acck_rp:.3f} med={rank_rp['median_rank']} | "
              f"vs CELL-1 base NF4 ({cell1_base_nf4:.3f}): diff={diff_vs_base_nf4:+.3f}",
              flush=True)
        if acck_rp > best_acck_rp:
            best_acck_rp = acck_rp; best_L = L

    print(f"  [{MODEL_70B_INSTRUCT} NF4 BEST] layer={best_L} top-5-RP={per_layer[str(best_L)]['acc_topk_rp']:.3f}", flush=True)
    del model, tokenizer
    gc.collect()
    for d in range(torch.cuda.device_count()):
        with torch.cuda.device(d):
            torch.cuda.empty_cache()
    best = per_layer[str(best_L)]
    return {
        "model_id": MODEL_70B_INSTRUCT, "mode": "nf4",
        "layers_probed": LAYERS_70B, "best_layer": best_L,
        "load_wall_s": t_load,
        "passage_extract_wall_s": t_pass, "query_extract_wall_s": t_q,
        "per_layer": per_layer,
        "acc_top1_raw": best["acc_top1_raw"], "acc_topk_raw": best["acc_topk_raw"],
        "acc_top1_rp": best["acc_top1_rp"], "acc_topk_rp": best["acc_topk_rp"],
        "rank_raw": best["rank_raw"], "rank_rp": best["rank_rp"],
        "hidden_dim": best["hidden_dim"],
    }


def compute_verdict(r_instruct: Dict) -> Tuple[str, str]:
    """Does Instruct rescue the late-layer crash that Base 70B (NF4 + fp16) suffered?"""
    L74_instruct = r_instruct["per_layer"]["74"]["acc_topk_rp"]
    L40_instruct = r_instruct["per_layer"]["40"]["acc_topk_rp"]
    L50_instruct = r_instruct["per_layer"]["50"]["acc_topk_rp"]
    best_instruct = r_instruct["acc_topk_rp"]
    best_L = r_instruct["best_layer"]

    L74_base_nf4 = CELL1_BASE_70B_NF4_TOPK_RP[74]
    L74_base_fp16 = CELL1_BASE_70B_FP16_TOPK_RP[74]
    L50_base_nf4 = CELL1_BASE_70B_NF4_TOPK_RP[50]
    L50_base_fp16 = CELL1_BASE_70B_FP16_TOPK_RP[50]
    L74_ratio = L74_instruct / max(L74_base_nf4, 1e-9)

    summary = (f"Instruct L=74={L74_instruct:.3f} vs base NF4 0.056 (ratio={L74_ratio:.2f}); "
               f"Instruct L=50={L50_instruct:.3f} vs base NF4 0.174 / base fp16 0.244; "
               f"BEST: Instruct L={best_L} top-5-RP={best_instruct:.3f}")

    if L74_instruct >= 2.0 * L74_base_nf4:
        return ("CLEAR_INSTRUCT_RESCUE",
                f"CLEAR_INSTRUCT_RESCUE: Llama-3.1-70B-Instruct's late-layer (L=74) retrieval "
                f"is >= 2x Base 70B NF4. Instruction-tuning rescues late-layer semantic "
                f"discriminability. {summary}")
    if L74_instruct >= 1.5 * L74_base_nf4:
        return ("MARGINAL_INSTRUCT_RESCUE",
                f"MARGINAL_INSTRUCT_RESCUE: Instruct L=74 is 1.5-2x Base NF4. Partial rescue; "
                f"late-layer crash is reduced but not eliminated by instruction-tuning. {summary}")
    return ("ARCHITECTURE_ROBUST",
            f"ARCHITECTURE_ROBUST: Instruct L=74 is < 1.5x Base NF4. Late-layer retrieval crash "
            f"persists across base AND instruct variants. The 70B late-layer specialization is "
            f"architecturally robust to fine-tuning. {summary}")


def main_local_pythia():
    """Local sanity-check on Pythia-160M; matches CELL-1 pipeline."""
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
        print(f"  L={L}: raw top-5={acck_raw:.3f} med={rank_raw['median_rank']} | "
              f"RP top-5={acck_rp:.3f} med={rank_rp['median_rank']}", flush=True)
        if acck_rp > best_acck: best_acck = acck_rp; best_L = L
    print(f"\n[PYTHIA-SANITY-VERDICT]", flush=True)
    if best_acck > 0.03:
        print(f"  PASS: best layer {best_L} top-5-RP={best_acck:.3f}. Pipeline functional. Safe to cloud.", flush=True)
    else:
        print(f"  FAIL: max top-5={best_acck:.3f}. Do NOT cloud-dispatch; fix pipeline first.", flush=True)


def main_cloud():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} N_passages={N_PASSAGES} N_queries={N_QUERIES} "
          f"top-k={TOP_K}", flush=True)
    hf_token = _load_hf_token()
    passages, questions, gold_indices = load_squad_v2_dev_shuffled()
    out_dir = get_output_dir(ANCHOR_NAME)

    t0 = time.time()
    print("\n=== Llama-3.1-70B-Instruct NF4 ===", flush=True)
    r_instruct = run_70b_instruct_nf4(passages, questions, gold_indices, hf_token)
    elapsed = time.time() - t0

    verdict, vmsg = compute_verdict(r_instruct)
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
        "per_model": {"70B_instruct_nf4": r_instruct},
        "elapsed_s": elapsed,
        "gpu_peak_gb": peak,
        "summary": vmsg,
        "cell1_base_70B_reference": {
            "nf4": CELL1_BASE_70B_NF4_TOPK_RP,
            "fp16": CELL1_BASE_70B_FP16_TOPK_RP,
        },
    }
    write_metrics(out_dir, metrics, [r_instruct])
    print("[metrics] written", flush=True)


def main():
    if LOCAL_PYTHIA:
        main_local_pythia()
    else:
        main_cloud()


if __name__ == "__main__":
    main()
