"""substrate_extraction_quality_1B_8B_70B_v2 -- CLOUD-1b (binding test redo with bug fixes).

ROUTING: research_to_testbed_CLOUD1_kill_CLOUD1b_authorized_2026-06-06 (Research
  green-lit all 5 design fixes after the v1 mean-pool bug was diagnosed via
  Pythia-160M local sanity check; CLOUD-1 v1 sunk \$0.50 producing 0/0 on
  both 8B fp16 and 70B 4-bit, confirming the bug).

DESIGN FIXES vs v1:
  1. LAST-TOKEN POOL for causal LMs (Llama-3.2-1B + Llama-3.1-8B + 70B);
     mean-pool was the v1 bug. Per [[causal-lm-last-token-pool]].
  2. MiniLM-L6-v2 baseline (sentence-transformer; bidirectional; mean-pool is
     correct for it). Should give 60-80% top-5 -- proves task is doable and
     calibrates Llama numbers against a known-good encoder.
  3. Per-query gold-passage RANK diagnostics emitted to metrics
     (median, p25, p75, p95, n_in_top_5, n_in_top_50, n_in_top_100). Tells us
     HOW close to top-5 the gold is when it's not in top-5.
  4. SHUFFLE gold_indices across full 1000 passages (deterministic seed=7).
     v1 had gold_indices concentrated in 41 unique passages from the first 15
     contexts because SQuAD-v2 dev orders questions by passage; shuffling
     spreads gold across the full corpus so retrieval is over 1000 candidates
     not effectively 41.
  5. Llama-3.2-1B as THIRD model -- gives 1B / 8B / 70B size-scaling curve.
     1B is the cheapest LLM rung we already use for substrate work and the
     answer to "is the cheap CPU/Mac fleet viable" depends critically on
     whether 1B's substrate quality is already adequate.

PIPELINE (per model):
  1. Tokenize passages + questions; truncate to MAX_TOK=256.
  2. Causal LMs (Llamas): extract hidden_states[layer_idx] at 50pct depth;
     LAST-TOKEN pool (last non-pad token's hidden state).
  3. MiniLM: use sentence_transformers' .encode() (handles its own pooling).
  4. Random-project to N=4096 (seed=1729; same across models so substrate
     dim doesn't bias the comparison).
  5. Top-5 cosine retrieval; record per-query rank.

PRE-REG BANDS (per Research's CLOUD-1 spec, unchanged):
  HARD-PASS:  8B-top5 / 70B-top5 >= 0.80  (substrate-purpose adequacy; cheap fleet wins)
  HARD-FAIL:  8B-top5 / 70B-top5 < 0.60   (need bigger models)
  MIDDLE:     0.60 <= ratio < 0.80
PLUS new secondary signal (informational; not binding):
  - 1B / 8B ratio -- does small-model substrate quality already match medium?
  - MiniLM upper bound -- does this task have signal at all?
  - per-query rank median -- positional placement of gold in retrieval

INFRA (carries forward from v1):
  - cloud_1_gh200.yaml setup path proven for GH200 + aarch64 + cu124 torch
  - bitsandbytes NF4 4-bit works on GH200 (39.57 GB peak for 70B; fits 96 GB)
  - File-first HF token (Llama gated)
  - ASCII-only stdout (no em-dash, no emoji)
  - PROT-022 import-time selftests + --self-test gate
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

ANCHOR_NAME = "substrate_extraction_quality_1B_8B_70B_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--local-pythia", action="store_true",
                  help="Run only on Pythia-160m locally (Pythia-sanity-check rung)")
_ARGS, _ = _ap.parse_known_args()

LOCAL_PYTHIA = _ARGS.local_pythia

# Models
MINILM    = "sentence-transformers/all-MiniLM-L6-v2"  # bidirectional; mean-pool native
LLAMA_1B  = "meta-llama/Llama-3.2-1B"  # 16 layers
LLAMA_8B  = "meta-llama/Llama-3.1-8B"  # 32 layers
LLAMA_70B = "meta-llama/Llama-3.1-70B"  # 80 layers
PYTHIA    = "EleutherAI/pythia-160m"  # 12 layers (sanity-check only)

# Depth-ratios to probe per Llama (5 layers each; "free" since output_hidden_states
# already returns all layers from one forward pass). Per local Pythia layer sweep
# 2026-06-06, top-5 acc was at the noise floor across mid-to-late layers, so we
# probe 5 depth-ratios and pick the one giving best 70B-acc (apples-to-apples
# for the 8B/70B binding-test ratio).
DEPTH_RATIOS = [0.50, 0.625, 0.75, 0.85, 0.92]


def layers_for_model(n_layers: int):
    """Return list of layer indices at DEPTH_RATIOS, deduped."""
    out = []
    seen = set()
    for r in DEPTH_RATIOS:
        L = round(r * n_layers)
        if L not in seen:
            seen.add(L); out.append(L)
    return out


N_LAYERS_1B = 16
N_LAYERS_8B = 32
N_LAYERS_70B = 80
N_LAYERS_PYTHIA = 12
LAYERS_1B = layers_for_model(N_LAYERS_1B)    # [8, 10, 12, 14, 15]
LAYERS_8B = layers_for_model(N_LAYERS_8B)    # [16, 20, 24, 27, 29]
LAYERS_70B = layers_for_model(N_LAYERS_70B)  # [40, 50, 60, 68, 74]
LAYERS_PYTHIA = layers_for_model(N_LAYERS_PYTHIA)  # [6, 8, 9, 10, 11]

N_SUBSTRATE = 4096
TOP_K = 5
MAX_TOK = 256
SHUFFLE_SEED = 7
RP_SEED = 1729

if RUN_MODE == "smoke":
    N_PASSAGES = 50
    N_QUERIES = 10
else:
    N_PASSAGES = 1000
    N_QUERIES = 500   # raised from 100 to tighten statistical noise (sigma ~10% -> ~4.5%)


def _load_hf_token() -> str:
    """File-first HF token precedence. Raises if missing (Llamas are gated)."""
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    env_tok = os.environ.get("HF_TOKEN", "").strip()
    if env_tok:
        return env_tok
    raise RuntimeError("HF token not found at <repo>/.hf_token or $HF_TOKEN.")


def random_projection_matrix(input_dim: int, output_dim: int, seed: int) -> torch.Tensor:
    g = torch.Generator().manual_seed(seed)
    return torch.randn(input_dim, output_dim, generator=g) / math.sqrt(output_dim)


def mean_pool(hs, am):
    am = am.unsqueeze(-1).to(hs.dtype)
    summed = (hs * am).sum(dim=1)
    counts = am.sum(dim=1).clamp_min(1.0)
    return summed / counts


def last_token_pool(hs, am):
    """Pool the LAST non-pad token's hidden state. hs: (B,T,H); am: (B,T) 1=valid 0=pad."""
    am_int = am.long()
    last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)
    batch_idx = torch.arange(hs.size(0), device=hs.device)
    return hs[batch_idx, last_idx]


def gold_rank_stats(sims, gold_indices) -> Dict:
    """Per-query rank of the gold passage (1 = best, N = worst). Diagnostic."""
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


def top_k_retrieval_acc(query_sub, corpus_sub, gold_indices, k):
    qn = F.normalize(query_sub, dim=-1)
    cn = F.normalize(corpus_sub, dim=-1)
    sims = qn @ cn.t()
    _, topk = sims.topk(k, dim=-1)
    hits = sum(1 for i, g in enumerate(gold_indices) if g in topk[i].tolist())
    return hits / len(gold_indices), sims


# ---------------- PROT-022 self-tests ----------------

def _selftest():
    # mean_pool sanity
    hs = torch.tensor([[[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]])
    am = torch.tensor([[1.0, 1.0, 0.0]])
    mp = mean_pool(hs, am)
    assert abs(float(mp[0, 0]) - 2.0) < 1e-5

    # last_token_pool: last valid token index
    hs2 = torch.tensor([[[1.0], [2.0], [3.0], [4.0]]])  # (1,4,1)
    am2 = torch.tensor([[1, 1, 1, 0]])  # last valid is index 2
    lt = last_token_pool(hs2, am2)
    assert lt.shape == (1, 1) and abs(float(lt[0, 0]) - 3.0) < 1e-5, f"last_token_pool got {lt}"

    # gold_rank_stats
    sims = torch.tensor([[0.1, 0.5, 0.9], [0.9, 0.5, 0.1]])
    gs = gold_rank_stats(sims, [2, 0])
    assert gs["median_rank"] == 1, f"median_rank should be 1 (both gold are best), got {gs}"

    # random projection deterministic
    P1 = random_projection_matrix(8, 16, seed=7)
    P2 = random_projection_matrix(8, 16, seed=7)
    assert torch.allclose(P1, P2)

    # top-k retrieval: identity corpus -> top-1
    corpus = torch.randn(10, 32)
    acc, _ = top_k_retrieval_acc(corpus.clone(), corpus, list(range(10)), k=1)
    assert acc == 1.0

    print("[selftest] PASS: mean_pool + last_token_pool + gold_rank_stats + RP + top_k", flush=True)


_selftest()
if _ARGS.self_test:
    print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
    sys.exit(0)


# ---- heavy path (model load) only below this gate ----
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available; this script is GPU-only.", flush=True)
    sys.exit(1)
DEVICE = torch.device("cuda")
print(f"[GPU] {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)", flush=True)


def load_squad_v2_dev_shuffled() -> Tuple[List[str], List[str], List[int]]:
    """Load SQuAD v2 dev set. Returns (passages_1k, questions, gold_passage_indices).

    SHUFFLE FIX (v2): The 1000 passages list is randomly shuffled (seed=SHUFFLE_SEED)
    after deduplication. Gold passage indices are re-mapped through the shuffle so
    they're spread across the full 0-999 range, not concentrated in 0-40 like v1.
    """
    from datasets import load_dataset
    ds = load_dataset("rajpurkar/squad_v2", split="validation")
    seen_passages_pre = {}  # context -> pre-shuffle index
    passages_pre = []
    for ex in ds:
        ctx = ex["context"]
        if ctx not in seen_passages_pre:
            seen_passages_pre[ctx] = len(passages_pre)
            passages_pre.append(ctx)
        if len(passages_pre) >= N_PASSAGES:
            break

    # Deterministic shuffle of passages
    rng = random.Random(SHUFFLE_SEED)
    pre_to_post = list(range(len(passages_pre)))
    rng.shuffle(pre_to_post)  # pre_to_post[old_idx] = new_idx_after_shuffle? Actually NO.
    # We want: new_passages[i] = passages_pre[some_permutation[i]]
    # Let's do it cleanly:
    permutation = list(range(len(passages_pre)))
    rng.shuffle(permutation)  # permutation[new_idx] = old_idx
    passages_post = [passages_pre[old_idx] for old_idx in permutation]
    # old_to_new[old_idx] = new_idx
    old_to_new = [0] * len(passages_pre)
    for new_idx, old_idx in enumerate(permutation):
        old_to_new[old_idx] = new_idx

    # Build seen_passages_post: context -> post-shuffle index
    seen_passages_post = {ctx: old_to_new[seen_passages_pre[ctx]] for ctx in seen_passages_pre}

    questions = []
    gold_indices = []
    for ex in ds:
        ctx = ex["context"]
        if ctx in seen_passages_post and len(ex["answers"]["text"]) > 0:
            questions.append(ex["question"])
            gold_indices.append(seen_passages_post[ctx])
            if len(questions) >= N_QUERIES:
                break
    print(f"[data] {len(passages_post)} unique passages + {len(questions)} questions; "
          f"gold_indices: {len(set(gold_indices))} unique passages "
          f"min={min(gold_indices)} max={max(gold_indices)} median={int(np.median(gold_indices))}",
          flush=True)
    return passages_post, questions, gold_indices


def run_minilm_baseline(passages, questions, gold_indices) -> Dict:
    """Sentence-transformer MiniLM as upper-bound calibrator (proves task is doable)."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("[WARN] sentence_transformers not installed; skipping MiniLM baseline", flush=True)
        return {"model_id": MINILM, "skipped": True}
    t0 = time.time()
    print(f"[load] {MINILM}", flush=True)
    m = SentenceTransformer(MINILM, device=str(DEVICE))
    t_load = time.time() - t0
    t0 = time.time()
    pas = torch.from_numpy(m.encode(passages, batch_size=64, show_progress_bar=False,
                                     convert_to_numpy=True, normalize_embeddings=False))
    q = torch.from_numpy(m.encode(questions, batch_size=64, show_progress_bar=False,
                                   convert_to_numpy=True, normalize_embeddings=False))
    t_extract = time.time() - t0
    # MiniLM native dim = 384; raw cosine + also RP-to-4096 for fair pipeline compare
    P = random_projection_matrix(pas.shape[1], N_SUBSTRATE, seed=RP_SEED)
    pas_sub = pas @ P
    q_sub = q @ P
    acc1_raw, sims_raw = top_k_retrieval_acc(q, pas, gold_indices, k=1)
    acck_raw, _ = top_k_retrieval_acc(q, pas, gold_indices, k=TOP_K)
    acc1_rp, sims_rp = top_k_retrieval_acc(q_sub, pas_sub, gold_indices, k=1)
    acck_rp, _ = top_k_retrieval_acc(q_sub, pas_sub, gold_indices, k=TOP_K)
    rank_raw = gold_rank_stats(sims_raw, gold_indices)
    rank_rp = gold_rank_stats(sims_rp, gold_indices)
    print(f"  [MiniLM raw] top-1={acc1_raw:.3f} top-5={acck_raw:.3f}", flush=True)
    print(f"  [MiniLM RP]  top-1={acc1_rp:.3f}  top-5={acck_rp:.3f}", flush=True)
    print(f"  [MiniLM rank] {rank_raw}", flush=True)
    del m
    torch.cuda.empty_cache()
    return {
        "model_id": MINILM, "hidden_dim": int(pas.shape[1]),
        "load_wall_s": t_load, "extract_wall_s": t_extract,
        "acc_top1_raw": acc1_raw, "acc_topk_raw": acck_raw,
        "acc_top1_rp": acc1_rp, "acc_topk_rp": acck_rp,
        "rank_raw": rank_raw, "rank_rp": rank_rp,
    }


def extract_lasttoken_hidden_states_multi_layer(model, tokenizer, texts, layer_indices,
                                                  batch_size=8) -> Dict[int, torch.Tensor]:
    """Forward each batch ONCE; pool LAST non-pad token at MULTIPLE layer indices.
    Returns {layer_idx: tensor(N, H)}. Essentially free since hidden_states already
    contains all layers; just pool at multiple positions."""
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


def extract_lasttoken_hidden_states(model, tokenizer, texts, layer_idx, batch_size=8) -> torch.Tensor:
    """Single-layer wrapper for backward compat (Pythia local sanity uses this)."""
    return extract_lasttoken_hidden_states_multi_layer(
        model, tokenizer, texts, [layer_idx], batch_size
    )[layer_idx]


def run_causal_lm(model_id: str, layer_indices, passages, questions, gold_indices,
                   quant_4bit: bool, hf_token: str) -> Dict:
    """Load causal LM, extract LAST-TOKEN hidden_states at MULTIPLE layers in one forward
    pass per batch, build substrate per layer, compute retrieval per layer. Picks best
    layer by top-5-RP and returns per-layer + best-layer metrics."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    print(f"[load] {model_id} (4bit={quant_4bit}) probing layers={layer_indices}", flush=True)
    if quant_4bit:
        from transformers import BitsAndBytesConfig
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                  bnb_4bit_compute_dtype=torch.bfloat16,
                                  bnb_4bit_use_double_quant=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, token=hf_token, quantization_config=bnb,
            device_map="auto", torch_dtype=torch.bfloat16,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, token=hf_token, torch_dtype=torch.float16,
            device_map={"": DEVICE},
        )
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    # CRITICAL: force right-padding. Llama-3.x tokenizers default to LEFT padding
    # (for generation). With left-padding, last_token_pool's `am.sum()-1` indexing
    # would point to a padding position rather than the actual last content token.
    # Force right-padding so am.sum()-1 correctly = (n_valid - 1) = last content token.
    tokenizer.padding_side = "right"
    print(f"  [tokenizer] padding_side forced to 'right' (was: original)", flush=True)
    t_load = time.time() - t0
    print(f"  [load] {t_load:.1f}s; peak {torch.cuda.max_memory_allocated(0)/1e9:.2f} GB", flush=True)

    t0 = time.time()
    pas_by_L = extract_lasttoken_hidden_states_multi_layer(model, tokenizer, passages, layer_indices)
    t_pass = time.time() - t0
    t0 = time.time()
    q_by_L = extract_lasttoken_hidden_states_multi_layer(model, tokenizer, questions, layer_indices)
    t_q = time.time() - t0

    # Per-layer retrieval
    per_layer = {}
    best_L = layer_indices[0]
    best_acck_rp = -1.0
    for L in layer_indices:
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
        per_layer[L] = {
            "layer_idx": L, "hidden_dim": hidden_dim,
            "acc_top1_raw": acc1_raw, "acc_topk_raw": acck_raw,
            "acc_top1_rp": acc1_rp, "acc_topk_rp": acck_rp,
            "rank_raw": rank_raw, "rank_rp": rank_rp,
        }
        print(f"  [L={L}] raw top-5={acck_raw:.3f} med-rank={rank_raw['median_rank']} | "
              f"RP top-5={acck_rp:.3f} med-rank={rank_rp['median_rank']}", flush=True)
        if acck_rp > best_acck_rp:
            best_acck_rp = acck_rp
            best_L = L

    print(f"  [{model_id} BEST] layer={best_L} top-5-RP={per_layer[best_L]['acc_topk_rp']:.3f}", flush=True)
    del model, tokenizer
    torch.cuda.empty_cache()
    best = per_layer[best_L]
    return {
        "model_id": model_id, "quant_4bit": quant_4bit,
        "layers_probed": layer_indices, "best_layer": best_L,
        "load_wall_s": t_load,
        "passage_extract_wall_s": t_pass, "query_extract_wall_s": t_q,
        "per_layer": per_layer,
        # Surface best-layer accuracies + ranks at top level for the verdict
        "acc_top1_raw": best["acc_top1_raw"], "acc_topk_raw": best["acc_topk_raw"],
        "acc_top1_rp": best["acc_top1_rp"], "acc_topk_rp": best["acc_topk_rp"],
        "rank_raw": best["rank_raw"], "rank_rp": best["rank_rp"],
        "hidden_dim": best["hidden_dim"],
    }


def compute_verdict(r1b, r8b, r70b, r_mini) -> Tuple[str, str]:
    """Primary binding test: 8B / 70B ratio. Use RP variant (matches substrate pipeline)."""
    acc_8 = r8b["acc_topk_rp"]
    acc_70 = r70b["acc_topk_rp"]
    acc_1 = r1b["acc_topk_rp"]
    acc_m = r_mini.get("acc_topk_rp", 0.0)
    ratio_8_70 = acc_8 / (acc_70 + 1e-9)
    ratio_1_8 = acc_1 / (acc_8 + 1e-9)
    summary = (f"top5-RP: 1B={acc_1:.3f} 8B={acc_8:.3f} 70B={acc_70:.3f} "
               f"MiniLM={acc_m:.3f} | ratios 8B/70B={ratio_8_70:.2f} 1B/8B={ratio_1_8:.2f}")
    # Task-validity gate: if MiniLM (known-good encoder) gives near-zero, the task or
    # data is broken -- don't declare HP/HF on noise.
    if acc_m < 0.10:
        return ("UNKNOWN",
                f"UNKNOWN: MiniLM baseline ({acc_m:.3f}) is below 10% -- task or data pipeline "
                f"is suspect; cannot interpret Llama ratios. {summary}")
    if acc_70 < 0.05:
        return ("UNKNOWN",
                f"UNKNOWN: 70B raw retrieval ({acc_70:.3f}) is near zero even with last-token pool. "
                f"Substrate quality is uniformly poor across the Llama family. {summary}")
    if ratio_8_70 >= 0.80:
        return ("HARD_PASS",
                f"HARD_PASS: 8B substrate retrieval >= 80% of 70B. Cheap CPU/Mac fleet path "
                f"is viable. {summary}")
    if ratio_8_70 < 0.60:
        return ("HARD_FAIL",
                f"HARD_FAIL: 8B substrate retrieval < 60% of 70B. Substrate needs bigger models; "
                f"cheap fleet path not viable. {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: 8B/70B ratio in (0.60, 0.80). Depends on application tolerance. {summary}")


def main_local_pythia():
    """Local sanity-check rung: run on Pythia-160M with multi-layer probe (matches cloud)."""
    print(f"[config] anchor={ANCHOR_NAME} mode=LOCAL-PYTHIA-SANITY layers={LAYERS_PYTHIA}", flush=True)
    passages, questions, gold_indices = load_squad_v2_dev_shuffled()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    print(f"[load] {PYTHIA} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(PYTHIA)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"  # safety; Pythia defaults to right but force explicit
    model = AutoModelForCausalLM.from_pretrained(PYTHIA, torch_dtype=torch.float32).to(DEVICE)
    print(f"[load] done in {time.time()-t0:.1f}s; tokenizer padding_side={tok.padding_side}", flush=True)
    t0 = time.time()
    pas_by_L = extract_lasttoken_hidden_states_multi_layer(model, tok, passages, LAYERS_PYTHIA)
    print(f"[extract] passages done in {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    q_by_L = extract_lasttoken_hidden_states_multi_layer(model, tok, questions, LAYERS_PYTHIA)
    print(f"[extract] queries done in {time.time()-t0:.1f}s", flush=True)

    best_acck = -1.0
    best_L = None
    print("\n[per-layer]", flush=True)
    print(f"{'L':<4} {'top-1-raw':>10} {'top-5-raw':>10} {'med-rank-raw':>13} "
          f"{'top-5-RP':>10} {'med-rank-RP':>12}", flush=True)
    for L in LAYERS_PYTHIA:
        pas_hs = pas_by_L[L]
        q_hs = q_by_L[L]
        hidden_dim = pas_hs.shape[1]
        P = random_projection_matrix(hidden_dim, N_SUBSTRATE, seed=RP_SEED)
        pas_sub = pas_hs @ P
        q_sub = q_hs @ P
        acc1_raw, sims_raw = top_k_retrieval_acc(q_hs, pas_hs, gold_indices, k=1)
        acck_raw, _ = top_k_retrieval_acc(q_hs, pas_hs, gold_indices, k=TOP_K)
        acck_rp, sims_rp = top_k_retrieval_acc(q_sub, pas_sub, gold_indices, k=TOP_K)
        rank_raw = gold_rank_stats(sims_raw, gold_indices)
        rank_rp = gold_rank_stats(sims_rp, gold_indices)
        print(f"{L:<4d} {acc1_raw:>10.3f} {acck_raw:>10.3f} {rank_raw['median_rank']:>13d} "
              f"{acck_rp:>10.3f} {rank_rp['median_rank']:>12d}", flush=True)
        if acck_rp > best_acck:
            best_acck = acck_rp; best_L = L

    print(f"\n[PYTHIA-SANITY-VERDICT]", flush=True)
    if best_acck > 0.03:
        print(f"  PASS: best layer {best_L} top-5-RP={best_acck:.3f} (>0.03 threshold).", flush=True)
        print(f"  Multi-layer probe pipeline works. Safe to dispatch to cloud.", flush=True)
    else:
        print(f"  FAIL: even with multi-layer probe + shuffled gold, max top-5={best_acck:.3f}.", flush=True)
        print(f"  Do NOT dispatch to cloud; fix pipeline first.", flush=True)


def main_cloud():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} | models=1B/8B/70B/MiniLM | "
          f"N_passages={N_PASSAGES} N_queries={N_QUERIES} top-k={TOP_K} N_substrate={N_SUBSTRATE}",
          flush=True)
    hf_token = _load_hf_token()
    passages, questions, gold_indices = load_squad_v2_dev_shuffled()
    out_dir = get_output_dir(ANCHOR_NAME)

    t0 = time.time()
    print("\n=== MiniLM-L6-v2 baseline ===", flush=True)
    r_mini = run_minilm_baseline(passages, questions, gold_indices)

    print("\n=== Llama-3.2-1B (5-layer probe) ===", flush=True)
    r1b = run_causal_lm(LLAMA_1B, LAYERS_1B, passages, questions, gold_indices,
                         quant_4bit=False, hf_token=hf_token)

    print("\n=== Llama-3.1-8B (5-layer probe) ===", flush=True)
    r8b = run_causal_lm(LLAMA_8B, LAYERS_8B, passages, questions, gold_indices,
                         quant_4bit=False, hf_token=hf_token)

    print("\n=== Llama-3.1-70B (4-bit NF4; 5-layer probe) ===", flush=True)
    r70b = run_causal_lm(LLAMA_70B, LAYERS_70B, passages, questions, gold_indices,
                          quant_4bit=True, hf_token=hf_token)

    elapsed = time.time() - t0
    verdict, vmsg = compute_verdict(r1b, r8b, r70b, r_mini)
    print(f"\n[VERDICT] {vmsg}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    print(f"[GPU] peak {peak:.2f} GB", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict, "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_passages": len(passages), "n_queries": len(questions),
        "top_k": TOP_K, "n_substrate": N_SUBSTRATE,
        "shuffle_seed": SHUFFLE_SEED, "rp_seed": RP_SEED,
        "per_model": {"MiniLM": r_mini, "1B": r1b, "8B": r8b, "70B": r70b},
        "ratio_8B_70B_topk_rp": r8b["acc_topk_rp"] / (r70b["acc_topk_rp"] + 1e-9),
        "ratio_1B_8B_topk_rp": r1b["acc_topk_rp"] / (r8b["acc_topk_rp"] + 1e-9),
        "elapsed_s": elapsed,
        "gpu_peak_gb": peak,
        "summary": vmsg,
    }
    write_metrics(out_dir, metrics, [r_mini, r1b, r8b, r70b])
    print("[metrics] written", flush=True)


def main():
    if LOCAL_PYTHIA:
        main_local_pythia()
    else:
        main_cloud()


if __name__ == "__main__":
    main()
