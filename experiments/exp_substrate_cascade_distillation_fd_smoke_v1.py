"""substrate_cascade_distillation_fd_smoke_v1 -- CELL-5 cascade distillation FD smoke.

ROUTING: research_to_testbed_CELL5_Path_X_Option_4_confirmed_2026-06-06 +
  research_to_testbed_CELL5_rulings_Q5_Q12_Path_A_flagged_user_2026-06-07.

PATH A (user-authorized 2026-06-07): teacher = Llama-3.3-70B-Instruct-Turbo
(70B because 405B serverless was blocked on user's Together account).

PIPELINE (Option 4 SFT-internal-FD):
  1. Load runner-prepared (prompts.jsonl, responses.jsonl) from bundle.
  2. Load off-shelf Llama-3.2-1B (Base). Extract last-token L=15 hidden state
     for each prompt -> H_off (N x H_dim) fp32.
  3. LoRA fine-tune a 1B copy on (prompt -> 405B/70B response) for 1 epoch.
     Response-only loss mask (label_pad=-100 on prompt tokens).
  4. Merge LoRA into base; extract last-token L=15 hidden state for SAME
     prompts -> H_ft (N x H_dim) fp32.
  5. H_baseline_centroid = mean(H_off) over all N prompts.
  6. FD_off = mean(1 - cos_sim(H_off, H_baseline_centroid)).
  7. FD_ft  = mean(1 - cos_sim(H_ft,  H_baseline_centroid)).
  8. Ratio = FD_ft / FD_off.

PRE-REG (Research recalibrated for 70B teacher; Path A bands):
  HP : ratio >= 1.3
  MID: 1.05 <= ratio < 1.3 (auto-escalate to 3 epochs per Q9)
  HF : ratio < 1.05

AUTO-ESCALATION (Research Q9):
  If 1-epoch verdict in {MID, HF}, automatically re-fine-tune with epochs=3 and
  re-run extraction + FD computation. Final verdict = better of (1-epoch, 3-epoch).
  Marginal cost ~$3.

HARDENING (28 risks from audit; all defenses inline):
  Phase 2 defenses:
  - r=16, alpha=32, lr=2e-4 (Research Q7 locked)
  - response-only label mask via custom DataCollator (Research Q8)
  - merge_and_unload before H_ft extraction
  - identical MAX_TOK + tokenizer config for H_off and H_ft
  - tokenizer.padding_side='right' forced
  - last_token_pool with cross-device safety (last_idx.to(hs.device))
  - AutoModel (no LM head -- saves 6GB OOM avoidance)
  - dict-keyed join (prompt_id -> response_id)
  - cos_dist = 1 - cos_sim (Research Q10)
  - fp32 cast before FD computation
  - epsilon check: assert FD_off > 0.001
  - NaN guard during training (early abort)
  - LoRA adapter saved to data/ alongside metrics
  - PROT-022 self-test for FD formula (deterministic)

EXIT:
  COMPLETE: clean ratio reported; verdict HP/MID/HF; auto-escalated if needed
  FAILED:   any infra fault or NaN
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse, time, math, gc, json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

ANCHOR_NAME = "substrate_cascade_distillation_fd_smoke_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--data-dir", type=str, default=str(REPO / "data" / "cell5_teacher"),
                  help="Directory with prompts.jsonl + responses.jsonl (runner-prepared)")
_ap.add_argument("--epochs", type=int, default=1,
                  help="LoRA epochs (Research Q7: default 1; auto-escalates to 3 on MID/HF)")
_ap.add_argument("--no-escalate", action="store_true",
                  help="Disable auto-escalation to 3-epoch follow-up (Research Q9)")
_ap.add_argument("--batch-extract", type=int, default=None,
                  help="Override BATCH_EXTRACT (defaults: 16 for H100; pass 4 for 4060 Ti 8GB)")
_ap.add_argument("--max-tok", type=int, default=None,
                  help="Override MAX_TOK (default 1024 for H100; 512 for low-VRAM)")
_ap.add_argument("--batch-train", type=int, default=None,
                  help="Override BATCH_TRAIN (default 4 for H100; pass 1 for 4060 Ti)")
_ARGS, _ = _ap.parse_known_args()

MODEL_LLAMA_1B = "meta-llama/Llama-3.2-1B"
LAYER_LLAMA = 15

# Locked specs from Research (Q5-Q12)
_DEFAULT_MAX_TOK = 1024
_DEFAULT_BATCH_EXTRACT = 16
MAX_TOK = _ARGS.max_tok if _ARGS.max_tok is not None else _DEFAULT_MAX_TOK
EXTRACT_MAX_TOK = MAX_TOK
PROMPT_TOK_CAP = MAX_TOK * 3 // 8   # 384 if MAX_TOK=1024; scales down for smaller
BATCH_EXTRACT = _ARGS.batch_extract if _ARGS.batch_extract is not None else _DEFAULT_BATCH_EXTRACT
BATCH_TRAIN = _ARGS.batch_train if _ARGS.batch_train is not None else 4
GRAD_ACCUM_STEPS = 4      # effective batch 16 for training
SEED = 1729               # determinism for LoRA init + training shuffle
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LEARNING_RATE = 2e-4
WEIGHT_DECAY = 0.0
WARMUP_STEPS = 50
LOG_EVERY = 50

# Verdict bands (Research-recalibrated Path A 70B teacher)
HP_THRESHOLD = 1.30
MID_LOW = 1.05
EPS = 1e-6


def _load_hf_token() -> Optional[str]:
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    return os.environ.get("HF_TOKEN", "").strip() or None


def last_token_pool(hs, am):
    """Cross-device safe last-non-pad-token pool."""
    am_int = am.long()
    last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)
    last_idx = last_idx.to(hs.device)
    batch_idx = torch.arange(hs.size(0), device=hs.device)
    return hs[batch_idx, last_idx]


def compute_fd_ratio(H_off: np.ndarray, H_ft: np.ndarray) -> Tuple[float, float, float]:
    """Per Research Q10: FD = 1 - cos_sim(H, centroid). All fp32.

    Returns (fd_off, fd_ft, ratio = fd_ft / fd_off).
    """
    H_off = H_off.astype(np.float32)
    H_ft = H_ft.astype(np.float32)
    centroid = H_off.mean(axis=0)  # (H_dim,)

    def cos_dist_to_centroid(M, c):
        # avoid division by zero with eps
        c_norm = np.linalg.norm(c) + EPS
        m_norm = np.linalg.norm(M, axis=1) + EPS
        sims = (M @ c) / (m_norm * c_norm)
        return 1.0 - sims  # (N,)

    fd_off = float(cos_dist_to_centroid(H_off, centroid).mean())
    fd_ft = float(cos_dist_to_centroid(H_ft, centroid).mean())
    ratio = fd_ft / max(fd_off, EPS)
    return fd_off, fd_ft, ratio


def _selftest():
    """PROT-022: deterministic FD-formula sanity.

    Tests (cosine distance is scale-invariant, so we use sign flip for a
    deterministic "further" case):
      (a) identity: H_ft = H_off -> ratio = 1.0
      (b) scale: H_ft = 2*H_off -> ratio = 1.0 (cosine scale-invariant)
      (c) sign flip: H_ft = -H_off -> ratio > 1.0 (opposite direction from centroid)
    """
    rng = np.random.default_rng(0)
    H_off = rng.standard_normal((100, 16)).astype(np.float32)

    # (a) identity
    fd_off, fd_ft, ratio = compute_fd_ratio(H_off, H_off)
    assert abs(ratio - 1.0) < 1e-4, f"(a) identity -> ratio=1 expected; got {ratio}"

    # (b) scale invariance
    _, _, ratio_scaled = compute_fd_ratio(H_off, 2.0 * H_off)
    assert abs(ratio_scaled - 1.0) < 1e-4, f"(b) scale-invariant -> ratio=1 expected; got {ratio_scaled}"

    # (c) sign flip
    _, _, ratio_flipped = compute_fd_ratio(H_off, -H_off)
    assert ratio_flipped > 1.0, f"(c) sign-flip -> ratio>1 expected; got {ratio_flipped}"

    # last_token_pool check
    hs = torch.tensor([[[1.0], [2.0], [3.0], [4.0]]])
    am = torch.tensor([[1, 1, 1, 0]])
    lt = last_token_pool(hs, am)
    assert lt.shape == (1, 1) and abs(float(lt[0, 0]) - 3.0) < 1e-5

    print(f"[selftest] PASS: FD identity=1, scale-invariant=1, sign-flip={ratio_flipped:.3f}>1, "
          f"last_token_pool", flush=True)


_selftest()
if _ARGS.self_test:
    print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
    sys.exit(0)

# Determinism for LoRA init + training shuffle + numpy operations
torch.manual_seed(SEED)
np.random.seed(SEED)


if not torch.cuda.is_available():
    print("[FATAL] CUDA not available; this script is GPU-only.", flush=True)
    sys.exit(1)
DEVICE = torch.device("cuda")
print(f"[GPU] {torch.cuda.get_device_name(0)} "
      f"({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)", flush=True)


def load_prompts_and_responses(data_dir: Path) -> List[Dict]:
    """Load + join prompts.jsonl and responses.jsonl by ID (dict-keyed; no list-order assumption)."""
    prompts_path = data_dir / "prompts.jsonl"
    responses_path = data_dir / "responses.jsonl"
    if not prompts_path.exists():
        raise RuntimeError(f"Missing {prompts_path}")
    if not responses_path.exists():
        raise RuntimeError(f"Missing {responses_path}")

    prompts_by_id = {}
    with open(prompts_path, "r", encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            prompts_by_id[str(p["id"])] = p

    responses_by_id = {}
    n_refusals = 0
    n_errors = 0
    with open(responses_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            pid = str(r["id"])
            if "error" in r:
                n_errors += 1
                continue
            if not r.get("response", "").strip():
                n_errors += 1
                continue
            if r.get("is_refusal"):
                n_refusals += 1
                # still include refusals; they are legitimate teacher outputs
            responses_by_id[pid] = r

    # Join + retain only IDs with BOTH prompt and response
    joined = []
    for pid in sorted(prompts_by_id.keys(), key=lambda s: int(s) if s.isdigit() else 0):
        if pid in responses_by_id:
            p = prompts_by_id[pid]
            r = responses_by_id[pid]
            joined.append({
                "id": pid,
                "instruction": p.get("instruction", ""),
                "context": p.get("context", ""),
                "category": p.get("category", ""),
                "response": r["response"],
                "is_refusal": r.get("is_refusal", False),
            })
    print(f"[data] joined: {len(joined)}/{len(prompts_by_id)} prompts have responses "
          f"(errors_or_empty={n_errors}, refusals={n_refusals})", flush=True)
    if len(joined) < 100:
        raise RuntimeError(f"Too few joined examples ({len(joined)}); aborting")
    return joined


def render_prompt(ex: Dict, tokenizer=None) -> str:
    """Render prompt; if tokenizer provided, truncate Context to fit PROMPT_TOK_CAP.

    Without this, a long-context Dolly example (e.g. summarization of a 2000-word
    article) eats the entire MAX_TOK budget and leaves no room for the response
    tokens in training, breaking the response-only label mask.
    """
    instruction = ex["instruction"].strip()
    context = ex.get("context", "").strip()
    if context and tokenizer is not None:
        # Tokenize prompt without context to see how many tokens it occupies
        no_ctx = f"Instruction: {instruction}\n\nResponse: "
        no_ctx_tokens = tokenizer(no_ctx, add_special_tokens=True)["input_ids"]
        # Leave room for "Context: " prefix + newlines + the rest
        ctx_budget = max(0, PROMPT_TOK_CAP - len(no_ctx_tokens) - 16)
        if ctx_budget > 0:
            ctx_tokens = tokenizer(context, add_special_tokens=False,
                                    truncation=True, max_length=ctx_budget)["input_ids"]
            context = tokenizer.decode(ctx_tokens, skip_special_tokens=True)
        else:
            context = ""
    if context:
        return f"Context: {context}\n\nInstruction: {instruction}\n\nResponse: "
    return f"Instruction: {instruction}\n\nResponse: "


def load_base_model_and_tokenizer(model_id: str, hf_token: Optional[str], use_lm_head: bool):
    """Load model. use_lm_head=True for training (needs LM head); False for extraction (AutoModel)."""
    from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
    cls = AutoModelForCausalLM if use_lm_head else AutoModel
    kwargs = {"torch_dtype": torch.float16, "device_map": {"": DEVICE}}
    if hf_token is not None:
        kwargs["token"] = hf_token
    print(f"[load] {model_id} ({'with' if use_lm_head else 'without'} LM head)", flush=True)
    t0 = time.time()
    model = cls.from_pretrained(model_id, **kwargs)
    tok_kwargs = {"token": hf_token} if hf_token else {}
    tokenizer = AutoTokenizer.from_pretrained(model_id, **tok_kwargs)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print(f"  load wall {time.time()-t0:.1f}s; peak {torch.cuda.max_memory_allocated(0)/1e9:.2f} GB", flush=True)
    return model, tokenizer


def extract_hidden_states(model, tokenizer, examples: List[Dict], layer: int,
                           batch_size: int = BATCH_EXTRACT) -> np.ndarray:
    """For each example: tokenize prompt_only, forward, last-token pool at layer.

    Returns (N, H_dim) fp32 numpy array.
    """
    model.eval()
    pooled = []
    with torch.no_grad():
        for i in range(0, len(examples), batch_size):
            batch = examples[i:i + batch_size]
            prompts = [render_prompt(b, tokenizer=tokenizer) for b in batch]
            enc = tokenizer(prompts, padding=True, truncation=True, max_length=EXTRACT_MAX_TOK,
                             return_tensors="pt").to(DEVICE)
            out = model(input_ids=enc["input_ids"],
                          attention_mask=enc["attention_mask"],
                          output_hidden_states=True,
                          use_cache=False)
            hs = out.hidden_states[layer]
            am = enc["attention_mask"].long()
            p = last_token_pool(hs.float(), am).cpu().numpy()
            pooled.append(p)
            if (i // batch_size) % 20 == 0:
                print(f"    [extract] {i}/{len(examples)} done", flush=True)
    return np.concatenate(pooled, axis=0).astype(np.float32)


class CausalSFTDataset(torch.utils.data.Dataset):
    """Response-only label-masked SFT dataset.

    Each example: render prompt (no response trailer), then concatenate response.
    Labels = -100 for prompt tokens; actual token IDs for response tokens.
    """

    def __init__(self, examples: List[Dict], tokenizer, max_tok: int):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_tok = max_tok

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        prompt = render_prompt(ex, tokenizer=self.tokenizer)
        response = ex["response"]
        # Tokenize prompt and response separately to know the boundary
        prompt_ids = self.tokenizer(prompt, add_special_tokens=True, truncation=True,
                                      max_length=self.max_tok)["input_ids"]
        response_ids = self.tokenizer(response, add_special_tokens=False, truncation=True,
                                        max_length=self.max_tok - len(prompt_ids))["input_ids"]
        # Add EOS at end of response
        if self.tokenizer.eos_token_id is not None and (not response_ids or response_ids[-1] != self.tokenizer.eos_token_id):
            response_ids = response_ids + [self.tokenizer.eos_token_id]
        input_ids = prompt_ids + response_ids
        labels = [-100] * len(prompt_ids) + response_ids
        # Truncate if over max_tok (defensive; shouldn't happen)
        input_ids = input_ids[:self.max_tok]
        labels = labels[:self.max_tok]
        attention_mask = [1] * len(input_ids)
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


class SFTCollator:
    """Right-pad collator (must be picklable for DataLoader num_workers>0; lambdas don't pickle)."""

    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def __call__(self, batch):
        max_len = max(len(b["input_ids"]) for b in batch)
        input_ids = []
        attention_mask = []
        labels = []
        for b in batch:
            n_pad = max_len - len(b["input_ids"])
            input_ids.append(b["input_ids"] + [self.pad_token_id] * n_pad)
            attention_mask.append(b["attention_mask"] + [0] * n_pad)
            labels.append(b["labels"] + [-100] * n_pad)
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
        }


def sft_collate(batch, pad_token_id: int):
    """Backwards-compatible wrapper around SFTCollator; not used by DataLoader."""
    return SFTCollator(pad_token_id)(batch)


def lora_finetune(model_id: str, hf_token: Optional[str], examples: List[Dict],
                   tokenizer, epochs: int, out_dir: Path) -> Path:
    """LoRA fine-tune; save adapter; return path to adapter dir."""
    from transformers import AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model, TaskType

    # Reset memory
    for d in range(torch.cuda.device_count()):
        torch.cuda.reset_peak_memory_stats(d)
    gc.collect()
    torch.cuda.empty_cache()

    print(f"[lora] loading model for training", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.bfloat16, device_map={"": DEVICE},
        token=hf_token,
    )
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()

    lora_cfg = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(model, lora_cfg)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"[lora] trainable params={trainable:,} / total={total:,} ({100*trainable/total:.2f}%)",
          flush=True)

    dataset = CausalSFTDataset(examples, tokenizer, max_tok=MAX_TOK)
    # Use class-based collator (picklable; required for num_workers > 0 on Windows + Linux)
    collator = SFTCollator(tokenizer.pad_token_id)
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=BATCH_TRAIN, shuffle=True,
        collate_fn=collator,
        num_workers=2, pin_memory=True,
    )

    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()),
                                    lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    n_steps = epochs * (len(loader) // GRAD_ACCUM_STEPS)
    print(f"[lora] epochs={epochs}, steps_per_epoch={len(loader)//GRAD_ACCUM_STEPS}, "
          f"total_steps={n_steps}", flush=True)

    model.train()
    step = 0
    losses = []
    nan_aborted = False
    for epoch in range(epochs):
        epoch_t0 = time.time()
        for bi, batch in enumerate(loader):
            batch = {k: v.to(DEVICE, non_blocking=True) for k, v in batch.items()}
            out = model(**batch)
            loss = out.loss / GRAD_ACCUM_STEPS
            if not torch.isfinite(loss):
                print(f"[lora] FATAL: non-finite loss at epoch={epoch} batch={bi}; aborting",
                      flush=True)
                nan_aborted = True
                break
            loss.backward()
            if (bi + 1) % GRAD_ACCUM_STEPS == 0:
                optimizer.step()
                optimizer.zero_grad()
                step += 1
                losses.append(float(loss.item() * GRAD_ACCUM_STEPS))
                if step % LOG_EVERY == 0 or step == 1:
                    recent = sum(losses[-LOG_EVERY:]) / max(len(losses[-LOG_EVERY:]), 1)
                    print(f"  [lora step {step}/{n_steps}] loss={recent:.4f}", flush=True)
        if nan_aborted:
            break
        print(f"  [lora epoch {epoch+1}/{epochs}] wall={time.time()-epoch_t0:.1f}s; "
              f"avg_loss={sum(losses)/max(len(losses),1):.4f}", flush=True)

    if nan_aborted:
        raise RuntimeError("LoRA training aborted on non-finite loss")

    adapter_dir = out_dir / f"lora_adapter_epochs{epochs}"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(adapter_dir)
    print(f"[lora] saved adapter to {adapter_dir}", flush=True)

    # Merge adapter into base for inference + free memory
    merged = model.merge_and_unload()
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return adapter_dir, merged


def run_extraction_with_model(model, tokenizer, examples: List[Dict]) -> np.ndarray:
    """Extract via the base transformer (skip LM head; avoid logits OOM).

    For a CausalLM model (post merge_and_unload), model() WITH output_hidden_states=True
    also computes the full vocab logits tensor: batch x seq x vocab_size.
    For Llama-3.2 vocab=128256, batch=16, seq=1024, fp16 -> 4.2 GB unnecessarily.
    Solution: access model.model (the inner LlamaModel) which returns BaseModelOutput.

    For a model that is ALREADY an AutoModel (LlamaModel), use it directly.
    """
    if hasattr(model, "model") and hasattr(model, "lm_head"):
        # CausalLM wrapper -> use inner transformer
        inner = model.model
    else:
        inner = model
    return extract_hidden_states(inner, tokenizer, examples, LAYER_LLAMA, batch_size=BATCH_EXTRACT)


def classify_verdict(ratio: float) -> str:
    if ratio >= HP_THRESHOLD:
        return "HARD_PASS"
    if ratio >= MID_LOW:
        return "MID"
    return "HARD_FAIL"


def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} model={MODEL_LLAMA_1B} layer={LAYER_LLAMA}",
          flush=True)
    hf_token = _load_hf_token()
    data_dir = Path(_ARGS.data_dir)
    print(f"[config] data_dir={data_dir}", flush=True)

    examples = load_prompts_and_responses(data_dir)
    print(f"[config] N joined examples = {len(examples)}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    t_global_start = time.time()

    # ----- Step 1: extract H_off -----
    print(f"\n=== STEP 1: extract H_off (off-shelf 1B at L={LAYER_LLAMA}) ===", flush=True)
    base_model, tokenizer = load_base_model_and_tokenizer(MODEL_LLAMA_1B, hf_token, use_lm_head=False)
    H_off = run_extraction_with_model(base_model, tokenizer, examples)
    print(f"[H_off] shape={H_off.shape} dtype={H_off.dtype}", flush=True)
    np.save(out_dir / "H_off.npy", H_off)
    del base_model
    gc.collect()
    torch.cuda.empty_cache()

    # ----- Step 2 + 3: LoRA fine-tune + extract H_ft (epochs from CLI) -----
    epochs = _ARGS.epochs
    print(f"\n=== STEP 2: LoRA fine-tune (epochs={epochs}) ===", flush=True)
    adapter_dir, merged_model = lora_finetune(
        MODEL_LLAMA_1B, hf_token, examples, tokenizer, epochs=epochs, out_dir=out_dir
    )

    print(f"\n=== STEP 3: extract H_ft (fine-tuned 1B; LoRA merged) ===", flush=True)
    H_ft = run_extraction_with_model(merged_model, tokenizer, examples)
    print(f"[H_ft] shape={H_ft.shape} dtype={H_ft.dtype}", flush=True)
    np.save(out_dir / f"H_ft_epochs{epochs}.npy", H_ft)
    del merged_model
    gc.collect()
    torch.cuda.empty_cache()

    # ----- Step 4: FD computation -----
    print(f"\n=== STEP 4: FD ratio ===", flush=True)
    fd_off, fd_ft, ratio = compute_fd_ratio(H_off, H_ft)
    assert fd_off > 0.001, f"FD_off too small ({fd_off}); cannot compute meaningful ratio"
    verdict_1 = classify_verdict(ratio)
    elapsed_1 = time.time() - t_global_start

    print(f"\n[1-EPOCH RESULT]", flush=True)
    print(f"  FD_off = {fd_off:.6f}", flush=True)
    print(f"  FD_ft  = {fd_ft:.6f}  (epochs={epochs})", flush=True)
    print(f"  ratio  = {ratio:.4f}", flush=True)
    print(f"  verdict (Path A bands HP>={HP_THRESHOLD}, MID [{MID_LOW},{HP_THRESHOLD}), HF<{MID_LOW}): "
          f"{verdict_1}", flush=True)

    results_log = [{
        "epochs": epochs,
        "fd_off": fd_off,
        "fd_ft": fd_ft,
        "ratio": ratio,
        "verdict": verdict_1,
        "wall_s": elapsed_1,
    }]

    # ----- Auto-escalation per Research Q9 -----
    final_verdict = verdict_1
    final_ratio = ratio
    if verdict_1 in ("MID", "HARD_FAIL") and not _ARGS.no_escalate and epochs == 1:
        print(f"\n=== AUTO-ESCALATION: re-running with 3 epochs (Q9) ===", flush=True)
        # Reload base + tokenizer (cleaner than holding refs)
        adapter_dir3, merged_model3 = lora_finetune(
            MODEL_LLAMA_1B, hf_token, examples, tokenizer, epochs=3, out_dir=out_dir
        )
        H_ft3 = run_extraction_with_model(merged_model3, tokenizer, examples)
        np.save(out_dir / "H_ft_epochs3.npy", H_ft3)
        fd_off3, fd_ft3, ratio3 = compute_fd_ratio(H_off, H_ft3)
        verdict_3 = classify_verdict(ratio3)
        elapsed_3 = time.time() - t_global_start
        print(f"\n[3-EPOCH RESULT]", flush=True)
        print(f"  FD_off = {fd_off3:.6f}", flush=True)
        print(f"  FD_ft  = {fd_ft3:.6f}  (epochs=3)", flush=True)
        print(f"  ratio  = {ratio3:.4f}  verdict: {verdict_3}", flush=True)
        results_log.append({
            "epochs": 3, "fd_off": fd_off3, "fd_ft": fd_ft3,
            "ratio": ratio3, "verdict": verdict_3, "wall_s": elapsed_3,
        })
        # Take the better of the two (higher ratio = stronger signal)
        if ratio3 > final_ratio:
            final_ratio = ratio3
            final_verdict = verdict_3
        del merged_model3
        gc.collect()
        torch.cuda.empty_cache()

    elapsed_total = time.time() - t_global_start
    result_summaries = [
        "%s@e%d=%.3f" % (r["verdict"], r["epochs"], r["ratio"]) for r in results_log
    ]
    summary = (f"{final_verdict}: ratio={final_ratio:.4f} (HP>={HP_THRESHOLD}); "
               f"results: {result_summaries}")
    print(f"\n[VERDICT] {summary}", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": final_verdict,
        "verdict_msg": summary,
        "ratio_final": final_ratio,
        "results_per_epoch": results_log,
        "model_id": MODEL_LLAMA_1B,
        "layer_idx": LAYER_LLAMA,
        "teacher_path": "A_70B_Turbo",
        "lora_config": {
            "r": LORA_R, "alpha": LORA_ALPHA, "dropout": LORA_DROPOUT,
            "lr": LEARNING_RATE, "weight_decay": WEIGHT_DECAY,
        },
        "n_examples": len(examples),
        "max_tok": MAX_TOK,
        "hp_threshold": HP_THRESHOLD,
        "mid_low": MID_LOW,
        "auto_escalated": len(results_log) > 1,
        "elapsed_s": elapsed_total,
        "gpu_peak_gb": float(torch.cuda.max_memory_allocated(0) / 1e9),
        "summary": summary,
    }
    write_metrics(out_dir, metrics, results_log)
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    main()
