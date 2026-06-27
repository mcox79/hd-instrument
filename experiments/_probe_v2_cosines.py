"""Probe: measure actual trigram-baseline cosines on REAL parsed Mathlib trees."""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np
import importlib.util
spec = importlib.util.spec_from_file_location(
    "v2", REPO / "experiments" / "exp_sub_atom_token_stream_encoder_v2_real_mathlib.py")
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

g = np.random.default_rng(7)
corpus, _ = v2.load_corpus("lean")
print("corpus n=%d, mean_len=%.1f" % (len(corpus),
      np.mean([len(s) for s in corpus])))

sym_to_idx, E = v2.build_symbol_codebook_from_corpus(corpus, 2000, 2048, g)
print("codebook size=%d" % len(sym_to_idx))

# Print actual cosines for trigram whole-vs-arg_0 on real corpus trees
codebook_h = {}
trees = v2._trees_from_corpus(corpus, 3, g, 20)
print("trees parsed=%d (target depth=3)" % len(trees))
print("\n=== TRIGRAM whole-vs-arg_0 cosines (depth=3) ===")
cos_list = []
for tree in trees[:20]:
    if tree[0] != "OP" or not tree[2]:
        continue
    whole_toks = v2.tree_token_stream(tree)
    arg0_toks = v2.tree_token_stream(tree[2][0])
    whole_enc = v2.encode_char_trigram(whole_toks, codebook_h, 2048)
    arg0_enc = v2.encode_char_trigram(arg0_toks, codebook_h, 2048)
    cos = float(np.dot(whole_enc, arg0_enc))
    cos_list.append(cos)
    print("  whole=%d toks, arg0=%d toks, cos=%.3f (>0.30=%s)" % (
        len(whole_toks), len(arg0_toks), cos, cos > 0.30))
print("mean cos=%.3f median cos=%.3f frac>0.30=%.3f" % (
    np.mean(cos_list), np.median(cos_list),
    np.mean(np.array(cos_list) > 0.30)))

# ROLE_FILLER unbind cosines
print("\n=== ROLE_FILLER unbind cosines (depth=3) ===")
role_atoms = v2.bipolar(3, 2048, g)
cos_rf = []
for tree in trees[:20]:
    if tree[0] != "OP" or not tree[2]:
        continue
    enc = v2.encode_role_filler(tree, sym_to_idx, E, role_atoms, 2048)
    target = v2.encode_role_filler(tree[2][0], sym_to_idx, E, role_atoms, 2048)
    recovered = v2.circ_unbind(enc, role_atoms[0])
    cos = float(np.dot(recovered, target))
    cos_rf.append(cos)
print("mean cos=%.3f median cos=%.3f frac>0.30=%.3f" % (
    np.mean(cos_rf), np.median(cos_rf),
    np.mean(np.array(cos_rf) > 0.30)))

# Tree depth distribution
depths = [v2._tree_depth(v2.parse_to_tree(v2.tokenize(s))) for s in corpus[:30]]
print("\nTree depths (first 30 corpus strings): min=%d max=%d mean=%.1f" % (
    min(depths), max(depths), np.mean(depths)))
print("Token counts (first 30): min=%d max=%d mean=%.1f" % (
    min(len(v2.tokenize(s)) for s in corpus[:30]),
    max(len(v2.tokenize(s)) for s in corpus[:30]),
    np.mean([len(v2.tokenize(s)) for s in corpus[:30]])))

# Show example trees
print("\n=== First 3 corpus strings + parsed trees ===")
for s in corpus[:3]:
    toks = v2.tokenize(s)
    tree = v2.parse_to_tree(toks)
    print("\nstr: %s" % s[:80])
    print("toks(%d): %s" % (len(toks), toks[:15]))
    print("tree depth=%d head=%s" % (v2._tree_depth(tree),
        tree[1] if tree[0] == "OP" else tree[1]))
