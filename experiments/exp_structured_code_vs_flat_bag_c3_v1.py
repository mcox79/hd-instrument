"""exp_structured_code_vs_flat_bag_c3_v1 -- DOES A STRUCTURED (DEPENDENCY-RELATION-BOUND
CONJUNCTIVE) CODE BEAT THE FLAT BAG-OF-CONTEXT-WORDS ON THE LIVE C3 OPEN-VOCABULARY KNOWN-ANSWER
READ-OUT?

PRE-REG: preregs/2026-08-14_exp_structured_code_vs_flat_bag_c3_v1.md, COMMITTED BEFORE this ran.

WHY THIS CELL, NOT A NEW MECHANISM (reuse before build). Three floored synthetic results say
structured/conjunctive/permutation codes beat additive/flat bags at resisting crosstalk
(exp_role_filler_factorization_compgen_v1, exp_interference_avoidance_conjunctive_vs_additive_v1,
exp_substrate_permutation_binding_multiocc_v2_full -- all re-verified on disk, see prereg section
0), but none of them ran on real text or the live reader. We already own an organ that performs
the real-text version of this swap: hdlab.reading_grounding_loop.StructuralEncoder /
structural_vector_masked (2026-08-13), a drop-in replacement for context_vector_masked that
encodes sign(sum(bind(REL_vec, filler_vec))) over 1-hop UD-dependency relations instead of a flat
sum of nearby content words. It was already tested once, full-scale, in
exp_structured_comparator_v1.py -- but gated on a HAND-SCORED MEANINGFUL delta that was
arithmetically incapable of returning a non-null (1 MEANINGFUL row in 100; STANDING DISCIPLINE 1
in notes/STATUS_LESSONS.md names that cell explicitly and prescribes a known-answer-recall gate
instead). This cell is that reopening: same encoder swap, unmodified, scored on the SAME
known-answer C3 harness that produced the 4.80% headline, instead of a hand-score.

BRAIN FIDELITY SCOPE (prereg section 1): the structured code here is OUR ENGINEERING CHOICE, not
a pinned brain algorithm. Perirhinal conjunctive coding is UNPINNED as an equation and the
feature-ambiguity account is CONTESTED with real failed replications; role-binding itself is
UNPINNED and three-ways contested. Whichever way this cell's result falls, it is not evidence
about brain fidelity, only about whether THIS structured encoding helps THIS task.

REUSES the harness, does not reinvent it: corpus/buckets/item construction/gold sets are imported
directly from experiments/exp_grounding_readout_known_answer_v1.py (C3). paired_bootstrap,
_score_space, _digest, _lcp are imported directly from
experiments/exp_graded_path_vs_orthographic_floor_v1.py (GP) rather than re-implemented. The
trigram/string-control matrix is imported from experiments/exp_meaning_supply_separation_v1.py
(MS.trigram_matrix), bit-identical to tools/c3_gate.py's own string_form_profile, so the
A5_STRINGCTRL arm doubles as the mandatory C3-gate guard. MS.build_salted_space supplies the
flat arm's between-random-projection-draw control; the structured arm's own projection-draw
control reuses the SAME cached dependency-parse features (StructuralEncoder.features is
deterministic and memoized) and only re-draws the REL/filler symbol vectors under a different
salt, so no re-parsing is needed for the spread control.

READ-ONLY on data/foundation/*. No hdlab default is touched or changed. Wires nothing -- this
cell MEASURES; wiring is a separate decision after a verdict.

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity = tmp_replace; SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint via tools/exp_checkpoint, resume-safe, sorted(set()) only
# - arms-must-differ: sha256 digest over each arm's correctness vector
# - floors are ARMS, not assertions
# - positive control: SR_BASE / SR_STRUCT self-retrieval >= 0.70 or the matched floor comparison
#   is VOID_PLUMBING
# - print-progress flushing (Sec 17): flush=True progress line every 250 lemmas / 500 items
ASCII-only.

Run:  .venv/Scripts/python.exe experiments/exp_structured_code_vs_flat_bag_c3_v1.py [--smoke|--self-test]
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

import hdlab.reading_grounding_loop as RGL  # noqa: E402
from hdlab.reading_grounding_loop import (  # noqa: E402
    normalize_lemma, StructuralEncoder, structural_vector_masked, context_vector_masked,
)
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
import experiments.exp_graded_path_vs_orthographic_floor_v1 as GP  # noqa: E402
from tools.exp_checkpoint import record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_structured_code_vs_flat_bag_c3_v1"
PREREG_PATH = "preregs/2026-08-14_exp_structured_code_vs_flat_bag_c3_v1.md"
MASTER_SEED = C3.MASTER_SEED
N_BOOT = 5000
N_PROJ_DRAWS = 3
SELF_RETRIEVAL_FLOOR = 0.70
SR_MAX = 300


def _out_dir(smoke: bool) -> str:
    name = ANCHOR_NAME + ("_smoke" if smoke else "")
    p = os.path.join(_REPO, "data", name)
    os.makedirs(p, exist_ok=True)
    return p


# ------------------------------------------------------------------ structured encoding helpers
def _encode_from_features(feats: List[Tuple[str, str]], symbol_fn, d: int) -> np.ndarray:
    """sum(bind(symbol_fn(REL), symbol_fn(filler))), sign-quantised only if GRADED_COMPARATOR is
    off -- the EXACT math of StructuralEncoder.vector() (post 2026-08-15 graded-switch fix),
    factored so it can be driven by a SALTED symbol_fn for the projection-draw control without
    re-parsing anything. self_test() proves this reproduces StructuralEncoder.vector() byte-for-
    byte when symbol_fn is the canonical RGL.symbol_vector."""
    if not feats:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for rel, filler in feats:
        acc += symbol_fn("REL:" + rel) * symbol_fn(filler)
    if RGL.GRADED_COMPARATOR:
        return acc
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def _salted_symbol_vector(sym: str, salt: str, d: int, cache: Dict[str, np.ndarray]) -> np.ndarray:
    key = salt + "|" + sym
    v = cache.get(key)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
        cache[key] = v
    return v


def selftest_local_encoding_matches_structural_encoder() -> dict:
    """Prove _encode_from_features(feats, canonical RGL.symbol_vector) reproduces the REAL
    StructuralEncoder.vector() bit-for-bit on a small fixture, so the salted projection-draw
    variant (same function, salted symbol_fn) differs from canonical ONLY in the symbol draw."""
    enc = StructuralEncoder(_REPO, d=32)
    sents = [
        "The artery carries blood to the heart.",
        "Boats travel through the valley past the bridge to the sea.",
        "She read verses from a book of poems at the library.",
    ]
    ok_all = True
    detail = []
    for s in sents:
        for lemma in ("artery", "blood", "boat", "valley", "book", "verse"):
            feats = enc.features(s, lemma)
            local = _encode_from_features(feats, lambda sym: RGL.symbol_vector(sym, enc.d), enc.d)
            real = enc.vector(s, lemma)
            ok = bool(np.array_equal(local, real))
            ok_all = ok_all and ok
            detail.append({"sent": s[:30], "lemma": lemma, "n_feats": len(feats), "ok": ok})
    return {"ok": ok_all, "detail": detail}


def self_test() -> int:
    print("[self-test] checking local structured-encoding reproduction of StructuralEncoder.vector...",
          flush=True)
    r = selftest_local_encoding_matches_structural_encoder()
    print("[self-test]", json.dumps(r, indent=1), flush=True)
    assert r["ok"], "local _encode_from_features diverges from the real StructuralEncoder.vector"
    print("[self-test] PASS", flush=True)
    return 0


# ------------------------------------------------------------------ space builders
def build_space_structured(sents: List[str], buckets: Dict[str, List[int]], encoder: StructuralEncoder,
                           output_dir: str) -> RGL.ConceptSpace:
    sp = RGL.ConceptSpace(d=encoder.d)
    t0 = time.time()
    lemmas = sorted(buckets)
    for k, w in enumerate(lemmas):
        for i in buckets[w][:C3._n_profile(len(buckets[w]))]:
            sp.observe(w, structural_vector_masked(sents[i], w, encoder))
        if k % 250 == 0 or k == len(lemmas) - 1:
            print("[space_struct] %d/%d lemmas elapsed=%.1fs n_parsed=%d" %
                  (k + 1, len(lemmas), time.time() - t0, encoder.n_parsed), flush=True)
            record_unit(output_dir, unit_key("space_struct", str(k + 1)),
                        {"k": k + 1, "n_parsed": encoder.n_parsed})
    return sp


def build_salted_structural_space(sents: List[str], buckets: Dict[str, List[int]],
                                  encoder: StructuralEncoder, salt: str,
                                  output_dir: str) -> RGL.ConceptSpace:
    """Re-draws the REL/filler symbol codebook under `salt`; reuses encoder.features()'s cached
    parses (deterministic, no RNG), so no re-parsing occurs -- only the bind+sum is redone."""
    sp = RGL.ConceptSpace(d=encoder.d)
    cache: Dict[str, np.ndarray] = {}

    def symbol_fn(sym: str) -> np.ndarray:
        return _salted_symbol_vector(sym, salt, encoder.d, cache)

    t0 = time.time()
    lemmas = sorted(buckets)
    for k, w in enumerate(lemmas):
        for i in buckets[w][:C3._n_profile(len(buckets[w]))]:
            feats = encoder.features(sents[i], w)
            sp.observe(w, _encode_from_features(feats, symbol_fn, encoder.d))
        if k % 1000 == 0 or k == len(lemmas) - 1:
            print("[projdraw_struct salt=%r] %d/%d elapsed=%.1fs" % (salt, k + 1, len(lemmas),
                                                                      time.time() - t0), flush=True)
    return sp


def _self_retrieval_structured(items: List[dict], sents: List[str], anchors: List[str],
                               pos: Dict[str, int], mat: np.ndarray, encoder: StructuralEncoder,
                               seed: int) -> Tuple[float, int]:
    rng = np.random.default_rng(seed)
    hits, n = 0, 0
    for it in items[:min(SR_MAX, len(items))]:
        L = it["L"]
        if it["sent_idx"] is None or L not in pos:
            continue
        other = anchors[int(rng.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (other == L or C3._is_variant(other, L)):
            other = anchors[int(rng.integers(len(anchors)))]
            tries += 1
        if other == L or other not in pos:
            continue
        q = structural_vector_masked(sents[it["sent_idx"]], L, encoder)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        cands = [L, other]
        cvecs = np.stack([mat[pos[c]] for c in cands], axis=0)
        cn = np.linalg.norm(cvecs, axis=1)
        ok = cn >= 1e-9
        if not ok.all():
            continue
        sc = (cvecs @ q) / (cn * qn)
        pick = cands[int(np.argmax(sc))]
        hits += int(pick == L)
        n += 1
    return (hits / max(1, n)), n


def _margin_block(marg: np.ndarray) -> dict:
    return {"mean": float(np.mean(marg)), "median": float(np.median(marg))}


def run(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    smoke = run_mode == "smoke"
    max_items = MS.SMOKE_MAX_ITEMS if smoke else C3.MAX_ITEMS

    assert RGL.GRADED_COMPARATOR is True, (
        "GRADED_COMPARATOR is False at import time -- the live default has changed again since "
        "this cell was written (2026-08-14). STOP: A1_BASE cannot be interpreted as the 0.0480 "
        "headline reproduction under that condition.")

    sents = C3.build_corpus("full" if not smoke else "smoke")
    buckets, counts = C3.build_buckets(sents)
    print("[corpus] n_sentences=%d n_candidate_lemmas=%d elapsed=%.1fs" %
          (len(sents), len(buckets), time.time() - t0), flush=True)

    # ---- A1_BASE: flat bag, live default, unmodified
    space_base = C3.build_space(sents, buckets, output_dir)
    anchors, mat_base = space_base.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    print("[space_base] n_anchors=%d elapsed=%.1fs" % (n_anchors, time.time() - t0), flush=True)

    items, diag = C3.build_items(space_base, buckets, counts, max_items)
    n = len(items)
    print("[build] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0),
          flush=True)

    mat_base_nrm = np.linalg.norm(mat_base, axis=1)
    mat_base_ok = mat_base_nrm >= 1e-9

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])

    gold_fn = C3.gold_meaning_set

    hits_base, ranks_base, top50_base, marg_base, picks_base = GP._score_space(
        anchors, pos, mat_base, mat_base_nrm, mat_base_ok, norm2idx, items, gold_fn, output_dir,
        "BASE")

    # ---- A2_STRUCTURED: dependency-relation-bound conjunctive code, same buckets/items/gold
    encoder = StructuralEncoder(_REPO, d=RGL.CTX_D)
    space_struct = build_space_structured(sents, buckets, encoder, output_dir)
    anchors_s, mat_struct = space_struct.anchor_matrix()
    assert anchors_s == anchors, "structured space's anchor set diverges from the flat space's"
    mat_struct_nrm = np.linalg.norm(mat_struct, axis=1)
    mat_struct_ok = mat_struct_nrm >= 1e-9
    print("[space_struct] done elapsed=%.1fs %s" % (time.time() - t0, json.dumps(encoder.stats())),
          flush=True)

    hits_struct, ranks_struct, top50_struct, marg_struct, picks_struct = GP._score_space(
        anchors, pos, mat_struct, mat_struct_nrm, mat_struct_ok, norm2idx, items, gold_fn,
        output_dir, "STRUCT")

    # ---- orthographic / frequency floors (arm-independent: pure string/count features)
    t_mat, t_cov = MS.trigram_matrix(anchors)
    trig_hits = np.zeros(n, dtype=bool)
    trig_ranks = np.zeros(n, dtype=np.int64)
    trig_top50 = np.zeros(n, dtype=bool)
    trig_marg = np.zeros(n, dtype=np.float64)
    pre_hits = np.zeros(n, dtype=bool)
    pre_ranks = np.zeros(n, dtype=np.int64)
    pre_top50 = np.zeros(n, dtype=bool)
    pre_marg = np.zeros(n, dtype=np.float64)
    freq_hits = np.zeros(n, dtype=bool)
    anchor_arr = np.array(anchors)
    alen = np.array([len(a) for a in anchors], dtype=np.float64)

    for i, it in enumerate(items):
        L = it["L"]
        gold = gold_fn(L)
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + ([pos[L]] if L in pos else []))):
            elig[k] = False
        elig_t = elig & t_cov
        sel_t = np.flatnonzero(elig_t)
        if sel_t.size and (t_cov[pos.get(L, -1)] if L in pos else False):
            tq = t_mat[pos[L]]
            sc = t_mat[sel_t] @ tq
            b = int(np.argmax(sc))
            pick = anchor_arr[sel_t[b]]
            trig_hits[i] = str(pick) in gold
            gsel = np.array([j for j, a in enumerate(sel_t) if anchors[a] in gold], dtype=np.int64)
            if gsel.size:
                bg = float(np.max(sc[gsel]))
                trig_ranks[i] = int(np.sum(sc > bg)) + 1
                trig_top50[i] = trig_ranks[i] <= 50
                ng = np.ones(sel_t.size, dtype=bool)
                ng[gsel] = False
                trig_marg[i] = (bg - float(np.max(sc[ng]))) if ng.any() else 0.0
            else:
                trig_ranks[i] = sel_t.size

        sel = np.flatnonzero(elig)
        if sel.size and L in pos:
            pre = np.array([GP._lcp(L, anchors[a]) for a in sel], dtype=np.float64)
            pre = pre / np.maximum(np.maximum(alen[sel], len(L)), 1.0)
            b = int(np.argmax(pre))
            pick = anchor_arr[sel[b]]
            pre_hits[i] = str(pick) in gold
            gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)
            if gsel.size:
                bg = float(np.max(pre[gsel]))
                pre_ranks[i] = int(np.sum(pre > bg)) + 1
                pre_top50[i] = pre_ranks[i] <= 50
                ng = np.ones(sel.size, dtype=bool)
                ng[gsel] = False
                pre_marg[i] = (bg - float(np.max(pre[ng]))) if ng.any() else 0.0
            else:
                pre_ranks[i] = sel.size

            cnts = np.array([counts[anchors[a]] for a in sel])
            fb = int(np.argmax(cnts))
            freq_hits[i] = anchor_arr[sel[fb]] in gold

        if (i + 1) % 500 == 0:
            print("[floors] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    # ---- scramble floors, matched per arm (fixed donor permutation, shared across arms)
    rng_scr = np.random.default_rng(MASTER_SEED + 21)
    donor = rng_scr.permutation(n)
    scr_base = np.zeros(n, dtype=bool)
    scr_struct = np.zeros(n, dtype=bool)
    for i, it in enumerate(items):
        L = it["L"]
        if L not in pos:
            continue
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            continue
        donor_L = items[int(donor[i])]["L"]
        if donor_L not in pos:
            continue
        gold = gold_fn(L)
        qb, qs = mat_base[pos[donor_L]], mat_struct[pos[donor_L]]
        qbn, qsn = float(np.linalg.norm(qb)), float(np.linalg.norm(qs))
        if qbn >= 1e-9:
            sc = (mat_base[sel] @ qb) / (mat_base_nrm[sel] * qbn)
            scr_base[i] = anchor_arr[sel[int(np.argmax(sc))]] in gold
        if qsn >= 1e-9:
            sc = (mat_struct[sel] @ qs) / (mat_struct_nrm[sel] * qsn)
            scr_struct[i] = anchor_arr[sel[int(np.argmax(sc))]] in gold

    # ---- between-random-projection-draw spread
    proj_base: List[float] = []
    for r in range(N_PROJ_DRAWS):
        sp = MS.build_salted_space(sents, buckets, "PROJDRAW_%d|" % r, output_dir)
        an2, m2 = sp.anchor_matrix()
        p2 = {a: j for j, a in enumerate(an2)}
        nr2 = np.linalg.norm(m2, axis=1)
        ok2 = nr2 >= 1e-9
        n2idx: Dict[str, List[int]] = defaultdict(list)
        for a in an2:
            n2idx[normalize_lemma(a)].append(p2[a])
        h = np.zeros(n, dtype=bool)
        for i, it in enumerate(items):
            L = it["L"]
            if L not in p2:
                continue
            gold = gold_fn(L)
            base_e = np.ones(len(an2), dtype=bool)
            for k in sorted(set(n2idx[normalize_lemma(L)] + [p2[L]])):
                base_e[k] = False
            e = base_e & ok2
            sel2 = np.flatnonzero(e)
            q2 = m2[p2[L]]
            qn2 = float(np.linalg.norm(q2))
            if sel2.size and qn2 >= 1e-9:
                sc = (m2[sel2] @ q2) / (nr2[sel2] * qn2)
                h[i] = an2[sel2[int(np.argmax(sc))]] in gold
        proj_base.append(float(h.mean()))
        print("[projdraw_base] draw=%d hit@1=%.4f" % (r, proj_base[-1]), flush=True)
        record_unit(output_dir, unit_key("projdraw_base", str(r)), {"hit_at_1": proj_base[-1]})

    proj_struct: List[float] = []
    for r in range(N_PROJ_DRAWS):
        sp = build_salted_structural_space(sents, buckets, encoder, "STRUCT_PROJDRAW_%d|" % r,
                                           output_dir)
        an2, m2 = sp.anchor_matrix()
        p2 = {a: j for j, a in enumerate(an2)}
        nr2 = np.linalg.norm(m2, axis=1)
        ok2 = nr2 >= 1e-9
        n2idx = defaultdict(list)
        for a in an2:
            n2idx[normalize_lemma(a)].append(p2[a])
        h = np.zeros(n, dtype=bool)
        for i, it in enumerate(items):
            L = it["L"]
            if L not in p2:
                continue
            gold = gold_fn(L)
            base_e = np.ones(len(an2), dtype=bool)
            for k in sorted(set(n2idx[normalize_lemma(L)] + [p2[L]])):
                base_e[k] = False
            e = base_e & ok2
            sel2 = np.flatnonzero(e)
            q2 = m2[p2[L]]
            qn2 = float(np.linalg.norm(q2))
            if sel2.size and qn2 >= 1e-9:
                sc = (m2[sel2] @ q2) / (nr2[sel2] * qn2)
                h[i] = an2[sel2[int(np.argmax(sc))]] in gold
        proj_struct.append(float(h.mean()))
        print("[projdraw_struct] draw=%d hit@1=%.4f" % (r, proj_struct[-1]), flush=True)
        record_unit(output_dir, unit_key("projdraw_struct", str(r)), {"hit_at_1": proj_struct[-1]})

    # ---- known-answer / positive control
    sr_base, sr_n_base = GP._self_retrieval(items, sents, anchors, pos, mat_base, True,
                                            MASTER_SEED + 9)
    sr_struct, sr_n_struct = _self_retrieval_structured(items, sents, anchors, pos, mat_struct,
                                                         encoder, MASTER_SEED + 9)
    print("[self-retrieval] BASE=%.4f (n=%d) STRUCT=%.4f (n=%d) floor=%.2f" %
          (sr_base, sr_n_base, sr_struct, sr_n_struct, SELF_RETRIEVAL_FLOOR), flush=True)

    # ---- assemble arms + bootstrap
    arms = {
        "A1_BASE": hits_base.astype(float),
        "A2_STRUCTURED": hits_struct.astype(float),
        "A5_STRINGCTRL": trig_hits.astype(float),
        "A7_PREFIX_ONLY": pre_hits.astype(float),
        "F_FREQUENCY": freq_hits.astype(float),
        "F_SCRAMBLE_BASE": scr_base.astype(float),
        "F_SCRAMBLE_STRUCT": scr_struct.astype(float),
    }
    deltas = [
        ("d_A2_STRUCTURED_minus_A1_BASE", "A2_STRUCTURED", "A1_BASE"),
        ("d_A2_STRUCTURED_minus_BASE", "A2_STRUCTURED", "A1_BASE"),          # c3_gate literal alias
        ("d_A1_BASE_minus_A5_STRINGCTRL", "A1_BASE", "A5_STRINGCTRL"),
        ("d_A2_STRUCTURED_minus_A5_STRINGCTRL", "A2_STRUCTURED", "A5_STRINGCTRL"),
        ("d_A1_BASE_minus_A7_PREFIX_ONLY", "A1_BASE", "A7_PREFIX_ONLY"),
        ("d_A2_STRUCTURED_minus_A7_PREFIX_ONLY", "A2_STRUCTURED", "A7_PREFIX_ONLY"),
        ("d_A1_BASE_minus_F_FREQUENCY", "A1_BASE", "F_FREQUENCY"),
        ("d_A2_STRUCTURED_minus_F_FREQUENCY", "A2_STRUCTURED", "F_FREQUENCY"),
        ("d_A1_BASE_minus_F_SCRAMBLE_BASE", "A1_BASE", "F_SCRAMBLE_BASE"),
        ("d_A1_BASE_minus_F_SCRAMBLE", "A1_BASE", "F_SCRAMBLE_BASE"),        # c3_gate literal alias
        ("d_A2_STRUCTURED_minus_F_SCRAMBLE_STRUCT", "A2_STRUCTURED", "F_SCRAMBLE_STRUCT"),
    ]
    bs = GP.paired_bootstrap(arms, deltas, N_BOOT, MASTER_SEED + 5)

    digests = {k: GP._digest(v) for k, v in arms.items()}
    dupe_groups = defaultdict(list)
    for k, dg in digests.items():
        dupe_groups[dg].append(k)
    collisions = {dg: v for dg, v in dupe_groups.items() if len(v) > 1}

    per_arm = {
        "A1_BASE": {"hit_at_1": float(hits_base.mean()), "median_rank": float(np.median(ranks_base)),
                    "frac_gold_in_top50": float(top50_base.mean()),
                    "separation_margin_z": _margin_block(marg_base), "tautology_rate": 0.0,
                    "example_picks": picks_base[:12]},
        "A2_STRUCTURED": {"hit_at_1": float(hits_struct.mean()),
                          "median_rank": float(np.median(ranks_struct)),
                          "frac_gold_in_top50": float(top50_struct.mean()),
                          "separation_margin_z": _margin_block(marg_struct), "tautology_rate": 0.0,
                          "example_picks": picks_struct[:12]},
        "A5_STRINGCTRL": {"hit_at_1": float(trig_hits.mean()), "median_rank": float(np.median(trig_ranks)),
                          "frac_gold_in_top50": float(trig_top50.mean()),
                          "separation_margin_z": _margin_block(trig_marg), "tautology_rate": 0.0},
        "A7_PREFIX_ONLY": {"hit_at_1": float(pre_hits.mean()), "median_rank": float(np.median(pre_ranks)),
                           "frac_gold_in_top50": float(pre_top50.mean()),
                           "separation_margin_z": _margin_block(pre_marg), "tautology_rate": 0.0},
        "F_FREQUENCY": {"hit_at_1": float(freq_hits.mean())},
        "F_SCRAMBLE_BASE": {"hit_at_1": float(scr_base.mean())},
        "F_SCRAMBLE_STRUCT": {"hit_at_1": float(scr_struct.mean())},
    }

    a1_reproduces_headline = abs(per_arm["A1_BASE"]["hit_at_1"] - 0.048) < 1e-9

    proj_base_sd, proj_struct_sd = float(np.std(proj_base)), float(np.std(proj_struct))
    d_struct_base = bs["deltas"]["d_A2_STRUCTURED_minus_A1_BASE"]
    structure_helps = bool(d_struct_base["ci_excludes_zero"] and d_struct_base["delta"] > 0
                           and abs(d_struct_base["delta"]) > max(proj_base_sd, proj_struct_sd))
    structure_hurts = bool(d_struct_base["ci_excludes_zero"] and d_struct_base["delta"] < 0
                           and abs(d_struct_base["delta"]) > max(proj_base_sd, proj_struct_sd))

    sr_ok_base = sr_base >= SELF_RETRIEVAL_FLOOR and sr_n_base >= 30
    sr_ok_struct = sr_struct >= SELF_RETRIEVAL_FLOOR and sr_n_struct >= 30

    def _clears_floor(arm_key: str, scr_key: str) -> Optional[bool]:
        d1 = bs["deltas"].get("d_%s_minus_A5_STRINGCTRL" % arm_key)
        d2 = bs["deltas"].get("d_%s_minus_F_FREQUENCY" % arm_key)
        d3 = bs["deltas"].get("d_%s_minus_%s" % (arm_key, scr_key))
        if d1 is None or d2 is None or d3 is None:
            return None
        return bool(d1["ci_excludes_zero"] and d1["delta"] > 0
                   and d2["ci_excludes_zero"] and d2["delta"] > 0
                   and d3["ci_excludes_zero"] and d3["delta"] > 0)

    base_clears = _clears_floor("A1_BASE", "F_SCRAMBLE_BASE")
    struct_clears = _clears_floor("A2_STRUCTURED", "F_SCRAMBLE_STRUCT")

    if not a1_reproduces_headline:
        verdict = "HARNESS_MISMATCH_STOP"
        verdict_msg = ("A1_BASE=%.6f does NOT reproduce the 0.0480 C3 headline within 1e-9 -- "
                      "harness-integrity gate FAILED, no conclusion drawn about structured vs "
                      "flat." % per_arm["A1_BASE"]["hit_at_1"])
    elif not (sr_ok_base and sr_ok_struct):
        verdict = "VOID_PLUMBING_SELF_RETRIEVAL"
        verdict_msg = ("self-retrieval positive control below floor %.2f: BASE=%.4f(n=%d) "
                      "STRUCT=%.4f(n=%d) -- instrument sanity check failed, floor comparisons "
                      "are VOID_PLUMBING." % (SELF_RETRIEVAL_FLOOR, sr_base, sr_n_base,
                                              sr_struct, sr_n_struct))
    elif structure_helps and struct_clears:
        verdict = "STRUCTURE_WINS_CLEARS_FLOOR"
        verdict_msg = ("STRUCTURED beats BASE by %.4f (CI [%.4f,%.4f], exceeds projdraw sd "
                      "base=%.4f struct=%.4f) AND clears max(string,freq,scramble)." %
                      (d_struct_base["delta"], d_struct_base["ci_lo"], d_struct_base["ci_hi"],
                       proj_base_sd, proj_struct_sd))
    elif structure_helps:
        verdict = "STRUCTURE_HELPS_BUT_STILL_BELOW_FLOOR"
        verdict_msg = ("STRUCTURED beats BASE by %.4f (CI [%.4f,%.4f], exceeds projdraw sd "
                      "base=%.4f struct=%.4f) but does NOT clear max(string,freq,scramble)." %
                      (d_struct_base["delta"], d_struct_base["ci_lo"], d_struct_base["ci_hi"],
                       proj_base_sd, proj_struct_sd))
    elif structure_hurts:
        verdict = "STRUCTURE_HURTS"
        verdict_msg = ("STRUCTURED is BELOW BASE by %.4f (CI [%.4f,%.4f])." %
                      (d_struct_base["delta"], d_struct_base["ci_lo"], d_struct_base["ci_hi"]))
    else:
        verdict = "STRUCTURE_DOES_NOT_HELP"
        verdict_msg = ("delta=%.4f CI=[%.4f,%.4f] vs projdraw_sd base=%.4f struct=%.4f -- either "
                      "CI does not exclude zero or the delta does not exceed the between-draw "
                      "spread. base_clears_floor=%s struct_clears_floor=%s" %
                      (d_struct_base["delta"], d_struct_base["ci_lo"], d_struct_base["ci_hi"],
                       proj_base_sd, proj_struct_sd, base_clears, struct_clears))

    rep = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "prereg": PREREG_PATH,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "GRADED_COMPARATOR_at_import": bool(RGL.GRADED_COMPARATOR),
        "n_items": n, "n_anchors": n_anchors, "item_construction": diag,
        "encoder_stats": encoder.stats(),
        "a1_base_reproduces_c3_headline_0480_exactly": a1_reproduces_headline,
        "self_retrieval": {"BASE": {"acc": sr_base, "n": sr_n_base, "ok": bool(sr_ok_base)},
                           "STRUCT": {"acc": sr_struct, "n": sr_n_struct, "ok": bool(sr_ok_struct)},
                           "floor": SELF_RETRIEVAL_FLOOR},
        "projdraw": {"BASE": {"draws": proj_base, "sd": proj_base_sd},
                    "STRUCT": {"draws": proj_struct, "sd": proj_struct_sd}},
        "bootstrap": bs,
        "per_arm": per_arm,
        "arm_digests": digests,
        "arms_must_differ": {"ok": len(collisions) == 0, "collisions": collisions},
        "base_clears_floor": base_clears,
        "struct_clears_floor": struct_clears,
        "structure_helps": structure_helps,
        "structure_hurts": structure_hurts,
        "tautology_rate": 0.0,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(output_dir, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print(json.dumps(per_arm, indent=1))
    print(json.dumps(bs["deltas"], indent=1))
    print("VERDICT:", verdict)
    print("VERDICT_MSG:", verdict_msg)
    print("WROTE", p)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else "full"
    output_dir = _out_dir(args.smoke)
    run(run_mode, output_dir)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        out = _out_dir("--smoke" in sys.argv)
        crash = os.path.join(out, "_crash_diagnostic.json")
        with open(crash + ".tmp", "w", encoding="utf-8") as fh:
            json.dump({"anchor_name": ANCHOR_NAME, "error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        os.replace(crash + ".tmp", crash)
        raise
