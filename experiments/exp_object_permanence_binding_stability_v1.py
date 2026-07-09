"""Object-permanence bake-in probe (innate-scaffolding bake-in #1).

Tests whether baking in "object-persistence as a binding-stability default"
gives the substrate an infant-like object permanence: a bound entity-identity
SURVIVES an occlusion-like corruption unless ACTIVELY broken, where a naive
representation loses the entity. Brain-grounded (Baillargeon/Spelke
violation-of-expectation: object continuity/solidity/cohesion, pre-linguistic
~2.5-4.5mo; Kellman & Spelke 1983; Baillargeon, Spelke & Wasserman 1985).

DESIGN (HD/VSA-native form of cohesion + continuity):
  An entity = identity token + F feature tokens. TWO storage arms encode the
  SAME entity (identical tokens; matched information) and are recovered by the
  SAME cleanup operation under the SAME corruption (paired trials):

  PERSISTENCE (holographic bound bundle -- the bake-in):
    E_p = bind(role_id, id_tok) + sum_f bind(role_f, feat_tok_f), spread over
    ALL N dims. Identity is DISTRIBUTED across every dimension by the binding
    operator (cohesion). Recover: cleanup(unbind(occ(E_p), role_id)).

  NAIVE (localist concatenation -- the baseline):
    Partition N into P=F+1 disjoint dim-blocks; store each token RAW in its own
    block (id in block 0, feature f in block f+1). No binding, no distribution;
    each field is localized -- there is no cross-field redundancy. Recover:
    cleanup(E_n[block0]) over block-0 dims.

  Neither arm is a strawman: localist per-field storage is a standard structured
  -record encoding. The claim under test is the biological one -- distributing a
  bound identity holographically (cohesion) yields occlusion-robustness the
  localist code lacks.

CORRUPTION (matched across arms; paired):
  STRUCTURED occlusion (an occluder covers whole parts of the object): zero k of
  the P dim-blocks, chosen uniformly. This is the object-permanence-relevant
  corruption -- correlated/structured loss, NOT i.i.d. dim noise.
    - PERSISTENCE: identity spread over all dims -> zeroing k/P of dims removes a
      uniform fraction of the id signal -> recoverable (graceful degradation).
    - NAIVE: identity confined to block 0 -> survives iff block 0 is not among
      the k occluded blocks -> recovery ~ (P-k)/P by construction.
  Diagnostic i.i.d. occlusion (same total fraction, scattered) is ALSO logged:
  under i.i.d. loss BOTH arms degrade proportionally (no gap) -- this pins the
  persistence advantage to STRUCTURED corruption specifically (honest scope; the
  holographic redundancy only helps against correlated loss).

MUST-FAIL CONTROLS (vacuous-guard; the pass must not be the tautology
"persistence always says present"):
  REMOVED: actively subtract the identity binding before querying
    (E_p_removed = E_p - bind(role_id, id_tok); naive: zero block 0). The entity
    was taken away -> recovery of id_tok MUST fall to chance. If persistence
    "recovers" a removed entity above chance -> LEAK/tautology -> HARD_FAIL.
  SCRAMBLED: bind id_tok to a WRONG role -> unbind(role_id) returns no id term
    -> recovery MUST be at chance (guards "recovery needs the correct binding").

DISCRIMINATOR (research pre-reg, both bands):
  ratio = rec_persist_structured / rec_naive_structured (paired, matched corrupt)
  HARD_PASS = ratio >= 2.0 AND rec_persist_structured >= 0.70 (strict floor) AND
    gap(persist-naive) >= MIN_EFFECT AND naive in measurable band AND the
    must-fail controls FAIL to recover (removed/scrambled <= chance+margin).
  HARD_FAIL = ratio <= 1.3 with a real occlusion effect (the persistence prior
    adds nothing -- naive already persists) OR a must-fail control RECOVERS
    (tautology/leak) regardless of ratio.
  MIDDLE = partial (ratio in (1.3, 2.0), or controls marginal).

Both outcomes are gold: PASS transfers biology's object-permanence-as-binding
-stability design principle to the substrate (a structural bake-in, composes
with the dual-number bake-in); FAIL says the naive binding already persists /
the prior adds nothing (one less thing to bake in). HONEST framing: this is an
architectural-support result (like dual-number: supports, not spontaneous-
learning); mechanism-analog, NOT task-analog.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; persist vs naive bit-distinct)
# - final_metrics_atomicity = tmp_replace (write_metrics) + per-seed write_partial
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: discriminator is a paired recovery-accuracy RATIO, not noise-floor est.
# - baseline_in_band at smoke (naive_structured in [chance+0.03, 0.90]; META_RULE_AG)
# - discriminator survives scale: smoke runs at FULL N=8192, 1 seed, reduced trials
# - HARD_PASS strictly above MIDDLE ceiling (ratio>=2.0 vs MIDDLE (1.3,2.0)) + persist floor
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (verdict counts len(per_seed))
# - per-unit failure-class instrumentation (no bare except; crash-diagnostic metrics)
# - calibration_check: default_ok_for_this_regime (clean synthetic; analytical SNR)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in comments

Numbers in this docstring / config (tagged):
  - naive_structured recovery ~ (P-k)/P = 3/8 = 0.375  THEORETICAL@block-survival prob C(P-1,k)/C(P,k)
  - persist_structured unbind cos ~ sqrt(N_surv/N)/sqrt(1+F) = 0.61/sqrt(8) ~ 0.216, z~12 vs
    competitor std 1/sqrt(N_surv) -> top-1 ~ 1.0  THEORETICAL@bipolar bundle unbind SNR
  - chance = 1/V_TOK = 1/64 = 0.0156  THEORETICAL@uniform argmax over codebook
  - P(object-permanence bake-in transfers) ~ structural-prior, deflated  CITED@notes/research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md:S2.bake-in-1

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# sys.path shim so `python experiments/exp_...py` (runner path) can import siblings.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
for _p in (_REPO, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    assert_discriminator_fires,
    get_output_dir,
    record_gate,
    resumable_seeds,
    write_metrics,
    write_partial,
)
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "exp_object_permanence_binding_stability_v1"

# ----------------------------------------------------------------------------
# Config (SMOKE=FULL parity: identical code path; only trial-count/seed differ).
# ----------------------------------------------------------------------------
N_DIM = 8192               # substrate dimensionality (project default anchor)
F_FEAT = 7                 # feature tokens per entity -> P = F+1 = 8 fields/blocks
P_BLOCKS = F_FEAT + 1      # 8 dim-blocks (block 0 = identity; 1..F = features)
B_WIDTH = N_DIM // P_BLOCKS  # 1024 dims per block (N divisible by P required)
V_TOK = 64                 # token codebook size; chance = 1/V_TOK
K_OCC = 5                  # STRUCTURED occlusion: zero 5 of 8 blocks (f_occ=0.625)
F_OCC = K_OCC / P_BLOCKS   # 0.625 total-dim occlusion fraction (i.i.d. matched)

SEEDS_FULL = (7, 17, 23)
SEEDS_SMOKE = (7,)
M_TRIALS_FULL = 600
M_TRIALS_SMOKE = 200

# Discriminator bands (research pre-reg, object-permanence prediction).
CHANCE = 1.0 / V_TOK       # 0.015625  THEORETICAL@uniform argmax
HP_RATIO = 2.0             # HARD_PASS: persist/naive recovery ratio >= 2.0
HFAIL_RATIO = 1.3          # HARD_FAIL: ratio <= 1.3 (prior adds nothing)
HP_PERSIST_FLOOR = 0.70    # HARD_PASS: persist_structured must clear this (strict)
MIN_EFFECT = 0.15          # min absolute recovery gap / occlusion effect to be "real"
REMOVED_MARGIN = 0.10      # control "correctly fails" iff recovery <= CHANCE + this
LEAK_MARGIN = 0.20         # control RECOVERS (leak/tautology) iff > CHANCE + this
NAIVE_BAND_LO = CHANCE + 0.03  # naive baseline must be a non-degenerate real baseline
NAIVE_BAND_HI = 0.90           # ... and not saturated (META_RULE_AG)
NO_OCC_FLOOR = 0.95        # both arms must recover ~perfectly with zero occlusion
RATIO_CAP = 100.0
EPS = 1e-9


# ----------------------------------------------------------------------------
# Substrate primitives (bipolar BSC: bind = elementwise mul, bundle = sum).
# ----------------------------------------------------------------------------
def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _bipolar(rng: np.random.Generator, rows: int, n: int) -> np.ndarray:
    """(rows, n) bipolar {-1,+1} float32 matrix."""
    return (rng.integers(0, 2, size=(rows, n)).astype(np.float32) * 2.0) - 1.0


def _block_slice(b: int) -> slice:
    """Dim range for field/occlusion block b."""
    return slice(b * B_WIDTH, (b + 1) * B_WIDTH)


def _cleanup_argmax(vec: np.ndarray, cb_slice: np.ndarray, dims: slice,
                    rng: np.random.Generator) -> int:
    """Top-1 codebook index by cosine of vec[dims] vs cb_slice rows.

    cb_slice is CB restricted to `dims` (shape (V_TOK, |dims|)). Degenerate
    (near-zero) query returns a UNIFORM RANDOM index -> recovery falls to chance
    (avoids argmax-index-0 bias; makes removed/occluded-block controls truly
    chance rather than a spurious constant).
    """
    v = vec[dims]
    nv = float(np.linalg.norm(v))
    if nv < 1e-8:
        return int(rng.integers(V_TOK))
    sims = cb_slice @ v  # (V_TOK,)
    cbn = np.linalg.norm(cb_slice, axis=1)
    cbn = np.where(cbn > 0, cbn, 1.0)
    sims = sims / (cbn * nv)
    sims = sims + rng.normal(0.0, 1e-9, size=V_TOK).astype(sims.dtype)  # tie-break
    return int(np.argmax(sims))


# ----------------------------------------------------------------------------
# Per-trial: build both arms, apply corruption variants, recover identity.
# ----------------------------------------------------------------------------
def _run_trials(rng, cb, roles, m_trials):
    """Return per-condition recovery accuracies + arm hashes for m_trials.

    Conditions (all PAIRED on identical id/feature/occlusion draws):
      positive occluded:  ps (persist_struct), ns (naive_struct),
                          pi (persist_iid),    ni (naive_iid)
      no-occlusion:       ps0, ns0  (machinery sanity; expect ~1.0)
      must-fail control:  prem (persist removed), nrem (naive removed),
                          pscr (persist scrambled)  (expect ~chance)
    """
    cb_full = cb                                  # (V_TOK, N) full-dim candidates
    blk0 = _block_slice(0)
    cb_blk0 = cb[:, blk0]                          # (V_TOK, B) block-0 candidates
    role_id = roles[0]

    hits = {k: 0 for k in ("ps", "ns", "pi", "ni", "ps0", "ns0",
                           "prem", "nrem", "pscr")}
    # arm-hash accumulators (structured-occluded persist vs naive; must differ).
    h_persist = hashlib.sha256()
    h_naive = hashlib.sha256()

    for _ in range(m_trials):
        id_tok = int(rng.integers(0, V_TOK))
        feat_toks = rng.integers(0, V_TOK, size=F_FEAT)

        # --- PERSISTENCE arm: holographic bound bundle over all N dims. -------
        E_p = role_id * cb[id_tok]
        for f in range(F_FEAT):
            E_p = E_p + roles[f + 1] * cb[feat_toks[f]]

        # --- NAIVE arm: localist raw tokens, each in its own block. -----------
        E_n = np.zeros(N_DIM, dtype=np.float32)
        E_n[blk0] = cb[id_tok][blk0]
        for f in range(F_FEAT):
            bs = _block_slice(f + 1)
            E_n[bs] = cb[feat_toks[f]][bs]

        # --- corruption masks (paired: same masks applied to both arms) ------
        occ_blocks = rng.choice(P_BLOCKS, size=K_OCC, replace=False)
        struct_mask = np.ones(N_DIM, dtype=np.float32)
        for b in occ_blocks:
            struct_mask[_block_slice(int(b))] = 0.0
        n_iid = int(round(F_OCC * N_DIM))
        iid_idx = rng.choice(N_DIM, size=n_iid, replace=False)
        iid_mask = np.ones(N_DIM, dtype=np.float32)
        iid_mask[iid_idx] = 0.0

        # --- STRUCTURED-occluded recoveries (headline) -----------------------
        Ep_s = E_p * struct_mask
        En_s = E_n * struct_mask
        h_persist.update(np.ascontiguousarray(Ep_s).tobytes())
        h_naive.update(np.ascontiguousarray(En_s).tobytes())
        ub_ps = role_id * Ep_s
        if _cleanup_argmax(ub_ps, cb_full, slice(0, N_DIM), rng) == id_tok:
            hits["ps"] += 1
        if _cleanup_argmax(En_s, cb_blk0, blk0, rng) == id_tok:
            hits["ns"] += 1

        # --- I.I.D.-occluded recoveries (diagnostic: expect no gap) ----------
        Ep_i = E_p * iid_mask
        En_i = E_n * iid_mask
        ub_pi = role_id * Ep_i
        if _cleanup_argmax(ub_pi, cb_full, slice(0, N_DIM), rng) == id_tok:
            hits["pi"] += 1
        if _cleanup_argmax(En_i, cb_blk0, blk0, rng) == id_tok:
            hits["ni"] += 1

        # --- NO-occlusion sanity (machinery must work) -----------------------
        ub_p0 = role_id * E_p
        if _cleanup_argmax(ub_p0, cb_full, slice(0, N_DIM), rng) == id_tok:
            hits["ps0"] += 1
        if _cleanup_argmax(E_n, cb_blk0, blk0, rng) == id_tok:
            hits["ns0"] += 1

        # --- MUST-FAIL controls (occluded, structured; expect ~chance) -------
        # REMOVED: actively subtract the identity binding / zero the id block.
        Ep_rem = (E_p - role_id * cb[id_tok]) * struct_mask
        ub_prem = role_id * Ep_rem
        if _cleanup_argmax(ub_prem, cb_full, slice(0, N_DIM), rng) == id_tok:
            hits["prem"] += 1
        En_rem = E_n.copy()
        En_rem[blk0] = 0.0
        En_rem = En_rem * struct_mask
        if _cleanup_argmax(En_rem, cb_blk0, blk0, rng) == id_tok:
            hits["nrem"] += 1
        # SCRAMBLED: bind id_tok to a WRONG role (role index != 0).
        wrong_role = roles[1 + int(rng.integers(0, F_FEAT))]
        E_scr = wrong_role * cb[id_tok]
        for f in range(F_FEAT):
            E_scr = E_scr + roles[f + 1] * cb[feat_toks[f]]
        ub_pscr = role_id * (E_scr * struct_mask)
        if _cleanup_argmax(ub_pscr, cb_full, slice(0, N_DIM), rng) == id_tok:
            hits["pscr"] += 1

    acc = {k: hits[k] / m_trials for k in hits}
    acc["hash_persist"] = h_persist.hexdigest()[:16]
    acc["hash_naive"] = h_naive.hexdigest()[:16]
    return acc


def _ratio(num: float, den: float) -> float:
    return min(max(num, 0.0) / max(den, EPS), RATIO_CAP)


def run_one_seed(seed: int, m_trials: int) -> dict:
    """Run all conditions for one seed; return recoveries, ratio, verdict."""
    t0 = time.perf_counter()
    rng = _rng(seed)
    cb = _bipolar(rng, V_TOK, N_DIM)
    roles = _bipolar(rng, P_BLOCKS, N_DIM)   # role 0 = identity role; 1..F = features
    acc = _run_trials(_rng(seed + 1), cb, roles, m_trials)

    ratio_struct = _ratio(acc["ps"], acc["ns"])
    ratio_iid = _ratio(acc["pi"], acc["ni"])
    gap_struct = acc["ps"] - acc["ns"]
    occ_effect = acc["ns0"] - acc["ns"]       # structured occlusion degrades naive
    control_max = max(acc["prem"], acc["nrem"], acc["pscr"])
    persist_control_max = max(acc["prem"], acc["pscr"])

    control_ok = control_max <= CHANCE + REMOVED_MARGIN
    control_leak = persist_control_max > CHANCE + LEAK_MARGIN
    naive_in_band = NAIVE_BAND_LO <= acc["ns"] <= NAIVE_BAND_HI
    occ_effective = occ_effect >= MIN_EFFECT

    hp = (ratio_struct >= HP_RATIO and acc["ps"] >= HP_PERSIST_FLOOR
          and gap_struct >= MIN_EFFECT and control_ok and naive_in_band)
    hf = control_leak or (occ_effective and ratio_struct <= HFAIL_RATIO)
    if hp:
        seed_verdict = "HARD_PASS"
    elif hf:
        seed_verdict = "HARD_FAIL"
    elif not occ_effective:
        seed_verdict = "INCONCLUSIVE_NO_OCCLUSION_EFFECT"
    else:
        seed_verdict = "MIDDLE_BAND"

    return {
        "seed": seed, "N": N_DIM, "run_mode": None,   # run_mode stamped by caller
        "m_trials": m_trials,
        "rec_persist_structured": acc["ps"], "rec_naive_structured": acc["ns"],
        "rec_persist_iid": acc["pi"], "rec_naive_iid": acc["ni"],
        "rec_persist_no_occ": acc["ps0"], "rec_naive_no_occ": acc["ns0"],
        "rec_persist_removed": acc["prem"], "rec_naive_removed": acc["nrem"],
        "rec_persist_scrambled": acc["pscr"],
        "ratio_structured": ratio_struct, "ratio_iid": ratio_iid,
        "gap_structured": gap_struct, "occ_effect_naive": occ_effect,
        "control_max": control_max, "persist_control_max": persist_control_max,
        "control_ok": bool(control_ok), "control_leak": bool(control_leak),
        "naive_in_band": bool(naive_in_band), "occ_effective": bool(occ_effective),
        "hash_persist": acc["hash_persist"], "hash_naive": acc["hash_naive"],
        "seed_verdict": seed_verdict,
        "chance": CHANCE,
        "elapsed_s": time.perf_counter() - t0,
    }


# ----------------------------------------------------------------------------
# Aggregation + verdict.
# ----------------------------------------------------------------------------
def _aggregate(per_seed: list, expected_n_units: int) -> dict:
    n = len(per_seed)
    if n < expected_n_units:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": (f"CARDINALITY_BREACH: {n} of {expected_n_units} "
                            f"seeds completed"),
            "summary": "CARDINALITY_BREACH",
            "n_units": n, "expected_n_units": expected_n_units,
        }

    def _mean(key):
        return float(np.mean([s[key] for s in per_seed]))

    m_ps, m_ns = _mean("rec_persist_structured"), _mean("rec_naive_structured")
    m_pi, m_ni = _mean("rec_persist_iid"), _mean("rec_naive_iid")
    m_prem = _mean("rec_persist_removed")
    m_nrem = _mean("rec_naive_removed")
    m_pscr = _mean("rec_persist_scrambled")
    m_ns0 = _mean("rec_naive_no_occ")
    m_ps0 = _mean("rec_persist_no_occ")
    ratio_struct = _ratio(m_ps, m_ns)
    ratio_iid = _ratio(m_pi, m_ni)
    gap = m_ps - m_ns
    occ_effect = m_ns0 - m_ns
    control_max = max(m_prem, m_nrem, m_pscr)
    persist_control_max = max(m_prem, m_pscr)

    control_ok = control_max <= CHANCE + REMOVED_MARGIN
    control_leak = persist_control_max > CHANCE + LEAK_MARGIN
    naive_in_band = NAIVE_BAND_LO <= m_ns <= NAIVE_BAND_HI
    occ_effective = occ_effect >= MIN_EFFECT

    n_hp = sum(1 for s in per_seed if s["seed_verdict"] == "HARD_PASS")
    n_hf = sum(1 for s in per_seed if s["seed_verdict"] == "HARD_FAIL")

    mean_hp = (ratio_struct >= HP_RATIO and m_ps >= HP_PERSIST_FLOOR
               and gap >= MIN_EFFECT and control_ok and naive_in_band)
    mean_hf = control_leak or (occ_effective and ratio_struct <= HFAIL_RATIO)

    if mean_hp and n_hp >= (n + 1) // 2:
        verdict = "HARD_PASS"
    elif mean_hf and (control_leak or n_hf >= (n + 1) // 2):
        verdict = "HARD_FAIL"
    elif not occ_effective:
        verdict = "INCONCLUSIVE_NO_OCCLUSION_EFFECT"
    else:
        verdict = "MIDDLE_BAND"

    msg = (f"{verdict}: ratio_struct={ratio_struct:.2f} "
           f"(persist={m_ps:.3f} vs naive={m_ns:.3f}, gap={gap:.3f}) ; "
           f"ratio_iid={ratio_iid:.2f} (persist={m_pi:.3f} vs naive={m_ni:.3f}, "
           f"no-gap-expected) ; must-fail controls removed_p={m_prem:.3f} "
           f"removed_n={m_nrem:.3f} scrambled_p={m_pscr:.3f} (chance={CHANCE:.3f}, "
           f"control_ok={control_ok}, leak={control_leak}) ; "
           f"no-occ persist={m_ps0:.3f} naive={m_ns0:.3f} ; occ_effect={occ_effect:.3f} ; "
           f"seeds HP={n_hp}/{n} HF={n_hf}/{n} ; HP_RATIO={HP_RATIO} "
           f"HFAIL_RATIO={HFAIL_RATIO} MIN_EFFECT={MIN_EFFECT} "
           f"HP_PERSIST_FLOOR={HP_PERSIST_FLOOR}")

    gate_claims = [
        record_gate("ratio_structured_ge_2", ratio_struct, HP_RATIO, ">="),
        record_gate("persist_structured_ge_floor", m_ps, HP_PERSIST_FLOOR, ">="),
        record_gate("gap_structured_ge_min_effect", gap, MIN_EFFECT, ">="),
        record_gate("naive_in_band_lo", m_ns, NAIVE_BAND_LO, ">="),
        record_gate("naive_in_band_hi", m_ns, NAIVE_BAND_HI, "<="),
        record_gate("control_removed_persist_le_margin", m_prem,
                    CHANCE + REMOVED_MARGIN, "<="),
        record_gate("control_scrambled_persist_le_margin", m_pscr,
                    CHANCE + REMOVED_MARGIN, "<="),
        record_gate("occ_effect_naive_ge_min_effect", occ_effect, MIN_EFFECT, ">="),
    ]

    return {
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "n_units": n, "expected_n_units": expected_n_units,
        "mean_rec_persist_structured": m_ps, "mean_rec_naive_structured": m_ns,
        "mean_rec_persist_iid": m_pi, "mean_rec_naive_iid": m_ni,
        "mean_rec_persist_removed": m_prem, "mean_rec_naive_removed": m_nrem,
        "mean_rec_persist_scrambled": m_pscr,
        "mean_rec_persist_no_occ": m_ps0, "mean_rec_naive_no_occ": m_ns0,
        "mean_ratio_structured": ratio_struct, "mean_ratio_iid": ratio_iid,
        "mean_gap_structured": gap, "mean_occ_effect": occ_effect,
        "control_ok": bool(control_ok), "control_leak": bool(control_leak),
        "n_seeds_hard_pass": n_hp, "n_seeds_hard_fail": n_hf,
        "chance": CHANCE,
        "per_seed": per_seed,
        "gate_claims": gate_claims,
        "config": {
            "N_DIM": N_DIM, "F_FEAT": F_FEAT, "P_BLOCKS": P_BLOCKS,
            "B_WIDTH": B_WIDTH, "V_TOK": V_TOK, "K_OCC": K_OCC, "F_OCC": F_OCC,
            "HP_RATIO": HP_RATIO, "HFAIL_RATIO": HFAIL_RATIO,
            "HP_PERSIST_FLOOR": HP_PERSIST_FLOOR, "MIN_EFFECT": MIN_EFFECT,
            "REMOVED_MARGIN": REMOVED_MARGIN, "LEAK_MARGIN": LEAK_MARGIN,
        },
    }


# ----------------------------------------------------------------------------
# Runner scaffolding: start marker, crash metrics.
# ----------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ----------------------------------------------------------------------------
# Run modes.
# ----------------------------------------------------------------------------
def _run(run_mode: str) -> dict:
    assert N_DIM % P_BLOCKS == 0, "N_DIM must be divisible by P_BLOCKS"
    if run_mode == "smoke":
        seeds, m_trials = SEEDS_SMOKE, M_TRIALS_SMOKE
    else:
        seeds, m_trials = SEEDS_FULL, M_TRIALS_FULL
    expected = len(seeds)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir_str = str(out_dir)
    _write_start_marker(out_dir_str, run_mode, expected)

    run_config = {"N": N_DIM, "run_mode": run_mode, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(list(seeds), out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(seeds)} seeds complete; running {remaining}",
          flush=True)

    t0 = time.perf_counter()
    with CellHeartbeat(out_dir_str, total_units=len(seeds), interval_s=30) as hb:
        for i, seed in enumerate(remaining):
            res = run_one_seed(seed, m_trials)
            res["run_mode"] = run_mode
            res["config_version"] = f"ANCHOR={ANCHOR_NAME},N={N_DIM},run_mode={run_mode}"
            write_partial(out_dir, seed, res)
            hb.tick(i, extra={"seed": seed, "seed_verdict": res["seed_verdict"],
                              "ratio": round(res["ratio_structured"], 2)})
            print(f"[progress] seed={seed} verdict={res['seed_verdict']} "
                  f"ratio_struct={res['ratio_structured']:.2f} "
                  f"persist={res['rec_persist_structured']:.3f} "
                  f"naive={res['rec_naive_structured']:.3f} "
                  f"removed_p={res['rec_persist_removed']:.3f} "
                  f"elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    agg_all = aggregate_partials(out_dir, list(seeds), run_config=run_config)
    per_seed = [agg_all[str(s)] for s in seeds if str(s) in agg_all]
    metrics = _aggregate(per_seed, expected)
    metrics["run_mode"] = run_mode
    metrics["elapsed_s"] = time.perf_counter() - t0
    metrics["ts_iso"] = datetime.now(timezone.utc).isoformat()

    # ---- SMOKE gates: discriminator must fire + must-fail control guard -----
    if run_mode == "smoke" and per_seed:
        s0 = per_seed[0]
        # META_RULE_AF: the two arms must be bit-distinct (arms-must-differ).
        assert s0["hash_persist"] != s0["hash_naive"], \
            "META_RULE_AF: persist and naive structured-occluded scenes bit-identical"
        metrics["arms_differ_verified"] = True
        # Machinery sanity: both arms recover ~perfectly with NO occlusion.
        no_occ_ok = (s0["rec_persist_no_occ"] >= NO_OCC_FLOOR
                     and s0["rec_naive_no_occ"] >= NO_OCC_FLOOR)
        metrics["no_occ_sanity_ok"] = bool(no_occ_ok)
        # Vacuous-guard: the must-fail control must NOT recover (leak == smoke-fail).
        assert_discriminator_fires(
            bool(s0["control_leak"]),
            control_name="removed_or_scrambled_entity",
            headline_name="persistence_recovery",
            run_mode="smoke",
            remedy="the actively-removed/scrambled entity is being 'recovered' "
                   "above chance -> the persistence recovery is a tautology/leak; "
                   "fix the removed-binding subtraction or the cleanup readout")
        # Baseline-in-band (META_RULE_AG): naive is a real, non-degenerate baseline.
        metrics["baseline_in_band"] = bool(s0["naive_in_band"])
        # Discriminator fires at smoke scale (structured occlusion degrades naive
        # AND persistence beats it): else do NOT dispatch FULL.
        smoke_fires = (s0["occ_effective"]
                       and s0["rec_persist_structured"] >= HP_PERSIST_FLOOR
                       and s0["ratio_structured"] >= 1.8
                       and s0["gap_structured"] >= MIN_EFFECT)
        metrics["smoke_discriminator_fires"] = bool(smoke_fires)
        if not (smoke_fires and no_occ_ok and s0["naive_in_band"]):
            metrics["verdict"] = "SMOKE_GATE_FAIL_DISCRIMINATOR_INERT"
            metrics["verdict_msg"] = (
                "SMOKE_GATE_FAIL: object-permanence discriminator did not fire "
                f"cleanly at smoke scale (occ_effective={s0['occ_effective']} "
                f"persist={s0['rec_persist_structured']:.3f} "
                f"ratio={s0['ratio_structured']:.2f} gap={s0['gap_structured']:.3f} "
                f"naive_in_band={s0['naive_in_band']} no_occ_ok={no_occ_ok}); "
                "re-spec regime before FULL dispatch")
            metrics["summary"] = metrics["verdict_msg"]

    gate_claims = metrics.pop("gate_claims", None)
    write_metrics(out_dir, metrics, results=per_seed, gate_claims=gate_claims)
    print(f"[done] run_mode={run_mode} verdict={metrics['verdict']}", flush=True)
    print(metrics["verdict_msg"], flush=True)
    return metrics


def self_test() -> int:
    """Fast correctness + telemetry-sensitivity checks (no FULL/SMOKE output path)."""
    print("[selftest] object-permanence binding-stability primitives", flush=True)
    # T1: bind/unbind self-inverse (bipolar) + block partition exact.
    N_T, V_T, P_T = 512, 16, 8
    B_T = N_T // P_T
    rng = _rng(0)
    cb = _bipolar(rng, V_T, N_T)
    a, b = cb[0], cb[1]
    assert np.allclose((a * b) * b, a), "bipolar unbind not self-inverse"
    assert N_T % P_T == 0, "block partition not exact"
    print("[selftest] T1 PASS: bind/unbind self-inverse + exact block partition",
          flush=True)

    # T2: analytical naive-structured recovery ~ (P-k)/P (block-survival prob).
    #   THEORETICAL@block survival = C(P-1,k)/C(P,k) = (P-k)/P = 3/8 = 0.375.
    r = run_one_seed(7, 300)
    exp_naive = (P_BLOCKS - K_OCC) / P_BLOCKS
    assert abs(r["rec_naive_structured"] - exp_naive) < 0.10, (
        f"naive_structured={r['rec_naive_structured']:.3f} deviates from "
        f"analytical (P-k)/P={exp_naive:.3f}")
    print(f"[selftest] T2 PASS: naive_structured={r['rec_naive_structured']:.3f} "
          f"~ (P-k)/P={exp_naive:.3f}", flush=True)

    # T3: persistence beats naive under STRUCTURED occlusion; controls at chance;
    #     no-occlusion machinery works; i.i.d. shows NO gap (structural scope).
    print(f"[selftest] seed7 persist_struct={r['rec_persist_structured']:.3f} "
          f"naive_struct={r['rec_naive_structured']:.3f} "
          f"ratio_struct={r['ratio_structured']:.2f} | "
          f"persist_iid={r['rec_persist_iid']:.3f} naive_iid={r['rec_naive_iid']:.3f} "
          f"ratio_iid={r['ratio_iid']:.2f} | "
          f"removed_p={r['rec_persist_removed']:.3f} "
          f"scrambled_p={r['rec_persist_scrambled']:.3f} chance={CHANCE:.3f} | "
          f"no_occ_p={r['rec_persist_no_occ']:.3f} no_occ_n={r['rec_naive_no_occ']:.3f}",
          flush=True)
    assert r["rec_persist_no_occ"] >= NO_OCC_FLOOR, "persist no-occ machinery broken"
    assert r["rec_naive_no_occ"] >= NO_OCC_FLOOR, "naive no-occ machinery broken"
    assert r["rec_persist_structured"] >= HP_PERSIST_FLOOR, \
        "persist_structured below floor (mechanism not robust to occlusion)"
    assert r["ratio_structured"] >= 1.8, \
        "structured ratio below smoke-fires threshold (no persistence advantage)"
    # must-fail controls at chance (not recovering a removed/scrambled entity).
    assert r["rec_persist_removed"] <= CHANCE + REMOVED_MARGIN, \
        "REMOVED control recovers above chance (tautology/leak)"
    assert r["rec_persist_scrambled"] <= CHANCE + REMOVED_MARGIN, \
        "SCRAMBLED control recovers above chance (binding-agnostic leak)"
    assert not r["control_leak"], "must-fail control leaked"
    # structural specificity: i.i.d. occlusion should NOT give a large gap.
    assert r["ratio_iid"] < 1.5, \
        "i.i.d. occlusion shows a large gap (advantage is not structural-specific)"
    print("[selftest] T3 PASS: persistence beats naive under STRUCTURED occlusion; "
          "controls at chance; i.i.d. shows no gap (structural-specific)", flush=True)

    # T4: telemetry-sensitivity -- perturbing the seed moves the metrics.
    r2 = run_one_seed(17, 300)
    assert r["hash_persist"] != r2["hash_persist"], \
        "two seeds gave identical persist scenes (not telemetry-sensitive)"
    assert (r["rec_naive_structured"], r["rec_persist_structured"]) != \
           (r2["rec_naive_structured"], r2["rec_persist_structured"]), \
        "two seeds gave identical recoveries (not telemetry-sensitive)"
    # arms bit-distinct.
    assert r["hash_persist"] != r["hash_naive"], "persist==naive arms bit-identical"
    print(f"[selftest] T4 PASS: telemetry-sensitive (seed17 "
          f"persist={r2['rec_persist_structured']:.3f} "
          f"naive={r2['rec_naive_structured']:.3f})", flush=True)
    print("[selftest] ALL PASS", flush=True)
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    run_mode = "smoke" if args.smoke else "full"
    out_dir = get_output_dir(ANCHOR_NAME)
    try:
        _run(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(str(out_dir), e)
        raise


if __name__ == "__main__":
    main()
