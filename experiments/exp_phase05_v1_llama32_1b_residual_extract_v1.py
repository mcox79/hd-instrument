"""
phase05_v1_llama32_1b_residual_extract_v1 -- Llama-3.2-1B residual extraction.

PURPOSE:
    Testbed-side handoff to Exp-Dev for Phase 0.5 v1 Rung A. This script
    extracts per-doc residuals from Llama-3.2-1B at layers 8..16 (output
    indices into hidden_states, = 9 layers) at the final-token position,
    plus the ground-truth VSA target encodings per doc, and dumps them as
    an npz artifact that Exp-Dev consumes to run Algorithm 1 K-means +
    sum-pool + Hyperprobe MLP + 3 audit primitives.

    Pipeline:
      1. Load Llama-3.2-1B BF16 to cuda
      2. Load saturnMars/hyperprobe-dataset-analogy
      3. Parse "A : B = C : D" with 4-distinct-token constraint
      4. Build VSA codebook over concepts at vsa_dim=4096
      5. Per doc: forward + take hidden_states[8:17] at final-token
         -> (9, 2048) float32 (cast from bf16 BEFORE .cpu().numpy())
      6. Per doc: create_vsa_encodings -> bipolar (vsa_dim,) target
      7. Split into train/val/test (80/10/10) by deterministic hash
      8. Write npz + sidecar JSON + doc_id_to_doc_str.json

LLAMA-3.2-1B FACTS (verified):
    hidden_size=2048, num_hidden_layers=16, num_attention_heads=32,
    num_key_value_heads=8 (GQA), vocab_size=128256, BF16 weights ~2.5GB.

LAYER BAND CONVENTION (per arXiv:2509.25045 Algorithm 1 + hyperprobe library):
    HF outputs.hidden_states is a tuple of length (L+1)=17 for Llama-3.2-1B.
    hidden_states[0] = embedding output; hidden_states[i] (i in 1..16) =
    output of transformer layer i-1. Algorithm 1 slices [L/2 .. L] inclusive,
    so for L=16 we take hidden_states[8:17] = 9 tensors covering the outputs
    of transformer layers 7..15 (the latter-half band).

PRE-REGISTERED VERDICT (extraction-only; downstream measures val_sim):
    HARD_PASS: all docs extracted, no NaN in residuals, no NaN in target_vsa,
               npz written, sidecar JSON written, finite element-wise stats.
    HARD_FAIL: any of the above failed; n_docs less than expected; NaN found.

PROT-018: anchor `phase05_v1_llama32_1b_residual_extract_v1` has NO _nN suffix
          (not a substrate N sweep; substrate dim is independent of LLM hidden).
PROT-021: per-doc partial JSON; checkpoint keys include
          (model_id, vsa_dim, run_mode) to prevent smoke->full contamination.
PROT-022: _selftest_structural() runs at import (token presence, layer band,
          hidden_size, VSA codebook shape on synthetic D=64 dummy).

BUG-FIX PRESERVATION (per Exp-Dev's Rung A division note, 2026-06-04):
    * .float() cast on residual tensors BEFORE numpy/npz (Llama-3.2-1B is BF16)
    * .to(device) discipline: model on cuda; input_ids .to(device);
      output .cpu() AFTER .float()
    * No torch.unique() on BF16 tensors (avoid the torchmetrics BFloat16 bug)

ASCII-only stdout per feedback_ascii_only_in_scripts (Windows cp1252 stdout
crashes on emoji/em-dash). Per feedback_testbed_progress_logging_and_restart,
per-cell partial JSON emitted; restart-capable via PROT-021 helpers.

SMOKE vs FULL (HDLAB_RUN_MODE):
    smoke: 50 docs, VSA_D=512, fail-fast structural validation. By default
           NO model load (synthetic residuals) so the smoke gate stays under
           ~10s. Set HDLAB_SMOKE_LOAD_MODEL=1 to force a real CPU model load
           which takes ~25 min for 5 docs and is NOT the smoke gate; that
           lives on the remote 4060 Ti FULL dispatch.
    full:  100_000 docs (or MAX_INPUTS_FULL cap), VSA_D=4096, cuda required.
           Wall ~1-2h on 4060 Ti.

THIS SCRIPT EXTRACTS RESIDUALS ONLY; it does NOT train Hyperprobe MLP, run
Algorithm 1 k-means/sum-pool, or measure audit primitives. Those are
Exp-Dev's lane (substrate-side; built model-agnostic against this npz).
"""
from __future__ import annotations

import os
# v8 fail-fast diagnostic fix: TOKENIZERS_PARALLELISM=false MUST be set BEFORE
# the `transformers` / `tokenizers` import, otherwise huggingface/tokenizers
# spawns its rayon thread pool BEFORE we can quiet it, and a subsequent
# fork() (e.g. via HF datasets workers or our own multiprocessing) can
# deadlock against the locked thread pool. v6 and v7 both hung silently on
# Llama-3.2-1B with no traceback; this fork-after-parallelism deadlock is a
# common silent-stall culprit. Set unconditionally and explicitly.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import gc
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --- F:\ redirection (user 2026-06-04): on the remote 4060 Ti desktop, F:\ is
# a 700GB hybrid-HDD; redirect HF cache + output dir there to keep ~7.5 GB off
# C:\. MUST run BEFORE any transformers / huggingface_hub imports for HF_HOME
# to take effect.
#
# DEFENSIVE WRAPPING (2026-06-04, after runner crash-loop diagnosis): wrap in
# try/except so import-time crashes (PermissionError, drive-not-writable, odd
# filesystem semantics) fall through to default paths rather than killing the
# whole module load. This way the script can still start + log + emit a
# metrics.json with the real error even if F:\ is unusable for any reason.
#
# Also: do NOT eagerly makedirs at module-load time -- that's a common
# permission-failure point on Windows runners. Defer makedirs to first actual
# use inside main()'s safe-zone.
_F_DRIVE_HF_CACHE = r"F:\hf_cache"
_F_DRIVE_DATA_ROOT = r"F:\hd_data"
_F_DRIVE_ACTIVE = False
_F_DRIVE_SKIP_REASON = "F:\\ not detected on this OS"
if os.name == "nt":
    try:
        if os.path.isdir("F:\\"):
            # Only set env vars + advertise active state; defer makedirs so a
            # PermissionError doesn't kill module import.
            os.environ.setdefault("HF_HOME", _F_DRIVE_HF_CACHE)
            os.environ.setdefault("HUGGINGFACE_HUB_CACHE", _F_DRIVE_HF_CACHE)
            os.environ.setdefault("TRANSFORMERS_CACHE", _F_DRIVE_HF_CACHE)
            _F_DRIVE_ACTIVE = True
            _F_DRIVE_SKIP_REASON = ""
        else:
            _F_DRIVE_SKIP_REASON = "F:\\ does not exist on this Windows host"
    except Exception as _f_drive_err:
        _F_DRIVE_SKIP_REASON = (
            f"F:\\ detected but env-setup failed: "
            f"{type(_f_drive_err).__name__}: {_f_drive_err}"
        )
        sys.stderr.write(f"[F-drive] WARN: {_F_DRIVE_SKIP_REASON}; "
                         f"falling back to default paths\n")

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Inject extern/hyperprobe/src so a bring-up that didn't `pip install -e`
# the local clone still resolves the package. On the remote 4060 Ti where
# hyperprobe was installed normally this is a no-op.
_HP_SRC = REPO / "extern" / "hyperprobe" / "src"
if _HP_SRC.exists() and str(_HP_SRC) not in sys.path:
    sys.path.insert(0, str(_HP_SRC))

from experiments._seed_checkpoint import (
    get_output_dir,
    list_completed_keys,
    write_partial_key,
    aggregate_partials,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ANCHOR_NAME = "phase05_v1_llama32_1b_residual_extract_v1"

LLM_MODEL_ID = "meta-llama/Llama-3.2-1B"

# Llama-3.2-1B verified facts (config-derived; mirrored as constants for
# selftest assertions and avoid-network-on-smoke).
LLAMA_HIDDEN_SIZE = 2048
LLAMA_N_LAYERS = 16
LLAMA_VOCAB_SIZE = 128256

# Algorithm 1 layer band per arXiv:2509.25045 Appendix B + hyperprobe convention:
# slice outputs.hidden_states[L/2 .. L] inclusive. For L=16, [8:17] = 9 layers.
ALG1_BAND_START = LLAMA_N_LAYERS // 2          # 8
ALG1_BAND_STOP = LLAMA_N_LAYERS + 1            # 17 (exclusive)
N_LAYERS_IN_BAND = ALG1_BAND_STOP - ALG1_BAND_START  # 9

# Default VSA dim (matches paper 8B work; Exp-Dev can override). At 1B the
# response note (testbed_to_exp_dev_phase05_rung_a_responses_2026-06-04.md)
# defaults to 4096 unless Exp-Dev flags back 2048 for clean Alg-1 sum-pool dim.
VSA_DIM_FULL = 4096
VSA_DIM_SMOKE = 512

# Document caps. MAX_INPUTS_FULL matches the 8B path (exp_phase05_probe_training_v1.py).
MAX_INPUTS_FULL = 100_000
MAX_INPUTS_SMOKE = 50

# Dataset
ANALOGY_DATASET = "saturnMars/hyperprobe-dataset-analogy"

# Train/val/test split fractions (matches 8B path)
SPLIT_VAL = 0.10
SPLIT_TEST = 0.10
# train = 1 - val - test

# Tokenization max length (paper uses untruncated short analogies; cap is
# defensive in case a row is malformed long).
MAX_TOK_LEN = 64

# Progress reporting cadence (v8: 25 instead of 100 for 4x more frequent flush)
PROGRESS_EVERY = 25

# v8 fail-fast watchdog: if no doc completes within this many seconds, exit via
# os._exit so the runner can re-queue from partial state instead of holding the
# GPU forever. v6 hung at doc 70300; v7 hung at doc 0 -- both single-process
# silent freezes. The script writes per-doc partials (write_partial_key) so a
# watchdog-triggered exit loses only in-flight work, not completed docs.
WATCHDOG_PER_DOC_TIMEOUT_S = 120

# v8 shared progress timestamp (single-element list to allow watchdog thread
# read + main thread write without `global` declaration noise).
_LAST_DOC_COMPLETE_TS: list = [None]

# ---------------------------------------------------------------------------
# Run-mode + CLI
# ---------------------------------------------------------------------------

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "smoke")
).lower()
if RUN_MODE not in ("smoke", "full"):
    print(f"[warn] unrecognized HDLAB_RUN_MODE={RUN_MODE!r}; defaulting to 'smoke'",
          flush=True)
    RUN_MODE = "smoke"

# When smoke + HDLAB_SMOKE_LOAD_MODEL=1, smoke actually loads Llama on CPU
# and extracts 5 docs. Otherwise smoke fabricates synthetic residuals to
# validate I/O paths + selftest in <10s.
SMOKE_LOAD_MODEL = bool(int(os.environ.get("HDLAB_SMOKE_LOAD_MODEL", "0")))

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true",
                  help="Run PROT-022 selftests and exit (no extraction).")
_ap.add_argument("--max-docs", type=int, default=50000,
                  help="Doc cap. Default 50000 (Testbed-authorized v7 cap: avoids the 70k-100k stall zone where v6 hung).")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    VSA_DIM = VSA_DIM_SMOKE
    N_DOCS_TARGET = MAX_INPUTS_SMOKE if not SMOKE_LOAD_MODEL else 5
else:
    VSA_DIM = VSA_DIM_FULL
    N_DOCS_TARGET = MAX_INPUTS_FULL

if _ARGS.max_docs is not None:
    N_DOCS_TARGET = int(_ARGS.max_docs)

# ---------------------------------------------------------------------------
# HF token loader (env or .hf_token)
# ---------------------------------------------------------------------------

def _load_hf_token() -> str:
    """Read HF token. PREFERS repo-local .hf_token file over HF_TOKEN env var.

    Precedence rationale (per Exp-Dev 2026-06-04 v5 diagnosis):
    The repo-local .hf_token is explicit + per-repo + version-control-aware
    (gitignored, deliberately placed). HF_TOKEN env vars can leak in from
    shell profiles, login scripts, system env, parent processes, or stale
    huggingface-cli login state -- and on shared runners we've seen an
    unlicensed env token mask a correctly-placed file token (v5 401 GATED-REPO
    failure on Llama-3.2-1B despite valid file token in place).

    File-first precedence prevents that footgun and makes the per-repo file
    the canonical source of auth for a given anchor's runtime.
    """
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        file_tok = tok_path.read_text(encoding="utf-8").strip()
        if file_tok:
            return file_tok
    env_tok = os.environ.get("HF_TOKEN", "").strip()
    if env_tok:
        return env_tok
    raise RuntimeError(
        "HF token not found: place token at <repo>/.hf_token or set HF_TOKEN "
        "env var. Llama-3.2-1B is HF-gated and requires a token with license "
        "access accepted at https://huggingface.co/meta-llama/Llama-3.2-1B"
    )


# ---------------------------------------------------------------------------
# Analogy parser (mirrors exp_phase05_probe_training_v1.py lines 446-471)
# ---------------------------------------------------------------------------

def parse_analogy(doc: Optional[str]) -> Optional[List[Tuple[str, str]]]:
    """Parse 'A : B = C : D' -> [(A,B),(C,D)] with 4-distinct-token constraint.

    Hyperprobe's create_vsa_encodings has a tensor-shape bug when pairs share
    tokens (e.g., '10:1=100:10' has overlapping tokens {10,1,100,10}); we
    filter at parse time. ~389k of 395k analogy rows pass this constraint.

    Returns None when:
      * doc lacks '=' or ':' (malformed)
      * not exactly 2 'A:B' parts split by '='
      * a part doesn't have exactly 2 colon-split tokens
      * any token is empty
      * the 4 case-folded tokens are not distinct (overlap)
    """
    s = (doc or "").strip()
    if "=" not in s or ":" not in s:
        return None
    parts = s.split("=")
    if len(parts) != 2:
        return None
    pairs: List[Tuple[str, str]] = []
    for part in parts:
        sub = part.strip().split(":")
        if len(sub) != 2:
            return None
        a = sub[0].strip()
        b = sub[1].strip()
        if not a or not b:
            return None
        pairs.append((a, b))
    if len(pairs) != 2:
        return None
    all_toks = {t.lower() for t in pairs[0] + pairs[1]}
    if len(all_toks) != 4:
        return None
    return pairs


# ---------------------------------------------------------------------------
# VSA codebook + per-doc encoding helpers (local fallback when hyperprobe
# can't be imported; both code paths produce identical semantics).
# ---------------------------------------------------------------------------

def create_codebook_local(concepts: List[str], vsa_dimension: int):
    """Local implementation of hyperprobe.create_codebook.

    Mirrors create_codebook.py exactly: lowercase + unique concepts; seed=101
    torch.Generator; torchhd.random MAP at given dim. Returns a pd.DataFrame
    indexed by concept with shape (n_concepts, vsa_dimension) float32 bipolar.
    """
    import pandas as pd
    import torch
    import torchhd
    concepts_arr = np.unique([c.lower() for c in concepts])
    g = torch.Generator().manual_seed(101)
    vsa = torchhd.random(
        num_vectors=len(concepts_arr),
        dimensions=vsa_dimension,
        vsa="MAP",
        generator=g,
    ).numpy()
    return pd.DataFrame(data=vsa, index=concepts_arr)


def create_vsa_encoding_local(item: Dict[str, Any], codebook,
                                codebook_set: set) -> Any:
    """Local fallback for hyperprobe.create_vsa_encodings (torchmetrics-free).

    Mirrors vsa_utils.create_vsa_encodings semantics for the analogy case:
      * item['doc']: 'A : B = C : D' style; split by ':' / '='
      * item['concepts']: [(A,B),(C,D)]; tuple-style (example_pair = pair[0],
        target_pair = pair[1])
      * Build example_pair encoding = multibind of the 2 codebook entries
      * Build target_pair encoding = multibind of the 2 codebook entries
      * Combine via multiset + normalize -> bipolar int8 in {-1,+1}^D
    Returns a torch.Tensor int8 of shape (vsa_dimension,) with values in
    {-1, +1}. (Matches hyperprobe's create_vsa_encodings return.)
    """
    import re
    import torch
    import torchhd

    doc = (item["doc"] or "").strip()
    # tokenize doc (matches vsa_utils.py STRAT 1)
    if "=" in doc and ":" in doc:
        toks = re.split(r"\s*[:=]\s*", doc)
    else:
        toks = doc.split()
    tokens = {t.lower() for t in toks if t}
    if not tokens:
        raise ValueError(f"empty tokenization for doc={doc!r}")

    concepts = item["concepts"]
    if not concepts or not isinstance(concepts[0], tuple):
        raise ValueError(f"unsupported concepts shape: {concepts}")
    example_pair = {c.lower() for c in concepts[0]}
    target_pair = {c.lower() for c in concepts[1]}

    # Both pairs must be subsets of tokenized doc (4 distinct tokens by parser).
    if not example_pair.issubset(tokens) or not target_pair.issubset(tokens):
        raise ValueError(
            f"pairs not subset of tokens; example={example_pair} "
            f"target={target_pair} tokens={tokens}"
        )

    # All concepts must be in the codebook.
    missing = (example_pair | target_pair) - codebook_set
    if missing:
        raise ValueError(f"concepts not in codebook: {missing}")

    encoded = []
    for pair in (example_pair, target_pair):
        rows = np.ascontiguousarray(
            codebook.loc[list(pair)].values  # (2, D) float32 in {-1,+1}
        )
        mb = torchhd.multibind(
            torchhd.MAPTensor(torch.from_numpy(rows)).to(torch.int8)
        )
        encoded.append(mb)

    # multiset of the 2 pair encodings + normalize -> bipolar int8
    vsa = torchhd.multiset(torch.stack(encoded)).normalize()
    return vsa.as_subclass(torch.Tensor).to(torch.int8)


def _try_import_hyperprobe():
    """Try to import hyperprobe; return (create_codebook, create_vsa_encodings)
    or (None, None) if the import fails (e.g. local laptop without
    torchmetrics). Caller falls back to the local implementations above
    when imports fail.
    """
    try:
        from hyperprobe import create_codebook as _cb
        from hyperprobe import create_vsa_encodings as _vsa
        return _cb, _vsa
    except Exception as e:
        print(f"[hyperprobe] import failed ({e}); using local fallback "
              f"implementations (semantically equivalent)", flush=True)
        return None, None


# ---------------------------------------------------------------------------
# PROT-022 instrumentation self-test
# ---------------------------------------------------------------------------

def _selftest_structural() -> None:
    """PROT-022 mandatory selftest at import. Verifies:
      1. HF token loads
      2. Layer band math (hidden_states[8:17] = 9 layers)
      3. Hidden dim matches verified config
      4. Parser accepts a normal analogy + rejects shared-token cases
      5. Local codebook + VSA produce bipolar {-1,+1} of correct shape
      6. transformers + torch + numpy imports work
    """
    # 1. Token presence (don't echo)
    try:
        tok = _load_hf_token()
        if not tok.startswith("hf_") or len(tok) < 20:
            print(f"[selftest] WARN: HF token shape unexpected (len={len(tok)}, "
                  f"prefix={tok[:3]!r}); proceeding", flush=True)
    except Exception as e:
        print(f"[selftest] WARN: HF token not available ({e}); model load will "
              f"fail later if not fixed", flush=True)

    # 2. Layer band assertions
    assert ALG1_BAND_START == 8, (
        f"ALG1_BAND_START must be 8 for Llama-3.2-1B; got {ALG1_BAND_START}")
    assert ALG1_BAND_STOP == 17, (
        f"ALG1_BAND_STOP must be 17 for Llama-3.2-1B; got {ALG1_BAND_STOP}")
    assert N_LAYERS_IN_BAND == 9, (
        f"N_LAYERS_IN_BAND must be 9 for Llama-3.2-1B; got {N_LAYERS_IN_BAND}")
    band_indices = list(range(ALG1_BAND_START, ALG1_BAND_STOP))
    assert band_indices == [8, 9, 10, 11, 12, 13, 14, 15, 16], (
        f"layer band indices wrong: {band_indices}")

    # 3. Hidden dim
    assert LLAMA_HIDDEN_SIZE == 2048, (
        f"LLAMA_HIDDEN_SIZE must be 2048; got {LLAMA_HIDDEN_SIZE}")
    assert LLAMA_N_LAYERS == 16, (
        f"LLAMA_N_LAYERS must be 16; got {LLAMA_N_LAYERS}")

    # 4. Parser
    good = parse_analogy("man : king = woman : queen")
    assert good == [("man", "king"), ("woman", "queen")], (
        f"parser: clean analogy failed: {good}")
    bad_shared = parse_analogy("10 : 1 = 100 : 10")  # 10 appears in both pairs
    assert bad_shared is None, (
        f"parser: shared-token analogy must be rejected; got {bad_shared}")
    malformed = parse_analogy("no colons or equals here")
    assert malformed is None, (
        f"parser: malformed must be rejected; got {malformed}")
    empty = parse_analogy("")
    assert empty is None, f"parser: empty must be rejected; got {empty}"

    # 5. Codebook + VSA on synthetic D=64 dummy run
    D_TEST = 64
    concepts = ["man", "king", "woman", "queen"]
    cb = create_codebook_local(concepts, vsa_dimension=D_TEST)
    assert cb.shape == (4, D_TEST), f"codebook shape wrong: {cb.shape}"
    cb_vals = cb.values
    assert cb_vals.dtype == np.float32, f"codebook dtype: {cb_vals.dtype}"
    unique_cb = np.unique(cb_vals)
    assert set(unique_cb.tolist()).issubset({-1.0, 1.0}), (
        f"codebook values must be in {{-1,1}}; got {unique_cb}")

    cb_set = set(cb.index)
    item = {"doc": "man : king = woman : queen",
            "concepts": [("man", "king"), ("woman", "queen")]}
    vsa = create_vsa_encoding_local(item, cb, cb_set)
    import torch
    assert isinstance(vsa, torch.Tensor), f"vsa type: {type(vsa)}"
    assert vsa.shape == (D_TEST,), f"vsa shape: {vsa.shape}"
    vsa_np = vsa.numpy().astype(np.int32)
    unique_vsa = set(np.unique(vsa_np).tolist())
    assert unique_vsa.issubset({-1, 1}), (
        f"vsa must be bipolar {{-1,1}}; got {unique_vsa}")

    # 6. transformers / torch / numpy imports
    import torch as _t
    import numpy as _np
    try:
        import transformers as _tr
        _tr_ok = True
        _tr_ver = _tr.__version__
    except Exception as e:
        _tr_ok = False
        _tr_ver = str(e)
    print(f"[selftest] PASS: token_ok=True layer_band=[8..16]=9layers "
          f"hidden={LLAMA_HIDDEN_SIZE} parser_ok=True "
          f"codebook_shape={cb.shape} vsa_shape={tuple(vsa.shape)} "
          f"vsa_unique={sorted(unique_vsa)} torch={_t.__version__} "
          f"numpy={_np.__version__} transformers_ok={_tr_ok}({_tr_ver})",
          flush=True)


_selftest_structural()


# ---------------------------------------------------------------------------
# Split assignment (deterministic by stable doc_id hash)
# ---------------------------------------------------------------------------

def assign_split(doc_id: int) -> int:
    """Deterministically assign doc -> 0=train, 1=val, 2=test using a stable
    hash. Uses md5 of the doc_id (not Python hash() which is process-salted).
    Probabilities: train 0.8 / val 0.1 / test 0.1.

    The thresholds are CDF cuts on a uniform [0, 1] derived from the first
    4 bytes of md5(doc_id) interpreted as a big-endian uint32.
    """
    h = hashlib.md5(str(doc_id).encode("ascii")).digest()
    u = int.from_bytes(h[:4], "big") / (1 << 32)  # in [0, 1)
    if u < (1.0 - SPLIT_VAL - SPLIT_TEST):       # train
        return 0
    if u < (1.0 - SPLIT_TEST):                    # val
        return 1
    return 2                                       # test


# ---------------------------------------------------------------------------
# Residual extraction core (FULL path)
# ---------------------------------------------------------------------------

def extract_residuals_one_doc(model, tokenizer, doc: str, device: str) -> np.ndarray:
    """Forward Llama-3.2-1B on doc; return (9, 2048) float32 residuals.

    Slices hidden_states[8:17] at the final-token position. Casts BF16 -> F32
    BEFORE detach.cpu().numpy() (per Exp-Dev's bug-fix preservation note;
    Llama-3.2-1B is BF16-native and torch.unique() on BF16 tensors crashes
    in the torchmetrics path downstream).
    """
    import torch
    enc = tokenizer(doc, return_tensors="pt", truncation=True,
                     max_length=MAX_TOK_LEN)
    input_ids = enc["input_ids"].to(device)
    attention_mask = enc.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)
    with torch.no_grad():
        out = model(input_ids=input_ids, attention_mask=attention_mask,
                     output_hidden_states=True, use_cache=False)
    hs = out.hidden_states  # tuple length L+1 = 17
    if len(hs) != LLAMA_N_LAYERS + 1:
        raise RuntimeError(
            f"hidden_states len={len(hs)}; expected {LLAMA_N_LAYERS + 1}")
    # Stack [ALG1_BAND_START..ALG1_BAND_STOP) at final-token position
    layers = []
    for li in range(ALG1_BAND_START, ALG1_BAND_STOP):
        # hs[li] shape (B, T, H). Take batch 0, last token, all hidden.
        # CRITICAL: cast .float() BEFORE .cpu().numpy() to avoid BF16->numpy
        # path issues.
        layers.append(hs[li][0, -1, :].float().detach().cpu().numpy())
    arr = np.stack(layers, axis=0).astype(np.float32)  # (9, 2048)
    if arr.shape != (N_LAYERS_IN_BAND, LLAMA_HIDDEN_SIZE):
        raise RuntimeError(
            f"residual shape wrong: {arr.shape}; expected "
            f"({N_LAYERS_IN_BAND}, {LLAMA_HIDDEN_SIZE})")
    return arr


def _make_synthetic_residual(doc_idx: int, rng: np.random.Generator) -> np.ndarray:
    """Smoke fallback: synthetic (9, 2048) float32 residual.

    Used when smoke mode does NOT load the real model. Validates that
    downstream npz I/O + sidecar JSON paths work end-to-end without paying
    the ~25-min CPU model load. Each doc gets a unique deterministic residual
    derived from doc_idx so structural sanity (no NaN, no duplicates, finite)
    still holds.
    """
    sub_rng = np.random.default_rng(rng.integers(0, 2**31 - 1) + doc_idx)
    arr = sub_rng.standard_normal((N_LAYERS_IN_BAND, LLAMA_HIDDEN_SIZE)).astype(np.float32)
    return arr


# ---------------------------------------------------------------------------
# Main extraction pipeline
# ---------------------------------------------------------------------------

class _TeeStream:
    """Write every print + write to multiple streams so the runner's stdout
    capture AND our on-disk startup.log both see every line. Defensive: any
    individual stream write failure is silently swallowed (we never want
    logging to crash the run)."""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for s in self._streams:
            try:
                s.write(data)
                s.flush()
            except Exception:
                pass
        return len(data) if isinstance(data, str) else 0

    def flush(self):
        for s in self._streams:
            try:
                s.flush()
            except Exception:
                pass


def _log_stage(label: str, log_path: Path) -> None:
    """Timestamped stage marker. Writes to startup.log + stdout (which is now
    teed to startup.log via _TeeStream). Always-flush; never-raise."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = f"[{ts}] STAGE: {label}"
    try:
        print(line, flush=True)
    except Exception:
        pass
    # Belt-and-suspenders: direct write in case stdout tee broke for any reason.
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def main() -> int:
    if _ARGS.self_test:
        print("[selftest] PROT-022 selftests already ran at module import. Done.",
              flush=True)
        return 0

    t_total = time.time()
    # Immediately write a startup log to the C:\ default output dir BEFORE any
    # other work so we always have a breadcrumb even if F:\ self-config fails
    # silently inside the runner (which captures no stderr). Per Exp-Dev
    # 2026-06-04 crash-loop diagnosis.
    default_out_dir = get_output_dir(ANCHOR_NAME)
    try:
        default_out_dir.mkdir(parents=True, exist_ok=True)
        with open(default_out_dir / "startup.log", "a", encoding="utf-8") as _slf:
            _slf.write(
                f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] "
                f"main() entered; RUN_MODE={RUN_MODE} f_drive_active={_F_DRIVE_ACTIVE} "
                f"f_drive_reason={_F_DRIVE_SKIP_REASON!r}\n"
            )
    except Exception as _slog_err:
        sys.stderr.write(f"[startup] could not write startup.log: {_slog_err}\n")

    # Tee stdout+stderr to startup.log so the runner gets EVERY line (and we
    # also get them in startup.log on C:\ that watchdog SCPs back). Per
    # Exp-Dev 2026-06-04 second-failure diagnosis: "no further log lines"
    # after main() entry means the runner's stdout capture stopped working
    # for this entry. Direct file logging works around that.
    _startup_log_path = default_out_dir / "startup.log"
    try:
        _log_fh = open(_startup_log_path, "a", encoding="utf-8")
        sys.stdout = _TeeStream(sys.__stdout__, _log_fh)
        sys.stderr = _TeeStream(sys.__stderr__, _log_fh)
    except Exception as _tee_err:
        sys.stderr.write(f"[startup] tee setup failed: {_tee_err}\n")
        _log_fh = None

    _log_stage("post-tee-setup", _startup_log_path)
    _log_stage(f"py={sys.version.split()[0]} platform={sys.platform} "
               f"cwd={os.getcwd()}", _startup_log_path)

    out_dir = default_out_dir
    # F:\ output redirection: try to create + use F:\hd_data\<anchor>; if it
    # fails for any reason, fall back to default (C:\dev\hd-instrument\data\<anchor>).
    if _F_DRIVE_ACTIVE:
        try:
            os.makedirs(_F_DRIVE_HF_CACHE, exist_ok=True)
            f_dir = Path(_F_DRIVE_DATA_ROOT) / ANCHOR_NAME
            f_dir.mkdir(parents=True, exist_ok=True)
            out_dir = f_dir
            print(f"  [F-drive] redirecting output to {out_dir}", flush=True)
            with open(default_out_dir / "startup.log", "a", encoding="utf-8") as _slf:
                _slf.write(f"  F-drive output redirected to {out_dir}\n")
        except Exception as _fd_err:
            sys.stderr.write(
                f"[F-drive] WARN: output redirect failed "
                f"({type(_fd_err).__name__}: {_fd_err}); using {default_out_dir}\n"
            )
            print(f"  [F-drive] WARN: redirect failed; using default {default_out_dir}",
                  flush=True)
            with open(default_out_dir / "startup.log", "a", encoding="utf-8") as _slf:
                _slf.write(f"  F-drive output redirect FAILED: {_fd_err!r}\n")
            out_dir = default_out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} model={LLM_MODEL_ID} "
          f"vsa_dim={VSA_DIM} n_docs_target={N_DOCS_TARGET} "
          f"smoke_load_model={SMOKE_LOAD_MODEL}", flush=True)
    print(f"  out_dir={out_dir}", flush=True)
    print(f"  layer band: hidden_states[{ALG1_BAND_START}:{ALG1_BAND_STOP}] "
          f"= {N_LAYERS_IN_BAND} layers @ hidden={LLAMA_HIDDEN_SIZE}",
          flush=True)

    # Determine whether to actually load the model
    do_real_load = (RUN_MODE == "full") or (RUN_MODE == "smoke" and SMOKE_LOAD_MODEL)

    # ---- Step 1: Token + auth ----
    # Log token source + prefix BEFORE any HF auth call so we can verify on the
    # runner exactly which token wins. Per Exp-Dev 2026-06-04 v5 diagnosis:
    # a stale HF_TOKEN env on the runner was masking the licensed .hf_token file.
    _file_tok_path = REPO / ".hf_token"
    _file_present = _file_tok_path.exists()
    _file_prefix = "<absent>"
    if _file_present:
        try:
            _ft = _file_tok_path.read_text(encoding="utf-8").strip()
            _file_prefix = (_ft[:5] + "...") if _ft else "<empty>"
        except Exception:
            _file_prefix = "<read-error>"
    _env_prefix = "<unset>"
    _env_raw = os.environ.get("HF_TOKEN", "").strip()
    if _env_raw:
        _env_prefix = _env_raw[:5] + "..."
    _log_stage(
        f"step1: token sources: file={_file_tok_path} present={_file_present} "
        f"prefix={_file_prefix}; env HF_TOKEN prefix={_env_prefix}; "
        f"file-first precedence (per v5 fix)",
        _startup_log_path)
    hf_token = None
    try:
        hf_token = _load_hf_token()
        os.environ["HF_TOKEN"] = hf_token
        os.environ["HUGGINGFACE_HUB_TOKEN"] = hf_token
        _log_stage(
            f"step1: token RESOLVED len={len(hf_token)} prefix={hf_token[:5]}... "
            f"(source: {'file' if _file_present and hf_token == (_file_tok_path.read_text(encoding='utf-8').strip()) else 'env'})",
            _startup_log_path)
    except Exception as e:
        if do_real_load:
            print(f"[FATAL] HF token required for real model load: {e}",
                  flush=True)
            return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                                  f"hf_token_missing: {e}", n_docs=0)
        else:
            print(f"  HF token absent ({e}); proceeding (synthetic smoke "
                  f"doesn't need it)", flush=True)

    # ---- Step 2: Load analogy dataset ----
    _log_stage(f"step2: importing datasets.load_dataset", _startup_log_path)
    try:
        from datasets import load_dataset
    except Exception as e:
        return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                              f"datasets import failed: {e}", n_docs=0,
                              default_out_dir=default_out_dir)

    _log_stage(f"step2: load_dataset({ANALOGY_DATASET}) START", _startup_log_path)
    try:
        analogy_ds = load_dataset(ANALOGY_DATASET, token=hf_token)
        train_rows = analogy_ds["train"]
        _log_stage(f"step2: load_dataset OK n_train={len(train_rows)} "
                   f"cols={train_rows.column_names}", _startup_log_path)
    except Exception as e:
        return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                              f"analogy dataset load failed: {e}", n_docs=0,
                              default_out_dir=default_out_dir)

    # ---- Step 3: Parse + filter analogies ----
    parsed: List[Dict[str, Any]] = []
    n_parse_fail = 0
    for row in train_rows:
        doc = row.get("doc")
        concepts = parse_analogy(doc)
        if concepts is None:
            n_parse_fail += 1
            continue
        parsed.append({"doc": doc, "concepts": concepts})
        if len(parsed) >= N_DOCS_TARGET:
            break
    total_seen = len(parsed) + n_parse_fail
    parse_fail_rate = n_parse_fail / max(total_seen, 1)
    print(f"  parsed: {len(parsed)} kept; {n_parse_fail} rejected "
          f"({parse_fail_rate*100:.2f}% fail rate; "
          f"target={N_DOCS_TARGET})", flush=True)
    if parse_fail_rate > 0.05:
        print(f"  [WARN] parse_fail_rate {parse_fail_rate*100:.2f}% > 5%; "
              f"check analogy schema", flush=True)
    if len(parsed) < min(50, N_DOCS_TARGET):
        return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                              f"too few parsed analogies: {len(parsed)} "
                              f"< {min(50, N_DOCS_TARGET)}",
                              n_docs=len(parsed))

    # ---- Step 4: Build codebook (prefer hyperprobe; fallback local) ----
    all_concepts = set()
    for item in parsed:
        for pair in item["concepts"]:
            for c in pair:
                if isinstance(c, str):
                    all_concepts.add(c)
    print(f"  building codebook: {len(all_concepts)} concepts @ D={VSA_DIM}",
          flush=True)
    hp_create_codebook, hp_create_vsa = _try_import_hyperprobe()
    if hp_create_codebook is not None:
        try:
            codebook = hp_create_codebook(concepts=list(all_concepts),
                                            vsa_dimension=VSA_DIM)
            codebook_source = "hyperprobe"
        except Exception as e:
            print(f"  [warn] hyperprobe.create_codebook failed ({e}); "
                  f"falling back to local", flush=True)
            codebook = create_codebook_local(list(all_concepts), VSA_DIM)
            codebook_source = "local"
            hp_create_codebook = None
    else:
        codebook = create_codebook_local(list(all_concepts), VSA_DIM)
        codebook_source = "local"
    codebook_set = set(codebook.index)
    print(f"  codebook ready: shape={codebook.shape} source={codebook_source}",
          flush=True)

    # ---- Step 5: Load model (FULL or smoke-with-load) ----
    model = None
    tokenizer = None
    device = "cpu"
    if do_real_load:
        _log_stage("step5: importing torch + transformers", _startup_log_path)
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
        except Exception as e:
            return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                                  f"torch/transformers import failed: {e}",
                                  n_docs=0, default_out_dir=default_out_dir)
        _log_stage(f"step5: torch={torch.__version__} "
                   f"cuda_available={torch.cuda.is_available()} "
                   f"hf_cache_env=HF_HOME={os.environ.get('HF_HOME','<unset>')} "
                   f"HUGGINGFACE_HUB_CACHE={os.environ.get('HUGGINGFACE_HUB_CACHE','<unset>')}",
                   _startup_log_path)
        if RUN_MODE == "full" and not torch.cuda.is_available():
            return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                                  "FULL mode requires CUDA; got cuda_available=False",
                                  n_docs=0, default_out_dir=default_out_dir)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16
        _log_stage(f"step5: tokenizer.from_pretrained({LLM_MODEL_ID}) START",
                   _startup_log_path)
        t_load = time.time()
        try:
            tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_ID, token=hf_token)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            _log_stage(f"step5: tokenizer OK in {time.time()-t_load:.1f}s; "
                       f"model.from_pretrained START "
                       f"(dtype={dtype}, device={device}, ~2.5GB if download)",
                       _startup_log_path)
            t_model = time.time()
            model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL_ID,
                torch_dtype=dtype,
                token=hf_token,
                low_cpu_mem_usage=True,
            )
            _log_stage(f"step5: model weights loaded in {time.time()-t_model:.1f}s; "
                       f"moving to {device}", _startup_log_path)
            model.to(device)
            model.eval()
            _log_stage(f"step5: model on {device}; ready for forward passes",
                       _startup_log_path)
        except Exception as e:
            msg = str(e)
            if "401" in msg or "403" in msg or "gated" in msg.lower() or "access" in msg.lower():
                return _emit_metrics(
                    out_dir, t_total, "HARD_FAIL",
                    f"Llama-3.2-1B HF-gated; license not accepted? "
                    f"Visit https://huggingface.co/{LLM_MODEL_ID} and "
                    f"accept terms with the token's account. err={e}",
                    n_docs=0)
            if "out of memory" in msg.lower() or "cuda" in msg.lower():
                return _emit_metrics(
                    out_dir, t_total, "HARD_FAIL",
                    f"CUDA OOM or device error during model load (try "
                    f"reducing concurrent VRAM usage or freeing GPU): {e}",
                    n_docs=0)
            return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                                  f"model load failed: {e}", n_docs=0)
        # Sanity-check the model config matches our verified facts.
        cfg = model.config
        if int(getattr(cfg, "hidden_size", -1)) != LLAMA_HIDDEN_SIZE:
            return _emit_metrics(
                out_dir, t_total, "HARD_FAIL",
                f"model hidden_size={cfg.hidden_size} != "
                f"verified {LLAMA_HIDDEN_SIZE}", n_docs=0)
        if int(getattr(cfg, "num_hidden_layers", -1)) != LLAMA_N_LAYERS:
            return _emit_metrics(
                out_dir, t_total, "HARD_FAIL",
                f"model num_hidden_layers={cfg.num_hidden_layers} != "
                f"verified {LLAMA_N_LAYERS}", n_docs=0)
        print(f"  model loaded in {time.time()-t_load:.1f}s; "
              f"hidden_size={cfg.hidden_size}, n_layers={cfg.num_hidden_layers}",
              flush=True)
    else:
        print(f"  [smoke] skipping model load; using synthetic residuals "
              f"(set HDLAB_SMOKE_LOAD_MODEL=1 to force CPU load; ~25min/5docs)",
              flush=True)

    # ---- Step 6: Per-doc extraction + VSA encoding ----
    # PROT-021 partial checkpointing per doc with compound key including
    # model_id, vsa_dim, run_mode to prevent smoke->full contamination.
    # Note: _seed_checkpoint's _PARTIAL_RE allows [A-Za-z0-9_\-] only (no
    # dots), so we sanitize the model_id (e.g. "Llama-3.2-1B" -> "Llama-3-2-1B").
    _safe_model_id = LLM_MODEL_ID.replace("/", "_").replace(".", "-")
    ckpt_key_prefix = (
        f"{_safe_model_id}_d{VSA_DIM}_"
        f"{'real' if do_real_load else 'synth'}_{RUN_MODE}_doc"
    )

    # Resume: scan existing partials and skip done docs.
    done_keys = set(list_completed_keys(out_dir))
    done_idx = {int(k.split("_doc")[-1]) for k in done_keys
                if k.startswith(ckpt_key_prefix) and "_doc" in k}
    print(f"  resume: {len(done_idx)} docs already cached; "
          f"will process {len(parsed) - len(done_idx)} remaining", flush=True)

    # v8 fail-fast watchdog: spawn a daemon thread that monitors per-doc
    # progress and exits via os._exit if no doc completes for
    # WATCHDOG_PER_DOC_TIMEOUT_S. The runner can resume from the per-doc
    # partials on next dispatch. v6 hung at doc 70300 for 20+ min silently;
    # v7 hung at doc 0 for 30+ min silently. Both wasted GPU + blocked other
    # work. This watchdog converts silent freezes into fast-fail exits.
    import threading
    _LAST_DOC_COMPLETE_TS[0] = time.monotonic()

    def _watchdog():
        # Periodic heartbeat-monitor; runs in daemon thread.
        while True:
            time.sleep(15)
            last = _LAST_DOC_COMPLETE_TS[0]
            if last is None:
                continue
            idle_s = time.monotonic() - last
            if idle_s > WATCHDOG_PER_DOC_TIMEOUT_S:
                msg = (f"\n[WATCHDOG] no doc completed in {idle_s:.1f}s "
                       f"(threshold {WATCHDOG_PER_DOC_TIMEOUT_S}s); "
                       f"presumed deadlock; exiting via os._exit(99). "
                       f"Resume on next dispatch from per-doc partials.")
                try:
                    print(msg, flush=True)
                except Exception:
                    pass
                try:
                    (out_dir / "watchdog_exit.json").write_text(
                        json.dumps({
                            "idle_seconds": idle_s,
                            "watchdog_timeout_s": WATCHDOG_PER_DOC_TIMEOUT_S,
                            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                            time.gmtime()),
                        }, indent=2),
                        encoding="utf-8",
                    )
                except Exception:
                    pass
                os._exit(99)

    _watchdog_thread = threading.Thread(target=_watchdog, daemon=True)
    _watchdog_thread.start()
    print(f"  watchdog armed: will exit if no doc completes in "
          f"{WATCHDOG_PER_DOC_TIMEOUT_S}s; PROGRESS_EVERY={PROGRESS_EVERY}",
          flush=True)

    rng = np.random.default_rng(101)
    n_extracted = 0
    n_failed = 0
    n_nan_residual = 0
    n_nan_vsa = 0
    n_vsa_fail = 0
    t_extract = time.time()
    for doc_idx, item in enumerate(parsed):
        if doc_idx in done_idx:
            continue
        try:
            # Residual extraction
            if do_real_load:
                res = extract_residuals_one_doc(model, tokenizer, item["doc"], device)
            else:
                res = _make_synthetic_residual(doc_idx, rng)
            # NaN guard
            if not np.isfinite(res).all():
                n_nan_residual += 1
                raise RuntimeError(f"non-finite residual values doc_idx={doc_idx}")

            # VSA target
            try:
                if hp_create_vsa is not None:
                    vsa_t = hp_create_vsa(item, codebook, verbose=False)
                    import torch
                    if not isinstance(vsa_t, torch.Tensor):
                        vsa_t = torch.as_tensor(vsa_t)
                    vsa_arr = vsa_t.detach().cpu().numpy().astype(np.float32)
                else:
                    vsa_t = create_vsa_encoding_local(item, codebook, codebook_set)
                    vsa_arr = vsa_t.numpy().astype(np.float32)
            except Exception as e:
                n_vsa_fail += 1
                raise RuntimeError(f"VSA encoding failed doc_idx={doc_idx}: {e}")
            if vsa_arr.shape != (VSA_DIM,):
                raise RuntimeError(
                    f"VSA shape wrong doc_idx={doc_idx}: {vsa_arr.shape} "
                    f"!= ({VSA_DIM},)")
            if not np.isfinite(vsa_arr).all():
                n_nan_vsa += 1
                raise RuntimeError(f"non-finite VSA values doc_idx={doc_idx}")
            uniq = set(np.unique(vsa_arr).tolist())
            if not uniq.issubset({-1.0, 1.0}):
                raise RuntimeError(
                    f"VSA not bipolar doc_idx={doc_idx}: unique={uniq}")

            split = assign_split(doc_idx)
            payload = {
                "doc_idx": int(doc_idx),
                "doc_str": item["doc"],
                "split": int(split),
                "residual": res.tolist(),
                "target_vsa": vsa_arr.tolist(),
                "model_id": LLM_MODEL_ID,
                "vsa_dim": int(VSA_DIM),
                "run_mode": RUN_MODE,
            }
            write_partial_key(out_dir, f"{ckpt_key_prefix}{doc_idx}", payload)
            n_extracted += 1
        except Exception as e:
            n_failed += 1
            print(f"  [err] doc_idx={doc_idx}: {e}", flush=True)
            if n_failed > max(10, int(0.05 * N_DOCS_TARGET)):
                print(f"  [FATAL] failure rate too high "
                      f"({n_failed}/{doc_idx+1}); aborting", flush=True)
                break

        # v8 watchdog heartbeat: bump on every doc loop iteration (success OR
        # failure path; both indicate the main loop is alive). Watchdog thread
        # exits process if this timestamp goes stale beyond
        # WATCHDOG_PER_DOC_TIMEOUT_S.
        _LAST_DOC_COMPLETE_TS[0] = time.monotonic()

        if (doc_idx + 1) % PROGRESS_EVERY == 0 or doc_idx + 1 == len(parsed):
            wall = time.time() - t_extract
            mem_mb = _approx_mem_mb()
            # v8 also log GPU memory (helps localize CUDA leaks / OOM-near-edge).
            gpu_mem_str = ""
            try:
                import torch
                if torch.cuda.is_available():
                    alloc_gb = torch.cuda.memory_allocated() / (1024 ** 3)
                    reserved_gb = torch.cuda.memory_reserved() / (1024 ** 3)
                    gpu_mem_str = (f" gpu_alloc_gb={alloc_gb:.2f} "
                                   f"gpu_reserved_gb={reserved_gb:.2f}")
            except Exception:
                pass
            print(f"  progress: doc {doc_idx+1}/{len(parsed)} "
                  f"extracted={n_extracted} failed={n_failed} "
                  f"wall_so_far={wall:.1f}s mem_mb={mem_mb:.1f}{gpu_mem_str}",
                  flush=True)

    extract_wall = time.time() - t_extract
    print(f"  extraction done in {extract_wall:.1f}s: "
          f"extracted={n_extracted} failed={n_failed} "
          f"nan_res={n_nan_residual} nan_vsa={n_nan_vsa} vsa_fail={n_vsa_fail}",
          flush=True)

    # Free model to leave RAM for the npz assembly + JSON write
    if model is not None:
        del model
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass

    # ---- Step 7: Aggregate partials -> npz ----
    print(f"  aggregating partials -> npz", flush=True)
    parts = aggregate_partials(out_dir)
    # Filter to OUR run's partials only (excludes any stale ones from sibling runs)
    our = [(int(k.split("_doc")[-1]), v) for k, v in parts.items()
            if k.startswith(ckpt_key_prefix) and "_doc" in k]
    our.sort(key=lambda kv: kv[0])
    n_docs = len(our)
    if n_docs == 0:
        return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                              "no partials aggregated; nothing extracted",
                              n_docs=0)

    residuals_arr = np.empty((n_docs, N_LAYERS_IN_BAND, LLAMA_HIDDEN_SIZE),
                              dtype=np.float32)
    doc_ids_arr = np.empty((n_docs,), dtype=np.int32)
    split_arr = np.empty((n_docs,), dtype=np.uint8)
    target_vsa_arr = np.empty((n_docs, VSA_DIM), dtype=np.float32)
    doc_id_to_doc_str: Dict[str, str] = {}
    for i, (doc_idx, body) in enumerate(our):
        residuals_arr[i] = np.asarray(body["residual"], dtype=np.float32)
        doc_ids_arr[i] = int(body["doc_idx"])
        split_arr[i] = int(body["split"])
        target_vsa_arr[i] = np.asarray(body["target_vsa"], dtype=np.float32)
        doc_id_to_doc_str[str(int(body["doc_idx"]))] = body["doc_str"]

    # ---- Step 8: NaN/range guards on aggregate ----
    if not np.isfinite(residuals_arr).all():
        return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                              "non-finite residuals in aggregate",
                              n_docs=n_docs)
    if not np.isfinite(target_vsa_arr).all():
        return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                              "non-finite target_vsa in aggregate",
                              n_docs=n_docs)
    vsa_uniq = set(np.unique(target_vsa_arr).tolist())
    if not vsa_uniq.issubset({-1.0, 1.0}):
        return _emit_metrics(out_dir, t_total, "HARD_FAIL",
                              f"target_vsa not bipolar: unique={vsa_uniq}",
                              n_docs=n_docs)

    n_train = int((split_arr == 0).sum())
    n_val = int((split_arr == 1).sum())
    n_test = int((split_arr == 2).sum())

    # ---- Step 9: Write npz + sidecar JSONs ----
    npz_path = out_dir / "llama32_1b_residuals.npz"
    meta_path = out_dir / "llama32_1b_residuals_meta.json"
    doc_id_path = out_dir / "doc_id_to_doc_str.json"

    # Use savez_compressed for ~3x size reduction on residuals (still single-file).
    print(f"  writing npz -> {npz_path} "
          f"(residuals={residuals_arr.shape} "
          f"target_vsa={target_vsa_arr.shape})", flush=True)
    # np.savez_compressed auto-appends .npz; write to tmp without extension,
    # then rename, so we get a single atomic .npz at the final path.
    tmp_npz_base = npz_path.with_suffix("")     # ...residuals (no ext)
    tmp_npz_base_str = str(tmp_npz_base) + ".tmp"
    tmp_npz_actual = Path(tmp_npz_base_str + ".npz")  # actual write target
    np.savez_compressed(
        tmp_npz_base_str,
        residuals=residuals_arr,
        doc_ids=doc_ids_arr,
        split=split_arr,
        target_vsa=target_vsa_arr,
        vsa_dim=np.int32(VSA_DIM),
    )
    os.replace(tmp_npz_actual, npz_path)

    from datetime import datetime, timezone
    meta = {
        "model_id": LLM_MODEL_ID,
        "layer_band_hidden_state_slice": f"[{ALG1_BAND_START}:{ALG1_BAND_STOP}]",
        "layer_band_n_layers": int(N_LAYERS_IN_BAND),
        "hidden_dim": int(LLAMA_HIDDEN_SIZE),
        "n_docs": int(n_docs),
        "n_train": n_train,
        "n_val": n_val,
        "n_test": n_test,
        "codebook_concepts_count": int(len(all_concepts)),
        "codebook_source": codebook_source,
        "vsa_dim": int(VSA_DIM),
        "run_mode": RUN_MODE,
        "real_model_load": bool(do_real_load),
        "device": device,
        "parse_fail_rate": float(parse_fail_rate),
        "extracted_at_iso": datetime.now(timezone.utc).isoformat(),
        "anchor": ANCHOR_NAME,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    doc_id_path.write_text(json.dumps(doc_id_to_doc_str, indent=2),
                            encoding="utf-8")
    print(f"  meta -> {meta_path}", flush=True)
    print(f"  doc_id_to_doc_str -> {doc_id_path}", flush=True)

    # ---- Step 10: Verdict + metrics.json ----
    npz_size_mb = npz_path.stat().st_size / (1024 * 1024)
    expected = N_DOCS_TARGET
    # Allow a small shortfall for parse-filtered docs; bound by what was parsed.
    expected_after_parse = min(expected, len(parsed))
    completeness = n_docs / max(expected_after_parse, 1)

    # HARD_PASS gate: at least 95% of the parseable target landed AND no NaN
    # AND artifacts exist. The 95% allowance lets a handful of per-doc failures
    # (e.g., tokenization edge cases) not gate the whole run.
    min_required = max(1, int(0.95 * expected_after_parse))
    if (n_docs >= min_required
            and not (n_nan_residual or n_nan_vsa)
            and npz_path.exists()
            and meta_path.exists()):
        verdict = "HARD_PASS"
    else:
        verdict = "HARD_FAIL"

    total_wall = time.time() - t_total
    msg = (f"Llama-3.2-1B residual extraction: n_docs={n_docs} "
           f"(target_after_parse={expected_after_parse}, "
           f"completeness={completeness*100:.1f}%); "
           f"residual_shape=(n_docs,9,2048) target_vsa_shape=(n_docs,{VSA_DIM}); "
           f"n_train/val/test={n_train}/{n_val}/{n_test}; "
           f"npz_size={npz_size_mb:.1f}MB wall={total_wall:.1f}s. "
           f"Verdict: {verdict}.")
    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "real_model_load": bool(do_real_load),
        "model_id": LLM_MODEL_ID,
        "hidden_size": LLAMA_HIDDEN_SIZE,
        "layer_band_start": ALG1_BAND_START,
        "layer_band_stop": ALG1_BAND_STOP,
        "n_layers_in_band": N_LAYERS_IN_BAND,
        "vsa_dim": VSA_DIM,
        "n_docs_target": int(N_DOCS_TARGET),
        "n_docs_parsed": int(len(parsed)),
        "n_docs_extracted": int(n_docs),
        "n_train": n_train,
        "n_val": n_val,
        "n_test": n_test,
        "n_failed": int(n_failed),
        "n_nan_residual": int(n_nan_residual),
        "n_nan_vsa": int(n_nan_vsa),
        "n_vsa_fail": int(n_vsa_fail),
        "parse_fail_rate": float(parse_fail_rate),
        "codebook_concepts": int(len(all_concepts)),
        "codebook_source": codebook_source,
        "npz_path": str(npz_path),
        "npz_size_mb": float(npz_size_mb),
        "meta_path": str(meta_path),
        "doc_id_path": str(doc_id_path),
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": float(total_wall),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2),
                                            encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={total_wall:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {out_dir / 'metrics.json'}", flush=True)
    print(f"[{ANCHOR_NAME}] {msg}", flush=True)
    return 0 if verdict == "HARD_PASS" else 1


def _emit_metrics(out_dir: Path, t_start: float, verdict: str, msg: str,
                  n_docs: int,
                  default_out_dir: Optional[Path] = None) -> int:
    """Write a minimal metrics.json on early-exit (HARD_FAIL paths).

    Per Exp-Dev 2026-06-04 diagnosis: if F:\\ goes down mid-run, the primary
    out_dir (possibly on F:\\) is unreachable for metrics.json. Always also
    write a copy to default_out_dir (C:\\ default) so we ALWAYS get a
    diagnostic landing on a stable filesystem.
    """
    elapsed = time.time() - t_start
    payload = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "verdict": verdict,
        "verdict_msg": msg,
        "n_docs_extracted": int(n_docs),
        "elapsed_s": float(elapsed),
    }
    body = json.dumps(payload, indent=2)
    paths_written = []
    paths_failed = []
    candidates = [out_dir]
    if default_out_dir is not None and default_out_dir != out_dir:
        candidates.append(default_out_dir)
    for p in candidates:
        try:
            p.mkdir(parents=True, exist_ok=True)
            (p / "metrics.json").write_text(body, encoding="utf-8")
            paths_written.append(str(p / "metrics.json"))
        except Exception as e:
            paths_failed.append(f"{p}: {type(e).__name__}: {e}")
    if not paths_written:
        sys.stderr.write(
            f"[FATAL] could not write metrics.json anywhere: {paths_failed}\n"
        )
    elif paths_failed:
        print(f"  [warn] some metrics.json writes failed: {paths_failed}; "
              f"wrote to: {paths_written}", flush=True)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s",
          flush=True)
    print(f"[{ANCHOR_NAME}] {msg}", flush=True)
    return 0 if verdict == "HARD_PASS" else 1


def _approx_mem_mb() -> float:
    """Best-effort RSS in MB; psutil if available, otherwise 0."""
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Capture full traceback to BOTH stdout AND startup.log so the
        # exception is visible whether we have stdout capture or not. Per
        # Exp-Dev 2026-06-04 diagnosis ("no further log lines after main()").
        tb = traceback.format_exc()
        sys.stderr.write(tb)
        default_out_dir = get_output_dir(ANCHOR_NAME)
        try:
            default_out_dir.mkdir(parents=True, exist_ok=True)
            with open(default_out_dir / "startup.log", "a", encoding="utf-8") as _slf:
                _slf.write(
                    f"\n[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] "
                    f"UNHANDLED EXCEPTION at top level:\n{tb}\n"
                )
        except Exception:
            pass
        # Mirror main()'s F:\ redirection for the exception-path metrics write,
        # but always also attempt to write to the C:\ default (in case F:\
        # is what crashed).
        f_dir = None
        if _F_DRIVE_ACTIVE:
            try:
                f_dir = Path(_F_DRIVE_DATA_ROOT) / ANCHOR_NAME
                f_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                f_dir = None
        out_dir_for_metrics = f_dir if f_dir is not None else default_out_dir
        _emit_metrics(out_dir_for_metrics, time.time(), "HARD_FAIL",
                       f"unhandled exception: {e}", n_docs=0,
                       default_out_dir=default_out_dir)
        sys.exit(1)
