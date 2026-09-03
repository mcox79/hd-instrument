"""Persisted probe (reproducible): the FIX's identity-weak-point recovery is CI-separated ON ITS OWN SUBSET,
and the glass-box Higgins classifier types the reversible specificational family (CUE 1) correctly.

Cited in SOLVED.md FURTHER PUSHES (A). Recomputes in memory; writes nothing to landed dirs.
Run: .venv/Scripts/python.exe notes/problems/the_reader_has_no_copular_is_a_binding_schema/prototype_identity_gain_ci.py
"""
import os
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)

import experiments._copular_nominal_events as M
import experiments.exp_copular_is_a_binding_readout_v1 as E
from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser
from hdlab.arc_labeler import ArcLabeler

pos = PosTagger.load(M._POS_ASSET)
arc = ArcParser.load(M._ARC_ASSET)
lab = ArcLabeler.load(M._LAB_ASSET)
sents = E.load_ud(E.UD_TEST)

# per-doc (25-sentence) identity-type base_tp / fix_tp / g -> bootstrap the identity-ONLY gain
per = []
cur = defaultdict(int)
sc = 0
for sent in sents:
    toks = [r[1] for r in sent]
    up = pos.tag(toks)
    heads = arc.parse(toks, up).heads
    base = set(M.extract_entity_states(toks, up, arc, lab))
    fix = base | E.robust_cop(toks, up, heads, gate=True)
    for (h, p, t) in E.typed_gold(sent):
        if t != "ident":
            continue
        cur["g"] += 1
        cur["base"] += int((h, p) in base)
        cur["fix"] += int((h, p) in fix)
    sc += 1
    if sc % 25 == 0:
        per.append(dict(cur)); cur = defaultdict(int)
if cur.get("g"):
    per.append(dict(cur))

g = np.array([d.get("g", 0) for d in per])
b = np.array([d.get("base", 0) for d in per])
f = np.array([d.get("fix", 0) for d in per])
rng = np.random.default_rng(E.SEED)
n = len(per)
obs = f.sum() / g.sum() - b.sum() / g.sum()
bs = np.empty(4000)
for k in range(4000):
    idx = rng.integers(0, n, n)
    den = max(g[idx].sum(), 1)
    bs[k] = f[idx].sum() / den - b[idx].sum() / den
lo, hi = np.percentile(bs, [2.5, 97.5])
print("IDENTITY-type gold n=%d  base_recall=%.4f  fix_recall=%.4f" % (g.sum(), b.sum() / g.sum(), f.sum() / g.sum()))
print("IDENTITY fix-vs-base gain: %+.4f CI[%+.4f,%+.4f] CI-sep=%s" % (obs, lo, hi, lo > 0))

print("\nspecificational/identity typing (PINNED CUE 1 reversibility family):")
for t in ("The winner is John .", "The captain is Ahab .", "The best option is the hotel ."):
    tk = t.split(); u = pos.tag(tk)
    got = [(tk[j], E.predicted_type(tk, u, 0, j)) for j in range(2, len(tk)) if u[j] in ("PROPN", "NOUN")]
    print("  '%s' -> %s" % (t, got))
