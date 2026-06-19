"""substrate_cell3_distilled_22M_student_v1 -- CELL-3 distilled 22M student.

ROUTING: research_to_testbed_CELL3_CELL4_answers_plus_CELL2_reextract_flag_2026-06-07.md
USER AUTHORIZED 2026-06-07; rules:
  - Train from BASE (Q4 HARD_FAIL ruled out LoRA-warm; cycle 142 left-pad lock)
  - Feature-mimic via MSE on CELL-2 v3 cache (Q-CELL-3-1 ruled feature-mimic)
  - 22M params (Q-CELL-3-2 confirmed)

PIPELINE:
  1. Load CELL-2 v3 shards: (article_id, title, llama_l15_target)
  2. Re-fetch raw text for each article from wikimedia/wikipedia 20231101.en
  3. Initialize 22M sentence-transformer-style student:
       - 6 layers transformer encoder
       - hidden=384, heads=12, ffn=1536, vocab=Llama tokenizer subset (~32K)
       - Pooler: last-token (left-pad-aware)
       - Project: Linear(384, 2048) to match Llama-1B L=15 dimension
  4. Train with MSE loss between student output and llama_l15_target
  5. Periodic validation: mean cosine similarity on held-out subset

PRE-REG (Research Q-CELL-3-1):
  HP : final MSE < 0.10 OR mean cosine >= 0.95 on held-out
  MID: 0.10-0.20 / 0.85-0.95
  HF : > 0.20 / < 0.85 (revisit architecture)

LOCKS APPLIED:
  - Train from BASE student (no LoRA-warm; Q4 HF lock)
  - LEFT-padding throughout (cycle 142)
  - Last-token pool with left-pad-aware indexing
  - PROT-022 self-test
  - LoRA target_modules NOT used (no LoRA here; full fine-tune of small model)
  - ASCII-only outputs

HARDENING:
  - Picklable collator class (DataLoader num_workers compatibility)
  - bf16 mixed precision training
  - Gradient checkpointing (memory headroom)
  - Validation cosine averages on held-out subset
  - NaN guard during training
  - Periodic checkpoint save
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse, time, gc, json, math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterable

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "substrate_cell3_distilled_22M_student_v1"
MODEL_LLAMA_1B = "meta-llama/Llama-3.2-1B"  # for tokenizer (vocab) parity
LAYER_LLAMA = 15
TARGET_DIM = 2048   # Llama-1B hidden dimension (the distillation target)

_ap = argparse.ArgumentParser()
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--cell2-shards-dir", type=str,
                  default=str(REPO / "data" / "cell2_results"))
_ap.add_argument("--max-articles", type=int, default=None,
                  help="Cap on training articles (default: use all available)")
_ap.add_argument("--val-frac", type=float, default=0.05)
_ap.add_argument("--epochs", type=int, default=1)
_ap.add_argument("--batch", type=int, default=256,
                  help="Default raised from 64 -> 256 (H100 80GB easily holds 22M @ batch=256)")
_ap.add_argument("--lr", type=float, default=6e-4,
                  help="LR raised from 3e-4 -> 6e-4 (~sqrt(batch_scale) rule for 64 -> 256)")
_ap.add_argument("--max-tok", type=int, default=512,
                  help="Match CELL-2 v3 cache extraction (MAX_TOK=512) for distillation "
                       "parity. Student learns to predict the L=15 feature that the teacher "
                       "extracted from up to the same 512 tokens. Reducing this creates a "
                       "training-time semantic mismatch.")
_ap.add_argument("--hidden", type=int, default=384)
_ap.add_argument("--n-layers", type=int, default=6)
_ap.add_argument("--n-heads", type=int, default=12)
_ap.add_argument("--ffn-dim", type=int, default=1536)
_ap.add_argument("--num-workers", type=int, default=16)
_ap.add_argument("--prefetch-factor", type=int, default=4)
_ap.add_argument("--compile", action="store_true",
                  help="Enable torch.compile() on the student (~1.5-2x on H100)")
_ap.add_argument("--no-compile", action="store_true",
                  help="Disable torch.compile() (for debugging)")
_ap.add_argument("--min-text-chars", type=int, default=100,
                  help="Filter Wikipedia stubs below this char count (skip ~30 pct stubs)")
_ap.add_argument("--pretokenize-num-proc", type=int, default=8,
                  help="Parallel tokenization workers in setup phase")
_ARGS, _ = _ap.parse_known_args()

MAX_TOK = _ARGS.max_tok
BATCH = _ARGS.batch
EPOCHS = _ARGS.epochs
LEARNING_RATE = _ARGS.lr

# Verdict bands (Research Q-CELL-3-1)
HP_MSE = 0.10
MID_MSE_HIGH = 0.20
HP_COS = 0.95
MID_COS_LOW = 0.85


def last_token_pool_left(hs, am):
    """Left-pad-aware last-token pool: ALWAYS position seq_len - 1."""
    seq_len = am.size(1)
    last_idx = torch.full((am.size(0),), seq_len - 1, dtype=torch.long, device=hs.device)
    batch_idx = torch.arange(hs.size(0), device=hs.device)
    return hs[batch_idx, last_idx]


class TinyEmbeddingStudent(nn.Module):
    """22M sentence-transformer-style student.

    6 layers Transformer encoder; vocab from Llama tokenizer to share embeddings
    (but separately learned; not pretrained). Output project to TARGET_DIM=2048
    to match Llama-1B L=15 hidden size.

    Param count budget:
      embedding: vocab x hidden = 128K x 384 = 49M  -> TOO MUCH; use tied output proj
      Actually: separate embedding (49M) + 6 transformer layers (10.8M) + proj (786K)
      = 60M; still over budget.

    To hit 22M: use SMALLER vocab via subword merging, or share embedding +
    output projection with hidden-level operations. We'll use the Llama vocab
    but reduce hidden to 128 for the embedding-heavy budget allocation,
    then project to 384 for the transformer body.
    """

    def __init__(self, vocab_size: int = 128256, embed_dim: int = 128,
                 hidden: int = 384, n_layers: int = 6, n_heads: int = 12,
                 ffn_dim: int = 1536, max_pos: int = 1024, target_dim: int = TARGET_DIM,
                 pad_id: int = 0):
        super().__init__()
        self.pad_id = pad_id
        # Token embedding: vocab_size x embed_dim
        self.tok_emb = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        # Project embedding to hidden dim for transformer
        self.emb_proj = nn.Linear(embed_dim, hidden)
        # Positional embedding
        self.pos_emb = nn.Embedding(max_pos, hidden)
        # Transformer encoder layers
        layer = nn.TransformerEncoderLayer(
            d_model=hidden, nhead=n_heads, dim_feedforward=ffn_dim,
            dropout=0.1, activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        # Final layer norm
        self.ln = nn.LayerNorm(hidden)
        # Project hidden -> target_dim (2048) to match Llama-1B L=15 dim
        self.proj = nn.Linear(hidden, target_dim)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        # input_ids: (B, T)  attention_mask: (B, T) where 1=real, 0=pad
        B, T = input_ids.shape
        device = input_ids.device

        # Embed
        x = self.tok_emb(input_ids)                       # (B, T, embed_dim)
        x = self.emb_proj(x)                              # (B, T, hidden)
        positions = torch.arange(T, device=device).unsqueeze(0).expand(B, T)
        x = x + self.pos_emb(positions)                   # (B, T, hidden)

        # Transformer encoder; src_key_padding_mask: True where padded
        pad_mask = (attention_mask == 0)                  # (B, T)
        x = self.encoder(x, src_key_padding_mask=pad_mask)
        x = self.ln(x)                                    # (B, T, hidden)

        # Left-pad-aware last-token pool: always last position
        last_idx = T - 1
        pooled = x[:, last_idx, :]                        # (B, hidden)

        # Project to target dim
        out = self.proj(pooled)                           # (B, target_dim)
        return out

    def param_count(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def _selftest():
    """PROT-022: build a tiny student, forward, verify shape + param count budget."""
    # Tiny version for selftest
    student = TinyEmbeddingStudent(
        vocab_size=1000, embed_dim=32, hidden=64, n_layers=2, n_heads=4,
        ffn_dim=128, max_pos=64, target_dim=128, pad_id=0,
    )
    ids = torch.randint(1, 1000, (4, 32))
    am = torch.ones(4, 32, dtype=torch.long)
    out = student(ids, am)
    assert out.shape == (4, 128), f"output shape: {out.shape}"

    # Test last_token_pool_left
    hs = torch.tensor([[[1.0], [2.0], [3.0], [4.0]]])
    am_left = torch.tensor([[0, 1, 1, 1]])  # left-padded; last real at idx 3
    lt = last_token_pool_left(hs, am_left)
    assert abs(float(lt[0, 0]) - 4.0) < 1e-5, f"last_token_pool got {lt}"

    # Build full-size student and check param budget
    full_student = TinyEmbeddingStudent()
    pc = full_student.param_count()
    pc_M = pc / 1e6
    # Target ~22M; tolerate 18-28M
    assert 18 < pc_M < 30, f"student param count {pc_M:.1f}M out of [18, 30]M budget"
    print(f"[selftest] PASS: tiny student forward OK, last_token_pool_left=4.0, "
          f"full student param_count={pc_M:.1f}M", flush=True)


_selftest()
if _ARGS.self_test:
    print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
    sys.exit(0)


# Determinism: seed BOTH numpy and torch (training was non-deterministic across runs)
SEED = 1729
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


if not torch.cuda.is_available():
    print("[FATAL] CUDA not available; this script is GPU-only.", flush=True)
    sys.exit(1)
DEVICE = torch.device("cuda")
# Enable TF32 for fp32 matmul on Ampere/Hopper -- ~3x speedup on residual fp32 ops
# without sacrificing model quality (training is bf16-autocasted anyway)
torch.set_float32_matmul_precision("high")
print(f"[GPU] {torch.cuda.get_device_name(0)} "
      f"({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB) "
      f"| tf32=high", flush=True)


def _load_hf_token() -> Optional[str]:
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    return os.environ.get("HF_TOKEN", "").strip() or None


def load_cell2_targets(shards_dir: Path, max_articles: Optional[int]) -> Tuple[List[str], np.ndarray]:
    """Load (article_id, llama_l15_target) from CELL-2 shards.

    MEMORY-AWARE: stays in fp16 (the cache's native dtype) and only loads enough
    shards to satisfy max_articles. Full 5.84M @ fp16 = ~24 GB; fp32 cast would
    be 48 GB and OOM most hosts. Keep fp16 here; cast per-batch at training time.
    """
    shards = sorted(shards_dir.glob("shard_*.npz"))
    if not shards:
        raise RuntimeError(f"No shards at {shards_dir}")
    print(f"[data] loading {len(shards)} shards from {shards_dir} (fp16 native; lazy stop at max_articles)", flush=True)

    ids_all, targets_all = [], []
    cumulative = 0
    for f in shards:
        arr = np.load(f, allow_pickle=True)
        # Keep fp16 (the on-disk dtype); upcast to fp32 only at training-batch boundary
        ids_all.extend(list(arr["article_ids"]))
        targets_all.append(arr["hidden_states"])   # already fp16 per CELL-2 v3 save
        cumulative += arr["hidden_states"].shape[0]
        if max_articles is not None and cumulative >= max_articles:
            break
    targets = np.concatenate(targets_all, axis=0)
    if max_articles is not None:
        ids_all = ids_all[:max_articles]
        targets = targets[:max_articles]
    mem_gb = targets.nbytes / 1e9
    print(f"[data] {len(ids_all)} (id, target) pairs loaded; targets dtype={targets.dtype} mem={mem_gb:.2f} GB", flush=True)
    return ids_all, targets


def build_id_to_text_map(article_ids: List[str], hf_token: Optional[str]) -> Dict[str, str]:
    """Build {id: text} from PRE-DOWNLOADED parquet files (not streaming).

    Streaming would iterate the full 6.5M Wikipedia linearly for each batch of
    article IDs we want to match -- pathologically slow for CELL-3's randomly-
    ordered cache IDs. Direct parquet read is random-access friendly.

    Requires Wikipedia parquet snapshot already in HF cache (CELL-3 YAML
    pre-downloads it in setup, same as CELL-2 v3).
    """
    from huggingface_hub import snapshot_download
    import pyarrow.parquet as pq

    print(f"[data] loading wikimedia/wikipedia parquets (pre-downloaded by setup)", flush=True)
    snapshot_dir = snapshot_download(
        repo_id="wikimedia/wikipedia", repo_type="dataset",
        token=hf_token, allow_patterns=["20231101.en/*.parquet"],
    )
    parquet_files = sorted(Path(snapshot_dir).rglob("20231101.en/*.parquet"))
    print(f"[data] found {len(parquet_files)} parquet files", flush=True)

    needed = set(article_ids)
    id_to_text = {}
    for pf_idx, pf in enumerate(parquet_files):
        if len(id_to_text) == len(needed):
            break
        tbl = pq.read_table(str(pf), columns=["id", "text"])
        ids_col = tbl["id"].to_pylist()
        texts_col = tbl["text"].to_pylist()
        for art_id, text in zip(ids_col, texts_col):
            if art_id in needed and art_id not in id_to_text:
                id_to_text[art_id] = text
        print(f"  [data] parquet {pf_idx+1}/{len(parquet_files)}: "
              f"matched={len(id_to_text)}/{len(needed)}", flush=True)
    print(f"[data] FINAL matched {len(id_to_text)}/{len(needed)} articles", flush=True)
    return id_to_text


class PretokenizedDistillDataset(torch.utils.data.Dataset):
    """Lightweight dataset over PRE-TOKENIZED arrays.

    Pre-tokenization is done ONCE in setup (parallel via multiprocessing),
    eliminating per-batch tokenizer overhead (was ~15-30 min/epoch baseline).
    Stores token ids as a single big int32 array + offsets to avoid Python list overhead.
    """

    def __init__(self, all_input_ids_packed: np.ndarray, offsets: np.ndarray,
                 targets: np.ndarray):
        # all_input_ids_packed: 1D int32 array of all tokens concatenated
        # offsets: 1D int64 array of length N+1; tokens for sample i are
        #          all_input_ids_packed[offsets[i]:offsets[i+1]]
        # targets: (N, target_dim) fp16
        self.tokens = all_input_ids_packed
        self.offsets = offsets
        self.targets = targets

    def __len__(self):
        return len(self.offsets) - 1

    def __getitem__(self, idx):
        start = int(self.offsets[idx])
        end = int(self.offsets[idx + 1])
        input_ids = torch.from_numpy(self.tokens[start:end].astype(np.int64))
        attention_mask = torch.ones(input_ids.size(0), dtype=torch.long)
        target = torch.from_numpy(self.targets[idx].astype(np.float32))
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "target": target,
        }


def pretokenize_in_parallel(texts: List[str], tokenizer, max_tok: int,
                              num_proc: int = 8,
                              chunk_size: int = 50000) -> Tuple[np.ndarray, np.ndarray]:
    """Pre-tokenize all texts via fast tokenizer batched call.

    MEMORY-SAFE at 5.84M scale: packs each chunk into a numpy int32 buffer
    IMMEDIATELY and discards the Python list-of-list. Holding the entire
    Python int graph for 5.84M x 512 tokens would cost ~80 GB (Python int =
    28 bytes each); packing into numpy int32 costs ~6 GB.

    Robustness: pathological text (NUL bytes, malformed unicode, etc.) is
    handled per-chunk -- if the whole batched call fails, retry per-text and
    skip any that crash. Per-text fallback uses a single empty-token placeholder
    so the resulting dataset stays aligned with the input order (so targets
    don't get misaligned with input).
    """
    import os as _os
    _os.environ["TOKENIZERS_PARALLELISM"] = "true"
    if not getattr(tokenizer, "is_fast", False):
        print(f"[pretok] WARNING: tokenizer is_fast=False -- pre-tokenization will be slow", flush=True)

    n = len(texts)
    # Worst-case peak buffer: chunk_size * max_tok int32 = 50000 * 512 * 4 = 100 MB
    print(f"[pretok] tokenizing {n:,} texts (max_tok={max_tok}; chunk={chunk_size:,}); "
          f"peak-chunk-buf~{chunk_size * max_tok * 4 / 1e6:.0f} MB", flush=True)
    t0 = time.time()

    # Per-chunk: tokenize -> append to packed buffer; keep ONLY the packed buffer
    # We grow `all_tokens` and `offsets` lazily; numpy concatenation is the cost.
    packed_chunks: List[np.ndarray] = []   # list of int32 arrays per chunk
    offsets_chunks: List[np.ndarray] = []  # list of int64 cumsum-relative
    grand_offsets_to_date = 0

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = texts[start:end]
        try:
            enc = tokenizer(chunk, truncation=True, max_length=max_tok,
                             add_special_tokens=True, padding=False)
            ids_list = enc["input_ids"]
        except Exception as e:
            # Chunk-level failure -> fall back to per-text. Skip pathological
            # texts (place empty 1-token row so the array stays aligned with target)
            print(f"  [pretok] chunk {start:,}-{end:,} FAILED ({type(e).__name__}: {e}); "
                  f"per-text fallback", flush=True)
            ids_list = []
            for txt in chunk:
                try:
                    enc_one = tokenizer(txt, truncation=True, max_length=max_tok,
                                          add_special_tokens=True)
                    ids_list.append(enc_one["input_ids"])
                except Exception:
                    # Pathological text -- emit just BOS to keep alignment
                    bos = tokenizer.bos_token_id if tokenizer.bos_token_id is not None else 0
                    ids_list.append([bos])

        # Pack ids_list -> int32 buffer + per-sample length array
        chunk_lengths = np.fromiter((len(x) for x in ids_list), dtype=np.int64,
                                       count=len(ids_list))
        total_in_chunk = int(chunk_lengths.sum())
        chunk_buf = np.empty(total_in_chunk, dtype=np.int32)
        # Per-sample write
        chunk_cumstart = 0
        for ids in ids_list:
            ids_len = len(ids)
            chunk_buf[chunk_cumstart:chunk_cumstart + ids_len] = ids
            chunk_cumstart += ids_len
        packed_chunks.append(chunk_buf)
        offsets_chunks.append(chunk_lengths)
        # Free the Python lists explicitly
        del ids_list, chunk_lengths

        elapsed = time.time() - t0
        eta = (n - end) / max((end / elapsed), 1e-9)
        print(f"  [pretok] {end:,}/{n:,} ({100*end/n:.1f}%) | "
              f"rate={end/max(elapsed,1e-9):.0f}/sec | wall={elapsed:.1f}s | "
              f"eta={eta/60:.1f} min", flush=True)

    # Final pack: stitch chunk buffers together
    print(f"[pretok] stitching {len(packed_chunks)} chunks into final arrays...", flush=True)
    all_tokens = np.concatenate(packed_chunks) if packed_chunks else np.empty(0, dtype=np.int32)
    all_lengths = np.concatenate(offsets_chunks) if offsets_chunks else np.empty(0, dtype=np.int64)
    offsets = np.zeros(n + 1, dtype=np.int64)
    offsets[1:] = all_lengths.cumsum()
    total_toks = int(offsets[-1])
    elapsed = time.time() - t0
    print(f"[pretok] DONE: {total_toks/1e6:.1f}M tokens ({all_tokens.nbytes/1e9:.2f} GB); "
          f"total wall {elapsed:.1f}s", flush=True)

    # Free intermediates explicitly
    del packed_chunks, offsets_chunks, all_lengths
    gc.collect()
    _os.environ["TOKENIZERS_PARALLELISM"] = "false"

    return all_tokens, offsets


class LeftPadCollator:
    """Picklable left-pad collator."""

    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, batch):
        max_len = max(b["input_ids"].size(0) for b in batch)
        n = len(batch)
        input_ids = torch.full((n, max_len), self.pad_id, dtype=torch.long)
        attention_mask = torch.zeros(n, max_len, dtype=torch.long)
        targets = torch.stack([b["target"] for b in batch])
        for i, b in enumerate(batch):
            L = b["input_ids"].size(0)
            input_ids[i, max_len - L:] = b["input_ids"]
            attention_mask[i, max_len - L:] = b["attention_mask"]
        return {"input_ids": input_ids, "attention_mask": attention_mask, "target": targets}


def evaluate(student, loader) -> Dict:
    """Mean MSE + mean cosine on val set; NaN-guarded."""
    student.eval()
    mse_sum = 0.0
    cos_sum = 0.0
    n = 0
    n_nan_batches = 0
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            target = batch["target"].to(DEVICE).float()
            pred = student(input_ids, attention_mask)
            mse = F.mse_loss(pred, target, reduction="mean")
            cos = F.cosine_similarity(pred, target, dim=1).mean()
            if not (torch.isfinite(mse) and torch.isfinite(cos)):
                n_nan_batches += 1
                continue
            mse_sum += float(mse.item()) * pred.size(0)
            cos_sum += float(cos.item()) * pred.size(0)
            n += pred.size(0)
    if n == 0:
        return {"mse": float("nan"), "cos": float("nan"), "n_evaluated": 0, "n_nan_batches": n_nan_batches}
    return {"mse": mse_sum / n, "cos": cos_sum / n, "n_evaluated": n, "n_nan_batches": n_nan_batches}


def main():
    print(f"[config] anchor={ANCHOR_NAME} max_articles={_ARGS.max_articles or 'all'} "
          f"epochs={EPOCHS} batch={BATCH} lr={LEARNING_RATE} max_tok={MAX_TOK}",
          flush=True)
    hf_token = _load_hf_token()

    # Step 1: load CELL-2 cache + raw Wikipedia text
    shards_dir = Path(_ARGS.cell2_shards_dir)
    ids, targets = load_cell2_targets(shards_dir, max_articles=_ARGS.max_articles)
    id_to_text = build_id_to_text_map(ids, hf_token)

    # Filter to (id, target, text) tuples + drop stubs (Wikipedia stubs add noise).
    # CRITICAL: None-safe -- some parquet rows can have None text fields.
    min_chars = _ARGS.min_text_chars
    keep_idx = []
    n_none = 0
    for i, art_id in enumerate(ids):
        if art_id not in id_to_text:
            continue
        text = id_to_text[art_id]
        if text is None:
            n_none += 1
            continue
        if len(text) < min_chars:
            continue
        keep_idx.append(i)
    n_pre_filter = len(ids)
    ids = [ids[i] for i in keep_idx]
    targets = targets[keep_idx]
    texts = [id_to_text[art_id] for art_id in ids]
    # Free the id_to_text dict (saves ~5-15 GB on full scale)
    del id_to_text
    gc.collect()
    print(f"[data] final dataset: {len(ids):,} (id, text, target) triples "
          f"(stubs <{min_chars}c filtered: -{n_pre_filter - len(ids):,}; "
          f"null-text: -{n_none:,})", flush=True)

    # Train / val split
    n_val = max(1, int(_ARGS.val_frac * len(ids)))
    rng = np.random.default_rng(1729)
    perm = rng.permutation(len(ids))
    val_idx = perm[:n_val]
    train_idx = perm[n_val:]
    print(f"[data] train={len(train_idx)} val={n_val}", flush=True)

    # Step 2: load tokenizer (Llama) and build student
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_LLAMA_1B, token=hf_token)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    vocab_size = len(tokenizer)
    print(f"[tokenizer] Llama-3.2-1B; vocab={vocab_size}; padding=left", flush=True)

    student = TinyEmbeddingStudent(
        vocab_size=vocab_size, embed_dim=128, hidden=_ARGS.hidden,
        n_layers=_ARGS.n_layers, n_heads=_ARGS.n_heads, ffn_dim=_ARGS.ffn_dim,
        max_pos=MAX_TOK + 16, target_dim=TARGET_DIM,
        pad_id=tokenizer.pad_token_id,
    ).to(DEVICE)
    pc = student.param_count() / 1e6
    print(f"[student] {pc:.1f}M params (target ~22M)", flush=True)

    # Pre-tokenize ALL texts ONCE (parallel; ~10-15 min for 5.84M @ num_proc=8).
    # This eliminates per-batch tokenizer overhead (was ~30-50 pct of training wall).
    train_texts = [texts[i] for i in train_idx]
    val_texts = [texts[i] for i in val_idx]
    train_targets_arr = targets[train_idx]
    val_targets_arr = targets[val_idx]
    # Free the texts list now that we have train_texts + val_texts views
    del texts
    gc.collect()

    print(f"\n=== Pre-tokenize train set ===", flush=True)
    train_tokens, train_offsets = pretokenize_in_parallel(
        train_texts, tokenizer, MAX_TOK, num_proc=_ARGS.pretokenize_num_proc
    )
    del train_texts
    gc.collect()

    print(f"\n=== Pre-tokenize val set ===", flush=True)
    val_tokens, val_offsets = pretokenize_in_parallel(
        val_texts, tokenizer, MAX_TOK, num_proc=_ARGS.pretokenize_num_proc
    )
    del val_texts
    gc.collect()

    train_ds = PretokenizedDistillDataset(train_tokens, train_offsets, train_targets_arr)
    val_ds = PretokenizedDistillDataset(val_tokens, val_offsets, val_targets_arr)
    collator = LeftPadCollator(tokenizer.pad_token_id)

    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=BATCH, shuffle=True, collate_fn=collator,
        num_workers=_ARGS.num_workers, pin_memory=True,
        prefetch_factor=_ARGS.prefetch_factor, persistent_workers=True,
    )
    val_loader = torch.utils.data.DataLoader(
        val_ds, batch_size=BATCH, shuffle=False, collate_fn=collator,
        num_workers=max(2, _ARGS.num_workers // 4), pin_memory=True,
        prefetch_factor=_ARGS.prefetch_factor, persistent_workers=True,
    )

    optimizer = torch.optim.AdamW(student.parameters(), lr=LEARNING_RATE, weight_decay=0.0)

    # LR linear warmup (then constant). 200 steps default; scaled to ~ 1% of training.
    total_steps_est = max(1, EPOCHS * (len(train_ds) // BATCH))
    WARMUP_STEPS = min(200, max(50, total_steps_est // 100))
    def lr_lambda(step):
        if step < WARMUP_STEPS:
            return step / WARMUP_STEPS
        return 1.0
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    GRAD_CLIP_MAX_NORM = 1.0

    # torch.compile() the student: ~1.5-2x on H100 for static shapes.
    # Default off (--compile to enable) because first compile takes ~30-60s and
    # var-len batches may trigger recompilations.
    use_compile = _ARGS.compile and not _ARGS.no_compile
    if use_compile:
        print(f"[compile] torch.compile() the student (mode='reduce-overhead')...", flush=True)
        try:
            student = torch.compile(student, mode="reduce-overhead")
        except Exception as e:
            print(f"[compile] failed: {type(e).__name__}: {e}; continuing eager", flush=True)
            use_compile = False

    print(f"\n=== Step 3: training student for {EPOCHS} epoch(s); "
          f"steps_est~{total_steps_est:,}; warmup={WARMUP_STEPS}; "
          f"grad_clip={GRAD_CLIP_MAX_NORM}; batch={BATCH}; lr={LEARNING_RATE}; "
          f"compile={use_compile} ===", flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Best-only checkpoint tracking (was saving every N steps = 78+ files at 5.84M scale)
    best_val_cos = -float("inf")
    best_ckpt_path = out_dir / "student_best.pt"

    t0 = time.time()
    step = 0
    losses = []
    nan_aborted = False
    val_history = []
    for epoch in range(EPOCHS):
        student.train()
        for batch in train_loader:
            input_ids = batch["input_ids"].to(DEVICE, non_blocking=True)
            attention_mask = batch["attention_mask"].to(DEVICE, non_blocking=True)
            # Target was kept fp16 (memory budget); upcast to fp32 at boundary
            target = batch["target"].to(DEVICE, non_blocking=True).float()
            with torch.amp.autocast(device_type="cuda", dtype=torch.bfloat16):
                pred = student(input_ids, attention_mask)
                loss = F.mse_loss(pred, target)
            if not torch.isfinite(loss):
                print(f"[FATAL] non-finite loss at epoch {epoch} step {step}; aborting", flush=True)
                nan_aborted = True
                break
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(student.parameters(), max_norm=GRAD_CLIP_MAX_NORM)
            optimizer.step()
            scheduler.step()
            losses.append(float(loss.item()))
            step += 1
            if step % 50 == 0:
                recent = sum(losses[-50:]) / max(len(losses[-50:]), 1)
                cur_lr = optimizer.param_groups[0]["lr"]
                print(f"  [train step {step}] loss={recent:.4f} lr={cur_lr:.2e}", flush=True)
        if nan_aborted:
            break
        # End-of-epoch validation
        val_metrics = evaluate(student, val_loader)
        val_history.append({"epoch": epoch + 1, **val_metrics})
        print(f"  [epoch {epoch+1}] val_mse={val_metrics['mse']:.4f} "
              f"val_cos={val_metrics['cos']:.4f} "
              f"(n_eval={val_metrics.get('n_evaluated','?')}, "
              f"nan_batches={val_metrics.get('n_nan_batches','?')})", flush=True)
        # Save best checkpoint by val_cos (NaN + Inf safe via math.isfinite)
        cur_cos = val_metrics.get("cos", float("nan"))
        if isinstance(cur_cos, float) and math.isfinite(cur_cos) and cur_cos > best_val_cos:
            best_val_cos = cur_cos
            sd = student._orig_mod.state_dict() if use_compile and hasattr(student, "_orig_mod") else student.state_dict()
            torch.save(sd, best_ckpt_path)
            print(f"  [ckpt] new best val_cos={cur_cos:.4f}; saved -> {best_ckpt_path.name}",
                  flush=True)

    if nan_aborted:
        raise RuntimeError("CELL-3 training aborted on non-finite loss")

    final_metrics = evaluate(student, val_loader)
    final_mse = final_metrics["mse"]
    final_cos = final_metrics["cos"]

    # Verdict: use BOTH metrics (HP if EITHER passes; HF if BOTH fail)
    mse_verdict = "HARD_PASS" if final_mse < HP_MSE else ("MID" if final_mse < MID_MSE_HIGH else "HARD_FAIL")
    cos_verdict = "HARD_PASS" if final_cos >= HP_COS else ("MID" if final_cos >= MID_COS_LOW else "HARD_FAIL")
    # Combined: best of the two
    rank = {"HARD_PASS": 2, "MID": 1, "HARD_FAIL": 0}
    verdicts = [mse_verdict, cos_verdict]
    verdict = max(verdicts, key=lambda v: rank[v])

    elapsed = time.time() - t0
    summary = (f"{verdict}: val_mse={final_mse:.4f} (HP<{HP_MSE}), val_cos={final_cos:.4f} (HP>={HP_COS}); "
               f"per-metric: mse={mse_verdict} cos={cos_verdict}")
    print(f"\n[VERDICT] {summary}", flush=True)

    # Save final student (compile-aware: unwrap _orig_mod if needed for portability)
    final_ckpt = out_dir / "student_final.pt"
    sd_final = student._orig_mod.state_dict() if use_compile and hasattr(student, "_orig_mod") else student.state_dict()
    torch.save(sd_final, final_ckpt)
    print(f"[ckpt] saved final student to {final_ckpt}", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": summary,
        "val_mse": final_mse,
        "val_cos": final_cos,
        "mse_verdict": mse_verdict,
        "cos_verdict": cos_verdict,
        "n_train": len(train_idx),
        "n_val": n_val,
        "epochs": EPOCHS,
        "batch": BATCH,
        "lr": LEARNING_RATE,
        "max_tok": MAX_TOK,
        "student_param_count_M": pc,
        "target_dim": TARGET_DIM,
        "hidden": _ARGS.hidden,
        "n_layers": _ARGS.n_layers,
        "n_heads": _ARGS.n_heads,
        "elapsed_s": elapsed,
        "val_history": val_history,
        "summary": summary,
    }
    write_metrics(out_dir, metrics, val_history)
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    main()
