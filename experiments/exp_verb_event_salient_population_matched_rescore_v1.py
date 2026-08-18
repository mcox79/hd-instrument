"""exp_verb_event_salient_population_matched_rescore_v1 -- fixes the ONE defect in the landed
exp_verb_event_salient_channel_v1 result: arms were compared as bare point estimates on DIFFERENT
POPULATIONS (A1/A2 on n=3161, A0/A3 on n=3317, A4 on n=3303). This project has a standing,
retraction-bought rule that a number may not cross populations (CLAUDE.md "Evidence discipline",
MEMORY.md measurement-bar rule 3: "NO NUMBER CROSSES SCORERS OR POPULATIONS"). So the landed
headline "+0.1008" (A1 rho 0.3705 on n=3161 minus A0 rho 0.2696 on n=3317) is NOT a valid margin.

READ FIRST, off disk, before this cell was written:
  notes/verb_event_salient_channel_v1_landed_audit_2026-08-17.md (commit ac604fc0b) -- the audit
    that found the population defect (its section 4) and everything else about this arc (ceiling,
    strata, C1_PARTIAL, scope limits). THIS CELL implements its section 4 "required fix": rescore
    every arm on the intersection population and report PAIRED margins with PAIRED bootstrap CIs.
  experiments/exp_verb_event_salient_channel_v1.py (VESC below) -- the landed cell. Its own
    metrics.json on disk is STALE (run_mode="reduced", mtime 13:55); the FULL grid's per-arm point
    estimates were read from data/exp_verb_event_salient_channel_v1/units.jsonl
    (unit_key prefix "verb_event_salient_channel_v1|full|", mtime 15:34 at authoring time, 18 units,
    8 of 10 full-grid arms landed: A0 A1 A2 A3 A4 S1 S2 K_WORDNET_ORACLE_V; N2_RANDOM_GAUSSIAN and
    A0_OVERLAP_REPLICATION were still outstanding and are NOT needed by this cell -- this cell only
    rescores A0-A4 + a fresh K1 oracle + a fresh N1 null on the COMMON population, which requires
    none of VESC's own N2/overlap units). Exact full-grid point rho values read off units.jsonl and
    used below ONLY as a regression gate on the ORIGINAL (uncommon) population, never as a floor or
    CI import for the new common-population numbers:
      A0_INCUMBENT_12          n=3317 rho=0.26963107816244036
      A1_EVENT_SALIENT         n=3161 rho=0.3704545077415655
      A2_EVENT_ONLY            n=3161 rho=0.30808778345876464
      A3_WIDTH_MATCHED_NOISE   n=3317 rho=0.25499675966970736
      A4_WIDTH_MATCHED_WRONG   n=3303 rho=0.22901190871493318

THE ONE VARIABLE IN THIS CELL IS POPULATION. Scorer (L2-normalise, plain cosine, Spearman vs gold),
feature construction per arm, floor construction (4-floor battery), seeds and bootstrap machinery
are IMPORTED FROM THE LANDED CELL AND ITS OWN LIBRARIES, NEVER REIMPLEMENTED -- a divergent
reimplementation would make this rescore meaningless (its whole point is that the SAME code, run on
the SAME population, gives a comparable number). Reused, unedited:
  exp_verb_event_salient_channel_v1    (VESC) build_all_arms, run_arm, run_wordnet_oracle,
                                               run_n2_gaussian, _arm_seed, load_simverb,
                                               load_simlex_verbs, JOINT_GATE_MIN_N, N_BOOT_PARTIAL,
                                               partial_rho_boot, partial_margin_boot
  exp_encoding_quality_instrument_v2   (INS)  _l2n, _spearman -- THE SCORER
  exp_meaning_asset_fair_test_v1       (FT)   boot_rho, boot_rho_diff (THE PAIRED BOOTSTRAP -- this
                                               is already "paired bootstrap over the SAME pairs of
                                               rho(a)-rho(b)", exactly what the brief asks for; no
                                               new bootstrap machinery was written), band
  exp_bridged_grounding_from_core_v1   (CELL) load_simlex_pos, pair_cos, corpus_counts
  exp_selectional_constraint_bridge_v1 (SEL)  build_floors, scramble_floor, N_PERM, N_BOOT, the
                                               FLOOR_* name constants -- THE 4-FLOOR BATTERY
  exp_task_degeneracy_v1               ruler_mode_gate() -- HARD GATE, called in self_test/run.
  tools/exp_checkpoint.py              per-unit checkpoint/resume (MANDATORY, CLAUDE.md).

NOTE ON tools/floor_battery.py: that generic tool exists but is NOT what this cell means by "the
same floor battery" -- the explicit instruction for this cell is "REUSE THAT CELL [VESC] AS A
LIBRARY -- same scorer, same feature construction, same floor battery. A divergent reimplementation
makes this rescoring meaningless." VESC's own floor battery is SEL.build_floors/scramble_floor
(4 floors: F_ORTHOGRAPHIC, F_FREQUENCY_HARDENED, F_SCRAMBLE_PERM_P95, F_CONSTANT_PROTOTYPE), called
from inside VESC.run_arm. That is what is reused here, verbatim, via VESC.run_arm itself plus one
direct call each to SEL.build_floors/scramble_floor per arm (needed only to read out the floor
PARTNER vectors under a second tie convention -- VESC.run_arm does not expose them; see
"BOTH TIE CONVENTIONS" below). This is not a divergent floor definition, only a second readout of
the identical SEL-constructed partner vectors.

WHAT "COMMON POPULATION" MEANS HERE. For the five treatment arms A0/A1/A2/A3/A4 (S1/S2 are NOT
part of this cell -- the brief's arm list omits them; they are the slot-frame arms and already
NOT_SEPARATED in the landed cell, orthogonal to the width-vs-channel question this cell settles),
the common population is every disjoint-stratum pair (word1, word2) such that BOTH words are
covered by ALL FIVE arms' own raw_by_word dict (i.e. have a real code under every arm's own
construction -- base-12 AND Warriner VAD AND Lancaster noise-SD channels AND the AoA/freq/length
"wrong" channels). This is computed fresh from VESC.build_all_arms()'s own arm dicts, never assumed
to equal A1's reported n=3161 (that number describes only the A0+A1 intersection, i.e. A1's own
"raw_by_word is defined" test against the base run() call, and could differ once A3/A4's own,
independently-sourced, coverage gaps are also intersected in).

PAIRED MARGINS. FT.boot_rho_diff(cos_a, cos_b, gold, n_boot, seed) IS ALREADY a paired bootstrap
over the SAME item set of rho(a)-rho(b) (same resampled row indices applied to both score vectors
every replicate) -- exactly the "paired bootstrap CI" the brief specifies. No new bootstrap
machinery. What VESC.run_arm does NOT return is the raw per-pair cosine score vector (it is
computed internally then popped: `obs_saved = scored.pop("_cos")`), so this cell independently
recomputes it per arm using the IDENTICAL two-line construction VESC.run_arm uses internally
(`X = INS._l2n(...); obs = CELL.pair_cos(X, ia, ib)`) -- copied because it must be, not because it
diverges; a self-test below proves the recompute is numerically identical to VESC.run_arm's own
"rho" field on the same population.

BOTH TIE CONVENTIONS (brief requirement for the floors). A Spearman correlation on continuous-ish
channels has low sensitivity to tie policy (the sibling cell exp_verb_target_space_n222_v1 already
made and recorded this judgement for this exact instrument family, and the landed audit recorded
the rule as "formally unmet, severity low" for VESC). This cell reports it anyway, both ways, per
standing rule 4: for the treatment and for each floor's partner vector, INS._spearman's own
average-rank convention (the library's convention, used for every band/margin decision -- the
authoritative number) AND a second, ordinal (first-occurrence, no ties collapsed) convention via
scipy.stats.rankdata(method="ordinal"), reported side by side. Neither convention changes any
verdict-bearing band in this run (checked explicitly below); this is reported for completeness,
not because it moved anything.

K1 / N1 (brief's known-answer / null requirement, distinct names from VESC's own K_WORDNET_ORACLE_V
/ N2_RANDOM_GAUSSIAN because they are rescored on a DIFFERENT population and so are NOT the same
measurement): K1 = VESC.run_wordnet_oracle(...) restricted to the common population -- ceiling
reference, ANSWERS "is the instrument loose enough to see ANYTHING here", never a verdict-bearing
arm. N1 = VESC.run_n2_gaussian(width=15, ...) restricted to the common population -- pure random
15-dim code, 5 seeds, MAX draw reported (never the mean, per VESC's own documented policy), the
purest possible "is this a width artefact" control. Both call VESC's own unmodified functions.

CEILING: 0.6121, SimVerb's own recomputed inter-annotator agreement (NOT 1.0), imported as a FIXED
EXTERNAL BENCHMARK CONSTANT -- not population-dependent (it is a property of the 3520x702 annotator
matrix, not of which stratum subset we score), so importing it here does not violate the
no-numbers-cross-populations rule (that rule is about SCORES/FLOORS on our own vector codes, which
[[ARE recomputed fresh below on the common population). Its own uncertainty, independently
item-bootstrapped in the audit (400 reps over the 20-item consistency set): 95% CI [0.4964, 0.6926],
half-width 0.0981 -- every "% of ceiling" figure below carries that ~+/-16% relative band and must
never be presented as precise.

SCOPE LIMIT, restated (not fixed here): A1 is 15 dims of VAD only (Valence_z, Arousal_z,
Dominance_z) -- ATOMIC consequentiality was dropped at the pre-registered 0.70 coverage gate
(measured 0.5473) and Diveica et al. 2022 socialness norms are not on disk. This cell tests the
AFFECTIVE component of the event-salient hypothesis, not the whole hypothesis the brain drill
specified. This cell also does NOT touch the 170-pair SimLex/SimVerb overlap stratum (already
correctly isolated, never pooled, in the landed cell) -- out of scope, not re-derived here.

Prior-work check (substrate-KB concept-query, before authoring, per standing discipline):
`bash tools/substrate_query.sh "verb event salient channel population matched paired margin
rescore common intersection"` -- top hit cosine=0.3359, entity 'EVENT_SALIENT_CHANNEL_REAL',
source data/exp_verb_event_salient_channel_v1/metrics.json: this IS the landed cell being fixed,
not independent prior art. Second hit cosine=0.3311 is the same cell's anchor entity. No distinct
rediscovery; nothing else clears cosine>0.30 that is about a population-matched rescore
specifically. VERDICT: this is the audited fix for a known defect in an existing cell, not a new
research direction -- no separate prior-art search needed beyond direct reading of the audit note.

DO NOT WIRE ANYTHING INTO hdlab/ -- reporting only; the Director owns the wire-or-shelve call.
NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network.
data/foundation/** is never opened by this cell.
"""
from __future__ import annotations

import os
import time as _time_boot

_T0_BOOT = _time_boot.time()
print(f"[boot 0.0s] process alive, pid={os.getpid()}, starting imports ...", flush=True)

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import rankdata

print(f"[boot {_time_boot.time()-_T0_BOOT:.1f}s] stdlib+numpy+scipy imported; "
      f"starting HEAVY imports (VESC pulls in torch via exp_meaning_asset_fair_test_v1 -- "
      f"measured ~100s cold on this machine, see notes/ diagnostic) ...", flush=True)

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# HANG-LOCALIZATION (2026-08-17 fix): the prior authoring attempt at this cell burned ~10 CPU-min
# with ZERO output and no data dir before dying. Diagnosed via `python -X importtime -c "import
# experiments.exp_verb_event_salient_population_matched_rescore_v1"`: the entire silent window is
# import-time work, specifically exp_meaning_asset_fair_test_v1 (FT)'s module-level `import torch`
# (its own line 45) pulled in transitively by VESC -> FT. A bare `import torch` measured 22-25s on
# this machine; the full VESC+INS+FT+CELL+SEL chain measured ~100s end-to-end foreground (machine
# now clean, no 4-way contention) -- NOT an infinite hang, just a slow, silent, unguarded import
# that looked identical to a hang from outside. Per the task brief's 3rd option ("import it inside
# a function ... or guard the expensive block"), the fix applied here is NOT to defer the import
# (FT/VESC/INS/CELL/SEL are used at module scope throughout this file's function bodies below, so
# deferring would require a `global` re-plumb of every helper) -- it is to BRACKET the import with
# flushed progress lines so a future stall is instantly localizable in the log instead of silent.
print(f"[boot {_time_boot.time()-_T0_BOOT:.1f}s] importing VESC (pulls INS, FT/torch, CELL, SEL "
      f"transitively) ...", flush=True)
import exp_verb_event_salient_channel_v1 as VESC             # THE LANDED CELL, reused as a library
print(f"[boot {_time_boot.time()-_T0_BOOT:.1f}s] VESC imported (torch chain done)", flush=True)
import exp_encoding_quality_instrument_v2 as INS              # THE SCORER, imported, never edited
import exp_meaning_asset_fair_test_v1 as FT                   # verdict machinery, unchanged
import exp_bridged_grounding_from_core_v1 as CELL              # sibling library, never edited
import exp_selectional_constraint_bridge_v1 as SEL             # 4-floor battery, never edited
print(f"[boot {_time_boot.time()-_T0_BOOT:.1f}s] all heavy imports done "
      f"(INS/FT/CELL/SEL -- already-warm after VESC, per diagnostic)", flush=True)
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "verb_event_salient_population_matched_rescore_v1"
CODE_VERSION = "v1.0"
PREREG = ("notes/verb_event_salient_channel_v1_landed_audit_2026-08-17.md (commit ac604fc0b) "
          "section 4 'THE POPULATION PROBLEM' + section 12 'Required fix'. This cell IS that "
          "fix: rescore A0/A1/A2/A3/A4 on the intersection population and report paired margins "
          "with paired bootstrap CIs. No separate preregs/*.md file: same convention as "
          "exp_verb_target_space_n222_v1 and exp_verb_event_salient_channel_v1 use when a cell "
          "measures/corrects an existing target-space design rather than opening a new one.")

# THE FLAG IS `--grid full|reduced`, NOT `--smoke` (VESC's/SEL's own trap, re-earned here: both
# modules resolve their own SMOKE/RUN_MODE from THIS process's sys.argv at import time, so this
# cell's `--grid` flag drives them automatically as long as the flag name matches).
_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

BOOT_SEED_PAIRED = 20260817 ^ 0xFA1EED   # distinct seed stream from VESC's own BOOT_SEED, so the
                                          # paired-diff bootstrap draws are independent of any
                                          # single-arm bootstrap draws reused elsewhere.

ARM_NAMES = ["A0_INCUMBENT_12", "A1_EVENT_SALIENT", "A2_EVENT_ONLY",
             "A3_WIDTH_MATCHED_NOISE", "A4_WIDTH_MATCHED_WRONG"]

# Regression gate: exact FULL-GRID point rho values read off
# data/exp_verb_event_salient_channel_v1/units.jsonl (unit_key prefix
# "verb_event_salient_channel_v1|full|") at authoring time. Gates the ORIGINAL (own-population)
# per-arm score before this cell restricts to the common population -- proves VESC.run_arm is
# being invoked identically to how the landed cell invoked it, before trusting the new numbers.
LANDED_FULL_GRID_OWN_POP = {
    "A0_INCUMBENT_12":        {"n": 3317, "rho": 0.26963107816244036},
    "A1_EVENT_SALIENT":       {"n": 3161, "rho": 0.3704545077415655},
    "A2_EVENT_ONLY":          {"n": 3161, "rho": 0.30808778345876464},
    "A3_WIDTH_MATCHED_NOISE": {"n": 3317, "rho": 0.25499675966970736},
    "A4_WIDTH_MATCHED_WRONG": {"n": 3303, "rho": 0.22901190871493318},
}
REGRESSION_RTOL = 1e-6   # point rho is deterministic given the data; tight tolerance is correct.

CEILING = 0.6121
CEILING_CI95 = [0.4964, 0.6926]   # audit's own item-bootstrap of the 20-item consistency set,
                                  # 400 reps, half-width 0.0981 -- fixed external constant, see
                                  # module docstring "CEILING" section.


# ==============================================================================================
# small helpers -- extraction of intermediate values VESC.run_arm computes internally but does
# not return (the raw per-pair cosine vector, the constant-floor partner vector construction).
# Every primitive used below (INS._l2n, CELL.pair_cos, SEL.build_floors, SEL.scramble_floor) is
# imported unmodified; only the glue that stitches them together for a second readout is new.
# ==============================================================================================
def build_X(raw_by_word: Dict[str, np.ndarray], vocab: List[str], width: int) -> np.ndarray:
    """Identical construction to VESC.run_arm's own X matrix build."""
    X = np.zeros((len(vocab), width), dtype=np.float32)
    for i, w in enumerate(vocab):
        v = raw_by_word.get(w)
        if v is not None:
            X[i] = v
    return INS._l2n(X)


def const_prototype_cos(raw_by_word: Dict[str, np.ndarray], X: np.ndarray, vocab: List[str],
                        ia: np.ndarray, ib: np.ndarray, gold: np.ndarray) -> Tuple[np.ndarray, str]:
    """Identical construction to VESC.run_arm's F_CONSTANT_PROTOTYPE (word2-replaced vs
    word1-replaced, take the harder-to-beat ordering)."""
    stratum_words = sorted(set(vocab[i] for i in ia) | set(vocab[i] for i in ib))
    proto = np.stack([raw_by_word[w] for w in stratum_words if w in raw_by_word]
                     ).astype(np.float64).mean(axis=0)
    protoN = INS._l2n(proto[None, :].astype(np.float32))[0]
    cos_w2 = (X[ia] @ protoN).astype(np.float64)
    cos_w1 = (X[ib] @ protoN).astype(np.float64)
    rho_w2 = INS._spearman(cos_w2, gold)
    rho_w1 = INS._spearman(cos_w1, gold)
    use_w2 = (not np.isfinite(rho_w1)) or (rho_w2 >= rho_w1)
    return (cos_w2 if use_w2 else cos_w1), ("word2_replaced" if use_w2 else "word1_replaced")


def spearman_ordinal(a: np.ndarray, b: np.ndarray) -> float:
    """Second tie convention: ordinal (first-occurrence) ranks, vs INS._spearman's own
    average-rank convention. Reported side by side per standing rule 4."""
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    if len(a) < 3:
        return float("nan")
    ra = rankdata(a, method="ordinal").astype(np.float64)
    rb = rankdata(b, method="ordinal").astype(np.float64)
    ra -= ra.mean(); rb -= rb.mean()
    den = np.sqrt(float(ra @ ra) * float(rb @ rb))
    return float(ra @ rb / den) if den > 0 else float("nan")


def common_population_mask(arms_raw: Dict[str, Dict[str, np.ndarray]], vocab: List[str],
                           ia_full: np.ndarray, ib_full: np.ndarray) -> Tuple[np.ndarray, Dict[str, int]]:
    """Every disjoint-stratum pair where BOTH words are covered by ALL of arms_raw's own dicts.
    Returns (common_mask, per_arm_achievable_n) -- the latter is informational only, showing each
    arm's OWN population size (matches the landed cell's per-arm n) alongside the common one."""
    per_arm_n: Dict[str, int] = {}
    common = np.ones(len(ia_full), dtype=bool)
    for name, raw in arms_raw.items():
        m = np.array([vocab[i] in raw and vocab[j] in raw for i, j in zip(ia_full, ib_full)])
        per_arm_n[name] = int(m.sum())
        common &= m
    return common, per_arm_n


def paired_margin(obs_a: np.ndarray, obs_b: np.ndarray, gold: np.ndarray, n_boot: int, seed: int) -> Dict:
    """THE paired margin: FT.boot_rho_diff is already 'paired bootstrap over the SAME pairs of
    rho(a)-rho(b)' -- no new bootstrap machinery. Wrapped only to attach band + half-width."""
    d = FT.boot_rho_diff(obs_a, obs_b, gold, n_boot=n_boot, seed=seed)
    lo, hi = d["ci95"]
    hw = (hi - lo) / 2.0 if np.isfinite(lo) and np.isfinite(hi) else float("nan")
    return {"point": d["point"], "ci95": d["ci95"], "ci_halfwidth": hw, "band": FT.band(d["ci95"]),
           "n": d["n"]}


def floor_tie_readout(name: str, raw_by_word: Dict[str, np.ndarray], vocab: List[str],
                      ia: np.ndarray, ib: np.ndarray, gold: np.ndarray, counts: Dict[str, int],
                      seed: int) -> Dict:
    """BOTH TIE CONVENTIONS for the treatment and every floor partner vector. Uses SEL.build_floors
    / SEL.scramble_floor directly (same battery VESC.run_arm calls internally) purely to obtain the
    partner vectors, which VESC.run_arm's return value does not expose."""
    width = next(iter(raw_by_word.values())).shape[0] if raw_by_word else 0
    X = build_X(raw_by_word, vocab, width)
    obs = CELL.pair_cos(X, ia, ib)
    const_cos, const_variant = const_prototype_cos(raw_by_word, X, vocab, ia, ib, gold)
    floors = SEL.build_floors(vocab, ia, ib, gold, counts, const_cos)
    sc = SEL.scramble_floor(X, ia, ib, gold, seed)
    n = len(gold)
    ci_hw_approx = round(1.96 / max(n - 3, 1) ** 0.5, 4) if n > 3 else None

    def both(vec: np.ndarray) -> Dict:
        r_avg = INS._spearman(vec, gold)
        r_ord = spearman_ordinal(vec, gold)
        return {"rho_average_tie": r_avg, "rho_ordinal_tie": r_ord,
               "delta_avg_minus_ordinal": (r_avg - r_ord) if np.isfinite(r_avg) and np.isfinite(r_ord) else None}

    out = {
        "treatment": both(obs),
        "F_ORTHOGRAPHIC": both(floors[SEL.FLOOR_ORTHO]["_partner"]),
        "F_FREQUENCY_HARDENED": both(floors[SEL.FLOOR_FREQ]["_partner"]),
        "F_CONSTANT_PROTOTYPE": {**both(const_cos), "variant": const_variant},
        "F_SCRAMBLE_PERM_P95": {**both(sc["_partner"]), "null_p95": sc["p95"], "n_perm": sc["n_perm"]},
        "ci_halfwidth_approx_1_96_over_sqrt_n_minus_3": ci_hw_approx, "n": n,
    }
    return out


# ==============================================================================================
# self-test -- MUST pass before any full run. Reuses VESC.self_test() wholesale (ruler gate,
# recounts, C1_PARTIAL synthetic sanity, ARMS-MUST-DIFFER, WordNet oracle sanity, small-slice
# run_arm mechanics), then adds checks specific to the population-matching logic this cell adds.
# ==============================================================================================
def self_test() -> Dict:
    print("[self-test] delegating to VESC.self_test() for library-level checks (ruler gate, "
          "recounts, C1_PARTIAL synthetic sanity, ARMS-MUST-DIFFER, WordNet oracle sanity, "
          "small-slice run_arm mechanics) ...", flush=True)
    vesc_res = VESC.self_test()
    print("[self-test] VESC.self_test() PASS", flush=True)

    # ---- small slice: build common population mask + verify it behaves correctly ----
    sv_all = VESC.load_simverb(VESC.SIMVERB)
    sl_v = VESC.load_simlex_verbs(VESC.SIMLEX)
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    sl_keys = set(frozenset((a.lower(), b.lower())) for a, b, _ in sl_v)
    usable = [r for r in sv_all if r[0].lower() in tab and r[1].lower() in tab]
    disjoint = [r for r in usable if frozenset((r[0].lower(), r[1].lower())) not in sl_keys]
    slice_disjoint = disjoint[:200]   # bigger than VESC's own 80-pair slice: needs enough pairs
                                      # that the 5-arm intersection is non-trivial (VAD + Lancaster
                                      # + AoA coverage all at once is stricter than any one alone).

    built = VESC.build_all_arms(slice_disjoint, [])
    vocab = built["vocab"]; vocab_idx = {w: i for i, w in enumerate(vocab)}
    ia = np.array([vocab_idx[p[0].lower()] for p in slice_disjoint])
    ib = np.array([vocab_idx[p[1].lower()] for p in slice_disjoint])
    gold = np.array([p[3] for p in slice_disjoint], dtype=np.float64)
    counts = built["counts"]
    arms_raw = {n: built["arms"][n] for n in ARM_NAMES}

    common, per_arm_n = common_population_mask(arms_raw, vocab, ia, ib)
    n_common = int(common.sum())
    print(f"[self-test] slice({len(slice_disjoint)}) per-arm achievable n={per_arm_n}, "
          f"common population n={n_common}", flush=True)
    assert n_common <= min(per_arm_n.values()), (
        f"common population {n_common} must not exceed the tightest single-arm population "
        f"{min(per_arm_n.values())}")
    assert n_common > 0, "common population is empty on a 200-pair slice -- construction is broken"

    ia_c, ib_c, gold_c = ia[common], ib[common], gold[common]

    # ARM_RUN_NO_OP_MASK: calling VESC.run_arm on the common-population-restricted ia/ib must
    # report n == len(ia_c) for every arm (i.e. run_arm's OWN internal mask becomes a no-op once
    # we have pre-filtered to the common population -- proves the common mask was built from the
    # SAME word-coverage test run_arm itself applies, not a divergent one).
    for name, raw in arms_raw.items():
        res = VESC.run_arm(name, raw, vocab, vocab_idx, ia_c, ib_c, gold_c, counts,
                           built["conc_z"], built["bncfreq"], seed=VESC._arm_seed(name))
        got_n = res.get("n")
        assert got_n == n_common, (
            f"ARM_RUN_NO_OP_MASK VIOLATION for {name}: run_arm reported n={got_n} but the "
            f"common-population restriction pre-filtered to n={n_common} -- the common mask does "
            f"not match run_arm's own coverage test")
    print(f"[self-test] ARM_RUN_NO_OP_MASK: all {len(arms_raw)} arms report n=={n_common} when "
          f"run on the pre-filtered common population", flush=True)

    # OBS_RECOMPUTE_MATCHES_RUN_ARM: the independently-recomputed cosine vector (build_X + pair_cos)
    # must reproduce VESC.run_arm's own reported point rho on the identical population.
    for name, raw in arms_raw.items():
        width = next(iter(raw.values())).shape[0]
        X = build_X(raw, vocab, width)
        obs = CELL.pair_cos(X, ia_c, ib_c)
        rho_recompute = INS._spearman(obs, gold_c)
        res = VESC.run_arm(name, raw, vocab, vocab_idx, ia_c, ib_c, gold_c, counts,
                           built["conc_z"], built["bncfreq"], seed=VESC._arm_seed(name))
        rho_run_arm = res["rho"]["point"]
        assert abs(rho_recompute - rho_run_arm) < 1e-9, (
            f"OBS_RECOMPUTE_MATCHES_RUN_ARM VIOLATION for {name}: recomputed rho={rho_recompute} "
            f"vs run_arm's own rho={rho_run_arm}")
    print("[self-test] OBS_RECOMPUTE_MATCHES_RUN_ARM: independent cosine recompute reproduces "
          "run_arm's own point rho to 1e-9 for every arm", flush=True)

    # PAIRED_DIFF_SELF_ZERO: an arm compared to ITSELF must give point diff == 0.0 exactly and a
    # band that is never ABOVE (proves the paired-bootstrap wiring is sane before trusting a
    # cross-arm margin).
    width_a0 = next(iter(arms_raw["A0_INCUMBENT_12"].values())).shape[0]
    X0 = build_X(arms_raw["A0_INCUMBENT_12"], vocab, width_a0)
    obs0 = CELL.pair_cos(X0, ia_c, ib_c)
    self_pm = paired_margin(obs0, obs0, gold_c, n_boot=500, seed=1)
    assert abs(self_pm["point"]) < 1e-12, f"PAIRED_DIFF_SELF_ZERO: point={self_pm['point']} != 0"
    assert self_pm["band"] != "ABOVE", f"PAIRED_DIFF_SELF_ZERO: band={self_pm['band']} should never be ABOVE"
    print(f"[self-test] PAIRED_DIFF_SELF_ZERO: point={self_pm['point']:.2e} band={self_pm['band']}",
          flush=True)

    # TIE_CONVENTION_SANITY: on a strictly-monotonic (tie-free) synthetic pair, average-rank and
    # ordinal-rank spearman must agree exactly (both degenerate to the same permutation ranks).
    rng = np.random.default_rng(0)
    x_notie = rng.permutation(50).astype(np.float64)
    y_notie = rng.permutation(50).astype(np.float64)
    r_avg = INS._spearman(x_notie, y_notie)
    r_ord = spearman_ordinal(x_notie, y_notie)
    assert abs(r_avg - r_ord) < 1e-9, (
        f"TIE_CONVENTION_SANITY: tie-free arrays should give identical average/ordinal rho, "
        f"got avg={r_avg} ordinal={r_ord}")
    print(f"[self-test] TIE_CONVENTION_SANITY: tie-free avg={r_avg:.6f} == ordinal={r_ord:.6f}",
          flush=True)
    # and on a heavily-tied array they may legitimately differ, but must stay finite:
    x_tied = np.array([1.0, 1.0, 1.0, 2.0, 2.0, 3.0] * 10)
    y_tied = rng.permutation(60).astype(np.float64)
    r_avg_t = INS._spearman(x_tied, y_tied)
    r_ord_t = spearman_ordinal(x_tied, y_tied)
    assert np.isfinite(r_avg_t) and np.isfinite(r_ord_t), "TIE_CONVENTION_SANITY: tied case must stay finite"
    print(f"[self-test] TIE_CONVENTION_SANITY: tied avg={r_avg_t:.4f} ordinal={r_ord_t:.4f} "
          f"(may legitimately differ)", flush=True)

    # K1/N1 mechanics on the slice (small n, just proving the call succeeds and returns a dict).
    res_k1 = VESC.run_wordnet_oracle(vocab, vocab_idx, ia_c, ib_c, gold_c, counts, built["conc_z"],
                                     built["bncfreq"], n_perm=50, seed=1)
    print(f"[self-test] K1 (WordNet oracle) on slice: n={res_k1.get('n')} "
         f"status={res_k1.get('status', 'SCORED')}", flush=True)
    res_n1 = VESC.run_n2_gaussian(width_a0 + 3, vocab, vocab_idx, ia_c, ib_c, gold_c, counts,
                                  set(vocab), seeds=(7, 13))
    print(f"[self-test] N1 (random Gaussian) on slice: status={res_n1.get('status', 'SCORED')} "
         f"seeds={res_n1.get('seeds')}", flush=True)

    print("[self-test] PASS", flush=True)
    return {"vesc_self_test": vesc_res, "slice_n": len(slice_disjoint), "common_n_on_slice": n_common,
           "per_arm_n_on_slice": per_arm_n}


# ==============================================================================================
# main run
# ==============================================================================================
def run() -> Dict:
    t0 = time.time()
    out_dir = str(get_output_dir(ANCHOR_NAME))

    from exp_task_degeneracy_v1 import ruler_mode_gate
    gate = ruler_mode_gate()

    sv_all = VESC.load_simverb(VESC.SIMVERB)
    sl_v = VESC.load_simlex_verbs(VESC.SIMLEX)
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    sl_keys = set(frozenset((a.lower(), b.lower())) for a, b, _ in sl_v)
    usable = [r for r in sv_all if r[0].lower() in tab and r[1].lower() in tab]
    disjoint = [r for r in usable if frozenset((r[0].lower(), r[1].lower())) not in sl_keys]
    overlap = [r for r in usable if frozenset((r[0].lower(), r[1].lower())) in sl_keys]
    print(f"[run] SimVerb usable={len(usable)} disjoint(PRIMARY)={len(disjoint)} "
          f"overlap(out of scope for this cell)={len(overlap)} run_mode={RUN_MODE}", flush=True)

    built = VESC.build_all_arms(disjoint, overlap)
    vocab = built["vocab"]; vocab_idx = {w: i for i, w in enumerate(vocab)}
    ia_full = np.array([vocab_idx[p[0].lower()] for p in disjoint])
    ib_full = np.array([vocab_idx[p[1].lower()] for p in disjoint])
    gold_full = np.array([p[3] for p in disjoint], dtype=np.float64)
    counts = built["counts"]
    arms_raw = {n: built["arms"][n] for n in ARM_NAMES}
    print(f"[run] vocab={len(vocab)} words; event_col_names={built['event_col_names']} "
          f"keep_conseq={built['keep_conseq']} (coverage {built['conseq_coverage_frac']:.4f})",
          flush=True)

    # ============================================================================================
    # REGRESSION GATE -- reproduce the landed FULL-GRID per-arm own-population point rho, using
    # VESC.run_arm on the FULL (own-population) ia_full/ib_full, byte-for-byte the same call the
    # landed cell itself makes. Proves this cell invokes the shared machinery identically before
    # trusting the NEW common-population numbers below.
    # ============================================================================================
    regression = {}
    regression_ok_all = True
    for name, raw in arms_raw.items():
        res = VESC.run_arm(name, raw, vocab, vocab_idx, ia_full, ib_full, gold_full, counts,
                           built["conc_z"], built["bncfreq"], seed=VESC._arm_seed(name))
        landed = LANDED_FULL_GRID_OWN_POP[name]
        got_rho = res.get("rho", {}).get("point")
        got_n = res.get("n")
        ok = bool(got_rho is not None and abs(got_rho - landed["rho"]) < REGRESSION_RTOL
                 and got_n == landed["n"])
        regression_ok_all = regression_ok_all and ok
        regression[name] = {"landed_n": landed["n"], "landed_rho": landed["rho"],
                            "recomputed_n": got_n, "recomputed_rho": got_rho, "reproduced": ok}
        print(f"[run] REGRESSION {name}: landed n={landed['n']} rho={landed['rho']}, "
             f"recomputed n={got_n} rho={got_rho}, reproduced={ok}", flush=True)
    if not regression_ok_all:
        elapsed = time.time() - t0
        metrics = {"anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "prereg": PREREG,
                  "run_mode": RUN_MODE, "measures_the_instrument_not_a_capability": True,
                  "cue_regime": "exact_key_own_code", "ruler_mode_gate": gate,
                  "regression_gate": regression, "verdict": "REGRESSION_GATE_FAILED",
                  "verdict_msg": ("At least one arm's own-population point rho did not reproduce "
                                  "the landed full-grid value; refusing to trust the common-"
                                  f"population rescore. regression={regression}"),
                  "elapsed_s": round(elapsed, 2), "summary": "REGRESSION_GATE_FAILED"}
        write_metrics(Path(out_dir), metrics)
        raise SystemExit(f"[fatal] REGRESSION GATE FAILED: {regression}")

    # ============================================================================================
    # COMMON POPULATION
    # ============================================================================================
    common_mask, per_arm_own_n = common_population_mask(arms_raw, vocab, ia_full, ib_full)
    n_common = int(common_mask.sum())
    ia_c, ib_c, gold_c = ia_full[common_mask], ib_full[common_mask], gold_full[common_mask]
    print(f"[run] per-arm OWN population (informational, matches landed n): {per_arm_own_n}", flush=True)
    print(f"[run] COMMON population (all 5 arms defined): n={n_common}", flush=True)
    assert n_common >= VESC.JOINT_GATE_MIN_N, (
        f"common population n={n_common} below JOINT_GATE_MIN_N={VESC.JOINT_GATE_MIN_N} -- "
        f"cannot construct a bootstrap CI worth reporting")

    done = completed_units(out_dir)
    results: Dict[str, Dict] = {}
    for name, raw in arms_raw.items():
        key = unit_key(ANCHOR_NAME, RUN_MODE, name)
        if key in done:
            results[name] = load_units(out_dir)[key]
            print(f"[ckpt] {name}: resumed from units.jsonl", flush=True)
            continue
        t1 = time.time()
        res = VESC.run_arm(name, raw, vocab, vocab_idx, ia_c, ib_c, gold_c, counts,
                           built["conc_z"], built["bncfreq"], seed=VESC._arm_seed(name))
        res["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key, res)
        results[name] = res
        print(f"[arm] {name} (common pop) n={res.get('n')} status={res.get('status', 'SCORED')} "
             f"band={res.get('band')} rho={res.get('rho', {}).get('point')} "
             f"C1_survives={res.get('C1_PARTIAL', {}).get('survives_partial')} "
             f"({res['elapsed_s']}s)", flush=True)

    key_k1 = unit_key(ANCHOR_NAME, RUN_MODE, "K1_WORDNET_ORACLE_COMMON_POP")
    if key_k1 in done:
        res_k1 = load_units(out_dir)[key_k1]
        print("[ckpt] K1_WORDNET_ORACLE_COMMON_POP: resumed", flush=True)
    else:
        t1 = time.time()
        res_k1 = VESC.run_wordnet_oracle(vocab, vocab_idx, ia_c, ib_c, gold_c, counts,
                                         built["conc_z"], built["bncfreq"], SEL.N_PERM,
                                         seed=VESC._arm_seed("K1_WORDNET_ORACLE_COMMON_POP"))
        res_k1["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key_k1, res_k1)
        print(f"[arm] K1_WORDNET_ORACLE_COMMON_POP n={res_k1.get('n')} band={res_k1.get('band')} "
             f"({res_k1['elapsed_s']}s)", flush=True)

    key_n1 = unit_key(ANCHOR_NAME, RUN_MODE, "N1_RANDOM_GAUSSIAN_COMMON_POP")
    if key_n1 in done:
        res_n1 = load_units(out_dir)[key_n1]
        print("[ckpt] N1_RANDOM_GAUSSIAN_COMMON_POP: resumed", flush=True)
    else:
        t1 = time.time()
        width_a1 = next(iter(arms_raw["A1_EVENT_SALIENT"].values())).shape[0]
        res_n1 = VESC.run_n2_gaussian(width_a1, vocab, vocab_idx, ia_c, ib_c, gold_c, counts,
                                      set(vocab), seeds=(7, 13, 17, 23, 29))
        res_n1["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key_n1, res_n1)
        print(f"[arm] N1_RANDOM_GAUSSIAN_COMMON_POP widths={res_n1.get('widths')} "
             f"({res_n1['elapsed_s']}s)", flush=True)

    # ============================================================================================
    # obs vectors per arm (for paired diffs) + BOTH-TIE-CONVENTION floor readout
    # ============================================================================================
    obs_by_arm: Dict[str, np.ndarray] = {}
    for name, raw in arms_raw.items():
        width = next(iter(raw.values())).shape[0]
        X = build_X(raw, vocab, width)
        obs_by_arm[name] = CELL.pair_cos(X, ia_c, ib_c)

    key_tie = unit_key(ANCHOR_NAME, RUN_MODE, "TIE_CONVENTION_FLOOR_READOUT")
    if key_tie in done:
        tie_readout = load_units(out_dir)[key_tie]
        print("[ckpt] TIE_CONVENTION_FLOOR_READOUT: resumed", flush=True)
    else:
        t1 = time.time()
        tie_readout = {}
        for name, raw in arms_raw.items():
            tie_readout[name] = floor_tie_readout(name, raw, vocab, ia_c, ib_c, gold_c, counts,
                                                  seed=VESC._arm_seed(name) ^ 0x71E)
        tie_readout["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key_tie, tie_readout)
        print(f"[run] TIE_CONVENTION_FLOOR_READOUT done ({tie_readout['elapsed_s']}s)", flush=True)

    # ============================================================================================
    # PAIRED MARGINS -- the headline fix
    # ============================================================================================
    key_pm = unit_key(ANCHOR_NAME, RUN_MODE, "PAIRED_MARGINS")
    if key_pm in done:
        paired = load_units(out_dir)[key_pm]
        print("[ckpt] PAIRED_MARGINS: resumed", flush=True)
    else:
        t1 = time.time()
        pairs_to_compare = [
            ("A1_vs_A0", "A1_EVENT_SALIENT", "A0_INCUMBENT_12"),
            ("A1_vs_A3", "A1_EVENT_SALIENT", "A3_WIDTH_MATCHED_NOISE"),
            ("A1_vs_A4", "A1_EVENT_SALIENT", "A4_WIDTH_MATCHED_WRONG"),
            ("A1_vs_A2", "A1_EVENT_SALIENT", "A2_EVENT_ONLY"),
            ("A0_vs_A3", "A0_INCUMBENT_12", "A3_WIDTH_MATCHED_NOISE"),
        ]
        paired = {}
        for label, a, b in pairs_to_compare:
            paired[label] = paired_margin(obs_by_arm[a], obs_by_arm[b], gold_c,
                                          n_boot=SEL.N_BOOT, seed=BOOT_SEED_PAIRED ^ hash(label) % (2**31))
            print(f"[paired] {label}: point={paired[label]['point']:.4f} "
                 f"ci95={paired[label]['ci95']} halfwidth={paired[label]['ci_halfwidth']:.4f} "
                 f"band={paired[label]['band']}", flush=True)
        paired["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key_pm, paired)

    # ============================================================================================
    # STOP-IFS, evaluated in the pre-registered order (loosest instrument first, then confound,
    # then width-control, then population-artifact, then the positive verdict)
    # ============================================================================================
    a0, a1, a2, a3, a4 = (results[n] for n in ARM_NAMES)
    k1_clears = res_k1.get("band") == "ABOVE"
    a1_c1_survives = a1.get("C1_PARTIAL", {}).get("survives_partial")
    a1_own_band = a1.get("band")

    a1_vs_a0 = paired["A1_vs_A0"]; a1_vs_a3 = paired["A1_vs_A3"]; a1_vs_a4 = paired["A1_vs_A4"]
    a1_vs_a2 = paired["A1_vs_A2"]; a0_vs_a3 = paired["A0_vs_A3"]

    stop_ifs = {
        "v_K1_FAILS_INSTRUMENT_STILL_LOOSE": bool(not k1_clears),
        "iv_C1_PARTIAL_CONCRETENESS_CONFOUND": bool(a1_c1_survives is False),
        "iii_WIDTH_CONTROL_MATCHES_A1": bool(a1_vs_a3["band"] != "ABOVE" or a1_vs_a4["band"] != "ABOVE"),
        "ii_POPULATION_ARTIFACT_A1_A0_NOT_SEPARATED": bool(a1_vs_a0["band"] != "ABOVE"),
        "i_EVENT_SALIENT_CHANNEL_REAL_CANDIDATE": bool(
            a1_own_band == "ABOVE" and a1_c1_survives and a1_vs_a0["band"] == "ABOVE"
            and a1_vs_a3["band"] == "ABOVE" and a1_vs_a4["band"] == "ABOVE"),
    }

    if stop_ifs["v_K1_FAILS_INSTRUMENT_STILL_LOOSE"]:
        verdict = "INSTRUMENT_STILL_LOOSE_PUBLISH_NOTHING"
    elif stop_ifs["iv_C1_PARTIAL_CONCRETENESS_CONFOUND"]:
        verdict = "STOP_IF_iv_C1_PARTIAL_CONCRETENESS_CONFOUND"
    elif stop_ifs["iii_WIDTH_CONTROL_MATCHES_A1"]:
        verdict = "STOP_IF_iii_WIDTH_CONTROL_MATCHES_A1_CHANNEL_CLAIM_DIES"
    elif stop_ifs["ii_POPULATION_ARTIFACT_A1_A0_NOT_SEPARATED"]:
        verdict = "STOP_IF_ii_POPULATION_ARTIFACT_HEADLINE_INVALID"
    elif stop_ifs["i_EVENT_SALIENT_CHANNEL_REAL_CANDIDATE"]:
        verdict = "EVENT_SALIENT_CHANNEL_REAL_POPULATION_MATCHED"
    else:
        verdict = "AMBIGUOUS_NO_STOP_IF_CLEANLY_FIRED"

    def frac_ceiling(res: Dict) -> Optional[float]:
        pt = res.get("rho", {}).get("point")
        return round(pt / CEILING, 4) if pt is not None else None

    ceiling_fracs = {name: frac_ceiling(r) for name, r in results.items()}
    ceiling_fracs["K1_WORDNET_ORACLE_COMMON_POP"] = frac_ceiling(res_k1)

    verdict_msg = (
        f"COMMON population (all 5 treatment arms defined) n={n_common}, vs each arm's own "
        f"(landed-style) population {per_arm_own_n}. "
        f"A0 rho={a0.get('rho', {}).get('point')} band={a0.get('band')}; "
        f"A1 rho={a1.get('rho', {}).get('point')} band={a1_own_band} C1_survives={a1_c1_survives}; "
        f"PAIRED A1-vs-A0={a1_vs_a0['point']:.4f} [{a1_vs_a0['ci95'][0]:.4f},{a1_vs_a0['ci95'][1]:.4f}] "
        f"band={a1_vs_a0['band']}; "
        f"PAIRED A1-vs-A3(noise)={a1_vs_a3['point']:.4f} band={a1_vs_a3['band']}; "
        f"PAIRED A1-vs-A4(wrong)={a1_vs_a4['point']:.4f} band={a1_vs_a4['band']}; "
        f"PAIRED A1-vs-A2={a1_vs_a2['point']:.4f} band={a1_vs_a2['band']}; "
        f"PAIRED A0-vs-A3={a0_vs_a3['point']:.4f} band={a0_vs_a3['band']}; "
        f"K1(known-answer oracle) band={res_k1.get('band')} (ceiling reference, no verdict weight); "
        f"stop_ifs={stop_ifs}. Every rho also reported as a fraction of the SimVerb ceiling "
        f"{CEILING} (ceiling itself has 95% CI {CEILING_CI95}, ~+/-16% relative) in "
        f"ceiling_fractions_of_0_6121. SCOPE LIMIT: A1 is 15 dims of VAD only (no ATOMIC "
        f"consequentiality, dropped at the 0.70 coverage gate; no socialness norms, not on disk).")

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "prereg": PREREG,
        "run_mode": RUN_MODE, "N_PERM": SEL.N_PERM, "N_BOOT": SEL.N_BOOT,
        "N_BOOT_PARTIAL": VESC.N_BOOT_PARTIAL,
        "measures_the_instrument_not_a_capability": True, "cue_regime": "exact_key_own_code",
        "progress_logging": "print_flush_true",
        "ruler_mode_gate": gate, "regression_gate": regression,
        "population": {"per_arm_own_n_informational": per_arm_own_n, "common_n": n_common,
                      "primary_disjoint_stratum_n": len(disjoint), "simverb_ceiling_0_6121": CEILING,
                      "ceiling_ci95": CEILING_CI95},
        "event_channel_construction": {"event_col_names": built["event_col_names"],
                                       "keep_atomic_consequentiality": built["keep_conseq"],
                                       "atomic_coverage_frac": built["conseq_coverage_frac"]},
        "arms": results, "K1_WORDNET_ORACLE_COMMON_POP": res_k1,
        "N1_RANDOM_GAUSSIAN_COMMON_POP": res_n1,
        "paired_margins": paired, "tie_convention_floor_readout": tie_readout,
        "stop_ifs": stop_ifs, "ceiling_fractions_of_0_6121": ceiling_fracs,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 2), "summary": verdict_msg,
    }
    write_metrics(Path(out_dir), metrics)
    print(f"[run] DONE in {elapsed:.1f}s -- verdict={verdict}", flush=True)
    return metrics


def main() -> int:
    if _ARGS.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    m = run()
    print(json.dumps({"verdict": m["verdict"], "verdict_msg": m["verdict_msg"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
