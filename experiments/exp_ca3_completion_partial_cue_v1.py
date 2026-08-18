"""exp_ca3_completion_partial_cue_v1 -- does a CA3 completer rescue an addressed store under a
PARTIAL cue?

Pre-registration: preregs/2026-08-16_exp_ca3_completion_partial_cue_v1.md, written BEFORE any arm
of this cell was scored. Every threshold below is quoted from section 5 of that file, including
its three pre-run amendments A1/A2/A3, all of which were raised by the ORGAN'S OWN SELF-TESTS
before this cell existed.

WHY THIS CELL EXISTS
--------------------
Conjunctive addressing failed on the real read-out and failed its own known-answer gate. The
measured mechanism was that isolation retrieves with the EXACT stored key -- where orthogonalising
keys is pure upside -- while real reading retrieves from a NEVER-SEEN, PARTIALLY-OVERLAPPING
context, where the same orthogonality destroys the only channel carrying signal. Shelving that on
"exact-key retrieval only" was performance-engineering wearing a research label: THE BRAIN NEVER
RETRIEVES WITH AN EXACT KEY. It COMPLETES FROM A PARTIAL CUE.

We own separators (dentate gyrus) and had no completer in front of any read-out. Separation and
completion are a MATCHED PAIR. This cell builds the missing half -- default-OFF -- and measures
retrieval as a CURVE OVER CUE OVERLAP.

  (a) A_FLAT              flat bag, no completion
  (b) B_ADDRESSED         addressed, no completion
  (c) C_ADDRESSED_CA3     addressed WITH completion   <- the brain-paired treatment
  (d) D_CA3_ONLY          completion alone, no addressing

PREDICTION TO FALSIFY: (b) degrades as overlap drops while (c) holds. IF (c) DOES NOT HOLD, THE
PAIRING HYPOTHESIS IS REFUTED AND THIS CELL SAYS SO PLAINLY.

(b) and (c) share a store, share content, share the scorer and share the cue. They differ in
EXACTLY ONE THING: whether a completer sits in front of the read-out.

WHAT THE PRIOR NEGATIVES DO AND DO NOT COVER
--------------------------------------------
notes/PLAN.md line 251 recommends against building CA3 completion, on three cells. Verified on
disk: `exp_att1_iterative_attractor_cleanup_v1` discriminates at NOISE_HARDER (isotropic noise on
a FULL cue, basin_ratio 1.00x); `exp_cleanup_graded_attractor_vs_argmax_v1` has one partial-cue row
and it reads "partial-cue hi-erasure top1 mh 1.000 vs argmax 1.000" -- BOTH ARMS AT CEILING, i.e.
the saturation trap. None tests an ADDRESS-ROUTED completer on a graded partial-cue axis. That is
a scope statement backed by the on-disk verdict strings. If this cell's gates fail it is a FOURTH
floored negative and is recorded as one.

BRAIN FIDELITY (PLAN R13) -- full block in prereg section 3.
  (a) STRUCTURE: hippocampal CA3 recurrent collaterals, paired with dentate gyrus separation.
  (b) REUSE: hdlab.iterative_attractor (the settle, cue-clamped), hdlab.hub_spoke_word (the
      address), and the predecessor cell's instrument. NO organ is rebuilt; gate IV6 asserts the
      completer is a bit-identical delegation, not a second implementation.
  (c) PINNED-BY-EVIDENCE: CA3 completes from a PARTIAL cue and this dissociates from full-cue
      retrieval (Nakazawa 2002). Cue-DRIVEN dynamics (Hasselmo 2002). Settling in ~1-2 gamma
      sub-cycles, which is why MAX_STEPS=4 is brain-motivated and not a tuned knob.
      OUR-INVENTION-BEING-TESTED: routing completion through an unbind-by-role-key address, and
      completing each spoke against its own codebook. Neither is in the literature. Ours.
  (d) REVIVAL, IN BRAIN TERMS: re-test over an EPISODIC INDEX (a sparse one-shot pointer), because
      Teyler & Rudy's index -- not the cortical lexicon -- is what CA3 completes. Never "revive if
      the number improves."

CONSTRUCTION PROOF. Synthetic and norm-derived spoke codes; self-identification. NO meaning claim
is licensed by any number here, and nothing here predicts movement in the 4.80% read-out.

NOTHING IS EDITED. The ruler, the parent cell, the predecessor cell, hdlab/hub_spoke_word.py and
hdlab/iterative_attractor.py are imported and never written.

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

import exp_encoding_quality_instrument_v2 as INS          # THE RULER -- imported, never edited
import exp_meaning_asset_fair_test_v1 as FT               # bootstrap constants, never edited
import exp_hub_spoke_word_representation_v1 as HS         # parent cell -- imported, never edited
import exp_hub_spoke_partial_cue_curve_v1 as PCC          # predecessor -- imported, never edited
from hdlab.hub_spoke_word import HubSpokeWord
from hdlab import ca3_completer as CC                     # the organ, default-OFF
from hdlab.iterative_attractor import iterative_cleanup
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "ca3_completion_partial_cue_v1"
CODE_VERSION = "v1.0"
PREREG = "preregs/2026-08-16_exp_ca3_completion_partial_cue_v1.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = HS.SMOKE                       # inherited, so V/d/seeds cannot diverge from the ruler
RUN_MODE = HS.RUN_MODE

# ---- config INHERITED. Nothing here is re-tuned by this cell. ----
V = HS.V
D_SWEEP = HS.D_SWEEP
SEEDS = HS.SEEDS
N_BOOT = HS.N_BOOT
BOOT_SEED = HS.BOOT_SEED
SPOKES4 = HS.SPOKES4

# prereg 5.1: the five mandated overlaps plus 0.35 and 0.10, because the predecessor measured the
# incumbent at 0.9668 (f=0.50) and 0.0322 (f=0.20) so the cliff is between them and a curve with
# no point inside it cannot show a shape. Adding sample points is not changing a threshold.
OVERLAPS = [1.00, 0.80, 0.50, 0.35, 0.20, 0.10, 0.00]
N_PROBE = PCC.N_PROBE                  # inherited from the predecessor, so numbers are comparable
TOPK = PCC.TOPK

# ---- completer settings, FIXED in prereg 5.1. No sweep is authorised in this cell. ----
ALPHA = CC.ALPHA_BRAIN_CANONICAL       # 0.5, the organ's own documented brain-canonical value
MAX_STEPS = CC.MAX_STEPS_BRAIN_MOTIVATED   # 4, ~1-2 gamma sub-cycles is the biology

# ---- pre-registered thresholds (prereg 5.3/5.4; do not edit) ----
T_IV1_KNOWN_ANSWER_MIN = 0.99
T_IV2_NULL_OVER_CHANCE = 0.01
T_IV3_NO_OVERLAP_OVER_CHANCE = 0.01
# prereg amendment A4 (at the smoke gate, before the full run): this cell's x-axis is CUE OVERLAP
# (rising), not ADDED NOISE (falling) as in the parent cell it was copied from, so the correct sign
# is POSITIVE. Magnitude unchanged at 0.80; strictness unchanged. An instance of PLAN R11 -- a
# threshold quoted without its axis.
T_IV4_SATURATION_SPEARMAN_MIN = +0.80
T_IV4B_NON_MEASURING = 0.99
T_IV9_CUE_COS_TOL = 0.05
F_PRIMARY = 0.20
F_SECONDARY = [0.35, 0.10]
T_P2_C_HOLDS = 0.50
T_P3_D_BAND = 0.02

ARMS = [
    "A_FLAT", "B_ADDRESSED", "C_ADDRESSED_CA3", "C_ADDRESSED_SNAP1", "D_CA3_ONLY",
    "B_ADDRESSED_SIGNED", "C_ADDRESSED_SIGNED_CA3",
    "KA_ORACLE_COMPLETE", "N_CA3_SHUFFLED", "F_CA3_RANDOMCB",
    "F_ORTHO_ONLY", "F_SCRAMBLE", "SLOTTED", "SLOTTED_CA3",
]
# prereg 5.4 G3. F_FREQ_ONLY is EXCLUDED, inherited from the predecessor's amendment A1 and for
# its reason: a frequency lift cannot identify an item from the item ITSELF.
FLOORS_FOR_G3 = ["F_ORTHO_ONLY", "F_SCRAMBLE", "F_CA3_RANDOMCB"]
CEILINGS_NOT_DIM_MATCHED = ["SLOTTED", "SLOTTED_CA3"]
EXCLUDED_INHERITED = ["F_FREQ_ONLY"]


def config_fp() -> str:
    """Config fingerprint in EVERY unit key, so a smoke unit can never be reloaded by a full run.
    tools/exp_checkpoint.unit_key ignores config by itself and that file is NOT edited."""
    cfg = {"code": CODE_VERSION, "mode": RUN_MODE, "V": V, "D_SWEEP": D_SWEEP, "SEEDS": SEEDS,
           "OVERLAPS": OVERLAPS, "N_PROBE": N_PROBE, "TOPK": TOPK, "N_BOOT": N_BOOT,
           "ALPHA": ALPHA, "MAX_STEPS": MAX_STEPS, "ARMS": ARMS}
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def _digest(X: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(INS._l2n(X)).tobytes()).hexdigest()[:16]


# ----------------------------------------------------------------------------------
# ARM CONSTRUCTION -- one store and one query per (arm, overlap)
# ----------------------------------------------------------------------------------
def _snap1_addressed(bundle, keys, cbs, spokes):
    """ONE nearest-neighbour snap per spoke -- routing WITHOUT settling (prereg arm, A3).

    This is the control that decides whether credit belongs to the ADDRESS or to CA3.
    """
    n, d = bundle.shape
    acc = np.zeros((n, d), dtype=np.float32)
    choices = np.zeros((n, len(spokes)), dtype=np.int64)
    for si, s in enumerate(spokes):
        frag = INS._l2n(bundle * keys[s][None, :])
        j = np.argmax(frag @ INS._l2n(cbs[s]).T, axis=1)
        choices[:, si] = j
        acc += cbs[s][j] * keys[s][None, :]
    return acc, choices


def build_unit_arms(d: int, seed: int, probe_idx: np.ndarray):
    """Return {arm: {f: (store, query_rows_for_probe, extra)}} lazily, one overlap at a time.

    Stores are built ONCE per arm. A completion arm deliberately SHARES its store with its
    uncompleted counterpart -- that is what makes (b) vs (c) a one-variable comparison.
    """
    S = HS.shared()
    words, counts = S["words"], S["counts"]
    codes = HS.spoke_codes(d, seed)
    freq_vec = FT.enc_frequency(words, counts, d, seed)
    base = PCC.arm_codes("ADDRESSED", codes, seed)              # {spoke: (V, d)} the real content
    scram = PCC.arm_codes("F_SCRAMBLE", codes, seed)

    codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
    codec_q = HubSpokeWord(d, SPOKES4, seed, quantize=True)
    keys = {s: codec.key(s) for s in SPOKES4}

    rng_rand = np.random.default_rng(INS._hash_seed("randcb", seed))
    rand_cbs = {s: rng_rand.choice(np.array([-1.0, 1.0], dtype=np.float32),
                                   size=base[s].shape) for s in SPOKES4}

    stores = {
        "A_FLAT": PCC.build_side("FLAT", base, d, seed, freq_vec),
        "B_ADDRESSED": PCC.build_side("ADDRESSED", base, d, seed, freq_vec),
        "B_ADDRESSED_SIGNED": PCC.build_side("ADDRESSED_SIGNED", base, d, seed, freq_vec),
        "F_ORTHO_ONLY": PCC.build_side("F_ORTHO_ONLY", base, d, seed, freq_vec),
        "F_SCRAMBLE": PCC.build_side("F_SCRAMBLE", scram, d, seed, freq_vec),
        "SLOTTED": PCC.build_side("SLOTTED", base, d, seed, freq_vec),
    }
    stores["C_ADDRESSED_CA3"] = stores["B_ADDRESSED"]
    stores["C_ADDRESSED_SNAP1"] = stores["B_ADDRESSED"]
    stores["D_CA3_ONLY"] = stores["A_FLAT"]
    stores["C_ADDRESSED_SIGNED_CA3"] = stores["B_ADDRESSED_SIGNED"]
    stores["KA_ORACLE_COMPLETE"] = stores["B_ADDRESSED"]
    stores["N_CA3_SHUFFLED"] = stores["B_ADDRESSED"]
    stores["F_CA3_RANDOMCB"] = stores["B_ADDRESSED"]
    stores["SLOTTED_CA3"] = stores["SLOTTED"]

    ctx = {"codes": codes, "freq_vec": freq_vec, "base": base, "scram": scram, "keys": keys,
           "codec": codec, "codec_q": codec_q, "rand_cbs": rand_cbs, "stores": stores,
           "words": words}
    return ctx


def query_for(arm: str, f: int, ctx: dict, d: int, seed: int, probe_idx: np.ndarray):
    """The query rows for one (arm, overlap). Returns (query_all_or_probe, extra_dict)."""
    base, scram, keys = ctx["base"], ctx["scram"], ctx["keys"]
    codec, codec_q = ctx["codec"], ctx["codec_q"]
    freq_vec = ctx["freq_vec"]
    extra: Dict[str, object] = {}

    # the cue: a NEW encounter, every spoke degraded INDEPENDENTLY (inherited model)
    src = scram if arm == "F_SCRAMBLE" else base
    dcodes = {s: PCC.degrade_rows(src[s], f, seed, f"cue:{s}") for s in SPOKES4}

    if arm == "A_FLAT":
        return codec.flat_sum(dcodes), extra
    if arm == "B_ADDRESSED":
        return codec.bundle(dcodes), extra
    if arm == "B_ADDRESSED_SIGNED":
        return codec_q.bundle(dcodes), extra
    if arm == "F_SCRAMBLE":
        return codec.bundle(dcodes), extra
    if arm == "F_ORTHO_ONLY":
        return dcodes[HS.SP_FORM].astype(np.float32), extra
    if arm == "SLOTTED":
        return np.concatenate([dcodes[s] for s in SPOKES4], axis=1), extra

    if arm in ("C_ADDRESSED_CA3", "C_ADDRESSED_SIGNED_CA3", "C_ADDRESSED_SNAP1",
               "N_CA3_SHUFFLED", "F_CA3_RANDOMCB", "KA_ORACLE_COMPLETE"):
        cue = (codec_q if arm == "C_ADDRESSED_SIGNED_CA3" else codec).bundle(dcodes)[probe_idx]
        if arm == "KA_ORACLE_COMPLETE":
            return CC.oracle_complete_addressed(probe_idx, keys, base, SPOKES4), extra
        if arm == "F_CA3_RANDOMCB":
            return CC.complete_addressed(cue, keys, ctx["rand_cbs"], SPOKES4,
                                         alpha=ALPHA, max_steps=MAX_STEPS), extra
        if arm == "C_ADDRESSED_SNAP1":
            q, ch = _snap1_addressed(cue, keys, base, SPOKES4)
            extra["per_spoke_completion_acc"] = float(np.mean(ch == probe_idx[:, None]))
            return q, extra
        q, ch = CC.complete_addressed(cue, keys, base, SPOKES4, alpha=ALPHA,
                                      max_steps=MAX_STEPS, return_choices=True)
        extra["per_spoke_completion_acc"] = float(np.mean(ch == probe_idx[:, None]))
        if arm == "N_CA3_SHUFFLED":
            perm = np.random.default_rng(INS._hash_seed(f"nullperm:{f}", seed)).permutation(
                len(probe_idx))
            acc = np.zeros_like(q)
            for si, s in enumerate(SPOKES4):
                acc += base[s][ch[perm, si]] * keys[s][None, :]
            return acc, extra
        return q, extra

    if arm == "D_CA3_ONLY":
        cue = codec.flat_sum(dcodes)[probe_idx]
        return CC.complete_flat(cue, ctx["stores"]["A_FLAT"], alpha=ALPHA,
                                max_steps=MAX_STEPS), extra

    if arm == "SLOTTED_CA3":
        # slots are PHYSICALLY SEPARATE -- no superposition crosstalk, so each fragment carries
        # cos ~ f rather than ~ f/2. Completion per slot, then re-concatenate. NOT dim-matched.
        acc = []
        hits = 0
        for s in SPOKES4:
            out = iterative_cleanup(dcodes[s][probe_idx].astype(np.float32), base[s],
                                    max_steps=MAX_STEPS, alpha=ALPHA)
            j = np.asarray(out["argmax_idx"], dtype=np.int64).reshape(-1)
            hits += int(np.sum(j == probe_idx))
            acc.append(base[s][j])
        extra["per_spoke_completion_acc"] = hits / float(len(probe_idx) * len(SPOKES4))
        return np.concatenate(acc, axis=1), extra

    raise KeyError(f"unknown arm {arm!r}")


# ----------------------------------------------------------------------------------
# ONE UNIT = (d, seed)
# ----------------------------------------------------------------------------------
def run_unit(d: int, seed: int) -> dict:
    t0 = time.time()
    S = HS.shared()
    n = len(S["words"])
    rngp = np.random.default_rng(INS._hash_seed("probe", seed))
    probe_idx = np.sort(rngp.choice(n, size=min(N_PROBE, n), replace=False))

    ctx = build_unit_arms(d, seed, probe_idx)
    res: Dict[str, object] = {"d": d, "seed": seed, "n_words": n, "n_probe": int(len(probe_idx)),
                              "chance_identify": 1.0 / n}

    curve: Dict[str, Dict[str, dict]] = {}
    per_word: Dict[str, Dict[str, np.ndarray]] = {}
    query_digest: Dict[str, str] = {}
    store_digest: Dict[str, str] = {a: _digest(ctx["stores"][a]) for a in ARMS}

    for arm in ARMS:
        store = ctx["stores"][arm]
        curve[arm] = {}
        per_word[arm] = {}
        for f in OVERLAPS:
            q, extra = query_for(arm, f, ctx, d, seed, probe_idx)
            if q.shape[0] == len(probe_idx):          # already probe-restricted
                full = np.zeros((store.shape[0], q.shape[1]), dtype=np.float32)
                full[probe_idx] = q
                qq = full
            else:
                qq = q
            out = PCC.identify(store, qq, probe_idx, seed, f"{arm}:{f}")
            per_word[arm][f"{f:.2f}"] = out["hit1"]
            blk = HS.boot_mean(out["hit1"])
            blk["median_rank"] = float(np.median(out["rank"]))
            blk[f"recall_at_{TOPK}"] = float(np.mean(out["topk"]))
            blk["measured_cue_cos_operator_space"] = PCC._rowwise_cos(
                qq[probe_idx], store[probe_idx])
            blk.update(extra)
            curve[arm][f"{f:.2f}"] = blk
            if abs(f - F_PRIMARY) < 1e-9:
                query_digest[arm] = _digest(qq[probe_idx])

    res["CURVE_identification_vs_cue_overlap"] = curve
    res["store_digests"] = store_digest
    res["query_digests_at_primary_overlap"] = query_digest
    res["arms_must_differ_ok"] = bool(len(set(query_digest.values())) == len(query_digest))
    res["store_sharing_is_deliberate"] = (
        "a completion arm SHARES its store with its uncompleted counterpart; that is what makes "
        "(b) vs (c) a one-variable comparison. arms_must_differ is checked on the QUERY.")

    # paired deltas -- the comparisons the gates are decided on
    def pair(a, b):
        return {f"{f:.2f}": HS.boot_diff(per_word[a][f"{f:.2f}"], per_word[b][f"{f:.2f}"])
                for f in OVERLAPS}
    res["PAIRED_DELTAS"] = {
        "G1_C_minus_B_the_pairing_gate": pair("C_ADDRESSED_CA3", "B_ADDRESSED"),
        "G2_C_minus_D_addressing_necessary": pair("C_ADDRESSED_CA3", "D_CA3_ONLY"),
        "G2b_C_minus_SNAP1_ca3_earns_its_credit": pair("C_ADDRESSED_CA3", "C_ADDRESSED_SNAP1"),
        "P3_D_minus_A_flat": pair("D_CA3_ONLY", "A_FLAT"),
        "P4_signed_minus_graded_completer": pair("C_ADDRESSED_SIGNED_CA3", "C_ADDRESSED_CA3"),
        "SLOTTED_CA3_minus_C": pair("SLOTTED_CA3", "C_ADDRESSED_CA3"),
        "C_minus_F_ORTHO_ONLY": pair("C_ADDRESSED_CA3", "F_ORTHO_ONLY"),
        "C_minus_F_CA3_RANDOMCB": pair("C_ADDRESSED_CA3", "F_CA3_RANDOMCB"),
    }

    # ---- X_ITERATION_LIFT_VS_CORRELATION (prereg A3, reported not gated) ----
    res["X_ITERATION_LIFT_VS_CORRELATION"] = iteration_lift_vs_correlation(d, seed)

    res["elapsed_s"] = time.time() - t0
    return res


def iteration_lift_vs_correlation(d: int, seed: int) -> dict:
    """Does the SETTLING earn anything, as a function of how correlated the codes are?

    Re-measures the organ self-test's table on the cell's own machinery via the parent's
    corr_spokes, so the mechanism claim is checked on real codebooks rather than a synthetic
    aside. REPORTED, NOT GATED (prereg amendment A3).
    """
    n_cb = 512 if SMOKE else 2048
    n_pr = 128 if SMOKE else 256
    out = {}
    for rho in (0.0, 0.5, 0.8):
        cb_map = HS.corr_spokes(rho, n_cb, d, seed, f=len(SPOKES4))
        names = sorted(cb_map)
        keys = {s: HubSpokeWord(d, names, seed).key(s) for s in names}
        cbs = {s: cb_map[s] for s in names}
        rng = np.random.default_rng(INS._hash_seed(f"itlift:{rho}", seed))
        idx = np.sort(rng.choice(n_cb, size=n_pr, replace=False))
        cue = np.zeros((n_pr, d), dtype=np.float32)
        for s in names:
            deg = PCC.degrade_rows(cbs[s], 0.5, seed, f"itlift:{rho}:{s}")[idx]
            cue += deg * keys[s][None, :]
        _, ch_it = CC.complete_addressed(cue, keys, cbs, names, alpha=ALPHA,
                                         max_steps=MAX_STEPS, return_choices=True)
        _, ch_1 = _snap1_addressed(cue, keys, cbs, names)
        a_it = float(np.mean(ch_it == idx[:, None]))
        a_1 = float(np.mean(ch_1 == idx[:, None]))
        out[f"rho={rho}"] = {"per_spoke_iterative": a_it, "per_spoke_single_snap": a_1,
                             "iteration_lift": a_it - a_1,
                             "measured_within_word_cos": float(np.mean(
                                 np.sum(INS._l2n(cbs[names[0]][idx]) * INS._l2n(cbs[names[1]][idx]),
                                        axis=1)))}
    return out


# ----------------------------------------------------------------------------------
# SELF-TESTS -- must pass BEFORE any data run. Assert VALUES, not absence of errors.
# ----------------------------------------------------------------------------------
def selftest() -> dict:
    out: Dict[str, object] = {}
    d, seed = 256, 7

    # IV6 -- the completer is a bit-identical DELEGATION, not a second implementation
    g = np.random.default_rng(55)
    cb = g.standard_normal((128, 64)).astype(np.float32)
    cue = cb[g.integers(0, 128, 16)] + 0.4 * g.standard_normal((16, 64)).astype(np.float32)
    assert np.array_equal(CC.complete_flat(cue, cb, alpha=ALPHA, max_steps=MAX_STEPS),
                          iterative_cleanup(cue.astype(np.float32), cb, max_steps=MAX_STEPS,
                                            alpha=ALPHA)["state"]), \
        "IV6 FAIL: complete_flat is not bit-identical to hdlab.iterative_attractor"
    out["IV6_completer_is_reuse_not_reimplementation"] = True

    # IV7 -- the arms this cell builds ARE the predecessor's, reconstructed independently
    codes = HS.spoke_codes(d, seed)
    S = HS.shared()
    freq_vec = FT.enc_frequency(S["words"], S["counts"], d, seed)
    base = PCC.arm_codes("ADDRESSED", codes, seed)
    codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
    assert np.array_equal(codec.bundle(base), PCC.build_side("ADDRESSED", base, d, seed, freq_vec)), \
        "IV7 FAIL: ADDRESSED store differs from the predecessor cell's"
    assert np.array_equal(codec.flat_sum(base), PCC.build_side("FLAT", base, d, seed, freq_vec)), \
        "IV7 FAIL: FLAT store differs from the predecessor cell's"
    out["IV7_stores_bit_identical_to_predecessor"] = True

    # IV9 -- the cue axis is what it is labelled
    X = base[HS.SP_FORM]
    track = {f"{f:.2f}": PCC._rowwise_cos(PCC.degrade_rows(X, f, seed, "st"), X)
             for f in OVERLAPS}
    assert all(abs(track[f"{f:.2f}"] - f) <= T_IV9_CUE_COS_TOL for f in OVERLAPS), \
        f"IV9 FAIL: cue cosine does not track f: {track}"
    assert all(track[f"{OVERLAPS[i]:.2f}"] > track[f"{OVERLAPS[i+1]:.2f}"]
               for i in range(len(OVERLAPS) - 1)), f"IV9 FAIL: cue cosine not monotone: {track}"
    out["IV9_cue_cos_tracks_f"] = track

    # small-scale IV1/IV2/IV3 on the REAL arm machinery
    n = len(S["words"])
    # AMENDMENT A5 (2026-08-16, at the FULL gate, before any full unit was scored). This check
    # first used 96 probes, at which ONE lucky hit is 0.0104 -- COARSER THAN THE 0.01 THRESHOLD
    # ITSELF, so a single chance hit fails the gate (it did, at 0.010417 vs a 0.010244 band).
    # That is an UNDERPOWERED CHECK, not a leak: at chance 1/4096, 96 probes expect 0.023 hits.
    # The fix raises the POWER, not the threshold -- no threshold in this file is changed.
    # 512 probes give a resolution of 0.00195, comfortably finer than the 0.01 band.
    pidx = np.sort(np.random.default_rng(2).choice(n, size=min(512, n), replace=False))
    ctx = build_unit_arms(d, seed, pidx)
    ka, nl, no = {}, {}, {}
    for arm in ("KA_ORACLE_COMPLETE", "N_CA3_SHUFFLED", "C_ADDRESSED_CA3", "B_ADDRESSED"):
        for f, bucket in ((1.00, ka), (0.00, no)):
            q, _ = query_for(arm, f, ctx, d, seed, pidx)
            store = ctx["stores"][arm]
            full = np.zeros((store.shape[0], q.shape[1]), dtype=np.float32)
            if q.shape[0] == len(pidx):
                full[pidx] = q
            else:
                full = q
            bucket[arm] = float(PCC.identify(store, full, pidx, seed, f"st:{arm}:{f}")["hit1"].mean())
    assert ka["KA_ORACLE_COMPLETE"] >= T_IV1_KNOWN_ANSWER_MIN, \
        f"IV1 FAIL: known-answer arm {ka['KA_ORACLE_COMPLETE']}"
    assert no["KA_ORACLE_COMPLETE"] >= T_IV1_KNOWN_ANSWER_MIN, \
        f"IV1 FAIL: known-answer arm is cue-sensitive at f=0: {no['KA_ORACLE_COMPLETE']}"
    q, _ = query_for("N_CA3_SHUFFLED", 0.50, ctx, d, seed, pidx)
    store = ctx["stores"]["N_CA3_SHUFFLED"]
    full = np.zeros((store.shape[0], q.shape[1]), dtype=np.float32)
    full[pidx] = q
    nullv = float(PCC.identify(store, full, pidx, seed, "st:null")["hit1"].mean())
    assert nullv <= 1.0 / n + T_IV2_NULL_OVER_CHANCE, f"IV2 FAIL: null arm at {nullv}"
    for arm in ("C_ADDRESSED_CA3", "B_ADDRESSED"):
        assert no[arm] <= 1.0 / n + T_IV3_NO_OVERLAP_OVER_CHANCE, \
            f"IV3 FAIL: {arm} at f=0 scores {no[arm]}"
    out["IV1_known_answer"] = ka
    out["IV2_null_shuffled_choice"] = nullv
    out["IV3_no_overlap"] = no

    # IV5 -- queries at the primary overlap must DIFFER across arms
    digs = {}
    for arm in ARMS:
        q, _ = query_for(arm, F_PRIMARY, ctx, d, seed, pidx)
        digs[arm] = _digest(q if q.shape[0] == len(pidx) else q[pidx])
    assert len(set(digs.values())) == len(digs), f"IV5 FAIL: arm queries collide: {digs}"
    out["IV5_arms_differ_at_primary_overlap"] = digs

    # ST metric can go down -- a measure that cannot decline is not a measurement
    hi, _ = query_for("B_ADDRESSED", 1.00, ctx, d, seed, pidx)
    lo, _ = query_for("B_ADDRESSED", 0.00, ctx, d, seed, pidx)
    sb = ctx["stores"]["B_ADDRESSED"]
    a_hi = float(PCC.identify(sb, hi, pidx, seed, "mv:hi")["hit1"].mean())
    a_lo = float(PCC.identify(sb, lo, pidx, seed, "mv:lo")["hit1"].mean())
    assert a_lo < a_hi, f"ST FAIL: the measure did not move with the cue: {a_hi} -> {a_lo}"
    out["ST_metric_moves"] = {"f1.00": a_hi, "f0.00": a_lo}

    # AMENDMENT A2 -- the reclassified floor is MEASURED here, not hidden
    qf, _ = query_for("F_CA3_RANDOMCB", 0.50, ctx, d, seed, pidx)
    fullf = np.zeros((sb.shape[0], qf.shape[1]), dtype=np.float32)
    fullf[pidx] = qf
    out["ST_A2_random_overcomplete_dictionary_floor_at_f050"] = {
        "top1": float(PCC.identify(sb, fullf, pidx, seed, "st:randcb")["hit1"].mean()),
        "M_over_d": sb.shape[0] / float(d),
        "reason": "reclassified from NULL to FLOOR: with M>d a random codebook is an overcomplete "
                  "dictionary and snapping to it reconstructs the cue"}

    # rulers TRACKED and CLEAN at HEAD
    import subprocess
    rs = {}
    for fpath in ("experiments/exp_encoding_quality_instrument_v2.py",
                  "experiments/exp_hub_spoke_word_representation_v1.py",
                  "experiments/exp_hub_spoke_partial_cue_curve_v1.py",
                  "hdlab/hub_spoke_word.py", "hdlab/iterative_attractor.py"):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", fpath],
                                 cwd=str(REPO), capture_output=True, text=True).returncode == 0
        porc = subprocess.run(["git", "status", "--porcelain", "--", fpath], cwd=str(REPO),
                              capture_output=True, text=True).stdout.strip()
        rs[fpath] = {"tracked": tracked, "porcelain": porc,
                     "sha256_16": hashlib.sha256((REPO / fpath).read_bytes()).hexdigest()[:16]}
        if tracked:
            assert porc == "", f"TRACKED RULER MODIFIED: {fpath} -> {porc!r}"
    out["ST_ruler_status"] = rs

    # the organ default is OFF and this cell did not flip it
    assert CC.CA3_COMPLETION is False, "ST FAIL: CA3_COMPLETION is not default-OFF"
    out["ST_organ_default_off"] = True

    banned = [m for m in sys.modules if any(
        t in m.lower() for t in ("transformers", "openai", "llama", "sentence_transformers"))]
    assert not banned, f"IV8 FAIL: external LLM module in the runtime path: {banned}"
    out["IV8_no_external_llm"] = True
    return out


# ----------------------------------------------------------------------------------
# EVALUATION
# ----------------------------------------------------------------------------------
def _mean(units, d, path, default=float("nan")):
    vals = []
    for u in units:
        if u.get("d") != d:
            continue
        cur = u
        try:
            for k in path:
                cur = cur[k]
            vals.append(float(cur))
        except (KeyError, TypeError, IndexError):
            continue
    return float(np.mean(vals)) if vals else default


def _agg_delta(units, d, key, f):
    pts, los, his = [], [], []
    for u in units:
        if u.get("d") != d:
            continue
        try:
            b = u["PAIRED_DELTAS"][key][f"{f:.2f}"]
        except (KeyError, TypeError):
            continue
        pts.append(b["point"])
        los.append(b["ci95"][0])
        his.append(b["ci95"][1])
    if not pts:
        return None
    return {"point": float(np.mean(pts)), "ci95": [float(np.mean(los)), float(np.mean(his))],
            "n_seeds": len(pts)}


def _agg_arm(units, d, arm, f, field="point"):
    return _mean(units, d, ["CURVE_identification_vs_cue_overlap", arm, f"{f:.2f}", field])


def _agg_ci(units, d, arm, f, which):
    vals = []
    for u in units:
        if u.get("d") != d:
            continue
        try:
            vals.append(u["CURVE_identification_vs_cue_overlap"][arm][f"{f:.2f}"]["ci95"][which])
        except (KeyError, TypeError, IndexError):
            continue
    return float(np.mean(vals)) if vals else float("nan")


def evaluate(units: List[dict]) -> dict:
    d_native = D_SWEEP[-1]                 # 256 = the production-native d
    chance = _mean(units, d_native, ["chance_identify"])
    ev: Dict[str, object] = {"d_reported": d_native, "chance": chance,
                             "d_sweep_all_reported": D_SWEEP}

    # ---- INSTRUMENT VALIDITY ----
    iv: Dict[str, object] = {}
    ka = {f"{f:.2f}": _agg_arm(units, d_native, "KA_ORACLE_COMPLETE", f) for f in OVERLAPS}
    iv["IV1_known_answer_per_overlap"] = ka
    iv["IV1_passed"] = bool(all(v >= T_IV1_KNOWN_ANSWER_MIN for v in ka.values()))
    nl = {f"{f:.2f}": _agg_arm(units, d_native, "N_CA3_SHUFFLED", f) for f in OVERLAPS}
    iv["IV2_null_per_overlap"] = nl
    iv["IV2_passed"] = bool(all(v <= chance + T_IV2_NULL_OVER_CHANCE for v in nl.values()))
    no = {a: _agg_arm(units, d_native, a, 0.00) for a in ARMS if a != "KA_ORACLE_COMPLETE"}
    iv["IV3_no_overlap_per_arm"] = no
    iv["IV3_passed"] = bool(all(v <= chance + T_IV3_NO_OVERLAP_OVER_CHANCE for v in no.values()))

    b_curve = [_agg_arm(units, d_native, "B_ADDRESSED", f) for f in OVERLAPS]
    rho = _spearman(OVERLAPS, b_curve)
    iv["IV4_saturation_spearman"] = rho
    iv["IV4_axis"] = "spearman(cue_overlap, B_ADDRESSED top1); rising axis, so the gate is POSITIVE"
    iv["IV4_passed"] = bool(rho >= T_IV4_SATURATION_SPEARMAN_MIN)

    scored = [a for a in ARMS if a not in ("KA_ORACLE_COMPLETE", "N_CA3_SHUFFLED")]
    nonmeas = {}
    for f in OVERLAPS:
        vals = [_agg_arm(units, d_native, a, f) for a in scored]
        nonmeas[f"{f:.2f}"] = bool(all(v > T_IV4B_NON_MEASURING for v in vals))
    iv["IV4b_non_measuring_overlaps"] = nonmeas
    iv["IV4b_primary_overlap_is_measuring"] = not nonmeas[f"{F_PRIMARY:.2f}"]

    iv["IV5_arms_must_differ_ok"] = bool(all(u.get("arms_must_differ_ok", False) for u in units))
    iv["IV6_IV7_IV8_IV9"] = "asserted in selftest(); the run aborts if any fails"
    iv["all_passed"] = bool(iv["IV1_passed"] and iv["IV2_passed"] and iv["IV3_passed"]
                            and iv["IV4_passed"] and iv["IV4b_primary_overlap_is_measuring"]
                            and iv["IV5_arms_must_differ_ok"])
    ev["INSTRUMENT_VALIDITY"] = iv

    # ---- THE CURVE (every arm, every overlap, both d) ----
    ev["CURVE"] = {f"d={d}": {a: {f"{f:.2f}": {
        "top1": _agg_arm(units, d, a, f),
        "ci95": [_agg_ci(units, d, a, f, 0), _agg_ci(units, d, a, f, 1)],
        f"recall_at_{TOPK}": _agg_arm(units, d, a, f, f"recall_at_{TOPK}"),
        "median_rank": _agg_arm(units, d, a, f, "median_rank"),
        "per_spoke_completion_acc": _agg_arm(units, d, a, f, "per_spoke_completion_acc"),
    } for f in OVERLAPS} for a in ARMS} for d in D_SWEEP}

    if not iv["all_passed"]:
        ev["VERDICT"] = "INSTRUMENT_STILL_LOOSE"
        ev["verdict_msg"] = ("INSTRUMENT_STILL_LOOSE: an instrument-validity gate failed; NO "
                             "quality number is published. " + json.dumps(
                                 {k: v for k, v in iv.items() if k.endswith("passed")}))
        return ev

    # ---- SCIENTIFIC GATES (prereg 5.4) ----
    g: Dict[str, object] = {}
    g1 = _agg_delta(units, d_native, "G1_C_minus_B_the_pairing_gate", F_PRIMARY)
    g["G1_pairing"] = {"delta": g1, "passed": bool(g1 and g1["ci95"][0] > 0.0)}
    g2 = _agg_delta(units, d_native, "G2_C_minus_D_addressing_necessary", F_PRIMARY)
    g["G2_addressing_necessary"] = {"delta": g2, "passed": bool(g2 and g2["ci95"][0] > 0.0)}
    g2b = _agg_delta(units, d_native, "G2b_C_minus_SNAP1_ca3_earns_its_credit", F_PRIMARY)
    g["G2b_ca3_earns_its_credit"] = {
        "delta": g2b, "passed": bool(g2b and g2b["ci95"][0] > 0.0),
        "meaning": "if this CI covers zero the SETTLING contributed nothing and any win belongs "
                   "to the ADDRESS (routing), not to CA3"}

    c_lo = _agg_ci(units, d_native, "C_ADDRESSED_CA3", F_PRIMARY, 0)
    floor_hi = {a: _agg_ci(units, d_native, a, F_PRIMARY, 1) for a in FLOORS_FOR_G3}
    strongest = max(floor_hi, key=lambda k: floor_hi[k])
    g["G3_floor"] = {"C_ci_lower": c_lo, "floor_ci_uppers": floor_hi,
                     "strongest_floor": strongest,
                     "passed": bool(c_lo > floor_hi[strongest])}

    c_r = _agg_arm(units, d_native, "C_ADDRESSED_CA3", F_PRIMARY, f"recall_at_{TOPK}")
    o_r = _agg_arm(units, d_native, "F_ORTHO_ONLY", F_PRIMARY, f"recall_at_{TOPK}")
    g["G4_spelling_neighbourhood_bar"] = {
        f"C_recall_at_{TOPK}": c_r, f"F_ORTHO_ONLY_recall_at_{TOPK}": o_r,
        "C_median_rank": _agg_arm(units, d_native, "C_ADDRESSED_CA3", F_PRIMARY, "median_rank"),
        "F_ORTHO_ONLY_median_rank": _agg_arm(units, d_native, "F_ORTHO_ONLY", F_PRIMARY,
                                             "median_rank"),
        "passed": bool(c_r > o_r),
        "note": "until this passes, no writeup may say 'beats the floors' -- only 'beats the "
                "floors on top-1'"}
    ev["SCIENTIFIC_GATES"] = g

    # ---- PREDICTIONS, SCORED HONESTLY ----
    b_hi = _agg_arm(units, d_native, "B_ADDRESSED", 0.50)
    b_pri = _agg_arm(units, d_native, "B_ADDRESSED", F_PRIMARY)
    c_pri = _agg_arm(units, d_native, "C_ADDRESSED_CA3", F_PRIMARY)
    p3 = _agg_delta(units, d_native, "P3_D_minus_A_flat", F_PRIMARY)
    p4 = _agg_delta(units, d_native, "P4_signed_minus_graded_completer", F_PRIMARY)
    ev["PREDICTIONS"] = {
        "P1_B_collapses": {"B_at_0.50": b_hi, "B_at_primary": b_pri,
                           "scored": "CONFIRMED" if b_pri < b_hi - 0.10 else "NOT_CONFIRMED"},
        "P2_C_holds_top1_ge_0.50_at_primary": {
            "C_at_primary": c_pri, "threshold": T_P2_C_HOLDS,
            "scored": "CONFIRMED" if c_pri >= T_P2_C_HOLDS else "FALSIFIED"},
        "P3_D_minus_A_within_band": {
            "delta": p3, "band": T_P3_D_BAND,
            "scored": "CONFIRMED" if p3 and abs(p3["point"]) <= T_P3_D_BAND else "NOT_CONFIRMED"},
        "P4_signing_costs_the_completer": {
            "delta": p4, "scored": "CONFIRMED" if p4 and p4["point"] < 0 else "NOT_CONFIRMED"},
    }

    # ---- the ceiling and the diagnostic, reported beside, never instead of ----
    ev["CEILINGS_NOT_DIMENSION_MATCHED"] = {
        a: {f"{f:.2f}": _agg_arm(units, d_native, a, f) for f in OVERLAPS}
        for a in CEILINGS_NOT_DIM_MATCHED}
    ev["SLOTTED_CA3_minus_C_at_primary"] = _agg_delta(units, d_native, "SLOTTED_CA3_minus_C",
                                                      F_PRIMARY)
    ev["X_ITERATION_LIFT_VS_CORRELATION"] = {
        f"d={d}": {rk: {m: _mean(units, d, ["X_ITERATION_LIFT_VS_CORRELATION", rk, m])
                        for m in ("per_spoke_iterative", "per_spoke_single_snap",
                                  "iteration_lift", "measured_within_word_cos")}
                   for rk in ("rho=0.0", "rho=0.5", "rho=0.8")} for d in D_SWEEP}

    ev["SECONDARY_OVERLAPS"] = {f"{f:.2f}": {
        "G1_C_minus_B": _agg_delta(units, d_native, "G1_C_minus_B_the_pairing_gate", f),
        "C": _agg_arm(units, d_native, "C_ADDRESSED_CA3", f),
        "B": _agg_arm(units, d_native, "B_ADDRESSED", f),
    } for f in F_SECONDARY}

    passed = [k for k, v in g.items() if v.get("passed")]
    if g["G1_pairing"]["passed"]:
        verdict = "COMPLETION_RESCUES_ADDRESSING" if len(passed) == len(g) \
            else "COMPLETION_HELPS_BUT_DOES_NOT_CLEAR_EVERY_GATE"
    else:
        verdict = "PAIRING_HYPOTHESIS_REFUTED"
    ev["VERDICT"] = verdict
    ev["verdict_msg"] = (
        f"{verdict}: at cue overlap {F_PRIMARY:.2f} (d={d_native}, chance {chance:.2e}) "
        f"B_ADDRESSED={b_pri:.4f} C_ADDRESSED_CA3={c_pri:.4f}; "
        f"G1 C-B delta={g1['point']:+.4f} CI{g1['ci95']}; "
        f"G2b C-SNAP1 delta={g2b['point']:+.4f} CI{g2b['ci95']} "
        f"(if this covers zero the settling earned nothing); "
        f"G3 floor={strongest} C_lo={c_lo:.4f} vs floor_hi={floor_hi[strongest]:.4f}; "
        f"gates passed {len(passed)}/{len(g)}. "
        f"P2 (C top1>={T_P2_C_HOLDS} at primary) "
        f"{ev['PREDICTIONS']['P2_C_holds_top1_ge_0.50_at_primary']['scored']}. "
        f"CONSTRUCTION PROOF ONLY -- no meaning claim, no read-out claim.")
    return ev


def _spearman(x, y) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 3:
        return float("nan")

    def rank(v):
        o = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), dtype=np.float64)
        r[o] = np.arange(len(v), dtype=np.float64)
        return r
    rx, ry = rank(x), rank(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = float(np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))
    return float((rx * ry).sum() / den) if den > 0 else float("nan")


# ----------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    st = selftest()
    if _ARGS.self_test:
        print("[%s self-test] PASS\n%s" % (ANCHOR_NAME, json.dumps(st, indent=2, default=float)),
              flush=True)
        return 0

    outdir = get_output_dir(ANCHOR_NAME)   # SH-5 appends the _smoke suffix from argv itself
    Path(outdir).mkdir(parents=True, exist_ok=True)
    fp = config_fp()
    done = completed_units(outdir)
    total = len(D_SWEEP) * len(SEEDS)
    i = 0
    for d in sorted(set(D_SWEEP)):
        for seed in sorted(set(SEEDS)):
            i += 1
            key = unit_key(f"cfg{fp}", f"d{d}", f"s{seed}")
            if key in done:
                print(f"[{ANCHOR_NAME}] {i}/{total} skip (done) {key}", flush=True)
                continue
            print(f"[{ANCHOR_NAME}] {i}/{total} running d={d} seed={seed} "
                  f"({time.time()-t0:.0f}s elapsed)", flush=True)
            r = run_unit(d, seed)
            record_unit(outdir, key, r)
            print(f"[{ANCHOR_NAME}] {i}/{total} done d={d} seed={seed} "
                  f"unit_elapsed={r['elapsed_s']:.0f}s", flush=True)

    # load_units returns {unit_key: result}. Iterating it directly yields KEYS, which silently
    # produced an EMPTY unit set and a full NaN verdict on the first smoke. The guard below is
    # the fix for that class: a cell must never publish a verdict computed on zero units.
    _loaded = load_units(outdir)
    units = [_loaded[k] for k in sorted(_loaded)
             if isinstance(_loaded[k], dict)
             and "CURVE_identification_vs_cue_overlap" in _loaded[k]]
    if len(units) != total:
        raise SystemExit(
            f"[fatal] loaded {len(units)} of {total} expected units -- refusing to evaluate "
            f"gates on an incomplete set")
    ev = evaluate(units)
    if not np.isfinite(ev.get("chance", float("nan"))):
        raise SystemExit("[fatal] chance is not finite -- the unit set did not carry the "
                         "expected fields; refusing to publish a verdict")
    metrics = {
        "anchor": ANCHOR_NAME, "code_version": CODE_VERSION, "prereg": PREREG,
        "run_mode": RUN_MODE, "V": V, "D_SWEEP": D_SWEEP, "SEEDS": SEEDS,
        "OVERLAPS": OVERLAPS, "N_PROBE": N_PROBE, "N_BOOT": N_BOOT,
        "ALPHA": ALPHA, "MAX_STEPS": MAX_STEPS,
        "organ_default_off": CC.CA3_COMPLETION,
        "excluded_channels_inherited": EXCLUDED_INHERITED,
        "config_fingerprint": fp, "n_units": len(units),
        "selftest": st, "elapsed_s": time.time() - t0,
        "verdict": ev["VERDICT"], "verdict_msg": ev["verdict_msg"],
        "summary": ev,
    }
    write_metrics(outdir, metrics)
    print(f"[{ANCHOR_NAME}] VERDICT {ev['VERDICT']}\n{ev['verdict_msg']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
