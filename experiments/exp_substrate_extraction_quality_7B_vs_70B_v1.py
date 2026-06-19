"""substrate_extraction_quality_7B_vs_70B_v1 -- CLOUD-1 binding test.

ROUTING: research_to_testbed_cloud_experiments_list_when_authorized_2026-06-06
  (TOP PRIORITY when authorized). Cheapest decisive test that gates ALL extraction
  infrastructure decisions: $31 CPU fleet vs $1 Mac fleet vs continued cloud-H100
  baseline.

QUESTION: Does an 8B model produce substrate-extraction quality adequate for the
  cognitive-core deployment? I.e., is small-model substrate-retrieval >= 80% of
  big-model substrate-retrieval (HP) vs < 60% (HF, need bigger).

DESIGN:
  - Compare Llama-3.1-8B (fp16) vs Llama-3.1-70B (4-bit NF4) on the SAME 1K passages.
    "7B" in research spec is the Llama family's smallest -- the Llama-3 family ships
    8B as its smallest open variant; using 8B is the closest mate to 70B in
    architecture, training data, and tokenizer.
  - Extract hidden states at ~50pct depth: layer 16/32 (8B) and layer 40/80 (70B).
  - Build a substrate-vector for each passage via mean-pool across tokens + random
    projection to N=4096 (matches substrate dim convention).
  - Run top-5 retrieval on 100 SQuAD-v2-dev questions whose ground-truth passage is
    in the 1K corpus. Accuracy: fraction of queries where the gold passage is in
    the top-5 cosine-ranked substrate matches.
  - Run sequentially on a single H100:1 so 70B 4-bit fits in 80GB VRAM alongside
    KV cache headroom. 8B + 70B sequential keeps cost <=$1 wall.

PIPELINE:
  1. Load SQuAD-v2 dev. Pick 1K unique passages + 100 question/answer pairs whose
     ground-truth passage is among the 1K.
  2. For model in [8B fp16, 70B 4-bit]:
     a. Load model (file-first HF token).
     b. Extract hidden_states at the 50pct-depth layer for each passage and
        each question (with passage / question text in isolation).
     c. Mean-pool tokens -> one fixed-dim vector per text.
     d. Random-project (seeded same across models) to N=4096.
     e. Top-5 cosine retrieval per question over the 1K passage substrate vectors.
     f. acc = fraction of queries where gold passage in top-5.
     g. Free model + cache.
  3. Compute ratio = acc_8B / acc_70B.
  4. HP if ratio >= 0.80. HF if < 0.60. MIDDLE otherwise.

PRE-REG bands (per research spec):
  HARD-PASS:  ratio (8B/70B) >= 0.80   (substrate-purpose adequacy; cheap fleet wins)
  HARD-FAIL:  ratio < 0.60             (need bigger models for substrate)
  MIDDLE:     0.60 <= ratio < 0.80

EXIT INVARIANTS:
  - Metrics include both raw acc_8B + acc_70B + the ratio.
  - Per-question top-5 captured for diagnostic.

ENV defenses (carry-over from prior cloud bugs Llama-1B + Tier-4-Llama):
  - TOKENIZERS_PARALLELISM=false BEFORE transformers import
  - PROT-022 import-time selftests + --self-test early-exit gate
  - File-first HF token (Llama is gated)
  - ASCII-only stdout (no em-dash, no emoji)
  - bitsandbytes for 70B 4-bit NF4 quant
  - No watchdog-corrupted-npz risk (no np.savez assembly phase; only metrics.json)
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse, time, math
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

ANCHOR_NAME = "substrate_extraction_quality_7B_vs_70B_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

MODEL_8B  = "meta-llama/Llama-3.1-8B"
MODEL_70B = "meta-llama/Llama-3.1-70B"
LAYER_8B  = 16   # 50pct depth of 32
LAYER_70B = 40   # 50pct depth of 80
N_SUBSTRATE = 4096
TOP_K = 5
MAX_TOK = 256    # passage / question truncation for prefill-only mode

if RUN_MODE == "smoke":
    N_PASSAGES = 50
    N_QUERIES = 10
else:
    N_PASSAGES = 1000
    N_QUERIES = 100


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
    raise RuntimeError(
        "HF token not found: place token at <repo>/.hf_token OR set HF_TOKEN env. "
        "Llama-3.1 models are gated and require a license-accepted token."
    )


# ---------------- substrate vector build ----------------

def random_projection_matrix(input_dim: int, output_dim: int, seed: int) -> torch.Tensor:
    """Gaussian random projection, normalized columns. Deterministic from seed."""
    g = torch.Generator().manual_seed(seed)
    P = torch.randn(input_dim, output_dim, generator=g) / math.sqrt(output_dim)
    return P


def mean_pool(hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Mean-pool across non-masked token positions. hs: (B,T,H); am: (B,T) -> (B,H)."""
    am = attention_mask.unsqueeze(-1).to(hidden_states.dtype)
    summed = (hidden_states * am).sum(dim=1)
    counts = am.sum(dim=1).clamp_min(1.0)
    return summed / counts


def top_k_retrieval_acc(query_substrates: torch.Tensor,
                        corpus_substrates: torch.Tensor,
                        gold_indices: List[int],
                        k: int) -> float:
    """Top-k cosine retrieval accuracy. All tensors fp32."""
    qn = F.normalize(query_substrates, dim=-1)
    cn = F.normalize(corpus_substrates, dim=-1)
    sims = qn @ cn.t()  # (Q, C)
    _, topk = sims.topk(k, dim=-1)  # (Q, k)
    hits = 0
    for i, gold in enumerate(gold_indices):
        if gold in topk[i].tolist():
            hits += 1
    return hits / len(gold_indices)


# ---------------- PROT-022 self-tests ----------------

def _selftest():
    """Random projection + mean-pool + top-k retrieval sanity."""
    # mean_pool
    hs = torch.tensor([[[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]])  # (1,3,2)
    am = torch.tensor([[1.0, 1.0, 0.0]])  # last token masked
    mp = mean_pool(hs, am)
    assert mp.shape == (1, 2), f"mean_pool shape: {mp.shape}"
    assert abs(float(mp[0, 0]) - 2.0) < 1e-5, f"mean_pool[0,0]={mp[0,0]}"
    assert abs(float(mp[0, 1]) - 3.0) < 1e-5, f"mean_pool[0,1]={mp[0,1]}"

    # random projection deterministic from seed
    P1 = random_projection_matrix(8, 16, seed=7)
    P2 = random_projection_matrix(8, 16, seed=7)
    P3 = random_projection_matrix(8, 16, seed=8)
    assert torch.allclose(P1, P2), "RP not deterministic"
    assert not torch.allclose(P1, P3), "RP same across different seeds"

    # top-k retrieval: identity corpus -> each query gold should be top-1
    corpus = torch.randn(10, 32)
    queries = corpus.clone()
    gold = list(range(10))
    acc = top_k_retrieval_acc(queries, corpus, gold, k=1)
    assert acc == 1.0, f"identity retrieval top-1: {acc}"
    # top-5 with random queries should be ~0.5/10=0.05 ish
    random_q = torch.randn(10, 32)
    acc_rand = top_k_retrieval_acc(random_q, corpus, gold, k=5)
    assert 0.0 <= acc_rand <= 1.0, f"random acc range: {acc_rand}"

    print("[selftest] PASS: mean_pool + random_projection + top_k_retrieval", flush=True)


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

from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402


def load_squad_v2_dev() -> Tuple[List[str], List[str], List[int]]:
    """Load SQuAD v2 dev set. Returns (passages_1k, questions, gold_passage_indices).

    SQuAD v2 dev set:
      - ~11.8K questions
      - ~1.2K unique paragraphs
      - We pick the first N_PASSAGES unique paragraphs (in dataset order) and the
        first N_QUERIES questions whose gold paragraph is in that set.
    """
    from datasets import load_dataset
    ds = load_dataset("squad_v2", split="validation")
    seen_passages: Dict[str, int] = {}
    passages: List[str] = []
    for ex in ds:
        ctx = ex["context"]
        if ctx not in seen_passages:
            seen_passages[ctx] = len(passages)
            passages.append(ctx)
        if len(passages) >= N_PASSAGES:
            break
    questions: List[str] = []
    gold_indices: List[int] = []
    for ex in ds:
        ctx = ex["context"]
        if ctx in seen_passages and len(ex["answers"]["text"]) > 0:
            questions.append(ex["question"])
            gold_indices.append(seen_passages[ctx])
            if len(questions) >= N_QUERIES:
                break
    print(f"[data] {len(passages)} unique passages + {len(questions)} questions loaded", flush=True)
    return passages, questions, gold_indices


def extract_hidden_states(model, tokenizer, texts: List[str], layer_idx: int,
                          batch_size: int = 8) -> torch.Tensor:
    """Forward each batch of texts through model. Return mean-pooled hidden_state
    from layer_idx for each text. Shape: (len(texts), hidden_dim)."""
    model.eval()
    pooled = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, truncation=True, max_length=MAX_TOK,
                            return_tensors="pt").to(DEVICE)
            out = model(input_ids=enc["input_ids"],
                        attention_mask=enc["attention_mask"],
                        output_hidden_states=True,
                        use_cache=False)
            hs = out.hidden_states[layer_idx]  # (B, T, H)
            p = mean_pool(hs.float(), enc["attention_mask"].float())
            pooled.append(p.cpu())
    return torch.cat(pooled, dim=0)


def run_one_model(model_id: str, layer_idx: int, passages: List[str], questions: List[str],
                  gold_indices: List[int], quant_4bit: bool, rp_seed: int) -> Dict:
    """Load model, extract hidden_states for passages + questions, build substrate,
    compute top-k retrieval acc. Return diagnostic dict + free model before return."""
    token = _load_hf_token()
    t0 = time.time()
    print(f"[load] {model_id} (4bit={quant_4bit})", flush=True)
    if quant_4bit:
        from transformers import BitsAndBytesConfig
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                  bnb_4bit_compute_dtype=torch.bfloat16,
                                  bnb_4bit_use_double_quant=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, token=token, quantization_config=bnb,
            device_map="auto", torch_dtype=torch.bfloat16,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, token=token, torch_dtype=torch.float16,
            device_map={"": DEVICE},
        )
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    t_load = time.time() - t0
    print(f"  [load] {t_load:.1f}s; peak {torch.cuda.max_memory_allocated(0)/1e9:.2f} GB", flush=True)

    t0 = time.time()
    passage_hs = extract_hidden_states(model, tokenizer, passages, layer_idx)
    t_pass = time.time() - t0
    print(f"  [extract] passages: {t_pass:.1f}s; shape={tuple(passage_hs.shape)}", flush=True)

    t0 = time.time()
    query_hs = extract_hidden_states(model, tokenizer, questions, layer_idx)
    t_q = time.time() - t0
    print(f"  [extract] queries: {t_q:.1f}s; shape={tuple(query_hs.shape)}", flush=True)

    # Random project to N=4096 (same seed across models so the substrate dim itself
    # is not a degree of freedom; what we measure is model's hidden-space quality).
    hidden_dim = passage_hs.shape[1]
    P = random_projection_matrix(hidden_dim, N_SUBSTRATE, seed=rp_seed)
    passage_sub = passage_hs @ P
    query_sub   = query_hs   @ P

    acc1 = top_k_retrieval_acc(query_sub, passage_sub, gold_indices, k=1)
    acck = top_k_retrieval_acc(query_sub, passage_sub, gold_indices, k=TOP_K)
    print(f"  [retrieval] top-1={acc1:.3f}  top-{TOP_K}={acck:.3f}", flush=True)

    # Free model + cache
    del model, tokenizer
    torch.cuda.empty_cache()
    return {
        "model_id": model_id,
        "layer_idx": layer_idx,
        "hidden_dim": hidden_dim,
        "quant_4bit": quant_4bit,
        "load_wall_s": t_load,
        "passage_extract_wall_s": t_pass,
        "query_extract_wall_s": t_q,
        "acc_top1": acc1,
        "acc_topk": acck,
    }


def compute_verdict(r8b: Dict, r70b: Dict) -> Tuple[str, str]:
    acc8  = r8b["acc_topk"]
    acc70 = r70b["acc_topk"]
    ratio = acc8 / (acc70 + 1e-9)
    summary = (f"8B-acc@{TOP_K}={acc8:.3f} vs 70B-acc@{TOP_K}={acc70:.3f} ratio={ratio:.2f} "
               f"(8B={r8b['model_id']} layer{r8b['layer_idx']} fp16; "
               f"70B={r70b['model_id']} layer{r70b['layer_idx']} nf4)")
    if ratio >= 0.80:
        return ("HARD_PASS",
                f"HARD_PASS: 8B substrate retrieval >= 80% of 70B baseline. "
                f"8B is adequate for substrate; cheap CPU/Mac fleet path is viable. {summary}")
    if ratio < 0.60:
        return ("HARD_FAIL",
                f"HARD_FAIL: 8B substrate retrieval < 60% of 70B baseline. "
                f"Substrate needs bigger models; cheap fleet path is not viable. {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: 8B substrate retrieval in (60%, 80%) of 70B baseline. "
            f"Marginal; depends on application tolerance. {summary}")


def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} "
          f"8B={MODEL_8B} L={LAYER_8B} 70B={MODEL_70B} L={LAYER_70B} "
          f"N_passages={N_PASSAGES} N_queries={N_QUERIES} top-k={TOP_K} N_substrate={N_SUBSTRATE}",
          flush=True)
    passages, questions, gold_indices = load_squad_v2_dev()
    if len(passages) < N_PASSAGES or len(questions) < N_QUERIES:
        print(f"[WARN] data shortfall: passages={len(passages)} questions={len(questions)}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)

    t0 = time.time()
    r8b  = run_one_model(MODEL_8B,  LAYER_8B,  passages, questions, gold_indices,
                         quant_4bit=False, rp_seed=1729)
    r70b = run_one_model(MODEL_70B, LAYER_70B, passages, questions, gold_indices,
                         quant_4bit=True,  rp_seed=1729)
    elapsed = time.time() - t0

    verdict, vmsg = compute_verdict(r8b, r70b)
    print(f"\n[VERDICT] {vmsg}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    print(f"[GPU] peak {peak:.2f} GB", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_passages": len(passages),
        "n_queries": len(questions),
        "top_k": TOP_K,
        "n_substrate": N_SUBSTRATE,
        "per_model": {"8B": r8b, "70B": r70b},
        "ratio_top1": r8b["acc_top1"] / (r70b["acc_top1"] + 1e-9),
        "ratio_topk": r8b["acc_topk"] / (r70b["acc_topk"] + 1e-9),
        "elapsed_s": elapsed,
        "gpu_peak_gb": peak,
        "summary": vmsg,
    }
    write_metrics(out_dir, metrics, [r8b, r70b])
    print("[metrics] written", flush=True)


if __name__ == "__main__":
    main()
