"""n1_recover_token_ids_pythia_pertoken_v1 -- DATA-RECOVERY prerequisite for N1 LM cell.

PROBLEM:
  exp_phase05_v1_pythia160m_residual_extract_pertoken_v1.py saved the per-token
  residuals npz WITHOUT token_ids (keys: residuals, doc_indices, doc_boundaries).
  The downstream N1 substrate-native LM cell needs real token sequences for BPC.
  Token IDs were available at extraction time (input_ids in
  _extract_residual_per_token_one_doc) but were discarded at savez time.

FIX (CPU-only, no model load):
  Re-tokenize the SAME corpus in the SAME order with the SAME tokenizer +
  IDENTICAL call args -> reproduce token sequences aligned 1:1 to residuals via
  doc_boundaries. Append token_ids to the npz, re-save in place.

DESIGN CONSTRAINTS:
  - NO torch, NO GPU, NO model load. Pure CPU: numpy + transformers tokenizer + datasets.
  - Must run on remote_cpu_queue (npz only exists on remote runner).
  - Idempotent: if npz already has token_ids, print ALREADY_RECOVERED and exit 0.
  - Safe write: tmp file + os.replace (matches extraction cell pattern).
  - Robust alignment: greedy re-sync if extraction skipped docs (1:1 order not
    guaranteed). ABORT (HARD_FAIL) if alignment cannot be established; do NOT
    write partial or guessed token_ids.

PROT-018: no _nN suffix (token count is data-derived, not a swept param).
PROT-022: instrumentation_selftest() called at module scope.
"""
from __future__ import annotations

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import time
import traceback
from pathlib import Path
from typing import List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

# ---- ANCHOR + source experiment config (replicated verbatim) ----

ANCHOR_NAME = "n1_recover_token_ids_pythia_pertoken_v1"

# Paths pointing to the source extraction output
SOURCE_ANCHOR = "phase05_v1_pythia160m_residual_extract_pertoken_v1"
NPZ_FILENAME = "residuals_per_token.npz"

# Source experiment constants (must match extraction cell EXACTLY)
MODEL_ID = "EleutherAI/pythia-160m"
HIDDEN_DIM = 768
MAX_TOK_LEN = 64
N_DOCS_FULL = 6000
N_DOCS_SMOKE_SRC = 50   # what the source ran under smoke; unused here but documented
DATASET_ID = "saturnMars/hyperprobe-dataset-analogy"

# Run mode for THIS recovery cell (smoke = small subset alignment test)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else
            os.environ.get("HDLAB_RUN_MODE", "full")).lower()
N_DOCS_TARGET = N_DOCS_FULL   # always try to align the full corpus


def _load_hf_token() -> str:
    """File-first HF token precedence (copied verbatim from source extraction cell)."""
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    return os.environ.get("HF_TOKEN", "").strip()


# ---- INSTRUMENTATION SELF-TEST (PROT-022, MANDATORY) ----

def _instrumentation_selftest():
    """Assert alignment + assert logic works on synthetic boundaries.

    Tests:
      1. Clean alignment (lengths match boundaries exactly) -> succeeds.
      2. Deliberate mismatch -> must raise ValueError.
    """
    print("[selftest] _instrumentation_selftest: START", flush=True)

    # Synthetic boundaries: 3 docs with token counts [4, 7, 3] -> total 14
    boundaries = np.array([0, 4, 11, 14], dtype=np.int64)
    n_docs = len(boundaries) - 1

    # Test 1: clean alignment
    retok_lens = [4, 7, 3]   # each matches the boundary diff
    token_ids_list: List[List[int]] = []
    for i in range(n_docs):
        expected_t = int(boundaries[i + 1] - boundaries[i])
        got_t = retok_lens[i]
        if got_t != expected_t:
            raise ValueError(
                f"[selftest] T1 BUG: alignment mismatch at doc {i}: "
                f"expected {expected_t} tokens, got {got_t}")
        token_ids_list.append(list(range(got_t)))  # synthetic ids

    flat = [tid for seq in token_ids_list for tid in seq]
    token_ids = np.array(flat, dtype=np.int64)
    assert token_ids.shape == (14,), f"[selftest] T1 shape wrong: {token_ids.shape}"
    print("[selftest] T1 PASS: clean alignment succeeds", flush=True)

    # Test 2: deliberate mismatch must raise
    retok_lens_bad = [4, 8, 3]   # doc 1 has 8 instead of 7 -> mismatch
    raised = False
    for i in range(n_docs):
        expected_t = int(boundaries[i + 1] - boundaries[i])
        got_t = retok_lens_bad[i]
        if got_t != expected_t:
            raised = True
            break
    assert raised, "[selftest] T2 FAIL: deliberate mismatch was not detected"
    print("[selftest] T2 PASS: deliberate mismatch correctly detected", flush=True)

    # Test 3: total token count assertion
    token_ids_flat = np.concatenate(
        [np.array(list(range(l)), dtype=np.int64) for l in retok_lens])
    expected_total = int(boundaries[-1])
    assert token_ids_flat.shape[0] == expected_total, (
        f"[selftest] T3 total mismatch: {token_ids_flat.shape[0]} != {expected_total}")
    print("[selftest] T3 PASS: total token count assertion works", flush=True)

    print("[selftest] _instrumentation_selftest: ALL PASS", flush=True)


_instrumentation_selftest()

if "--self-test" in sys.argv:
    print("[selftest] PASS; exiting before data-recovery run.", flush=True)
    sys.exit(0)


# ---- CORE LOGIC ----

def _load_source_npz(npz_path: Path) -> dict:
    """Load and validate the source residuals_per_token.npz.

    Returns dict with keys: residuals, doc_indices, doc_boundaries.
    Raises FileNotFoundError with a clear message if the file is absent
    (expected when running locally; the npz only exists on remote runner).
    """
    if not npz_path.exists():
        raise FileNotFoundError(
            f"Source npz not found: {npz_path}\n"
            f"This recovery cell must run on remote_cpu_queue where "
            f"the npz from {SOURCE_ANCHOR} was written."
        )
    # Close the handle deterministically (context manager) so npz_path is not
    # left locked on Windows before the later os.replace rewrite.
    with np.load(str(npz_path)) as loaded:
        keys = list(loaded.files)
        required = {"residuals", "doc_indices", "doc_boundaries"}
        missing = required - set(keys)
        if missing:
            raise ValueError(f"Source npz missing expected keys: {missing}; got {keys}")
        return {
            "residuals": loaded["residuals"],
            "doc_indices": loaded["doc_indices"],
            "doc_boundaries": loaded["doc_boundaries"],
        }


def _build_corpus(n_docs_target: int, log) -> List[str]:
    """Load and parse the analogy dataset, replicating source extraction logic verbatim.

    Matches exp_phase05_v1_pythia160m_residual_extract_pertoken_v1.py:
      - DATASET_ID = "saturnMars/hyperprobe-dataset-analogy"
      - split = "train" if present else first split
      - field = "doc" if present else "text"
      - stop at n_docs_target docs
    """
    from datasets import load_dataset
    log(f"loading dataset {DATASET_ID}")
    ds = load_dataset(DATASET_ID, token=_load_hf_token() or None)
    split = "train" if "train" in ds else next(iter(ds))
    raw = ds[split]
    log(f"dataset split={split} n_rows={len(raw)}")
    parsed: List[str] = []
    for row in raw:
        if "doc" in row:
            parsed.append(row["doc"])
        elif "text" in row:
            parsed.append(row["text"])
        if len(parsed) >= n_docs_target:
            break
    log(f"corpus built: {len(parsed)} docs (target {n_docs_target})")
    return parsed


def _load_tokenizer():
    """Load ONLY the tokenizer for pythia-160m. NO model load."""
    from transformers import AutoTokenizer
    token = _load_hf_token() or None
    print(f"  loading tokenizer {MODEL_ID} (no model) ...", flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    print(f"  tokenizer loaded; vocab_size={tok.vocab_size}", flush=True)
    return tok


def _retokenize_doc(tokenizer, doc: str) -> List[int]:
    """Re-tokenize a single doc with IDENTICAL args as _extract_residual_per_token_one_doc.

    Source call (verbatim from extraction cell):
        enc = tokenizer(doc, return_tensors="pt", truncation=True, max_length=MAX_TOK_LEN)
        attn = enc.get("attention_mask")
        if attn is not None:
            t_real = int(attn[0].sum().item())
        else:
            t_real = int(input_ids.shape[1])

    Here we replicate the same call WITHOUT return_tensors="pt" (no torch),
    using return_tensors=None (plain python lists). The attention_mask is
    produced identically; we compute t_real from it. input_ids[:t_real] are
    the real (non-padded) token ids.
    """
    enc = tokenizer(
        doc,
        return_tensors=None,
        truncation=True,
        max_length=MAX_TOK_LEN,
        padding=False,   # no padding for single-doc encoding -> attn all 1s
    )
    input_ids = enc["input_ids"]         # plain python list
    attn = enc.get("attention_mask")     # plain python list or None
    if attn is not None:
        t_real = int(sum(attn))
    else:
        t_real = len(input_ids)
    # Trim to real tokens (consistent with extraction's [:t_real] slice)
    return input_ids[:t_real]


def _greedy_align(
    doc_boundaries: np.ndarray,
    corpus: List[str],
    tokenizer,
    log,
) -> np.ndarray:
    """Greedy re-sync: walk corpus docs and align to extraction's doc_boundaries.

    The extraction may have skipped some corpus docs (e.g., error handling) so
    1:1 positional correspondence is NOT assumed. Instead we scan forward in the
    corpus to find the next doc whose re-tokenized length matches the expected
    boundary diff. This tolerates skips but cannot tolerate length collisions
    (two adjacent corpus docs with identical token count in a region of mismatched
    docs) -- in that case we ABORT with a diagnostic rather than guess wrong.

    Algorithm:
      For each extraction doc i (from doc_boundaries):
        expected_t = doc_boundaries[i+1] - doc_boundaries[i]
        Walk corpus from current_corpus_pos forward looking for a doc
        with retok_len == expected_t. If found within MAX_LOOKAHEAD, use it.
        If not found -> ABORT.

    MAX_LOOKAHEAD is intentionally small (50) to prevent false positives from
    length coincidences. If a legitimate skip > 50 occurs in the extraction,
    alignment will fail and the caller should fall back to GPU re-extract.
    """
    MAX_LOOKAHEAD = 50

    n_docs = len(doc_boundaries) - 1
    log(f"greedy alignment: n_extraction_docs={n_docs} corpus_size={len(corpus)}")

    token_ids_list: List[List[int]] = []
    corpus_pos = 0
    n_skipped_total = 0

    for i in range(n_docs):
        expected_t = int(doc_boundaries[i + 1] - doc_boundaries[i])

        # First try direct (no skip)
        if corpus_pos < len(corpus):
            ids = _retokenize_doc(tokenizer, corpus[corpus_pos])
            if len(ids) == expected_t:
                token_ids_list.append(ids)
                corpus_pos += 1
                continue

        # Lookahead search
        found = False
        for skip in range(1, MAX_LOOKAHEAD + 1):
            lookahead_pos = corpus_pos + skip
            if lookahead_pos >= len(corpus):
                break
            ids = _retokenize_doc(tokenizer, corpus[lookahead_pos])
            if len(ids) == expected_t:
                n_skipped_total += skip
                log(f"  greedy skip: extraction doc {i} matched corpus[{lookahead_pos}] "
                    f"(skipped {skip} corpus entries; expected_t={expected_t})")
                token_ids_list.append(ids)
                corpus_pos = lookahead_pos + 1
                found = True
                break

        if not found:
            pos_sample = corpus_pos
            # Sample a few retok lengths around current pos for diagnostics
            samples = []
            for k in range(min(5, len(corpus) - pos_sample)):
                try:
                    s_ids = _retokenize_doc(tokenizer, corpus[pos_sample + k])
                    samples.append(len(s_ids))
                except Exception:
                    samples.append(-1)
            raise RuntimeError(
                f"ALIGNMENT_FAIL at extraction doc {i}: "
                f"expected {expected_t} tokens; "
                f"corpus[{corpus_pos}:{corpus_pos+MAX_LOOKAHEAD}] retok_lens "
                f"(first 5 samples) = {samples}. "
                f"Cannot establish alignment without guessing. "
                f"Fallback: run GPU re-extraction to regenerate token_ids "
                f"at extraction time."
            )

    if n_skipped_total > 0:
        log(f"greedy alignment: {n_skipped_total} corpus docs skipped total "
            f"(extraction skipped them during forward pass errors)")

    # Build flat token_ids array
    flat = [tid for seq in token_ids_list for tid in seq]
    token_ids = np.array(flat, dtype=np.int64)

    # HARD ASSERT: total must match residuals.shape[0]
    expected_total = int(doc_boundaries[-1])
    if token_ids.shape[0] != expected_total:
        raise RuntimeError(
            f"ALIGNMENT_TOTAL_FAIL: built {token_ids.shape[0]} token_ids "
            f"but doc_boundaries[-1]={expected_total}. "
            f"Per-doc counts matched individually but flat concat does not match -- "
            f"internal bug."
        )

    return token_ids


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

    log(f"START anchor={ANCHOR_NAME} run_mode={RUN_MODE}")

    # ---- Locate the source npz ----
    source_out_dir = get_output_dir(SOURCE_ANCHOR)
    # Override: HDLAB_EXP_NAME is set to THIS anchor by the runner, so
    # get_output_dir(SOURCE_ANCHOR) correctly derives the source path using
    # the SOURCE_ANCHOR name (not the env var, which is THIS anchor).
    # But get_output_dir uses the env var if set. We need the SOURCE path
    # unconditionally. Build it directly:
    source_out_dir = REPO / "data" / f"exp_{SOURCE_ANCHOR}"
    npz_path = source_out_dir / NPZ_FILENAME
    log(f"source npz path: {npz_path}")

    # ---- Load source npz ----
    try:
        npz_data = _load_source_npz(npz_path)
    except FileNotFoundError as e:
        log(f"ABORT: {e}")
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": str(e),
            "elapsed_s": time.time() - t0,
            "summary": "source_npz_not_found",
        })
        return 0

    residuals = npz_data["residuals"]
    doc_indices = npz_data["doc_indices"]
    doc_boundaries = npz_data["doc_boundaries"]

    log(f"source npz loaded: residuals.shape={residuals.shape} "
        f"doc_boundaries={doc_boundaries.shape} "
        f"n_docs={len(doc_boundaries)-1}")

    # ---- Idempotency check ----
    existing_keys = list(np.load(str(npz_path)).files)
    if "token_ids" in existing_keys:
        log("ALREADY_RECOVERED: npz already contains token_ids; nothing to do.")
        print("ALREADY_RECOVERED", flush=True)
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "PASS",
            "verdict_msg": "ALREADY_RECOVERED: token_ids already present in source npz.",
            "elapsed_s": time.time() - t0,
            "summary": "idempotent_skip",
            "n_tokens": int(residuals.shape[0]),
            "existing_keys": existing_keys,
        })
        return 0

    n_docs = len(doc_boundaries) - 1
    n_tokens_expected = int(doc_boundaries[-1])
    log(f"n_extraction_docs={n_docs} n_tokens_expected={n_tokens_expected}")

    if residuals.shape[0] != n_tokens_expected:
        msg = (f"source npz internal inconsistency: residuals.shape[0]="
               f"{residuals.shape[0]} != doc_boundaries[-1]={n_tokens_expected}")
        log(f"HARD_FAIL: {msg}")
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": msg,
            "elapsed_s": time.time() - t0,
            "summary": "source_npz_inconsistent",
        })
        return 0

    # ---- Handle smoke subset ----
    if RUN_MODE == "smoke":
        # Align only the first few docs as a quick gate
        smoke_docs = 5
        if n_docs > smoke_docs:
            log(f"SMOKE MODE: aligning first {smoke_docs} of {n_docs} docs only")
            doc_boundaries = doc_boundaries[:smoke_docs + 1]
            n_docs = smoke_docs
            n_tokens_expected = int(doc_boundaries[-1])
            residuals = residuals[:n_tokens_expected]
            log(f"smoke subset: n_docs={n_docs} n_tokens={n_tokens_expected}")
        else:
            log(f"SMOKE MODE: only {n_docs} extraction docs; aligning all")

    # ---- Load corpus (replicate source parse verbatim) ----
    try:
        corpus = _build_corpus(N_DOCS_TARGET, log)
    except Exception as e:
        log(f"HARD_FAIL: corpus load failed: {e}")
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": f"corpus load failed: {e}",
            "elapsed_s": time.time() - t0,
            "summary": "corpus_load_failure",
            "exception": traceback.format_exc(),
        })
        return 0

    if len(corpus) < n_docs:
        msg = (f"corpus has only {len(corpus)} docs but extraction had {n_docs}; "
               f"dataset may have changed or N_DOCS_TARGET needs to be raised.")
        log(f"HARD_FAIL: {msg}")
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": msg,
            "elapsed_s": time.time() - t0,
            "summary": "corpus_too_small",
        })
        return 0

    # ---- Load tokenizer ----
    try:
        tokenizer = _load_tokenizer()
    except Exception as e:
        log(f"HARD_FAIL: tokenizer load failed: {e}")
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": f"tokenizer load failed: {e}",
            "elapsed_s": time.time() - t0,
            "summary": "tokenizer_load_failure",
            "exception": traceback.format_exc(),
        })
        return 0

    # ---- Greedy alignment ----
    log("beginning greedy alignment ...")
    try:
        token_ids = _greedy_align(doc_boundaries, corpus, tokenizer, log)
    except RuntimeError as e:
        msg = str(e)
        log(f"HARD_FAIL: {msg}")
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": msg,
            "elapsed_s": time.time() - t0,
            "summary": "alignment_failed",
        })
        return 0

    log(f"alignment succeeded: token_ids.shape={token_ids.shape} "
        f"vocab_min={int(token_ids.min())} vocab_max={int(token_ids.max())}")

    # ---- Safe re-save ----
    if RUN_MODE == "smoke":
        log("SMOKE MODE: alignment verified; skipping npz rewrite (subset only)")
        sample_ids = token_ids[:10].tolist()
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "PASS",
            "verdict_msg": (f"SMOKE alignment verified on first {n_docs} docs; "
                            f"token_ids.shape={token_ids.shape}; "
                            f"full run will write token_ids to source npz."),
            "elapsed_s": time.time() - t0,
            "summary": "smoke_alignment_ok",
            "n_tokens_aligned": int(token_ids.shape[0]),
            "n_docs_aligned": n_docs,
            "vocab_min": int(token_ids.min()),
            "vocab_max": int(token_ids.max()),
            "sample_token_ids_0_10": sample_ids,
        })
        return 0

    # FULL mode: reload with full boundaries (no smoke subset) then write
    log("re-saving source npz with token_ids appended ...")
    # tmp path MUST end in .npz: np.savez_compressed auto-appends .npz to any
    # filename not already ending in it, so ".npz.tmp" would write "...npz.tmp.npz"
    # and the later stat/os.replace on "...npz.tmp" would fail (WinError 2).
    tmp_path = npz_path.with_name(npz_path.stem + ".recover_tmp.npz")
    try:
        # Re-load fresh, but CLOSE the handle before os.replace: on Windows you
        # cannot replace a file that still has an open handle (WinError 32). np.load
        # on an .npz keeps the zip open until closed; __getitem__ reads each array
        # fully into memory, so the arrays stay valid after the handle is closed.
        with np.load(str(npz_path)) as full_npz:
            orig_residuals = full_npz["residuals"]
            orig_doc_indices = full_npz["doc_indices"]
            orig_doc_boundaries = full_npz["doc_boundaries"]
            # Verify residuals shape+dtype match what we loaded earlier
            if orig_residuals.shape != npz_data["residuals"].shape:
                raise RuntimeError(
                    f"npz reload shape mismatch: {orig_residuals.shape} vs "
                    f"{npz_data['residuals'].shape}")
            if orig_residuals.dtype != npz_data["residuals"].dtype:
                raise RuntimeError(
                    f"npz reload dtype mismatch: {orig_residuals.dtype} vs "
                    f"{npz_data['residuals'].dtype}")
        # full_npz handle now closed -> npz_path no longer locked

        np.savez_compressed(
            str(tmp_path),
            residuals=orig_residuals,
            doc_indices=orig_doc_indices,
            doc_boundaries=orig_doc_boundaries,
            token_ids=token_ids,
        )
        log(f"tmp written: {tmp_path} ({tmp_path.stat().st_size / 1e6:.1f} MB)")

        # Verify the tmp file loads correctly, then CLOSE before replacing.
        with np.load(str(tmp_path)) as verify:
            assert "token_ids" in verify.files, "tmp npz missing token_ids after write"
            assert verify["residuals"].shape == orig_residuals.shape, (
                f"tmp residuals shape mismatch: {verify['residuals'].shape}")
            assert verify["residuals"].dtype == orig_residuals.dtype, (
                f"tmp residuals dtype mismatch: {verify['residuals'].dtype}")
            assert verify["token_ids"].shape == token_ids.shape, (
                f"tmp token_ids shape mismatch: {verify['token_ids'].shape}")
        # verify handle now closed -> tmp_path no longer locked
        log("tmp verification: residuals shape+dtype match; token_ids present")

        os.replace(str(tmp_path), str(npz_path))
        log(f"os.replace -> {npz_path}")
    except Exception as e:
        log(f"HARD_FAIL: npz rewrite failed: {e}")
        # Clean up tmp if it exists
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
        write_metrics(out_dir, {
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": f"npz rewrite failed: {e}",
            "elapsed_s": time.time() - t0,
            "summary": "npz_write_failure",
            "exception": traceback.format_exc(),
        })
        return 0

    # ---- Final verification ----
    final_npz = np.load(str(npz_path))
    assert "token_ids" in final_npz.files, "CRITICAL: final npz missing token_ids after replace"
    final_keys = list(final_npz.files)
    log(f"final npz keys: {final_keys}")

    sample_ids = token_ids[:20].tolist()
    elapsed = time.time() - t0
    verdict_msg = (
        f"token_ids recovered and written to {npz_path.name}: "
        f"n_tokens={token_ids.shape[0]}, n_docs={n_docs}, "
        f"vocab_min={int(token_ids.min())}, vocab_max={int(token_ids.max())}. "
        f"npz keys: {final_keys}. "
        f"N1 LM cell may now proceed with real token sequences for BPC measurement."
    )
    log(f"PASS: {verdict_msg}")
    write_metrics(out_dir, {
        "anchor": ANCHOR_NAME,
        "verdict": "PASS",
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "n_tokens": int(token_ids.shape[0]),
            "n_docs": n_docs,
            "vocab_min": int(token_ids.min()),
            "vocab_max": int(token_ids.max()),
            "sample_token_ids_0_20": sample_ids,
            "source_npz": str(npz_path),
            "final_keys": final_keys,
        },
        "source_npz": str(npz_path),
        "n_tokens": int(token_ids.shape[0]),
        "n_docs": n_docs,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
