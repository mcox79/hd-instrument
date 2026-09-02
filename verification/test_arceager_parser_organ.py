"""Witness for the PROMOTED arc-eager parser organ (hdlab/arceager_parser.py).

Confirms the promotion is byte-faithful to experiments/exp_arceager_parser_operator_v1.py:
  [1] LOAD  -- hdlab.arceager_parser.load_model(MODEL_PATH) loads the trained weights.
  [2] PARSE -- a handful of sentences produce a VALID tree (every token has a head in
               range, a ROOT exists) and a confidence value per attachment.
  [3] BYTE-FAITHFUL -- the ORIGINAL experiment cell, loading the SAME model, parses the
               SAME >=5 sentences and yields IDENTICAL heads and IDENTICAL confidence
               (within 1e-9). The promotion changed nothing.

Deterministic, CPU numpy only, NO external LLM. Run with the venv python.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import sys
import importlib.util
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# --- the promoted hdlab organ ---
import hdlab.arceager_parser as organ

# --- the ORIGINAL experiment cell, loaded directly by file path (no package needed) ---
_exp_path = os.path.join(REPO, "experiments", "exp_arceager_parser_operator_v1.py")
_spec = importlib.util.spec_from_file_location("exp_arceager_parser_operator_v1", _exp_path)
exp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp)

# >=5 sentences, each (tokens, UPOS tags). Tags are identical for both parsers, so the
# byte-faithful comparison is unaffected by any tagging choice.
SENTS = [
    (["The", "dog", "chased", "the", "ball", "."],
     ["DET", "NOUN", "VERB", "DET", "NOUN", "PUNCT"]),
    (["She", "quickly", "ran", "home", "."],
     ["PRON", "ADV", "VERB", "ADV", "PUNCT"]),
    (["John", "gave", "Mary", "a", "book", "."],
     ["PROPN", "VERB", "PROPN", "DET", "NOUN", "PUNCT"]),
    (["The", "old", "man", "sat", "on", "the", "bench", "."],
     ["DET", "ADJ", "NOUN", "VERB", "ADP", "DET", "NOUN", "PUNCT"]),
    (["I", "think", "that", "he", "is", "right", "."],
     ["PRON", "VERB", "SCONJ", "PRON", "AUX", "ADJ", "PUNCT"]),
    (["Birds", "fly", "."],
     ["NOUN", "VERB", "PUNCT"]),
]

fails = []


def check(name, ok, detail=""):
    print(("  [PASS] " if ok else "  [FAIL] ") + name + (("  -- " + detail) if detail else ""))
    if not ok:
        fails.append(name)


print("=" * 72)
print("WITNESS: hdlab/arceager_parser.py  (promoted arc-eager parser organ)")
print("=" * 72)

# --------------------------------------------------------------------------- [1]
print("\n[1] LOAD via hdlab organ")
print("    MODEL_PATH = %s" % organ.MODEL_PATH)
check("MODEL_PATH exists on disk", os.path.exists(organ.MODEL_PATH), organ.MODEL_PATH)
W_hd = organ.load_model(organ.MODEL_PATH)
check("hdlab.load_model returns an ndarray", isinstance(W_hd, np.ndarray))
n_weights = int(W_hd.size)
n_nonzero = int(np.count_nonzero(W_hd))
print("    weight-vector size = %d (feature-hash table SIZE=%d)  non-zero weights = %d  dtype=%s"
      % (n_weights, organ.SIZE, n_nonzero, W_hd.dtype))
check("weight vector has expected hash-table size", n_weights == organ.SIZE, "got %d" % n_weights)
check("weight vector is non-trivial (trained)", n_nonzero > 1000, "%d non-zero" % n_nonzero)

# --------------------------------------------------------------------------- [2]
print("\n[2] PARSE a few sentences -> valid tree + confidence per attachment")
for toks, pos in SENTS:
    heads, conf, marg = organ.parse_with_conf(toks, pos, W_hd)
    n = len(toks)
    keys_ok = set(heads.keys()) == set(range(1, n + 1))
    range_ok = all(0 <= heads[i] <= n for i in range(1, n + 1))
    root_ok = any(heads[i] == 0 for i in range(1, n + 1))
    conf_present = all(i in conf for i in range(1, n + 1))
    conf_range = all(0.0 <= conf[i] <= 1.0 for i in range(1, n + 1))
    ok = keys_ok and range_ok and root_ok and conf_present and conf_range
    root_tok = [i for i in range(1, n + 1) if heads[i] == 0]
    detail = "heads=%s root@%s conf[min,max]=[%.3f,%.3f]" % (
        [heads[i] for i in range(1, n + 1)], root_tok,
        min(conf[i] for i in range(1, n + 1)), max(conf[i] for i in range(1, n + 1)))
    check("valid tree + conf: '" + " ".join(toks) + "'", ok, detail)

# --------------------------------------------------------------------------- [3]
print("\n[3] BYTE-FAITHFUL vs original experiment cell")
# Same model, loaded independently by the experiment cell.
W_exp = exp.load_model(organ.MODEL_PATH)
check("load_model returns identical weights (organ vs experiment)",
      np.array_equal(W_hd, W_exp), "arrays equal element-for-element")

n_sent = 0
max_head_diff = 0
max_conf_diff = 0.0
max_marg_diff = 0.0
for toks, pos in SENTS:
    h_hd, c_hd, m_hd = organ.parse_with_conf(toks, pos, W_hd)
    h_ex, c_ex, m_ex = exp.parse_with_conf(toks, pos, W_exp)
    n = len(toks)
    heads_same = all(h_hd[i] == h_ex[i] for i in range(1, n + 1))
    conf_d = max(abs(c_hd[i] - c_ex[i]) for i in range(1, n + 1))
    marg_d = max(abs(m_hd[i] - m_ex[i]) for i in range(1, n + 1))
    max_head_diff = max(max_head_diff, 0 if heads_same else 1)
    max_conf_diff = max(max_conf_diff, conf_d)
    max_marg_diff = max(max_marg_diff, marg_d)
    ok = heads_same and conf_d <= 1e-9 and marg_d <= 1e-9
    check("identical parse: '" + " ".join(toks) + "'", ok,
          "head_match=%s max|dconf|=%.2e max|dmarg|=%.2e" % (heads_same, conf_d, marg_d))
    n_sent += 1

print("\n    sentences compared = %d  identical-heads = %s  max|dconf| = %.2e  max|dmarg| = %.2e"
      % (n_sent, max_head_diff == 0, max_conf_diff, max_marg_diff))

# --------------------------------------------------------------------------- verdict
print("\n" + "=" * 72)
if fails:
    print("RESULT: FAIL (%d check(s) failed): %s" % (len(fails), fails))
    sys.exit(1)
print("RESULT: ALL CHECKS PASS -- promotion is byte-faithful.")
print("=" * 72)
