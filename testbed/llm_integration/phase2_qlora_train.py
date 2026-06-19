"""PP-8 Week 2 Phase 2: QLoRA fine-tune (Q-Former bridge + readout + LoRA on Phi-3).

Per parent handoff sec "Phase 2: QLoRA fine-tune smoke":
  - Apply QLoRA on toy dataset (5K-10K paired examples)
  - Validate bridge converges (loss decreases monotonically; no NaN/Inf;
    checkpoint saves cleanly)
  - First 100-500 steps + validation eval at end
  - Acceptance: loss decreases >=30% over first 200 steps;
    validation eval >random retrieval quality;
    no NaN/Inf crashes; total session cost <= $100

Architecture (trainable params):
  - LoRA adapters on Phi-3 attention layers (q_proj, k_proj, v_proj, o_proj
    at r=16; ~5-10M params)
  - QueryReadoutHead (14.69M; fp32; full)
  - QFormerBridge (62.97M; fp32; full)
Frozen:
  - Phi-3-mini-3.8B 4-bit NF4 base
  - Substrate codebook + relation graph

Training forward pass (substrate BYPASSED for differentiability):
  query_text -> tokenize -> Phi-3 prefill (LoRA active) -> last hidden
    -> readout (soft tanh; trainable) -> bridge (cross-attn; trainable)
    -> 8 prefix tokens -> Phi-3 + prefix (LoRA active) -> logits at first
    output position -> CE vs target_token_id

Validation forward pass (substrate IN THE LOOP):
  ... -> readout -> SIGN -> Path D depth=5 -> codeword (from codebook)
    -> bridge -> 8 prefix tokens -> Phi-3 + prefix -> argmax token
    -> compare to target_token_id; report top-1 accuracy.

Run (REMOTE GPU; CPU mock-train possible for tiny smoke):
  python -m testbed.llm_integration.phase2_qlora_train \
    --dataset-dir data/testbed_pp8_week2/dataset_v1 \
    --max-steps 200 --batch-size 4 --lr 1e-4 \
    --eval-every-k 50 --checkpoint-every-k 100 \
    --out-dir data/testbed_pp8_week2/train_v1 \
    --device cuda
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from torch import nn

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402
from testbed.llm_integration.qformer_bridge import (  # noqa: E402
    QFormerBridge, QueryReadoutHead,
)


_N_SUBSTRATE = 4096
_M_SUBSTRATE = 4096
_K_PATHS = 500
_D_MODEL = 3072
_DEPTH = 5
_N_QUERIES = 8
_PHI3_MODEL = "microsoft/Phi-3-mini-4k-instruct"


def _bipolar_from_soft(soft_query: torch.Tensor) -> torch.Tensor:
    bipolar = torch.sign(soft_query)
    zero_mask = bipolar == 0
    if zero_mask.any():
        bipolar = bipolar + zero_mask.to(dtype=bipolar.dtype)
    return bipolar


def _build_v1prime_val_to_token(
    model, tokenizer, val_idx_values: list[int], pool_ids: list[int],
    device: torch.device,
) -> dict[int, int]:
    """Path 1a v1': Phi-3-derived val targets (semantic val-side alignment).

    For each distinct val_idx V, forward "Val {V:04d}: " through Phi-3 and
    take argmax over the alphabetic 1024-token target pool. This replaces
    the random val_idx->target_token mapping with one that aligns with
    Phi-3's actual output distribution -- so the training loss has a
    gradient signal connected to a real LLM prediction direction (not a
    random target the LLM has no semantic prior for).

    Per strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md
    Prong A v1' (the val-side complement to v1 key SimHash projection).
    Research notes bundling v1+v1' raises P_deflated from 0.32 -> 0.42;
    v1 alone is predicted to HARD-FAIL P=0.65.
    """
    pool_t = torch.tensor(pool_ids, device=device, dtype=torch.long)
    distinct = sorted(set(int(v) for v in val_idx_values))
    print(f"[path1a_v1prime] computing Phi-3-derived val targets "
          f"for {len(distinct)} distinct val_idx values (one-time)...")
    v_to_t: dict[int, int] = {}
    with torch.no_grad():
        for i, v in enumerate(distinct):
            text = f"Val {v:04d}: "
            enc = tokenizer(text, return_tensors="pt").to(device)
            out = model(input_ids=enc.input_ids)
            logits = out.logits[0, -1, :].to(dtype=torch.float32)
            # Mask non-pool logits to -inf
            mask = torch.full_like(logits, float("-inf"))
            mask[pool_t] = 0.0
            logits_masked = logits + mask
            pred = int(logits_masked.argmax().item())
            v_to_t[v] = pred
            if (i + 1) % 500 == 0:
                print(f"  [path1a_v1prime] {i+1}/{len(distinct)} done")
    return v_to_t


def _build_derived_key_codebook(
    model, tokenizer, key_idx: torch.Tensor, d_model: int, n_sub: int,
    device: torch.device, projection_seed: int = 23,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Path 1a v1: build derived key codewords from Phi-3 hidden states.

    For each key_idx[i], forward "Key {key_idx[i]:04d}: " through Phi-3,
    extract last-position hidden state h_i (d_model-dim), then compute
    derived_key_i = sign(R @ h_i) where R is a fixed Gaussian projection
    (n_sub x d_model) seeded at projection_seed.

    Per research deliverable (notes/research_pp8_phi3_hidden_codeword_design_v1):
    - R fixed, drawn once at init; no trainable parameters
    - Gradient flows through h_i (LLM update direction); no STE at key-generation
    - Codewords are deterministic function of h_i; LLM doesn't need to learn
      the text->codeword mapping, only to produce hidden states whose
      projection retrieves correctly

    Returns:
      derived_keys: (M, n_sub) bipolar {-1, +1}
      R: (n_sub, d_model) fixed Gaussian projection matrix
      h_stack: (M, d_model) raw hidden states (for diagnostics)
    """
    M = int(key_idx.numel())
    print(f"[path1a_v1] computing derived key codewords from Phi-3 hidden states "
          f"({M} keys; this is a one-time forward-pass loop)...")
    h_stack = torch.zeros(M, d_model, device=device, dtype=torch.float32)
    with torch.no_grad():
        for i in range(M):
            k = int(key_idx[i].item())
            text = f"Key {k:04d}: "
            enc = tokenizer(text, return_tensors="pt").to(device)
            try:
                out = model(input_ids=enc.input_ids, output_hidden_states=True)
            except Exception as exc:
                raise RuntimeError(
                    f"path1a_v1: Phi-3 forward failed at key_idx={k} (i={i}): {exc}")
            h = out.hidden_states[-1][0, -1, :].to(dtype=torch.float32)
            h_stack[i] = h
            if (i + 1) % 500 == 0:
                print(f"  [path1a_v1] {i+1}/{M} key hidden states computed")
    # Draw fixed Gaussian R, seeded
    g = torch.Generator(device="cpu")
    g.manual_seed(projection_seed)
    R_cpu = torch.randn(n_sub, d_model, generator=g, dtype=torch.float32)
    R = R_cpu.to(device)
    # Project + sign
    proj = h_stack @ R.T  # (M, n_sub)
    derived = torch.sign(proj)
    derived[derived == 0] = 1.0
    print(f"[path1a_v1] derived codebook shape {tuple(derived.shape)}; "
          f"sample derived[0,:8]: {derived[0,:8].cpu().tolist()}")
    return derived, R, h_stack


def _gram_diagnostic(derived_keys: torch.Tensor) -> dict[str, Any]:
    """Pre-flight Gram-matrix diagnostic on derived key codebook.

    Per research deliverable: if mean |off-diagonal K_ij| > 0.10, apply
    median-threshold centering before training (FM-2 anisotropy rescue).
    """
    M, n_sub = derived_keys.shape
    # Normalized inner products: K = (1/n_sub) k_i . k_j
    K = (derived_keys @ derived_keys.T) / float(n_sub)  # (M, M)
    # Off-diagonal mask
    mask = ~torch.eye(M, dtype=torch.bool, device=K.device)
    off_diag = K[mask]
    mean_abs = off_diag.abs().mean().item()
    pct_above_010 = (off_diag.abs() > 0.10).float().mean().item()
    pct_above_005 = (off_diag.abs() > 0.05).float().mean().item()
    pct_above_030 = (off_diag.abs() > 0.30).float().mean().item()
    diag_mean = K[~mask].mean().item()
    return {
        "M": M,
        "n_sub": n_sub,
        "mean_abs_off_diag": round(mean_abs, 6),
        "diag_mean": round(diag_mean, 6),  # should be 1.0 (bipolar self-correlation)
        "pct_off_diag_above_005": round(pct_above_005, 6),
        "pct_off_diag_above_010": round(pct_above_010, 6),
        "pct_off_diag_above_030": round(pct_above_030, 6),
        # Per research FM-1: collapse threshold; FM-2: anisotropy bias threshold
        "fm1_collapse_warn": pct_above_010 > 0.50,
        "fm2_anisotropy_warn": mean_abs > 0.10,
    }


def _substrate_retrieve_soft(
    codebook: torch.Tensor, key_idx: torch.Tensor, val_idx: torch.Tensor,
    soft_query: torch.Tensor, temperature: float = 1.0,
) -> torch.Tensor:
    """Phase 2.5 iteration 2: soft-substrate retrieval (attention-weighted).

    Fully differentiable replacement for the STE pipeline. Computes attention
    weights from soft_query to each key codeword in the substrate, then takes
    a weighted sum of the corresponding value codewords:

      sim = soft_query @ codebook[key_idx].T / temperature  # (B, M)
      attn = softmax(sim, dim=-1)                            # (B, M)
      retrieved = attn @ codebook[val_idx]                  # (B, n_sub)

    Compared to STE (which had backward-identity-through-discrete-retrieval),
    the gradient through softmax-attention DIRECTLY tells the readout: "the
    way to retrieve a more useful value codeword is to make soft_query more
    similar to key codeword K_i (where K_i is the key whose value would help
    the bridge produce a better prefix)."

    Temperature parameter:
    - High (>10): smooth attention; weak inductive bias toward discrete keys
    - 1.0: standard softmax; well-separated keys produce sharp attention
    - Low (<0.1): nearly argmax; vanishing gradients into low-weight keys

    Start at 1.0 (default). If training converges at this temperature, can
    anneal toward smaller values for more discrete behavior.
    """
    keys_codebook = codebook[key_idx].to(dtype=soft_query.dtype)  # (M, n_sub)
    vals_codebook = codebook[val_idx].to(dtype=soft_query.dtype)  # (M, n_sub) aligned
    sim = soft_query @ keys_codebook.T / max(temperature, 1e-6)  # (B, M)
    attn = torch.softmax(sim, dim=-1)
    retrieved = attn @ vals_codebook  # (B, n_sub)
    return retrieved


def _substrate_retrieve_ste(
    codebook: torch.Tensor, key_idx: torch.Tensor, val_idx: torch.Tensor,
    relation: dict, soft_query: torch.Tensor,
) -> torch.Tensor:
    """Phase 2.5 substrate-in-loop retrieval with straight-through estimator.

    Performs true key->value lookup via the substrate's relation graph:
      1. sign(soft_query) -> bipolar query (B, n_sub)
      2. Find nearest KEY codeword: argmax_k(bipolar @ codebook[key_idx_k].T)
      3. Look up value: relation[chosen_key_idx] -> val_idx
      4. Retrieve value codeword: codebook[val_idx] (B, n_sub) discrete bipolar

    STE: forward returns the discrete retrieved value codeword (bipolar);
    backward passes gradient through soft_query (identity) so the readout
    can learn to produce queries that retrieve task-relevant codewords.

    NB: this fixes the architectural gap discovered during Phase 2.5 design:
    the existing `path_d_run` returns a correctness INDICATOR (0/1), not a
    codeword. The wiring smoke (Phase 1) was inadvertently using
    `codebook[0..1]` as the "retrieved" codeword regardless of query.
    True associative memory retrieval requires the key->relation->value
    pipeline implemented here.
    """
    B, n_sub = soft_query.shape
    with torch.no_grad():
        bipolar = _bipolar_from_soft(soft_query)
        # Restrict cleanup to the M codewords that ARE keys in the relation
        # graph (avoids matching to value-only codewords; semantically the
        # readout encodes a KEY, not an arbitrary codeword).
        keys_codebook = codebook[key_idx]  # (M, n_sub)
        sim = bipolar @ keys_codebook.T  # (B, M)
        nearest_pos = sim.argmax(dim=-1)  # (B,) positions in key_idx tensor
        # Map back to codebook indices, then look up value via relation graph
        nearest_key_idx = key_idx[nearest_pos]  # (B,) codebook indices
        retrieved_rows: list[torch.Tensor] = []
        for b in range(B):
            k = int(nearest_key_idx[b].item())
            v = relation.get(k, k)  # default to identity if key not in graph
            v = max(0, min(int(v), codebook.shape[0] - 1))
            retrieved_rows.append(codebook[v].to(dtype=torch.float32))
        retrieved = torch.stack(retrieved_rows, dim=0)  # (B, n_sub)
    # STE: forward value = retrieved (discrete); backward gradient = identity
    # to soft_query.
    return soft_query + (retrieved - soft_query).detach()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _batchify(rows: list[dict[str, Any]], batch_size: int, shuffle: bool, seed: int):
    """Yields lists of `batch_size` row-dicts. Drops the last partial batch."""
    if shuffle:
        rng = torch.Generator()
        rng.manual_seed(seed)
        idx = torch.randperm(len(rows), generator=rng).tolist()
    else:
        idx = list(range(len(rows)))
    for i in range(0, len(idx) - batch_size + 1, batch_size):
        yield [rows[k] for k in idx[i:i + batch_size]]


def _tokenize_batch(tokenizer, batch: list[dict[str, Any]], device: torch.device):
    """Tokenize query_text + target_token_id; return prompt input_ids + targets."""
    texts = [row["query_text"] for row in batch]
    targets = [row["target_token_id"] for row in batch]
    enc = tokenizer(texts, return_tensors="pt", padding=True)
    return (
        enc.input_ids.to(device),
        enc.attention_mask.to(device),
        torch.tensor(targets, dtype=torch.long, device=device),
    )


def _last_position_hidden(out, attention_mask: torch.Tensor) -> torch.Tensor:
    """Extract last-non-pad position hidden state from HF output.hidden_states[-1].

    `out.hidden_states[-1]` shape (B, T, d_model); we want the hidden state at
    the last attended position per row.
    """
    hidden = out.hidden_states[-1]  # (B, T, d)
    seq_lens = attention_mask.sum(dim=1) - 1  # (B,) index of last attended pos
    B = hidden.shape[0]
    return hidden[torch.arange(B, device=hidden.device), seq_lens, :]


def _load_mock_model(device: torch.device):
    """CPU mock: tiny GPT-2 at d_model=3072 + GPT-2-small tokenizer + NO LoRA.

    For local-CPU smoke of the training+eval flow without bitsandbytes/CUDA.
    Phi-3 + LoRA = production; this mock validates shapes + loss-decreases +
    backward grad flow on bridge + readout only (model itself is frozen).
    """
    from transformers import GPT2Config, GPT2LMHeadModel, GPT2Tokenizer
    cfg = GPT2Config(
        vocab_size=50257, n_positions=512, n_embd=_D_MODEL, n_layer=2,
        n_head=8, n_inner=4096,
    )
    model = GPT2LMHeadModel(cfg).to(device).to(dtype=torch.float32).eval()
    # Freeze ALL model params (mock-LoRA: only bridge + readout train)
    for p in model.parameters():
        p.requires_grad = False
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if not hasattr(model, "dtype"):
        model.dtype = torch.float32
    return model, tokenizer


def _load_phi3_lora(device: torch.device, lora_r: int, lora_alpha: int):
    """Load Phi-3-mini-4bit + attach LoRA adapters (trainable)."""
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              BitsAndBytesConfig)
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    if device.type != "cuda":
        raise RuntimeError(
            "Phi-3 + QLoRA requires CUDA. Use --mock-model for CPU smoke.")

    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(_PHI3_MODEL, trust_remote_code=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        _PHI3_MODEL,
        quantization_config=bnb_cfg,
        device_map={"": 0},
        trust_remote_code=False,
        attn_implementation="eager",
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model, tokenizer


def _train_step(
    model, readout, bridge, batch, tokenizer, device, optimizer, scheduler=None,
    substrate_in_loop: bool = False, substrate_tuple=None,
    substrate_soft: bool = False, substrate_soft_temperature: float = 1.0,
    path1a_R: torch.Tensor | None = None,
) -> float:
    """One training step. Returns scalar loss.

    Three modes for the readout -> bridge intermediate:
      - substrate_soft (Phase 2.5 iteration 2): softmax-attention-weighted
        retrieval over keys; fully differentiable; gradient pushes readout
        toward "produce queries that select better keys"
      - substrate_in_loop (Phase 2.5 iteration 1, STE): discrete cleanup +
        argmax + relation lookup, STE for backward; empirically degenerate
        because STE gradient = identity through retrieval
      - neither (Phase 2 baseline): soft_tanh straight to bridge; bypasses
        substrate; validates bridge trainability but not substrate utility
    """
    input_ids, attention_mask, targets = _tokenize_batch(tokenizer, batch, device)

    # Phase 1 prefill (LoRA active)
    out = model(
        input_ids=input_ids, attention_mask=attention_mask,
        use_cache=True, output_hidden_states=True,
    )
    past = out.past_key_values
    hidden = _last_position_hidden(out, attention_mask).to(dtype=torch.float32)

    # Soft-query computation: either via the trainable readout (Phase 2/2.5)
    # or via the fixed Path 1a v1 R-projection (no trainable params per research
    # deliverable; codewords are deterministic function of h_i).
    if path1a_R is not None:
        soft_query = hidden @ path1a_R.T  # (B, n_sub) continuous
    else:
        soft_query = readout(hidden)  # (B, n_sub) tanh-bounded
    if substrate_soft and substrate_tuple is not None:
        codebook, _W, key_idx, val_idx, _relation = substrate_tuple
        bridge_input = _substrate_retrieve_soft(
            codebook, key_idx, val_idx, soft_query,
            temperature=substrate_soft_temperature,
        )
    elif substrate_in_loop and substrate_tuple is not None:
        codebook, _W, key_idx, val_idx, relation = substrate_tuple
        bridge_input = _substrate_retrieve_ste(
            codebook, key_idx, val_idx, relation, soft_query,
        )
    else:
        bridge_input = soft_query
    prefix_tokens = bridge(bridge_input)  # (B, n_queries, d_model)

    # Phase 2 decode-1-token: inject prefix as 8 soft-prompt embeddings,
    # extend KV cache, and read logits at the first decode position.
    decode_out = model(
        inputs_embeds=prefix_tokens.to(dtype=model.dtype),
        past_key_values=past,
        use_cache=False,
    )
    # decode_out.logits shape: (B, n_queries, vocab); take last-prefix position
    logits = decode_out.logits[:, -1, :]  # (B, vocab)
    loss = F.cross_entropy(logits, targets)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if scheduler is not None:
        scheduler.step()
    return float(loss.item())


@torch.no_grad()
def _eval(
    model, readout, bridge, val_rows, tokenizer, device,
    substrate_tuple, batch_size: int = 4, max_samples: int | None = None,
    use_substrate_in_loop: bool = True,
    substrate_soft: bool = False, substrate_soft_temperature: float = 1.0,
    target_pool_ids: list[int] | None = None,
    path1a_R: torch.Tensor | None = None,
) -> dict[str, Any]:
    """Validation eval. Reports top-1 accuracy on val set.

    If use_substrate_in_loop, the substrate Path D retrieval is used between
    readout and bridge (validation against the real inference pipeline).
    Otherwise the bypass-substrate path is used (debug-mode; should match
    training-time behavior).
    """
    model.eval()
    readout.eval()
    bridge.eval()
    codebook, W, key_idx, val_idx, relation = substrate_tuple
    starts = key_idx[:1].to(device)

    rows = val_rows if max_samples is None else val_rows[:max_samples]
    correct = 0
    total = 0

    for batch in _batchify(rows, batch_size, shuffle=False, seed=0):
        input_ids, attention_mask, targets = _tokenize_batch(tokenizer, batch, device)
        out = model(
            input_ids=input_ids, attention_mask=attention_mask,
            use_cache=True, output_hidden_states=True,
        )
        past = out.past_key_values
        hidden = _last_position_hidden(out, attention_mask).to(dtype=torch.float32)

        if path1a_R is not None:
            soft_query = hidden @ path1a_R.T  # (B, n_sub) continuous
        else:
            soft_query = readout(hidden)  # (B, n_sub)
        if substrate_soft:
            codeword_batch = _substrate_retrieve_soft(
                codebook, key_idx, val_idx, soft_query,
                temperature=substrate_soft_temperature,
            )
        elif use_substrate_in_loop:
            codeword_batch = _substrate_retrieve_ste(
                codebook, key_idx, val_idx, relation, soft_query,
            )
        else:
            codeword_batch = soft_query  # Phase 2 baseline path

        prefix_tokens = bridge(codeword_batch)  # (B, n_queries, d_model)
        decode_out = model(
            inputs_embeds=prefix_tokens.to(dtype=model.dtype),
            past_key_values=past,
            use_cache=False,
        )
        logits = decode_out.logits[:, -1, :]
        # CRITICAL: restrict argmax to the target pool. Without this mask,
        # argmax over the full ~32K Phi-3 vocab will preferentially pick
        # common non-pool tokens ("the", "of", " ", etc.) regardless of how
        # well the model has learned to skew probability toward the 1024-
        # token target pool. The CE loss measures distribution-level skew
        # (which trains fine; loss decreases 40-44% across runs); argmax
        # accuracy on the full vocab does not reflect that skew. The task
        # constrains the answer to one of 1024 target tokens, so the eval
        # argmax should be similarly constrained.
        if target_pool_ids is not None:
            mask = torch.full_like(logits, float("-inf"))
            pool_tensor = torch.tensor(target_pool_ids, device=logits.device,
                                       dtype=torch.long)
            mask[:, pool_tensor] = 0.0
            logits = logits + mask
        pred = logits.argmax(dim=-1)
        correct += int((pred == targets).sum().item())
        total += int(targets.numel())

    acc = correct / max(1, total)
    model.train()
    readout.train()
    bridge.train()
    return {"acc_top1": acc, "n": total, "correct": correct}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PP-8 Week 2 Phase 2: QLoRA fine-tune (Q-Former + readout + LoRA)")
    parser.add_argument("--dataset-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--eval-every-k", type=int, default=50)
    parser.add_argument("--checkpoint-every-k", type=int, default=100)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--substrate-seed", type=int, default=7,
                        help="Must match dataset's substrate_seed (manifest)")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eval-max-samples", type=int, default=200,
                        help="Cap val-eval to first N samples per step for speed")
    parser.add_argument("--substrate-in-loop-eval", action="store_true",
                        help="Eval through key-cleanup + relation graph value "
                             "lookup (Phase 2.5). Implies substrate-in-loop is "
                             "the eval pipeline; auto-enabled when "
                             "--substrate-in-loop-train is set.")
    parser.add_argument("--substrate-in-loop-train", action="store_true",
                        help="(Phase 2.5 STE iteration; superseded by "
                             "--substrate-soft) Train with substrate IN THE LOOP "
                             "via discrete cleanup + STE. Empirically degenerate "
                             "(STE gradient bypasses substrate's discriminative "
                             "function; commit 8d1e44a deliverable).")
    parser.add_argument("--substrate-soft", action="store_true",
                        help="(Phase 2.5 iteration 2) Train with substrate "
                             "IN THE LOOP via softmax-attention-weighted "
                             "retrieval (fully differentiable). Replaces the "
                             "STE pipeline. Auto-enables substrate-soft eval "
                             "for train/eval pipeline consistency.")
    parser.add_argument("--substrate-soft-temperature", type=float, default=1.0,
                        help="Temperature for soft-substrate softmax attention "
                             "(higher = smoother attention over keys; lower = "
                             "more peaked toward argmax). Default 1.0.")
    parser.add_argument("--path1a-v1", action="store_true",
                        help="(Phase 2.5 Path 1a v1) Use fixed Gaussian "
                             "random projection + sign for substrate key "
                             "codewords (derived from Phi-3 hidden states). "
                             "Per research deliverable v1; no new trainable "
                             "params (readout MLP excluded from optimizer). "
                             "Requires --substrate-soft for the retrieval path. "
                             "Implies substrate-in-loop eval.")
    parser.add_argument("--path1a-projection-seed", type=int, default=23,
                        help="Seed for the fixed Gaussian projection R matrix "
                             "(reproducible across runs).")
    parser.add_argument("--lr-schedule", default="cosine",
                        choices=["cosine", "wsd", "constant"],
                        help="LR schedule: cosine (default; current baseline; "
                             "warmup -> cosine decay); wsd (warmup-stable-decay; "
                             "Round 4 v1b primary mitigation); constant (warmup "
                             "then constant LR; no decay).")
    parser.add_argument("--lr-warmup-frac", type=float, default=0.10,
                        help="Fraction of max_steps for linear warmup. Default 0.10.")
    parser.add_argument("--lr-stable-frac", type=float, default=0.60,
                        help="(WSD only) fraction of max_steps for stable-at-peak "
                             "phase between warmup and decay. Default 0.60.")
    parser.add_argument("--lr-decay-floor-frac", type=float, default=0.0,
                        help="LR floor as fraction of peak LR after decay. "
                             "Default 0.0 (decay to zero; reproduces v1+v1' / "
                             "Option A behavior). Try 0.3 for stable convergence.")
    parser.add_argument("--ema-decay", type=float, default=0.0,
                        help="EMA shadow-model decay coefficient. 0.0 disables. "
                             "Round 4 v1b recommends 0.999.")
    parser.add_argument("--path1a-v1prime", action="store_true",
                        help="(Phase 2.5 Path 1a v1') Val-side semantic "
                             "alignment: replace random val_idx->target_token "
                             "with Phi-3-most-likely next-token of "
                             "'Val {V:04d}: ' restricted to alphabetic pool. "
                             "Bundles with --path1a-v1 to form the v1+v1' "
                             "intervention (research P_deflated=0.42 vs "
                             "v1-only P_deflated=0.32).")
    parser.add_argument("--path1a-frozen-random-keys", action="store_true",
                        help="(Round 4 D1-1 control test) Replace v1's "
                             "Phi-3-derived key codebook with frozen random "
                             "bipolar vectors (seeded per key_idx). Discriminates "
                             "M1-dominant (random suffices) vs M2-load-bearing "
                             "(Phi-3 semantic geometry required) per research "
                             "Round 4 mechanism analysis. Requires --path1a-v1 "
                             "+ --path1a-v1prime for proper control comparison.")
    parser.add_argument("--mock-model", action="store_true",
                        help="Use a CPU mock model (GPT-2 at d_model=3072) "
                             "with model frozen and only readout+bridge "
                             "trainable. For local-smoke validation of the "
                             "training pipeline before H100 dispatch. "
                             "Implies --device cpu.")
    args = parser.parse_args()

    if args.mock_model:
        device = torch.device("cpu")
    elif args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    # Phase 2.5: substrate-in-loop training implies substrate-in-loop eval
    # (train + eval pipelines must match or val metric is meaningless).
    if args.substrate_in_loop_train and not args.substrate_in_loop_eval:
        args.substrate_in_loop_eval = True
        print("[qlora_train] --substrate-in-loop-train set; auto-enabling "
              "--substrate-in-loop-eval for train/eval pipeline consistency")
    if args.substrate_soft and not args.substrate_in_loop_eval:
        args.substrate_in_loop_eval = True
        print("[qlora_train] --substrate-soft set; auto-enabling "
              "--substrate-in-loop-eval for train/eval pipeline consistency")
    if args.path1a_v1:
        if not args.substrate_soft:
            args.substrate_soft = True
            print("[qlora_train] --path1a-v1 set; auto-enabling --substrate-soft "
                  "(required for the soft-retrieval over derived codebook)")
        if not args.substrate_in_loop_eval:
            args.substrate_in_loop_eval = True

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.is_absolute():
        dataset_dir = _REPO_ROOT / dataset_dir

    # Lazily regenerate dataset if missing (e.g. fresh cloud instance where
    # only the repo + substrate_seed are deterministic; dataset is not in git).
    if not (dataset_dir / "manifest.json").is_file():
        print(f"[qlora_train] dataset_dir missing manifest.json; "
              f"regenerating from substrate_seed={args.substrate_seed}...")
        import subprocess
        regen_cmd = [
            sys.executable, "-u",
            "-m", "testbed.llm_integration.phase2_toy_dataset_gen",
            "--n-train", "4000", "--n-val", "1000",
            "--substrate-seed", str(args.substrate_seed),
            "--out-dir", str(dataset_dir),
        ]
        proc = subprocess.run(regen_cmd, cwd=str(_REPO_ROOT))
        if proc.returncode != 0:
            raise RuntimeError(
                f"dataset regen failed (rc={proc.returncode}); check stderr")

    # Load dataset
    print(f"[qlora_train] loading dataset from {dataset_dir}...")
    manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest["substrate_seed"] != args.substrate_seed:
        raise RuntimeError(
            f"substrate_seed mismatch: dataset has {manifest['substrate_seed']}, "
            f"trainer arg is {args.substrate_seed}. They MUST match.")
    train_rows = _load_jsonl(dataset_dir / "train.jsonl")
    val_rows = _load_jsonl(dataset_dir / "val.jsonl")
    random_baseline = manifest["random_baseline_top1"]
    target_pool_ids = manifest.get("target_vocab_pool_ids", None)
    print(f"[qlora_train] {len(train_rows)} train / {len(val_rows)} val")
    print(f"[qlora_train] random-baseline top-1 = {random_baseline:.4%}")
    if target_pool_ids is not None:
        print(f"[qlora_train] eval argmax restricted to "
              f"{len(target_pool_ids)}-token target pool")

    # Build substrate (same seed as dataset)
    print(f"[qlora_train] building substrate (seed={args.substrate_seed})...")
    substrate_tuple = build_shared(
        _N_SUBSTRATE, _M_SUBSTRATE, args.substrate_seed, device)

    # Load model + bridge + readout
    if args.mock_model:
        print(f"[qlora_train] loading CPU MOCK (GPT-2 frozen at d_model={_D_MODEL})...")
        model, tokenizer = _load_mock_model(device)
        # The dataset's target_token_id field uses Phi-3 tokenizer IDs; for the
        # mock we ignore that and just check loss-decrease on whatever the GPT-2
        # tokenizer does with the query text. This validates the training loop
        # mechanics, not the actual target-token-prediction quality.
    else:
        print(f"[qlora_train] loading Phi-3 + LoRA (r={args.lora_r}, alpha={args.lora_alpha})...")
        model, tokenizer = _load_phi3_lora(device, args.lora_r, args.lora_alpha)

    torch.manual_seed(args.seed)
    readout = QueryReadoutHead().to(device).to(dtype=torch.float32)
    bridge = QFormerBridge().to(device).to(dtype=torch.float32)

    # Path 1a v1': Phi-3-derived val targets (run BEFORE v1 to share the
    # one-time Phi-3 forward overhead with v1 build below).
    v1prime_summary: dict[str, Any] | None = None
    if args.path1a_v1prime:
        if args.mock_model:
            print(f"[path1a_v1prime] --mock-model: skipping Phi-3 val-target "
                  f"derivation (CUDA-only); val targets stay from dataset")
        elif target_pool_ids is None:
            print(f"[path1a_v1prime] WARN: dataset manifest has no "
                  f"target_vocab_pool_ids; cannot run v1' val derivation")
        else:
            all_val_idx = [r["val_idx"] for r in train_rows + val_rows]
            v_to_t_v1prime = _build_v1prime_val_to_token(
                model, tokenizer, all_val_idx, target_pool_ids, device,
            )
            # Rewrite target_token_id field in train + val rows
            for r in train_rows:
                r["target_token_id"] = v_to_t_v1prime[r["val_idx"]]
                r["target_token_str"] = tokenizer.decode(
                    [r["target_token_id"]]).strip()
            for r in val_rows:
                r["target_token_id"] = v_to_t_v1prime[r["val_idx"]]
                r["target_token_str"] = tokenizer.decode(
                    [r["target_token_id"]]).strip()
            # Summary stats
            from collections import Counter
            tok_counts = Counter(v_to_t_v1prime.values())
            v1prime_summary = {
                "n_distinct_val_idx": len(v_to_t_v1prime),
                "n_distinct_target_tokens": len(tok_counts),
                "max_token_multiplicity": max(tok_counts.values()),
                "min_token_multiplicity": min(tok_counts.values()),
            }
            print(f"[path1a_v1prime] {v1prime_summary}")

    # Path 1a v1: derived key codebook + fixed R projection (no trainable readout)
    path1a_R: torch.Tensor | None = None
    path1a_gram: dict[str, Any] | None = None
    if args.path1a_v1:
        if args.path1a_frozen_random_keys:
            # Round 4 D1-1: control test. Substitute Phi-3-derived keys with
            # frozen random bipolar vectors. v1' val-side stays Phi-3-derived.
            # Discriminates Mechanism 1 (random sufficient) vs Mechanism 2
            # (Phi-3 semantic geometry load-bearing).
            print(f"[d1_1_control] --path1a-frozen-random-keys: replacing v1 "
                  f"Phi-3 hidden-state derivation with frozen random bipolar "
                  f"vectors (seeded per key_idx; semantic geometry control)")
            M = int(substrate_tuple[2].numel())
            g = torch.Generator(device="cpu")
            g.manual_seed(args.path1a_projection_seed + 1000)  # distinct seed
            random_keys_cpu = torch.sign(torch.randn(
                M, _N_SUBSTRATE, generator=g, dtype=torch.float32))
            random_keys_cpu[random_keys_cpu == 0] = 1.0
            derived_keys = random_keys_cpu.to(device)
            # Still need path1a_R for the readout-side projection (the readout
            # projects hidden -> soft_query; even with random keys, the
            # projection is needed for the soft-attention sim computation).
            R_g = torch.Generator(device="cpu")
            R_g.manual_seed(args.path1a_projection_seed)
            path1a_R = torch.randn(_N_SUBSTRATE, _D_MODEL, generator=R_g,
                                   dtype=torch.float32).to(device)
            # Diagnostic on the random keys (should show very different Gram
            # from a Phi-3-derived codebook -- baseline for comparison)
            path1a_gram = _gram_diagnostic(derived_keys)
            print(f"[d1_1_control] Gram diagnostic (frozen random keys):")
            for k, v in path1a_gram.items():
                print(f"  {k}: {v}")
            # Replace key codewords in substrate codebook with random keys
            codebook_mut = substrate_tuple[0].clone()
            codebook_mut[substrate_tuple[2]] = derived_keys.to(
                dtype=codebook_mut.dtype)
            substrate_tuple = (codebook_mut,) + substrate_tuple[1:]
            print(f"[d1_1_control] substrate codebook updated: keys at "
                  f"codebook[key_idx] replaced with frozen random bipolar")
        elif args.mock_model:
            # Mock mode: skip Phi-3 derivation; use random R-projection only
            print(f"[path1a_v1] --mock-model + --path1a-v1: skipping Phi-3 "
                  f"hidden-state derivation (CUDA-only); using random R only")
            g = torch.Generator(device="cpu")
            g.manual_seed(args.path1a_projection_seed)
            path1a_R = torch.randn(_N_SUBSTRATE, _D_MODEL, generator=g,
                                   dtype=torch.float32).to(device)
        else:
            derived_keys, path1a_R, h_stack = _build_derived_key_codebook(
                model, tokenizer, substrate_tuple[2], _D_MODEL, _N_SUBSTRATE,
                device, projection_seed=args.path1a_projection_seed,
            )
            # Pre-flight Gram-matrix diagnostic
            path1a_gram = _gram_diagnostic(derived_keys)
            print(f"[path1a_v1] Gram diagnostic:")
            for k, v in path1a_gram.items():
                print(f"  {k}: {v}")
            if path1a_gram["fm1_collapse_warn"]:
                print(f"[WARN] FM-1 collapse risk: "
                      f"{path1a_gram['pct_off_diag_above_010']:.1%} pairs >0.10. "
                      f"Per research deliverable, consider mid-layer probe.")
            if path1a_gram["fm2_anisotropy_warn"]:
                print(f"[WARN] FM-2 anisotropy bias: "
                      f"mean |off-diag|={path1a_gram['mean_abs_off_diag']:.4f} > 0.10. "
                      f"Per research deliverable, consider median-threshold centering.")
            # Replace key codewords in substrate codebook with derived ones
            codebook_mut = substrate_tuple[0].clone()
            codebook_mut[substrate_tuple[2]] = derived_keys.to(dtype=codebook_mut.dtype)
            substrate_tuple = (codebook_mut,) + substrate_tuple[1:]
            print(f"[path1a_v1] substrate codebook updated: keys at "
                  f"codebook[key_idx] replaced with sign(R @ h_i)")

    # Build optimizer over ALL trainable params (LoRA + readout + bridge)
    # When --path1a-v1, readout is EXCLUDED (becomes fixed R-projection per research).
    trainable_params = []
    n_readout = 0
    n_bridge = 0
    n_lora = 0
    if not args.path1a_v1:
        for p in readout.parameters():
            trainable_params.append(p)
            n_readout += p.numel()
    else:
        # Freeze readout params (they're not used; we use path1a_R directly)
        for p in readout.parameters():
            p.requires_grad = False
        print(f"[path1a_v1] readout MLP excluded from trainable params "
              f"(replaced by fixed R-projection; ~25MB fixed weight)")
    for p in bridge.parameters():
        trainable_params.append(p)
        n_bridge += p.numel()
    for p in model.parameters():
        if p.requires_grad:
            trainable_params.append(p)
            n_lora += p.numel()
    print(f"[qlora_train] trainable: readout {n_readout/1e6:.2f}M + "
          f"bridge {n_bridge/1e6:.2f}M + lora {n_lora/1e6:.2f}M = "
          f"{(n_readout + n_bridge + n_lora)/1e6:.2f}M")

    optimizer = torch.optim.AdamW(
        trainable_params, lr=args.lr, weight_decay=0.01, betas=(0.9, 0.999),
    )
    # LR schedule: cosine (current default) / wsd (warmup-stable-decay; PRIMARY
    # mitigation per research v1b grid) / constant (warmup-then-constant).
    warmup_frac = args.lr_warmup_frac
    warmup_steps = max(1, int(args.max_steps * warmup_frac))
    stable_frac = args.lr_stable_frac  # WSD only: fraction at peak between warmup and decay
    decay_floor_frac = args.lr_decay_floor_frac  # cosine/wsd: floor as frac of peak

    if args.lr_schedule == "cosine":
        def lr_lambda(step):
            if step < warmup_steps:
                return step / warmup_steps
            progress = (step - warmup_steps) / max(1, args.max_steps - warmup_steps)
            decay = 0.5 * (1.0 + math.cos(math.pi * progress))
            return decay_floor_frac + (1.0 - decay_floor_frac) * decay
    elif args.lr_schedule == "wsd":
        stable_end = warmup_steps + int(stable_frac * args.max_steps)
        def lr_lambda(step):
            if step < warmup_steps:
                return step / warmup_steps
            if step < stable_end:
                return 1.0
            progress = (step - stable_end) / max(1, args.max_steps - stable_end)
            decay = 0.5 * (1.0 + math.cos(math.pi * progress))
            return decay_floor_frac + (1.0 - decay_floor_frac) * decay
    elif args.lr_schedule == "constant":
        def lr_lambda(step):
            if step < warmup_steps:
                return step / warmup_steps
            return 1.0
    else:
        raise ValueError(f"unknown --lr-schedule: {args.lr_schedule}")
    print(f"[qlora_train] LR schedule: {args.lr_schedule} "
          f"(warmup_steps={warmup_steps}, stable_frac={stable_frac}, "
          f"decay_floor_frac={decay_floor_frac})")
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    # EMA shadow model (zero-cost dual-eval per research v1b spec): exponential
    # moving average of the trainable params. eval can use shadow weights to
    # measure "what the model would predict at a smoothed-trajectory point"
    # instead of the live noisy weights.
    ema_decay = args.ema_decay
    ema_enabled = ema_decay > 0.0
    if ema_enabled:
        ema_shadow: dict[str, torch.Tensor] = {}
        # Snapshot ALL trainable params (readout + bridge + LoRA) into shadow
        for mname, mod in [("readout", readout), ("bridge", bridge)]:
            for pname, p in mod.named_parameters():
                if p.requires_grad:
                    ema_shadow[f"{mname}.{pname}"] = p.detach().clone()
        for pname, p in model.named_parameters():
            if p.requires_grad:
                ema_shadow[f"model.{pname}"] = p.detach().clone()
        print(f"[qlora_train] EMA shadow enabled (decay={ema_decay}; "
              f"tracking {len(ema_shadow)} param tensors)")
    else:
        ema_shadow = None
        print(f"[qlora_train] EMA shadow disabled (--ema-decay=0)")

    # Training loop
    progress_path = out_dir / "train_progress.jsonl"
    progress_path.write_text("", encoding="utf-8")

    model.train()
    readout.train()
    bridge.train()

    def _swap_to_ema():
        """Swap live weights for EMA shadow. Returns mapping of {key: live tensor} to restore."""
        saved = {}
        if not ema_enabled or ema_shadow is None:
            return saved
        with torch.no_grad():
            for mname, mod in [("readout", readout), ("bridge", bridge)]:
                for pname, p in mod.named_parameters():
                    if not p.requires_grad:
                        continue
                    key = f"{mname}.{pname}"
                    saved[key] = p.data.clone()
                    p.data.copy_(ema_shadow[key])
            for pname, p in model.named_parameters():
                if not p.requires_grad:
                    continue
                key = f"model.{pname}"
                if key in ema_shadow:
                    saved[key] = p.data.clone()
                    p.data.copy_(ema_shadow[key])
        return saved

    def _restore_from_ema(saved):
        if not saved:
            return
        with torch.no_grad():
            for mname, mod in [("readout", readout), ("bridge", bridge)]:
                for pname, p in mod.named_parameters():
                    if not p.requires_grad:
                        continue
                    key = f"{mname}.{pname}"
                    if key in saved:
                        p.data.copy_(saved[key])
            for pname, p in model.named_parameters():
                if not p.requires_grad:
                    continue
                key = f"model.{pname}"
                if key in saved:
                    p.data.copy_(saved[key])

    step = 0
    losses_window: list[float] = []  # rolling for smooth log
    early_baseline_loss: float | None = None
    val_history: list[tuple[int, float, float]] = []  # (step, live_acc, ema_acc)
    t0 = time.perf_counter()
    print(f"[qlora_train] starting; max_steps={args.max_steps} "
          f"batch_size={args.batch_size} lr={args.lr} "
          f"eval_every_k={args.eval_every_k} ckpt_every_k={args.checkpoint_every_k}")

    while step < args.max_steps:
        for batch in _batchify(
            train_rows, args.batch_size, shuffle=True, seed=args.seed + step,
        ):
            if step >= args.max_steps:
                break
            try:
                loss_val = _train_step(
                    model, readout, bridge, batch, tokenizer, device,
                    optimizer, scheduler,
                    substrate_in_loop=args.substrate_in_loop_train,
                    substrate_tuple=substrate_tuple,
                    substrate_soft=args.substrate_soft,
                    substrate_soft_temperature=args.substrate_soft_temperature,
                    path1a_R=path1a_R,
                )
                # EMA shadow update (per-step; after optimizer step)
                if ema_enabled and ema_shadow is not None:
                    with torch.no_grad():
                        for mname, mod in [("readout", readout), ("bridge", bridge)]:
                            for pname, p in mod.named_parameters():
                                if not p.requires_grad:
                                    continue
                                key = f"{mname}.{pname}"
                                ema_shadow[key].mul_(ema_decay).add_(
                                    p.detach(), alpha=1.0 - ema_decay)
                        for pname, p in model.named_parameters():
                            if not p.requires_grad:
                                continue
                            key = f"model.{pname}"
                            if key in ema_shadow:
                                ema_shadow[key].mul_(ema_decay).add_(
                                    p.detach(), alpha=1.0 - ema_decay)
            except Exception as exc:
                print(f"[ERROR] step {step}: {exc}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                # write a marker and continue
                with progress_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "step": step, "kind": "error", "error": str(exc),
                        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }) + "\n")
                step += 1
                continue

            if math.isnan(loss_val) or math.isinf(loss_val):
                print(f"[FAIL] step {step}: loss is {loss_val}; aborting",
                      file=sys.stderr)
                with progress_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "step": step, "kind": "nan_inf_fail",
                        "loss": loss_val,
                        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }) + "\n")
                return 2

            losses_window.append(loss_val)
            if len(losses_window) > 50:
                losses_window.pop(0)
            if early_baseline_loss is None and step >= 5:
                early_baseline_loss = sum(losses_window) / len(losses_window)

            # Periodic logging
            if step % 10 == 0 or step == args.max_steps - 1:
                lr_now = optimizer.param_groups[0]["lr"]
                roll = sum(losses_window) / len(losses_window)
                print(f"  step {step:>4d}/{args.max_steps} "
                      f"loss={loss_val:.4f} rolling50={roll:.4f} lr={lr_now:.2e}",
                      flush=True)

            # Per-step JSONL
            with progress_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "step": step, "kind": "train",
                    "loss": round(loss_val, 6),
                    "lr": optimizer.param_groups[0]["lr"],
                    "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                }) + "\n")

            # Eval
            if args.eval_every_k > 0 and (
                step > 0 and step % args.eval_every_k == 0
                or step == args.max_steps - 1
            ):
                eval_t0 = time.perf_counter()
                ev = _eval(
                    model, readout, bridge, val_rows, tokenizer, device,
                    substrate_tuple, batch_size=args.batch_size,
                    max_samples=args.eval_max_samples,
                    use_substrate_in_loop=args.substrate_in_loop_eval,
                    substrate_soft=args.substrate_soft,
                    substrate_soft_temperature=args.substrate_soft_temperature,
                    target_pool_ids=target_pool_ids,
                    path1a_R=path1a_R,
                )
                ev_ema = None
                if ema_enabled:
                    saved = _swap_to_ema()
                    try:
                        ev_ema = _eval(
                            model, readout, bridge, val_rows, tokenizer, device,
                            substrate_tuple, batch_size=args.batch_size,
                            max_samples=args.eval_max_samples,
                            use_substrate_in_loop=args.substrate_in_loop_eval,
                            substrate_soft=args.substrate_soft,
                            substrate_soft_temperature=args.substrate_soft_temperature,
                            target_pool_ids=target_pool_ids,
                            path1a_R=path1a_R,
                        )
                    finally:
                        _restore_from_ema(saved)
                # Track val history for peak / stability / retention metrics
                val_history.append((
                    step,
                    ev["acc_top1"],
                    ev_ema["acc_top1"] if ev_ema is not None else float("nan"),
                ))
                eval_wall = time.perf_counter() - eval_t0
                lift_over_random = ev["acc_top1"] / max(1e-9, random_baseline)
                ema_str = ""
                if ev_ema is not None:
                    ema_lift = ev_ema["acc_top1"] / max(1e-9, random_baseline)
                    ema_str = (f"; EMA top1={ev_ema['acc_top1']:.4%} "
                               f"({ev_ema['correct']}/{ev_ema['n']}; "
                               f"{ema_lift:.1f}x)")
                print(f"  [eval] step {step}: top1={ev['acc_top1']:.4%} "
                      f"({ev['correct']}/{ev['n']}; {lift_over_random:.1f}x random){ema_str}; "
                      f"wall={eval_wall:.1f}s")
                with progress_path.open("a", encoding="utf-8") as f:
                    rec = {
                        "step": step, "kind": "eval",
                        "acc_top1": ev["acc_top1"],
                        "n_eval": ev["n"],
                        "correct": ev["correct"],
                        "lift_over_random": lift_over_random,
                        "eval_wall_s": round(eval_wall, 2),
                        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }
                    if ev_ema is not None:
                        rec["acc_top1_ema"] = ev_ema["acc_top1"]
                        rec["correct_ema"] = ev_ema["correct"]
                    f.write(json.dumps(rec) + "\n")

            # Checkpoint
            if (args.checkpoint_every_k > 0
                and step > 0 and step % args.checkpoint_every_k == 0):
                ckpt_path = out_dir / f"checkpoint_step{step}.pt"
                torch.save({
                    "step": step,
                    "readout_state": readout.state_dict(),
                    "bridge_state": bridge.state_dict(),
                    "lora_state": {
                        n: p.detach().cpu()
                        for n, p in model.named_parameters() if p.requires_grad
                    },
                    "optimizer_state": optimizer.state_dict(),
                    "config": vars(args),
                }, ckpt_path)
                print(f"  [ckpt] step {step}: saved {ckpt_path}")
                with progress_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "step": step, "kind": "checkpoint",
                        "path": str(ckpt_path),
                        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }) + "\n")

            step += 1

    # Final eval + summary
    print(f"\n[qlora_train] final eval...")
    final_eval = _eval(
        model, readout, bridge, val_rows, tokenizer, device,
        substrate_tuple, batch_size=args.batch_size,
        max_samples=None,  # full val set
        use_substrate_in_loop=args.substrate_in_loop_eval,
        substrate_soft=args.substrate_soft,
        substrate_soft_temperature=args.substrate_soft_temperature,
        target_pool_ids=target_pool_ids,
        path1a_R=path1a_R,
    )
    final_lift = final_eval["acc_top1"] / max(1e-9, random_baseline)
    final_eval_ema = None
    if ema_enabled:
        saved = _swap_to_ema()
        try:
            final_eval_ema = _eval(
                model, readout, bridge, val_rows, tokenizer, device,
                substrate_tuple, batch_size=args.batch_size,
                max_samples=None, use_substrate_in_loop=args.substrate_in_loop_eval,
                substrate_soft=args.substrate_soft,
                substrate_soft_temperature=args.substrate_soft_temperature,
                target_pool_ids=target_pool_ids, path1a_R=path1a_R,
            )
        finally:
            _restore_from_ema(saved)

    # v1b metrics: peak / stability / retention (per strategy pre-reg).
    # val_history is [(step, live_acc, ema_acc), ...]; use the BEST of live/ema
    # per checkpoint since either may carry the signal.
    def _v1b_metrics(track: str):
        if track == "live":
            vals = [(s, v) for s, v, _ in val_history]
            final_v = final_eval["acc_top1"]
        else:
            vals = [(s, v) for s, _, v in val_history if not math.isnan(v)]
            final_v = final_eval_ema["acc_top1"] if final_eval_ema else float("nan")
        if not vals:
            return None
        peak_step, peak_val = max(vals, key=lambda sv: sv[1])
        # Stability: mean val within [peak_step-25, peak_step+25]
        window_vals = [v for s, v in vals if abs(s - peak_step) <= 25]
        stability = sum(window_vals) / max(1, len(window_vals))
        retention_ratio = (final_v / peak_val) if peak_val > 1e-9 else 0.0
        return {
            "peak_val": round(peak_val, 6),
            "peak_step": peak_step,
            "stability_window_mean": round(stability, 6),
            "final_val": round(final_v, 6),
            "retention_ratio": round(retention_ratio, 6),
            "stability_frac_of_peak": round(
                stability / peak_val if peak_val > 1e-9 else 0.0, 6),
        }
    v1b_live = _v1b_metrics("live")
    v1b_ema = _v1b_metrics("ema") if ema_enabled else None
    # v1b retention HARD-PASS at >= 0.80 for any track
    v1b_retention_passes = []
    if v1b_live and v1b_live["retention_ratio"] >= 0.80:
        v1b_retention_passes.append("live")
    if v1b_ema and v1b_ema["retention_ratio"] >= 0.80:
        v1b_retention_passes.append("ema")

    total_wall = time.perf_counter() - t0

    final_loss_rolling = sum(losses_window) / max(1, len(losses_window))
    if early_baseline_loss is None:
        loss_decrease_pct = 0.0
    else:
        loss_decrease_pct = (
            (early_baseline_loss - final_loss_rolling)
            / max(1e-9, early_baseline_loss)
        )

    # Acceptance criteria per parent handoff
    pass_loss = loss_decrease_pct >= 0.30  # >=30% decrease
    pass_acc = final_eval["acc_top1"] > random_baseline  # > random
    pass_no_nan = True  # would have aborted otherwise

    if pass_loss and pass_acc and pass_no_nan:
        verdict = "PASS"
    elif (loss_decrease_pct >= 0.15 and pass_no_nan):
        verdict = "MIDDLE"
    else:
        verdict = "FAIL"

    summary = {
        "schema_version": 1,
        "verdict": verdict,
        "total_wall_s": round(total_wall, 2),
        "steps_completed": step,
        "max_steps_arg": args.max_steps,
        "early_baseline_loss": round(early_baseline_loss, 6) if early_baseline_loss else None,
        "final_rolling_loss": round(final_loss_rolling, 6),
        "loss_decrease_pct": round(loss_decrease_pct, 4),
        "final_val_acc_top1": round(final_eval["acc_top1"], 6),
        "final_val_n": final_eval["n"],
        "final_val_correct": final_eval["correct"],
        "random_baseline": random_baseline,
        "lift_over_random": round(final_lift, 2),
        "pass_loss_decrease_30pct": pass_loss,
        "pass_val_above_random": pass_acc,
        "pass_no_nan_inf": pass_no_nan,
        "dataset_dir": str(dataset_dir),
        "args": vars(args),
        "path1a_gram": path1a_gram,  # None unless --path1a-v1
        "v1prime_summary": v1prime_summary,  # None unless --path1a-v1prime
        "final_val_acc_top1_ema": (round(final_eval_ema["acc_top1"], 6)
                                    if final_eval_ema else None),
        "v1b_metrics_live": v1b_live,
        "v1b_metrics_ema": v1b_ema,
        "v1b_retention_pass_tracks": v1b_retention_passes,
        "val_history": [{"step": s, "live": v, "ema": e}
                        for s, v, e in val_history],
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print()
    print(f"[qlora_train] verdict: {verdict}")
    print(f"  loss: {early_baseline_loss} -> {final_loss_rolling:.4f} "
          f"({loss_decrease_pct:.1%} decrease)")
    print(f"  val top-1: {final_eval['acc_top1']:.4%} "
          f"({final_eval['correct']}/{final_eval['n']}; "
          f"{final_lift:.1f}x random)")
    print(f"  total wall: {total_wall/60:.1f} min")
    print(f"  summary: {summary_path}")

    if verdict == "FAIL":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
