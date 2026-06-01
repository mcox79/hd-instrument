"""PP-8 Week 2 Phase 2 prereq: toy dataset for QLoRA fine-tune.

Per parent handoff testbed_handoff_pp8_week2_feasibility_smoke_authorized
sec "Phase 2: QLoRA fine-tune smoke":
  - 5K-10K paired examples of "query + expected substrate retrieval + LLM continuation"

Toy task: associative recall via natural language.

  - Substrate N=4096, M=4096 (key_idx -> val_idx pairs from relation graph)
  - Each val_idx is pre-assigned a deterministic random Phi-3 single-token continuation
    (random_token_for_val_idx[v] = sampled from a restricted vocab subset, seeded)
  - Training example:
      text:   f"Key {key_idx:04d}: "
      target: random_token_for_val_idx[val_idx]
  - Training pipeline (substrate BYPASSED for differentiability):
      tokenize -> Phi-3 prefill -> last hidden -> readout -> SOFT TANH
        -> bridge -> 8 prefix tokens -> Phi-3 + prefix -> 1 token logits
        -> CE vs target_token
  - Validation pipeline (substrate IN THE LOOP):
      ... -> readout -> SIGN -> Path D depth=5 -> codeword
        -> bridge -> 8 prefix tokens -> Phi-3 + prefix -> argmax token
      Measure top-1 accuracy on held-out keys.

This is the "Q-Former + readout teaches Phi-3 to look up arbitrary
non-prior-knowledge facts via the substrate" test. The substrate is
load-bearing because random_token_for_val_idx is not learnable by Phi-3
alone (no semantic prior connecting "Key 0042" to its random target token).

Split: 80% train / 20% val by SHUFFLED INDEX (held-out KEYS, not held-out
key->value associations -- the relation graph is fixed, but training only
sees 80% of keys during fit; val measures retrieval on unseen keys).

Output: train.jsonl, val.jsonl, manifest.json with substrate_seed +
val_to_token_map.

Run:
  python -m testbed.llm_integration.phase2_toy_dataset_gen \
    --n-train 4000 --n-val 1000 --substrate-seed 7 \
    --out-dir data/testbed_pp8_week2/dataset_v1
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

import torch

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments._multi_hop_mechanisms import build_shared  # noqa: E402


_N_SUBSTRATE = 4096
_M_SUBSTRATE = 4096
_PHI3_MODEL = "microsoft/Phi-3-mini-4k-instruct"
# Restricted vocab subset: alphabetic single-token IDs in the Phi-3 vocab.
# Chosen to keep target tokens "natural" (not bytes/markers/control tokens)
# AND to put a sharp ceiling on random-baseline accuracy. With 1024 candidates,
# random = 1/1024 = 0.098%, so any val-eval accuracy >>0.1% is signal.
_TARGET_VOCAB_POOL_SIZE = 1024


def _build_target_vocab_pool(tokenizer, pool_size: int, seed: int) -> list[int]:
    """Pick a deterministic set of `pool_size` token IDs to use as targets.

    Selection: token IDs whose decoded form is a 2-4 letter ASCII alphabetic
    string (single-token "words" the model can comfortably output). Excludes
    special / control / byte / numeric tokens.
    """
    vocab = tokenizer.get_vocab()
    rng = random.Random(seed)
    candidates: list[int] = []
    for tok_str, tok_id in vocab.items():
        # Decode token via tokenizer to get the actual string
        try:
            decoded = tokenizer.decode([tok_id]).strip()
        except Exception:
            continue
        # 2-4 lowercase or capitalized letters only
        if not (2 <= len(decoded) <= 4):
            continue
        if not decoded.isalpha():
            continue
        if not decoded.isascii():
            continue
        candidates.append(tok_id)
    rng.shuffle(candidates)
    if len(candidates) < pool_size:
        raise RuntimeError(
            f"Only {len(candidates)} candidate tokens in vocab; "
            f"requested {pool_size}. Lower --target-vocab-pool-size.")
    return sorted(candidates[:pool_size])


def _build_val_to_token_map(
    val_idx_values: list[int], pool: list[int], seed: int,
) -> dict[int, int]:
    """Deterministic map val_idx -> target_token_id, seeded.

    val_idx values are indices into the codebook (range [0, codebook_size)),
    NOT positions in [0, M). Build the map over the distinct val_idx values
    actually used in the relation graph.

    Each distinct val_idx gets ONE token_id from `pool` (with replacement,
    so multiple val_idxs may share a target token; that's expected -- the
    bridge learns to encode val-of-different-key + same-target as same prefix).

    Iterating in sorted order makes the map deterministic across runs at
    fixed substrate_seed + val_to_token_seed.
    """
    rng = random.Random(seed)
    distinct = sorted(set(int(v) for v in val_idx_values))
    return {v: rng.choice(pool) for v in distinct}


def _make_query_text(key_idx: int) -> str:
    """Tokenizable query template; Phi-3 will prefill on this."""
    return f"Key {key_idx:04d}: "


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PP-8 Week 2 Phase 2 toy dataset generator")
    parser.add_argument("--n-train", type=int, default=4000)
    parser.add_argument("--n-val", type=int, default=1000)
    parser.add_argument("--substrate-seed", type=int, default=7,
                        help="Substrate build seed (locks codebook + relation)")
    parser.add_argument("--vocab-pool-seed", type=int, default=11,
                        help="Seed for target-vocab pool selection")
    parser.add_argument("--val-to-token-seed", type=int, default=13,
                        help="Seed for val_idx -> target_token map")
    parser.add_argument("--target-vocab-pool-size", type=int,
                        default=_TARGET_VOCAB_POOL_SIZE)
    parser.add_argument("--out-dir", required=True,
                        help="Output directory for train.jsonl/val.jsonl/manifest.json")
    parser.add_argument("--no-holdout", action="store_true",
                        help="Path 1c sanity-check mode: val SHARES keys with "
                             "train (sampled with replacement from same pool). "
                             "Tests whether the architecture can learn ANY val "
                             "signal when held-out generalization isn't required. "
                             "Default off: val keys are held out from training.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[dataset_gen] building substrate (N={_N_SUBSTRATE}, M={_M_SUBSTRATE}, "
          f"seed={args.substrate_seed}) on CPU...")
    device = torch.device("cpu")
    codebook, W, key_idx_t, val_idx_t, relation = build_shared(
        _N_SUBSTRATE, _M_SUBSTRATE, args.substrate_seed, device,
    )
    print(f"[dataset_gen] substrate built: codebook shape {tuple(codebook.shape)}, "
          f"M-pairs {key_idx_t.numel()}")

    # The relation graph contains M closed-loop facts; key_idx_t and val_idx_t
    # are tensors of length M with the actual (k, v) pair indices.
    pairs = list(zip(
        key_idx_t.cpu().tolist(), val_idx_t.cpu().tolist(),
    ))
    M = len(pairs)
    print(f"[dataset_gen] {M} (key, val) pairs from relation graph")

    print(f"[dataset_gen] loading Phi-3 tokenizer ({_PHI3_MODEL})...")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        _PHI3_MODEL, trust_remote_code=False)

    print(f"[dataset_gen] building target-vocab pool "
          f"(size={args.target_vocab_pool_size}, seed={args.vocab_pool_seed})...")
    pool = _build_target_vocab_pool(
        tokenizer, args.target_vocab_pool_size, args.vocab_pool_seed)
    print(f"[dataset_gen] target-vocab pool: {len(pool)} tokens")
    print(f"[dataset_gen] sample tokens: "
          f"{[tokenizer.decode([t]).strip() for t in pool[:8]]}")

    print(f"[dataset_gen] mapping val_idx -> target_token (seed={args.val_to_token_seed})...")
    val_to_token = _build_val_to_token_map(
        val_idx_t.cpu().tolist(), pool, args.val_to_token_seed)
    # Stats: distribution of token assignments
    from collections import Counter
    tok_counts = Counter(val_to_token.values())
    print(f"[dataset_gen] target-token assignment: "
          f"{len(tok_counts)} distinct tokens used out of pool {len(pool)}; "
          f"max-count={max(tok_counts.values())} min-count={min(tok_counts.values())}")

    # ----- Split pairs into train (80%) and val (20%) by KEY -----
    rng = random.Random(args.substrate_seed + 1000)
    indices = list(range(M))
    rng.shuffle(indices)
    n_total = args.n_train + args.n_val
    if args.no_holdout:
        # Path 1c sanity mode: val SHARES keys with train (sampled with
        # replacement from the same pool). Tests architecture-can-learn-val
        # without requiring held-out generalization. Each val example uses
        # an arbitrary pair from the full M=4096 pool; same pair may also
        # appear in train.
        print(f"[dataset_gen] --no-holdout: val keys SHARE pool with train "
              f"(architecture sanity check; val NOT held out)")
        train_indices = [rng.choice(indices) for _ in range(args.n_train)]
        val_indices = [rng.choice(indices) for _ in range(args.n_val)]
    elif n_total > M:
        # We need more examples than we have unique pairs; sample with replacement
        # for train, hold out distinct keys for val.
        print(f"[dataset_gen] n_train + n_val = {n_total} > M = {M}; "
              f"train will sample with replacement from non-val keys.")
        val_set_size = args.n_val
        val_indices = indices[:val_set_size]
        train_indices_source = indices[val_set_size:]
        # Sample with replacement to reach n_train
        train_indices = [rng.choice(train_indices_source) for _ in range(args.n_train)]
    else:
        val_indices = indices[:args.n_val]
        train_indices = indices[args.n_val:args.n_val + args.n_train]

    split_desc = "val SHARES keys with train" if args.no_holdout else "val held-out keys"
    print(f"[dataset_gen] split: {len(train_indices)} train / "
          f"{len(val_indices)} val ({split_desc})")

    # ----- Write train.jsonl + val.jsonl -----
    def _write_split(split: str, indices: list[int], path: Path):
        with path.open("w", encoding="utf-8") as f:
            for idx in indices:
                k, v = pairs[idx]
                target_tok = val_to_token[v]
                record = {
                    "key_idx": int(k),
                    "val_idx": int(v),
                    "target_token_id": int(target_tok),
                    "target_token_str": tokenizer.decode([target_tok]).strip(),
                    "query_text": _make_query_text(int(k)),
                }
                f.write(json.dumps(record) + "\n")
        print(f"[dataset_gen] wrote {len(indices)} {split} examples -> {path}")

    train_path = out_dir / "train.jsonl"
    val_path = out_dir / "val.jsonl"
    _write_split("train", train_indices, train_path)
    _write_split("val", val_indices, val_path)

    # ----- Manifest -----
    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "n_substrate": _N_SUBSTRATE,
        "m_substrate": _M_SUBSTRATE,
        "n_train": len(train_indices),
        "n_val": len(val_indices),
        "substrate_seed": args.substrate_seed,
        "vocab_pool_seed": args.vocab_pool_seed,
        "val_to_token_seed": args.val_to_token_seed,
        "target_vocab_pool_size": args.target_vocab_pool_size,
        "phi3_model": _PHI3_MODEL,
        "random_baseline_top1": round(1.0 / args.target_vocab_pool_size, 6),
        "ceiling_top1": 1.0,
        # Save the full val_to_token map so the trainer can use it without re-deriving.
        "val_to_token_map": {str(k): int(v) for k, v in val_to_token.items()},
        # Save the pool itself for completeness
        "target_vocab_pool_ids": pool,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[dataset_gen] wrote manifest -> {manifest_path}")
    print()
    print(f"  Random-baseline top-1 accuracy: "
          f"{manifest['random_baseline_top1']:.4%}")
    print(f"  Target ceiling (if substrate retrieval is perfect): 100%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
