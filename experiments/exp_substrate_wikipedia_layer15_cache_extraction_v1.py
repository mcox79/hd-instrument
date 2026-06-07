"""substrate_wikipedia_layer15_cache_extraction_v1 -- CELL-2 Phase 4a production substrate foundation.

ROUTING: research_to_testbed_HOLD_for_CELL2_user_decision_2026-06-06 (CELL-2 production
  substrate foundation). User authorized 2026-06-06 evening; target hardware GH200 1x.

QUESTION: build cached layer-15 last-token-pool hidden states for Llama-3.2-1B Base on
  English Wikipedia. The cache enables downstream HP-12 V2 (CELL-4 at 100K facts),
  retrieval at production scale, and the 22-26M distilled student training data
  (CELL-3).

DESIGN:
  - Stream `wikimedia/wikipedia` 20231101.en (canonical recent English Wikipedia, ~6.4M articles)
  - For each article: tokenize (MAX_TOK=512 truncation), forward through Llama-3.2-1B Base
    with output_hidden_states=True, pool last-non-pad-token at LAYER=15 (per CLOUD-1b
    optimal-depth finding for 1B; 92pct depth)
  - Save per-shard npz: hidden_states (fp16) + article_ids + titles
  - Shard size: SHARD_SIZE=10000 articles per npz (resumability + memory bounded)
  - Total output: ~640 shards x ~40 MB each = ~26 GB (at fp16)

INFRA: CELL-2-specific (carried forward from CELL-1 + 70B-Instruct):
  - TOKENIZERS_PARALLELISM=false BEFORE transformers import
  - File-first HF token (.hf_token); Llama-3.2-1B Base is gated separately from Instruct
  - tokenizer.padding_side='right' forced (Llama defaults to left)
  - last-token pool with cross-device safety (last_idx.to(hs.device))
  - PROT-022 self-test gate + --self-test flag
  - --local-pythia for runner-side sanity check (loads small Wikipedia subset on Pythia-160m)
  - ASCII-only output
  - write_metrics with REQUIRED_FIELDS

RESUMABILITY:
  - Each shard's .npz is written atomically (write to .tmp, then rename)
  - Existing shards on disk are SKIPPED on rerun (don't re-extract)
  - Final metrics.json includes shard manifest for downstream consumers

EXIT BANDS (informational; not a binding test):
  COMPLETE: all expected shards written; total_articles >= target
  PARTIAL:  some shards written; resumable on next dispatch
  FAILED:   no shards or fatal error at model load / data load
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
from typing import List, Tuple, Dict, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)
import numpy as np

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "substrate_wikipedia_layer15_cache_extraction_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--local-pythia", action="store_true")
_ap.add_argument("--max-articles", type=int, default=None,
                  help="Cap on total articles processed (overrides defaults; useful for smoke)")
_ARGS, _ = _ap.parse_known_args()

LOCAL_PYTHIA = _ARGS.local_pythia

MODEL_LLAMA_1B = "meta-llama/Llama-3.2-1B"
PYTHIA = "EleutherAI/pythia-160m"
WIKI_DATASET = "wikimedia/wikipedia"
WIKI_CONFIG = "20231101.en"

LAYER_LLAMA = 15   # per CLOUD-1b: 92pct depth of 16-layer Llama-3.2-1B
LAYER_PYTHIA = 11  # 92pct depth of 12-layer Pythia-160m (sanity check)

MAX_TOK = 512
BATCH_SIZE = 128       # v3: bumped from 64 to 128 (GH200 96GB; 1B at batch=128 ~5GB peak)
NUM_WORKERS = 16       # v3: bumped from 8 to 16 (data is local-disk now; tokenization can parallelize harder)
PREFETCH_FACTOR = 8    # v3: bumped from 4 to 8 (deeper pipeline; GPU never starved)

if RUN_MODE == "smoke":
    SHARD_SIZE = 200
    TARGET_ARTICLES = 1000
elif LOCAL_PYTHIA:
    SHARD_SIZE = 100
    TARGET_ARTICLES = 500
else:
    SHARD_SIZE = 10000        # ~40 MB per shard at hidden_dim=2048 fp16
    TARGET_ARTICLES = 6500000 # v3 re-extract: FULL Wikipedia with left-pad + pre-download + bigger batch

if _ARGS.max_articles is not None:
    TARGET_ARTICLES = _ARGS.max_articles
    SHARD_SIZE = min(SHARD_SIZE, TARGET_ARTICLES)


def _load_hf_token() -> str:
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    env_tok = os.environ.get("HF_TOKEN", "").strip()
    if env_tok:
        return env_tok
    raise RuntimeError("HF token not found at <repo>/.hf_token or $HF_TOKEN.")


def last_token_pool(hs, am, padding_side: str = "left"):
    """Cross-device safe last-non-pad-token pool.

    For LEFT-padding (cycle 142 fix): non-pad tokens occupy positions [pad_count,
    seq_len), so the last real token is ALWAYS at position seq_len - 1 regardless
    of attention mask. Using am.sum(dim=1) - 1 here would extract the WRONG
    position (mid-sequence rather than the last position).

    For RIGHT-padding: non-pad tokens occupy positions [0, sum(am)), so the last
    real token is at position sum(am) - 1.
    """
    am_int = am.long()
    if padding_side == "left":
        seq_len = am.size(1)
        last_idx = torch.full((am.size(0),), seq_len - 1, dtype=torch.long, device=am.device)
    else:  # right
        last_idx = (am_int.sum(dim=1) - 1).clamp_min(0)
    last_idx = last_idx.to(hs.device)
    batch_idx = torch.arange(hs.size(0), device=hs.device)
    return hs[batch_idx, last_idx]


def _selftest():
    """PROT-022: test BOTH padding sides + collate."""
    import torch
    hs = torch.tensor([[[1.0], [2.0], [3.0], [4.0]]])

    # Right-padding case: am = [1,1,1,0] -> last real at position 2 -> expect 3.0
    am_right = torch.tensor([[1, 1, 1, 0]])
    lt_right = last_token_pool(hs, am_right, padding_side="right")
    assert abs(float(lt_right[0, 0]) - 3.0) < 1e-5, f"right-pad last_token got {lt_right}"

    # Left-padding case: am = [0,1,1,1] -> last real at position 3 -> expect 4.0
    am_left = torch.tensor([[0, 1, 1, 1]])
    lt_left = last_token_pool(hs, am_left, padding_side="left")
    assert abs(float(lt_left[0, 0]) - 4.0) < 1e-5, f"left-pad last_token got {lt_left}"

    # Check torch + numpy interop
    arr = np.array([1, 2, 3], dtype=np.float32)
    t = torch.from_numpy(arr)
    assert float(t.sum()) == 6.0

    print("[selftest] PASS: last_token_pool (left+right) + numpy interop", flush=True)


def _selftest_collate():
    """Separate from _selftest() because collate_pad is defined later in the file.
    Called after collate_pad definition."""
    import torch
    batch = [
        {"input_ids": torch.tensor([7, 8, 9]), "attention_mask": torch.tensor([1, 1, 1]),
         "id": "0", "title": "t0", "token_count": 3},
        {"input_ids": torch.tensor([5]), "attention_mask": torch.tensor([1]),
         "id": "1", "title": "t1", "token_count": 1},
    ]
    out = collate_pad(batch)
    # Expected after LEFT-pad to max_len=3:
    #   row 0: [7, 8, 9]  am=[1, 1, 1]
    #   row 1: [0, 0, 5]  am=[0, 0, 1]  <- pads at LEFT (not at the right!)
    assert out["input_ids"].tolist() == [[7, 8, 9], [0, 0, 5]], f"collate input_ids: {out['input_ids']}"
    assert out["attention_mask"].tolist() == [[1, 1, 1], [0, 0, 1]], f"collate am: {out['attention_mask']}"
    print("[selftest] PASS: LEFT-pad collate_pad", flush=True)


_selftest()
# _selftest_collate() + CUDA check deferred until after collate_pad is defined


def stream_wikipedia(model_for_pythia_sanity: bool = False):
    """Stream Wikipedia articles. Returns iterator of (article_id, title, text).

    CRITICAL: streaming=True is mandatory (regardless of Pythia sanity vs cloud).
    streaming=False triggers a full ~20 GB Wikipedia download which is wasteful
    for sanity tests AND wastes cloud time on the first-time download.
    """
    from datasets import load_dataset
    print(f"[data] loading {WIKI_DATASET}/{WIKI_CONFIG} (streaming mode)...", flush=True)
    ds = load_dataset(WIKI_DATASET, WIKI_CONFIG, split="train",
                       streaming=True, trust_remote_code=False)
    yielded = 0
    for ex in ds:
        yield ex.get("id", str(yielded)), ex.get("title", ""), ex.get("text", "")
        yielded += 1
        if yielded >= TARGET_ARTICLES:
            return


def find_existing_shards(out_dir: Path) -> Dict[int, Path]:
    """Return {shard_idx: path} for already-written shards (resumability)."""
    existing = {}
    for f in out_dir.glob("shard_*.npz"):
        try:
            idx = int(f.stem.split("_")[1])
            existing[idx] = f
        except (IndexError, ValueError):
            continue
    return existing


def shard_path(out_dir: Path, shard_idx: int) -> Path:
    return out_dir / f"shard_{shard_idx:05d}.npz"


def save_shard(out_dir: Path, shard_idx: int, hidden_states: np.ndarray,
                article_ids: List[str], titles: List[str], token_counts: List[int]):
    """Save shard atomically: write to file-object then os.replace.

    NOTE: np.savez_compressed AUTO-APPENDS '.npz' to a path arg if it doesn't
    already end in .npz. To control the exact filename for atomic-rename, write
    to an open file-object instead (no auto-append) and use os.replace.
    """
    p = shard_path(out_dir, shard_idx)
    p_tmp = str(p) + ".tmp"
    with open(p_tmp, "wb") as f:
        np.savez_compressed(
            f,
            hidden_states=hidden_states.astype(np.float16),
            article_ids=np.array(article_ids, dtype=object),
            titles=np.array(titles, dtype=object),
            token_counts=np.array(token_counts, dtype=np.int32),
        )
    os.replace(p_tmp, str(p))


class WikiStreamDataset(torch.utils.data.IterableDataset):
    """Streaming Wikipedia dataset that auto-shards across DataLoader workers.

    Each worker takes every Nth article (N=num_workers, offset=worker_id) so
    parallel workers don't fetch duplicate articles. Tokenization happens inside
    each worker, giving us parallel network IO + parallel CPU tokenization.

    Yields dicts: {input_ids, attention_mask, id, title, token_count}.
    """

    def __init__(self, tokenizer, max_articles: int, max_tok: int,
                 is_pythia_sanity: bool = False):
        super().__init__()
        self.tokenizer = tokenizer
        self.max_articles = max_articles
        self.max_tok = max_tok
        self.is_pythia_sanity = is_pythia_sanity

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is None:
            worker_id, num_workers = 0, 1
        else:
            worker_id, num_workers = worker_info.id, worker_info.num_workers

        from datasets import load_dataset
        ds = load_dataset(WIKI_DATASET, WIKI_CONFIG, split="train",
                          streaming=True, trust_remote_code=False)

        # HF Datasets >=2.18 AUTO-shards streaming dataset across DataLoader
        # workers based on the dataset's file shards. v1 bug: I additionally
        # filtered by `idx % num_workers == worker_id` ON TOP of the auto-shard,
        # giving 1/64 sampling instead of 1/8. Resulting in only 12.5% of
        # articles extracted. Removed; auto-sharding is sufficient.

        # Per-worker target: split TARGET_ARTICLES across workers
        per_worker_target = max(1, self.max_articles // num_workers)
        emitted = 0
        for idx, ex in enumerate(ds):
            if emitted >= per_worker_target:
                return
            text = ex.get("text", "")
            article_id = ex.get("id", str(idx))
            title = ex.get("title", "")
            enc = self.tokenizer(text, truncation=True, max_length=self.max_tok,
                                 return_tensors="pt")
            input_ids = enc["input_ids"].squeeze(0)
            attention_mask = enc["attention_mask"].squeeze(0)
            yield {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "id": article_id,
                "title": title,
                "token_count": int(attention_mask.sum().item()),
            }
            emitted += 1


def collate_pad(batch):
    """Pad batch to max length within batch (LEFT-padding per cycle 142).

    Right-padding causes ~22.6 pct retrieval-quality loss via PAD-token extraction
    (Q4 + cycle 142 empirical validation 2026-06-07). torch.nn.utils.rnn.pad_sequence
    only RIGHT-pads, so we implement LEFT-padding manually here.
    """
    max_len = max(b["input_ids"].size(0) for b in batch)
    pad_id = 0
    input_ids = torch.zeros(len(batch), max_len, dtype=torch.long)
    attention_mask = torch.zeros(len(batch), max_len, dtype=torch.long)
    for i, b in enumerate(batch):
        n = b["input_ids"].size(0)
        # Pad on LEFT: real tokens go at the END of the row
        input_ids[i, max_len - n:] = b["input_ids"]
        attention_mask[i, max_len - n:] = b["attention_mask"]
        if pad_id != 0:
            input_ids[i, :max_len - n] = pad_id
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "ids": [b["id"] for b in batch],
        "titles": [b["title"] for b in batch],
        "token_counts": [b["token_count"] for b in batch],
    }


# Run collate test now that collate_pad is defined; THEN check --self-test exit
_selftest_collate()
if _ARGS.self_test:
    print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
    sys.exit(0)

# CUDA check happens AFTER --self-test exit so self-test works without GPU
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available; this script is GPU-only.", flush=True)
    sys.exit(1)
DEVICE = torch.device("cuda")
print(f"[GPU] {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)", flush=True)


def run_extraction(model_id: str, layer_idx: int, hf_token: Optional[str],
                    is_pythia_sanity: bool = False) -> Dict:
    """Stream Wikipedia, extract per-shard, save resumably. Returns metrics."""
    # CRITICAL: use AutoModel (no LM head) instead of AutoModelForCausalLM. The
    # final lm_head computes vocab-sized logits tensor (e.g., 50K x 64 x 512 x 4 =
    # 6 GB on Pythia at batch=64 seq=512). We only need hidden_states for last-
    # token pool; the logits are wasted. AutoModel returns BaseModelOutput with
    # output_hidden_states=True providing all transformer-block outputs.
    from transformers import AutoModel, AutoTokenizer
    # Reset peak memory (no carryover)
    for d in range(torch.cuda.device_count()):
        torch.cuda.reset_peak_memory_stats(d)
    gc.collect()
    torch.cuda.empty_cache()

    # Pythia sanity uses smaller effective batch to fit 8 GB consumer GPU
    bs = BATCH_SIZE if not is_pythia_sanity else 8

    print(f"[load] {model_id}; layer={layer_idx}; batch={bs}; max_tok={MAX_TOK}", flush=True)
    t0 = time.time()
    load_kwargs = {"torch_dtype": torch.float16, "device_map": {"": DEVICE}}
    if hf_token is not None:
        load_kwargs["token"] = hf_token
    if is_pythia_sanity:
        # Pythia uses fp32 (small enough on host) + no token needed
        load_kwargs = {"torch_dtype": torch.float32, "device_map": {"": DEVICE}}

    model = AutoModel.from_pretrained(model_id, **load_kwargs)
    tokenizer_kwargs = {"token": hf_token} if hf_token is not None else {}
    tokenizer = AutoTokenizer.from_pretrained(model_id, **tokenizer_kwargs)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"  # v3: cycle 142 fix (Q4 empirical +22.6 pct retrieval lift)
    t_load = time.time() - t0
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    print(f"  [load] {t_load:.1f}s; GPU peak {peak:.2f} GB", flush=True)
    print(f"  [tokenizer] padding_side forced to '{tokenizer.padding_side}' (v3 cycle 142 left-pad fix)", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = find_existing_shards(out_dir)
    if existing:
        print(f"  [resume] found {len(existing)} existing shards; will skip them.", flush=True)

    # Determine the starting shard index: continue from after the highest existing shard
    next_shard_idx = max(existing.keys()) + 1 if existing else 0
    total_skipped_existing = len(existing) * SHARD_SIZE
    print(f"  [start] resuming from shard_idx={next_shard_idx} (already-on-disk={len(existing)} shards)", flush=True)

    # PARALLEL DATA PIPELINE: DataLoader(num_workers) so parallel network IO
    # + parallel tokenization can keep the GPU fed. Each worker shards the
    # streaming dataset by article index modulo num_workers.
    n_workers = NUM_WORKERS if not is_pythia_sanity else 2
    # Effective target excludes already-extracted articles
    remaining_target = max(1, TARGET_ARTICLES - total_skipped_existing)
    print(f"  [pipeline] DataLoader workers={n_workers} prefetch_factor={PREFETCH_FACTOR} "
          f"batch={bs} remaining_target={remaining_target}", flush=True)

    dataset = WikiStreamDataset(tokenizer, max_articles=remaining_target,
                                  max_tok=MAX_TOK,
                                  is_pythia_sanity=is_pythia_sanity)
    loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=bs,
        num_workers=n_workers,
        collate_fn=collate_pad,
        prefetch_factor=PREFETCH_FACTOR,
        persistent_workers=False,
    )

    # Shard accumulators
    shard_idx = next_shard_idx
    pooled_buf = []     # list of (N, H) arrays per batch
    ids_buf = []
    titles_buf = []
    tc_buf = []
    total_extracted = 0
    t_run_start = time.time()
    t_last_print = time.time()
    batches_done = 0

    model.eval()
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(DEVICE, non_blocking=True)
            attention_mask = batch["attention_mask"].to(DEVICE, non_blocking=True)

            out = model(input_ids=input_ids,
                          attention_mask=attention_mask,
                          output_hidden_states=True,
                          use_cache=False)
            hs = out.hidden_states[layer_idx]
            am = attention_mask.long()
            p = last_token_pool(hs.float(), am, padding_side="left").cpu().numpy()

            pooled_buf.append(p)
            ids_buf.extend(batch["ids"])
            titles_buf.extend(batch["titles"])
            tc_buf.extend(batch["token_counts"])
            batches_done += 1

            # Flush shard when accumulator reaches SHARD_SIZE
            while sum(arr.shape[0] for arr in pooled_buf) >= SHARD_SIZE:
                hs_concat = np.concatenate(pooled_buf, axis=0)
                cut = SHARD_SIZE
                hs_this = hs_concat[:cut]
                hs_rest = hs_concat[cut:]
                ids_this, ids_buf = ids_buf[:cut], ids_buf[cut:]
                titles_this, titles_buf = titles_buf[:cut], titles_buf[cut:]
                tc_this, tc_buf = tc_buf[:cut], tc_buf[cut:]

                save_shard(out_dir, shard_idx, hs_this, ids_this, titles_this, tc_this)
                total_extracted += cut
                elapsed_total = time.time() - t_run_start
                rate = total_extracted / max(elapsed_total, 1e-9)
                done = total_extracted + total_skipped_existing
                eta_s = (TARGET_ARTICLES - done) / max(rate, 1e-9)
                print(f"  [shard {shard_idx:5d}] flushed n={cut} | total extracted={total_extracted} "
                      f"skipped={total_skipped_existing} | rate={rate:.0f}/s | ETA={eta_s/60:.1f}min",
                      flush=True)
                shard_idx += 1
                pooled_buf = [hs_rest] if hs_rest.shape[0] > 0 else []

            # Light heartbeat between shards so we know workers are alive
            now = time.time()
            if now - t_last_print > 30 and batches_done > 0:
                queued = sum(arr.shape[0] for arr in pooled_buf)
                print(f"  [heartbeat] batches={batches_done} | extracted={total_extracted} "
                      f"| in_buf={queued} | rate={total_extracted/max(now-t_run_start,1e-9):.0f}/s",
                      flush=True)
                t_last_print = now

    # Flush final partial shard
    if pooled_buf and sum(arr.shape[0] for arr in pooled_buf) > 0:
        hs_concat = np.concatenate(pooled_buf, axis=0)
        n_final = hs_concat.shape[0]
        save_shard(out_dir, shard_idx, hs_concat, ids_buf, titles_buf, tc_buf)
        total_extracted += n_final
        print(f"  [shard {shard_idx:5d}] FINAL n={n_final} (partial)", flush=True)
        shard_idx += 1

    elapsed = time.time() - t_run_start
    final_existing = find_existing_shards(out_dir)
    return {
        "model_id": model_id,
        "layer_idx": layer_idx,
        "target_articles": TARGET_ARTICLES,
        "extracted_this_run": total_extracted,
        "skipped_existing_this_run": total_skipped_existing,
        "n_shards_on_disk": len(final_existing),
        "shard_size": SHARD_SIZE,
        "batch_size": BATCH_SIZE,
        "max_tok": MAX_TOK,
        "hidden_dim": int(model.config.hidden_size),
        "load_wall_s": t_load,
        "extract_wall_s": elapsed,
        "gpu_peak_gb": float(peak),
        "padding_side": tokenizer.padding_side,
    }


def main_local_pythia():
    """Local sanity check: 500-article Wikipedia subset on Pythia-160m."""
    print(f"[config] anchor={ANCHOR_NAME} mode=LOCAL-PYTHIA-SANITY target_articles={TARGET_ARTICLES}", flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    # Use Pythia anchor namespace to keep separate from real run
    pythia_anchor = ANCHOR_NAME + "_pythia_sanity"
    pythia_out = REPO / "data" / f"exp_{pythia_anchor}"
    pythia_out.mkdir(parents=True, exist_ok=True)
    # Hack: temporarily change out_dir; we want to write to pythia_out
    os.environ["HDLAB_EXP_NAME"] = pythia_anchor
    r = run_extraction(PYTHIA, LAYER_PYTHIA, hf_token=None, is_pythia_sanity=True)
    print(f"\n[PYTHIA-SANITY-VERDICT]", flush=True)
    if r["n_shards_on_disk"] > 0 and r["extracted_this_run"] > 0:
        print(f"  PASS: Pipeline functional. Extracted {r['extracted_this_run']} articles in "
              f"{r['extract_wall_s']:.1f}s ({r['extracted_this_run']/max(r['extract_wall_s'],1e-9):.1f}/s). "
              f"Hidden dim={r['hidden_dim']}. Safe to dispatch to cloud.", flush=True)
    else:
        print(f"  FAIL: extracted={r['extracted_this_run']} shards_on_disk={r['n_shards_on_disk']}. "
              f"Do NOT dispatch to cloud; fix pipeline first.", flush=True)


def main_cloud():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} target_articles={TARGET_ARTICLES} "
          f"shard_size={SHARD_SIZE} batch={BATCH_SIZE} max_tok={MAX_TOK} layer={LAYER_LLAMA}", flush=True)
    hf_token = _load_hf_token()
    t0 = time.time()
    r = run_extraction(MODEL_LLAMA_1B, LAYER_LLAMA, hf_token)
    elapsed = time.time() - t0

    # Verdict: COMPLETE / PARTIAL / FAILED
    if r["n_shards_on_disk"] == 0:
        verdict = "FAILED"
        vmsg = f"FAILED: 0 shards on disk after run. {r}"
    elif r["extracted_this_run"] + r["skipped_existing_this_run"] >= TARGET_ARTICLES * 0.95:
        verdict = "COMPLETE"
        vmsg = (f"COMPLETE: {r['n_shards_on_disk']} shards on disk; "
                f"{r['extracted_this_run']} extracted this run; "
                f"{r['skipped_existing_this_run']} skipped (resumed)")
    else:
        verdict = "PARTIAL"
        vmsg = (f"PARTIAL: only {r['extracted_this_run'] + r['skipped_existing_this_run']} of "
                f"{TARGET_ARTICLES} articles extracted; resumable via rerun")

    print(f"\n[VERDICT] {vmsg}", flush=True)
    print(f"[GPU peak] {r['gpu_peak_gb']:.2f} GB", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "model_id": MODEL_LLAMA_1B,
        "layer_idx": LAYER_LLAMA,
        "target_articles": TARGET_ARTICLES,
        "shard_size": SHARD_SIZE,
        "extracted_this_run": r["extracted_this_run"],
        "skipped_existing_this_run": r["skipped_existing_this_run"],
        "n_shards_on_disk": r["n_shards_on_disk"],
        "hidden_dim": r["hidden_dim"],
        "load_wall_s": r["load_wall_s"],
        "extract_wall_s": r["extract_wall_s"],
        "elapsed_s": elapsed,
        "gpu_peak_gb": r["gpu_peak_gb"],
        "summary": vmsg,
    }
    out_dir = get_output_dir(ANCHOR_NAME)
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written", flush=True)


def main():
    if LOCAL_PYTHIA:
        main_local_pythia()
    else:
        main_cloud()


if __name__ == "__main__":
    main()
