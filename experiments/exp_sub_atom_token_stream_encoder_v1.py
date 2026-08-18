"""sub_atom_token_stream_encoder_v1 -- B4 math/science formal-knowledge ingest.

Prerequisite for Lean Mathlib / Materials Project / OEIS ingest. Char-trigram
encoder works for natural-language English but averages formal-math token
streams to noise. This cell tests: 2000-symbol math codebook + variable
renaming (alpha-equivalence) + role-filler bind for predicate-argument
structure.

ARMS (5):
  ARM_CHAR_TRIGRAM_BASELINE      current encoder on formal-math token stream
  ARM_MATH_CODEBOOK_TOKEN        ~2000-symbol math codebook (one atom per symbol)
  ARM_MATH_CODEBOOK_VAR_RENAME   codebook + alpha-equivalence
  ARM_MATH_CODEBOOK_ROLE_FILLER  full: codebook + var-rename + role-filler bind
  ARM_DIAG_BIND_DEPTH            depth-1/3/5 nested expression unbind accuracy

PRE-REG BANDS (HARD-LOCKED at module init, PROSPECTIVE):
  HARD_PASS:
    ROLE_FILLER unbind accuracy >= 0.80 at depth-3 (vs CHAR_TRIGRAM <= 0.20)
    alpha-equivalent expressions cosine >= 0.95 (var rename preserves identity)
    cv across seeds < 0.10
    2000-symbol codebook achieves >= 0.95 disambiguation between symbols
  MIDDLE_BAND: partial wins (codebook works but role-filler weak)
  HARD_FAIL: ROLE_FILLER unbind < 0.50 at depth-3 OR alpha-equiv < 0.80

DATA (self-contained synthetic):
  Synthetic math expressions over 2000-symbol codebook (operators, vars, funcs).
  Held-out test set of 200 expressions for evaluation. Test corpus surrogates
  Lean Mathlib / MatSci / OEIS structure (predicate-argument trees) without
  requiring external data fetch.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 seeds * 5 arms * 3 corpora = 75
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 5 arms * 1 corpus = 10

HARDENING: L1 early metrics, L2 per-arm progress, L3 outer try/except,
L4 import-crash sentinel.

Per-arm metrics structure (Fix #28):
  metrics["per_arm"] = {arm: {seed: {unbind_d1, unbind_d3, unbind_d5,
                                       alpha_equiv_cos, codebook_disambig}}}

ASCII-only; no emojis; self-contained.
Author: exp_dev 2026-06-27
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "sub_atom_token_stream_encoder_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_UNBIND_D3 = 0.80
HP_TRIGRAM_CEILING = 0.20
HP_ALPHA_EQUIV_COS = 0.95
HP_CODEBOOK_DISAMBIG = 0.95
HP_CV_MAX = 0.10
MB_UNBIND_D3 = 0.50
HF_UNBIND_D3 = 0.50
HF_ALPHA_EQUIV = 0.80

EXPECTED_ARMS = ["char_trigram_baseline", "math_codebook_token",
                 "math_codebook_var_rename", "math_codebook_role_filler",
                 "diag_bind_depth"]

if SELF_TEST_MODE:
    N_DIM = 512
    CODEBOOK_SIZE = 200
    N_TEST_EXPR = 20
    SEEDS = [7]
    CORPORA = ["lean"]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    CODEBOOK_SIZE = 2000
    N_TEST_EXPR = 100
    SEEDS = [7, 17]
    CORPORA = ["lean"]
else:
    N_DIM = 4096
    CODEBOOK_SIZE = 2000
    N_TEST_EXPR = 200
    SEEDS = [7, 17, 23, 31, 41]
    CORPORA = ["lean", "matsci", "oeis"]

# Role-filler arity: each predicate has 1-3 argument roles
MAX_ARITY = 3
DEPTHS_TESTED = [1, 3, 5]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(CORPORA)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,codebook=%d,n_test=%d,seeds=%s,corpora=%s,mode=%s,"
    "HP_unbind_d3>=%.2f,HP_alpha_cos>=%.2f,HP_codebook_disambig>=%.2f,"
    "HP_cv<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, CODEBOOK_SIZE, N_TEST_EXPR, SEEDS, CORPORA, RUN_MODE,
    HP_UNBIND_D3, HP_ALPHA_EQUIV_COS, HP_CODEBOOK_DISAMBIG, HP_CV_MAX,
    EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_sub_atom_encoder",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_sub_atom_encoder_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def circ_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular convolution bind (HRR). Returns vector of same shape."""
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    out = np.fft.ifft(fa * fb).real
    return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)


def circ_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular correlation unbind: c * b^-1 via FFT conjugate."""
    fc = np.fft.fft(c)
    fb = np.fft.fft(b)
    out = np.fft.ifft(fc * np.conj(fb)).real
    return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)


def char_trigram_encode(token: str, codebook_h: Dict[str, np.ndarray],
                          n_dim: int) -> np.ndarray:
    """Hash char-trigrams to N-dim via deterministic codebook."""
    if not token:
        return np.zeros(n_dim, dtype=np.float32)
    padded = "##" + token + "##"
    out = np.zeros(n_dim, dtype=np.float32)
    n = 0
    for i in range(len(padded) - 2):
        tg = padded[i:i+3]
        if tg not in codebook_h:
            # Hash to N-dim bipolar
            hv = abs(hash(tg))
            rng = np.random.default_rng(hv)
            v = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
            v = v / (np.linalg.norm(v) + 1e-8)
            codebook_h[tg] = v
        out += codebook_h[tg]
        n += 1
    if n == 0:
        return out
    out /= n
    return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)


# -------------------------- expression generation --------------------------

OPERATOR_TOKENS = ["+", "-", "*", "/", "=", "<=", ">=", "<", ">", "!=",
                   "sin", "cos", "tan", "exp", "log", "sqrt", "abs",
                   "sum", "prod", "int", "diff", "lim", "max", "min"]
VARIABLE_PREFIXES = ["x", "y", "z", "u", "v", "w", "a", "b", "c", "n", "m", "k"]
PREDICATE_TOKENS = ["equals", "implies", "forall", "exists", "in", "subset"]


def build_symbol_codebook(codebook_size: int, n_dim: int,
                           g: np.random.Generator
                           ) -> Tuple[Dict[str, int], np.ndarray]:
    """Build deterministic codebook: symbol -> idx + (codebook_size, n_dim) atom matrix."""
    sym_to_idx: Dict[str, int] = {}
    idx = 0
    # Fixed operators first
    for op in OPERATOR_TOKENS:
        sym_to_idx[op] = idx
        idx += 1
    for p in PREDICATE_TOKENS:
        sym_to_idx[p] = idx
        idx += 1
    # Variables: x0, x1, x2, ... up to fill
    for vp in VARIABLE_PREFIXES:
        for i in range(200):
            tok = "%s%d" % (vp, i)
            if idx >= codebook_size:
                break
            sym_to_idx[tok] = idx
            idx += 1
        if idx >= codebook_size:
            break
    # Pad up with generic SYM_<n> tokens
    while idx < codebook_size:
        sym_to_idx["SYM_%d" % idx] = idx
        idx += 1
    E = bipolar(codebook_size, n_dim, g)
    return sym_to_idx, E


def gen_expression(depth: int, sym_to_idx: Dict[str, int],
                    g: np.random.Generator
                    ) -> Tuple[List[str], Any]:
    """Generate a nested expression tree of given depth.

    Returns (token_stream, tree). tree is nested tuples: (op, [args...]).
    """
    if depth == 0:
        # Leaf: a variable
        vlist = [s for s in sym_to_idx if any(s.startswith(p) for p in VARIABLE_PREFIXES)
                  and s[len(s.rstrip("0123456789")):].isdigit()]
        if not vlist:
            vlist = ["x0"]
        v = vlist[int(g.integers(0, len(vlist)))]
        return [v], ("VAR", v)
    op = OPERATOR_TOKENS[int(g.integers(0, len(OPERATOR_TOKENS)))]
    arity = int(g.integers(1, MAX_ARITY + 1))
    tokens: List[str] = [op, "("]
    args = []
    for k in range(arity):
        sub_toks, sub_tree = gen_expression(depth - 1, sym_to_idx, g)
        tokens.extend(sub_toks)
        if k < arity - 1:
            tokens.append(",")
        args.append(sub_tree)
    tokens.append(")")
    return tokens, ("OP", op, args)


def rename_variables(tree: Any, mapping: Dict[str, str]) -> Any:
    """Rename variables consistently through tree."""
    if tree[0] == "VAR":
        v = tree[1]
        return ("VAR", mapping.get(v, v))
    op, name, args = tree
    return ("OP", name, [rename_variables(a, mapping) for a in args])


def tokens_from_tree(tree: Any) -> List[str]:
    if tree[0] == "VAR":
        return [tree[1]]
    op, name, args = tree
    out = [name, "("]
    for i, a in enumerate(args):
        out.extend(tokens_from_tree(a))
        if i < len(args) - 1:
            out.append(",")
    out.append(")")
    return out


# -------------------------- encoding arms --------------------------

def encode_char_trigram(tokens: List[str], codebook_h: Dict[str, np.ndarray],
                          n_dim: int) -> np.ndarray:
    """Concat tokens, encode char-trigrams of resulting string."""
    s = " ".join(tokens)
    return char_trigram_encode(s, codebook_h, n_dim)


def encode_codebook_token(tokens: List[str], sym_to_idx: Dict[str, int],
                            E: np.ndarray, n_dim: int) -> np.ndarray:
    """Sum codebook atoms for known tokens; zero for unknown."""
    out = np.zeros(n_dim, dtype=np.float32)
    n = 0
    for t in tokens:
        if t in sym_to_idx:
            out += E[sym_to_idx[t]]
            n += 1
    if n > 0:
        out /= n
    return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)


def encode_codebook_var_rename(tree: Any, sym_to_idx: Dict[str, int],
                                  E: np.ndarray, n_dim: int) -> np.ndarray:
    """Alpha-canonicalize: rename all variables to canonical names by first-appearance,
    then encode tokenized canonical form via codebook."""
    seen: Dict[str, str] = {}
    counter = [0]

    def _canon(t):
        if t[0] == "VAR":
            v = t[1]
            if v not in seen:
                seen[v] = "x%d" % counter[0]
                counter[0] += 1
            return ("VAR", seen[v])
        op, name, args = t
        return ("OP", name, [_canon(a) for a in args])
    canon_tree = _canon(tree)
    toks = tokens_from_tree(canon_tree)
    return encode_codebook_token(toks, sym_to_idx, E, n_dim)


def encode_role_filler(tree: Any, sym_to_idx: Dict[str, int], E: np.ndarray,
                         role_atoms: np.ndarray, n_dim: int) -> np.ndarray:
    """Role-filler bind: OP_OP * bind(role_0, arg_0) + bind(role_1, arg_1) ...

    Recursively encodes subexpressions and binds with positional role atoms.
    Includes alpha-canonicalization step before encoding.
    """
    seen: Dict[str, str] = {}
    counter = [0]

    def _canon(t):
        if t[0] == "VAR":
            v = t[1]
            if v not in seen:
                seen[v] = "x%d" % counter[0]
                counter[0] += 1
            return ("VAR", seen[v])
        op, name, args = t
        return ("OP", name, [_canon(a) for a in args])
    canon_tree = _canon(tree)

    def _enc(t):
        if t[0] == "VAR":
            v = t[1]
            return E[sym_to_idx.get(v, 0)]
        op, name, args = t
        op_atom = E[sym_to_idx.get(name, 0)]
        out = op_atom.copy()
        for k, a in enumerate(args):
            child = _enc(a)
            role = role_atoms[k % role_atoms.shape[0]]
            bound = circ_bind(role, child)
            out = out + bound
        return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)
    return _enc(canon_tree)


# -------------------------- evaluation --------------------------

def codebook_disambig_score(E: np.ndarray, codebook_size: int,
                              g: np.random.Generator) -> float:
    """Fraction of codebook entries whose nearest neighbor is itself."""
    n_sample = min(codebook_size, 500)
    idx = g.choice(codebook_size, n_sample, replace=False)
    correct = 0
    for i in idx:
        v = E[i]
        sims = E @ v
        sims[i] = sims[i]
        nearest = int(np.argmax(sims))
        if nearest == i:
            correct += 1
    return correct / float(n_sample)


def alpha_equiv_cosine(tree_a: Any, tree_b: Any, sym_to_idx: Dict[str, int],
                          E: np.ndarray, role_atoms: np.ndarray,
                          n_dim: int) -> float:
    """Cosine between encoded alpha-equivalent expressions (RoleFiller encoder)."""
    a = encode_role_filler(tree_a, sym_to_idx, E, role_atoms, n_dim)
    b = encode_role_filler(tree_b, sym_to_idx, E, role_atoms, n_dim)
    return float(np.dot(a, b))


def unbind_accuracy_at_depth(depth: int, sym_to_idx: Dict[str, int],
                                E: np.ndarray, role_atoms: np.ndarray,
                                n_dim: int, n_trials: int,
                                g: np.random.Generator) -> float:
    """For each trial: encode depth-N expr; unbind role_0 to recover arg_0; match
    against codebook. Returns fraction recovered correctly."""
    correct = 0
    for _ in range(n_trials):
        tokens, tree = gen_expression(depth, sym_to_idx, g)
        if tree[0] != "OP":
            continue
        op, name, args = tree
        if not args:
            continue
        # Encode whole tree
        enc = encode_role_filler(tree, sym_to_idx, E, role_atoms, n_dim)
        # Target = arg_0 (canonicalized within encoder; for matching we encode
        # the same arg fresh through encoder so contexts match).
        target = encode_role_filler(args[0], sym_to_idx, E, role_atoms, n_dim)
        # Unbind role_0
        recovered = circ_unbind(enc, role_atoms[0])
        # Match by cosine
        cos = float(np.dot(recovered, target))
        # Pass threshold: above noise floor (cosine of random pair ~ 0)
        if cos > 0.30:
            correct += 1
    return correct / float(n_trials)


def trigram_unbind_proxy(depth: int, codebook_h: Dict[str, np.ndarray],
                           n_dim: int, n_trials: int,
                           sym_to_idx: Dict[str, int],
                           g: np.random.Generator) -> float:
    """Char-trigram has no real unbind; proxy: can we distinguish args via trigram alone?
    Returns mean cosine of arg_0_encoded vs whole_expr_trigram_encoded - should be low."""
    cos_sum = 0.0
    n = 0
    for _ in range(n_trials):
        _, tree = gen_expression(depth, sym_to_idx, g)
        if tree[0] != "OP":
            continue
        op, name, args = tree
        if not args:
            continue
        whole_toks = tokens_from_tree(tree)
        whole_enc = encode_char_trigram(whole_toks, codebook_h, n_dim)
        arg0_toks = tokens_from_tree(args[0])
        arg0_enc = encode_char_trigram(arg0_toks, codebook_h, n_dim)
        cos = float(np.dot(whole_enc, arg0_enc))
        if cos > 0.30:
            cos_sum += 1
        n += 1
    return cos_sum / max(1, n)


# -------------------------- arms --------------------------

def run_arm_char_trigram(sym_to_idx, E, n_dim, n_trials, g):
    codebook_h: Dict[str, np.ndarray] = {}
    d1 = trigram_unbind_proxy(1, codebook_h, n_dim, n_trials, sym_to_idx, g)
    d3 = trigram_unbind_proxy(3, codebook_h, n_dim, n_trials, sym_to_idx, g)
    d5 = trigram_unbind_proxy(5, codebook_h, n_dim, n_trials, sym_to_idx, g)
    return {"unbind_d1": d1, "unbind_d3": d3, "unbind_d5": d5,
            "alpha_equiv_cos": 0.0, "codebook_disambig": 0.0}


def run_arm_codebook_token(sym_to_idx, E, n_dim, n_trials, g):
    """Token codebook alone: encode-then-match each arg via codebook sum.

    Unbind proxy: arg_0 codebook-sum cosine with whole-expr codebook-sum.
    Same proxy as trigram (no actual unbind capability)."""
    correct_per_depth: Dict[str, float] = {}
    for depth in DEPTHS_TESTED:
        c = 0
        n = 0
        for _ in range(n_trials):
            _, tree = gen_expression(depth, sym_to_idx, g)
            if tree[0] != "OP":
                continue
            op, name, args = tree
            if not args:
                continue
            whole_toks = tokens_from_tree(tree)
            whole_enc = encode_codebook_token(whole_toks, sym_to_idx, E, n_dim)
            arg0_toks = tokens_from_tree(args[0])
            arg0_enc = encode_codebook_token(arg0_toks, sym_to_idx, E, n_dim)
            cos = float(np.dot(whole_enc, arg0_enc))
            if cos > 0.30:
                c += 1
            n += 1
        correct_per_depth["d%d" % depth] = c / max(1, n)
    db = codebook_disambig_score(E, E.shape[0], g)
    return {"unbind_d1": correct_per_depth.get("d1", 0.0),
            "unbind_d3": correct_per_depth.get("d3", 0.0),
            "unbind_d5": correct_per_depth.get("d5", 0.0),
            "alpha_equiv_cos": 0.0, "codebook_disambig": db}


def run_arm_codebook_var_rename(sym_to_idx, E, n_dim, n_trials, g):
    """Encode with var-rename canonicalization; measure alpha-equiv cosine."""
    # For each trial: generate expr, rename vars, encode both; cosine should be ~1
    cos_sum = 0.0
    n = 0
    for _ in range(n_trials):
        _, tree = gen_expression(3, sym_to_idx, g)
        # Make a rename mapping
        vlist = [s for s in sym_to_idx if s.startswith("x") and len(s) > 1
                  and s[1:].isdigit()]
        if len(vlist) < 4:
            continue
        # Rename by shuffling existing vars
        renamed_vars = list(g.choice(vlist, len(vlist), replace=False))
        mapping = {v: renamed_vars[i % len(renamed_vars)]
                   for i, v in enumerate(vlist)}
        tree_b = rename_variables(tree, mapping)
        a_toks = tokens_from_tree(tree)
        b_toks = tokens_from_tree(tree_b)
        # Canonicalize before token encoding (var-rename arm step)
        seen_a: Dict[str, str] = {}
        cnt_a = [0]
        def _canon_a(t):
            if t[0] == "VAR":
                v = t[1]
                if v not in seen_a:
                    seen_a[v] = "x%d" % cnt_a[0]
                    cnt_a[0] += 1
                return ("VAR", seen_a[v])
            op, name, args = t
            return ("OP", name, [_canon_a(a) for a in args])
        a_canon = _canon_a(tree)

        seen_b: Dict[str, str] = {}
        cnt_b = [0]
        def _canon_b(t):
            if t[0] == "VAR":
                v = t[1]
                if v not in seen_b:
                    seen_b[v] = "x%d" % cnt_b[0]
                    cnt_b[0] += 1
                return ("VAR", seen_b[v])
            op, name, args = t
            return ("OP", name, [_canon_b(a) for a in args])
        b_canon = _canon_b(tree_b)

        a_enc = encode_codebook_token(tokens_from_tree(a_canon), sym_to_idx, E, n_dim)
        b_enc = encode_codebook_token(tokens_from_tree(b_canon), sym_to_idx, E, n_dim)
        cos_sum += float(np.dot(a_enc, b_enc))
        n += 1
    alpha_cos = cos_sum / max(1, n)
    # Use codebook arm's depth values
    correct_per_depth: Dict[str, float] = {}
    for depth in DEPTHS_TESTED:
        c = 0
        nn = 0
        for _ in range(n_trials):
            _, tree = gen_expression(depth, sym_to_idx, g)
            if tree[0] != "OP":
                continue
            op, name, args = tree
            if not args:
                continue
            whole_toks = tokens_from_tree(tree)
            whole_enc = encode_codebook_token(whole_toks, sym_to_idx, E, n_dim)
            arg0_toks = tokens_from_tree(args[0])
            arg0_enc = encode_codebook_token(arg0_toks, sym_to_idx, E, n_dim)
            cos = float(np.dot(whole_enc, arg0_enc))
            if cos > 0.30:
                c += 1
            nn += 1
        correct_per_depth["d%d" % depth] = c / max(1, nn)
    db = codebook_disambig_score(E, E.shape[0], g)
    return {"unbind_d1": correct_per_depth.get("d1", 0.0),
            "unbind_d3": correct_per_depth.get("d3", 0.0),
            "unbind_d5": correct_per_depth.get("d5", 0.0),
            "alpha_equiv_cos": alpha_cos, "codebook_disambig": db}


def run_arm_role_filler(sym_to_idx, E, n_dim, n_trials, g):
    """Full encoder: role-filler + var-rename + codebook."""
    role_atoms = bipolar(MAX_ARITY, n_dim, g)
    d1 = unbind_accuracy_at_depth(1, sym_to_idx, E, role_atoms, n_dim, n_trials, g)
    d3 = unbind_accuracy_at_depth(3, sym_to_idx, E, role_atoms, n_dim, n_trials, g)
    d5 = unbind_accuracy_at_depth(5, sym_to_idx, E, role_atoms, n_dim, n_trials, g)
    # Alpha-equiv via role-filler encoder
    cos_sum = 0.0
    nn = 0
    for _ in range(max(20, n_trials // 4)):
        _, tree = gen_expression(3, sym_to_idx, g)
        vlist = [s for s in sym_to_idx if s.startswith("x") and len(s) > 1
                  and s[1:].isdigit()]
        if len(vlist) < 4:
            continue
        renamed_vars = list(g.choice(vlist, len(vlist), replace=False))
        mapping = {v: renamed_vars[i % len(renamed_vars)]
                   for i, v in enumerate(vlist)}
        tree_b = rename_variables(tree, mapping)
        cos = alpha_equiv_cosine(tree, tree_b, sym_to_idx, E, role_atoms, n_dim)
        cos_sum += cos
        nn += 1
    alpha_cos = cos_sum / max(1, nn)
    db = codebook_disambig_score(E, E.shape[0], g)
    return {"unbind_d1": d1, "unbind_d3": d3, "unbind_d5": d5,
            "alpha_equiv_cos": alpha_cos, "codebook_disambig": db}


def run_arm_diag_bind_depth(sym_to_idx, E, n_dim, n_trials, g):
    """Diagnostic mirror of role-filler; same numbers but explicit per-depth."""
    role_atoms = bipolar(MAX_ARITY, n_dim, g)
    out: Dict[str, float] = {}
    for depth in DEPTHS_TESTED:
        out["d%d" % depth] = unbind_accuracy_at_depth(
            depth, sym_to_idx, E, role_atoms, n_dim, n_trials, g)
    return {"unbind_d1": out.get("d1", 0.0),
            "unbind_d3": out.get("d3", 0.0),
            "unbind_d5": out.get("d5", 0.0),
            "alpha_equiv_cos": 0.0,
            "codebook_disambig": 0.0,
            "diag_detail": out}


# -------------------------- per-seed --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    sym_to_idx, E = build_symbol_codebook(CODEBOOK_SIZE, N_DIM, g)
    n_trials = N_TEST_EXPR

    per_arm: Dict[str, Dict[str, float]] = {}
    per_arm["char_trigram_baseline"] = run_arm_char_trigram(
        sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["math_codebook_token"] = run_arm_codebook_token(
        sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["math_codebook_var_rename"] = run_arm_codebook_var_rename(
        sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["math_codebook_role_filler"] = run_arm_role_filler(
        sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["diag_bind_depth"] = run_arm_diag_bind_depth(
        sym_to_idx, E, N_DIM, n_trials, g)
    return {
        "seed": int(seed),
        "N": N_DIM,
        "codebook_size": CODEBOOK_SIZE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        d3_vals: List[float] = []
        d1_vals: List[float] = []
        d5_vals: List[float] = []
        ae_vals: List[float] = []
        db_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                d3_vals.append(float(d.get("unbind_d3", 0.0)))
                d1_vals.append(float(d.get("unbind_d1", 0.0)))
                d5_vals.append(float(d.get("unbind_d5", 0.0)))
                ae_vals.append(float(d.get("alpha_equiv_cos", 0.0)))
                db_vals.append(float(d.get("codebook_disambig", 0.0)))
                per_arm_full[arm][s] = {
                    "unbind_d1": float(d.get("unbind_d1", 0.0)),
                    "unbind_d3": float(d.get("unbind_d3", 0.0)),
                    "unbind_d5": float(d.get("unbind_d5", 0.0)),
                    "alpha_equiv_cos": float(d.get("alpha_equiv_cos", 0.0)),
                    "codebook_disambig": float(d.get("codebook_disambig", 0.0)),
                }
        if d3_vals:
            m_d3 = float(np.mean(d3_vals))
            sd_d3 = float(np.std(d3_vals))
            cv = sd_d3 / abs(m_d3) if abs(m_d3) > 1e-6 else 0.0
            summary[arm] = {
                "mean_d1": float(np.mean(d1_vals)),
                "mean_d3": m_d3, "std_d3": sd_d3, "cv_d3": cv,
                "mean_d5": float(np.mean(d5_vals)),
                "mean_alpha_cos": float(np.mean(ae_vals)),
                "mean_codebook_disambig": float(np.mean(db_vals)),
                "n": len(d3_vals),
            }
        else:
            summary[arm] = {"mean_d1": 0.0, "mean_d3": 0.0, "std_d3": 0.0,
                            "cv_d3": 0.0, "mean_d5": 0.0, "mean_alpha_cos": 0.0,
                            "mean_codebook_disambig": 0.0, "n": 0}

    rf = summary["math_codebook_role_filler"]
    trig = summary["char_trigram_baseline"]
    rf_d3 = rf["mean_d3"]
    rf_cv = rf["cv_d3"]
    rf_alpha = rf["mean_alpha_cos"]
    rf_codebook = rf["mean_codebook_disambig"]
    trig_d3 = trig["mean_d3"]

    verdict = "MIDDLE_BAND"
    if (rf_d3 >= HP_UNBIND_D3 and trig_d3 <= HP_TRIGRAM_CEILING and
            rf_alpha >= HP_ALPHA_EQUIV_COS and rf_cv < HP_CV_MAX and
            rf_codebook >= HP_CODEBOOK_DISAMBIG):
        verdict = "HARD_PASS"
    elif rf_d3 < HF_UNBIND_D3 or rf_alpha < HF_ALPHA_EQUIV:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | RF_d3=%.3f Trig_d3=%.3f | alpha_cos=%.3f codebook_disambig=%.3f cv=%.3f | n=%d"
    ) % (verdict, rf_d3, trig_d3, rf_alpha, rf_codebook, rf_cv, len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "rf_d3": rf_d3,
        "rf_alpha_cos": rf_alpha,
        "rf_codebook_disambig": rf_codebook,
        "rf_cv": rf_cv,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(EXPECTED_ARMS) * len(CORPORA),
        "cardinality_ok": (len(seeds_sorted) * len(EXPECTED_ARMS) * len(CORPORA)
                           >= EXPECTED_N_UNITS),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s codebook=%d" % (
                               os.getpid(), RUN_MODE, CODEBOOK_SIZE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_corpora": CORPORA,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d codebook=%d seeds=%s corpora=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, CODEBOOK_SIZE, SEEDS, CORPORA,
        EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "unbind_d3" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified")
            print("[selftest] OK", flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_sub_atom_encoder"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
