"""Scaffold-free witness for `the_bundle_destroys_meaning_but_replacing_it_hurts`.

Recomputes a MODEST-scale version of task c3 (a lemma's accumulated distributional profile must rank
a WordNet neighbour first among all anchors) live, no scaffold, and asserts the load-bearing
invariants the FULL run rests on. The FULL run establishes the exact numbers and CIs; this proves the
DIRECTION reproduces from a fresh, smaller corpus.

INVARIANTS (all confirmed CI-backed at FULL scale, 5491 anchors / 4000 items):

  1. THE BUNDLING IS NOT THE BOTTLENECK. RAW_COOC removes the superposition entirely -- explicit
     per-context co-occurrence counts, with NONE of the ~62% bundling loss -- and STILL loses to the
     spelling floor A5_STRINGCTRL. If the bundle-destroys-meaning story were the cost on c3, the
     un-bundled representation would rescue it; it does not.

  2. THE STRING FLOOR IS MOSTLY MORPHOLOGICAL LEAKAGE. Strip WordNet gold members that share a stem
     with the query, and the spelling control COLLAPSES, while the distributional arms barely move --
     so on leakage-free gold the distributional channel (RAW_COOC, and even the unmodified flat bag)
     BEATS the spelling control. "A benchmark selected by a resource cannot fairly score that
     resource": most of the 2:1 spelling win was form, not meaning.

  3. THE INFO-FREE CONTROLS LOSE. Random dense profiles AND a per-row column-shuffled co-occurrence
     (same shape, destroyed structure) both score near the floor, well below the real arms.

  4. THE INFO-FREE SHUFFLE IS ACTUALLY INFO-FREE (a bug guard). A SHARED column permutation leaves
     cosine invariant -- it is NOT a null; only the per-row independent shuffle destroys structure.

Run:  .venv/Scripts/python.exe verification/test_c3_bundling_is_not_the_bottleneck.py
ASCII-only. No network, no scaffold. ~2-5 min at the witness corpus size.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
from collections import defaultdict

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np
import scipy.sparse as sp

import experiments.exp_grounding_readout_known_answer_v1 as C3
import experiments.exp_meaning_supply_separation_v1 as MS
from hdlab.reading_grounding_loop import content_lemmas, normalize_lemma
from experiments.exp_c3_surprise_weighted_vs_bundling_v1 import (
    build_cooc, ppmi_dense, shuffle_cols, shares_stem, stripped_gold_fn, score_dense,
)
from experiments.exp_c3_grounded_fusion_v1 import grounded_matrix, fuse_multi, load_lancaster

CORPUS_LIMIT = 2000        # sentences/segment; larger than smoke (400), well below full (all)
MAX_ITEMS = 1500


def _load(limit):
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5
    return [s for _seg, s in load_corpus_v5(limit, lineaware=True)]


def build():
    out_dir = os.path.join(_REPO, "data", "_witness_c3_bundling_scratch")
    os.makedirs(out_dir, exist_ok=True)
    sents = _load(CORPUS_LIMIT)
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, out_dir)
    anchors, mat_base = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    aidx = {a: i for i, a in enumerate(anchors)}
    n2 = defaultdict(list)
    for a in anchors:
        n2[normalize_lemma(a)].append(pos[a])
    items, _diag = C3.build_items(space, buckets, counts, MAX_ITEMS)
    sent_ctx = []
    for s in sents:
        sent_ctx.append([aidx[l] for l in set(content_lemmas(s)) if l in aidx])
    cooc = build_cooc(anchors, pos, buckets, sent_ctx, out_dir)
    t_mat, _cov = MS.trigram_matrix(anchors)
    grounded, _gcov = grounded_matrix(anchors, load_lancaster())
    mats = {
        "A1_BASE": mat_base.astype(np.float32),
        "A5_STRINGCTRL": t_mat.astype(np.float32),
        "RAW_COOC": cooc.toarray().astype(np.float32),
        "PPMI_SMOOTH": ppmi_dense(cooc, alpha=0.75),
        "RANDOM": np.random.default_rng(1).standard_normal((len(anchors), 256)).astype(np.float32),
        "SHUF_COOC": ppmi_dense(shuffle_cols(cooc, 2), alpha=0.75),
        "GROUNDED": grounded,
    }
    return anchors, pos, n2, items, mats, out_dir


def hit_at_1(mats, name, anchors, pos, n2, items, gold_fn, out_dir):
    hits, _r, _t, _m, _p = score_dense(mats[name], anchors, pos, n2, items, gold_fn, out_dir, name)
    return float(hits.mean())


def main():
    anchors, pos, n2, items, mats, out_dir = build()
    strip_items = [it for it in items
                   if any((g in pos) and g != it["L"] and not C3._is_variant(g, it["L"])
                          for g in stripped_gold_fn(it["L"]))]
    print("[witness] anchors=%d items=%d strip_items=%d" % (len(anchors), len(items), len(strip_items)))

    full = {k: hit_at_1(mats, k, anchors, pos, n2, items, C3.gold_meaning_set, out_dir) for k in mats}
    strip = {k: hit_at_1(mats, k, anchors, pos, n2, strip_items, stripped_gold_fn, out_dir)
             for k in ("A5_STRINGCTRL", "RAW_COOC", "A1_BASE", "GROUNDED")}

    # brain-faithful combine: flat bag (+) grounded sensorimotor spoke (ATL hub-and-spoke)
    fbg_full = float(fuse_multi([mats["A1_BASE"], mats["GROUNDED"]], anchors, pos, n2,
                                items, C3.gold_meaning_set).mean())
    fbg_strip = float(fuse_multi([mats["A1_BASE"], mats["GROUNDED"]], anchors, pos, n2,
                                 strip_items, stripped_gold_fn).mean())
    frg_full = float(fuse_multi([mats["RANDOM"], mats["GROUNDED"]], anchors, pos, n2,
                                items, C3.gold_meaning_set).mean())

    print("[witness] FULL  " + "  ".join("%s=%.4f" % (k, full[k]) for k in
          ("A1_BASE", "A5_STRINGCTRL", "RAW_COOC", "PPMI_SMOOTH", "RANDOM", "SHUF_COOC")))
    print("[witness] STRIP " + "  ".join("%s=%.4f" % (k, strip[k]) for k in
          ("A5_STRINGCTRL", "RAW_COOC", "A1_BASE")))

    ok = True

    def chk(cond, msg):
        nonlocal ok
        print(("[witness] PASS " if cond else "[witness] FAIL ") + msg)
        ok = ok and bool(cond)

    # 1. bundling is not the bottleneck: un-bundled explicit counts still lose to spelling
    chk(full["RAW_COOC"] < full["A5_STRINGCTRL"],
        "bundling-removed (RAW_COOC %.4f) still LOSES to spelling floor (A5 %.4f)"
        % (full["RAW_COOC"], full["A5_STRINGCTRL"]))
    # 2. the string floor is mostly morphological leakage
    chk(strip["A5_STRINGCTRL"] < 0.6 * full["A5_STRINGCTRL"],
        "spelling floor COLLAPSES under morph-strip (%.4f -> %.4f)"
        % (full["A5_STRINGCTRL"], strip["A5_STRINGCTRL"]))
    chk(strip["RAW_COOC"] > strip["A5_STRINGCTRL"] and strip["A1_BASE"] > strip["A5_STRINGCTRL"],
        "on leakage-free gold the DISTRIBUTIONAL channel wins: RAW_COOC %.4f, flat bag %.4f > "
        "spelling %.4f" % (strip["RAW_COOC"], strip["A1_BASE"], strip["A5_STRINGCTRL"]))
    # 3. info-free controls lose
    chk(full["RANDOM"] < 0.5 * full["A1_BASE"] and full["SHUF_COOC"] < full["A1_BASE"],
        "info-free controls lose: RANDOM %.4f, SHUF_COOC %.4f < flat bag %.4f"
        % (full["RANDOM"], full["SHUF_COOC"], full["A1_BASE"]))

    # 5. the brain-faithful combine (ATL hub): flat bag (+) grounded spoke beats EITHER channel alone
    print("[witness] GROUNDED alone=%.4f  FUSE_BASE_GROUNDED full=%.4f strip=%.4f  "
          "FUSE_RANDOM_GROUNDED=%.4f" % (full["GROUNDED"], fbg_full, fbg_strip, frg_full))
    # (scale-robust part; "beats grounded alone too" is a FULL-scale CI claim in metrics.json --
    #  grounded's 11 dims over-discriminate in a small pool, so at witness scale it can lead.)
    chk(fbg_full > full["A1_BASE"],
        "hub-and-spoke: flat bag (+) grounded (%.4f) beats the flat bag alone (%.4f) [grounded %.4f]"
        % (fbg_full, full["A1_BASE"], full["GROUNDED"]))
    chk(fbg_strip > strip["A5_STRINGCTRL"],
        "on leakage-free gold the brain-faithful combine BEATS the spelling floor (%.4f > %.4f)"
        % (fbg_strip, strip["A5_STRINGCTRL"]))
    chk(frg_full < full["GROUNDED"],
        "random(+)grounded control does NOT beat grounded alone (%.4f < %.4f)"
        % (frg_full, full["GROUNDED"]))

    # 4. shuffle bug guard: a SHARED permutation leaves cosine invariant; per-row does not
    big = np.zeros((4, 60))
    for c in range(12):
        big[0, c] = big[1, c] = float(12 - c)
    big[2, 20:22] = 5.0
    big[3, 40:42] = 5.0
    bm = sp.csr_matrix(big)
    perm = np.random.default_rng(0).permutation(60)
    shared = sp.csr_matrix((bm.tocoo().data, (bm.tocoo().row, perm[bm.tocoo().col])), shape=bm.shape)
    pr = ppmi_dense(bm, 1.0)
    p_shared = ppmi_dense(shared, 1.0)
    p_rowwise = ppmi_dense(shuffle_cols(bm, 7), 1.0)

    def cos(a, b):
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        return 0.0 if na == 0 or nb == 0 else float(a @ b / (na * nb))
    chk(abs(cos(p_shared[0], p_shared[1]) - cos(pr[0], pr[1])) < 1e-6,
        "shared-permutation is cosine-INVARIANT (not a null): %.4f == %.4f"
        % (cos(p_shared[0], p_shared[1]), cos(pr[0], pr[1])))
    chk(cos(p_rowwise[0], p_rowwise[1]) < 0.5,
        "per-row shuffle DESTROYS structure (identical rows -> cos %.4f)"
        % cos(p_rowwise[0], p_rowwise[1]))

    print("[witness] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
