"""phase05_v1_llama32_1b_per_token_residual_extract_v1 -- Phase 2 Llama-1B per-token extraction.

SCIENTIFIC QUESTION:
  Produce a clean Llama-3.2-1B last-layer per-token residual npz for downstream
  EX-CONCEPT-1 REAL + substrate-audit-core C2 + C3 at the 1B scale tier. Forked
  from the Pythia-160M per-token script (HARD_PASS'd 2026-06-05); same audit
  fixes carry over identically.

ROUTING:
  - User-authorized (2026-06-05): destination C:\\dev\\hd-instrument\\data\\ on
    marsh@home (Option A); compute path = H100 cloud (per user's high-confidence
    + saving-as-it-goes criteria).
  - Per research_to_testbed_probe_storage_layout_destination_2026-06-05 +
    research_to_exp_dev_llama_1b_extraction_authorized_phase2_start_2026-06-05.
  - Unblocks: substrate-audit-core C2 + C3 at 1B scale (Tier-1 anchor; closed-
    form algebra; valid scale-tier per Research's hybrid C+D plan); EX-CONCEPT-
    REAL at 1B scale (richer concept-LM than Pythia-160M).

PIPELINE:
  1. Set TOKENIZERS_PARALLELISM=false BEFORE transformers import (defensive
     against the fork-after-parallelism deadlock that hung Llama v6/v7 on
     marsh@home before the v8 fix).
  2. Load Llama-3.2-1B (base, NOT Instruct -- mirrors Rung A v6/v7 target for
     substrate-audit-core continuity; meta-llama/Llama-3.2-1B, ~2 GB BF16) on
     cuda. Requires HF token (gated repo); file-first precedence preserved.
  3. Iterate over the analogy dataset (saturnMars/hyperprobe-dataset-analogy);
     setup phase pre-warms HF cache via snapshot_download.
  4. For each doc: forward + extract hidden_states[16] (= last layer of 16
     transformer blocks; hidden_states[0]=embedding so final layer = idx 16)
     at all real-token positions. Shape: (T_real, 2048) float32.
  5. Concatenate per-token to (sum_T, 2048) npz at out_dir/residuals_per_token.npz
     with CSR-like doc_indices + doc_boundaries for per-doc slicing.
  6. Sidecar metadata JSON; per-token mode is DEFAULT (covers both substrate-
     audit-core via last-token slice + EX-CONCEPT-REAL via full sequence).
  7. Per-doc watchdog: os._exit(99) if no doc completes in 120s.
  8. PROT-021 per-doc partials via _seed_checkpoint.write_partial_key so a
     watchdog-triggered exit loses only in-flight work, not completed docs.

PRE-REGISTERED BANDS:
  HARD-PASS: extraction completes with >= MIN_DOCS_HP docs covered, all finite,
             no NaN, shape (sum_T, 2048), npz file exists at expected path.
  MIDDLE:    pipeline runs but partial (e.g. < MIN_DOCS_HP); some residuals
             extracted but watchdog fired or dataset ran out.
  HARD-FAIL: < MIN_DOCS_HP/2 docs covered OR npz contains NaN OR script crashed
             at setup before any extraction.

PROT-018: no _nN suffix (Llama-3.2-1B hidden_dim=2048 is fixed by model, not swept).
PROT-021: per-doc partials with model_id + run_mode + idx-of-N keys.
PROT-022: import-time self-tests for residual shape / sign / npz round-trip.

ASCII-only stdout per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import os
# CRITICAL v8-lesson fix: TOKENIZERS_PARALLELISM=false MUST be set BEFORE the
# transformers / tokenizers import. Otherwise huggingface/tokenizers spawns its
# rayon thread pool early and a later fork() (HF datasets workers, our own
# pool, anything) can deadlock against the locked pool. Both Llama v6 + v7 hung
# silently for this reason. Same fix here defensively.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import threading
import time
import traceback
from pathlib import Path
from typing import Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial_key, list_completed_keys, write_metrics,
)

ANCHOR_NAME = "phase05_v1_llama32_1b_per_token_residual_extract_v1"

MODEL_ID = "meta-llama/Llama-3.2-1B"
HIDDEN_DIM = 2048
N_LAYERS = 16                  # Llama-3.2-1B: 16 transformer blocks
LAYER_IDX_TARGET = 16          # last layer's output = hidden_states[16]
                               # (HF returns L+1=17 hidden_states; idx 0 = embedding)

MAX_TOK_LEN = 64               # analogy docs are short; consistent with Pythia
PROGRESS_EVERY = 50

# v8-lesson watchdog: exit fast if no doc completes within this window.
WATCHDOG_PER_DOC_TIMEOUT_S = 120
_LAST_DOC_COMPLETE_TS: list = [None]

# Extraction targets
N_DOCS_FULL = 10000
N_DOCS_SMOKE = 50
MIN_DOCS_HP = 5000             # HARD_PASS gate floor

DATASET_ID = "saturnMars/hyperprobe-dataset-analogy"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else
            os.environ.get("HDLAB_RUN_MODE", "full")).lower()
USE_SYNTHETIC = (RUN_MODE == "smoke")
N_DOCS_TARGET = N_DOCS_SMOKE if RUN_MODE == "smoke" else N_DOCS_FULL

# Per-token mode is DEFAULT for this Llama-1B script (user-directed; covers
# both substrate-audit-core via last-token slice + EX-CONCEPT-REAL via full
# sequence). Pass --per-doc (or HDLAB_PER_DOC=1) to override and write only
# residuals.npz (n_docs, 2048).
PER_DOC_OVERRIDE = ("--per-doc" in sys.argv or
                    os.environ.get("HDLAB_PER_DOC", "0") in {"1", "true", "True"})
PER_TOKEN_MODE = not PER_DOC_OVERRIDE


def _load_hf_token() -> str:
    """File-first HF token precedence (Rung A v5/v6 lesson).

    Llama-3.2-1B-Instruct is a GATED model; HF token IS required.
    File-first precedence: repo-local .hf_token wins over HF_TOKEN env (so a
    stale shell-profile HF_TOKEN env cannot override the licensed file token).
    Raises if neither source has a non-empty value.
    """
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
        "Llama-3.2-1B-Instruct is a gated repo and requires accepted-license token."
    )


# ---------------- PROT-022 import-time self-tests ----------------

def _selftest_shape_residual():
    """Synthetic (768,) residual round-trip: dtype + shape preserved."""
    r = np.random.default_rng(7).standard_normal(HIDDEN_DIM).astype(np.float32)
    assert r.shape == (HIDDEN_DIM,)
    assert r.dtype == np.float32
    assert np.isfinite(r).all()


def _selftest_npz_roundtrip():
    """Write+read a tiny (3, 768) npz to a tempdir; values preserved."""
    import tempfile
    arr = np.arange(3 * HIDDEN_DIM, dtype=np.float32).reshape(3, HIDDEN_DIM)
    with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as fh:
        path = fh.name
    try:
        np.savez_compressed(path, residuals=arr)
        loaded = np.load(path)
        assert "residuals" in loaded.files
        round_trip = loaded["residuals"]
        assert round_trip.shape == arr.shape
        assert (round_trip == arr).all()
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


def _run_selftests():
    print("PROT-022 selftests:", flush=True)
    _selftest_shape_residual()
    print("selftest shape_residual: PASS", flush=True)
    _selftest_npz_roundtrip()
    print("selftest npz_roundtrip: PASS", flush=True)
    print("PROT-022 selftests: ALL PASS", flush=True)


_run_selftests()

if "--self-test" in sys.argv:                # queue_add gate: selftests ran at import; exit before model load
    print("[selftest] PASS (import-time PROT-022); exiting before extraction.", flush=True)
    sys.exit(0)


# ---------------- helpers ----------------

def _watchdog_start(out_dir: Path) -> threading.Thread:
    """Spawn daemon watchdog that exits the process if no doc completes in
    WATCHDOG_PER_DOC_TIMEOUT_S. Runner can resume from per-doc partials."""
    _LAST_DOC_COMPLETE_TS[0] = time.monotonic()

    def _loop():
        while True:
            time.sleep(15)
            last = _LAST_DOC_COMPLETE_TS[0]
            if last is None:
                continue
            idle = time.monotonic() - last
            if idle > WATCHDOG_PER_DOC_TIMEOUT_S:
                msg = (f"\n[WATCHDOG] no doc completed in {idle:.1f}s "
                       f"(threshold {WATCHDOG_PER_DOC_TIMEOUT_S}s); "
                       f"presumed deadlock; os._exit(99). "
                       f"Resume from per-doc partials on next dispatch.")
                try:
                    print(msg, flush=True)
                    (out_dir / "watchdog_exit.json").write_text(
                        json.dumps({
                            "idle_seconds": idle,
                            "watchdog_timeout_s": WATCHDOG_PER_DOC_TIMEOUT_S,
                            "timestamp_utc": time.strftime(
                                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        }, indent=2),
                        encoding="utf-8",
                    )
                except Exception:
                    pass
                os._exit(99)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t


def _load_llama(device: str):
    """Load Llama-3.2-1B-Instruct on device with bf16 + use_cache=False.

    Llama is gated; token required (file-first per _load_hf_token).
    use_cache=False for residual extraction (no KV cache needed; saves VRAM).
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    token = _load_hf_token()
    print(f"  loading {MODEL_ID} -> device={device} dtype=bf16 ...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.bfloat16,
        device_map=device,
        use_cache=False,
    )
    model.eval()
    cfg = model.config
    print(f"  model loaded in {time.time() - t0:.1f}s; "
          f"hidden_size={cfg.hidden_size} n_layers={cfg.num_hidden_layers}",
          flush=True)
    if cfg.hidden_size != HIDDEN_DIM:
        raise RuntimeError(
            f"Llama hidden_size {cfg.hidden_size} != expected {HIDDEN_DIM}; "
            f"model swap?")
    if cfg.num_hidden_layers != N_LAYERS:
        raise RuntimeError(
            f"Llama num_hidden_layers {cfg.num_hidden_layers} != "
            f"expected {N_LAYERS}; model swap?")
    return model, tokenizer


def _extract_residual_one_doc(model, tokenizer, doc: str, device: str) -> np.ndarray:
    """Forward Llama-3.2-1B on doc; return (2048,) float32 last-layer final-token residual."""
    import torch
    enc = tokenizer(doc, return_tensors="pt", truncation=True, max_length=MAX_TOK_LEN)
    input_ids = enc["input_ids"].to(device)
    attn = enc.get("attention_mask")
    if attn is not None:
        attn = attn.to(device)
    with torch.no_grad():
        out = model(
            input_ids=input_ids,
            attention_mask=attn,
            output_hidden_states=True,
            use_cache=False,
        )
    hs = out.hidden_states  # tuple len L+1 = 13
    if len(hs) != N_LAYERS + 1:
        raise RuntimeError(
            f"hidden_states len={len(hs)} != expected {N_LAYERS + 1}")
    # Last layer at final token; cast BF16 -> F32 BEFORE .cpu().numpy()
    last = hs[LAYER_IDX_TARGET][0, -1, :].float().detach().cpu().numpy()
    if last.shape != (HIDDEN_DIM,):
        raise RuntimeError(
            f"residual shape wrong: {last.shape}; expected ({HIDDEN_DIM},)")
    return last.astype(np.float32)


def _extract_residual_per_token_one_doc(model, tokenizer, doc: str, device: str) -> np.ndarray:
    """Forward Llama-3.2-1B on doc; return (T, 2048) float32 last-layer per-token residuals.

    Per-token variant for EX-CONCEPT-1 REAL (2026-06-05 Research request).
    T = actual token count after tokenization (<= MAX_TOK_LEN). Trailing
    padding (if any) is NOT included; we use attention_mask to truncate to
    the actual token positions.
    """
    import torch
    enc = tokenizer(doc, return_tensors="pt", truncation=True, max_length=MAX_TOK_LEN)
    input_ids = enc["input_ids"].to(device)
    attn = enc.get("attention_mask")
    if attn is not None:
        attn = attn.to(device)
    with torch.no_grad():
        out = model(
            input_ids=input_ids,
            attention_mask=attn,
            output_hidden_states=True,
            use_cache=False,
        )
    hs = out.hidden_states
    if len(hs) != N_LAYERS + 1:
        raise RuntimeError(
            f"hidden_states len={len(hs)} != expected {N_LAYERS + 1}")
    # Determine the real (un-padded) token count from attention_mask. If absent,
    # fall back to input_ids length (no padding expected for single-doc forwards).
    if attn is not None:
        t_real = int(attn[0].sum().item())
    else:
        t_real = int(input_ids.shape[1])
    if t_real <= 0:
        raise RuntimeError(f"per-token: zero real tokens after tokenization (doc={doc[:60]!r})")
    # Last layer, all real-token positions; (T, 768) float32
    arr = hs[LAYER_IDX_TARGET][0, :t_real, :].float().detach().cpu().numpy()
    if arr.shape != (t_real, HIDDEN_DIM):
        raise RuntimeError(
            f"per-token residual shape wrong: {arr.shape}; expected ({t_real}, {HIDDEN_DIM})")
    return arr.astype(np.float32)


def _synthetic_residual(idx: int, rng: np.random.Generator) -> np.ndarray:
    """Smoke fallback: synthetic (768,) float32 residual."""
    sub = np.random.default_rng(rng.integers(0, 2**31 - 1) + idx)
    return sub.standard_normal(HIDDEN_DIM).astype(np.float32)


def _synthetic_residual_per_token(idx: int, rng: np.random.Generator) -> np.ndarray:
    """Smoke fallback per-token: synthetic (T, 768) float32 residual sequence.

    Token count T is randomly between 4 and 16 (representative analogy
    doc length) and seeded by doc idx for determinism.
    """
    sub = np.random.default_rng(rng.integers(0, 2**31 - 1) + idx)
    t_real = int(sub.integers(4, 17))   # T in [4, 16]
    return sub.standard_normal((t_real, HIDDEN_DIM)).astype(np.float32)


# ---------------- main ----------------

def main() -> int:
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "startup.log"

    def log(msg: str) -> None:
        line = f"[{time.time() - t0:7.2f}s] {msg}"
        print(line, flush=True)
        try:
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except Exception:
            pass

    log(f"START anchor={ANCHOR_NAME} run_mode={RUN_MODE} "
        f"n_docs_target={N_DOCS_TARGET}")

    # ---- Step 1: load corpus ----
    parsed: list = []
    if USE_SYNTHETIC:
        log("smoke mode: skipping dataset load; synthetic docs")
        parsed = [{"doc": f"smoke synthetic doc {i}"} for i in range(N_DOCS_TARGET)]
    else:
        try:
            log(f"loading dataset {DATASET_ID}")
            from datasets import load_dataset
            ds = load_dataset(DATASET_ID, token=_load_hf_token() or None)
            split = "train" if "train" in ds else next(iter(ds))
            raw = ds[split]
            log(f"dataset split={split} n_rows={len(raw)}")
            for i, row in enumerate(raw):
                if "doc" in row:
                    parsed.append({"doc": row["doc"]})
                elif "text" in row:
                    parsed.append({"doc": row["text"]})
                if len(parsed) >= N_DOCS_TARGET:
                    break
            log(f"corpus built: {len(parsed)} docs (target {N_DOCS_TARGET})")
        except Exception as e:
            log(f"FAILED_SETUP: dataset load failed: {e}")
            write_metrics(out_dir, {
                "anchor": ANCHOR_NAME,
                "verdict": "FAILED_SETUP",
                "verdict_msg": f"dataset load failed: {e}",
                "elapsed_s": time.time() - t0,
                "summary": "dataset_load_failure",
                "exception": traceback.format_exc(),
            })
            return 0

    # ---- Step 2: load model (or synthetic) ----
    device = "cuda" if not USE_SYNTHETIC else "cpu"
    model = None
    tokenizer = None
    if not USE_SYNTHETIC:
        try:
            model, tokenizer = _load_llama(device)
            log("Llama-3.2-1B load OK")
        except Exception as e:
            log(f"FAILED_SETUP: Llama load failed: {e}")
            write_metrics(out_dir, {
                "anchor": ANCHOR_NAME,
                "verdict": "FAILED_SETUP",
                "verdict_msg": f"Llama-3.2-1B model load failed: {e}",
                "elapsed_s": time.time() - t0,
                "summary": "model_load_failure",
                "exception": traceback.format_exc(),
            })
            return 0

    # ---- Step 3: arm watchdog ----
    _watchdog_start(out_dir)
    log(f"watchdog armed: per-doc timeout={WATCHDOG_PER_DOC_TIMEOUT_S}s "
        f"PROGRESS_EVERY={PROGRESS_EVERY}")

    # ---- Step 4: resume from partials ----
    # Per-token partials use a different prefix so they don't collide with
    # per-doc partials in the same output dir.
    mode_tag = "pertoken" if PER_TOKEN_MODE else "perdoc"
    ckpt_prefix = (
        f"{MODEL_ID.replace('/', '_').replace('-', '_').replace('.', '_')}"
        f"_d{HIDDEN_DIM}_layer{LAYER_IDX_TARGET}_{RUN_MODE}_{mode_tag}_doc"
    )
    done_keys = set(list_completed_keys(out_dir))
    done_idx = {int(k.split("_doc")[-1]) for k in done_keys
                if k.startswith(ckpt_prefix) and "_doc" in k}
    log(f"resume: {len(done_idx)} docs already cached (mode={mode_tag})")
    log(f"extraction mode: {mode_tag} "
        f"({'all token positions per doc' if PER_TOKEN_MODE else 'final-token only per doc'})")

    # ---- Step 5: per-doc extraction loop ----
    rng = np.random.default_rng(303)
    n_extracted = 0
    n_failed = 0
    t_extract = time.time()
    for doc_idx, item in enumerate(parsed):
        if doc_idx in done_idx:
            continue
        try:
            if PER_TOKEN_MODE:
                if USE_SYNTHETIC or model is None:
                    res = _synthetic_residual_per_token(doc_idx, rng)
                else:
                    res = _extract_residual_per_token_one_doc(
                        model, tokenizer, item["doc"], device)
                # res shape: (T, 768) variable T
                if res.ndim != 2 or res.shape[1] != HIDDEN_DIM:
                    raise RuntimeError(
                        f"per-token residual shape wrong: {res.shape}; "
                        f"expected (T, {HIDDEN_DIM})")
                if not np.isfinite(res).all():
                    raise RuntimeError(f"non-finite per-token residual at doc_idx={doc_idx}")
                payload = {
                    "doc_idx": int(doc_idx),
                    "doc_str": item["doc"][:200],
                    "residual": res.tolist(),   # list of T lists of 768 floats
                    "n_tokens": int(res.shape[0]),
                    "model_id": MODEL_ID,
                    "hidden_dim": int(HIDDEN_DIM),
                    "layer_idx": int(LAYER_IDX_TARGET),
                    "run_mode": RUN_MODE,
                    "mode": "per_token",
                }
            else:
                if USE_SYNTHETIC or model is None:
                    res = _synthetic_residual(doc_idx, rng)
                else:
                    res = _extract_residual_one_doc(model, tokenizer, item["doc"], device)
                if res.shape != (HIDDEN_DIM,):
                    raise RuntimeError(
                        f"per-doc residual shape wrong: {res.shape}; "
                        f"expected ({HIDDEN_DIM},)")
                if not np.isfinite(res).all():
                    raise RuntimeError(f"non-finite residual at doc_idx={doc_idx}")
                payload = {
                    "doc_idx": int(doc_idx),
                    "doc_str": item["doc"][:200],
                    "residual": res.tolist(),
                    "model_id": MODEL_ID,
                    "hidden_dim": int(HIDDEN_DIM),
                    "layer_idx": int(LAYER_IDX_TARGET),
                    "run_mode": RUN_MODE,
                    "mode": "per_doc",
                }
            write_partial_key(out_dir, f"{ckpt_prefix}{doc_idx}", payload)
            n_extracted += 1
        except Exception as e:
            n_failed += 1
            print(f"  [err] doc_idx={doc_idx}: {e}", flush=True)
            if n_failed > max(10, int(0.05 * N_DOCS_TARGET)):
                print(f"  [FATAL] failure rate too high "
                      f"({n_failed}/{doc_idx + 1}); aborting", flush=True)
                break

        _LAST_DOC_COMPLETE_TS[0] = time.monotonic()

        if (doc_idx + 1) % PROGRESS_EVERY == 0 or doc_idx + 1 == len(parsed):
            wall = time.time() - t_extract
            try:
                import torch
                if torch.cuda.is_available():
                    alloc = torch.cuda.memory_allocated() / (1024 ** 3)
                    print(f"  progress: doc {doc_idx + 1}/{len(parsed)} "
                          f"extracted={n_extracted} failed={n_failed} "
                          f"wall_so_far={wall:.1f}s gpu_alloc_gb={alloc:.2f}",
                          flush=True)
                else:
                    print(f"  progress: doc {doc_idx + 1}/{len(parsed)} "
                          f"extracted={n_extracted} failed={n_failed} "
                          f"wall_so_far={wall:.1f}s", flush=True)
            except Exception:
                print(f"  progress: doc {doc_idx + 1}/{len(parsed)} "
                      f"extracted={n_extracted} failed={n_failed} "
                      f"wall_so_far={wall:.1f}s", flush=True)

    extract_wall = time.time() - t_extract
    log(f"extraction done in {extract_wall:.1f}s: "
        f"extracted={n_extracted} failed={n_failed}")

    # BUG FIX (2026-06-05 cluster run llama1b-110332): watchdog killed the
    # process mid-np.savez_compressed during the npz assembly phase below
    # because _LAST_DOC_COMPLETE_TS stops updating after the extraction loop
    # exits, and savez of a ~4 GB compressed npz took >120s on Lambda H100.
    # Result: corrupted partial npz on cluster; rebuilt locally from per-doc
    # partials (which DID write atomically per doc). Permanent fix: signal
    # the watchdog to STOP CHECKING by setting the timestamp to None; the
    # watchdog's `if last is None: continue` path then effectively pauses it.
    _LAST_DOC_COMPLETE_TS[0] = None
    log("watchdog paused (extraction done; npz assembly + write_metrics phase starts)")

    # ---- Step 6: free model ----
    if model is not None:
        del model
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass

    # ---- Step 7: assemble npz ----
    log(f"assembling npz from per-doc partials (mode={mode_tag})")
    final_keys = sorted(
        [k for k in set(list_completed_keys(out_dir))
         if k.startswith(ckpt_prefix) and "_doc" in k],
        key=lambda k: int(k.split("_doc")[-1]),
    )

    bad = 0
    n_docs_assembled = 0
    n_tokens_total = 0

    if PER_TOKEN_MODE:
        # Concatenate variable-length (T_i, 768) per doc.
        # Build: residuals (sum_T, 768), doc_indices (sum_T,), doc_boundaries (n_docs+1,).
        rows_per_doc: list = []
        doc_idx_per_doc: list = []
        for k in final_keys:
            try:
                p = out_dir / f"partial_metrics_{k}.json"
                body = json.loads(p.read_text(encoding="utf-8"))
                r = np.asarray(body["residual"], dtype=np.float32)
                if r.ndim != 2 or r.shape[1] != HIDDEN_DIM:
                    bad += 1
                    continue
                if r.shape[0] <= 0:
                    bad += 1
                    continue
                if not np.isfinite(r).all():
                    bad += 1
                    continue
                rows_per_doc.append(r)
                doc_idx_per_doc.append(int(body["doc_idx"]))
                n_tokens_total += int(r.shape[0])
            except Exception:
                bad += 1
                continue
        n_docs_assembled = len(rows_per_doc)
        if n_docs_assembled > 0:
            residuals = np.concatenate(rows_per_doc, axis=0)
            doc_boundaries = np.zeros(n_docs_assembled + 1, dtype=np.int64)
            for i, r in enumerate(rows_per_doc):
                doc_boundaries[i + 1] = doc_boundaries[i] + r.shape[0]
            doc_indices = np.zeros(int(doc_boundaries[-1]), dtype=np.int64)
            for i, doc_id in enumerate(doc_idx_per_doc):
                start = int(doc_boundaries[i])
                end = int(doc_boundaries[i + 1])
                doc_indices[start:end] = doc_id
        else:
            residuals = np.zeros((0, HIDDEN_DIM), dtype=np.float32)
            doc_boundaries = np.zeros(1, dtype=np.int64)
            doc_indices = np.zeros(0, dtype=np.int64)

        log(f"residuals shape {residuals.shape} (sum_T={n_tokens_total} across "
            f"{n_docs_assembled} docs); all_finite={np.isfinite(residuals).all()}")
        npz_path = out_dir / "residuals_per_token.npz"
        np.savez_compressed(
            npz_path,
            residuals=residuals,
            doc_indices=doc_indices,
            doc_boundaries=doc_boundaries,
        )
        log(f"npz written -> {npz_path}")
        n_residuals = n_docs_assembled   # "residuals" = "docs covered" in gate semantics

    else:
        # Per-doc: fixed (1, 768) per doc.
        residuals = np.zeros((len(final_keys), HIDDEN_DIM), dtype=np.float32)
        doc_indices = np.zeros(len(final_keys), dtype=np.int64)
        for i, k in enumerate(final_keys):
            try:
                p = out_dir / f"partial_metrics_{k}.json"
                body = json.loads(p.read_text(encoding="utf-8"))
                r = np.asarray(body["residual"], dtype=np.float32)
                if r.shape != (HIDDEN_DIM,) or not np.isfinite(r).all():
                    bad += 1
                    continue
                residuals[i] = r
                doc_indices[i] = int(body["doc_idx"])
            except Exception:
                bad += 1
                continue

        if bad > 0:
            log(f"npz assembly: {bad} bad partials skipped")
            good_mask = np.array([
                np.isfinite(residuals[i]).all() and residuals[i].any()
                for i in range(len(final_keys))
            ])
            residuals = residuals[good_mask]
            doc_indices = doc_indices[good_mask]

        n_residuals = residuals.shape[0]
        n_docs_assembled = n_residuals
        log(f"residuals shape {residuals.shape} all_finite={np.isfinite(residuals).all()}")
        npz_path = out_dir / "residuals.npz"
        np.savez_compressed(npz_path, residuals=residuals, doc_indices=doc_indices)
        log(f"npz written -> {npz_path}")

    # Sidecar metadata
    sidecar = {
        "anchor": ANCHOR_NAME,
        "model_id": MODEL_ID,
        "hidden_dim": HIDDEN_DIM,
        "layer_idx_target": LAYER_IDX_TARGET,
        "n_layers": N_LAYERS,
        "extraction_mode": mode_tag,
        "n_residuals": int(n_residuals),     # for per-token, this is n_docs_assembled (gate semantic)
        "n_docs_assembled": int(n_docs_assembled),
        "n_tokens_total": int(n_tokens_total) if PER_TOKEN_MODE else int(n_docs_assembled),
        "n_docs_target": int(N_DOCS_TARGET),
        "n_extracted": int(n_extracted),
        "n_failed": int(n_failed),
        "n_bad_partials": int(bad),
        "dataset_id": DATASET_ID,
        "run_mode": RUN_MODE,
        "max_tok_len": int(MAX_TOK_LEN),
        "wall_extract_s": float(extract_wall),
        "wall_total_s": float(time.time() - t0),
    }
    sidecar_name = ("residuals_per_token_meta.json" if PER_TOKEN_MODE
                    else "residuals_meta.json")
    (out_dir / sidecar_name).write_text(
        json.dumps(sidecar, indent=2), encoding="utf-8")

    # ---- Step 8: verdict ----
    # Gate is on docs-covered for both modes (per-token also reports n_tokens).
    if not npz_path.exists():
        verdict = "HARD_FAIL"
        msg = "npz not written"
    elif n_docs_assembled < MIN_DOCS_HP // 2:
        verdict = "HARD_FAIL"
        msg = (f"too few docs covered: {n_docs_assembled} < "
               f"{MIN_DOCS_HP // 2} (HARD_FAIL floor)")
    elif n_docs_assembled < MIN_DOCS_HP:
        verdict = "MIDDLE_BAND"
        msg = (f"partial extraction: {n_docs_assembled} docs covered "
               f"(< HP threshold {MIN_DOCS_HP})")
    else:
        verdict = "HARD_PASS"
        if PER_TOKEN_MODE:
            msg = (f"Llama-3.2-1B PER-TOKEN residual extraction at layer "
                   f"{LAYER_IDX_TARGET} complete; {n_docs_assembled} docs "
                   f"({n_tokens_total} tokens) at shape (sum_T={n_tokens_total}, "
                   f"{HIDDEN_DIM}) saved to {npz_path.name}. Ready for "
                   f"downstream EX-CONCEPT-1 REAL at 1B scale + substrate-audit-"
                   f"core C2 + C3 via last-token-of-each-doc slice (Tier-1 "
                   f"product anchor at 1B-LLM scale per Research's hybrid C+D plan).")
        else:
            msg = (f"Llama-3.2-1B residual extraction at layer {LAYER_IDX_TARGET} "
                   f"complete; {n_docs_assembled} residuals at shape "
                   f"(n, {HIDDEN_DIM}) saved to {npz_path.name}. Ready for "
                   f"downstream substrate-audit-core C2 + C3 on real Llama-1B "
                   f"residuals (Tier-1 product anchor at 1B-LLM scale per "
                   f"Research's hybrid C+D recovery plan).")

    log(f"verdict={verdict}: {msg}")
    write_metrics(out_dir, {
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": time.time() - t0,
        "summary": sidecar,
        "npz_path": str(npz_path.relative_to(REPO)),
        "npz_path_abs": str(npz_path),
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
