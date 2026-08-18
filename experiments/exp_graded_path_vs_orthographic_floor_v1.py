"""exp_graded_path_vs_orthographic_floor_v1 -- DOES THE GRADED PATH (ALREADY ON BY DEFAULT) CLEAR
THE ORTHOGRAPHIC FLOOR, AND WOULD TURNING IT OFF HAVE SCORED DIFFERENTLY, ON THE IDENTICAL C3
HARNESS?

PRE-REG: preregs/2026-08-14_exp_graded_path_vs_orthographic_floor_v1.md, COMMITTED BEFORE this ran.
Section 0 of that file records a PREMISE CORRECTION: the dispatch brief that produced this cell
assumed `GRADED_COMPARATOR` (hdlab/reading_grounding_loop.py:103) is default-OFF. It is not --
commit 38f7a0d5c flipped it to default-ON, and the 0.0480 "ours" headline this cell compares
against the 0.0870 trigram floor was ALREADY measured with graded ON
(data/exp_grounding_readout_known_answer_v1/metrics.json: graded_comparator=true,
HD_GRADED_COMPARATOR_env=1, ts_iso AFTER the flip commit). So "A1_GRADED_ON" here is a
REPRODUCTION (harness-integrity check), and "A9_GRADED_OFF" is the genuinely NOVEL arm: the
pre-flip signed/ternary comparator, never before measured on this open-vocabulary pool/scorer.

ONE VARIABLE. `ConceptSpace.observe()` always accumulates the raw graded sum regardless of the
switch (hdlab/reading_grounding_loop.py:462-466) -- the switch only changes what `anchor_matrix()`
(:474) / `bundle()` (:496) RETURN. Because GRADED_COMPARATOR is read once at hdlab import time, it
cannot be toggled mid-process; this cell builds ONE ConceptSpace (always graded, since observe()
is switch-independent) and derives BOTH read-out views locally: A1_GRADED_ON = the raw sums
exactly as anchor_matrix()/bundle() return under the live default; A9_GRADED_OFF = np.sign() of
the same sums, byte-for-byte what anchor_matrix()/bundle() would return under
HD_GRADED_COMPARATOR=0 (plain np.sign, no zero-fix -- verified at :490/:504). This is a STRONGER
identity guarantee between arms than re-running the process twice with different env vars: same
corpus, same items, same eligibility, same gold sets, same seeds, by construction.

REUSES the harness, does not reinvent it: corpus/buckets/space/items/gold-set construction is
imported directly from experiments/exp_grounding_readout_known_answer_v1.py (C3), exactly as
tools/orthographic_floor_vet_v1.py already does. The trigram/string-control matrix is imported
from experiments/exp_meaning_supply_separation_v1.py (MS.trigram_matrix) -- bit-identical
construction to tools/c3_gate.py's own string_form_profile (same boundary chars, same hash, same
dim=512), so this cell's A5_STRINGCTRL arm doubles as the mandatory C3-gate guard. MS's
build_salted_space supplies the between-random-projection-draw control.

READ-ONLY on data/foundation/*. No hdlab default is touched or changed. Wires nothing.

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity = tmp_replace; SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint via tools/exp_checkpoint, resume-safe, sorted(set()) only
# - arms-must-differ: sha256 digest over each arm's correctness vector
# - floors are ARMS, not assertions
# - positive control: SR_ON / SR_OFF self-retrieval >= 0.70 or the matched floor comparison is
#   VOID_PLUMBING
ASCII-only.

Run:  .venv/Scripts/python.exe experiments/exp_graded_path_vs_orthographic_floor_v1.py [--smoke|--self-test]
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
from hdlab.reading_grounding_loop import normalize_lemma  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
from tools.exp_checkpoint import record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_graded_path_vs_orthographic_floor_v1"
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


def _lcp(a: str, b: str) -> int:
    k = 0
    for x, y in zip(a, b):
        if x != y:
            break
        k += 1
    return k


def _digest(hits: np.ndarray) -> str:
    return hashlib.sha256(hits.astype(np.int8).tobytes()).hexdigest()[:16]


def paired_bootstrap(arms: Dict[str, np.ndarray], deltas, n_boot: int, seed: int) -> dict:
    keys = sorted(arms)
    n = len(arms[keys[0]])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = {k: arms[k][idx].mean(axis=1) for k in keys}
    out = {"n_boot": n_boot, "seed": seed, "n_items": n, "arm_acc_ci": {}, "deltas": {}}
    for k in keys:
        out["arm_acc_ci"][k] = {"acc": float(arms[k].mean()),
                                 "ci_lo": float(np.percentile(boots[k], 2.5)),
                                 "ci_hi": float(np.percentile(boots[k], 97.5)),
                                 "sd": float(np.std(boots[k]))}
    for name, a, b in deltas:
        db = boots[a] - boots[b]
        lo, hi = float(np.percentile(db, 2.5)), float(np.percentile(db, 97.5))
        out["deltas"][name] = {"delta": float(arms[a].mean() - arms[b].mean()),
                                "ci_lo": lo, "ci_hi": hi, "sd": float(np.std(db)),
                                "ci_excludes_zero": bool(lo > 0 or hi < 0)}
    return out


def selftest_signed_matches_switch() -> dict:
    """Prove A9_GRADED_OFF's local np.sign derivation is byte-identical to what
    ConceptSpace.anchor_matrix()/bundle() actually return when GRADED_COMPARATOR is False --
    on a small fixture, by monkeypatching the module constant (not the environment, which is
    inert after import) and calling the REAL methods."""
    sp = RGL.ConceptSpace(d=16)
    rng = np.random.default_rng(0)
    for w in ("alpha", "beta", "gamma"):
        for _ in range(5):
            sp.observe(w, rng.normal(size=16))
    anchors_g, mat_g = sp.anchor_matrix()
    q_g = sp.bundle("alpha")
    local_signed_mat = np.sign(mat_g)
    local_signed_q = np.sign(q_g)

    prior = RGL.GRADED_COMPARATOR
    RGL.GRADED_COMPARATOR = False
    sp._mat_cache = None
    try:
        anchors_s, mat_s = sp.anchor_matrix()
        q_s = sp.bundle("alpha")
    finally:
        RGL.GRADED_COMPARATOR = prior
        sp._mat_cache = None
    ok_mat = bool(np.array_equal(mat_s, local_signed_mat))
    ok_q = bool(np.array_equal(q_s, local_signed_q))
    ok_anchors = anchors_s == anchors_g
    return {"ok": ok_mat and ok_q and ok_anchors, "ok_mat": ok_mat, "ok_q": ok_q,
            "ok_anchors": ok_anchors}


def self_test() -> int:
    print("[self-test] checking A9_GRADED_OFF derivation matches the real switch...", flush=True)
    r = selftest_signed_matches_switch()
    print("[self-test]", r, flush=True)
    assert r["ok"], "local np.sign derivation diverges from the real GRADED_COMPARATOR=False path"
    print("[self-test] PASS", flush=True)
    return 0


def _score_space(anchors: List[str], pos: Dict[str, int], mat: np.ndarray, mat_nrm: np.ndarray,
                 mat_ok: np.ndarray, norm2idx, items: List[dict], gold_fn, output_dir: str,
                 unit_prefix: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
    """One arm's hit@1 / rank / top50 / separation-margin over `items`, given a fixed
    (anchors, mat) field. `mat` may be graded or signed -- the caller decides which."""
    n = len(items)
    hits = np.zeros(n, dtype=bool)
    ranks = np.zeros(n, dtype=np.int64)
    top50 = np.zeros(n, dtype=bool)
    margins = np.zeros(n, dtype=np.float64)
    picks: List[str] = []
    anchor_arr = np.array(anchors)
    for i, it in enumerate(items):
        L = it["L"]
        gold = gold_fn(L)
        elig = mat_ok.copy()
        for k in sorted(set(norm2idx[normalize_lemma(L)] + ([pos[L]] if L in pos else []))):
            elig[k] = False
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            picks.append("")
            continue
        gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)
        if L not in pos:
            picks.append("")
            continue
        q = mat[pos[L]]
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            picks.append("")
            continue
        sc = (mat[sel] @ q) / (mat_nrm[sel] * qn)
        b = int(np.argmax(sc))
        pick = anchor_arr[sel[b]]
        picks.append(str(pick))
        hits[i] = str(pick) in gold
        if gsel.size:
            best_gold = float(np.max(sc[gsel]))
            ranks[i] = int(np.sum(sc > best_gold)) + 1
            top50[i] = ranks[i] <= 50
            ng = np.ones(sel.size, dtype=bool)
            ng[gsel] = False
            margins[i] = (best_gold - float(np.max(sc[ng]))) if ng.any() else 0.0
        else:
            ranks[i] = sel.size
        if (i + 1) % 500 == 0:
            print("[score:%s] %d/%d" % (unit_prefix, i + 1, n), flush=True)
            record_unit(output_dir, unit_key("score", unit_prefix, str(i + 1)), {"i": i + 1})
    return hits, ranks, top50, margins, picks


def _self_retrieval(items: List[dict], sents: List[str], anchors: List[str], pos: Dict[str, int],
                    mat: np.ndarray, graded: bool, seed: int) -> Tuple[float, int]:
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
        qraw = RGL.context_vector_masked(sents[it["sent_idx"]], L)
        q = qraw if graded else np.sign(qraw)
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


def run(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    max_items = MS.SMOKE_MAX_ITEMS if run_mode == "smoke" else C3.MAX_ITEMS

    assert RGL.GRADED_COMPARATOR is True, (
        "GRADED_COMPARATOR is False at import time -- the live default has changed again since "
        "this cell was written (2026-08-14, commit 38f7a0d5c set it True). STOP: the harness "
        "assumption this pre-reg documents no longer holds; do not interpret A1_GRADED_ON as a "
        "reproduction of the 0.0480 headline under that condition.")

    sents = C3.build_corpus("full" if run_mode != "smoke" else "smoke")
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, output_dir)
    anchors, mat_graded = space.anchor_matrix()          # raw, since GRADED_COMPARATOR True
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    items, diag = C3.build_items(space, buckets, counts, max_items)
    n = len(items)
    print("[build] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0),
          flush=True)

    mat_signed = np.sign(mat_graded)                     # what anchor_matrix() would give at OFF
    mat_g_nrm = np.linalg.norm(mat_graded, axis=1)
    mat_s_nrm = np.linalg.norm(mat_signed, axis=1)
    mat_g_ok = mat_g_nrm >= 1e-9
    mat_s_ok = mat_s_nrm >= 1e-9

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])

    gold_fn = C3.gold_meaning_set

    hits_on, ranks_on, top50_on, marg_on, picks_on = _score_space(
        anchors, pos, mat_graded, mat_g_nrm, mat_g_ok, norm2idx, items, gold_fn, output_dir, "ON")
    hits_off, ranks_off, top50_off, marg_off, picks_off = _score_space(
        anchors, pos, mat_signed, mat_s_nrm, mat_s_ok, norm2idx, items, gold_fn, output_dir, "OFF")

    # ---- trigram / string-control arm (also the mandatory C3-gate guard, A5_STRINGCTRL)
    t_mat, t_cov = MS.trigram_matrix(anchors)
    trig_hits = np.zeros(n, dtype=bool)
    trig_ranks = np.zeros(n, dtype=np.int64)
    trig_top50 = np.zeros(n, dtype=bool)
    trig_marg = np.zeros(n, dtype=np.float64)
    # ---- prefix arm
    pre_hits = np.zeros(n, dtype=bool)
    pre_ranks = np.zeros(n, dtype=np.int64)
    pre_top50 = np.zeros(n, dtype=bool)
    pre_marg = np.zeros(n, dtype=np.float64)
    # ---- frequency floor
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
        if sel_t.size and t_cov[pos.get(L, -1)] if L in pos else False:
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
            pre = np.array([_lcp(L, anchors[a]) for a in sel], dtype=np.float64)
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

        if (i + 1) % 1000 == 0:
            print("[floors] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    # ---- scramble floor, matched per arm (fixed donor permutation)
    rng_scr = np.random.default_rng(MASTER_SEED + 21)
    donor = rng_scr.permutation(n)
    scr_on = np.zeros(n, dtype=bool)
    scr_off = np.zeros(n, dtype=bool)
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
        qg, qs = mat_graded[pos[donor_L]], mat_signed[pos[donor_L]]
        qgn, qsn = float(np.linalg.norm(qg)), float(np.linalg.norm(qs))
        if qgn >= 1e-9:
            sc = (mat_graded[sel] @ qg) / (mat_g_nrm[sel] * qgn)
            scr_on[i] = anchor_arr[sel[int(np.argmax(sc))]] in gold
        if qsn >= 1e-9:
            sc = (mat_signed[sel] @ qs) / (mat_s_nrm[sel] * qsn)
            scr_off[i] = anchor_arr[sel[int(np.argmax(sc))]] in gold

    # ---- between-random-projection-draw spread, both graded and signed
    proj_on, proj_off = [], []
    for r in range(N_PROJ_DRAWS):
        sp = MS.build_salted_space(sents, buckets, "PROJDRAW_%d|" % r, output_dir)
        an2, m2g = sp.anchor_matrix()
        m2s = np.sign(m2g)
        p2 = {a: j for j, a in enumerate(an2)}
        nr2g, nr2s = np.linalg.norm(m2g, axis=1), np.linalg.norm(m2s, axis=1)
        ok2g, ok2s = nr2g >= 1e-9, nr2s >= 1e-9
        n2idx: Dict[str, List[int]] = defaultdict(list)
        for a in an2:
            n2idx[normalize_lemma(a)].append(p2[a])
        hg, hs = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
        for i, it in enumerate(items):
            L = it["L"]
            if L not in p2:
                continue
            gold = gold_fn(L)
            base_e = np.ones(len(an2), dtype=bool)
            for k in sorted(set(n2idx[normalize_lemma(L)] + [p2[L]])):
                base_e[k] = False
            eg, es = base_e & ok2g, base_e & ok2s
            selg, sels = np.flatnonzero(eg), np.flatnonzero(es)
            qg2, qs2 = m2g[p2[L]], m2s[p2[L]]
            qgn2, qsn2 = float(np.linalg.norm(qg2)), float(np.linalg.norm(qs2))
            if selg.size and qgn2 >= 1e-9:
                sc = (m2g[selg] @ qg2) / (nr2g[selg] * qgn2)
                hg[i] = an2[selg[int(np.argmax(sc))]] in gold
            if sels.size and qsn2 >= 1e-9:
                sc = (m2s[sels] @ qs2) / (nr2s[sels] * qsn2)
                hs[i] = an2[sels[int(np.argmax(sc))]] in gold
        proj_on.append(float(hg.mean()))
        proj_off.append(float(hs.mean()))
        print("[projdraw] draw=%d ON=%.4f OFF=%.4f" % (r, proj_on[-1], proj_off[-1]), flush=True)
        record_unit(output_dir, unit_key("projdraw", str(r)), {"on": proj_on[-1], "off": proj_off[-1]})

    # ---- known-answer / positive control, both graded and signed
    sr_on, sr_n_on = _self_retrieval(items, sents, anchors, pos, mat_graded, True, MASTER_SEED + 9)
    sr_off, sr_n_off = _self_retrieval(items, sents, anchors, pos, mat_signed, False, MASTER_SEED + 9)
    print("[self-retrieval] ON=%.4f (n=%d) OFF=%.4f (n=%d) floor=%.2f"
          % (sr_on, sr_n_on, sr_off, sr_n_off, SELF_RETRIEVAL_FLOOR), flush=True)

    # ---- assemble arms + bootstrap
    arms = {
        "A1_GRADED_ON": hits_on.astype(float),
        "A9_GRADED_OFF": hits_off.astype(float),
        "A5_STRINGCTRL": trig_hits.astype(float),
        "A7_PREFIX_ONLY": pre_hits.astype(float),
        "F_FREQUENCY": freq_hits.astype(float),
        "F_SCRAMBLE_ON": scr_on.astype(float),
        "F_SCRAMBLE_OFF": scr_off.astype(float),
    }
    deltas = [
        ("d_A1_GRADED_ON_minus_A9_GRADED_OFF", "A1_GRADED_ON", "A9_GRADED_OFF"),
        ("d_A1_GRADED_ON_minus_A5_STRINGCTRL", "A1_GRADED_ON", "A5_STRINGCTRL"),
        ("d_A9_GRADED_OFF_minus_A5_STRINGCTRL", "A9_GRADED_OFF", "A5_STRINGCTRL"),
        ("d_A1_GRADED_ON_minus_A7_PREFIX_ONLY", "A1_GRADED_ON", "A7_PREFIX_ONLY"),
        ("d_A1_GRADED_ON_minus_F_FREQUENCY", "A1_GRADED_ON", "F_FREQUENCY"),
        ("d_A9_GRADED_OFF_minus_F_FREQUENCY", "A9_GRADED_OFF", "F_FREQUENCY"),
        ("d_A1_GRADED_ON_minus_F_SCRAMBLE_ON", "A1_GRADED_ON", "F_SCRAMBLE_ON"),
        ("d_A9_GRADED_OFF_minus_F_SCRAMBLE_OFF", "A9_GRADED_OFF", "F_SCRAMBLE_OFF"),
    ]
    bs = paired_bootstrap(arms, deltas, N_BOOT, MASTER_SEED + 5)

    digests = {k: _digest(v) for k, v in arms.items()}
    dupe_groups = defaultdict(list)
    for k, dg in digests.items():
        dupe_groups[dg].append(k)
    arms_must_differ_ok = all(len(v) == 1 for v in dupe_groups.values()
                              if not (len(v) == 1))
    # more directly: any group with >1 member other than trivially-empty arms is a collision
    collisions = {dg: v for dg, v in dupe_groups.items() if len(v) > 1}

    def _margin_block(marg: np.ndarray) -> dict:
        return {"mean": float(np.mean(marg)), "median": float(np.median(marg))}

    per_arm = {
        "A1_GRADED_ON": {"hit_at_1": float(hits_on.mean()), "median_rank": float(np.median(ranks_on)),
                          "frac_gold_in_top50": float(top50_on.mean()),
                          "separation_margin_z": _margin_block(marg_on), "tautology_rate": 0.0,
                          "example_picks": picks_on[:12]},
        "A9_GRADED_OFF": {"hit_at_1": float(hits_off.mean()), "median_rank": float(np.median(ranks_off)),
                           "frac_gold_in_top50": float(top50_off.mean()),
                           "separation_margin_z": _margin_block(marg_off), "tautology_rate": 0.0,
                           "example_picks": picks_off[:12]},
        "A5_STRINGCTRL": {"hit_at_1": float(trig_hits.mean()), "median_rank": float(np.median(trig_ranks)),
                           "frac_gold_in_top50": float(trig_top50.mean()),
                           "separation_margin_z": _margin_block(trig_marg), "tautology_rate": 0.0},
        "A7_PREFIX_ONLY": {"hit_at_1": float(pre_hits.mean()), "median_rank": float(np.median(pre_ranks)),
                            "frac_gold_in_top50": float(pre_top50.mean()),
                            "separation_margin_z": _margin_block(pre_marg), "tautology_rate": 0.0},
        "F_FREQUENCY": {"hit_at_1": float(freq_hits.mean())},
        "F_SCRAMBLE_ON": {"hit_at_1": float(scr_on.mean())},
        "F_SCRAMBLE_OFF": {"hit_at_1": float(scr_off.mean())},
    }

    a1_reproduces_headline = abs(per_arm["A1_GRADED_ON"]["hit_at_1"] - 0.048) < 1e-9

    proj_on_sd, proj_off_sd = float(np.std(proj_on)), float(np.std(proj_off))
    d_on_off = bs["deltas"]["d_A1_GRADED_ON_minus_A9_GRADED_OFF"]
    graded_helps = bool(d_on_off["ci_excludes_zero"] and d_on_off["delta"] > 0
                        and abs(d_on_off["delta"]) > max(proj_on_sd, proj_off_sd))
    graded_hurts = bool(d_on_off["ci_excludes_zero"] and d_on_off["delta"] < 0
                        and abs(d_on_off["delta"]) > max(proj_on_sd, proj_off_sd))

    sr_ok_on = sr_on >= SELF_RETRIEVAL_FLOOR and sr_n_on >= 30
    sr_ok_off = sr_off >= SELF_RETRIEVAL_FLOOR and sr_n_off >= 30

    def _clears_floor(arm_key: str) -> Optional[bool]:
        d1 = bs["deltas"].get("d_%s_minus_A5_STRINGCTRL" % arm_key)
        d2 = bs["deltas"].get("d_%s_minus_F_FREQUENCY" % arm_key)
        scr_key = "F_SCRAMBLE_ON" if arm_key == "A1_GRADED_ON" else "F_SCRAMBLE_OFF"
        d3 = bs["deltas"].get("d_%s_minus_%s" % (arm_key, scr_key))
        if d1 is None or d2 is None or d3 is None:
            return None
        return bool(d1["ci_excludes_zero"] and d1["delta"] > 0
                    and d2["ci_excludes_zero"] and d2["delta"] > 0
                    and d3["ci_excludes_zero"] and d3["delta"] > 0)

    on_clears = _clears_floor("A1_GRADED_ON")
    off_clears = _clears_floor("A9_GRADED_OFF")

    if not a1_reproduces_headline:
        verdict = "HARNESS_MISMATCH_STOP"
        verdict_msg = ("A1_GRADED_ON=%.6f does NOT reproduce the 0.0480 C3 headline within 1e-9 -- "
                       "harness-integrity gate FAILED, no conclusion drawn about ON/OFF or the "
                       "floor." % per_arm["A1_GRADED_ON"]["hit_at_1"])
    elif not (sr_ok_on and sr_ok_off):
        verdict = "VOID_PLUMBING_SELF_RETRIEVAL"
        verdict_msg = ("self-retrieval positive control below floor %.2f: ON=%.4f(n=%d) "
                       "OFF=%.4f(n=%d) -- instrument sanity check failed, floor comparisons are "
                       "VOID_PLUMBING." % (SELF_RETRIEVAL_FLOOR, sr_on, sr_n_on, sr_off, sr_n_off))
    elif on_clears or off_clears:
        verdict = "CLEARS_ORTHOGRAPHIC_FLOOR"
        verdict_msg = "on_clears=%s off_clears=%s" % (on_clears, off_clears)
    else:
        verdict = "DOES_NOT_CLEAR_ORTHOGRAPHIC_FLOOR"
        parts = ["on_clears=%s off_clears=%s" % (on_clears, off_clears),
                "graded_helps=%s graded_hurts=%s (delta=%.4f CI=[%.4f,%.4f] vs projdraw_sd "
                "on=%.4f off=%.4f)" % (graded_helps, graded_hurts, d_on_off["delta"],
                                       d_on_off["ci_lo"], d_on_off["ci_hi"], proj_on_sd, proj_off_sd)]
        verdict_msg = " | ".join(parts)

    rep = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "prereg": "preregs/2026-08-14_exp_graded_path_vs_orthographic_floor_v1.md",
        "premise_correction": "GRADED_COMPARATOR is default-ON as of 38f7a0d5c, NOT default-OFF as "
                              "the dispatch brief assumed; A1_GRADED_ON is a reproduction, "
                              "A9_GRADED_OFF is the novel arm. See prereg section 0.",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "GRADED_COMPARATOR_at_import": bool(RGL.GRADED_COMPARATOR),
        "n_items": n, "n_anchors": n_anchors, "item_construction": diag,
        "a1_graded_on_reproduces_c3_headline_0480_exactly": a1_reproduces_headline,
        "self_retrieval": {"ON": {"acc": sr_on, "n": sr_n_on, "ok": bool(sr_ok_on)},
                           "OFF": {"acc": sr_off, "n": sr_n_off, "ok": bool(sr_ok_off)},
                           "floor": SELF_RETRIEVAL_FLOOR},
        "projdraw": {"ON": {"draws": proj_on, "sd": proj_on_sd},
                    "OFF": {"draws": proj_off, "sd": proj_off_sd}},
        "bootstrap": bs,
        "per_arm": per_arm,
        "arm_digests": digests,
        "arms_must_differ": {"ok": len(collisions) == 0, "collisions": collisions},
        "on_clears_floor": on_clears,
        "off_clears_floor": off_clears,
        "graded_helps": graded_helps,
        "graded_hurts": graded_hurts,
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
