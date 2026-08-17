"""exp_cue_binarised_readout_transfer_v1 -- DOES BINARISING THE CUE MOVE THE REAL READ-OUT?

THE QUESTION, DECOMPOSED SO THE ANSWER CANNOT BE A SINGLE NUMBER MISREAD ACROSS SCORERS.
data/exp_cue_compression_property_diagnosis_v1/metrics.json (commit 201776cc9) found that on
partial-cue ADDRESSING (n=3994 items / 5491 anchors), a BINARISED representation -- presence/
absence of each content word, counts discarded, no dense projection -- scores 0.1094 against the
live 256-dim projected encoder's 0.0711: margin +0.0383 CI [+0.0293,+0.0476], CI-separated ABOVE.
That is an ADDRESSING result: does the argmax land on the right ROW. It says NOTHING about whether
the row it lands on is the right ANSWER under the task's own scorer (hit@1 against WordNet gold).
Those are different scorers on different quantities and the project's own standing rule (a number
may not cross scorers or populations) forbids inferring one from the other. This cell measures
hit@1 directly, on the identical population, for the identical arms, and reports both numbers
side by side for every arm -- never one presented as if it were the other.

THE HONEST PRIOR, STATED BEFORE ANY HIT@1 NUMBER IS READ (per the dispatch brief).
notes/readout_ceiling_findings_2026-08-17.md's diagnosis is that our store encodes CO-OCCURRENCE
(SYNTAGMATIC neighbours -- words that occur WITH the query) while hit@1 scores SUBSTITUTABILITY
(PARADIGMATIC neighbours -- words that occur INSTEAD of the query): the correct answer's median
sentence-level co-occurrence with the query is exactly zero. Binarising the cue changes HOW MUCH of
each word's presence survives compression; it does not change WHICH RELATION is written to the
store in the first place. So the pre-registered expectation is: binarising helps ADDRESSING (it is
a compression-defect fix) and LEAVES HIT@1 WHERE IT WAS (the write-rule defect is untouched). If
that holds, it is a clean, useful result on its own: addressing and read-out are SEPARATELY CAPPED,
and fixing one does not fix the other. If R1 instead clears the hit@1 floor, that is the more
interesting outcome, and it earns extra scrutiny under the spelling-floor / rule-12 check below,
because a floor cleared by looking MORE like a spell-checker is a failure dressed as a win.

ARMS, one variable at a time, on the IDENTICAL store, cue, pool, gold and scorer (the harness
cache exp_task_degeneracy_v1.py already built: scratch/sparse_code_real_task/real_cache.npz, and
the raw content-word counts exp_cue_information_audit_v1.py already checkpointed:
data/exp_cue_information_audit_v1/units.jsonl, both REUSED READ-ONLY, never rebuilt):
  R0_INCUMBENT              cos(mat[a], Q_part[i]) -- the live 256-dim projected count encoder.
                            Bit-identical construction to C0_PROJECTED_256 in the diagnosis cell.
  R1_BINARISED              presence/absence, counts discarded, NO dense projection. Bit-identical
                            construction to B1_BINARIZED_RAW in the diagnosis cell.
  R2_BINARISED_PROJECTED    binarise THEN project to 256 dims through a fresh dense {-1,+1} random
                            projection (3 independent draws; BETWEEN_PROJECTION_DRAW_SD reported).
                            Tests whether the compression defect and the frequency-weighting defect
                            are INDEPENDENT (R2 close to R1: binarising still helps after
                            projection) or INTERACT (R2 close to R0: the projection erases the
                            binarisation gain regardless).
  U0_UNCOMPRESSED, S1, N1   NOT new arms -- reproduced ONLY inside the REGRESSION GATE below, at
                            the diagnosis cell's OWN seeds, to verify its three headline figures
                            off disk before anything new is trusted.
  K1_KNOWN_ANSWER           per-space self-query (query = the anchor's own stored row in that
                            space; CPD.score_space's K1_EXACT_KEY). Must sit >= 0.98 in EVERY
                            space or the instrument is dead and NO quality number is published.
                            (This is an ADDRESSING-side liveness check, not a hit@1 check -- it is
                            deliberately insensitive to the WordNet gold pairing, matching the
                            KA_SELF_ADDRESS convention in exp_readout_ceiling_diagnosis_v1.)
  N1_NULL                   real cue reassigned to a different item (same shared derangement across
                            every arm, for comparability). Must sit near chance on BOTH measures.

FLOORS (hit@1 side): max(F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE), every one
RECOMPUTED on this cell's own population, both tie conventions, CI half-width and the analytic null
width 1.96*sqrt(p(1-p)/n) reported beside every margin. 0.0480, 0.0870, 0.1382, 0.2070, 0.1390,
-0.1959 are NEVER imported. F_ORTHOGRAPHIC / F_FREQUENCY / F_CONSTANT_PROTOTYPE do not depend on
cue regime (they read the target LEMMA's own trigram profile / the anchor's own corpus frequency /
the anchor's own mean-direction cosine -- none of which touches Q_part or Q_exact) and are
therefore IDENTICAL whether scored against a partial or an exact cue; F_SCRAMBLE DOES depend on
cue regime and is recomputed here against the PARTIAL cue Q_part (matching R0/R1/R2's own regime),
NOT the EXACT-KEY Q_exact that exp_readout_ceiling_diagnosis_v1 used -- crossing that regime would
be exactly the population-crossing error the project's standing rule forbids. `tools/floor_battery`
supplies every floor and every scorer; it is imported, never reimplemented or edited.

STANDING RULE 12 (a floor is cleared by understanding, never adopted). If R1 clears the trigram
floor, that could mean the binarised representation moved TOWARD a spelling channel rather than
toward substitutability. Tested explicitly: the per-item hit@1 GAIN (R1 minus R0) is correlated
against the item's own orthographic similarity to its best gold anchor (F_ORTHOGRAPHIC's own score
for that anchor). Reported whichever way it falls, with a bootstrap CI on the correlation.

STOP-IF (pre-registered here, before any hit@1 number is read):
  (i)   R1 clears max(four floors) on hit@1, CI-separated -> report with every control and every
        floor named; state the level as well as the margin, do not overstate it.
  (ii)  R1 improves addressing (already true per the diagnosis cell, reproduced below) but hit@1 is
        NOT_SEPARATED from R0 -> ADDRESSING AND READ-OUT ARE SEPARATELY CAPPED; report in those
        words; this redirects effort to the write rule, not to further cue engineering.
  (iii) R1 beats the trigram floor AND the per-item gain CI-separates positively with orthographic
        similarity to the gold -> the win is SPELLING; report it as a FAILURE under rule 12, not a
        capability win, however (i) reads.
  (iv)  K1 fails in any space -> INSTRUMENT_STILL_LOOSE; publish no quality number for that space.

ORGAN REUSE, enumerated and verified by import, never edited: tools/floor_battery (scorer, floors,
bootstrap), tools/exp_checkpoint (per-unit checkpoint), experiments/exp_task_degeneracy_v1 (DEG;
harness cache + aux + ruler_mode_gate), experiments/exp_grounding_readout_known_answer_v1 (C3;
build_items, MAX_ITEMS, _n_profile), experiments/exp_cue_information_audit_v1 (AUD; raw-count
reconstruction, shim space, vocab/sparse machinery, corpus+bucket cache),
experiments/exp_cue_compression_property_diagnosis_v1 (CPD; score_space, binarize_sparse,
project_dense, project_sparse_hash, build_hash_projection, build_nonneg_projection,
load_or_build_counts -- its OWN checkpoint under data/exp_cue_information_audit_v1/units.jsonl is
reused READ-ONLY). NONE of these is edited. This cell does not import, edit, or otherwise touch any
experiments/exp_readout_* file or anything named paradigmatic -- a sibling agent owns that surface
concurrently; this cell's floor/population construction is written out independently here instead
(short, and avoids that file's module-level argv parsing coupling to this process's own argv).

BRAIN FIDELITY: none is claimed. This is an information/format audit of our own encoder plus a
task-scorer transfer check, exactly like the two cells it extends -- inventing an anatomy here
would be exactly the laundering the project's brain-fidelity gate exists to ban.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THIS PATH. ASCII-only. CPU. No network. The store is NEVER
rebuilt -- rebuilding it would break the identical-instrument invariant every arm depends on.
data/foundation/** is never opened. Writes only under
data/exp_cue_binarised_readout_transfer_v1[_smoke]/.
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import (numpy sizes its pools at import time).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools import floor_battery as FB                                       # noqa: E402
from tools.exp_checkpoint import load_units, record_unit, unit_key          # noqa: E402

import experiments.exp_task_degeneracy_v1 as DEG                            # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3              # noqa: E402
import experiments.exp_cue_information_audit_v1 as AUD                      # noqa: E402
import experiments.exp_cue_compression_property_diagnosis_v1 as CPD         # noqa: E402

# =================================================================================================
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: "tmp_replace" (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no quantitative noise floor of that form applies; capacity feasibility n/a here
# - baseline_in_band checked implicitly via K1/N1 validity gates (addressing self-check + null)
# - discriminator survives scale: the addressing gap is ALREADY MEASURED at full-N (the diagnosis
#   cell); this cell's OWN discriminator (hit@1 transfer) is read only at full grid, smoke is
#   labelled SMOKE and never substituted for it
# - HARD_PASS strictly above floor + 5% band-width is not this cell's vocabulary; it uses
#   CI-separated / NOT_SEPARATED / BELOW per floor_battery.margin, consistent with the sibling cells
# - cardinality_ok: this cell has a fixed arm set (R0,R1,R2x3draws,S1,N1,4 floors,ORACLE), no sweep
# - per-unit failure-class instrumentation: no bare except; SystemExit/KeyboardInterrupt re-raised
# - calibration_check: "default_ok_for_this_regime" (identical population to 3 landed sibling cells)
# - all numbers in this docstring are MEASURED@ the cited metrics.json paths (see PROVENANCE below)
# =================================================================================================

ANCHOR_NAME = "exp_cue_binarised_readout_transfer_v1"
AUD_FULL_OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_cue_information_audit_v1")

MASTER_SEED = 20260817400
N_BOOT = 10000
KA_CEILING_MIN = 0.98
D_PROJ = 256
N_PROJ_DRAWS = 3
N_SMOKE_ITEMS = 150
ANCHOR_POOL_SMOKE = 250

# PROVENANCE, verified off disk before this cell was authored (Read the file directly):
# data/exp_cue_compression_property_diagnosis_v1/metrics.json, commit 201776cc9.
REGRESSION_C0_ADDR = 0.0711
REGRESSION_U0_ADDR = 0.0849            # NOTE: the diagnosis cell's own gate compares to 0.0849
                                        # but measured 0.0846 on its full run and PASSED at tol
                                        # 5e-4 -- both are cited; PASS uses the diagnosis cell's
                                        # own tolerance against its own expected constant.
REGRESSION_B1_ADDR = 0.1094
REGRESSION_B1_VS_C0 = {"point": 0.0383, "ci95": [0.0293, 0.0476], "band": "ABOVE"}
REGRESSION_B1_VS_U0 = {"point": 0.0248, "ci95": [0.0160, 0.0338], "band": "ABOVE"}
REGRESSION_S1_DRAW0_ADDR = 0.0611      # S1_SPARSE_HASH_PROJ draws[0], seed CPD.MASTER_SEED+3000+0
REGRESSION_S1_VS_C0_BAND = "BELOW"
REGRESSION_N1_DRAW0_ADDR = 0.0709      # N1_NONNEG_PROJ draws[0], seed CPD.MASTER_SEED+4000+0
REGRESSION_N1_VS_C0_BAND = "NOT_SEPARATED"
REGRESSION_TOL = 5e-4
REGRESSION_MARGIN_TOL = 0.004          # bootstrap-draw tolerance on a re-drawn CI POINT estimate


def _out_dir(grid: str) -> str:
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + ("_smoke" if grid == "reduced" else ""))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def _dense(M) -> np.ndarray:
    return np.asarray(M.todense(), dtype=np.float32)


def _halfwidth(p: float, n: int) -> float:
    if n <= 0:
        return float("nan")
    p = min(max(p, 0.0), 1.0)
    return float(1.96 * ((p * (1.0 - p) / n) ** 0.5))


def build_dense_signed_projection(vocab_size: int, d: int, seed: int) -> np.ndarray:
    """R2's projection: a DENSE {-1,+1} random matrix -- every word touches every output dim (same
    denseness as the incumbent R0), signed (unlike N1_NONNEG_PROJ's {0,1} isolate, so contributions
    CAN cancel, matching the incumbent's own sign convention). This is deliberately the SAME family
    as CPD.build_nonneg_projection (dense, per-word iid draw, no structure) but signed -- it is NOT
    a reconstruction of the incumbent's literal projection matrix (which is not available as a
    standalone object; mat/Q_part are already fully projected in the harness cache), it is the
    standard-engineering proxy for 'apply a generic dense random projection to the binarised input',
    exactly the role CPD's N1_NONNEG_PROJ played for the raw-count input."""
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=(vocab_size, d)).astype(np.float32) * 2.0 - 1.0)


def derangement(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    perm = np.arange(n)
    tries = 0
    while np.any(perm == np.arange(n)) and tries < 200:
        perm = rng.permutation(n)
        tries += 1
    return perm


def pearson_ci_bootstrap(x: np.ndarray, y: np.ndarray, seed: int, n_boot: int = 5000) -> Dict:
    """Pearson r between x and y, paired bootstrap CI over items, plus the analytic band."""
    m = np.isfinite(x) & np.isfinite(y)
    xa, ya = np.asarray(x, dtype=np.float64)[m], np.asarray(y, dtype=np.float64)[m]
    n = xa.size
    if n < 8 or np.std(xa) < 1e-12 or np.std(ya) < 1e-12:
        return {"n": int(n), "r": None, "ci95": None, "band": "VOID_INSUFFICIENT_VARIANCE"}
    r0 = float(np.corrcoef(xa, ya)[0, 1])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    rs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        xb, yb = xa[idx[b]], ya[idx[b]]
        sdx, sdy = np.std(xb), np.std(yb)
        rs[b] = float(np.corrcoef(xb, yb)[0, 1]) if sdx > 1e-12 and sdy > 1e-12 else 0.0
    lo, hi = float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))
    band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")
    return {"n": int(n), "r": round(r0, 4), "ci95": [round(lo, 4), round(hi, 4)], "band": band}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    res: dict = {}
    rng = np.random.default_rng(9)

    # T0 -- the shared rulers self-test.
    res["floor_battery_selftest_keys"] = sorted(FB.self_test().keys())
    res["CPD_selftest_ran"] = sorted(CPD.self_test().keys())

    # T1 -- build_dense_signed_projection: values in {-1,+1}, genuinely dense, two seeds differ,
    # and (unlike the sparse hash projection) essentially every row touches every output dim.
    R = build_dense_signed_projection(40, 16, seed=1)
    assert set(np.unique(R).tolist()) <= {-1.0, 1.0}, "values outside {-1,+1}"
    assert np.all(R != 0), "dense signed projection has zero entries"
    R2b = build_dense_signed_projection(40, 16, seed=2)
    assert not np.array_equal(R, R2b), "two different seeds produced the identical matrix"
    res["T1_dense_signed_projection"] = True

    # T2 -- derangement: no fixed points, and it is a genuine permutation (bijection).
    d = derangement(37, seed=3)
    assert np.all(d != np.arange(37)), "derangement has a fixed point"
    assert sorted(d.tolist()) == list(range(37)), "derangement is not a permutation"
    res["T2_derangement"] = True

    # T3 -- pearson_ci_bootstrap: a KNOWN strong positive correlation must read ABOVE, a KNOWN null
    # (independent noise) must read NOT_SEPARATED, on the SAME n and seed family.
    xk = rng.standard_normal(400)
    yk = 0.8 * xk + 0.2 * rng.standard_normal(400)
    pk = pearson_ci_bootstrap(xk, yk, seed=11, n_boot=1000)
    assert pk["band"] == "ABOVE", "known positive correlation did not read ABOVE: %r" % pk
    xn = rng.standard_normal(400)
    yn = rng.standard_normal(400)
    pn = pearson_ci_bootstrap(xn, yn, seed=12, n_boot=1000)
    assert pn["band"] == "NOT_SEPARATED", "known-null pair did not read NOT_SEPARATED: %r" % pn
    res["T3_pearson_ci_bootstrap"] = {"known_positive": pk, "known_null": pn}

    # T4 -- _halfwidth: matches the closed-form binomial normal-approx half-width at a known point.
    hw = _halfwidth(0.05, 3994)
    expected = 1.96 * ((0.05 * 0.95 / 3994) ** 0.5)
    assert abs(hw - expected) < 1e-9, "halfwidth formula drifted"
    res["T4_halfwidth"] = round(hw, 6)

    # T5 -- end-to-end hit@1 wiring on a tiny synthetic pool: a QUERY-DEPENDENT arm must win, a
    # CONSTANT arm must NOT (this population is built so no constant can), and the null (permuted
    # cue) must fall to a low rate -- the same three-way check every sibling cell runs.
    n_a, n_i = 60, 200
    MAT = FB.l2n(rng.standard_normal((n_a, 8)).astype(np.float32))
    gold_idx = rng.integers(0, n_a, size=n_i)
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    GOLD[gold_idx, np.arange(n_i)] = True
    E = np.ones((n_a, n_i), dtype=bool)
    Q = MAT[gold_idx]                                      # exact-key cue: must win near-ceiling
    S_know = MAT @ Q.T
    h_know = FB.hit_at_1_both_tie_conventions(S_know, E, GOLD)["hit_exp"]
    assert h_know.mean() > 0.98, "known-answer synthetic pool did not read near ceiling"
    const_vec = FB.constant_prototype_floor(MAT)
    S_const = FB.as_constant_matrix(const_vec, n_i)
    h_const = FB.hit_at_1_both_tie_conventions(S_const, E, GOLD)["hit_exp"]
    S_null = MAT @ Q[derangement(n_i, seed=4)].T
    h_null = FB.hit_at_1_both_tie_conventions(S_null, E, GOLD)["hit_exp"]
    assert h_know.mean() > h_const.mean() + 0.3, "known arm did not beat the constant floor by a wide margin on this pool"
    assert h_know.mean() > h_null.mean() + 0.3, "known arm did not beat the permuted null by a wide margin"
    res["T5_hit1_end_to_end"] = {"known": round(float(h_know.mean()), 4),
                                 "constant": round(float(h_const.mean()), 4),
                                 "null": round(float(h_null.mean()), 4)}

    # T6 -- REAL CODE PATH: exercise the actual substrate entrypoints this cell depends on, at
    # trivial scale, not a synthetic-only branch (SCHEMA-VET F.1).
    g6 = DEG.ruler_mode_gate()
    assert g6.get("PASS") is True, g6
    assert "--smoke" not in sys.argv, sys.argv
    cnt = AUD.raw_counts_for_window("the quick brown fox jumps over the lazy dog", "fox")
    assert isinstance(cnt, Counter) and len(cnt) > 0, "raw_counts_for_window did not return real counts"
    res["T6_real_code_path"] = {"ruler_mode_gate": g6, "raw_counts_sample_len": len(cnt)}

    # T7 -- regression PROVENANCE constants are internally consistent (bands match signs).
    assert REGRESSION_B1_VS_C0["ci95"][0] > 0 and REGRESSION_B1_VS_C0["band"] == "ABOVE"
    assert REGRESSION_S1_VS_C0_BAND == "BELOW" and REGRESSION_N1_VS_C0_BAND == "NOT_SEPARATED"
    res["T7_provenance_constants_self_consistent"] = True

    print("[selftest] PASS " + json.dumps(res, default=str)[:1800], flush=True)
    return res


# =================================================================================================
# population (independent of exp_readout_ceiling_diagnosis_v1 -- see module docstring for why)
# =================================================================================================
def build_population() -> Dict:
    C = DEG.load_cache()
    aux = DEG.load_aux(C)
    anchors, mat, mat_ok = C["anchors"], C["mat"], C["mat_ok"]
    n_anchors, n_items_all = len(anchors), len(C["L_words"])
    qidx = np.array([C["pos"].get(w, -1) for w in C["L_words"]], dtype=np.int64)
    GOLD_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    E_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    for i in range(n_items_all):
        if not C["keep"][i]:
            continue
        E_ALL[:, i] = mat_ok
        if len(C["excl"][i]):
            E_ALL[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD_ALL[gi, i] = True
    GOLD_ALL &= E_ALL
    keep_ALL = C["keep"] & GOLD_ALL.any(axis=0)
    return {"C": C, "aux": aux, "anchors": anchors, "mat": mat, "mat_ok": mat_ok,
            "n_anchors": n_anchors, "qidx": qidx, "GOLD": GOLD_ALL, "E": E_ALL, "keep": keep_ALL}


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir = _out_dir(grid)
    os.makedirs(out_dir, exist_ok=True)
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "out_dir": out_dir,
                "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                "RULER_MODE_GATE": DEG.ruler_mode_gate(), "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "progress_logging": True}

    # ---- population -------------------------------------------------------------------------
    cache_prov = DEG.build_cache_if_missing()
    P0 = build_population()
    C, aux = P0["C"], P0["aux"]
    anchors, mat, mat_ok = P0["anchors"], P0["mat"], P0["mat_ok"]
    n_anchors, qidx = P0["n_anchors"], P0["qidx"]
    GOLD_ALL, E_ALL, keep_ALL = P0["GOLD"], P0["E"], P0["keep"]
    rep["cache_provenance"] = cache_prov
    print("[load] n_anchors=%d n_items_all=%d %.0fs" % (n_anchors, len(C["L_words"]), time.time() - t0),
         flush=True)

    # ---- items (needed ONLY to key the raw-count checkpoint reuse) ---------------------------
    sents, buckets, counts, corpus_prov = AUD.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    shim = AUD._ShimSpace(anchors, C["pos"], mat)
    items, item_diag = C3.build_items(shim, buckets, counts, C3.MAX_ITEMS)
    recov = AUD.verify_recoverability(items, C, sents)
    rep["RECOVERABILITY_GATE"] = recov
    print("[recoverability] checked=%d ALL_EXACT=%s %.0fs" % (
        recov["n_checked_full_pop"], recov["ALL_EXACT"], time.time() - t0), flush=True)
    if not recov["ALL_EXACT"]:
        rep["STOP_IF_FIRED"] = "RECOVERABILITY_DID_NOT_REPRODUCE -- no arm can be trusted; stopping."
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
        return rep

    L_of = {it["item_id"]: it["L"] for it in items}
    sentidx_of = {it["item_id"]: it["sent_idx"] for it in items}
    item_id_of_idx = [it["item_id"] for it in items]

    eligible_item_idx = np.flatnonzero(keep_ALL)
    if grid == "full":
        item_idx = eligible_item_idx
        anchor_ids = list(anchors)
        reuse_dir = AUD_FULL_OUT_DIR
    else:
        item_idx = eligible_item_idx[:N_SMOKE_ITEMS]
        own = sorted({L_of[item_id_of_idx[i]] for i in item_idx})
        rngp = np.random.default_rng(MASTER_SEED + 1)
        pad_pool = [a for a in anchors if a not in set(own)]
        pad = rngp.choice(pad_pool, size=max(0, ANCHOR_POOL_SMOKE - len(own)), replace=False).tolist()
        anchor_ids = sorted(set(own) | set(pad))
        reuse_dir = None
    T = item_idx
    n_items_w = int(T.size)
    n_anchors_w = len(anchor_ids)
    rep["POOL"] = {"grid": grid, "n_items_working": n_items_w, "n_anchors_working": n_anchors_w,
                   "n_items_eligible_full_pop": int(eligible_item_idx.size), "n_anchors_full_pop": n_anchors,
                   "reuse_dir": reuse_dir,
                   "pool_description": "the LANDED OPEN pool (mat_ok minus per-item exclusions), "
                                       "identical construction to exp_cue_information_audit_v1 / "
                                       "exp_cue_compression_property_diagnosis_v1 / "
                                       "exp_readout_ceiling_diagnosis_v1 (same CACHE file)."}
    print("[pool] grid=%s n_items=%d n_anchors=%d reuse_dir=%s" % (
        grid, n_items_w, n_anchors_w, reuse_dir), flush=True)

    anchor_pos_global = C["pos"]
    anchor_global_idx = np.array([anchor_pos_global[a] for a in anchor_ids], dtype=np.int64)
    mat_w = mat[anchor_global_idx]
    mat_ok_w = mat_ok[anchor_global_idx]
    local_pos = {a: i for i, a in enumerate(anchor_ids)}
    item_ids_w = [item_id_of_idx[i] for i in item_idx]
    L_w = [L_of[iid] for iid in item_ids_w]
    qidx_w = np.array([local_pos[L] for L in L_w], dtype=np.int64)
    Qpart_w = C["Q_part"][item_idx]
    GOLD_T = GOLD_ALL[anchor_global_idx][:, T]
    E_T = E_ALL[anchor_global_idx][:, T]
    chance_addr = 1.0 / max(int(mat_ok_w.sum()), 1)
    perm = derangement(n_items_w, seed=MASTER_SEED + 501)

    # ---- raw counts, reused READ-ONLY from the audit cell's full-grid checkpoint --------------
    P, p_diag = CPD.load_or_build_counts(
        anchor_ids, "Pstore", buckets, sents,
        lambda a: sum((AUD.raw_counts_for_window(sents[i], a)
                      for i in buckets.get(a, [])[:C3._n_profile(len(buckets.get(a, [])))]), Counter()),
        out_dir, reuse_dir)
    rep["STORE_COUNTS_SOURCE"] = p_diag
    Qctx, q_diag = CPD.load_or_build_counts(
        item_ids_w, "Qcue_context", buckets, sents,
        lambda iid: AUD.raw_counts_for_window(sents[sentidx_of[iid]], L_of[iid]),
        out_dir, reuse_dir)
    rep["CONTEXT_CUE_SOURCE"] = q_diag
    print("[counts] store built=%d reused_local=%d reused_ext=%d; cue built=%d reused_local=%d reused_ext=%d %.0fs" % (
        p_diag["n_built"], p_diag["n_reused_local"], p_diag["n_reused_external"],
        q_diag["n_built"], q_diag["n_reused_local"], q_diag["n_reused_external"], time.time() - t0), flush=True)

    vocab = AUD.build_vocab([P, Qctx])
    rep["VOCAB"] = {"n_distinct_content_words": len(vocab)}
    P_raw = AUD.to_sparse(P, anchor_ids, vocab)
    Q_raw = AUD.to_sparse(Qctx, item_ids_w, vocab)

    # =============================================================================================
    # ADDRESSING SIDE -- R0 / U0(regression-only) / R1 / R2(x3 draws) / S1,N1(regression-only)
    # =============================================================================================
    addr_spaces: Dict[str, Dict] = {}
    addr_hits: Dict[str, np.ndarray] = {}

    R0_store_n = FB.l2n(mat_w)
    R0_cue_n = FB.l2n(Qpart_w)
    out_r0, hits_r0, _ = CPD.score_space("R0_INCUMBENT", R0_store_n, R0_cue_n, mat_ok_w, qidx_w,
                                         perm, chance_addr)
    addr_spaces["R0_INCUMBENT"] = out_r0
    addr_hits["R0_INCUMBENT"] = hits_r0

    Pm = AUD.l2n_sparse(P_raw)
    Qm = AUD.l2n_sparse(Q_raw)
    U0_store_n, U0_cue_n = _dense(Pm), _dense(Qm)
    out_u0, hits_u0, _ = CPD.score_space("U0_UNCOMPRESSED_regression_only", U0_store_n, U0_cue_n,
                                         mat_ok_w, qidx_w, perm, chance_addr)
    addr_spaces["U0_UNCOMPRESSED_regression_only"] = out_u0
    addr_hits["U0_UNCOMPRESSED_regression_only"] = hits_u0
    del U0_store_n, U0_cue_n, Pm, Qm

    Pb = AUD.l2n_sparse(CPD.binarize_sparse(P_raw))
    Qb = AUD.l2n_sparse(CPD.binarize_sparse(Q_raw))
    R1_store_n, R1_cue_n = _dense(Pb), _dense(Qb)
    out_r1, hits_r1, _ = CPD.score_space("R1_BINARISED", R1_store_n, R1_cue_n, mat_ok_w, qidx_w,
                                         perm, chance_addr)
    addr_spaces["R1_BINARISED"] = out_r1
    addr_hits["R1_BINARISED"] = hits_r1
    del Pb, Qb

    Pbin = CPD.binarize_sparse(P_raw)
    Qbin = CPD.binarize_sparse(Q_raw)
    r2_draws = []
    R2_store_n0 = R2_cue_n0 = None
    for d in range(N_PROJ_DRAWS):
        Rproj = build_dense_signed_projection(len(vocab), D_PROJ, MASTER_SEED + 6000 + d)
        Ps = FB.l2n(CPD.project_dense(Pbin, Rproj))
        Qs = FB.l2n(CPD.project_dense(Qbin, Rproj))
        out_d, hits_d, _ = CPD.score_space("R2_BINARISED_PROJECTED_draw%d" % d, Ps, Qs, mat_ok_w,
                                           qidx_w, perm, chance_addr)
        r2_draws.append(out_d)
        if d == 0:
            R2_store_n0, R2_cue_n0 = Ps, Qs
            addr_hits["R2_BINARISED_PROJECTED"] = hits_d
    r2_main_vals = [x["accuracy"]["MAIN"] for x in r2_draws]
    rep["R2_BINARISED_PROJECTED"] = {"draws": r2_draws,
                                     "BETWEEN_PROJECTION_DRAW_SD": {
                                         "n_draws": N_PROJ_DRAWS, "mean": round(float(np.mean(r2_main_vals)), 4),
                                         "sd": round(float(np.std(r2_main_vals)), 4), "values": r2_main_vals}}
    addr_spaces["R2_BINARISED_PROJECTED"] = r2_draws[0]
    del Pbin, Qbin

    # ---- REGRESSION-ONLY S1/N1 reproduction, BIT-IDENTICAL seeds to the diagnosis cell ---------
    Rh = CPD.build_hash_projection(len(vocab), D_PROJ, seed=CPD.MASTER_SEED + 3000 + 0)
    Ps1 = FB.l2n(CPD.project_sparse_hash(P_raw, Rh))
    Qs1 = FB.l2n(CPD.project_sparse_hash(Q_raw, Rh))
    out_s1r, hits_s1r, _ = CPD.score_space("S1_REGRESSION_CHECK", Ps1, Qs1, mat_ok_w, qidx_w, perm,
                                           chance_addr)
    addr_hits["S1_REGRESSION_CHECK"] = hits_s1r
    del Ps1, Qs1

    Rn = CPD.build_nonneg_projection(len(vocab), D_PROJ, seed=CPD.MASTER_SEED + 4000 + 0)
    Pn1 = FB.l2n(CPD.project_dense(P_raw, Rn))
    Qn1 = FB.l2n(CPD.project_dense(Q_raw, Rn))
    out_n1r, hits_n1r, _ = CPD.score_space("N1_REGRESSION_CHECK", Pn1, Qn1, mat_ok_w, qidx_w, perm,
                                           chance_addr)
    addr_hits["N1_REGRESSION_CHECK"] = hits_n1r
    del Pn1, Qn1, P_raw, Q_raw

    # ---- PRE-REGISTERED REGRESSION GATE (addressing side): reproduce the diagnosis cell's THREE
    # headline figures fresh, off disk, before anything downstream is trusted. -------------------
    mask_all = np.ones(n_items_w, dtype=bool)
    boot_reg = FB.paired_bootstrap_ci(
        {"C0": hits_r0, "U0": hits_u0, "B1": hits_r1, "S1": hits_s1r, "N1": hits_n1r},
        mask_all, N_BOOT, MASTER_SEED + 909)
    b1_vs_c0 = FB.margin(boot_reg["boot"], "B1", "C0")
    b1_vs_u0 = FB.margin(boot_reg["boot"], "B1", "U0")
    s1_vs_c0 = FB.margin(boot_reg["boot"], "S1", "C0")
    n1_vs_c0 = FB.margin(boot_reg["boot"], "N1", "C0")

    def _close(a: float, b: float, tol: float) -> bool:
        return abs(a - b) <= tol

    reg_checks = {
        "C0_addr": {"measured": out_r0["accuracy"]["MAIN"], "expected": REGRESSION_C0_ADDR,
                    "PASS": _close(out_r0["accuracy"]["MAIN"], REGRESSION_C0_ADDR, REGRESSION_TOL)},
        "U0_addr": {"measured": out_u0["accuracy"]["MAIN"], "expected": REGRESSION_U0_ADDR,
                    "PASS": _close(out_u0["accuracy"]["MAIN"], REGRESSION_U0_ADDR, REGRESSION_TOL)},
        "B1_addr": {"measured": out_r1["accuracy"]["MAIN"], "expected": REGRESSION_B1_ADDR,
                    "PASS": _close(out_r1["accuracy"]["MAIN"], REGRESSION_B1_ADDR, REGRESSION_TOL)},
        "S1_draw0_addr": {"measured": out_s1r["accuracy"]["MAIN"], "expected": REGRESSION_S1_DRAW0_ADDR,
                          "PASS": _close(out_s1r["accuracy"]["MAIN"], REGRESSION_S1_DRAW0_ADDR, REGRESSION_TOL)},
        "N1_draw0_addr": {"measured": out_n1r["accuracy"]["MAIN"], "expected": REGRESSION_N1_DRAW0_ADDR,
                          "PASS": _close(out_n1r["accuracy"]["MAIN"], REGRESSION_N1_DRAW0_ADDR, REGRESSION_TOL)},
        "B1_vs_C0_margin": {"measured": b1_vs_c0, "expected": REGRESSION_B1_VS_C0,
                            "PASS": bool(_close(b1_vs_c0["point"], REGRESSION_B1_VS_C0["point"], REGRESSION_MARGIN_TOL)
                                        and b1_vs_c0["band"] == REGRESSION_B1_VS_C0["band"])},
        "B1_vs_U0_margin": {"measured": b1_vs_u0, "expected": REGRESSION_B1_VS_U0,
                            "PASS": bool(_close(b1_vs_u0["point"], REGRESSION_B1_VS_U0["point"], REGRESSION_MARGIN_TOL)
                                        and b1_vs_u0["band"] == REGRESSION_B1_VS_U0["band"])},
        "S1_vs_C0_band": {"measured": s1_vs_c0, "expected_band": REGRESSION_S1_VS_C0_BAND,
                          "PASS": bool(s1_vs_c0["band"] == REGRESSION_S1_VS_C0_BAND)},
        "N1_vs_C0_band": {"measured": n1_vs_c0, "expected_band": REGRESSION_N1_VS_C0_BAND,
                          "PASS": bool(n1_vs_c0["band"] == REGRESSION_N1_VS_C0_BAND)},
    }
    reg_checks["ALL_PASS"] = bool(all(v["PASS"] for k, v in reg_checks.items() if k != "ALL_PASS"))
    reg_checks["enforced"] = (grid == "full")
    reg_checks["note_if_not_enforced"] = ("ONLY MEANINGFUL at --grid full: the landed diagnosis-cell "
        "figures were measured on the full 3994-item/5491-anchor pool; a --grid reduced population is "
        "a different, much smaller pool by construction and is NOT expected to reproduce them.")
    rep["REGRESSION_GATE_DIAGNOSIS_CELL_REPRODUCTION"] = reg_checks
    print("[regression] enforced=%s ALL_PASS=%s :: %s" % (reg_checks["enforced"], reg_checks["ALL_PASS"],
          json.dumps({k: v.get("PASS") for k, v in reg_checks.items() if k not in ("ALL_PASS", "enforced", "note_if_not_enforced")})), flush=True)
    if grid == "full" and not reg_checks["ALL_PASS"]:
        rep["STOP_IF_FIRED"] = ("REGRESSION_FAILED_TO_REPRODUCE_DIAGNOSIS_CELL -- a failed "
                                "reproduction of a load-bearing number outranks everything else "
                                "in this brief. STOPPING before any hit@1 number is read. %r"
                                % reg_checks)
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
        print("STOP: " + rep["STOP_IF_FIRED"], flush=True)
        return rep

    # ---- K1_KNOWN_ANSWER validity gate, EVERY space, must pass or publish nothing ---------------
    k1_by_space = {"R0_INCUMBENT": out_r0["accuracy"]["K1_EXACT_KEY"],
                   "R1_BINARISED": out_r1["accuracy"]["K1_EXACT_KEY"],
                   "R2_BINARISED_PROJECTED_draw0": r2_draws[0]["accuracy"]["K1_EXACT_KEY"]}
    k1_pass = {k: bool(v >= KA_CEILING_MIN) for k, v in k1_by_space.items()}
    rep["K1_KNOWN_ANSWER"] = {"values": k1_by_space, "gate": KA_CEILING_MIN, "PASS_by_space": k1_pass,
                              "ALL_PASS": bool(all(k1_pass.values()))}
    print("[K1] %r" % rep["K1_KNOWN_ANSWER"], flush=True)
    if not rep["K1_KNOWN_ANSWER"]["ALL_PASS"]:
        rep["STOP_IF_FIRED"] = ("iv_INSTRUMENT_STILL_LOOSE -- K1_KNOWN_ANSWER failed in at least one "
                                "space (%r). No quality number is published." % k1_by_space)
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
        print("STOP: " + rep["STOP_IF_FIRED"], flush=True)
        return rep

    # ---- N1_NULL, addressing side, already computed; report + soft-check ------------------------
    n1_addr = {"R0": out_r0["accuracy"]["N1_RANDOM_KEY"], "R1": out_r1["accuracy"]["N1_RANDOM_KEY"],
              "R2_draw0": r2_draws[0]["accuracy"]["N1_RANDOM_KEY"], "chance": round(chance_addr, 8),
              "S1_regr": out_s1r["accuracy"]["N1_RANDOM_KEY"], "N1_regr": out_n1r["accuracy"]["N1_RANDOM_KEY"]}
    rep["N1_NULL_ADDRESSING"] = n1_addr

    rep["ADDRESSING_ARM_DIGESTS_ARMS_MUST_DIFFER"] = {k: _digest(v) for k, v in addr_hits.items()}
    assert len(set(rep["ADDRESSING_ARM_DIGESTS_ARMS_MUST_DIFFER"].values())) > 1, (
        "ALL addressing MAIN hit vectors are IDENTICAL -- a construction bug")

    boot_addr = FB.paired_bootstrap_ci(addr_hits, mask_all, N_BOOT, MASTER_SEED + 1010)
    addr_margins = {
        "R1_vs_R0": FB.margin(boot_addr["boot"], "R1_BINARISED", "R0_INCUMBENT"),
        "R2_vs_R0": FB.margin(boot_addr["boot"], "R2_BINARISED_PROJECTED", "R0_INCUMBENT"),
        "R2_vs_R1": FB.margin(boot_addr["boot"], "R2_BINARISED_PROJECTED", "R1_BINARISED")}
    rep["ADDRESSING_ACCURACY"] = {"spaces": addr_spaces, "margins": addr_margins}
    print("[addressing] R0=%.4f R1=%.4f R2draw0=%.4f margins=%r" % (
        out_r0["accuracy"]["MAIN"], out_r1["accuracy"]["MAIN"], r2_draws[0]["accuracy"]["MAIN"],
        addr_margins), flush=True)

    # =============================================================================================
    # HIT@1 SIDE -- THE REAL QUESTION. Same store_n/cue_n objects already built above, reused.
    # =============================================================================================
    def hit1_arm(store_n: np.ndarray, cue_n: np.ndarray) -> Tuple[Dict, Dict, np.ndarray]:
        S = (store_n @ cue_n.T).astype(np.float32)
        h = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)
        Sp = (store_n @ cue_n[perm].T).astype(np.float32)
        hp = FB.hit_at_1_both_tie_conventions(Sp, E_T, GOLD_T)
        return h, hp, S

    h_r0, hp_r0, S_r0 = hit1_arm(R0_store_n, R0_cue_n)
    h_r1, hp_r1, S_r1 = hit1_arm(R1_store_n, R1_cue_n)
    h_r2, hp_r2, S_r2 = hit1_arm(R2_store_n0, R2_cue_n0)
    del R1_store_n, R1_cue_n, S_r0, S_r2

    n_gold = (GOLD_T & E_T).sum(axis=0).astype(np.float64)
    n_elig = E_T.sum(axis=0).astype(np.float64)
    rep["HIT1_POPULATION"] = {
        "n_items": n_items_w, "n_anchors": n_anchors_w,
        "n_gold_per_item_mean": round(float(n_gold.mean()), 3),
        "n_elig_per_item_mean": round(float(n_elig.mean()), 1),
        "analytic_chance_hit1_mean_gold_over_elig": round(float((n_gold / np.maximum(n_elig, 1)).mean()), 6),
        "scorer": "tools/floor_battery.hit_at_1_both_tie_conventions, hit_exp (tie-corrected) primary",
        "gold": "WordNet generous meaning set as built by exp_grounding_readout_known_answer_v1, "
                "identical construction to every sibling cell on this cache",
        "cue_regime": "PARTIAL (context-sentence), matching R0/R1/R2's own regime"}

    # ---- floors, hit@1 side, ALL recomputed fresh on THIS population, PARTIAL-cue regime --------
    floors_S: Dict[str, np.ndarray] = {}
    floors_S["F_ORTHOGRAPHIC"] = (FB.l2n(aux["t_mat"][anchor_global_idx])
                                  @ FB.l2n(aux["Tq"][T]).T).astype(np.float32)
    floors_S["F_FREQUENCY"] = FB.as_constant_matrix(
        FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)[anchor_global_idx]), n_items_w)
    floors_S["F_SCRAMBLE"] = (FB.l2n(FB.scramble_null(mat_w, MASTER_SEED + 91))
                              @ FB.l2n(Qpart_w).T).astype(np.float32)
    const_vec = FB.constant_prototype_floor(mat_w, mat_ok_w)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(const_vec, n_items_w)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors_w, [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items_w)]),
        n_items_w)
    rep["FLOOR_NOTE"] = ("F_ORTHOGRAPHIC / F_FREQUENCY / F_CONSTANT_PROTOTYPE do not depend on cue "
                         "regime; F_SCRAMBLE is scored against the PARTIAL cue Q_part here (matching "
                         "R0/R1/R2), NOT the EXACT-KEY cue exp_readout_ceiling_diagnosis_v1 used -- "
                         "crossing that regime would be a population-crossing error.")

    hit_exp: Dict[str, np.ndarray] = {"R0_INCUMBENT": h_r0["hit_exp"], "R1_BINARISED": h_r1["hit_exp"],
                                      "R2_BINARISED_PROJECTED": h_r2["hit_exp"]}
    hit_opt: Dict[str, np.ndarray] = {"R0_INCUMBENT": h_r0["hit_opt"], "R1_BINARISED": h_r1["hit_opt"],
                                      "R2_BINARISED_PROJECTED": h_r2["hit_opt"]}
    hit_cons: Dict[str, np.ndarray] = {"R0_INCUMBENT": h_r0["hit_cons"], "R1_BINARISED": h_r1["hit_cons"],
                                       "R2_BINARISED_PROJECTED": h_r2["hit_cons"]}
    for fname, Sf in floors_S.items():
        hh = FB.hit_at_1_both_tie_conventions(Sf, E_T, GOLD_T)
        hit_exp[fname] = hh["hit_exp"]; hit_opt[fname] = hh["hit_opt"]; hit_cons[fname] = hh["hit_cons"]
    hh_orc = FB.hit_at_1_both_tie_conventions(oracle_S, E_T, GOLD_T)
    hit_exp["ORACLE_CONSTANT_not_a_floor"] = hh_orc["hit_exp"]
    hit_opt["ORACLE_CONSTANT_not_a_floor"] = hh_orc["hit_opt"]
    hit_cons["ORACLE_CONSTANT_not_a_floor"] = hh_orc["hit_cons"]

    n = n_items_w
    hit1_summary = {}
    for name, v_exp in hit_exp.items():
        v_opt, v_cons = hit_opt[name], hit_cons[name]
        p_exp = float(v_exp.mean())
        hit1_summary[name] = {
            "hit_exp_tie_corrected": round(p_exp, 4), "halfwidth_analytic_null_at_this_n": round(_halfwidth(p_exp, n), 4),
            "hit_opt": round(float(v_opt.mean()), 4), "hit_cons": round(float(v_cons.mean()), 4)}
    rep["HIT1_ARM_SUMMARY"] = hit1_summary
    print("[hit1] " + json.dumps(hit1_summary, default=str)[:2200], flush=True)

    rep["HIT1_ARM_DIGESTS_ARMS_MUST_DIFFER"] = {k: _digest(v) for k, v in hit_exp.items()}
    assert len(set(rep["HIT1_ARM_DIGESTS_ARMS_MUST_DIFFER"].values())) > 1, (
        "ALL hit@1 hit_exp vectors are IDENTICAL -- a construction bug")

    boot_hit1 = FB.paired_bootstrap_ci(hit_exp, mask_all, N_BOOT, MASTER_SEED + 2020)
    floor_names = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")
    winning_floor = max(floor_names, key=lambda f: hit1_summary[f]["hit_exp_tie_corrected"])
    hit1_margins = {
        "R1_vs_R0": FB.margin(boot_hit1["boot"], "R1_BINARISED", "R0_INCUMBENT"),
        "R2_vs_R0": FB.margin(boot_hit1["boot"], "R2_BINARISED_PROJECTED", "R0_INCUMBENT"),
        "R2_vs_R1": FB.margin(boot_hit1["boot"], "R2_BINARISED_PROJECTED", "R1_BINARISED"),
        "R1_vs_max_floor(%s)" % winning_floor: FB.margin(boot_hit1["boot"], "R1_BINARISED", winning_floor),
        "R0_vs_max_floor(%s)" % winning_floor: FB.margin(boot_hit1["boot"], "R0_INCUMBENT", winning_floor),
        "R2_vs_max_floor(%s)" % winning_floor: FB.margin(boot_hit1["boot"], "R2_BINARISED_PROJECTED", winning_floor),
        "R1_vs_F_ORTHOGRAPHIC": FB.margin(boot_hit1["boot"], "R1_BINARISED", "F_ORTHOGRAPHIC"),
    }
    for fn in floor_names:
        hit1_margins["%s_vs_null_p95_note" % fn] = (
            "half-width reported per-arm above (halfwidth_analytic_null_at_this_n); this margin "
            "uses the PAIRED bootstrap, which is stricter than the marginal analytic width")
    rep["HIT1_MARGINS"] = hit1_margins
    print("[hit1 margins] " + json.dumps({k: v for k, v in hit1_margins.items() if isinstance(v, dict)},
                                          default=str)[:2500], flush=True)

    # ---- N1_NULL, hit@1 side (permuted cue) -------------------------------------------------------
    n1_hit1 = {"R0_null_hit_exp": round(float(hp_r0["hit_exp"].mean()), 6),
              "R1_null_hit_exp": round(float(hp_r1["hit_exp"].mean()), 6),
              "R2_null_hit_exp": round(float(hp_r2["hit_exp"].mean()), 6),
              "analytic_chance_reference": rep["HIT1_POPULATION"]["analytic_chance_hit1_mean_gold_over_elig"]}
    n1_hit1["near_chance"] = {k: bool(abs(v - n1_hit1["analytic_chance_reference"]) < 0.02)
                              for k, v in n1_hit1.items() if k.endswith("_hit_exp")}
    rep["N1_NULL_HIT1"] = n1_hit1
    print("[N1 hit1] %r" % n1_hit1, flush=True)

    # =============================================================================================
    # STANDING RULE 12 -- orthographic-correlation check on the per-item R1 vs R0 GAIN
    # =============================================================================================
    gain_r1_minus_r0 = h_r1["hit_exp"] - h_r0["hit_exp"]
    orth_to_gold = np.full(n_items_w, np.nan, dtype=np.float64)
    F_ORTH = floors_S["F_ORTHOGRAPHIC"]
    for i in range(n_items_w):
        gcols = np.flatnonzero(GOLD_T[:, i])
        if gcols.size:
            orth_to_gold[i] = float(np.max(F_ORTH[gcols, i]))
    corr_all = pearson_ci_bootstrap(gain_r1_minus_r0, orth_to_gold, seed=MASTER_SEED + 3030)
    nz = gain_r1_minus_r0 != 0.0
    corr_nz = pearson_ci_bootstrap(gain_r1_minus_r0[nz], orth_to_gold[nz], seed=MASTER_SEED + 3031)
    rep["RULE12_ORTHOGRAPHIC_CORRELATION_CHECK"] = {
        "what": "pearson r between per-item (R1_hit_exp - R0_hit_exp) and that item's own best-gold "
                "F_ORTHOGRAPHIC score. ABOVE (CI-separated positive) means R1's gains concentrate on "
                "items where the answer LOOKS LIKE the query -- a spelling-shaped win, not a "
                "substitutability win, per standing rule 12.",
        "all_items": corr_all, "gain_nonzero_items_only": corr_nz,
        "n_gain_nonzero": int(nz.sum())}
    print("[rule12] %r" % rep["RULE12_ORTHOGRAPHIC_CORRELATION_CHECK"], flush=True)

    # =============================================================================================
    # STOP-IF DECISION, exactly the four pre-registered branches
    # =============================================================================================
    r1_clears_floor = hit1_margins["R1_vs_max_floor(%s)" % winning_floor]["band"] == "ABOVE"
    r1_addr_above_r0 = addr_margins["R1_vs_R0"]["band"] == "ABOVE"
    r1_hit1_not_separated_from_r0 = hit1_margins["R1_vs_R0"]["band"] == "NOT_SEPARATED"
    r1_beats_trigram = hit1_margins["R1_vs_F_ORTHOGRAPHIC"]["band"] == "ABOVE"
    spelling_correlated = corr_all["band"] == "ABOVE"

    fired = []
    if r1_clears_floor:
        fired.append("i_R1_CLEARS_MAX_FLOOR")
    if r1_addr_above_r0 and r1_hit1_not_separated_from_r0:
        fired.append("ii_ADDRESSING_AND_READOUT_ARE_SEPARATELY_CAPPED")
    if r1_beats_trigram and spelling_correlated:
        fired.append("iii_WIN_IS_SPELLING_RULE12_FAILURE")
    # (iv) already handled above as an early-STOP branch; if we reach here it did not fire.

    if not fired:
        verdict = "NONE_OF_FOUR_addressing_improved_hit1_did_not_CI_separate_either_way"
    elif "iii_WIN_IS_SPELLING_RULE12_FAILURE" in fired:
        verdict = "iii_WIN_IS_SPELLING_RULE12_FAILURE"          # overrides (i) if both fire
    elif "ii_ADDRESSING_AND_READOUT_ARE_SEPARATELY_CAPPED" in fired:
        verdict = "ii_ADDRESSING_AND_READOUT_ARE_SEPARATELY_CAPPED"
    else:
        verdict = fired[0]

    rep["STOP_IF_VERDICT"] = {
        "fired": fired, "primary_verdict": verdict,
        "r1_clears_max_floor": r1_clears_floor, "winning_floor": winning_floor,
        "r1_addressing_above_r0": r1_addr_above_r0,
        "r1_hit1_not_separated_from_r0": r1_hit1_not_separated_from_r0,
        "r1_beats_trigram_floor": r1_beats_trigram,
        "gain_correlates_with_orthographic_similarity_to_gold": spelling_correlated,
        "does_fixing_addressing_fix_readout": (
            "NO -- addressing and read-out are separately capped"
            if "ii_ADDRESSING_AND_READOUT_ARE_SEPARATELY_CAPPED" in fired else
            "THE WIN IS SPELLING, NOT SUBSTITUTABILITY -- report as a rule-12 failure"
            if verdict == "iii_WIN_IS_SPELLING_RULE12_FAILURE" else
            "YES, PARTIALLY -- R1 clears the floor and the gain is not explained by orthography"
            if (r1_clears_floor and not spelling_correlated) else
            "NOT SETTLED BY THIS RUN -- addressing improved but hit@1 neither clears the floor "
            "nor reads NOT_SEPARATED from R0; report the exact margins, do not force a verdict")}
    print("[VERDICT] %s" % json.dumps(rep["STOP_IF_VERDICT"], default=str), flush=True)

    rep["elapsed_s"] = round(time.time() - t0, 1)
    _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
    print("WROTE " + os.path.join(out_dir, "metrics.json"), flush=True)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "reduced"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    out_dir = _out_dir(a.grid)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        run(a.grid)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(out_dir, "_crash_diagnostic.json"),
                    {"error": "%s: %s" % (type(exc).__name__, exc),
                     "traceback": traceback.format_exc(),
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
