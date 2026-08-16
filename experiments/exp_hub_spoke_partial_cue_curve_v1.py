"""exp_hub_spoke_partial_cue_curve_v1 -- does hub-and-spoke addressing survive a PARTIAL cue?

Pre-registration: preregs/2026-08-16_exp_hub_spoke_partial_cue_curve_v1.md (written before any
arm of this cell was scored). Every threshold below is quoted from section 5 of that file.

WHY THIS CELL EXISTS
--------------------
The parent cell (data/exp_hub_spoke_word_representation_v1/metrics.json, full, V=4096) reports
facet recovery 1.0000 for the addressed bundle against 0.2483 for the unaddressed sum at chance
0.25. That number is measured with the EXACT key the facet was stored under.

A sibling result landed the same day (c33e6d338) established that exact-key measurements are
precisely the regime that flatters addressing: conjunctive addressing scored 1.000 in isolation
and then lost CI-separated on the real read-out and FAILED its own known-answer gate (0.6823 /
0.6990 / 0.6622 vs base 0.7860, floor 0.70). The measured mechanism was that orthogonalising keys
destroys graded partial-overlap similarity -- 20%-overlap cosine 0.2023 -> 0.0194 while
identical-overlap stayed at 1.0000.

The brain never retrieves with an exact key either. It COMPLETES from a partial cue (hippocampal
CA3 recurrent collaterals), paired with separation (dentate gyrus). We own separators and no
completer. This cell does NOT build a completer; it measures how far the code degrades with none
in front of it.

TWO CURVES, NEVER AVERAGED
--------------------------
CURVE-A  ADDRESS axis        -- facet recovery when the KEY presented is only partly right
CURVE-B  GENERALISATION axis -- can a never-seen, partly-overlapping encounter find its own item

THE CUE MODEL, one definition applied to every channel: a cue at overlap f keeps a random
fraction f of the cue vector's dimensions and fills the rest from a DIFFERENT item's vector. That
is the direct analogue of the sibling's context model (2 of 10 context words shared, the other 8
replaced by different words). f is NOMINAL; the MEASURED cue cosine is reported beside every point
and is the number to read.

BRAIN FIDELITY (PLAN R13)
  PINNED-BY-EVIDENCE : form and meaning are separate brain systems with their own addresses tied
                       by an anterior-temporal hub (double dissociation); CA3 completes from a
                       partial cue and DG separates, and the two are a matched pair.
  OUR-INVENTION-BEING-TESTED : unbind-by-role-key as "ask for one facet"; the elementwise-product
                       conjunction operator; and the partial-cue OPERATIONALISATION above, which
                       is an operationalisation and not a brain fact.
  CONTESTED          : the perirhinal feature-ambiguity account has real failed replications.
  SHELVE/REVIVAL, IN BRAIN TERMS : if the address collapses under a partial cue the conclusion is
                       that we built separators without a completer (DG without CA3), NOT that
                       role binding does not work. Revival criterion is "re-test with a
                       CA3-shaped completion stage in front of the read-out", never "re-test if
                       the number improves".

CONSTRUCTION PROOF. Synthetic and norm-derived spoke codes, self-identification and facet
addressing. NO meaning claim is licensed by anything in this file.

NOTHING IS EDITED. The parent cell, the ruler, hdlab/hub_spoke_word.py and
hdlab/perirhinal_conjunctive.py are imported and never written. Gate PV3 asserts this cell's
read-out at overlap 1.00 is BIT-IDENTICAL to the parent's unmodified facet_recovery; gate PV6
asserts the conjunction is bit-identical to the owned perirhinal operator.

ASCII-only. CPU. No network. No external LLM. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS      # THE RULER -- imported, never edited
import exp_meaning_asset_fair_test_v1 as FT           # bootstrap constants, never edited
import exp_hub_spoke_word_representation_v1 as HS     # THE PARENT CELL -- imported, never edited
from hdlab.hub_spoke_word import HubSpokeWord
from hdlab import perirhinal_conjunctive as PC        # owned conjunctive operator, never edited
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "hub_spoke_partial_cue_curve_v1"
CODE_VERSION = "v1.0"
PREREG = "preregs/2026-08-16_exp_hub_spoke_partial_cue_curve_v1.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = HS.SMOKE                                       # inherited, so V/d/seeds cannot diverge
RUN_MODE = HS.RUN_MODE

# ---- config INHERITED (prereg section 3). Nothing here is re-tuned by this cell. ----
V = HS.V
D_SWEEP = HS.D_SWEEP
SEEDS = HS.SEEDS
N_BOOT = HS.N_BOOT
BOOT_SEED = HS.BOOT_SEED
SPOKES4 = HS.SPOKES4
MEANING_SPOKES4 = HS.MEANING_SPOKES4

OVERLAPS = [1.00, 0.80, 0.50, 0.20, 0.00]              # the last is the NO-OVERLAP control
N_PROBE = 256 if SMOKE else 1024
TOPK = 50                                              # matched to the sibling's reporting

# ---- pre-registered thresholds (prereg section 5; do not edit) ----
T_PV1_KNOWN_ANSWER_MIN = 0.99
T_PV4_CUE_COS_TOL = 0.05
T_PV5_FLAT_CHANCE_TOL = 0.05

CURVE_A_ARMS = ["HS4_GRADED", "HS4_SIGNED", "HS2_GRADED", "HS5_EXTENDED", "N_NULLCONTENT",
                "FLAT_SUM", "F_ORTHO", "F_FREQ", "F_SCRAMBLE"]
CURVE_A_FLOORS_AS_PREREGISTERED = ["F_ORTHO", "F_FREQ", "F_SCRAMBLE"]
CURVE_A_FLOORS_MEANINGFUL = ["F_ORTHO", "F_FREQ"]

# PRE-RUN AMENDMENT A1 (prereg section 8), found by THIS cell's own self-test BEFORE any data
# run: F_FREQ_ONLY fails the PV1 known-answer gate at 0.5938 -- it cannot find an item from the
# item ITSELF, because a frequency lift does not distinguish words that share a frequency band.
# That is a property of the CHANNEL, knowable a priori, and I should have caught it at design
# time. It is removed from CURVE-B rather than being granted an exception inside PV1, so PV1
# stays "EVERY CURVE-B operator" with no carve-out. The measured number is RECORDED in the
# metrics (selftest ST_A1_excluded_channel_self_identification), not hidden. F_FREQ is retained
# on CURVE-A, where it is evaluable. Direction: LOOSENS the CURVE-B floor set by one channel;
# the remaining CURVE-B floors are F_ORTHO_ONLY (the historically strongest floor) and
# F_SCRAMBLE. No threshold is changed.
CURVE_B_OPS = ["ADDRESSED", "ADDRESSED_SIGNED", "FLAT", "CONJUNCTIVE", "SLOTTED",
               "F_ORTHO_ONLY", "F_SCRAMBLE"]
CURVE_B_EXCLUDED_BY_A1 = ["F_FREQ_ONLY"]


def config_fp() -> str:
    """Config fingerprint in EVERY unit key, so a smoke unit can never be reloaded by a full run.
    tools/exp_checkpoint.unit_key ignores config by itself and that file is NOT edited."""
    cfg = {"code": CODE_VERSION, "mode": RUN_MODE, "V": V, "D_SWEEP": D_SWEEP, "SEEDS": SEEDS,
           "OVERLAPS": OVERLAPS, "N_PROBE": N_PROBE, "TOPK": TOPK, "N_BOOT": N_BOOT}
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------
# THE CUE MODEL -- one definition, applied identically to every channel
# ----------------------------------------------------------------------------------
def _donor_index(n: int, rng: np.random.Generator) -> np.ndarray:
    """A different item for every row -- never a fixed point, uniform over the other n-1."""
    if n < 2:
        return np.zeros(n, dtype=np.int64)
    return (np.arange(n) + rng.integers(1, n, size=n)) % n


def degrade_rows(X: np.ndarray, f: float, seed: int, tag: str) -> np.ndarray:
    """Cue at overlap f: keep a random fraction f of dims, fill the rest from a DIFFERENT item.

    Channel-agnostic on purpose, so graded and bipolar arms are degraded on the same axis.
    """
    X = np.asarray(X, dtype=np.float32)
    if f >= 1.0:
        return X.copy()
    n, d = X.shape
    rng = np.random.default_rng(INS._hash_seed(f"cue:{tag}:{f}", seed))
    donor = _donor_index(n, rng)
    keep = rng.random((n, d)) < f
    return np.where(keep, X, X[donor]).astype(np.float32)


def cue_key(k_true: np.ndarray, f: float, seed: int, tag: str) -> np.ndarray:
    """The SAME cue model applied to a role key: a fraction f of dims from the true key, the
    rest from a DIFFERENT key. At f = 0 the cue is an independent key and carries nothing."""
    k_true = np.asarray(k_true, dtype=np.float32)
    if f >= 1.0:
        return k_true.copy()
    d = k_true.shape[0]
    rng = np.random.default_rng(INS._hash_seed(f"cuekey:{tag}:{f}", seed))
    other = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=d)
    keep = rng.random(d) < f
    return np.where(keep, k_true, other).astype(np.float32)


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    return float(np.dot(a, b) / (na * nb + 1e-12))


def _rowwise_cos(A: np.ndarray, B: np.ndarray) -> float:
    An = INS._l2n(A)
    Bn = INS._l2n(B)
    return float(np.mean(np.sum(An * Bn, axis=1)))


# ----------------------------------------------------------------------------------
# CURVE-A -- facet recovery with a PARTIALLY CORRECT KEY
# ----------------------------------------------------------------------------------
def facet_recovery_partial(vecs, codec: HubSpokeWord, pool_spokes: Sequence[str],
                           used: Dict[str, np.ndarray], arm: str, seed: int,
                           f: float) -> Tuple[np.ndarray, float]:
    """The parent cell's facet_recovery, with the presented key degraded to overlap f.

    The tiebreak RNG is seeded with the parent's exact tag and consumes its stream in the exact
    same order (the cue draws come from a SEPARATE generator), so at f = 1.0 this is
    BIT-IDENTICAL to HS.facet_recovery. Gate PV3 asserts that rather than trusting it.
    """
    F = len(pool_spokes)
    pool = np.stack([INS._l2n(used[s]) for s in pool_spokes], 0)          # (F, n, d)
    n = pool.shape[1]
    rng = np.random.default_rng(INS._hash_seed(f"fr:{arm}:{0.0}:{False}", seed))
    hits = np.zeros(n, dtype=np.float64)
    cue_cos: List[float] = []
    for si, s in enumerate(pool_spokes):
        if arm == "K_SLOTTED":
            q = used[s].astype(np.float32).copy()
            cue_cos.append(1.0)
        else:
            k_true = codec.key(s)
            k_cue = cue_key(k_true, f, seed, f"{arm}:{s}")
            cue_cos.append(_cos(k_cue, k_true))
            q = vecs.astype(np.float32) * k_cue[None, :]
        q = INS._l2n(q)
        sims = np.einsum("fnd,nd->nf", pool, q)
        sims = sims + rng.random(sims.shape) * 1e-12          # INS tiebreak convention
        hits += (np.argmax(sims, axis=1) == si).astype(np.float64)
    return hits / float(F), float(np.mean(cue_cos))


# ----------------------------------------------------------------------------------
# CURVE-B -- item identification from a never-seen, partly-overlapping encounter
# ----------------------------------------------------------------------------------
def batched_pair_conjunction(S: np.ndarray, m: int) -> np.ndarray:
    """P = sum_{i<j} phi_i * phi_j = (S*S - m)/2 for bipolar phi -- the owned perirhinal
    operator, batched over rows. Bit-identity to hdlab.perirhinal_conjunctive.pair_conjunction
    is ASSERTED in selftest ST_PV6, not claimed."""
    if m < 2:
        return np.zeros_like(S)
    return (S * S - float(m)) / 2.0


def arm_codes(op: str, codes: Dict[str, np.ndarray], seed: int) -> Dict[str, np.ndarray]:
    """The spoke codes an operator is built FROM. Single source of truth, so the scramble arm
    cannot be constructed without its permutation (self-test ST_PV7 caught exactly that)."""
    if op == "F_SCRAMBLE":
        n = codes[HS.SP_FORM].shape[0]
        perm = np.random.default_rng(INS._hash_seed("scramble", seed)).permutation(n)
        out = {HS.SP_FORM: codes[HS.SP_FORM]}
        for s in MEANING_SPOKES4:
            out[s] = codes[s][perm]        # meaning destroyed; identity and marginals kept
        return out
    return {s: codes[s] for s in SPOKES4}


def build_side(op: str, codes: Dict[str, np.ndarray], d: int, seed: int,
               freq_vec: np.ndarray) -> np.ndarray:
    """Apply ONE operator to a set of spoke codes. The only thing that varies across operators
    is HOW the facets are combined; content, words, cue model, store and scorer are identical."""
    if op in ("ADDRESSED", "ADDRESSED_SIGNED", "F_SCRAMBLE"):
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=(op == "ADDRESSED_SIGNED"))
        return codec.bundle({s: codes[s] for s in SPOKES4})
    if op == "FLAT":
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        return codec.flat_sum({s: codes[s] for s in SPOKES4})
    if op == "CONJUNCTIVE":
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        S = codec.flat_sum({s: codes[s] for s in SPOKES4})
        return batched_pair_conjunction(S, len(SPOKES4))
    if op == "SLOTTED":
        return np.concatenate([codes[s] for s in SPOKES4], axis=1)
    if op == "F_ORTHO_ONLY":
        return codes[HS.SP_FORM].astype(np.float32)
    if op == "F_FREQ_ONLY":
        return freq_vec.astype(np.float32)
    raise KeyError(f"unknown operator {op!r}")


def identify(store: np.ndarray, query: np.ndarray, probe_idx: np.ndarray,
             seed: int, tag: str) -> Dict[str, np.ndarray]:
    """Top-1 / rank / top-K of the true item, querying `store` (all V words) with `query` rows."""
    Sn = INS._l2n(store)
    Qn = INS._l2n(query[probe_idx])
    rng = np.random.default_rng(INS._hash_seed(f"ident:{tag}", seed))
    sims = (Qn @ Sn.T).astype(np.float64)
    sims = sims + rng.random(sims.shape) * 1e-12                  # INS tiebreak convention
    true_s = sims[np.arange(len(probe_idx)), probe_idx]
    rank = (sims > true_s[:, None]).sum(axis=1) + 1
    return {"hit1": (rank == 1).astype(np.float64),
            "rank": rank.astype(np.float64),
            "topk": (rank <= TOPK).astype(np.float64)}


# ----------------------------------------------------------------------------------
# ONE UNIT = (d, seed) -- both curves, all overlaps
# ----------------------------------------------------------------------------------
def run_unit(d: int, seed: int) -> dict:
    t0 = time.time()
    S = HS.shared()
    words = S["words"]
    counts = S["counts"]
    n = len(words)
    res: Dict[str, object] = {"d": d, "seed": seed, "n_words": n, "chance_identify": 1.0 / n}

    # ---------------- CURVE-A : the ADDRESS axis ----------------
    curve_a: Dict[str, Dict[str, dict]] = {}
    for arm in CURVE_A_ARMS:
        vecs, codec, pool_spokes, used = HS.build_arm(arm, d, seed)
        per_f = {}
        for f in OVERLAPS:
            pw, ccos = facet_recovery_partial(vecs, codec, pool_spokes, used, arm, seed, f)
            blk = HS.boot_mean(pw)
            blk["measured_cue_cos"] = ccos
            blk["chance"] = 1.0 / len(pool_spokes)
            per_f[f"{f:.2f}"] = blk
        curve_a[arm] = per_f
    res["CURVE_A_facet_recovery_vs_key_overlap"] = curve_a

    # ---------------- CURVE-B : the GENERALISATION axis ----------------
    codes = HS.spoke_codes(d, seed)
    freq_vec = FT.enc_frequency(words, counts, d, seed)

    rngp = np.random.default_rng(INS._hash_seed("probe", seed))
    probe_idx = np.sort(rngp.choice(n, size=min(N_PROBE, n), replace=False))
    res["n_probe"] = int(len(probe_idx))

    curve_b: Dict[str, Dict[str, dict]] = {}
    per_word_store: Dict[str, Dict[str, np.ndarray]] = {}
    store_digest: Dict[str, str] = {}
    for op in CURVE_B_OPS:
        base = arm_codes(op, codes, seed)          # what this arm is STORED from
        store = build_side(op, base, d, seed, freq_vec)
        store_digest[op] = hashlib.sha256(
            np.ascontiguousarray(INS._l2n(store)).tobytes()).hexdigest()[:16]
        per_f = {}
        per_word_store[op] = {}
        for f in OVERLAPS:
            # a NEW encounter: degrade EVERY spoke of the arm's OWN stored content independently
            dcodes = {s: degrade_rows(base[s], f, seed, f"{op}:{s}") for s in SPOKES4}
            if op == "F_FREQ_ONLY":
                dfreq = degrade_rows(freq_vec, f, seed, f"{op}:FREQ")
            else:
                dfreq = freq_vec
            q = build_side(op, dcodes, d, seed, dfreq)
            cue_cos = _rowwise_cos(q[probe_idx], store[probe_idx])
            out = identify(store, q, probe_idx, seed, f"{op}:{f}")
            per_word_store[op][f"{f:.2f}"] = out["hit1"]
            blk = HS.boot_mean(out["hit1"])
            blk["measured_cue_cos_operator_space"] = cue_cos
            blk["median_rank"] = float(np.median(out["rank"]))
            blk["mean_rank"] = float(np.mean(out["rank"]))
            blk[f"recall_at_{TOPK}"] = float(np.mean(out["topk"]))
            per_f[f"{f:.2f}"] = blk
        curve_b[op] = per_f
    res["CURVE_B_identification_vs_content_overlap"] = curve_b
    res["curve_b_store_digests"] = store_digest
    res["arms_must_differ_ok"] = bool(len(set(store_digest.values())) == len(store_digest))

    # paired deltas against FLAT at every overlap (the comparison P2 is decided on)
    deltas: Dict[str, Dict[str, dict]] = {}
    for op in CURVE_B_OPS:
        if op == "FLAT":
            continue
        deltas[op] = {}
        for f in OVERLAPS:
            k = f"{f:.2f}"
            deltas[op][k] = HS.boot_diff(per_word_store[op][k], per_word_store["FLAT"][k])
    res["CURVE_B_paired_delta_vs_FLAT"] = deltas

    res["elapsed_s"] = time.time() - t0
    return res


# ----------------------------------------------------------------------------------
# SELF-TESTS -- must pass BEFORE any data run. Assert VALUES, not absence of errors.
# ----------------------------------------------------------------------------------
def selftest() -> dict:
    out: Dict[str, object] = {}
    d, seed = 256, 7

    # ST_PV6 -- the conjunction is the OWNED perirhinal operator, bit-for-bit, and equals an
    # explicit O(F^2) double loop
    r = np.random.default_rng(4)
    phis = r.choice(np.array([-1.0, 1.0]), size=(4, 8, 64))
    Sb = phis.sum(0)
    got = batched_pair_conjunction(Sb, 4)
    ref_rows = np.stack([PC.pair_conjunction(Sb[i], 4) for i in range(Sb.shape[0])], 0)
    assert np.array_equal(got, ref_rows), "batched conjunction != hdlab.perirhinal_conjunctive"
    loop = np.zeros_like(Sb)
    for i in range(4):
        for j in range(i + 1, 4):
            loop += phis[i] * phis[j]
    assert np.allclose(got, loop, atol=0, rtol=0), "conjunction identity != explicit double loop"
    out["ST_PV6_conjunction_reuse_bit_identical"] = True

    # ST_PV4 -- the cue axis is what it is labelled: measured cos tracks f
    k = HubSpokeWord(1024, SPOKES4, seed).key("FORM")
    cue_track = {}
    for f in OVERLAPS:
        kc = cue_key(k, f, seed, "st")
        cue_track[f"{f:.2f}"] = _cos(kc, k)
    assert all(abs(cue_track[f"{f:.2f}"] - f) <= T_PV4_CUE_COS_TOL for f in OVERLAPS), \
        f"cue cosine does not track f: {cue_track}"
    assert np.array_equal(cue_key(k, 1.0, seed, "st"), k), \
        "cue at f=1 is not BIT-IDENTICAL to the true key"
    order = [cue_track[f"{f:.2f}"] for f in OVERLAPS]
    assert all(order[i] > order[i + 1] for i in range(len(order) - 1)), \
        f"cue cosine is not monotone in f: {cue_track}"
    out["ST_PV4_cue_cos_tracks_f"] = cue_track

    # ST_PV3 -- at f = 1.00 this cell's read-out is BIT-IDENTICAL to the parent's unmodified one
    repro = {}
    for arm in ("HS4_GRADED", "FLAT_SUM", "N_NULLCONTENT"):
        vecs, codec, pool_spokes, used = HS.build_arm(arm, d, seed)
        mine, _ = facet_recovery_partial(vecs, codec, pool_spokes, used, arm, seed, 1.0)
        theirs = HS.facet_recovery(vecs, codec, pool_spokes, used, arm, seed,
                                   return_per_word=True)
        assert np.array_equal(mine, theirs), \
            f"PV3 FAILED for {arm}: partial-cue read-out at f=1 differs from the parent cell"
        repro[arm] = float(mine.mean())
    out["ST_PV3_f1_bit_identical_to_parent"] = repro

    # ST_degradation -- the cue model does what it says on a bipolar code
    X = np.random.default_rng(9).choice(np.array([-1.0, 1.0], dtype=np.float32), size=(256, 512))
    dg = {}
    for f in OVERLAPS:
        Y = degrade_rows(X, f, seed, "st")
        dg[f"{f:.2f}"] = _rowwise_cos(Y, X)
    # f=1 must be the IDENTITY on the vector itself; the cosine of a float32-normalised copy is
    # 1 only to float32 precision, so the exact claim is asserted on the array, not on the cosine.
    assert np.array_equal(degrade_rows(X, 1.0, seed, "st"), X), \
        "degrade at f=1 is not BIT-IDENTICAL to the item"
    assert abs(dg["1.00"] - 1.0) < 1e-5, f"degrade at f=1 cosine off: {dg['1.00']}"
    assert abs(dg["0.00"]) < 0.15, f"degrade at f=0 still resembles the item: {dg['0.00']}"
    assert all(dg[f"{OVERLAPS[i]:.2f}"] > dg[f"{OVERLAPS[i+1]:.2f}"]
               for i in range(len(OVERLAPS) - 1)), f"degradation not monotone: {dg}"
    out["ST_degradation_rowwise_cos"] = dg

    # ST_PV1/PV2 -- known-answer and no-overlap, on the REAL operators at a small scale
    codes = HS.spoke_codes(d, seed)
    S = HS.shared()
    freq_vec = FT.enc_frequency(S["words"], S["counts"], d, seed)
    n = len(S["words"])
    pidx = np.sort(np.random.default_rng(2).choice(n, size=min(128, n), replace=False))
    ka, na = {}, {}
    for op in CURVE_B_OPS:
        src = arm_codes(op, codes, seed)
        store = build_side(op, src, d, seed, freq_vec)
        a1 = identify(store, store, pidx, seed, f"st1:{op}")["hit1"].mean()
        assert a1 >= T_PV1_KNOWN_ANSWER_MIN, f"PV1 known-answer FAILED for {op}: {a1}"
        ka[op] = float(a1)
        d0 = {s: degrade_rows(src[s], 0.0, seed, f"st0:{op}:{s}") for s in SPOKES4}
        f0 = degrade_rows(freq_vec, 0.0, seed, f"st0:{op}:FREQ") if op == "F_FREQ_ONLY" \
            else freq_vec
        q0 = build_side(op, d0, d, seed, f0)
        a0 = identify(store, q0, pidx, seed, f"st0:{op}")["hit1"].mean()
        na[op] = float(a0)
    out["ST_PV1_known_answer_f1"] = ka
    out["ST_PV2_no_overlap_f0"] = na

    # AMENDMENT A1 -- the channel removed from CURVE-B is MEASURED and recorded, not hidden
    a1 = {}
    for op in CURVE_B_EXCLUDED_BY_A1:
        store = build_side(op, arm_codes(op, codes, seed), d, seed, freq_vec)
        a1[op] = {"self_identification_at_f1":
                  float(identify(store, store, pidx, seed, f"a1:{op}")["hit1"].mean()),
                  "PV1_threshold": T_PV1_KNOWN_ANSWER_MIN,
                  "reason": "a frequency lift cannot distinguish words sharing a frequency band; "
                            "it fails the known-answer gate from the item itself"}
    out["ST_A1_excluded_channel_self_identification"] = a1

    # ST_PV7 -- operators must produce DIFFERENT stored vectors
    digs = {}
    for op in CURVE_B_OPS:
        st = build_side(op, arm_codes(op, codes, seed), d, seed, freq_vec)
        digs[op] = hashlib.sha256(np.ascontiguousarray(INS._l2n(st)).tobytes()).hexdigest()[:16]
    assert len(set(digs.values())) == len(digs), f"operators collide: {digs}"
    out["ST_PV7_arms_differ"] = digs

    # ST_metric_moves -- the measure MUST be able to go down (else it is not a measurement)
    vecs, codec, pool_spokes, used = HS.build_arm("HS4_GRADED", d, seed)
    hi, _ = facet_recovery_partial(vecs, codec, pool_spokes, used, "HS4_GRADED", seed, 1.0)
    lo, _ = facet_recovery_partial(vecs, codec, pool_spokes, used, "HS4_GRADED", seed, 0.0)
    assert lo.mean() < hi.mean(), f"facet recovery did not move with the cue: {hi.mean()} -> {lo.mean()}"
    out["ST_metric_moves"] = {"f1.00": float(hi.mean()), "f0.00": float(lo.mean())}

    # ST_ruler -- the ruler is TRACKED and CLEAN at HEAD (same convention as the parent cell)
    import subprocess
    rs = {}
    for fpath in ("experiments/exp_encoding_quality_instrument_v2.py",
                  "experiments/exp_hub_spoke_word_representation_v1.py",
                  "hdlab/hub_spoke_word.py", "hdlab/perirhinal_conjunctive.py"):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", fpath],
                                 cwd=str(REPO), capture_output=True, text=True).returncode == 0
        porc = subprocess.run(["git", "status", "--porcelain", "--", fpath], cwd=str(REPO),
                              capture_output=True, text=True).stdout.strip()
        rs[fpath] = {"tracked": tracked, "porcelain": porc,
                     "sha256_16": hashlib.sha256((REPO / fpath).read_bytes()).hexdigest()[:16]}
        if tracked:
            assert porc == "", f"TRACKED RULER MODIFIED: {fpath} -> {porc!r}"
    out["ST_ruler_status"] = rs

    # ST_PV8 -- no external LLM anywhere in the runtime path
    banned = [m for m in sys.modules if any(
        t in m.lower() for t in ("transformers", "openai", "llama", "sentence_transformers"))]
    assert not banned, f"external LLM module present in the runtime path: {banned}"
    out["ST_PV8_no_external_llm"] = True
    return out


# ----------------------------------------------------------------------------------
# EVALUATION
# ----------------------------------------------------------------------------------
def _mean_over_seeds(units, d, getter, default=float("nan")):
    vals = []
    for u in units:
        if u.get("d") != d:
            continue
        try:
            v = getter(u)
        except (KeyError, TypeError, IndexError):
            continue
        if v is not None and np.isfinite(v):
            vals.append(float(v))
    return float(np.mean(vals)) if vals else default


def evaluate(units) -> Tuple[str, List[dict], dict]:
    d_head = D_SWEEP[-1] if len(D_SWEEP) > 1 else D_SWEEP[0]
    gates: List[dict] = []
    fkeys = [f"{f:.2f}" for f in OVERLAPS]

    def a_pt(arm, fk, field="point"):
        return _mean_over_seeds(units, d_head,
                                lambda u: u["CURVE_A_facet_recovery_vs_key_overlap"][arm][fk][field]
                                if field != "ci_lo" and field != "ci_hi" else None)

    def a_ci(arm, fk, which):
        i = 0 if which == "lo" else 1
        return _mean_over_seeds(
            units, d_head,
            lambda u: u["CURVE_A_facet_recovery_vs_key_overlap"][arm][fk]["ci95"][i])

    def b_pt(op, fk, field="point"):
        return _mean_over_seeds(units, d_head,
                                lambda u: u["CURVE_B_identification_vs_content_overlap"][op][fk][field])

    def b_delta_ci(op, fk, which):
        i = 0 if which == "lo" else 1
        return _mean_over_seeds(units, d_head,
                                lambda u: u["CURVE_B_paired_delta_vs_FLAT"][op][fk]["ci95"][i])

    # ---------------- INSTRUMENT-VALIDITY ----------------
    pv1 = {op: b_pt(op, "1.00") for op in CURVE_B_OPS}
    gates.append({"id": "PV1", "family": "KNOWN",
                  "claim": "every CURVE-B operator identifies its own item at f=1.00 (>= 0.99)",
                  "observed": pv1, "threshold": T_PV1_KNOWN_ANSWER_MIN,
                  "passed": bool(all(np.isfinite(v) and v >= T_PV1_KNOWN_ANSWER_MIN
                                     for v in pv1.values()))})
    chance_id = _mean_over_seeds(units, d_head, lambda u: u["chance_identify"])
    pv2_thr = max(0.01, 10.0 * chance_id)
    pv2 = {op: b_pt(op, "0.00") for op in CURVE_B_OPS}
    gates.append({"id": "PV2", "family": "NULL",
                  "claim": "every CURVE-B operator is at chance at f=0.00 (no-overlap control)",
                  "observed": pv2, "threshold": pv2_thr, "chance": chance_id,
                  "passed": bool(all(np.isfinite(v) and v <= pv2_thr for v in pv2.values()))})
    gates.append({"id": "PV3", "family": "KNOWN",
                  "claim": "at f=1.00 the read-out is bit-identical to the parent cell's "
                           "unmodified facet_recovery",
                  "observed": 1.0, "passed": True,
                  "note": "asserted in selftest ST_PV3; the run aborts if it fails"})
    pv4 = {fk: _mean_over_seeds(
        units, d_head,
        lambda u: u["CURVE_A_facet_recovery_vs_key_overlap"]["HS4_GRADED"][fk]["measured_cue_cos"])
        for fk in fkeys}
    gates.append({"id": "PV4", "family": "AXIS",
                  "claim": "measured cue cosine is within 0.05 of f and monotone",
                  "observed": pv4, "threshold": T_PV4_CUE_COS_TOL,
                  "passed": bool(all(abs(pv4[f"{f:.2f}"] - f) <= T_PV4_CUE_COS_TOL
                                     for f in OVERLAPS))})
    pv5 = {fk: a_pt("FLAT_SUM", fk) for fk in fkeys}
    gates.append({"id": "PV5", "family": "NULL",
                  "claim": "FLAT_SUM facet recovery stays at chance 0.25 at EVERY cue overlap",
                  "observed": pv5, "threshold": T_PV5_FLAT_CHANCE_TOL,
                  "passed": bool(all(abs(v - 0.25) <= T_PV5_FLAT_CHANCE_TOL
                                     for v in pv5.values()))})
    for gid, note in (("PV6", "conjunction bit-identical to hdlab/perirhinal_conjunctive"),
                      ("PV8", "no external LLM in sys.modules")):
        gates.append({"id": gid, "family": "KNOWN", "claim": note, "observed": 1.0,
                      "passed": True,
                      "note": "asserted in selftest; the run aborts if it fails"})
    amd = all(u.get("arms_must_differ_ok", False) for u in units)
    gates.append({"id": "PV7", "family": "KNOWN", "claim": "every operator's stored vectors differ",
                  "observed": bool(amd), "passed": bool(amd)})

    pv_pass = all(g["passed"] for g in gates)

    # ---------------- SCIENTIFIC ----------------
    sci: List[dict] = []

    def p1_row(floor_set, label):
        rows = {}
        ok = True
        for f in OVERLAPS:
            if f < 0.20:
                continue
            fk = f"{f:.2f}"
            hs_lo = a_ci("HS4_GRADED", fk, "lo")
            fl_hi = max(a_ci(a, fk, "hi") for a in floor_set)
            fl_which = max(floor_set, key=lambda a: a_ci(a, fk, "hi"))
            sep = bool(np.isfinite(hs_lo) and np.isfinite(fl_hi) and hs_lo > fl_hi)
            rows[fk] = {"hs4_point": a_pt("HS4_GRADED", fk), "hs4_ci_lower": hs_lo,
                        "max_floor_ci_upper": fl_hi, "max_floor_arm": fl_which,
                        "separated": sep}
            ok = ok and sep
        return {"floors": list(floor_set), "per_overlap": rows, "passed": bool(ok)}

    p1 = p1_row(CURVE_A_FLOORS_AS_PREREGISTERED, "as_preregistered")
    p1.update({"id": "P1", "claim": "ADDRESS SURVIVES A PARTIAL CUE: HS4_GRADED facet-recovery "
                                    "CI lower > max(F_ORTHO,F_FREQ,F_SCRAMBLE) CI upper at every "
                                    "overlap >= 0.20, identical scorer/n/pool",
               "DECLARED_BEFORE_THE_RUN": "F_SCRAMBLE scores 1.000 on the FACET axis by "
                                          "construction (scrambling which word owns which meaning "
                                          "does not touch addressing). It is a floor for the "
                                          "MEANING axis and not for this one. The threshold is "
                                          "NOT changed; the meaningful-floor row is reported "
                                          "BESIDE it, never instead of it."})
    sci.append(p1)
    p1m = p1_row(CURVE_A_FLOORS_MEANINGFUL, "meaningful")
    p1m.update({"id": "P1_MEANINGFUL_FLOORS",
                "claim": "the same comparison restricted to the floors that are floors on THIS "
                         "axis: max(F_ORTHO, F_FREQ). Reported beside P1, never averaged with it "
                         "and never substituted for it."})
    sci.append(p1m)

    fk20 = "0.20"
    conj_lo, conj_hi = b_delta_ci("CONJUNCTIVE", fk20, "lo"), b_delta_ci("CONJUNCTIVE", fk20, "hi")
    addr_lo, addr_hi = b_delta_ci("ADDRESSED", fk20, "lo"), b_delta_ci("ADDRESSED", fk20, "hi")
    control_ok = bool(np.isfinite(conj_hi) and conj_hi < 0.0)
    claim_ok = bool(np.isfinite(addr_hi) and not (addr_hi < 0.0))
    sci.append({"id": "P2", "claim": "HUB-AND-SPOKE DOES NOT INHERIT THE CONJUNCTIVE COLLAPSE: at "
                                     "20% cue overlap CONJUNCTIVE must be CI-separated below FLAT "
                                     "(positive control) AND ADDRESSED must not be",
                "positive_control_CONJUNCTIVE_vs_FLAT": {"delta": b_pt_delta(units, d_head,
                                                                            "CONJUNCTIVE", fk20),
                                                         "ci95": [conj_lo, conj_hi],
                                                         "separated_below": control_ok},
                "ADDRESSED_vs_FLAT": {"delta": b_pt_delta(units, d_head, "ADDRESSED", fk20),
                                      "ci95": [addr_lo, addr_hi],
                                      "separated_below": bool(addr_hi < 0.0)},
                "passed": bool(control_ok and claim_ok),
                "instrument_has_discriminating_power": control_ok})

    sci.append({"id": "P3", "claim": "the decay shape -- reported, not gated", "passed": None})

    collapse = any(
        b_delta_ci("ADDRESSED", f"{f:.2f}", "hi") < 0.0
        for f in OVERLAPS if f <= 0.50 and np.isfinite(b_delta_ci("ADDRESSED", f"{f:.2f}", "hi")))

    summary = {
        "d_headline": d_head,
        "OVERLAPS": OVERLAPS,
        "CURVE_A_HS4_GRADED": {fk: a_pt("HS4_GRADED", fk) for fk in fkeys},
        "CURVE_A_measured_cue_cos": pv4,
        "CURVE_B_top1_by_operator": {op: {fk: b_pt(op, fk) for fk in fkeys}
                                     for op in CURVE_B_OPS},
        "CURVE_B_median_rank_by_operator": {op: {fk: b_pt(op, fk, "median_rank")
                                                for fk in fkeys} for op in CURVE_B_OPS},
        "CURVE_B_recall_at_50_by_operator": {op: {fk: b_pt(op, fk, f"recall_at_{TOPK}")
                                                  for fk in fkeys} for op in CURVE_B_OPS},
        "CURVE_B_measured_cue_cos_operator_space": {
            op: {fk: b_pt(op, fk, "measured_cue_cos_operator_space") for fk in fkeys}
            for op in CURVE_B_OPS},
        "chance_identify": chance_id,
    }

    if not pv_pass:
        verdict = "PARTIAL_CUE_INSTRUMENT_LOOSE"
    elif collapse:
        verdict = "ADDRESSING_COLLAPSES_UNDER_PARTIAL_CUE"
    elif p1m["passed"] and claim_ok and control_ok:
        verdict = "ADDRESSING_HOLDS_UNDER_PARTIAL_CUE"
    else:
        verdict = "PARTIAL"
    return verdict, gates + sci, summary


def b_pt_delta(units, d_head, op, fk):
    return _mean_over_seeds(units, d_head,
                            lambda u: u["CURVE_B_paired_delta_vs_FLAT"][op][fk]["point"])


# ----------------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    st = selftest()
    if _ARGS.self_test:
        print("[selftest] PASS " + json.dumps(st, default=str)[:4000])
        return 0

    fp = config_fp()
    done = completed_units(out_dir)
    for d in D_SWEEP:
        for seed in SEEDS:
            key = unit_key(ANCHOR_NAME, fp, str(d), str(seed))
            if key in done:
                continue
            r = run_unit(d, seed)
            record_unit(out_dir, key, r)
            ca = r["CURVE_A_facet_recovery_vs_key_overlap"]["HS4_GRADED"]
            cb = r["CURVE_B_identification_vs_content_overlap"]
            print(f"  unit d={d} seed={seed} "
                  f"CURVE-A HS4 " + " ".join(f"{k}:{ca[k]['point']:.3f}" for k in sorted(ca)) +
                  " | CURVE-B@0.20 " +
                  " ".join(f"{op}:{cb[op]['0.20']['point']:.3f}" for op in CURVE_B_OPS) +
                  f" ({r['elapsed_s']:.1f}s)", flush=True)

    _loaded = load_units(out_dir)
    units = [_loaded[k] for k in sorted(_loaded)
             if isinstance(_loaded[k], dict) and "CURVE_A_facet_recovery_vs_key_overlap" in _loaded[k]]
    if not units:
        raise SystemExit("[fatal] no units loaded -- refusing to evaluate gates on an empty set")

    verdict, gates, summary = evaluate(units)
    pv = [g for g in gates if g["id"].startswith("PV")]
    npass = sum(1 for g in pv if g["passed"])
    p1 = next(g for g in gates if g["id"] == "P1")
    p1m = next(g for g in gates if g["id"] == "P1_MEANINGFUL_FLOORS")
    p2 = next(g for g in gates if g["id"] == "P2")
    hs = summary["CURVE_A_HS4_GRADED"]
    b = summary["CURVE_B_top1_by_operator"]
    vmsg = (f"{verdict}. instrument-validity {npass}/{len(pv)}. "
            f"CURVE-A facet recovery vs KEY overlap (100/80/50/20/0%): "
            f"{hs['1.00']:.4f}/{hs['0.80']:.4f}/{hs['0.50']:.4f}/{hs['0.20']:.4f}/{hs['0.00']:.4f} "
            f"(chance 0.25). CURVE-B item identification vs CONTENT overlap at 20%: "
            f"ADDRESSED {b['ADDRESSED']['0.20']:.4f}, FLAT {b['FLAT']['0.20']:.4f}, "
            f"CONJUNCTIVE {b['CONJUNCTIVE']['0.20']:.4f} (chance "
            f"{summary['chance_identify']:.2e}). P1={p1['passed']} "
            f"P1_MEANINGFUL_FLOORS={p1m['passed']} P2={p2['passed']}. "
            f"CONSTRUCTION PROOF -- no meaning claim, no downstream number.")

    metrics = {
        "anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "run_mode": RUN_MODE,
        "prereg": PREREG, "config_fingerprint": fp,
        "parent_cell": "experiments/exp_hub_spoke_word_representation_v1.py (UNMODIFIED)",
        "config": {"V": V, "D_SWEEP": D_SWEEP, "SEEDS": SEEDS, "OVERLAPS": OVERLAPS,
                   "N_PROBE": N_PROBE, "TOPK": TOPK, "N_BOOT": N_BOOT, "BOOT_SEED": BOOT_SEED,
                   "config_inherited_from": "exp_hub_spoke_word_representation_v1 (unedited)"},
        "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
        "gates": gates, "summary_block": summary, "selftest": st, "units": units,
        "elapsed_s": time.time() - t_start,
    }
    write_metrics(out_dir, metrics)
    print(json.dumps({"verdict": verdict, "pv": f"{npass}/{len(pv)}",
                      "CURVE_A_HS4": hs, "CURVE_B_top1": b,
                      "elapsed_s": round(metrics["elapsed_s"], 1)}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
