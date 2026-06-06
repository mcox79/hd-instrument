"""Q4 LoRA retrieval quality test (CELL-5 follow-up; gates CELL-3 starting point).

ROUTING: research_to_testbed_CELL3_CELL4_LoRA_test_AUTHORIZED_2026-06-07.md (Q4 design).

QUESTION: does the CELL-5-trained LoRA adapter IMPROVE retrieval quality at L=15
on Llama-3.2-1B Base? If yes, CELL-3 should use it as the student starting point.
If no, CELL-3 trains from base.

METHODOLOGY (CELL-1 / CLOUD-1b parity):
  - Load Llama-3.2-1B BASE
  - Tokenizer: padding_side='left' (cycle 142 correction)
  - SQuAD-v2 dev set; 500 queries against 1000 passages (or all that fit)
  - For each passage: extract last-token L=15 hidden state (with and without LoRA)
  - Random projection to N=4096 (SEED=1729)
  - Top-5 cosine retrieval; gold = paired passage id (shuffled SEED=7)
  - Metric: top-5-RP accuracy

PRE-REG (Research Q4):
  HP : top-5-RP with LoRA > 0.30 (>= 6% over CELL-1 base 0.282)
  MID: 0.27-0.30 (preserves baseline)
  HF : < 0.27 (LoRA degrades retrieval)

HARDENING:
  - last-token pool with cross-device safety
  - padding_side='left' (NOTE: differs from CELL-2/CELL-5 right-padding;
    cycle 142 indicates left-padding is correct for retrieval extraction)
  - AutoModel (no LM head) for base
  - PeftModel + merge_and_unload for the LoRA case
  - Identical pipeline (same tokenizer config, max_tok, batching) for both
  - PROT-022 self-test for last-token pool + cosine retrieval
  - ASCII-only output
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse, time, gc
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import torch
import numpy as np

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "q4_lora_retrieval_quality_test_v1"
MODEL_LLAMA_1B = "meta-llama/Llama-3.2-1B"
DEFAULT_ADAPTER = REPO / "data" / "cell5_results" / "lora_adapter_epochs1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--adapter", type=str, default=str(DEFAULT_ADAPTER))
_ap.add_argument("--n-queries", type=int, default=500)
_ap.add_argument("--n-passages", type=int, default=1000)
_ap.add_argument("--max-tok", type=int, default=512)
_ap.add_argument("--batch", type=int, default=4)
_ARGS, _ = _ap.parse_known_args()

LAYER_LLAMA = 15
N_QUERIES = _ARGS.n_queries
N_PASSAGES = _ARGS.n_passages
MAX_TOK = _ARGS.max_tok
BATCH = _ARGS.batch
RP_DIM = 4096
TOPK = 5

SHUFFLE_SEED = 7  # CELL-1 / CLOUD-1b methodology
RP_SEED = 1729

# CELL-1 reference (Llama-3.2-1B BASE at L=15; SQuAD-v2; top-5-RP)
CELL1_LLAMA1B_BASE_L15_TOPK_RP = 0.282

# Verdict thresholds (Research Q4)
HP_THRESHOLD = 0.30
MID_LOW = 0.27


def last_token_pool(hs, am):
    """Cross-device safe last-non-pad-token pool.

    For LEFT-padding (which we use here per cycle 142), the last non-pad token
    is ALWAYS at position seq_len-1 regardless of mask. We still use the
    am-based computation for safety + parity with right-padding scripts.
    """
    am_int = am.long()
    last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)
    # For left-padding the formula above gives the last non-pad position WHEN
    # measured from the start of NON-PAD tokens. We actually want the absolute
    # last non-pad token. With left-padding, non-pads are AT THE END of the
    # sequence: positions [seq_len - sum, seq_len). So the last is at seq_len - 1.
    # For left-padding correctness, use seq_len - 1 (= last index) directly.
    seq_len = am.size(1)
    last_idx = torch.full_like(last_idx, seq_len - 1)
    last_idx = last_idx.to(hs.device)
    batch_idx = torch.arange(hs.size(0), device=hs.device)
    return hs[batch_idx, last_idx]


def top_k_retrieval(query_embs: np.ndarray, passage_embs: np.ndarray,
                     gold_indices: np.ndarray, k: int = TOPK) -> float:
    """Compute top-k cosine similarity retrieval accuracy.

    query_embs: (N_queries, D), passage_embs: (N_passages, D)
    gold_indices: (N_queries,) -- index into passage_embs for each query
    Returns accuracy in [0, 1].
    """
    qn = query_embs / (np.linalg.norm(query_embs, axis=1, keepdims=True) + 1e-8)
    pn = passage_embs / (np.linalg.norm(passage_embs, axis=1, keepdims=True) + 1e-8)
    sims = qn @ pn.T  # (N_queries, N_passages)
    topk_idx = np.argpartition(-sims, k, axis=1)[:, :k]
    hits = sum(1 for i, gi in enumerate(gold_indices) if gi in topk_idx[i])
    return hits / max(len(gold_indices), 1)


def _selftest():
    rng = np.random.default_rng(0)
    # Identity: matching embeddings -> top-1 = 1.0
    embs = rng.standard_normal((50, 32)).astype(np.float32)
    gold = np.arange(50)
    acc = top_k_retrieval(embs, embs, gold, k=1)
    assert abs(acc - 1.0) < 1e-6, f"identity top-1 should be 1.0; got {acc}"

    # Random: top-k for k=5 in pool of 50 ≈ 5/50 = 0.1 (random chance)
    q = rng.standard_normal((100, 32)).astype(np.float32)
    p = rng.standard_normal((50, 32)).astype(np.float32)
    g = rng.integers(0, 50, size=100)
    acc_rand = top_k_retrieval(q, p, g, k=5)
    # Allow generous bounds for finite-sample noise
    assert 0.0 <= acc_rand <= 0.3, f"random top-5 of 50 ~ 0.10; got {acc_rand}"

    hs = torch.tensor([[[1.0], [2.0], [3.0], [4.0]]])
    am = torch.tensor([[0, 0, 1, 1]])  # left-padded: non-pads at positions 2,3
    lt = last_token_pool(hs, am)
    assert abs(float(lt[0, 0]) - 4.0) < 1e-5, f"left-pad last-token should be 4.0; got {lt}"

    print(f"[selftest] PASS: top-k identity=1.0, random=~{acc_rand:.3f}, "
          f"left-pad last-token=4.0", flush=True)


_selftest()
if _ARGS.self_test:
    print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
    sys.exit(0)


if not torch.cuda.is_available():
    print("[FATAL] CUDA not available; this script is GPU-only.", flush=True)
    sys.exit(1)
DEVICE = torch.device("cuda")
print(f"[GPU] {torch.cuda.get_device_name(0)} "
      f"({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)", flush=True)


def _load_hf_token() -> Optional[str]:
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    return os.environ.get("HF_TOKEN", "").strip() or None


def load_squad_v2() -> Tuple[List[str], List[str], np.ndarray]:
    """Load SQuAD-v2 dev set, return (passages, questions, gold_indices)."""
    from datasets import load_dataset
    print(f"[data] loading SQuAD-v2 dev set...", flush=True)
    ds = load_dataset("rajpurkar/squad_v2", split="validation",
                       streaming=False, trust_remote_code=False)
    # Dedupe passages by (title, context)
    by_passage = {}
    for ex in ds:
        key = (ex.get("title", ""), ex.get("context", ""))
        by_passage.setdefault(key, []).append(ex)
    unique_passages = list(by_passage.keys())
    print(f"[data] {len(ds)} total examples; {len(unique_passages)} unique passages", flush=True)

    rng = np.random.default_rng(SHUFFLE_SEED)
    p_indices = rng.permutation(len(unique_passages))[:N_PASSAGES]
    selected_passages = [unique_passages[i] for i in p_indices]
    passage_texts = [p[1] for p in selected_passages]

    # Sample N_QUERIES queries from those passages
    queries = []
    gold_indices = []
    for qi in range(N_QUERIES):
        pi = qi % N_PASSAGES
        ex = by_passage[selected_passages[pi]][0]
        question = ex.get("question", "").strip()
        if not question:
            question = "What is described in this passage?"
        queries.append(question)
        gold_indices.append(pi)
    gold_indices = np.array(gold_indices, dtype=np.int64)
    print(f"[data] selected {N_PASSAGES} passages, {N_QUERIES} queries", flush=True)
    return passage_texts, queries, gold_indices


def load_model(use_lora: bool, hf_token: Optional[str], adapter_path: Optional[str]):
    """Load Llama-3.2-1B BASE (AutoModel; no LM head). Optionally merge LoRA adapter."""
    from transformers import AutoModel, AutoTokenizer
    print(f"[load] {MODEL_LLAMA_1B} use_lora={use_lora}", flush=True)
    t0 = time.time()
    for d in range(torch.cuda.device_count()):
        torch.cuda.reset_peak_memory_stats(d)
    gc.collect()
    torch.cuda.empty_cache()

    load_kwargs = {"torch_dtype": torch.float16, "device_map": {"": DEVICE}}
    if hf_token:
        load_kwargs["token"] = hf_token

    if use_lora:
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        base_cm = AutoModelForCausalLM.from_pretrained(MODEL_LLAMA_1B, **load_kwargs)
        peft_model = PeftModel.from_pretrained(base_cm, adapter_path, is_trainable=False)
        merged = peft_model.merge_and_unload()
        del peft_model, base_cm
        gc.collect()
        torch.cuda.empty_cache()
        # Return the full CausalLM model; extraction will use .model attribute
        # (avoid storing parent ref as child attribute -- causes recursion in train()/eval())
        model = merged
    else:
        model = AutoModel.from_pretrained(MODEL_LLAMA_1B, **load_kwargs)

    tok_kwargs = {"token": hf_token} if hf_token else {}
    tokenizer = AutoTokenizer.from_pretrained(MODEL_LLAMA_1B, **tok_kwargs)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"  # cycle 142 fix
    print(f"  load wall {time.time()-t0:.1f}s; GPU peak {torch.cuda.max_memory_allocated(0)/1e9:.2f} GB", flush=True)
    print(f"  [tokenizer] padding_side forced to 'left'", flush=True)
    return model, tokenizer


def extract_embeddings(model, tokenizer, texts: List[str]) -> np.ndarray:
    """Extract last-token L=15 hidden state for each text; return (N, H_dim) fp32.

    If model is a CausalLM wrapper (post merge_and_unload), use .model attribute
    to skip the LM head and avoid 8 GB logits tensor.
    """
    inner = model.model if (hasattr(model, "model") and hasattr(model, "lm_head")) else model
    inner.eval()
    pooled = []
    with torch.no_grad():
        for i in range(0, len(texts), BATCH):
            batch = texts[i:i + BATCH]
            enc = tokenizer(batch, padding=True, truncation=True, max_length=MAX_TOK,
                             return_tensors="pt").to(DEVICE)
            out = inner(input_ids=enc["input_ids"],
                          attention_mask=enc["attention_mask"],
                          output_hidden_states=True,
                          use_cache=False)
            hs = out.hidden_states[LAYER_LLAMA]
            am = enc["attention_mask"].long()
            p = last_token_pool(hs.float(), am).cpu().numpy()
            pooled.append(p)
            if (i // BATCH) % 50 == 0:
                print(f"    [extract] {i}/{len(texts)} done", flush=True)
    return np.concatenate(pooled, axis=0).astype(np.float32)


def random_projection(X: np.ndarray, target_dim: int, seed: int) -> np.ndarray:
    """JL-style projection to target_dim."""
    rng = np.random.default_rng(seed)
    D = X.shape[1]
    proj = rng.standard_normal((D, target_dim)).astype(np.float32) / np.sqrt(target_dim)
    return X @ proj


def evaluate(model, tokenizer, passages, queries, gold) -> Dict:
    pe = extract_embeddings(model, tokenizer, passages)
    qe = extract_embeddings(model, tokenizer, queries)
    pe_rp = random_projection(pe, RP_DIM, RP_SEED)
    qe_rp = random_projection(qe, RP_DIM, RP_SEED)
    raw = top_k_retrieval(qe, pe, gold, k=TOPK)
    rp = top_k_retrieval(qe_rp, pe_rp, gold, k=TOPK)
    return {"top_5_raw": raw, "top_5_rp": rp, "hidden_dim": int(pe.shape[1])}


def main():
    print(f"[config] anchor={ANCHOR_NAME} adapter={_ARGS.adapter} "
          f"N_passages={N_PASSAGES} N_queries={N_QUERIES} max_tok={MAX_TOK} batch={BATCH}",
          flush=True)
    hf_token = _load_hf_token()
    passages, queries, gold = load_squad_v2()

    t0 = time.time()

    # Phase A: BASE (no LoRA)
    print(f"\n=== Phase A: Llama-3.2-1B BASE (no LoRA) ===", flush=True)
    base_model, tokenizer = load_model(use_lora=False, hf_token=hf_token, adapter_path=None)
    base_metrics = evaluate(base_model, tokenizer, passages, queries, gold)
    print(f"  [BASE] top-5 raw={base_metrics['top_5_raw']:.3f} | top-5 RP={base_metrics['top_5_rp']:.3f}", flush=True)
    del base_model
    gc.collect()
    torch.cuda.empty_cache()

    # Phase B: BASE + LoRA merged
    adapter_path = _ARGS.adapter
    if not Path(adapter_path).exists():
        print(f"[FATAL] adapter not found at {adapter_path}", flush=True)
        sys.exit(1)

    print(f"\n=== Phase B: Llama-3.2-1B BASE + CELL-5 LoRA merged ===", flush=True)
    lora_model, lora_tokenizer = load_model(use_lora=True, hf_token=hf_token, adapter_path=adapter_path)
    lora_metrics = evaluate(lora_model, lora_tokenizer, passages, queries, gold)
    print(f"  [LoRA] top-5 raw={lora_metrics['top_5_raw']:.3f} | top-5 RP={lora_metrics['top_5_rp']:.3f}", flush=True)
    del lora_model
    gc.collect()
    torch.cuda.empty_cache()

    base_rp = base_metrics["top_5_rp"]
    lora_rp = lora_metrics["top_5_rp"]
    delta = lora_rp - base_rp
    rel_delta = delta / max(base_rp, 1e-6)

    # Verdict per Research Q4 (RP-based since CELL-1 baseline is RP)
    if lora_rp > HP_THRESHOLD:
        verdict = "HARD_PASS"
    elif lora_rp >= MID_LOW:
        verdict = "MID"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    summary = (f"{verdict}: LoRA top-5-RP={lora_rp:.3f} vs BASE={base_rp:.3f} "
               f"(delta={delta:+.3f}, rel={rel_delta:+.1%}); "
               f"CELL-1 ref={CELL1_LLAMA1B_BASE_L15_TOPK_RP}; "
               f"HP>{HP_THRESHOLD}, MID [{MID_LOW},{HP_THRESHOLD}], HF<{MID_LOW}")
    print(f"\n[VERDICT] {summary}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": summary,
        "base_top5_rp": base_rp,
        "base_top5_raw": base_metrics["top_5_raw"],
        "lora_top5_rp": lora_rp,
        "lora_top5_raw": lora_metrics["top_5_raw"],
        "delta_rp": delta,
        "rel_delta_rp": rel_delta,
        "cell1_reference": CELL1_LLAMA1B_BASE_L15_TOPK_RP,
        "model_id": MODEL_LLAMA_1B,
        "layer_idx": LAYER_LLAMA,
        "adapter_path": str(adapter_path),
        "n_passages": N_PASSAGES,
        "n_queries": N_QUERIES,
        "max_tok": MAX_TOK,
        "batch": BATCH,
        "hp_threshold": HP_THRESHOLD,
        "mid_low": MID_LOW,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    write_metrics(out_dir, metrics, [metrics])
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    main()
