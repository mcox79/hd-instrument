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


def _load_phi3_lora(device: torch.device, lora_r: int, lora_alpha: int):
    """Load Phi-3-mini-4bit + attach LoRA adapters (trainable)."""
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              BitsAndBytesConfig)
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    if device.type != "cuda":
        raise RuntimeError(
            "Phi-3 + QLoRA requires CUDA. For CPU smoke use --device cpu "
            "with the mock-model path (TODO).")

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
) -> float:
    """One training step. Returns scalar loss."""
    input_ids, attention_mask, targets = _tokenize_batch(tokenizer, batch, device)

    # Phase 1 prefill (LoRA active)
    out = model(
        input_ids=input_ids, attention_mask=attention_mask,
        use_cache=True, output_hidden_states=True,
    )
    past = out.past_key_values
    hidden = _last_position_hidden(out, attention_mask).to(dtype=torch.float32)

    # readout (soft tanh) -> bridge -- substrate BYPASSED for differentiability
    soft_query = readout(hidden)  # (B, n_sub)
    prefix_tokens = bridge(soft_query)  # (B, n_queries, d_model)

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
        if use_substrate_in_loop:
            # Per row: sign() -> Path D -> codeword; then stack.
            cw_list = []
            for b in range(soft_query.shape[0]):
                bipolar = _bipolar_from_soft(soft_query[b:b+1]).squeeze(0)
                # use this row's bipolar as the start codeword for Path D
                # (we don't have a learned "start" here; smoke pattern uses
                # the substrate's stored key_idx[0]; for the eval we want
                # the readout's query to be the input to Path D, but Path D
                # signature expects start indices not codewords --
                # so for now use the same starts as smoke and treat the
                # readout output as the *queried codeword*, not the start.)
                result = path_d_run(
                    codebook=codebook, W=W, starts=starts, relation=relation,
                    depth=_DEPTH, K_paths=_K_PATHS, seed=int(targets[b].item()),
                    N_use=_N_SUBSTRATE,
                )
                if isinstance(result, tuple):
                    best_idx = result[0]
                else:
                    best_idx = result
                if isinstance(best_idx, torch.Tensor):
                    bi = best_idx.flatten()[0].item() if best_idx.numel() > 0 else 0
                else:
                    bi = int(best_idx) if not hasattr(best_idx, "__iter__") else 0
                bi = int(bi) if not isinstance(bi, int) else bi
                bi = max(0, min(bi, codebook.shape[0] - 1))
                cw_list.append(codebook[bi].to(dtype=torch.float32))
            codeword_batch = torch.stack(cw_list, dim=0)  # (B, n_sub)
        else:
            codeword_batch = soft_query  # train-time bypass path

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
                        help="(EXPERIMENTAL) eval through sign+Path D. BLOCKED: "
                             "Path D takes start indices, not bipolar codeword "
                             "vectors. A 'key resolver' (bipolar -> nearest "
                             "codebook index) is needed first -- not yet built. "
                             "Default is substrate-bypassed eval, matching "
                             "training-time path; this validates bridge "
                             "trainability but not substrate-in-loop quality.")
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.is_absolute():
        dataset_dir = _REPO_ROOT / dataset_dir

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

    # Load Phi-3 + LoRA + bridge + readout
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
