"""exp_sharpening_readout_sister_separation_v1 -- does a SHARPENING (dense/modern-Hopfield)
read-out separate PARADIGMATIC SISTERS that plain argmax cannot?

PRE-REG: preregs/2026-08-14_sharpening_readout_sister_separation.md, COMMITTED (ab0e7507c) BEFORE
this file existed and BEFORE any arm was scored. Every arm, band, floor and the EXPECTED NULL are
frozen there.

THE DEFECT (pre-reg 1)
MEASURED@data/exp_grounding_readout_known_answer_v1/metrics.json: open-vocabulary hit@1 4.80% vs
scramble 0.80% (n=4000, 5491 anchors). Every correct hit is a paradigmatic SISTER of the target.
SELF_RETRIEVAL 0.786 -- retrieval is not the constraint. This is a SEPARATION problem.

THE LEAD (pre-reg 2)
MEASURED@data/exp_dense_hopfield_readout_capacity_correlated_codes_v1/metrics.json (HARD_PASS):
3.25x capacity lift on CORRELATED codes; per-correlation 6.74x (mild) -> 3.12x (mod) -> 1.63x
(strong). NOTE THE DIRECTION: the lift SHRINKS as correlation strengthens, and sisters are the
strongly-correlated end, so the parent predicts the SMALL end of its effect here.

THE PRE-DECLARED EXPECTED OUTCOME IS NULL (pre-reg 3)
MEASURED@data/exp_cleanup_graded_attractor_vs_argmax_v1: modern-Hopfield ~= plain argmax at the
cliff; verdict STEP_IS_CODEBOOK_SNR_WALL_NOT_CLEANUP_RULE. If the evidence separating target from
sister is not in the anchor scores, no cleanup rule can manufacture it. A null here is a RESULT: it
closes cleanup-rule fixes as a CLASS for this defect. Pre-reg 3.1 declares, in advance, the
observation that separates "sharpening works" from "we are at the SNR wall".

THE ANALYTIC TRAP (pre-reg 5) -- softmax is MONOTONE, so a softmax over the TWO eligible candidate
scores is BIT-IDENTICAL to plain argmax at every beta. Arm S3 runs it anyway and the cell ASSERTS
the identity, because a demonstrated trap is cheaper than a rediscovered one. The real sharpening
arm is the one-step modern-Hopfield update over the FULL anchor set, whose RETRIEVED BLEND re-ranks
(CITED@hdlab/modern_hopfield_readout.py "RANKING NOTE"). Every beta reports the ENTROPY of its
weight distribution; nothing assumes a beta softens anything
(CITED@hdlab/multi_hop.py:84-96, where beta=None defaults to n_dim = a Dirac delta and confounded
two prior cells).

NOTHING UNDER hdlab/ IS MODIFIED. ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import (numpy sizes its pools at import time).
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import platform
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---- ORGANS REUSED. Imported, never modified. -------------------------------------------------
from hdlab.reading_grounding_loop import (                                   # noqa: E402
    CTX_D, GRADED_COMPARATOR, ConceptSpace, canonicalize_fast, normalize_lemma,
    context_vector_masked,
)
from hdlab.modern_hopfield_readout import ModernHopfieldReadout             # noqa: E402
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

# ---- THE TESTBED, IMPORTED WHOLE (pre-reg 6). Its own S1-S9 self-test runs at this import. -----
import exp_context_conditioned_near_neighbour_v1 as NN                      # noqa: E402

ANCHOR_NAME = "exp_sharpening_readout_sister_separation_v1"
PREREG_PATH = "preregs/2026-08-14_sharpening_readout_sister_separation.md"
PREREG_COMMIT = "ab0e7507c"

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

MASTER_SEED = 20260814
BOOTSTRAP_SEED = 20260814
N_BOOTSTRAP = 5000

MAX_ITEMS = 4000
MIN_ITEMS = 200
SMOKE_ITEM_SCALES = (150, 600)

# beta sweep -- logits are beta * cos / sqrt(CTX_D); sqrt(256)=16, so the effective scale is
# beta/16. The span is deliberately wide enough to reach BOTH uniform and Dirac; the entropy gate
# (pre-reg 3.1) FAILS THE CELL if it does not.
BETAS = (0.5, 2.0, 8.0, 32.0, 128.0, 512.0, 2048.0, 8192.0, 32768.0)
ENTROPY_HI_REQ = 0.80       # sweep must contain a point with normalised entropy above this
ENTROPY_LO_REQ = 0.20       # ... and one below this

HP_DS = 0.030               # best-beta S1 - S0
HP_DC = 0.020               # S1 - S2 at the same beta
HP_SISTER_CONV = 0.05       # fraction of sister errors converted
SNR_FLAT = 0.020            # |S1 - S0| below this at EVERY beta, CI including 0
SNR_SISTER = 0.01
STRICT_MARGIN_FRAC = 0.05   # META_RULE_L
SELF_RETRIEVAL_FLOOR = 0.70
CHANCE = 0.50
N_DRAWS_FULL, N_DRAWS_SMOKE = 3, 2      # between-anchor-draw floor (pre-reg 8.4)
N_EQUIV_SUBSAMPLE = 300


# ---------------------------------------------------------------------------------------------
# Durability plumbing
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _heartbeat(output_dir: str, phase: str, elapsed_s: float, extra: Optional[dict] = None) -> None:
    os.makedirs(output_dir, exist_ok=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "phase": phase,
           "elapsed_s": round(elapsed_s, 3)}
    if extra:
        row["extra"] = extra
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _atomic_write_metrics(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)                                  # META_RULE_AH
    return final


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_metrics(output_dir, {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "run_mode": "crash", "failure_class": type(exc).__name__,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME})


def _seed_for(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 32)


# ---------------------------------------------------------------------------------------------
# CONTROLLED FORK #1 -- NN.split_pools with a SALT, for the between-anchor-draw floor.
# Self-test S2 asserts salt="" reproduces NN.split_pools byte-identically.
# ---------------------------------------------------------------------------------------------
def split_pools_salted(buckets: Dict[str, List[str]], salt: str
                       ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    prof, ev = {}, {}
    for w in sorted(buckets):
        s = list(buckets[w])
        np.random.default_rng(_seed_for("split|" + salt + w)).shuffle(s)
        prof[w] = s[:NN.N_PROFILE]
        ev[w] = s[NN.N_PROFILE:]
    return prof, ev


# ---------------------------------------------------------------------------------------------
# BATCHED read-out math. The organ (ModernHopfieldReadout) is the REFERENCE; these are its batched
# equivalents, asserted equal on a subsample by self-test S3/S4. Batching only; no new mechanism.
# ---------------------------------------------------------------------------------------------
def _unit_rows(M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=1, keepdims=True)
    return (M / np.where(n < 1e-12, 1.0, n)).astype(np.float32)


def cosine_scores(Q: np.ndarray, Khat: np.ndarray) -> np.ndarray:
    """(n, M) cosine of every query against every anchor -- exactly canonicalize_fast's `sims`."""
    return (_unit_rows(Q) @ Khat.T).astype(np.float32)


def _softmax_rows(Z: np.ndarray) -> np.ndarray:
    Z = Z - Z.max(axis=1, keepdims=True)
    E = np.exp(Z, dtype=np.float32)
    return (E / E.sum(axis=1, keepdims=True)).astype(np.float32)


def hopfield_rescore(S: np.ndarray, Khat: np.ndarray, beta: float,
                     perm: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """One-step modern-Hopfield update over ALL anchors, then re-score every anchor against the
    retrieved blend.  y = K.T softmax(beta * K q / sqrt(N));  return (cos(y, K) [n, M], W [n, M]).

    `perm` (the S2/O2 control): permute the SCORE vector before the softmax, so each anchor's
    weight comes from a DIFFERENT anchor's score. The weight distribution is then a PERMUTATION of
    the real one -- its entropy is EXACTLY EQUAL by construction -- but it is content-blind."""
    n_dim = Khat.shape[1]
    Z = (float(beta) / float(np.sqrt(n_dim))) * (S if perm is None else S[:, perm])
    W = _softmax_rows(Z)
    Y = (W @ Khat).astype(np.float32)
    return (_unit_rows(Y) @ Khat.T).astype(np.float32), W


def mean_normalised_entropy(W: np.ndarray) -> float:
    """H(W)/ln(M), averaged over rows. 1.0 = uniform, 0.0 = Dirac (the multi_hop.py trap)."""
    P = np.clip(W, 1e-30, 1.0)
    H = -(P * np.log(P)).sum(axis=1)
    return float(np.mean(H) / np.log(W.shape[1]))


def pick2(C: np.ndarray, ti: np.ndarray, di: np.ndarray) -> np.ndarray:
    """2AFC from a score matrix. Tie -> the LOWER anchor index, matching canonicalize_fast's
    first-max-in-sorted-order tie-break."""
    st = C[np.arange(C.shape[0]), ti]
    sd = C[np.arange(C.shape[0]), di]
    lower_wins_target = ti < di
    return np.where(st != sd, st > sd, lower_wins_target)


# ---------------------------------------------------------------------------------------------
# Paired bootstrap over an arbitrary arm dict (all arms score the SAME items)
# ---------------------------------------------------------------------------------------------
def paired_bootstrap(correct: Dict[str, np.ndarray], deltas: Sequence[Tuple[str, str, str]],
                     n_boot: int, seed: int) -> dict:
    keys = sorted(correct)
    mat = np.stack([correct[k].astype(np.float64) for k in keys], axis=0)
    n = mat.shape[1]
    rng = np.random.default_rng(seed)
    acc = np.empty((n_boot, len(keys)), dtype=np.float64)
    done, chunk = 0, 400
    while done < n_boot:
        m = min(chunk, n_boot - done)
        idx = rng.integers(0, n, size=(m, n))
        acc[done:done + m] = mat[:, idx].mean(axis=2).T
        done += m
    ki = {k: j for j, k in enumerate(keys)}
    out = {"n_boot": n_boot, "seed": seed, "arm_acc_ci": {}, "deltas": {}}
    for k in keys:
        lo, hi = np.percentile(acc[:, ki[k]], [2.5, 97.5])
        out["arm_acc_ci"][k] = {"acc": round(float(mat[ki[k]].mean()), 6),
                                "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
                                "sd": round(float(acc[:, ki[k]].std()), 6)}
    for name, a, b in deltas:
        d = acc[:, ki[a]] - acc[:, ki[b]]
        point = float(mat[ki[a]].mean() - mat[ki[b]].mean())
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["deltas"][name] = {"delta": round(point, 6), "ci_lo": round(float(lo), 6),
                               "ci_hi": round(float(hi), 6), "sd": round(float(d.std()), 6),
                               "mde_95": round(float(1.96 * d.std()), 6),
                               "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0)}
    return out


# ---------------------------------------------------------------------------------------------
# Verdict (pre-reg 9) -- frozen before the run
# ---------------------------------------------------------------------------------------------
def decide_verdict(res: dict) -> Tuple[str, List[str]]:
    notes: List[str] = []
    ent = res["entropy_gate"]
    if not ent["gate_passed"]:
        return "SWEEP_DID_NOT_SPAN_THE_RANGE", [
            "entropy sweep spans [%.3f, %.3f]; needs a point > %.2f AND one < %.2f -- sharpening "
            "was NOT tested, no read licensed" % (ent["min"], ent["max"], ENTROPY_HI_REQ,
                                                  ENTROPY_LO_REQ)]
    dS = res["dS_best"]["delta"]
    dS_ex = res["dS_best"]["ci_excludes_zero"]
    dC = res["dC_at_best"]["delta"]
    dC_ex = res["dC_at_best"]["ci_excludes_zero"]
    bsd = res["between_draw_sd_S0"]
    conv = res["sister_conversion_rate"]
    conv_ctl = res["sister_conversion_rate_scrambled"]
    s2_gain = res["S2_at_best_minus_S0"]

    if dS > 0.0 and s2_gain >= dS:
        return "HARD_FAIL_SHARPENING_IS_CONTENT_BLIND", [
            "S1-S0=%.4f but the CONTENT-BLIND control gains %.4f (>=): the weight distribution is "
            "equally sharp by construction, so the gain is not separation" % (dS, s2_gain)]

    hp = (dS >= HP_DS and dS_ex and dC >= HP_DC and dC_ex and dS > 2.0 * bsd
          and conv >= HP_SISTER_CONV and conv_ctl < conv / 3.0)
    if hp:
        m_dS, m_dC = HP_DS * (1.0 + STRICT_MARGIN_FRAC), HP_DC * (1.0 + STRICT_MARGIN_FRAC)
        if dS < m_dS or dC < m_dC:
            return "MIDDLE_BAND_FLOOR_HUGGING", [
                "META_RULE_L: a HARD_PASS gate cleared by < 5%% of its floor "
                "(dS=%.4f/%.4f dC=%.4f/%.4f)" % (dS, m_dS, dC, m_dC)]
        return "HARD_PASS_SHARPENING_SEPARATES_SISTERS", [
            "dS=%.4f dC=%.4f both CI-clean, dS > 2*between_draw_sd (%.4f), sister conversion "
            "%.4f with control %.4f" % (dS, dC, bsd, conv, conv_ctl)]

    flat = all(abs(v["delta"]) < SNR_FLAT and not v["ci_excludes_zero"]
               for v in res["per_beta_delta"].values())
    if flat and conv <= SNR_SISTER:
        return "SNR_WALL_CLEANUP_RULE_CANNOT_HELP", [
            "the entropy sweep spans %.3f -> %.3f (uniform to Dirac: the mechanism had FULL dynamic "
            "range) and the 2AFC decision is invariant to it at every beta (max |S1-S0| = %.4f, "
            "every CI includes 0); open-vocab sister conversion %.4f <= %.2f. The binding "
            "constraint is CODEBOOK SNR, not the cleanup rule -- this closes cleanup-rule fixes as "
            "a CLASS for the sister-separation defect, agreeing with "
            "exp_cleanup_graded_attractor_vs_argmax_v1 STEP_IS_CODEBOOK_SNR_WALL_NOT_CLEANUP_RULE"
            % (ent["max"], ent["min"],
               max(abs(v["delta"]) for v in res["per_beta_delta"].values()), conv, SNR_SISTER)]
    notes.append("dS=%.4f (CI %s 0) dC=%.4f; between_draw_sd=%.4f; sister conversion %.4f "
                 "(control %.4f): neither the HARD_PASS conjunction nor the SNR-wall conjunction "
                 "is met" % (dS, "excludes" if dS_ex else "includes", dC, bsd, conv, conv_ctl))
    return "MIDDLE_BAND", notes


# ---------------------------------------------------------------------------------------------
# Self-test (MANDATORY, module scope, before any measurement; must not touch the 251 MB corpus)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {}
    rng = np.random.default_rng(5)

    # S1 -- the testbed imported cleanly and ITS OWN S1-S9 self-test passed at this import.
    assert isinstance(NN._SELFTEST_RESULT, dict) and NN._SELFTEST_RESULT.get("readout_moves"), \
        "testbed self-test did not run or did not populate"
    res["testbed_selftest_readout_moves"] = NN._SELFTEST_RESULT["readout_moves"]
    res["testbed_graded_comparator"] = bool(GRADED_COMPARATOR)

    # S2 -- CONTROLLED FORK: split_pools_salted("") is BYTE-IDENTICAL to NN.split_pools.
    fake_buckets = {w: ["s%d %s" % (i, w) for i in range(NN.N_PROFILE + 12)]
                    for w in ("poet", "river", "novelist")}
    p_a, e_a = NN.split_pools(fake_buckets)
    p_b, e_b = split_pools_salted(fake_buckets, "")
    assert p_a == p_b and e_a == e_b, "split_pools_salted('') has FORKED NN.split_pools"
    p_c, _ = split_pools_salted(fake_buckets, "draw2|")
    assert p_c != p_a, "a salted redraw produced the SAME split -- the floor axis does not vary"
    res["split_salt_identity_and_variation"] = True

    # S3 -- BATCHED cosine == canonicalize_fast's own sims, on a REAL ConceptSpace.
    sp = ConceptSpace(d=CTX_D)
    prof = {"poet": ["The poet wrote verses and published a book of poems every winter.",
                     "A famous poet read verses aloud at the library and the school."],
            "novelist": ["The novelist wrote a long story about a family and a war.",
                         "A novelist published a story and later wrote another long book."],
            "river": ["The river flows through the valley and past the bridge each spring.",
                      "Boats travel along the river between the town and the sea."],
            "valley": ["The valley lies between two mountains and holds a small town.",
                       "Farmers work the valley fields beside the road each summer."]}
    for w, sents in prof.items():
        for s in sents:
            sp.observe(w, context_vector_masked(s, w))
    anchors, mat = sp.anchor_matrix()
    Khat = _unit_rows(mat)
    probes = ["She read verses from a book of poems at the library.",
              "Boats travel through the valley past the bridge to the sea.",
              "A long story about a family and a war was published."]
    Q = np.stack([NN._ctx_masked_multi(s, []) for s in probes], axis=0)
    S = cosine_scores(Q, Khat)
    # open-vocabulary argmax must match canonicalize_fast with every anchor eligible
    for i, s in enumerate(probes):
        pick, _c = canonicalize_fast("__slot__", Q[i], sp, thresh=-1.0)
        assert anchors[int(np.argmax(S[i]))] == pick, (
            "BATCHED BASELINE HAS FORKED canonicalize_fast on probe %d: %r vs %r"
            % (i, anchors[int(np.argmax(S[i]))], pick))
    res["batched_baseline_matches_canonicalize_fast"] = True

    # S4 -- BATCHED Hopfield == the ORGAN (ModernHopfieldReadout), row by row.
    for beta in (2.0, 64.0, 1024.0):
        Cy, W = hopfield_rescore(S, Khat, beta)
        r = ModernHopfieldReadout(beta=beta, normalize_query_and_store=True)
        for i in range(Q.shape[0]):
            _top, y_ref, w_ref = r.top_k_by_retrieved(Q[i], mat, k=1)
            assert np.allclose(W[i], w_ref, atol=2e-5), (
                "batched attention weights diverged from the organ at beta=%g row %d" % (beta, i))
            yn = float(np.linalg.norm(y_ref))
            cos_ref = (Khat @ (y_ref / yn)).astype(np.float32)
            assert np.allclose(Cy[i], cos_ref, atol=2e-5), (
                "batched retrieved re-score diverged from the organ at beta=%g row %d" % (beta, i))
    res["batched_hopfield_matches_organ"] = ["beta=2", "beta=64", "beta=1024"]

    # S5 -- THE TRAP, DEMONSTRATED: a softmax over the TWO eligible scores is bit-identical to
    #       argmax at every beta (monotone), while the FULL-SET Hopfield update is NOT.
    M = 40
    Kt = _unit_rows(rng.standard_normal((M, 64)).astype(np.float32))
    Qt = rng.standard_normal((200, 64)).astype(np.float32)
    St = cosine_scores(Qt, Kt)
    ti = rng.integers(0, M, size=200)
    di = (ti + 1 + rng.integers(0, M - 1, size=200)) % M
    base = pick2(St, ti, di)
    for beta in (0.5, 8.0, 512.0):
        two = _softmax_rows(beta * np.stack([St[np.arange(200), ti],
                                             St[np.arange(200), di]], axis=1))
        assert np.array_equal(two[:, 0] > two[:, 1], St[np.arange(200), ti]
                              > St[np.arange(200), di]), \
            "2-candidate softmax is NOT monotone-pinned at beta=%g -- the trap analysis is wrong" \
            % beta
    Cy_mid, _ = hopfield_rescore(St, Kt, 8.0)
    assert not np.array_equal(pick2(Cy_mid, ti, di), base), (
        "the FULL-SET Hopfield update produced IDENTICAL picks to argmax on random codes -- the "
        "sharpening arm cannot move and would be analytically pinned")
    res["trap_two_candidate_softmax_is_pinned"] = True
    res["fullset_hopfield_can_move"] = True

    # S6 -- entropy is real and MONOTONE DECREASING in beta (the multi_hop.py trap gate).
    ents = [mean_normalised_entropy(hopfield_rescore(St, Kt, b)[1])
            for b in (0.01, 1.0, 100.0, 100000.0)]
    assert all(ents[i] >= ents[i + 1] - 1e-6 for i in range(len(ents) - 1)), \
        "normalised entropy is not monotone in beta: %r" % ents
    assert ents[0] > 0.99, "beta -> 0 did not give a near-uniform distribution: %.4f" % ents[0]
    assert ents[-1] < 0.05, "beta -> inf did not give a near-Dirac distribution: %.4f" % ents[-1]
    res["entropy_monotone_and_spans"] = [round(e, 4) for e in ents]

    # S7 -- the CONTENT-BLIND control has EXACTLY the same entropy and DIFFERENT picks.
    perm = np.roll(np.arange(M), M // 2 + 1)
    Cy_r, W_r = hopfield_rescore(St, Kt, 8.0)
    Cy_c, W_c = hopfield_rescore(St, Kt, 8.0, perm=perm)
    assert abs(mean_normalised_entropy(W_r) - mean_normalised_entropy(W_c)) < 1e-5, \
        "the scrambled control is NOT entropy-matched -- it is not an equally-sharp control"
    assert not np.array_equal(pick2(Cy_r, ti, di), pick2(Cy_c, ti, di)), \
        "the content-blind control produced identical picks -- it cannot discriminate"
    res["control_entropy_matched_and_differs"] = True

    # S8 -- the bootstrap separates a real delta from a null one (false-positive RATE, not a draw).
    n = 300
    b0 = rng.random(n) < 0.50
    b1 = b0 | (rng.random(n) < 0.25)
    bs = paired_bootstrap({"A": b1, "B": b0}, [("d", "A", "B")], 400, 7)
    assert bs["deltas"]["d"]["ci_excludes_zero"], "bootstrap missed a real delta"
    fp = 0
    for s in range(6):
        r2 = np.random.default_rng(2000 + s)
        null = {"A": r2.random(800) < 0.5, "B": r2.random(800) < 0.5}
        if paired_bootstrap(null, [("d", "A", "B")], 400, 7)["deltas"]["d"]["ci_excludes_zero"]:
            fp += 1
    assert fp <= 1, "bootstrap false-positive rate too high: %d/6" % fp
    res["bootstrap_selftest"] = {"real_delta": bs["deltas"]["d"]["delta"], "null_fp": fp}

    # S9 -- every verdict branch is REACHABLE.
    def _r(dS, dSex, dC, dCex, bsd, conv, conv_c, s2, ent_ok=True, flat=False):
        pb = {"b1": {"delta": 0.001 if flat else dS, "ci_excludes_zero": False if flat else dSex},
              "b2": {"delta": -0.002 if flat else dS, "ci_excludes_zero": False if flat else dSex}}
        return {"entropy_gate": {"gate_passed": ent_ok, "min": 0.02, "max": 0.99},
                "dS_best": {"delta": dS, "ci_excludes_zero": dSex},
                "dC_at_best": {"delta": dC, "ci_excludes_zero": dCex},
                "between_draw_sd_S0": bsd, "sister_conversion_rate": conv,
                "sister_conversion_rate_scrambled": conv_c, "S2_at_best_minus_S0": s2,
                "per_beta_delta": pb}
    seen = sorted({
        decide_verdict(_r(0.09, True, 0.06, True, 0.005, 0.20, 0.01, 0.01))[0],
        decide_verdict(_r(0.031, True, 0.021, True, 0.005, 0.06, 0.001, 0.01))[0],
        decide_verdict(_r(0.05, True, 0.03, True, 0.004, 0.10, 0.02, 0.06))[0],
        decide_verdict(_r(0.0, False, 0.0, False, 0.004, 0.0, 0.0, -0.01, flat=True))[0],
        decide_verdict(_r(0.02, True, 0.01, True, 0.004, 0.02, 0.001, 0.005))[0],
        decide_verdict(_r(0.09, True, 0.06, True, 0.005, 0.2, 0.01, 0.01, ent_ok=False))[0]})
    want = sorted(["HARD_PASS_SHARPENING_SEPARATES_SISTERS", "MIDDLE_BAND_FLOOR_HUGGING",
                   "HARD_FAIL_SHARPENING_IS_CONTENT_BLIND", "SNR_WALL_CLEANUP_RULE_CANNOT_HELP",
                   "MIDDLE_BAND", "SWEEP_DID_NOT_SPAN_THE_RANGE"])
    assert seen == want, "verdict branches not all reachable: got %r want %r" % (seen, want)
    res["verdict_branches_reachable"] = seen

    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# One anchor draw: build space + queries + baseline/sharpened scores for a given split salt
# ---------------------------------------------------------------------------------------------
def _build_draw(assets: dict, salt: str, max_items: int):
    prof, ev = split_pools_salted(assets["buckets"], salt)
    items, diag = NN.build_items(assets["pairs_strict"], ev, max_items)
    if len(items) < 2:
        raise AssertionError("VACUOUS DRAW %r: %d items" % (salt, len(items)))
    words = sorted({w for it in items for w in (it["target"], it["distractor"])})
    space = NN.build_space(words, prof)
    anchors, mat = space.anchor_matrix()
    assert float(np.linalg.norm(mat, axis=1).min()) > 0, "an anchor is a zero vector"
    return items, diag, space, anchors, mat, prof


def _queries(items, kind: str) -> Tuple[np.ndarray, int]:
    """kind='real' -> this item's masked sentence; 'scram' -> a DIFFERENT item's (derangement)."""
    if kind == "real":
        src = list(range(len(items)))
    else:
        src = NN.assign_donors(items)
    out, n_zero = [], 0
    for i, it in enumerate(items):
        d = items[src[i]]
        drop = [normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                it["target"], it["distractor"]]
        if src[i] != i:
            drop += [normalize_lemma(d["target"]), normalize_lemma(d["distractor"]),
                     d["target"], d["distractor"]]
        q = NN._ctx_masked_multi(d["sentence"], drop)
        if float(np.linalg.norm(q)) < 1e-9:
            n_zero += 1
        out.append(q)
    return np.stack(out, axis=0), n_zero


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, max_items: int) -> dict:
    t0 = time.time()
    n_draws = N_DRAWS_FULL if run_mode == "full" else N_DRAWS_SMOKE
    n_boot = N_BOOTSTRAP if run_mode == "full" else 1000
    _write_start_marker(output_dir, run_mode, (2 + 2 * len(BETAS)) + n_draws)

    assets = NN.build_corpus_assets()
    counts = assets["counts"]

    # ---- PRIMARY DRAW (salt "" == the landed baseline's own split, byte-identical) --------------
    items, item_diag, space, anchors, mat, prof = _build_draw(assets, "", max_items)
    n = len(items)
    print("[items] n=%d anchors=%d %s" % (n, len(anchors), json.dumps(item_diag["removals"])),
          flush=True)
    if run_mode == "full" and n < MIN_ITEMS:
        m = {"verdict": "INSUFFICIENT_ITEMS_NO_READ",
             "verdict_msg": "only %d clean items (floor %d); STOPPED rather than underpowered"
                            % (n, MIN_ITEMS),
             "summary": "sharpening read-out -- item gate stopped the run", "n_items": n,
             "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
             "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
             "ts_iso": datetime.now(timezone.utc).isoformat(), "cardinality_ok": False}
        _atomic_write_metrics(output_dir, m)
        return m

    pos = {a: i for i, a in enumerate(anchors)}
    ti = np.array([pos[it["target"]] for it in items], dtype=np.int64)
    di = np.array([pos[it["distractor"]] for it in items], dtype=np.int64)
    Khat = _unit_rows(mat)

    Q, n_zero_q = _queries(items, "real")
    Qs, n_zero_qs = _queries(items, "scram")
    S = cosine_scores(Q, Khat)
    Ss = cosine_scores(Qs, Khat)
    _heartbeat(output_dir, "scores_built", time.time() - t0, {"n": n, "M": len(anchors)})

    # ---- GATE: the batched baseline must BE the live read-out ----------------------------------
    rng_eq = np.random.default_rng(MASTER_SEED)
    sub = np.sort(rng_eq.choice(n, size=min(N_EQUIV_SUBSAMPLE, n), replace=False))
    n_mismatch_2afc = n_mismatch_open = 0
    for i in sub:
        if float(np.linalg.norm(Q[i])) < 1e-9:
            continue
        m2 = np.zeros(len(anchors), dtype=bool)
        m2[ti[i]] = True
        m2[di[i]] = True
        p2, _c = canonicalize_fast("__slot__", Q[i], space, thresh=-1.0, eligible_mask=m2)
        mine2 = anchors[ti[i]] if pick2(S[i:i + 1], ti[i:i + 1], di[i:i + 1])[0] \
            else anchors[di[i]]
        n_mismatch_2afc += int(mine2 != p2)
        po, _c = canonicalize_fast("__slot__", Q[i], space, thresh=-1.0)
        n_mismatch_open += int(anchors[int(np.argmax(S[i]))] != po)
    baseline_is_live = (n_mismatch_2afc == 0 and n_mismatch_open == 0)
    print("[gate] baseline-vs-canonicalize_fast mismatches: 2afc=%d open=%d (n_sub=%d)"
          % (n_mismatch_2afc, n_mismatch_open, len(sub)), flush=True)

    # ---- ARMS ----------------------------------------------------------------------------------
    perm = np.roll(np.arange(len(anchors)), len(anchors) // 2 + 1)   # deterministic derangement
    correct: Dict[str, np.ndarray] = {}
    correct["S0_ARGMAX_BASELINE"] = pick2(S, ti, di)
    correct["SF_SCRAMBLE_FLOOR"] = pick2(Ss, ti, di)
    fr, fr_diag = NN.arm_frequency(items, counts, np.random.default_rng(MASTER_SEED + 4))
    correct["SF_FREQUENCY_FLOOR"] = fr

    open_hit: Dict[str, np.ndarray] = {}
    open_pick: Dict[str, np.ndarray] = {}
    open_pick["O0_ARGMAX"] = np.asarray(anchors, dtype=object)[np.argmax(S, axis=1)]
    open_hit["O0_ARGMAX"] = (np.argmax(S, axis=1) == ti)
    open_hit["OF_SCRAMBLE_FLOOR"] = (np.argmax(Ss, axis=1) == ti)

    entropies: Dict[str, float] = {}
    per_beta: Dict[str, dict] = {}
    for beta in BETAS:
        Cy, W = hopfield_rescore(S, Khat, beta)
        Cc, Wc = hopfield_rescore(S, Khat, beta, perm=perm)
        e_r, e_c = mean_normalised_entropy(W), mean_normalised_entropy(Wc)
        assert abs(e_r - e_c) < 1e-4, "control not entropy-matched at beta=%g" % beta
        entropies["beta_%g" % beta] = round(e_r, 6)
        correct["S1_SHARPEN_b%g" % beta] = pick2(Cy, ti, di)
        correct["S2_SCRAMBLED_b%g" % beta] = pick2(Cc, ti, di)
        # the PINNED arm (pre-reg 5): softmax over the two eligible scores only
        two = _softmax_rows(beta * np.stack([S[np.arange(n), ti], S[np.arange(n), di]], axis=1))
        correct["S3_TWOCAND_b%g" % beta] = two[:, 0] > two[:, 1]
        am, amc = np.argmax(Cy, axis=1), np.argmax(Cc, axis=1)
        open_pick["O1_SHARPEN_b%g" % beta] = np.asarray(anchors, dtype=object)[am]
        open_pick["O2_SCRAMBLED_b%g" % beta] = np.asarray(anchors, dtype=object)[amc]
        open_hit["O1_SHARPEN_b%g" % beta] = (am == ti)
        open_hit["O2_SCRAMBLED_b%g" % beta] = (amc == ti)
        key = unit_key(ANCHOR_NAME, run_mode, str(n), "beta%g" % beta)
        if key not in completed_units(output_dir):
            record_unit(output_dir, key, {
                "beta": beta, "entropy": entropies["beta_%g" % beta],
                "S1": float(correct["S1_SHARPEN_b%g" % beta].mean()),
                "S2": float(correct["S2_SCRAMBLED_b%g" % beta].mean()),
                "O1": float(open_hit["O1_SHARPEN_b%g" % beta].mean())})
        print("[beta] %-8g entropy=%.4f S1=%.4f S2=%.4f S3=%.4f O1=%.5f O2=%.5f"
              % (beta, e_r, correct["S1_SHARPEN_b%g" % beta].mean(),
                 correct["S2_SCRAMBLED_b%g" % beta].mean(),
                 correct["S3_TWOCAND_b%g" % beta].mean(),
                 open_hit["O1_SHARPEN_b%g" % beta].mean(),
                 open_hit["O2_SCRAMBLED_b%g" % beta].mean()), flush=True)
        _heartbeat(output_dir, "beta_done", time.time() - t0, {"beta": beta})
        del Cy, W, Cc, Wc

    # ---- the TRAP assertion: S3 is bit-identical to S0 at every beta ----------------------------
    trap_ok = all(np.array_equal(correct["S3_TWOCAND_b%g" % b], correct["S0_ARGMAX_BASELINE"])
                  for b in BETAS)

    # ---- entropy gate (pre-reg 3.1) ------------------------------------------------------------
    e_vals = list(entropies.values())
    entropy_gate = {"min": round(min(e_vals), 6), "max": round(max(e_vals), 6),
                    "need_above": ENTROPY_HI_REQ, "need_below": ENTROPY_LO_REQ,
                    "gate_passed": bool(max(e_vals) > ENTROPY_HI_REQ
                                        and min(e_vals) < ENTROPY_LO_REQ),
                    "per_beta": entropies}

    # ---- bootstrap on the 2AFC arms ------------------------------------------------------------
    boot_arms = {k: v for k, v in correct.items() if not k.startswith("S3_")}
    deltas = [("d_S1b%g_minus_S0" % b, "S1_SHARPEN_b%g" % b, "S0_ARGMAX_BASELINE") for b in BETAS]
    deltas += [("d_S1b%g_minus_S2b%g" % (b, b), "S1_SHARPEN_b%g" % b, "S2_SCRAMBLED_b%g" % b)
               for b in BETAS]
    deltas += [("d_S2b%g_minus_S0" % b, "S2_SCRAMBLED_b%g" % b, "S0_ARGMAX_BASELINE")
               for b in BETAS]
    deltas += [("d_S0_minus_SCRAMBLE", "S0_ARGMAX_BASELINE", "SF_SCRAMBLE_FLOOR"),
               ("d_S0_minus_FREQUENCY", "S0_ARGMAX_BASELINE", "SF_FREQUENCY_FLOOR")]
    bs = paired_bootstrap(boot_arms, deltas, n_boot, BOOTSTRAP_SEED)

    per_beta = {("beta_%g" % b): bs["deltas"]["d_S1b%g_minus_S0" % b] for b in BETAS}
    best_beta = max(BETAS, key=lambda b: bs["deltas"]["d_S1b%g_minus_S0" % b]["delta"])
    dS_best = bs["deltas"]["d_S1b%g_minus_S0" % best_beta]
    dC_best = bs["deltas"]["d_S1b%g_minus_S2b%g" % (best_beta, best_beta)]
    s2_gain = bs["deltas"]["d_S2b%g_minus_S0" % best_beta]["delta"]

    # ---- OPEN-VOCAB: SISTER-ERROR CONVERSION (pre-reg 7.2) -- the finding ----------------------
    sib: Dict[str, set] = defaultdict(set)
    for a, b in assets["pairs_loose"]:
        sib[a].add(b)
        sib[b].add(a)
    tgt = np.asarray([it["target"] for it in items], dtype=object)
    base_wrong = ~open_hit["O0_ARGMAX"]
    base_sister_err = np.array([bool(base_wrong[i] and open_pick["O0_ARGMAX"][i] in sib[tgt[i]])
                                for i in range(n)], dtype=bool)
    n_sister_err = int(base_sister_err.sum())
    best_o_beta = max(BETAS, key=lambda b: float(open_hit["O1_SHARPEN_b%g" % b].mean()))
    conv = {}
    for b in BETAS:
        conv["beta_%g" % b] = {
            "converted_by_O1": int((base_sister_err & open_hit["O1_SHARPEN_b%g" % b]).sum()),
            "converted_by_O2_control":
                int((base_sister_err & open_hit["O2_SCRAMBLED_b%g" % b]).sum())}
    n_conv = max(v["converted_by_O1"] for v in conv.values())
    n_conv_ctl = max(v["converted_by_O2_control"] for v in conv.values())
    conv_rate = round(n_conv / max(1, n_sister_err), 6)
    conv_rate_ctl = round(n_conv_ctl / max(1, n_sister_err), 6)
    print("[sister] baseline open-vocab errors that are WordNet sisters: %d/%d; BEST-beta "
          "conversions: %d (control %d) -> rate %.4f (control %.4f)"
          % (n_sister_err, int(base_wrong.sum()), n_conv, n_conv_ctl, conv_rate, conv_rate_ctl),
          flush=True)

    open_bs = paired_bootstrap(
        {"O0_ARGMAX": open_hit["O0_ARGMAX"], "OF_SCRAMBLE_FLOOR": open_hit["OF_SCRAMBLE_FLOOR"],
         "O1_BEST": open_hit["O1_SHARPEN_b%g" % best_o_beta],
         "O2_BEST": open_hit["O2_SCRAMBLED_b%g" % best_o_beta]},
        [("d_O0_minus_FLOOR", "O0_ARGMAX", "OF_SCRAMBLE_FLOOR"),
         ("d_O1_minus_O0", "O1_BEST", "O0_ARGMAX"),
         ("d_O1_minus_O2", "O1_BEST", "O2_BEST")], n_boot, BOOTSTRAP_SEED + 1)

    # ---- SNR DIAGNOSTICS (pre-reg 7.3) ---------------------------------------------------------
    rank_t = (S > S[np.arange(n), ti][:, None]).sum(axis=1) + 1
    gap = S[np.arange(n), ti] - S[np.arange(n), di]
    snr = {"median_rank_of_target_among_all_anchors": float(np.median(rank_t)),
           "mean_rank_of_target": round(float(rank_t.mean()), 2),
           "n_anchors": len(anchors),
           "frac_target_outside_top50": round(float((rank_t > 50).mean()), 6),
           "frac_target_rank1": round(float((rank_t == 1).mean()), 6),
           "frac_items_score_gap_below_1e-3": round(float((np.abs(gap) < 1e-3).mean()), 6),
           "mean_abs_gap_when_baseline_correct":
               round(float(np.abs(gap[correct["S0_ARGMAX_BASELINE"]]).mean()), 6),
           "mean_abs_gap_when_baseline_wrong":
               round(float(np.abs(gap[~correct["S0_ARGMAX_BASELINE"]]).mean()), 6)}
    print("[snr] median target rank=%.0f/%d outside_top50=%.4f gap<1e-3=%.4f"
          % (snr["median_rank_of_target_among_all_anchors"], len(anchors),
             snr["frac_target_outside_top50"], snr["frac_items_score_gap_below_1e-3"]), flush=True)

    # ---- POSITIVE CONTROL: SELF_RETRIEVAL (inherited) ------------------------------------------
    rng_sr = np.random.default_rng(MASTER_SEED + 9)
    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    sr_words = [words_used[i] for i in
                np.sort(rng_sr.choice(len(words_used), size=min(300, len(words_used)),
                                      replace=False))]
    sr_hits = 0
    for w in sr_words:
        sents = prof.get(w, [])
        if not sents:
            continue
        other = words_used[int(rng_sr.integers(len(words_used)))]
        while other == w:
            other = words_used[int(rng_sr.integers(len(words_used)))]
        q = NN._ctx_masked_multi(sents[0], [w, other, normalize_lemma(w), normalize_lemma(other)])
        m = np.zeros(len(anchors), dtype=bool)
        m[pos[w]] = True
        m[pos[other]] = True
        p, _c = canonicalize_fast("__slot__", q, space, thresh=-1.0, eligible_mask=m)
        sr_hits += int(p == w)
    self_retrieval = round(sr_hits / max(1, len(sr_words)), 4)
    print("[positive-control] SELF_RETRIEVAL=%.4f (floor %.2f, n=%d)"
          % (self_retrieval, SELF_RETRIEVAL_FLOOR, len(sr_words)), flush=True)

    # ---- BETWEEN-ANCHOR-DRAW FLOOR (pre-reg 8.4) -----------------------------------------------
    draw_S0, draw_dS = [float(correct["S0_ARGMAX_BASELINE"].mean())], [dS_best["delta"]]
    for r in range(1, n_draws):
        salt = "draw%d|" % r
        it_r, _dg, sp_r, an_r, mat_r, _pr = _build_draw(assets, salt, max_items)
        pos_r = {a: i for i, a in enumerate(an_r)}
        ti_r = np.array([pos_r[x["target"]] for x in it_r], dtype=np.int64)
        di_r = np.array([pos_r[x["distractor"]] for x in it_r], dtype=np.int64)
        Kh_r = _unit_rows(mat_r)
        Q_r, _z = _queries(it_r, "real")
        S_r = cosine_scores(Q_r, Kh_r)
        b0 = pick2(S_r, ti_r, di_r)
        Cy_r, _W = hopfield_rescore(S_r, Kh_r, best_beta)
        b1 = pick2(Cy_r, ti_r, di_r)
        draw_S0.append(float(b0.mean()))
        draw_dS.append(float(b1.mean() - b0.mean()))
        key = unit_key(ANCHOR_NAME, run_mode, str(n), "draw%d" % r)
        if key not in completed_units(output_dir):
            record_unit(output_dir, key, {"salt": salt, "n_items": len(it_r),
                                          "S0": draw_S0[-1], "dS": draw_dS[-1]})
        print("[draw] %s n=%d S0=%.4f dS(best_beta)=%.4f"
              % (salt, len(it_r), draw_S0[-1], draw_dS[-1]), flush=True)
        _heartbeat(output_dir, "draw_done", time.time() - t0, {"salt": salt})
        del S_r, Cy_r, Kh_r, mat_r
    between_sd_S0 = float(np.std(draw_S0, ddof=1)) if len(draw_S0) > 1 else 0.0
    between_sd_dS = float(np.std(draw_dS, ddof=1)) if len(draw_dS) > 1 else 0.0

    # ---- META_RULE_AF, applied at the MECHANISM level rather than pairwise -----------------------
    # A blanket pairwise "no two arms may be bit-identical" is the WRONG SHAPE for a beta SWEEP and
    # was replaced after the first smoke exposed three ANALYTICALLY FORCED identities that are not
    # defects but predictions:
    #   (a) S3[b] == S0 at every beta -- the declared trap (softmax is monotone). REQUIRED, not
    #       tolerated; `trap_ok` fails the cell if it does NOT hold.
    #   (b) S1[b] == S2[b] wherever the weight distribution is UNIFORM: a PERMUTATION of a uniform
    #       vector is that same uniform vector, so the real and content-blind blends are the same
    #       object. Allowed ONLY where entropy > 0.999; an identity at a NON-uniform beta would
    #       mean the control is not actually content-blind, and IS a violation.
    #   (c) S1[b1] == S1[b2] for adjacent betas in saturation (both Dirac) -- what a saturating
    #       sweep looks like; the sweep's whole purpose is to show where it saturates.
    # What AF is actually FOR here -- the arms must differ WHERE THE CLAIM IS MADE -- is enforced
    # strictly at the best beta, which is the only beta any band reads.
    digests = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in correct.items()}
    af_violations: List[str] = []
    if digests["S1_SHARPEN_b%g" % best_beta] == digests["S0_ARGMAX_BASELINE"]:
        af_violations.append("S1[best_beta=%g] is bit-identical to the baseline: the sharpening "
                             "arm did nothing at its OWN best point" % best_beta)
    if digests["S1_SHARPEN_b%g" % best_beta] == digests["S2_SCRAMBLED_b%g" % best_beta]:
        af_violations.append("S1[best_beta=%g] is bit-identical to the content-blind control"
                             % best_beta)
    for b in BETAS:
        if (digests["S1_SHARPEN_b%g" % b] == digests["S2_SCRAMBLED_b%g" % b]
                and entropies["beta_%g" % b] <= 0.999):
            af_violations.append("S1==S2 at beta=%g where entropy=%.4f is NOT uniform: the "
                                 "control is not content-blind" % (b, entropies["beta_%g" % b]))
    dup = ["S1==S2 at beta=%g (entropy %.4f, uniform: analytically forced)"
           % (b, entropies["beta_%g" % b]) for b in BETAS
           if digests["S1_SHARPEN_b%g" % b] == digests["S2_SCRAMBLED_b%g" % b]]
    dup += ["S3==S0 at every beta (the declared trap)"] if trap_ok else []
    undeclared_dup = af_violations

    # ---- VERDICT --------------------------------------------------------------------------------
    res = {"entropy_gate": entropy_gate, "dS_best": dS_best, "dC_at_best": dC_best,
           "between_draw_sd_S0": between_sd_S0, "sister_conversion_rate": conv_rate,
           "sister_conversion_rate_scrambled": conv_rate_ctl,
           "S2_at_best_minus_S0": s2_gain, "per_beta_delta": per_beta}
    verdict, notes = decide_verdict(res)
    if not baseline_is_live:
        verdict = "INSTRUMENTATION_SUSPECT_BASELINE_FORK"
        notes = ["the batched baseline is NOT canonicalize_fast: %d 2AFC / %d open-vocab "
                 "mismatches on a %d-item subsample -- no read licensed"
                 % (n_mismatch_2afc, n_mismatch_open, len(sub))] + notes
    if not trap_ok:
        verdict = "INSTRUMENTATION_SUSPECT_TRAP_ASSERTION_FAILED"
        notes = ["S3 (2-candidate softmax) is NOT bit-identical to S0; softmax monotonicity is "
                 "violated, so the score plumbing is wrong"] + notes
    if self_retrieval < SELF_RETRIEVAL_FLOOR:
        verdict = "INSTRUMENTATION_SUSPECT_SELF_RETRIEVAL_BELOW_FLOOR"
        notes = ["SELF_RETRIEVAL=%.4f < %.2f" % (self_retrieval, SELF_RETRIEVAL_FLOOR)] + notes
    if undeclared_dup:
        verdict = "HARD_FAIL_META_RULE_AF_ARMS_IDENTICAL"
        notes = ["undeclared bit-identical arms: %r" % undeclared_dup] + notes

    units = load_units(output_dir)
    accs = {k: round(float(v.mean()), 6) for k, v in correct.items()}
    open_accs = {k: round(float(v.mean()), 6) for k, v in open_hit.items()}
    msg = ("n=%d anchors=%d | S0=%.4f (live baseline; landed pre-flip 0.6395, graded-ON target "
           "0.698) scramble=%.4f frequency=%.4f chance=0.50 | best_beta=%g dS=%.4f "
           "CI=[%.4f,%.4f] dC=%.4f CI=[%.4f,%.4f] S2-S0=%.4f | between_draw_sd(S0)=%.4f "
           "(n_draws=%d) | entropy %.3f..%.3f gate=%s | OPEN-VOCAB O0=%.5f floor=%.5f best "
           "O1=%.5f | SISTER ERRORS %d, CONVERTED %d (rate %.4f) vs content-blind control %d "
           "(rate %.4f) | median target rank %.0f/%d | self_retrieval=%.4f | %s"
           % (n, len(anchors), accs["S0_ARGMAX_BASELINE"], accs["SF_SCRAMBLE_FLOOR"],
              accs["SF_FREQUENCY_FLOOR"], best_beta, dS_best["delta"], dS_best["ci_lo"],
              dS_best["ci_hi"], dC_best["delta"], dC_best["ci_lo"], dC_best["ci_hi"], s2_gain,
              between_sd_S0, n_draws, entropy_gate["min"], entropy_gate["max"],
              entropy_gate["gate_passed"], open_accs["O0_ARGMAX"],
              open_accs["OF_SCRAMBLE_FLOOR"], open_accs["O1_SHARPEN_b%g" % best_o_beta],
              n_sister_err, n_conv, conv_rate, n_conv_ctl, conv_rate_ctl,
              snr["median_rank_of_target_among_all_anchors"], len(anchors), self_retrieval,
              "; ".join(notes)))

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "does a sharpening (dense/modern-Hopfield) read-out separate paradigmatic "
                   "sisters that plain argmax cannot, or are we at the codebook SNR wall?",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "prereg_commit": PREREG_COMMIT,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "hdlab_modified": False,
        "n_items": n, "n_anchors": len(anchors), "chance": CHANCE,
        "arm_accuracy_2afc": accs, "open_vocab_hit_at_1": open_accs,
        "arm_labels": {
            "S0_ARGMAX_BASELINE": "live read-out unchanged (canonicalize_fast, 2 eligible)",
            "S1_SHARPEN_b<beta>": "one-step modern-Hopfield update over ALL anchors "
                                  "(hdlab.modern_hopfield_readout), then argmax over the 2",
            "S2_SCRAMBLED_b<beta>": "THE DECIDING CONTROL: identical update with the anchor-score "
                                    "vector permuted before the softmax -- entropy EXACTLY equal "
                                    "by construction, content-blind",
            "S3_TWOCAND_b<beta>": "PINNED BY CONSTRUCTION: softmax over the 2 eligible scores; "
                                  "softmax is monotone so this IS argmax at every beta",
            "SF_SCRAMBLE_FLOOR": "donor-sentence query (deterministic derangement)",
            "SF_FREQUENCY_FLOOR": "pick the corpus-more-frequent candidate",
            "O0/O1/O2": "the same three read-outs with ALL anchors eligible (open vocabulary)"},
        "beta_sweep": {"betas": list(BETAS), "mean_normalised_entropy": entropies,
                       "entropy_gate": entropy_gate,
                       "per_beta_delta_vs_baseline": per_beta,
                       "best_beta_2afc": best_beta, "best_beta_open_vocab": best_o_beta,
                       "logit_scale_note": "logits = beta * cos / sqrt(%d); entropy is REPORTED, "
                                           "never assumed (multi_hop.py beta=n_dim trap)" % CTX_D},
        "headline_deltas": {"dS_best_S1_minus_S0": dS_best, "dC_best_S1_minus_S2": dC_best,
                            "S2_at_best_minus_S0": s2_gain},
        "floors": {"chance": CHANCE,
                   "in_cell_scramble": accs["SF_SCRAMBLE_FLOOR"],
                   "frequency": accs["SF_FREQUENCY_FLOOR"],
                   "between_anchor_draw_sd_S0": round(between_sd_S0, 6),
                   "between_anchor_draw_sd_dS": round(between_sd_dS, 6),
                   "n_draws": n_draws, "per_draw_S0": [round(x, 6) for x in draw_S0],
                   "per_draw_dS": [round(x, 6) for x in draw_dS],
                   "draw_axis_note": "context_vector's projection is a sha256(word)-seeded bipolar "
                                     "draw with NO salt (hdlab/grounding_acquisition_loop.py:155), "
                                     "so no projection seed exists to vary without forking the "
                                     "live encoder; the redraw axis is ANCHOR CONSTRUCTION "
                                     "(independent profile/eval split seeds, space rebuilt)"},
        "sister_error_conversion": {
            "definition": "sister(target) = WordNet LOOSE sibling set (pairs_loose, the "
                          "predecessor's own criterion). Among items where the OPEN-VOCAB baseline "
                          "was WRONG and its pick is a sister of the target, how many does the "
                          "sharpened read-out get RIGHT?",
            "n_open_vocab_errors": int(base_wrong.sum()),
            "n_sister_errors": n_sister_err,
            "n_converted_best_beta": n_conv, "conversion_rate": conv_rate,
            "n_converted_content_blind_control": n_conv_ctl,
            "conversion_rate_control": conv_rate_ctl,
            "per_beta": conv,
            "comparison_declared_in_prereg": "the prior rank-1 common-mode cell converted ZERO"},
        "open_vocab_bootstrap": open_bs,
        "snr_diagnostics": snr,
        "bootstrap_2afc": bs,
        "verdict_notes": notes,
        "bands": {"HARD_PASS": {"dS": HP_DS, "dC": HP_DC, "sister_conversion": HP_SISTER_CONV,
                                "and_dS_gt_2x_between_draw_sd": True},
                  "SNR_WALL": {"all_beta_abs_delta_below": SNR_FLAT,
                               "and_sister_conversion_at_most": SNR_SISTER,
                               "and_entropy_gate_passed": True},
                  "HARD_FAIL_CONTENT_BLIND": {"S2_minus_S0_ge_dS": True},
                  "strict_margin_frac": STRICT_MARGIN_FRAC,
                  "declared_in": PREREG_PATH, "declared_at_commit": PREREG_COMMIT},
        "gates": {"baseline_is_live_readout": baseline_is_live,
                  "n_mismatch_2afc": n_mismatch_2afc, "n_mismatch_open": n_mismatch_open,
                  "equivalence_subsample_n": len(sub),
                  "trap_S3_identical_to_S0": trap_ok,
                  "n_zero_norm_query_real": n_zero_q, "n_zero_norm_query_scramble": n_zero_qs,
                  "arms_differ_verified": not undeclared_dup,
                  "declared_identical_pairs": dup},
        "positive_control_self_retrieval": {"value": self_retrieval, "floor": SELF_RETRIEVAL_FLOOR,
                                            "n": len(sr_words)},
        "baseline_provenance": {
            "landed_pre_flip": 0.6395, "graded_on_live_target": 0.698,
            "NOT_USED_0.69975": "divisive-normalisation arm, NEVER SHIPPED "
                                "(reading_grounding_loop.py:526 defaults normalise='none')",
            "NOT_USED_0.7495": "the d=1024 arm, also not shipped",
            "note": "S0 is RECOMPUTED in-run at HEAD, never quoted"},
        "organs_reused": {
            "testbed": "experiments/exp_context_conditioned_near_neighbour_v1.py (imported whole: "
                       "corpus assets, items, leak controls, space build, _ctx_masked_multi)",
            "sharpening_readout": "hdlab.modern_hopfield_readout.ModernHopfieldReadout",
            "read_out": "hdlab.reading_grounding_loop.canonicalize_fast",
            "controlled_forks": ["split_pools_salted (salt='' asserted byte-identical to "
                                 "NN.split_pools, self-test S2)",
                                 "batched cosine + Hopfield (asserted equal to canonicalize_fast "
                                 "and to ModernHopfieldReadout, self-tests S3/S4)"]},
        "item_construction": item_diag, "frequency_arm_diag": fr_diag,
        "n_units": len(units), "expected_n_units": len(BETAS) + n_draws - 1,
        "cardinality_ok": len(units) >= len(BETAS),
        "compute_architecture": "sequential-CPU; thread pins set before numpy import",
        "storage_strategy": "sharded (one anchor vector per word); no_composition",
        "selftest": _SELFTEST_RESULT,
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s -- %s" % (verdict, msg), flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=("full", "smoke", "self_test"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-items", type=int, default=MAX_ITEMS)
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    if mode == "self_test":
        _atomic_write_metrics(OUT_SELFTEST, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "module-import self-test ran successfully",
            "summary": "self_test", "elapsed_s": 0.0, "run_mode": "self_test",
            "selftest": _SELFTEST_RESULT})
        return
    if mode == "smoke":
        for k in SMOKE_ITEM_SCALES:
            out = OUT_SMOKE + "_n%d" % k
            print("=== SMOKE at max_items=%d -> %s ===" % (k, out), flush=True)
            m = run("smoke", out, k)
            if m["n_items"] < 10:
                raise AssertionError("VACUOUS SMOKE at %d: %d items" % (k, m["n_items"]))
            if not m["gates"]["baseline_is_live_readout"]:
                raise AssertionError("BLOCK_DISPATCH: batched baseline forked canonicalize_fast")
            if not m["gates"]["trap_S3_identical_to_S0"]:
                raise AssertionError("BLOCK_DISPATCH: trap assertion failed")
            if not m["beta_sweep"]["entropy_gate"]["gate_passed"]:
                raise AssertionError("BLOCK_DISPATCH: entropy sweep did not span the range: %r"
                                     % m["beta_sweep"]["entropy_gate"])
            if m["positive_control_self_retrieval"]["value"] < SELF_RETRIEVAL_FLOOR:
                raise AssertionError("BLOCK_DISPATCH: SELF_RETRIEVAL %.4f < %.2f"
                                     % (m["positive_control_self_retrieval"]["value"],
                                        SELF_RETRIEVAL_FLOOR))
            a = m["arm_accuracy_2afc"]
            if not (0.05 < a["S0_ARGMAX_BASELINE"] < 0.95):
                raise AssertionError("META_RULE_AG: baseline out of band: %r"
                                     % a["S0_ARGMAX_BASELINE"])
            for k2, v in a.items():
                if v in (0.0, 1.0):
                    raise AssertionError("INSTRUMENTATION_SUSPECT: arm %s pinned at %r" % (k2, v))
            if not m["gates"]["arms_differ_verified"]:
                raise AssertionError("META_RULE_AF: %r" % m["gates"]["declared_identical_pairs"])
            if m["elapsed_s"] < 0.1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: <100ms exit at %d" % k)
            print("[smoke] n%d OK verdict=%s" % (k, m["verdict"]), flush=True)
        print("SMOKE=PASS (all scales)", flush=True)
        return
    run("full", OUT_FULL, args.max_items)


_SELFTEST_RESULT = _instrumentation_selftest()      # module scope, before any measurement

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                          # NOT BaseException
        _write_crash_metrics(OUT_SMOKE if "smoke" in sys.argv else OUT_FULL, _e)
        raise
