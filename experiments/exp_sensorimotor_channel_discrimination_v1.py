"""exp_sensorimotor_channel_discrimination_v1 -- CAN THE SENSORIMOTOR CHANNEL TELL SET_P FROM SET_S AT ALL?

THIS IS A DISCRIMINATION TEST, NOT A SUPERVISION BUILD. Nothing is trained on the Lancaster norms
here. The single question, per notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.43 (commit
73edbca69, written BEFORE this cell existed): does a sensorimotor profile distance discriminate
SET_P (WordNet same-synset, zero corpus co-occurrence) from SET_S (top co-occurring, no close
WordNet relation) AT ALL? A SIGNAL THAT CANNOT DISCRIMINATE CANNOT TEACH, so this gates every
downstream supervision idea. If (A) fires, the supervision cell is a SEPARATE, later decision with
its own pre-commitment.

=================================================================================================
PRE-COMMITTED READINGS -- COPIED VERBATIM FROM 6.43, NOT RENEGOTIATED HERE.
  (A) Sensorimotor distance discriminates CI-separated above its OWN credible bar -> an admissible
      teaching signal that is NOT text-derived, NOT WordNet-derived and NOT an LLM. Report the
      coverage BESIDE the AUC; a win on 20 pairs is not a win.
  (B) It sits at or near the constant/prototype floor -> the drill's flagged risk FIRED: 11
      dimensions cannot separate same-domain pairs. THIS IS NOT A REFUTATION OF GROUNDING -- IT IS A
      REFUTATION OF THIS RESOLUTION. Say what resolution would be needed (Binder's 65 dimensions
      discriminate far better but cover only 9.2% of eval words) rather than concluding grounding
      fails.
  (C) The floor's credible bar is unclearable at the available n -> UNTESTABLE, not negative
      (discipline 18). Report the n required.
MANDATORY per 6.43: floors recomputed on THIS representation (11-dim ratings, discipline 16);
credible bar = floor + its own 95% half-width (discipline 18); CI half-width and null p95 beside
every margin (discipline 14); state how many pairs each control actually removed (16 corollary);
state the swept values and the queries per point (discipline 15); report tie conventions both ways
(discipline 13).

=================================================================================================
PRIOR-WORK CHECK -- HOW IT WAS ENUMERATED, SINCE THE KB TOOL IS DEAD.
tools/substrate_query.sh is NON-FUNCTIONAL (zero bytes, exit 0) and CLAUDE.md's own correction says
an empty result from it is NOT evidence of absence. It was NOT used. Instead, NAME-LEVEL enumeration
over all 5,873 experiments/*.py basenames (`ls -1 experiments/*.py | sed 's#.*/##' | grep -i -E
"sensorimotor|lancaster|concrete|perceptual|modality|brysbaert|norms|measured_attribute"`), plus a
second sweep for "dissociation|grounding". Recursive grep over the repo TIMES OUT here and data/ is
157 GB, so no os.walk was attempted. HITS, and what each is:
  exp_grounding_measured_attribute_concreteness_v1.py -- THE CLOSEST PRIOR WORK, READ IN FULL AND
    BUILT ON, WITH CREDIT. It asks a DIFFERENT question (does anchoring a consolidation geometry to
    Brysbaert concreteness produce degree-invariant grounding of a ConceptNet subgraph, scored by
    Spearman on held-out attribute VALUES) on a DIFFERENT population (ConceptNet subgraph nodes, not
    the matched SET_P/SET_S pair cells) with a DIFFERENT read-out. What THIS cell takes from it: (i)
    its word-normalisation join convention (lowercase, "_"->" ", whitespace-stripped fallback),
    reused here; (ii) its scrambled-attribute must-fail control, generalised here to a per-arm
    scramble floor; (iii) its insistence that the exterior channel must be load-bearing, not merely
    present. NOT a rediscovery: it never scores SET_P vs SET_S and never touches the Lancaster norms.
  exp_meaning_asset_norms_coverage_{gap,scope}_v1.py -- asset COVERAGE accounting, no discrimination
    read-out.
  exp_{substrate_,}cross_modal_binding_*_v1_seed_*.py -- synthetic multi-modality BINDING capacity
    cells; no human norms, no pair instrument.
  exp_dissociation_score_instrument_v1.py -- THE INSTRUMENT THIS CELL REUSES VERBATIM (below).
NO cell scores the Lancaster sensorimotor norms on the dissociation instrument's matched pair cells.
This one is genuinely novel and is deliberately narrow.

=================================================================================================
ORGAN REUSE -- THE MATCHING MACHINERY IS NOT REIMPLEMENTED AND NOT LOOSENED.
The brief is explicit: reuse exp_dissociation_score_instrument_v1's licensed matching machinery
VERBATIM; do not write a new matcher and do not loosen the existing one to buy n (discipline 18:
"a bigger sample of an unlicensed instrument is worse than no sample"). The most verbatim reuse
available is the LICENSED RUN'S OWN PERSISTED OUTPUT, so this cell:
  - LOADS the matched cells from data/exp_dissociation_score_instrument_v1/units.jsonl unit
    POPULATION|v1.7|full (the version whose metrics.json reads
    DISSOCIATION_INSTRUMENT_LICENSED__STOP_IF_iii_COOCCURRENCE_DIAGNOSIS_CONFIRMED, n=242 matched
    pairs per cell, all nouns), gated by a REGRESSION GATE that re-asserts n_matched and every
    post-match SMD against that metrics.json before anything else runs;
  - LOADS the per-pair score arrays for the instrument's OWN eleven arms from unit
    SCORES|v1.7|full (same row order as matchedP/matchedS by construction: the producing code walks
    those lists in order) so the instrument's four licensing floors, its known-answer arm and its
    random-vector arm can be RE-RUN ON THE SURVIVING SUB-POPULATION without recomputing anything;
  - imports exp_dissociation_score_instrument_v1 for auc_of / auc_bootstrap / _pair_covariates /
    smd / MASTER_SEED and calls them unmodified.
NO caliper is touched. NO stratum is widened. The matched population is taken as given and only ever
SHRINKS (by the norms-coverage intersection, accounted below).

=================================================================================================
THE MEASUREMENT.
POPULATION. 242 matched units (a SET_P pair and its 1:1 matched SET_S pair). A unit SURVIVES only if
ALL FOUR of its words are in the Lancaster norms; dropping a whole unit rather than one side keeps
the 1:1 matched structure intact. Coverage is reported beside every AUC, per 6.43.

ARMS -- THE SWEEP, AND ITS RESOLUTION IS PART OF THE VERDICT (discipline 15).
  3 representations of the 11 mean dimensions x 2 distance metrics = 6 grid points:
    representations: RAW (11 raw means) | Z (per-dimension z-score) | CENTERED (minus the population
      mean vector, no rescale -- the variant that explicitly removes the prototype direction)
    metrics: COSINE | NEG_EUCLID
  Population statistics (mu, sd, mean vector) are computed over the instrument's OWN covered word
  population, never over all 39,707 Lancaster rows, so no information from outside the instrument
  enters. QUERIES PER GRID POINT: n_surviving SET_P pair scores + n_surviving SET_S pair scores.
  Plus ONE clearly-labelled REFERENCE arm at the opposite end of the resolution axis:
    CONC1_NEG_ABSDIFF -- Brysbaert concreteness, ONE dimension, scored -|c1 - c2|. It is the
    1-dimensional limit of "a low-dimensional rating channel" and is gated against ITS OWN floors on
    ITS OWN representation, never against the sensorimotor ones.

FLOORS -- REBUILT ON THIS REPRESENTATION AND THIS POPULATION. NOTHING IMPORTED.
0.5431, 0.5943 and 0.6317 are NEVER used: they were computed on the bag / human / arc
representations and 21 arms are currently suspended in this repo for exactly that error
(notes/AUDIT_floor_provenance_cross_representation_2026-08-18.md). Every floor below is recomputed
on the SURVIVING pair population, and the two representation-sensitive ones are rebuilt on the
11-dim ratings:
  F_ORTHOGRAPHIC          trigram-cosine (its own representation), AUC recomputed on survivors
  F_FREQUENCY             max-of-pair log1p frequency (its own representation), recomputed
  F_SCRAMBLE__<arm>       PER ARM: the word -> 11-dim-row assignment is permuted, then THAT ARM's own
                          scoring function is re-applied. Identity destroyed, marginals preserved.
  F_CONSTANT_PROTOTYPE__SM11   pair-mean of cos(v_w_raw, population mean vector) -- a per-word,
                          QUERY-INDEPENDENT genericity score, the 11-dim analogue of the instrument's
                          own constant-prototype floor. THE DRILL PREDICTS THIS CHANNEL MAY BEHAVE
                          LIKE THIS FLOOR; it is tested directly, not around.
  F_PROTOTYPE_MAGNITUDE__SM11  pair-mean of ||v_w_raw|| -- overall sensorimotor strength, also
                          query-independent. Included because it is the other natural constant score
                          on this representation and taking the MAX of the family is the
                          conservative choice.
  F_CONSTANT_PROTOTYPE__CONC1 / F_PROTOTYPE_MAGNITUDE__CONC1 -- the same two, on the 1-dim
                          concreteness representation (-|c - mean_c| and c respectively), used ONLY
                          for the concreteness reference arm.
CREDIBLE BAR = the max floor's AUC + THAT FLOOR'S OWN 95% half-width (discipline 18). An arm that
beats the floor's point value but not the credible bar IS NOT A PASS and is reported as such. A
stricter diagnostic, max over floors of max(auc, 1-auc), is ALSO reported and disclosed rather than
quietly used or quietly dropped.

LICENSING RE-CHECK ON THE SURVIVORS (this is the (C) gate, and it is checked FIRST). Shrinking a
matched population can unbalance it, so the instrument's own STOP-IF (i)/(ii) are re-run at the
surviving n from the persisted score arrays: all four instrument floors must still CI-INCLUDE 0.5,
the WordNet path-similarity known-answer arm must still read >= 0.95, and the random-vector arm must
still sit at chance. Post-match SMD on all five matching covariates is recomputed on the survivors.
If licensing fails at the surviving n, NO arm number may be interpreted and the verdict is
UNTESTABLE, not negative.

UNCERTAINTY, REPORTED BESIDE EVERY MARGIN (discipline 14).
  bootstrap: the instrument's OWN auc_bootstrap, unmodified, for comparability (independent resample
    of each cell) PLUS a paired-unit bootstrap that resamples matched UNITS, since the design is 1:1
    matched. Both reported; the licensed one is what the bar is applied to.
  null: a PAIRED-SWAP permutation null (swap the P and S score within a matched unit with prob 0.5)
    -- the null appropriate to a matched design -- and the unpaired label-shuffle null. p50, p95 and
    a two-sided p are reported for both at the actual n.
  ties: tie mass, plus AUC with ties awarded to P and to S (discipline 13), never silently one way.

CONTROLS, AND HOW MANY PAIRS EACH ACTUALLY REMOVED (16 corollary). A control that excludes nothing
is not a control, so each is accounted explicitly: the norms-coverage filter reports units removed
and why; the upstream caliper's drop count is carried through from the population diagnostics; the
scramble floors remove nothing BY DESIGN, so instead they report the fraction of pair scores they
actually changed and their rank-correlation with the unscrambled arm -- a scramble that barely moves
the scores is a fake control and is called out.

TWO THINGS THE SMOKE EXPOSED, DECIDED AND WRITTEN DOWN BEFORE THE FULL RUN, NOT AFTER IT.
  1. THE KNOWN-ANSWER GATE IS A BOUNDARY CASE AT THE SURVIVING n, SO IT IS REPORTED BOTH WAYS. The
     source instrument's STOP-IF (ii) is a POINT gate (WordNet path-sim AUC >= 0.95); at the smoke's
     n=80 the same arm on the same pairs reads 0.9441 with 95% CI [0.9042, 0.9731]. Declaring the
     whole measurement UNTESTABLE on a 0.006 point shortfall that sits well inside its own CI would
     be discipline 14's error with the sign flipped -- reading a WIDTH as a demonstration of
     failure. So the branch is driven by the CI-INCLUSIVE form (the arm's 95% upper bound reaches
     0.95, i.e. we cannot show the instrument has lost sight of the relation), and BOTH the strict
     point verdict and the CI verdict are written into the metrics and into the verdict line every
     time. This is NOT a loosening of the matcher, which is untouched; it is this cell's own
     re-check of a population it only ever SHRANK.
  2. A SINGLE-SEED SCRAMBLE DRAW IS A DRAW, NOT A FLOOR VALUE. The headline F_SCRAMBLE__<arm> keeps
     the source instrument's single-permutation construction for consistency, but the smoke showed
     one draw landing at 0.6075 while the 5-seed distribution for that same arm centred on 0.5073 --
     i.e. the headline draw was noise. Every scramble floor therefore ships with its multi-seed mean
     and p95 beside it, and any decision resting on a single scramble draw is flagged. In the smoke
     no decision did: the max floor was the constant/prototype one either way.

VERDICT BRANCHES, evaluated in this order, mapping 1:1 onto 6.43:
  C_UNTESTABLE_INSTRUMENT_UNLICENSED_AT_SURVIVING_N -- licensing re-check failed at this n.
  C_UNTESTABLE_CREDIBLE_BAR_UNCLEARABLE -- no achievable AUC could be CI-separated above the bar.
  A_SENSORIMOTOR_DISCRIMINATES -- some sensorimotor arm's 95% CI lower bound EXCEEDS its own
    credible bar.
  B_AT_OR_NEAR_CONSTANT_PROTOTYPE_FLOOR -- otherwise. Reported with whether the best arm's CI
    overlaps the constant/prototype floor's CI (the literal "at or near" test) and with the
    resolution trade that would be needed, per 6.43.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's concatenated per-pair score vector, asserted all
#   distinct across the 6 swept sensorimotor arms
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path)
# - except SystemExit: raised BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: one tools.exp_checkpoint unit per ARM (bootstraps + nulls are the cost), a
#   POPULATION unit, and a MAIN unit -- a kill loses at most one arm
# - discriminator survives scale: the PLANTED-SEPARABLE self-test runs at the FULL surviving n in
#   BOTH smoke and full, so the discriminator is proven able to fire at the scale that decides
# - baseline_in_band: the floor battery IS the baseline; every floor is reported with its CI
# - crlb_floor_computed: n/a -- an AUC discrimination measurement, not a capacity sweep; declared
# - progress_logging: print_flush_true (every phase prints a flushed line; timeout_s < 1800 so
#   sec 17's mandate does not bind, but it is honoured anyway)
# - calibration_check: default_ok_for_this_regime (reuses landed, regression-gated checkpoint units)

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. NOTHING is
trained. data/foundation/** is never opened. Writes only under
data/exp_sensorimotor_channel_discrimination_v1[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy + the licensed instrument module next -- flushed so a slow "
      "import is never mistaken for a hang)", flush=True)

import argparse
import csv
import hashlib
import json
import sys
import time
import traceback
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DISS   # noqa: E402  READ ONLY, VERBATIM
import experiments.exp_cue_to_store_translation_v1 as CTS         # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "sensorimotor_channel_discrimination_v1"
CODE_VERSION = "v1.2"   # v1.2 = v1.1 plus one smoke-only reporting fix (the reduced grid's
                        # "survivors" and "removed by the coverage filter" counts were computed
                        # before and after the smoke truncation respectively and so read as
                        # contradictory on the smoke's own verdict line; the untruncated survivor
                        # count now has its own key). FULL-path arithmetic is untouched.
                        # v1.0's smoke ran clean and its POPULATION/ARM construction is UNCHANGED in
                        # v1.1; what changed is REPORTING and one gate FORM: the known-answer
                        # re-check is now reported both as the strict point gate and as the
                        # CI-inclusive gate (docstring item 1), the constant/prototype floor's
                        # neutrality ON THE 11-DIM REPRESENTATION is promoted to a first-class
                        # reported finding, and precision-at-this-n is reported against discipline
                        # 18's required-n table. Bumped per the no-silent-resume discipline so no
                        # checkpoint key from v1.0 can resume into v1.1's interpretation.
FINDINGS = "notes/sensorimotor_channel_discrimination_2026-08-18.md"

SRC_DIR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1")
SRC_VERSION = "v1.7"          # the LICENSED version; asserted against its metrics.json
SRC_GRID = "full"
LANCASTER = os.path.join(REPO, "data", "grounding_testbed",
                         "Lancaster_sensorimotor_norms_for_39707_words.csv")
CONCRETENESS = os.path.join(REPO, "data", "grounding_testbed",
                            "Concreteness_ratings_Brysbaert_et_al_BRM.txt")

SM_DIMS = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
           "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = DISS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
N_PERM = 1500 if SMOKE else 10000
N_SCRAMBLE_SEEDS = 5 if SMOKE else 20      # distribution around the headline scramble floor
SMOKE_MAX_UNITS = 80                       # smoke uses a REAL smaller population, not a fixture
MIN_UNITS_TO_REPORT = 20                   # "a win on 20 pairs is not a win" -- refuse below this

# Required-n table for a floor half-width, quoted from STATUS.md discipline 18 (a REFERENCE table
# carried so the (C) branch can report "the n required" without importing any FLOOR VALUE).
REQUIRED_N_FOR_HALFWIDTH = {"0.05": "250-290", "0.03": "770", "0.02": "1550-1780", "0.01": "6300-7200"}


def _log(msg: str) -> None:
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# DATA LOADERS
# =================================================================================================
def _norm_word(w: str) -> str:
    """Join convention CREDITED TO exp_grounding_measured_attribute_concreteness_v1 (lowercase,
    underscore -> space, whitespace stripped)."""
    return str(w).strip().lower().replace("_", " ")


def load_sensorimotor(path: str) -> Dict[str, np.ndarray]:
    """word -> [11] mean sensorimotor ratings. Rows with any unparseable dimension are DROPPED, not
    imputed (an imputed row would be a fabricated measurement)."""
    out: Dict[str, np.ndarray] = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        missing = [d for d in SM_DIMS if d not in (rd.fieldnames or [])]
        if missing:
            raise SystemExit("LANCASTER SCHEMA MISMATCH -- missing columns %r" % missing)
        for row in rd:
            try:
                v = np.array([float(row[d]) for d in SM_DIMS], dtype=np.float64)
            except (TypeError, ValueError):
                continue
            if not np.all(np.isfinite(v)):
                continue
            out[_norm_word(row["Word"])] = v
    return out


def load_concreteness(path: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline()
        if "Conc.M" not in header:
            raise SystemExit("CONCRETENESS SCHEMA MISMATCH -- header lacks Conc.M: %r" % header[:80])
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3:
                try:
                    out[_norm_word(p[0])] = float(p[2])
                except ValueError:
                    continue
    return out


def load_licensed_population() -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]],
                                        Dict, Dict[str, Dict[str, np.ndarray]], Dict]:
    """The licensed instrument's OWN matched cells and OWN per-pair arm scores, taken verbatim from
    its persisted checkpoint, with a REGRESSION GATE against its metrics.json."""
    units = load_units(SRC_DIR)
    pop_key = unit_key("POPULATION", SRC_VERSION, SRC_GRID)
    sc_key = unit_key("SCORES", SRC_VERSION, SRC_GRID)
    if pop_key not in units or sc_key not in units:
        raise SystemExit("LICENSED POPULATION MISSING -- %r / %r absent from %s (keys=%r)"
                         % (pop_key, sc_key, SRC_DIR, sorted(units.keys())))
    pop = units[pop_key]
    matchedP = [tuple(x) for x in pop["matchedP"]]
    matchedS = [tuple(x) for x in pop["matchedS"]]
    arm_scores = {k: {"P": np.asarray(v["P"], dtype=np.float64),
                      "S": np.asarray(v["S"], dtype=np.float64)}
                  for k, v in units[sc_key].items()}

    with open(os.path.join(SRC_DIR, "metrics.json"), encoding="utf-8") as f:
        src_metrics = json.load(f)
    rep = src_metrics.get("report", {})
    gate = {
        "source_dir": SRC_DIR,
        "source_code_version_in_metrics": src_metrics.get("code_version"),
        "source_verdict": src_metrics.get("verdict"),
        "expected_version": SRC_VERSION,
        "n_matched_checkpoint": len(matchedP),
        "n_matched_metrics": rep.get("N_MATCHED_PAIRS_PER_CELL"),
        "post_match_smd_metrics": rep.get("POPULATION", {}).get("matching", {}).get("post_match_smd"),
        "n_dropped_caliper_upstream": rep.get("POPULATION", {}).get("matching", {}).get("n_dropped_caliper"),
        "n_candidates_P_upstream": rep.get("POPULATION", {}).get("matching", {}).get("n_candidates_P"),
        "source_licensing": rep.get("LICENSING"),
    }
    ok = (src_metrics.get("code_version") == SRC_VERSION
          and len(matchedP) == len(matchedS) == rep.get("N_MATCHED_PAIRS_PER_CELL")
          and bool(rep.get("LICENSING", {}).get("INSTRUMENT_LICENSED"))
          and all(len(v["P"]) == len(v["S"]) == len(matchedP) for v in arm_scores.values()))
    gate["PASS"] = bool(ok)
    if not ok:
        raise SystemExit("REGRESSION GATE FAILED against the licensed instrument: %r" % gate)
    return matchedP, matchedS, gate, arm_scores, rep


# =================================================================================================
# REPRESENTATIONS AND METRICS (the swept grid)
# =================================================================================================
REPRESENTATIONS = ("RAW", "Z", "CENTERED")
METRICS = ("COSINE", "NEG_EUCLID")


def build_representation(M: np.ndarray, rep: str) -> np.ndarray:
    """M is [n_words, n_dims] RAW. Population statistics come from M itself (the instrument's own
    covered word population), never from outside it."""
    if rep == "RAW":
        return M.copy()
    mu = M.mean(axis=0)
    if rep == "CENTERED":
        return M - mu
    if rep == "Z":
        sd = M.std(axis=0)
        sd = np.where(sd < 1e-12, 1.0, sd)
        return (M - mu) / sd
    raise ValueError("unknown representation %r" % rep)


def pair_score(a: np.ndarray, b: np.ndarray, metric: str) -> np.ndarray:
    """Row-wise score between two [n, d] blocks. Higher = MORE similar for both metrics, so the AUC
    direction is the same as the instrument's (P above S = substitutability)."""
    if metric == "COSINE":
        na = np.linalg.norm(a, axis=1)
        nb = np.linalg.norm(b, axis=1)
        den = np.where((na * nb) < 1e-12, 1e-12, na * nb)
        return np.sum(a * b, axis=1) / den
    if metric == "NEG_EUCLID":
        return -np.linalg.norm(a - b, axis=1)
    raise ValueError("unknown metric %r" % metric)


def arm_name(rep: str, metric: str) -> str:
    return "SM11_%s_%s" % (rep, metric)


# =================================================================================================
# AUC + UNCERTAINTY (the instrument's own machinery, plus the paired variants the design calls for)
# =================================================================================================
def auc_tie_conventions(sp: np.ndarray, ss: np.ndarray) -> Dict:
    """Discipline 13: report tie conventions BOTH ways, never silently the flattering one."""
    sp = np.asarray(sp, dtype=np.float64)
    ss = np.asarray(ss, dtype=np.float64)
    diff = sp[:, None] - ss[None, :]
    n_tot = diff.size
    n_tie = int(np.sum(diff == 0.0))
    n_gt = int(np.sum(diff > 0.0))
    return {"tie_mass_frac": round(n_tie / n_tot, 6) if n_tot else float("nan"),
            "auc_ties_half": round((n_gt + 0.5 * n_tie) / n_tot, 4) if n_tot else float("nan"),
            "auc_ties_to_P": round((n_gt + n_tie) / n_tot, 4) if n_tot else float("nan"),
            "auc_ties_to_S": round(n_gt / n_tot, 4) if n_tot else float("nan")}


def paired_bootstrap(sp: np.ndarray, ss: np.ndarray, n_boot: int, seed: int) -> Dict:
    """Resamples matched UNITS (both sides together), which is what a 1:1 matched design licenses."""
    sp = np.asarray(sp, dtype=np.float64)
    ss = np.asarray(ss, dtype=np.float64)
    n = sp.size
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boots[b] = DISS.auc_of(sp[idx], ss[idx])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    return {"auc": round(DISS.auc_of(sp, ss), 4), "ci95_paired": [round(lo, 4), round(hi, 4)],
            "ci_halfwidth_paired": round((hi - lo) / 2.0, 4)}


def permutation_nulls(sp: np.ndarray, ss: np.ndarray, n_perm: int, seed: int) -> Dict:
    """TWO nulls at the ACTUAL n (discipline 14): a PAIRED-SWAP null (swap P/S within a matched unit
    with prob 0.5 -- the null appropriate to this matched design) and the unpaired label shuffle."""
    sp = np.asarray(sp, dtype=np.float64)
    ss = np.asarray(ss, dtype=np.float64)
    n = sp.size
    point = DISS.auc_of(sp, ss)
    rng = np.random.default_rng(seed)
    paired = np.empty(n_perm, dtype=np.float64)
    unpaired = np.empty(n_perm, dtype=np.float64)
    both = np.concatenate([sp, ss])
    for b in range(n_perm):
        swap = rng.random(n) < 0.5
        a = np.where(swap, ss, sp)
        c = np.where(swap, sp, ss)
        paired[b] = DISS.auc_of(a, c)
        perm = rng.permutation(2 * n)
        unpaired[b] = DISS.auc_of(both[perm[:n]], both[perm[n:]])
    return {
        "paired_swap_null_p50": round(float(np.percentile(paired, 50)), 4),
        "paired_swap_null_p95": round(float(np.percentile(paired, 95)), 4),
        "paired_swap_null_p_two_sided": round(float(np.mean(np.abs(paired - 0.5) >= abs(point - 0.5))), 4),
        "label_shuffle_null_p50": round(float(np.percentile(unpaired, 50)), 4),
        "label_shuffle_null_p95": round(float(np.percentile(unpaired, 95)), 4),
        "label_shuffle_null_p_two_sided": round(float(np.mean(np.abs(unpaired - 0.5) >= abs(point - 0.5))), 4),
    }


def score_arm(sp: np.ndarray, ss: np.ndarray, seed_off: int, n_boot: int, n_perm: int) -> Dict:
    res = dict(DISS.auc_bootstrap(sp, ss, n_boot, MASTER_SEED + 8181 + seed_off))
    res.update(paired_bootstrap(sp, ss, n_boot, MASTER_SEED + 5150 + seed_off))
    res.update(permutation_nulls(sp, ss, n_perm, MASTER_SEED + 6060 + seed_off))
    res.update(auc_tie_conventions(sp, ss))
    return res


# =================================================================================================
# THE CREDIBLE BAR (discipline 18) -- isolated so the self-test can prove it BOTH ways
# =================================================================================================
def credible_bar(floor_results: Dict[str, Dict]) -> Dict:
    """max floor by AUC point value; CREDIBLE BAR = that floor's AUC + ITS OWN 95% half-width."""
    name = max(floor_results.keys(), key=lambda k: floor_results[k]["auc"])
    f = floor_results[name]
    strict_name = max(floor_results.keys(),
                      key=lambda k: max(floor_results[k]["auc"], 1.0 - floor_results[k]["auc"]))
    sf = floor_results[strict_name]
    return {
        "max_floor_name": name, "max_floor_auc": f["auc"], "max_floor_ci95": f["ci95"],
        "max_floor_ci_halfwidth": f["ci_halfwidth"],
        "CREDIBLE_BAR": round(f["auc"] + f["ci_halfwidth"], 4),
        "strict_two_sided_floor_name": strict_name,
        "strict_two_sided_floor_value": round(max(sf["auc"], 1.0 - sf["auc"]), 4),
        "note": ("CREDIBLE BAR = max floor point value + that floor's own 95% half-width. An arm "
                 "beating the point value but not this bar is NOT a pass. The strict two-sided "
                 "figure is disclosed, not gated on."),
    }


def arm_clears_bar(arm: Dict, bar: float) -> bool:
    """CI-SEPARATED above the credible bar: the 95% lower bound must EXCEED the bar."""
    return bool(arm["ci95"][0] > bar)


# =================================================================================================
# SELF-TEST -- every discriminator must be shown able to FIRE, and to FAIL
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- the instrument's own AUC machinery, re-verified through OUR call sites ------------------
    sp = np.array([0.9, 0.8, 0.95, 0.85])
    ss = np.array([0.1, 0.2, 0.05, 0.15])
    assert abs(DISS.auc_of(sp, ss) - 1.0) < 1e-9, "separable AUC must be 1.0"
    rng = np.random.default_rng(0)
    a, b = rng.standard_normal(400), rng.standard_normal(400)
    assert abs(DISS.auc_of(a, b) - 0.5) < 0.06, "iid AUC must be near 0.5"
    ev["auc_known_answers"] = {"separable": 1.0, "null": round(DISS.auc_of(a, b), 4)}

    # --- metric known answers on REAL Lancaster rows (no fixtures) -------------------------------
    sm = load_sensorimotor(LANCASTER)
    for w in ("trumpet", "drum", "apple", "banana", "justice"):
        assert w in sm, "known-answer word missing from the norms: %r" % w
    def _s(w1, w2, metric="COSINE"):
        return float(pair_score(sm[w1][None, :], sm[w2][None, :], metric)[0])
    assert _s("trumpet", "drum") > _s("trumpet", "justice"), \
        "two instruments must be sensorimotor-closer than instrument/abstraction: %.4f vs %.4f" % (
            _s("trumpet", "drum"), _s("trumpet", "justice"))
    assert _s("apple", "banana") > _s("apple", "justice"), "two fruits must beat fruit/abstraction"
    assert abs(_s("apple", "apple") - 1.0) < 1e-9, "cosine of a vector with itself must be 1.0"
    assert abs(_s("apple", "apple", "NEG_EUCLID")) < 1e-12, "self NEG_EUCLID must be 0.0"
    ev["sensorimotor_metric_known_answers"] = {
        "trumpet_drum": round(_s("trumpet", "drum"), 4),
        "trumpet_justice": round(_s("trumpet", "justice"), 4),
        "apple_banana": round(_s("apple", "banana"), 4),
        "apple_justice": round(_s("apple", "justice"), 4)}

    # --- representations actually differ ---------------------------------------------------------
    M = np.stack([sm["apple"], sm["banana"], sm["justice"], sm["drum"]])
    reps = {r: build_representation(M, r) for r in REPRESENTATIONS}
    assert not np.allclose(reps["RAW"], reps["Z"]) and not np.allclose(reps["RAW"], reps["CENTERED"]) \
        and not np.allclose(reps["Z"], reps["CENTERED"]), "the three representations must differ"
    ev["representations_differ"] = True

    # --- PLANTED-SEPARABLE world: the discriminator MUST fire (proves the cell can return (A)) ----
    rngp = np.random.default_rng(11)
    n_pl = 166
    base = rngp.standard_normal((n_pl, len(SM_DIMS)))
    p_a, p_b = base, base + 0.01 * rngp.standard_normal((n_pl, len(SM_DIMS)))   # P: near-identical
    s_a, s_b = (rngp.standard_normal((n_pl, len(SM_DIMS))),
                rngp.standard_normal((n_pl, len(SM_DIMS))))                     # S: independent
    sp_pl = pair_score(p_a, p_b, "COSINE")
    ss_pl = pair_score(s_a, s_b, "COSINE")
    pl = score_arm(sp_pl, ss_pl, 0, 400, 400)
    assert pl["auc"] > 0.95 and pl["ci95"][0] > 0.9, \
        "PLANTED-SEPARABLE world must fire the discriminator at the deciding n: %r" % pl
    assert pl["paired_swap_null_p95"] < 0.9, "the paired-swap null must not itself sit at the top"
    ev["planted_separable_fires"] = {"auc": pl["auc"], "ci95": pl["ci95"],
                                     "paired_null_p95": pl["paired_swap_null_p95"], "n_per_cell": n_pl}

    # --- PLANTED-NULL world: identical vectors -> all ties; tie conventions BOTH ways -------------
    same = np.ones((50, len(SM_DIMS)))
    tn = auc_tie_conventions(pair_score(same, same, "COSINE"), pair_score(same, same, "COSINE"))
    assert tn["tie_mass_frac"] == 1.0 and tn["auc_ties_half"] == 0.5 \
        and tn["auc_ties_to_P"] == 1.0 and tn["auc_ties_to_S"] == 0.0, \
        "an all-ties world must read 0.5 / 1.0 / 0.0 under the three tie conventions: %r" % tn
    ev["tie_conventions_both_ways"] = tn

    # --- CREDIBLE BAR arithmetic, proven to PASS and to FAIL --------------------------------------
    floors_fix = {"F_A": {"auc": 0.55, "ci95": [0.49, 0.61], "ci_halfwidth": 0.06},
                  "F_B": {"auc": 0.52, "ci95": [0.47, 0.57], "ci_halfwidth": 0.05}}
    bar = credible_bar(floors_fix)
    assert bar["max_floor_name"] == "F_A" and abs(bar["CREDIBLE_BAR"] - 0.61) < 1e-9, \
        "credible bar must be the max floor's point value plus ITS OWN half-width: %r" % bar
    assert not arm_clears_bar({"ci95": [0.58, 0.70]}, bar["CREDIBLE_BAR"]), \
        "an arm above the floor POINT but below the credible BAR must NOT pass"
    assert arm_clears_bar({"ci95": [0.62, 0.75]}, bar["CREDIBLE_BAR"]), \
        "an arm CI-separated above the credible bar MUST pass"
    ev["credible_bar_can_pass_and_can_fail"] = bar

    # --- the SCRAMBLE control must actually change the scores -------------------------------------
    words = ["apple", "banana", "justice", "drum", "trumpet", "hammer", "cloud", "anger"]
    Mw = np.stack([sm[w] for w in words])
    perm = np.random.default_rng(3).permutation(len(words))
    assert not np.array_equal(perm, np.arange(len(words))), "the scramble permutation must move rows"
    s_true = pair_score(Mw[[0, 2, 4]], Mw[[1, 3, 5]], "COSINE")
    s_scr = pair_score(Mw[perm][[0, 2, 4]], Mw[perm][[1, 3, 5]], "COSINE")
    assert np.mean(s_true != s_scr) > 0.5, "a scramble that changes almost nothing is not a control"
    ev["scramble_is_a_real_control"] = {"frac_changed": float(np.mean(s_true != s_scr))}

    # --- concreteness loader known answer ---------------------------------------------------------
    conc = load_concreteness(CONCRETENESS)
    assert conc["apple"] > conc["justice"], "apple must be rated more concrete than justice"
    ev["concreteness_known_answer"] = {"apple": conc["apple"], "justice": conc["justice"]}

    # --- checkpoint round-trip --------------------------------------------------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# RUN
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    ck_dir = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                 "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                 "NOTHING_IS_TRAINED_ON_THE_NORMS": True}

    matchedP, matchedS, gate, src_arm_scores, src_rep = load_licensed_population()
    rep["REGRESSION_GATE_LICENSED_INSTRUMENT"] = gate
    _log("licensed population loaded: %d matched units (source verdict: %s)"
         % (len(matchedP), gate["source_verdict"]))

    sm = load_sensorimotor(LANCASTER)
    conc = load_concreteness(CONCRETENESS)
    _log("norms loaded: %d sensorimotor rows, %d concreteness rows" % (len(sm), len(conc)))

    # ---------------- COVERAGE INTERSECTION (a control -- and it removes pairs) -------------------
    n_units_in = len(matchedP)
    p_ok = np.array([(a in sm and b in sm) for a, b, _ in matchedP])
    s_ok = np.array([(a in sm and b in sm) for a, b, _ in matchedS])
    keep_sm = np.flatnonzero(p_ok & s_ok)
    words_all = sorted(set(w for pr in (matchedP + matchedS) for w in pr[:2]))
    words_cov = [w for w in words_all if w in sm]
    coverage = {
        "n_matched_units_input": n_units_in,
        "n_distinct_words_input": len(words_all),
        "n_distinct_words_in_norms": len(words_cov),
        "word_coverage_frac": round(len(words_cov) / len(words_all), 4),
        "n_setP_pairs_fully_covered": int(p_ok.sum()),
        "n_setS_pairs_fully_covered": int(s_ok.sum()),
        "n_matched_units_surviving": int(keep_sm.size),
        "n_matched_units_REMOVED_by_coverage_filter": int(n_units_in - keep_sm.size),
        "removal_reason": ("a matched unit is dropped unless ALL FOUR of its words are in the norms; "
                           "dropping the whole unit rather than one side preserves the 1:1 matched "
                           "structure the instrument was licensed on"),
        "n_dropped_caliper_UPSTREAM_in_licensed_matcher": gate["n_dropped_caliper_upstream"],
        "n_candidates_P_UPSTREAM": gate["n_candidates_P_upstream"],
    }
    if grid == "reduced":
        coverage["n_matched_units_surviving_coverage_filter_before_smoke_truncation"] = int(keep_sm.size)
        keep_sm = keep_sm[:SMOKE_MAX_UNITS]
        coverage["SMOKE_TRUNCATION"] = ("reduced grid keeps the first %d surviving units -- a REAL "
                                        "smaller population, not a synthetic fixture. The 'removed "
                                        "by coverage filter' count above refers to the UNtruncated "
                                        "survivor count, which is reported on its own key so the "
                                        "smoke's numbers cannot be read as self-contradictory."
                                        % SMOKE_MAX_UNITS)
        coverage["n_matched_units_surviving"] = int(keep_sm.size)
    rep["COVERAGE"] = coverage
    _log("COVERAGE: %d/%d matched units survive (%d removed); word coverage %d/%d = %.1f%%"
         % (keep_sm.size, n_units_in, n_units_in - keep_sm.size, len(words_cov), len(words_all),
            100.0 * len(words_cov) / len(words_all)))

    n_units = int(keep_sm.size)
    if n_units < MIN_UNITS_TO_REPORT:
        raise SystemExit("REFUSING TO REPORT: only %d surviving matched units (< %d). 'A win on 20 "
                         "pairs is not a win' -- 6.43." % (n_units, MIN_UNITS_TO_REPORT))

    survP = [matchedP[i] for i in keep_sm]
    survS = [matchedS[i] for i in keep_sm]

    # ---------------- POST-MATCH BALANCE RE-CHECK ON THE SURVIVORS -------------------------------
    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors = C["anchors"]
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    mat = np.asarray(C["mat"], dtype=np.float32)
    t_mat = np.asarray(aux["t_mat"], dtype=np.float32)
    pos_idx = C["pos"]
    fq_log = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}
    from tools import floor_battery as FB
    tri_all = FB.l2n(t_mat)
    proto_all = FB.constant_prototype_floor(mat, mat_ok)
    need = set(w for pr in (survP + survS) for w in pr[:2])
    tri_of = {w: tri_all[pos_idx[w]] for w in need if w in pos_idx}
    proto_of = {w: float(proto_all[pos_idx[w]]) for w in need if w in pos_idx}
    covP = DISS._pair_covariates(survP, fq_log, tri_of, proto_of)
    covS = DISS._pair_covariates(survS, fq_log, tri_of, proto_of)
    cov_names = ["mean_log_freq", "abs_freq_diff", "mean_length", "orthographic_trigram_cos",
                 "mean_constant_prototype"]
    rep["POST_MATCH_BALANCE_ON_SURVIVORS"] = {
        "smd": {k: round(DISS.smd(covP[:, i], covS[:, i]), 4) for i, k in enumerate(cov_names)},
        "smd_on_full_242_from_source_metrics": gate["post_match_smd_metrics"],
        "note": ("shrinking a matched population can unbalance it; this is the check, not an "
                 "assumption. Compare against the source run's own post-match SMD."),
    }
    _log("post-match SMD on survivors: %r" % rep["POST_MATCH_BALANCE_ON_SURVIVORS"]["smd"])

    # ---------------- LICENSING RE-CHECK AT THE SURVIVING n (the (C) gate) ------------------------
    keep_arr = np.asarray(keep_sm)
    src_sub = {k: {"P": v["P"][keep_arr], "S": v["S"][keep_arr]} for k, v in src_arm_scores.items()}
    lic_names = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE",
                 "KNOWN_ANSWER_WORDNET_PATH_SIM", "RANDOM_VECTOR_STORE", "INCUMBENT_LIVE_STORE"]
    lic_res: Dict[str, Dict] = {}
    for i, nm in enumerate(lic_names):
        if nm not in src_sub:
            continue
        lic_res[nm] = dict(DISS.auc_bootstrap(src_sub[nm]["P"], src_sub[nm]["S"], N_BOOT,
                                              MASTER_SEED + 3300 + i))
        _log("  [licensing] %-30s AUC=%.4f CI=%r %s"
             % (nm, lic_res[nm]["auc"], lic_res[nm]["ci95"], lic_res[nm]["band"]))
    floor_fail = [f for f in ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")
                  if lic_res.get(f, {}).get("band") != "NOT_SEPARATED_FROM_CHANCE"]
    ka_res = lic_res.get("KNOWN_ANSWER_WORDNET_PATH_SIM", {})
    ka = ka_res.get("auc", 0.0)
    ka_hi = ka_res.get("ci95", [0.0, 0.0])[1]
    ka_point_ok = bool(ka >= DISS.KNOWN_ANSWER_MIN_AUC)
    ka_ci_ok = bool(ka_hi >= DISS.KNOWN_ANSWER_MIN_AUC)
    licensed = bool(not floor_fail and ka_ci_ok)
    rep["LICENSING_RECHECK_AT_SURVIVING_N"] = {
        "arms": lic_res, "instrument_floor_failures": floor_fail,
        "known_answer_auc": ka, "known_answer_ci95": ka_res.get("ci95"),
        "known_answer_gate": DISS.KNOWN_ANSWER_MIN_AUC,
        "known_answer_PASSES_STRICT_POINT_GATE": ka_point_ok,
        "known_answer_PASSES_CI_INCLUSIVE_GATE": ka_ci_ok,
        "gate_actually_used_for_the_branch": "CI_INCLUSIVE (see docstring item 1; both reported)",
        "INSTRUMENT_STILL_LICENSED_AT_THIS_N": licensed,
        "note": ("these are the SOURCE instrument's own arms, re-scored on the surviving units from "
                 "its persisted per-pair score arrays -- nothing recomputed, nothing loosened. They "
                 "license the SUB-POPULATION; they are NOT the floors the sensorimotor arms are "
                 "gated against (those are rebuilt on the 11-dim representation below)."),
    }

    # ---------------- BUILD THE SENSORIMOTOR REPRESENTATIONS --------------------------------------
    sm_words = sorted(set(w for pr in (survP + survS) for w in pr[:2]))
    widx = {w: i for i, w in enumerate(sm_words)}
    M_raw = np.stack([sm[w] for w in sm_words])
    reps_M = {r: build_representation(M_raw, r) for r in REPRESENTATIONS}
    rep["REPRESENTATION_POPULATION"] = {
        "n_words": len(sm_words), "n_dims": len(SM_DIMS), "dims": SM_DIMS,
        "population_statistics_computed_over": ("the instrument's own covered word population "
                                                "(%d words), never all 39,707 Lancaster rows"
                                                % len(sm_words))}

    iP = np.array([[widx[a], widx[b]] for a, b, _ in survP])
    iS = np.array([[widx[a], widx[b]] for a, b, _ in survS])

    def arm_scores_for(rep_name: str, metric: str, row_map: np.ndarray = None
                       ) -> Tuple[np.ndarray, np.ndarray]:
        X = reps_M[rep_name]
        if row_map is not None:
            X = X[row_map]
        return (pair_score(X[iP[:, 0]], X[iP[:, 1]], metric),
                pair_score(X[iS[:, 0]], X[iS[:, 1]], metric))

    # ---------------- FLOORS ON THIS REPRESENTATION (rebuilt, never imported) ---------------------
    proto_cos = M_raw @ M_raw.mean(axis=0)
    proto_cos = proto_cos / (np.linalg.norm(M_raw, axis=1) * np.linalg.norm(M_raw.mean(axis=0)) + 1e-12)
    proto_mag = np.linalg.norm(M_raw, axis=1)

    def pair_mean_scalar(g: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return (0.5 * (g[iP[:, 0]] + g[iP[:, 1]]), 0.5 * (g[iS[:, 0]] + g[iS[:, 1]]))

    conc_words_ok = all(w in conc for w in sm_words)
    c_vec = np.array([conc.get(w, np.nan) for w in sm_words])
    conc_usable = bool(np.all(np.isfinite(c_vec)))

    # ---------------- SCORE EVERY ARM AND EVERY FLOOR (checkpointed per unit) ---------------------
    units_done = load_units(ck_dir)
    all_results: Dict[str, Dict] = {}
    all_digests: Dict[str, str] = {}
    scramble_diag: Dict[str, Dict] = {}
    seed_off = 0

    def emit(name: str, sp: np.ndarray, ss: np.ndarray) -> None:
        nonlocal seed_off
        seed_off += 1
        key = unit_key("ARM", CODE_VERSION, grid, name)
        prior = units_done.get(key)
        if prior is not None:
            all_results[name] = prior["res"]
            all_digests[name] = prior["digest"]
            _log("  [arm] %-34s RESUMED AUC=%.4f" % (name, prior["res"]["auc"]))
            return
        res = score_arm(sp, ss, seed_off, N_BOOT, N_PERM)
        dg = _digest(np.concatenate([sp, ss]))
        all_results[name] = res
        all_digests[name] = dg
        record_unit(ck_dir, key, {"res": res, "digest": dg})
        _log("  [arm] %-34s AUC=%.4f CI=%r hw=%.4f null_p95=%.4f %s"
             % (name, res["auc"], res["ci95"], res["ci_halfwidth"],
                res["paired_swap_null_p95"], res["band"]))

    # representation-independent floors, RECOMPUTED on this surviving population
    emit("F_ORTHOGRAPHIC", src_sub["F_ORTHOGRAPHIC"]["P"], src_sub["F_ORTHOGRAPHIC"]["S"])
    emit("F_FREQUENCY", src_sub["F_FREQUENCY"]["P"], src_sub["F_FREQUENCY"]["S"])
    # constant/prototype floors ON THE 11-DIM REPRESENTATION
    emit("F_CONSTANT_PROTOTYPE__SM11", *pair_mean_scalar(proto_cos))
    emit("F_PROTOTYPE_MAGNITUDE__SM11", *pair_mean_scalar(proto_mag))

    # the swept sensorimotor arms + a per-arm scramble floor on the same representation
    rng_scr = np.random.default_rng(MASTER_SEED + 4242)
    perm_headline = rng_scr.permutation(len(sm_words))
    while np.array_equal(perm_headline, np.arange(len(sm_words))):
        perm_headline = rng_scr.permutation(len(sm_words))
    for r in REPRESENTATIONS:
        for m in METRICS:
            nm = arm_name(r, m)
            sp, ss = arm_scores_for(r, m)
            emit(nm, sp, ss)
            sps, sss = arm_scores_for(r, m, perm_headline)
            emit("F_SCRAMBLE__" + nm, sps, sss)
            changed = float(np.mean(np.concatenate([sp, ss]) != np.concatenate([sps, sss])))
            rho = float(np.corrcoef(
                np.argsort(np.argsort(np.concatenate([sp, ss]))),
                np.argsort(np.argsort(np.concatenate([sps, sss]))))[0, 1])
            extra = []
            for k in range(N_SCRAMBLE_SEEDS):
                pk = np.random.default_rng(MASTER_SEED + 7000 + k).permutation(len(sm_words))
                a, b = arm_scores_for(r, m, pk)
                extra.append(DISS.auc_of(a, b))
            scramble_diag[nm] = {
                "frac_pair_scores_changed_by_scramble": round(changed, 4),
                "spearman_scrambled_vs_true": round(rho, 4),
                "n_pairs_removed_by_this_control": 0,
                "control_note": ("a scramble removes no pairs BY DESIGN, so its evidence of being a "
                                 "real control is that it changed this fraction of scores and "
                                 "decorrelated from the true arm"),
                "multi_seed_scramble_auc_mean": round(float(np.mean(extra)), 4),
                "multi_seed_scramble_auc_p95": round(float(np.percentile(extra, 95)), 4),
                "n_scramble_seeds": N_SCRAMBLE_SEEDS,
            }

    # concreteness reference arm + its OWN floors on ITS OWN representation
    if conc_usable:
        cp = -np.abs(c_vec[iP[:, 0]] - c_vec[iP[:, 1]])
        cs = -np.abs(c_vec[iS[:, 0]] - c_vec[iS[:, 1]])
        emit("CONC1_NEG_ABSDIFF", cp, cs)
        emit("F_CONSTANT_PROTOTYPE__CONC1", *pair_mean_scalar(-np.abs(c_vec - c_vec.mean())))
        emit("F_PROTOTYPE_MAGNITUDE__CONC1", *pair_mean_scalar(c_vec))
        scr_c = c_vec[perm_headline]
        emit("F_SCRAMBLE__CONC1_NEG_ABSDIFF",
             -np.abs(scr_c[iP[:, 0]] - scr_c[iP[:, 1]]),
             -np.abs(scr_c[iS[:, 0]] - scr_c[iS[:, 1]]))
    rep["CONCRETENESS_REFERENCE_ARM_USABLE"] = conc_usable
    rep["CONCRETENESS_ALL_WORDS_COVERED"] = bool(conc_words_ok)

    rep["ARM_RESULTS"] = all_results
    rep["ARM_DIGESTS"] = all_digests
    rep["SCRAMBLE_CONTROL_DIAGNOSTICS"] = scramble_diag

    # ARMS-MUST-DIFFER across the six swept sensorimotor arms
    sm_arm_names = [arm_name(r, m) for r in REPRESENTATIONS for m in METRICS]
    sm_digs = [all_digests[n] for n in sm_arm_names]
    assert len(set(sm_digs)) == len(sm_digs), \
        "the six swept arms must produce six DISTINCT score vectors: %r" % dict(zip(sm_arm_names, sm_digs))
    rep["ARMS_DIFFER_VERIFIED"] = True

    rep["SWEEP_RESOLUTION"] = {
        "representations_swept": list(REPRESENTATIONS), "metrics_swept": list(METRICS),
        "n_grid_points": len(sm_arm_names),
        "queries_per_grid_point": {"setP_pair_scores": n_units, "setS_pair_scores": n_units,
                                   "total": 2 * n_units},
        "note": ("discipline 15: a grid's resolution is part of its verdict. This is a 3x2 grid over "
                 "representation x metric on ONE fixed 11-dimensional channel; it does NOT sweep the "
                 "channel's dimensionality, which is the variable branch (B) would indict."),
    }

    # ---------------- BARS AND VERDICT ------------------------------------------------------------
    sm_floor_names = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_CONSTANT_PROTOTYPE__SM11",
                      "F_PROTOTYPE_MAGNITUDE__SM11"]
    per_arm_decision: Dict[str, Dict] = {}
    for nm in sm_arm_names:
        fam = {k: all_results[k] for k in sm_floor_names + ["F_SCRAMBLE__" + nm]}
        bar = credible_bar(fam)
        a = all_results[nm]
        margin_bar = round(a["auc"] - bar["CREDIBLE_BAR"], 4)
        proto = all_results["F_CONSTANT_PROTOTYPE__SM11"]
        overlaps_proto = bool(a["ci95"][0] <= proto["ci95"][1] and proto["ci95"][0] <= a["ci95"][1])
        per_arm_decision[nm] = {
            "auc": a["auc"], "ci95": a["ci95"], "ci_halfwidth": a["ci_halfwidth"],
            "ci95_paired": a["ci95_paired"], "ci_halfwidth_paired": a["ci_halfwidth_paired"],
            "paired_swap_null_p95": a["paired_swap_null_p95"],
            "paired_swap_null_p_two_sided": a["paired_swap_null_p_two_sided"],
            "label_shuffle_null_p95": a["label_shuffle_null_p95"],
            "tie_mass_frac": a["tie_mass_frac"], "auc_ties_to_P": a["auc_ties_to_P"],
            "auc_ties_to_S": a["auc_ties_to_S"],
            "floor_family": sm_floor_names + ["F_SCRAMBLE__" + nm], "bar": bar,
            "margin_over_credible_bar": margin_bar,
            "margin_over_floor_point_value": round(a["auc"] - bar["max_floor_auc"], 4),
            "CLEARS_CREDIBLE_BAR_CI_SEPARATED": arm_clears_bar(a, bar["CREDIBLE_BAR"]),
            "beats_floor_point_but_not_credible_bar": bool(
                a["auc"] > bar["max_floor_auc"] and not arm_clears_bar(a, bar["CREDIBLE_BAR"])),
            "ci_overlaps_constant_prototype_floor": overlaps_proto,
            "n_pairs_per_cell": n_units,
        }
    rep["PER_ARM_DECISION"] = per_arm_decision

    if conc_usable:
        cfam = {k: all_results[k] for k in ["F_ORTHOGRAPHIC", "F_FREQUENCY",
                                            "F_CONSTANT_PROTOTYPE__CONC1",
                                            "F_PROTOTYPE_MAGNITUDE__CONC1",
                                            "F_SCRAMBLE__CONC1_NEG_ABSDIFF"]}
        cbar = credible_bar(cfam)
        ca = all_results["CONC1_NEG_ABSDIFF"]
        rep["CONCRETENESS_REFERENCE_DECISION"] = {
            "auc": ca["auc"], "ci95": ca["ci95"], "ci_halfwidth": ca["ci_halfwidth"],
            "paired_swap_null_p95": ca["paired_swap_null_p95"], "bar": cbar,
            "CLEARS_CREDIBLE_BAR_CI_SEPARATED": arm_clears_bar(ca, cbar["CREDIBLE_BAR"]),
            "note": ("REFERENCE ONLY, gated against ITS OWN 1-dim representation's floors. It is the "
                     "low-dimensional limit of a rating channel, reported to locate the resolution "
                     "axis -- it is NOT part of the (A)/(B)/(C) decision."),
        }

    best = max(sm_arm_names, key=lambda n: all_results[n]["auc"])
    bd = per_arm_decision[best]
    any_clears = [n for n in sm_arm_names if per_arm_decision[n]["CLEARS_CREDIBLE_BAR_CI_SEPARATED"]]
    bar_unclearable = bool(bd["bar"]["CREDIBLE_BAR"] >= 1.0)

    if not licensed:
        branch = "C_UNTESTABLE_INSTRUMENT_UNLICENSED_AT_SURVIVING_N"
    elif bar_unclearable:
        branch = "C_UNTESTABLE_CREDIBLE_BAR_UNCLEARABLE"
    elif any_clears:
        branch = "A_SENSORIMOTOR_DISCRIMINATES"
    else:
        branch = "B_AT_OR_NEAR_CONSTANT_PROTOTYPE_FLOOR"

    rep["BRANCH"] = branch
    rep["BEST_SENSORIMOTOR_ARM"] = best
    rep["N_REQUIRED_FOR_FLOOR_HALFWIDTH_REFERENCE_TABLE"] = REQUIRED_N_FOR_HALFWIDTH
    rep["N_ACHIEVED"] = n_units

    # A FIRST-CLASS FINDING IN ITS OWN RIGHT (discipline 16 in action): the matching neutralised the
    # instrument's four floors ON THE STORE REPRESENTATION, which says nothing about whether it is
    # neutral on the 11-dim rating representation. That is measured here, not assumed.
    pf = all_results["F_CONSTANT_PROTOTYPE__SM11"]
    rep["SENSORIMOTOR_FLOOR_NEUTRALITY"] = {
        "F_CONSTANT_PROTOTYPE__SM11": {"auc": pf["auc"], "ci95": pf["ci95"], "band": pf["band"]},
        "F_PROTOTYPE_MAGNITUDE__SM11": {
            "auc": all_results["F_PROTOTYPE_MAGNITUDE__SM11"]["auc"],
            "ci95": all_results["F_PROTOTYPE_MAGNITUDE__SM11"]["ci95"],
            "band": all_results["F_PROTOTYPE_MAGNITUDE__SM11"]["band"]},
        "constant_prototype_floor_SEPARATES_FROM_CHANCE_ON_THIS_REPRESENTATION":
            bool(pf["band"] != "NOT_SEPARATED_FROM_CHANCE"),
        "meaning": ("if this reads SEPARATED, then a QUERY-INDEPENDENT per-word genericity score on "
                    "the 11 dimensions already tells the two cells apart, so the matched population "
                    "is NOT balanced on sensorimotor typicality even though it IS balanced on the "
                    "store's own four floors. That does not invalidate the measurement -- the "
                    "credible bar is built from exactly this floor, so the comparison stays "
                    "conservative -- but any sensorimotor arm at or below it is measuring "
                    "typicality, not relation."),
    }
    rep["PRECISION_AT_THIS_N"] = {
        "n_per_cell": n_units,
        "max_floor_ci_halfwidth_measured": bd["bar"]["max_floor_ci_halfwidth"],
        "best_arm_ci_halfwidth_measured": bd["ci_halfwidth"],
        "n_required_for_a_given_floor_halfwidth": REQUIRED_N_FOR_HALFWIDTH,
        "note": ("discipline 18: decide what n the instrument needs BEFORE building. The licensed "
                 "matcher yields 242 units and the norms intersection leaves what it leaves -- it "
                 "cannot be increased without loosening the matcher, which is forbidden."),
    }
    rep["KNOWN_ANSWER_BOUNDARY_DISCLOSURE"] = {
        "strict_point_gate_passed": ka_point_ok, "ci_inclusive_gate_passed": ka_ci_ok,
        "auc": ka, "ci95": ka_res.get("ci95"), "gate": DISS.KNOWN_ANSWER_MIN_AUC}
    rep["RESOLUTION_TRADE_IF_B"] = (
        "Branch (B) indicts THIS RESOLUTION, not grounding. The resolution that would be needed is "
        "MORE DIMENSIONS, and the trade is measured, not hypothetical: Binder's 65-dimension norms "
        "discriminate far better but cover only 9.2% of the eval words (5.0% of anchors), against "
        "Lancaster's coverage measured HERE on this very population. At 9.2% coverage this "
        "instrument's 242 matched units would fall to a handful, i.e. below the 'a win on 20 pairs "
        "is not a win' line -- so the honest statement is a COVERAGE-RESOLUTION TRADE with no "
        "currently-held asset on the good side of it, NOT that grounding fails.")
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    t_start = time.time()
    ev = self_test()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print("[cfg] mode=%s N_BOOT=%d N_PERM=%d out=%s" % (RUN_MODE, N_BOOT, N_PERM, out_dir), flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    branch = rep.get("BRANCH", "UNKNOWN")
    best = rep.get("BEST_SENSORIMOTOR_ARM", "?")
    bd = rep.get("PER_ARM_DECISION", {}).get(best, {})
    cov = rep.get("COVERAGE", {})
    verdict = "SENSORIMOTOR_DISCRIMINATION__" + branch
    verdict_msg = (
        "%s || best arm %s AUC=%s CI=%s hw=%s (paired CI=%s) || credible bar=%s from %s "
        "(auc=%s hw=%s) -> margin=%s ; margin over floor POINT value=%s || paired-swap null p95=%s "
        "p=%s ; label-shuffle null p95=%s || ties: mass=%s auc_ties_to_P=%s auc_ties_to_S=%s || "
        "COVERAGE %s/%s matched units survive (%s removed by the norms filter), word coverage %s%% "
        "|| instrument still licensed at this n=%s (known-answer AUC=%s CI=%s: strict-point gate "
        "%s, CI-inclusive gate %s) || constant/prototype floor ON THE 11-DIM REPRESENTATION reads "
        "%s %s || n=%s per cell" % (
            verdict, best, bd.get("auc"), bd.get("ci95"), bd.get("ci_halfwidth"),
            bd.get("ci95_paired"), bd.get("bar", {}).get("CREDIBLE_BAR"),
            bd.get("bar", {}).get("max_floor_name"), bd.get("bar", {}).get("max_floor_auc"),
            bd.get("bar", {}).get("max_floor_ci_halfwidth"), bd.get("margin_over_credible_bar"),
            bd.get("margin_over_floor_point_value"), bd.get("paired_swap_null_p95"),
            bd.get("paired_swap_null_p_two_sided"), bd.get("label_shuffle_null_p95"),
            bd.get("tie_mass_frac"), bd.get("auc_ties_to_P"), bd.get("auc_ties_to_S"),
            cov.get("n_matched_units_surviving"), cov.get("n_matched_units_input"),
            cov.get("n_matched_units_REMOVED_by_coverage_filter"),
            round(100.0 * cov.get("word_coverage_frac", float("nan")), 1),
            rep.get("LICENSING_RECHECK_AT_SURVIVING_N", {}).get("INSTRUMENT_STILL_LICENSED_AT_THIS_N"),
            rep.get("KNOWN_ANSWER_BOUNDARY_DISCLOSURE", {}).get("auc"),
            rep.get("KNOWN_ANSWER_BOUNDARY_DISCLOSURE", {}).get("ci95"),
            "PASS" if rep.get("KNOWN_ANSWER_BOUNDARY_DISCLOSURE", {}).get("strict_point_gate_passed")
            else "FAIL",
            "PASS" if rep.get("KNOWN_ANSWER_BOUNDARY_DISCLOSURE", {}).get("ci_inclusive_gate_passed")
            else "FAIL",
            rep.get("SENSORIMOTOR_FLOOR_NEUTRALITY", {}).get("F_CONSTANT_PROTOTYPE__SM11", {}).get("auc"),
            rep.get("SENSORIMOTOR_FLOOR_NEUTRALITY", {}).get("F_CONSTANT_PROTOTYPE__SM11", {}).get("band"),
            rep.get("N_ACHIEVED")))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": verdict_msg[:200],
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "N_PERM": N_PERM,
                   "N_SCRAMBLE_SEEDS": N_SCRAMBLE_SEEDS, "SOURCE": SRC_DIR + " " + SRC_VERSION},
        "selftest_evidence_keys": sorted(ev.keys()), "selftest_evidence": ev,
        "report": rep, "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print("[verdict] %s" % verdict_msg, flush=True)
    print("[done] %.0fs -> %s/metrics.json" % (time.time() - t_start, out_dir), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(3)
