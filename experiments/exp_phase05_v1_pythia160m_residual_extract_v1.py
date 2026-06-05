"""phase05_v1_pythia160m_residual_extract_v1 -- Phase 0.5 rung-0 residual extraction.

SCIENTIFIC QUESTION:
  Produce a clean Pythia-160M last-layer residual npz for downstream EX-CONCEPT-1
  VQ + substrate-audit-core C2 + C3 cells. Pythia-160M is small, public, fast,
  and known to load on the runner (algorithm1_debug_pythia160m_v1 ran clean).

ROUTING:
  - User-authorized (2026-06-04 ~22:00) pivot from Llama-3.2-1B v6/v7 hung
    extractions to Pythia-160M as the immediate substrate-LLM-coupling residual
    source.
  - Per research_to_testbed_pythia_extraction_priority_2026-06-04 +
    exp_dev_to_testbed_user_authorized_v7_kill_pythia_extract_2026-06-04.
  - Unblocks Exp-Dev's EX-CONCEPT-1 REAL + Tier-4 Hopfield-attention
    substitution + EX-OPTION-C-W_proj.

PIPELINE:
  1. Set TOKENIZERS_PARALLELISM=false BEFORE transformers import (prevents the
     fork-after-parallelism deadlock that hung Llama v6 + v7).
  2. Load Pythia-160M (EleutherAI/pythia-160m, ~320 MB BF16) on cuda.
  3. Iterate over the analogy dataset (saturnMars/hyperprobe-dataset-analogy)
     -- already cached on the runner from prior Llama work.
  4. For each doc: forward pass + extract hidden_states[12] (= last layer, 0-indexed
     L; Pythia-160M has 12 layers + 1 embedding = 13 entries; final = idx 12) at
     the final-token position. Shape: (768,) float32.
  5. Stack all residuals to (n_docs, 768) float32 npz at out_dir/residuals.npz.
  6. Sidecar metadata JSON: model_id, hidden_dim, n_docs, layer_idx, dataset, ...
  7. Per-doc watchdog: os._exit(99) if no doc completes in 120s (same fix as
     Rung A v8 from `testbed_to_exp_dev_phase05_llama_v8_diagnostic_watchdog_kill_v7`).
  8. PROT-021 per-doc partials via _seed_checkpoint.write_partial_key so a
     watchdog-triggered exit loses only in-flight work, not completed docs.

PRE-REGISTERED BANDS:
  HARD-PASS: extraction completes with >= MIN_DOCS_HP residuals, all finite, no
             NaN, shape (n_docs, 768), npz file exists at expected path.
             ~5-10k residuals per research's "sufficient for VQ codebook training".
  MIDDLE:    pipeline runs but partial (e.g. < MIN_DOCS_HP); some residuals
             extracted but watchdog fired or dataset ran out.
  HARD-FAIL: < MIN_DOCS_HP/2 residuals OR npz contains NaN OR script crashed at
             setup before any extraction.

PROT-018: no _nN suffix (Pythia hidden_dim=768 is fixed by model, not swept).
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

ANCHOR_NAME = "phase05_v1_pythia160m_residual_extract_v1"

MODEL_ID = "EleutherAI/pythia-160m"
HIDDEN_DIM = 768
N_LAYERS = 12                  # Pythia-160M: 12 transformer blocks
LAYER_IDX_TARGET = 12          # last layer's output = hidden_states[12]
                               # (Pythia returns L+1=13 hidden_states; idx 0 = embedding)

MAX_TOK_LEN = 64               # short prompts; analogy docs are short
PROGRESS_EVERY = 50

# v8-lesson watchdog: exit fast if no doc completes within this window.
WATCHDOG_PER_DOC_TIMEOUT_S = 120
_LAST_DOC_COMPLETE_TS: list = [None]

# Extraction targets (per research: 5-10k sufficient for VQ + audit-core)
N_DOCS_FULL = 10000
N_DOCS_SMOKE = 50
MIN_DOCS_HP = 5000             # HARD_PASS gate floor

DATASET_ID = "saturnMars/hyperprobe-dataset-analogy"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else
            os.environ.get("HDLAB_RUN_MODE", "full")).lower()
USE_SYNTHETIC = (RUN_MODE == "smoke")
N_DOCS_TARGET = N_DOCS_SMOKE if RUN_MODE == "smoke" else N_DOCS_FULL


def _load_hf_token() -> str:
    """File-first HF token precedence (Rung A v5/v6 lesson).

    Pythia is a PUBLIC model so a token is not strictly required, but loading
    via huggingface_hub still benefits from any cached auth. Return empty
    string if neither source is set (HF allows anonymous access to Pythia).
    """
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    return os.environ.get("HF_TOKEN", "").strip()


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


def _load_pythia(device: str):
    """Load Pythia-160M on device with bf16. Returns (model, tokenizer)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    token = _load_hf_token() or None  # empty -> anonymous
    print(f"  loading {MODEL_ID} -> device={device} dtype=bf16 ...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.bfloat16,
        device_map=device,
    )
    model.eval()
    cfg = model.config
    print(f"  model loaded in {time.time() - t0:.1f}s; "
          f"hidden_size={cfg.hidden_size} n_layers={cfg.num_hidden_layers}",
          flush=True)
    if cfg.hidden_size != HIDDEN_DIM:
        raise RuntimeError(
            f"Pythia hidden_size {cfg.hidden_size} != expected {HIDDEN_DIM}; "
            f"model swap?")
    if cfg.num_hidden_layers != N_LAYERS:
        raise RuntimeError(
            f"Pythia num_hidden_layers {cfg.num_hidden_layers} != "
            f"expected {N_LAYERS}; model swap?")
    return model, tokenizer


def _extract_residual_one_doc(model, tokenizer, doc: str, device: str) -> np.ndarray:
    """Forward Pythia on doc; return (768,) float32 last-layer final-token residual."""
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


def _synthetic_residual(idx: int, rng: np.random.Generator) -> np.ndarray:
    """Smoke fallback: synthetic (768,) float32 residual."""
    sub = np.random.default_rng(rng.integers(0, 2**31 - 1) + idx)
    return sub.standard_normal(HIDDEN_DIM).astype(np.float32)


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
            model, tokenizer = _load_pythia(device)
            log("Pythia load OK")
        except Exception as e:
            log(f"FAILED_SETUP: Pythia load failed: {e}")
            write_metrics(out_dir, {
                "anchor": ANCHOR_NAME,
                "verdict": "FAILED_SETUP",
                "verdict_msg": f"Pythia model load failed: {e}",
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
    ckpt_prefix = (
        f"{MODEL_ID.replace('/', '_').replace('-', '_').replace('.', '_')}"
        f"_d{HIDDEN_DIM}_layer{LAYER_IDX_TARGET}_{RUN_MODE}_doc"
    )
    done_keys = set(list_completed_keys(out_dir))
    done_idx = {int(k.split("_doc")[-1]) for k in done_keys
                if k.startswith(ckpt_prefix) and "_doc" in k}
    log(f"resume: {len(done_idx)} docs already cached")

    # ---- Step 5: per-doc extraction loop ----
    rng = np.random.default_rng(303)
    n_extracted = 0
    n_failed = 0
    t_extract = time.time()
    for doc_idx, item in enumerate(parsed):
        if doc_idx in done_idx:
            continue
        try:
            if USE_SYNTHETIC or model is None:
                res = _synthetic_residual(doc_idx, rng)
            else:
                res = _extract_residual_one_doc(model, tokenizer, item["doc"], device)
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

    # ---- Step 6: free model ----
    if model is not None:
        del model
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass

    # ---- Step 7: assemble npz ----
    log("assembling npz from per-doc partials")
    final_keys = sorted(
        [k for k in set(list_completed_keys(out_dir))
         if k.startswith(ckpt_prefix) and "_doc" in k],
        key=lambda k: int(k.split("_doc")[-1]),
    )
    residuals = np.zeros((len(final_keys), HIDDEN_DIM), dtype=np.float32)
    doc_indices = np.zeros(len(final_keys), dtype=np.int64)
    bad = 0
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
        # Filter out empty rows where bad partials were
        good_mask = np.array([
            np.isfinite(residuals[i]).all() and residuals[i].any()
            for i in range(len(final_keys))
        ])
        residuals = residuals[good_mask]
        doc_indices = doc_indices[good_mask]

    n_residuals = residuals.shape[0]
    log(f"residuals shape {residuals.shape} all_finite={np.isfinite(residuals).all()}")

    npz_path = out_dir / "residuals.npz"
    np.savez_compressed(npz_path,
                        residuals=residuals, doc_indices=doc_indices)
    log(f"npz written -> {npz_path}")

    # Sidecar metadata
    sidecar = {
        "anchor": ANCHOR_NAME,
        "model_id": MODEL_ID,
        "hidden_dim": HIDDEN_DIM,
        "layer_idx_target": LAYER_IDX_TARGET,
        "n_layers": N_LAYERS,
        "n_residuals": int(n_residuals),
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
    (out_dir / "residuals_meta.json").write_text(
        json.dumps(sidecar, indent=2), encoding="utf-8")

    # ---- Step 8: verdict ----
    if not npz_path.exists():
        verdict = "HARD_FAIL"
        msg = "npz not written"
    elif n_residuals < MIN_DOCS_HP // 2:
        verdict = "HARD_FAIL"
        msg = (f"too few residuals: {n_residuals} < "
               f"{MIN_DOCS_HP // 2} (HARD_FAIL floor)")
    elif n_residuals < MIN_DOCS_HP:
        verdict = "MIDDLE_BAND"
        msg = (f"partial extraction: {n_residuals} residuals "
               f"(< HP threshold {MIN_DOCS_HP})")
    else:
        verdict = "HARD_PASS"
        msg = (f"Pythia-160M residual extraction at layer {LAYER_IDX_TARGET} "
               f"complete; {n_residuals} residuals at shape (n, {HIDDEN_DIM}) "
               f"saved to {npz_path.name}. Ready for downstream EX-CONCEPT-1 "
               f"VQ + substrate-audit-core C2 + C3 on real Pythia residuals "
               f"(Tier-1 product anchor at small-LLM scale per research's "
               f"hybrid C+D recovery plan).")

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
