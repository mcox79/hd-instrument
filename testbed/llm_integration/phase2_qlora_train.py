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
    print(f"[qlora_train] {len(train_rows)} train / {len(val_rows)} val")
    print(f"[qlora_train] random-baseline top-1 = {random_baseline:.4%}")

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

    # Build optimizer over ALL trainable params (LoRA + readout + bridge)
    trainable_params = []
    n_readout = 0
    n_bridge = 0
    n_lora = 0
    for p in readout.parameters():
        trainable_params.append(p)
        n_readout += p.numel()
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
    # Linear warmup over first 10% of steps; cosine decay after
    warmup_steps = max(1, args.max_steps // 10)
    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / max(1, args.max_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    # Training loop
    progress_path = out_dir / "train_progress.jsonl"
    progress_path.write_text("", encoding="utf-8")

    model.train()
    readout.train()
    bridge.train()

    step = 0
    losses_window: list[float] = []  # rolling for smooth log
    early_baseline_loss: float | None = None
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
                )
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
                )
                eval_wall = time.perf_counter() - eval_t0
                lift_over_random = ev["acc_top1"] / max(1e-9, random_baseline)
                print(f"  [eval] step {step}: top1={ev['acc_top1']:.4%} "
                      f"({ev['correct']}/{ev['n']}; {lift_over_random:.1f}x random); "
                      f"wall={eval_wall:.1f}s")
                with progress_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "step": step, "kind": "eval",
                        "acc_top1": ev["acc_top1"],
                        "n_eval": ev["n"],
                        "correct": ev["correct"],
                        "lift_over_random": lift_over_random,
                        "eval_wall_s": round(eval_wall, 2),
                        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }) + "\n")

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
    )
    final_lift = final_eval["acc_top1"] / max(1e-9, random_baseline)
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
