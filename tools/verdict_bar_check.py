#!/usr/bin/env python
"""Recompute every BANKED VERDICT against the standing bar and report the DISAGREEMENTS.

WHY THIS EXISTS. A cell's VERDICT STRING can say PASS while its actual claim does not survive
the standing bar, and the string is what every triage tool we own keys on. It fired twice on
2026-08-15/16:

  * `exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` reads `4WC_HARD_PASS`
    BEFORE and AFTER a re-run, so a reader scanning verdict strings sees no change -- but the
    banked ratios were a saturated 1.000/1.000/1.000/1.000 from ONE seed at N=512 in 0.09 s,
    and the real 5-seed N=16384 run gives 0.951/0.966/0.942/0.980.
  * `exp_meaning_asset_calibrated_floor_verdict_v1` landed announcing
    `ASSET_CLEARS_THE_CALIBRATED_FLOOR_ON_THE_INSTRUMENT_POPULATION`, yet 2 of its 3 "clearing"
    arms are NOT CI-separated from the hardened frequency channel.

Base rate, measured: 0 of 30 audited cells meet the standing bar (23 gate on a bare threshold
only, 6 have a floor but no CI, 1 has a CI but no floor) --
`.claude/scan-out/rerun-skipped-fulls.json` LEAD_4.

THE BAR, exactly (notes/LONG_TERM_PLAN.md sec 5; MEMORY.md "A GATE IS A CI-SEPARATED MARGIN"):
    a CI-SEPARATED margin over max(orthographic, frequency, scramble) on the IDENTICAL
    scorer / n / pool / gold -- never a bare absolute number -- plus a KNOWN-ANSWER arm
    licensing the instrument and a NULL arm licensing the effect, which fail INDEPENDENTLY.

THIS IS A REPORT, NOT AN ENFORCEMENT ACTION. It writes no metrics.json, no atom, no label, and
it never demotes anything. Demotion is the operator's call; this project has already issued 17
corrections-of-a-correction from premature demotion.

SINGLE SOURCE OF TRUTH. The bar predicate, the conservative MIN-ci_lo rule and the arm-role
classifier all live in `tools/c3_gate.py` and are IMPORTED here. This file does not re-implement
"does it pass" -- a second gate implementation would be the same class of defect the tool exists
to catch.

BRAIN-FIDELITY BLOCK (mandatory even for a tool):
  (a) This is INSTRUMENTATION. It makes NO brain-structure claim of any kind. There is no
      neural system this checker is modelled on, and inventing one would be exactly the
      laundering the fidelity gate bans. It measures our own bookkeeping, not cognition.
  (b) ORGAN REUSE: c3_gate.py (the bar predicate, the floor-role classifier, the MIN-ci_lo
      rule), session_start_hook.py's proven persisted-report pattern from result_index_join.py,
      and verification/ collection so it rides inside run_certification.py. Nothing new was
      built that already existed.
  (c) PINNED vs OUR-INVENTION. PINNED (by the standing rule, not by us): the bar itself; the
      three required floor roles; MIN-over-ci_lo as the conservative choice; "a chance baseline
      is not one of the three floors". OUR-INVENTION, being tested and freely revisable: the
      verdict-string pass/not-pass/ambiguous lexicon; the saturation heuristic (all decimal
      metrics in a verdict_msg pinned at 1.000); the disagreement-class precedence order; the
      shape-driven floor/CI extractor. Each is falsifiable by the self-test and by the
      AMBIGUOUS/UNPARSED residue this tool reports rather than hides.
  (d) SHELVE CRITERION, brain-framed: none applies. This is measurement overhead, not a bet on
      a mechanism, so there is nothing to shelve on a brain-fidelity ground. Retire it only if
      the verdict string stops being how results are cited.

Usage:
    python tools/verdict_bar_check.py --self-test          # prove it flags both offenders
    python tools/verdict_bar_check.py --scan               # full audit (~5 min), persists JSON
    python tools/verdict_bar_check.py --hook               # fast: read newest persisted report
    python tools/verdict_bar_check.py --cell <metrics.json>

Exit codes: 0 = ran (disagreements are DATA, not an error), 1 = hook found no/stale report,
2 = bad input, 3 = an input could not be read.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import math
import re
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.c3_gate import (  # noqa: E402  -- the ONE gate implementation, imported not forked
    BAR_FAILS, BAR_MEETS, BAR_NO_EVIDENCE, CONTROL_ROLES, REQUIRED_FLOOR_ROLES,
    arm_ceiling_shape, claim_arm_eligibility, classify_arm_role, evaluate_standing_bar,
    min_ci_lo,
)

DATA = os.path.join(REPO, "data")
REPORT_DIR = os.path.join(DATA, "verdict_bar_reports")

# ------------------------------------------------------------------ disagreement classes
AGREES = "AGREES"
STRING_PASSES_BAR_FAILS = "STRING_PASSES_BAR_FAILS"
NO_FLOOR = "NO_FLOOR"
NO_CI = "NO_CI"
SATURATED_CEILING = "SATURATED_CEILING"
NO_VERDICT = "NO_VERDICT"          # residue bucket; never silently dropped
CLASSES = (SATURATED_CEILING, STRING_PASSES_BAR_FAILS, NO_FLOOR, NO_CI, AGREES, NO_VERDICT)

# Set False only by --_disable_guard, to prove in the self-test that the guard is load-bearing.
GUARD_ENABLED = True


# ================================================================== 1. ENUMERATION (from disk)
def enumerate_metrics(data_dir: str = DATA) -> List[str]:
    """EVERY data/**/metrics.json, by os.walk. Filesystem first; the registry is reconciled
    against this, never the reverse (CLAUDE.md "Evidence discipline" sec 2).

    Deliberately NOT a glob: `Glob` returns empty SILENTLY on a bad path in this environment
    (CLAUDE.md sec 6), and an empty search is not evidence of absence. os.walk from an absolute
    path either yields entries or the directory does not exist, which is checked by the caller.

    Naming drift is handled by not depending on names at all: every directory is visited and
    every metrics.json is opened, so `_v2` / `_smoke` / `_full` / `_fulldev` / `_h100` /
    `_local` / `_cpu` / `_ckfix` suffixes are irrelevant to whether a cell is seen.
    """
    out: List[str] = []
    for root, dirs, files in os.walk(data_dir):
        dirs.sort()
        if "metrics.json" in files:
            out.append(os.path.join(root, "metrics.json"))
    return sorted(out)


# ================================================================== 2. VERDICT STRING
# OUR-INVENTION (see brain-fidelity block c): this lexicon is a hypothesis about how our own
# verdict vocabulary reads, not a pinned rule. NEGATIVE tokens are tested FIRST and win, because
# 'NOT_SEPARATED' contains 'SEPARATED' and 'HARD_FAIL' would otherwise be read by a bare 'PASS'
# scan of a longer message. Anything positive-sounding but outside the lexicon is reported as
# AMBIGUOUS rather than assumed benign -- the vocabulary went from 13 strings in June to 444 in
# July, so silent assumption is how a real offender would be missed.
_NEG = re.compile(
    r"NOT[_ ]SEPARATED|HARD[_ -]?FAIL|\bFAIL(ED|S|URE)?\b|_FAIL\b|MIDDLE[_ ]BAND|INCONCLUSIVE|"
    r"\bUNKNOWN\b|\bPARTIAL\b|SANITY[_ ]FAIL|\bNOOP\b|\bKILLED\b|REFUTED|\bBELOW\b|"
    r"NOT[_ ]EVALUABLE|NO[_ ]SIGNAL|\bNULL[_ ]RESULT\b|DOES[_ ]NOT|NEVER[_ ]RAN", re.IGNORECASE)
_POS = re.compile(
    r"HARD[_ -]?PASS|\bPASS(ED|ES)?\b|\bCLEARS?\b|\bSEPARATED\b|\bABOVE\b|CONFIRMED|"
    r"\bSUPPORTED\b|\bWINS?\b|OUTSIDE[_ ]BANDS", re.IGNORECASE)

READS_PASS, READS_NOT_PASS, READS_AMBIGUOUS, READS_NONE = (
    "READS_PASS", "READS_NOT_PASS", "READS_AMBIGUOUS", "READS_NONE")

# Verdict strings are SNAKE_CASE / PIPE-joined far more often than they are prose, so `\b` does
# not fire inside them: `_` is a word character, which makes `\bPASS\b` miss `KF45_SMOKE_PASS`
# and `\bCLEARS\b` miss `ASSET_CLEARS_THE_CALIBRATED_FLOOR`. Both misses were caught by the
# self-test on the two REAL offender strings before this normalisation existed. Every match runs
# against the token-normalised form.
_TOKEN_SPLIT = re.compile(r"[^A-Za-z0-9]+")


def _normalise_verdict(s: str) -> str:
    return " " + _TOKEN_SPLIT.sub(" ", str(s)).strip() + " "

# Where a verdict string actually lives, in on-disk frequency order (measured 2026-08-16 over
# all 7,768 metrics.json: .verdict 7530, .verdict_msg 7517, .summary 6671, then the long tail).
_VERDICT_KEYS = ("verdict", "summary", "verdict_msg", "VERDICT", "final_verdict", "result")


def extract_verdict(m: dict) -> Tuple[Optional[str], Optional[str]]:
    """(verdict string, the key path it came from). Top-level first, then one nested level."""
    for k in _VERDICT_KEYS:
        v = m.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip(), k
    for outer in ("summary", "verdict_detail", "detail", "result", "results"):
        blk = m.get(outer)
        if isinstance(blk, dict):
            for k in _VERDICT_KEYS:
                v = blk.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip(), f"{outer}.{k}"
    return None, None


def verdict_reads_as(s: Optional[str]) -> str:
    """READS_PASS / READS_NOT_PASS / READS_AMBIGUOUS / READS_NONE."""
    if not s:
        return READS_NONE
    t = _normalise_verdict(s)
    if _NEG.search(t):
        return READS_NOT_PASS
    toks = t.split()
    for i, tok in enumerate(toks):
        if not _POS.search(f" {tok} "):
            continue
        if _negated_before(toks, i):
            continue
        return READS_PASS
    return READS_AMBIGUOUS


_NEGATORS = {"NO", "NOT", "NONE", "NEVER", "CANNOT", "CANT", "WITHOUT", "DO", "DOES", "DID",
             "FAILS", "FAILED", "UNABLE", "NEITHER", "NOR"}


def _negated_before(tokens: Sequence[str], i: int) -> bool:
    """Is the positive token at `tokens[i]` negated by a negator appearing EARLIER in the string?

    Measured need, not a hypothetical: the first cut read
    `NO_ASSET_CLEARS_THE_STRONGEST_FLOOR` and `NORMS_DO_NOT_CLEAR_CI_SEPARATED` as PASSES and
    put four honest negatives into the disagreement list.

    Scope is the PREFIX, not a fixed window. A 2-token window was tried first and still read
    `NORMS DO NOT CLEAR CI SEPARATED` as a pass, because the negation lands on `CLEAR` while the
    match that decided the outcome was `SEPARATED` three tokens later -- one predicate, two
    positive words. Prefix scope is nonetheless directional, not whole-string: it deliberately
    does NOT flip `HARD_PASS_STRUCTURAL_NO_LEAK`, where the `NO` comes AFTER the `PASS` and
    negates the leak rather than the pass. Where a long prose message makes this over-negate,
    the result is READS_AMBIGUOUS, which is REPORTED as residue rather than assumed benign.
    """
    return any(tokens[j].upper() in _NEGATORS for j in range(i))


# ================================================================== 3. SATURATION
# A metric pinned at 1.000 across every arm is not a pass, it is a broken measurement. A
# SCRAMBLE control scored 1.0000 on the facet axis in one of 2026-08-15's cells; the rank-3 cell
# banked 1.000/1.000/1.000/1.000 from a 0.09 s run.
#
# Rule (a), verdict_msg: parse `name=<decimal>` tokens. The DECIMAL POINT is the discriminator
# that keeps config fields out -- `N=512` and `seeds=1` are integers and are not metrics, while
# `baseline_ratio=1.000` is. Requires >= 2 such tokens (one number at 1.0 is not a "pinned
# across all arms" shape) and ALL of them at 1.0.
_KV_DECIMAL = re.compile(r"([A-Za-z_][A-Za-z0-9_.|]*)\s*=\s*(-?\d+\.\d+)")
_CEIL_TOL = 1e-9


def _is_ceiling(x: float) -> bool:
    return abs(float(x) - 1.0) <= _CEIL_TOL


def saturation_scan(m: dict, verdict_msg: Optional[str]) -> dict:
    """Detect the saturation SHAPE specifically: HEADLINE metric at ceiling for EVERY arm.

    Two tiers, and the distinction is load-bearing:

    HEADLINE (fires SATURATED_CEILING). The numbers the cell itself quotes in its verdict_msg --
    those ARE the headline, by the cell's own choice of what to report. `baseline_ratio=1.000
    A_4way_ratio=1.000 B_cleanup_ratio=1.000 C_combined_ratio=1.000 C_verify=1.000` is the
    banked rank-3 message and is exactly this shape. For cells that wrote no numeric verdict_msg
    at all, a score-shaped metric pinned at ceiling across an arm-shaped container is promoted to
    headline, because otherwise those cells have no headline to check.

    SECONDARY (reported, does NOT set the class). Any other metric at ceiling across siblings.
    First cut of this tool made every such hit primary and produced 949 flags against 217 real
    ones -- `select_tau`, `weight`, `n_valid_seeds` and a boolean field literally named
    `ceiling`. A detector that flags a third of the corpus tells the operator nothing. The hits
    are still recorded so the tightening is auditable rather than a silent threshold change.
    """
    headline: List[dict] = []
    secondary: List[dict] = []

    # (a) the verdict_msg key=decimal shape -- the cell's OWN choice of headline numbers.
    msg_had_decimals = False
    if verdict_msg:
        toks = [(k, float(v)) for k, v in _KV_DECIMAL.findall(verdict_msg)]
        msg_had_decimals = bool(toks)
        if len(toks) >= 2 and all(_is_ceiling(v) for _, v in toks):
            headline.append({"where": "verdict_msg", "metric": "all key=decimal tokens",
                             "arms": [k for k, _ in toks], "values": [v for _, v in toks],
                             "tier": "headline"})

    # (b) the STRUCTURAL shape: >=2 ARM-shaped sub-dicts sharing a SCORE-shaped metric key, all
    #     at ceiling.
    for parent_path, node in _iter_dicts(m):
        parent_key = _dot(parent_path)
        subs = {k: v for k, v in node.items() if isinstance(v, dict)}
        if len(subs) < 2 or not _looks_like_arm_container(subs):
            continue
        common: Dict[str, List[Tuple[str, float]]] = {}
        for arm, sub in subs.items():
            for mk, mv in sub.items():
                if isinstance(mv, bool) or not isinstance(mv, (int, float)):
                    continue
                common.setdefault(mk, []).append((arm, float(mv)))
        for mk, pairs in common.items():
            if len(pairs) < 2 or len(pairs) != len(subs):
                continue
            if _NON_METRIC_KEY.search(mk) or _HYPERPARAM_KEY.search(mk):
                continue
            if not all(_is_ceiling(v) for _, v in pairs):
                continue
            is_score = bool(_SCORE_KEY.search(mk))
            hit = {"where": parent_key or "<root>", "metric": mk,
                   "arms": [a for a, _ in pairs], "values": [v for _, v in pairs],
                   "tier": "headline" if (is_score and not msg_had_decimals) else "secondary"}
            (headline if hit["tier"] == "headline" else secondary).append(hit)

    return {"saturated": bool(headline) and GUARD_ENABLED,
            "evidence": headline[:6],
            "secondary_ceiling_shapes": secondary[:6],
            "n_headline_shapes": len(headline), "n_secondary_shapes": len(secondary)}


# A metric is a SCORE; tau/alpha/weight/threshold are knobs the experimenter SET, and a knob
# sitting at 1.0 in every arm is a configuration, not a saturated measurement.
_SCORE_KEY = re.compile(
    r"(^|_)(acc|accuracy|hit|hits|recall|precision|f1|auc|rho|corr|correlation|score|ratio|"
    r"rate|frac|fraction|mrr|ndcg|map|success|coverage|agreement|separation|margin)($|_)|"
    r"hit_?at_?\d+|top_?\d+", re.IGNORECASE)
_HYPERPARAM_KEY = re.compile(
    r"^(tau|alpha|beta|gamma|lambda|eta|lr|weight|weights|temperature|temp|threshold|thresh|"
    r"tol|tolerance|sigma|mu|p|q|w|momentum|decay|dropout|scale|gain_param|hp|hf|"
    r".*_tau|.*_alpha|.*_beta|.*_weight|.*_threshold|.*_lr)$", re.IGNORECASE)
# A container keyed by numbers is a SWEEP (acc_grid: {800: ..., 1600: ...}), not a set of arms.
_NUMERIC_KEY = re.compile(r"^-?\d+(\.\d+)?$")


def _looks_like_arm_container(subs: Dict[str, dict]) -> bool:
    """True when the sibling sub-dicts read as ARMS rather than as a numeric sweep grid."""
    named = [k for k in subs if not _NUMERIC_KEY.match(str(k))]
    return len(named) >= 2 and len(named) == len(subs)


# Counts, sizes and identifiers are not headline METRICS; a run with 1 seed is not "at ceiling".
_NON_METRIC_KEY = re.compile(
    r"^(n|N|k|K|w|d|dim|seed|seeds|n_seeds|n_chains|n_items|n_pairs|n_units|n_bootstrap|"
    r"count|counts|steps|epochs|iters?|reps?|trials|elapsed|elapsed_s|wall_s|pid|rank|"
    r"version|config_version|index|idx|id|size|len|length|batch|.*_count|.*_n)$", re.IGNORECASE)


def _iter_dicts(o, key: Tuple[str, ...] = (), depth: int = 0,
                budget: Optional[List[int]] = None):
    """Yield (path TUPLE, dict) for every dict in the tree, depth- and budget-bounded.

    A TUPLE of segments, not a dotted string. That is a correctness fix, not a style choice:
    arm names on disk contain literal dots (`S_INPLACE_d256_f0.020__KA` -- the active fraction
    is in the name), so a dotted path splits the arm's name in half and `path.rsplit('.')` hands
    back `020__KA` as if it were a whole segment. On 2026-08-16 that is one of the three
    independent reasons a planted-answer arm was chosen to carry a cell's claim. A tuple cannot
    lose a segment boundary, whatever a key contains.

    Budget exists because 9 metrics.json on disk exceed 1 MB (max 6.5 MB) and an unbounded walk
    of those dominates the scan. Bounded traversal is a measured cost decision, and the bound is
    REPORTED per cell (`traversal_truncated`) rather than hidden -- an audit that silently gives
    up is the failure mode this whole tool is about.
    """
    if budget is None:
        budget = [MAX_NODES]
    if depth > MAX_DEPTH or budget[0] <= 0:
        return
    if isinstance(o, dict):
        budget[0] -= 1
        yield key, o
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                yield from _iter_dicts(v, key + (str(k),), depth + 1, budget)
    elif isinstance(o, list):
        for v in o[:MAX_LIST]:
            if isinstance(v, (dict, list)):
                yield from _iter_dicts(v, key + ("[]",), depth + 1, budget)


def _dot(path: Tuple[str, ...]) -> str:
    """Display form of a path tuple. For HUMAN OUTPUT ONLY -- never parsed back."""
    return ".".join(path)


MAX_DEPTH = 8
MAX_NODES = 20000
MAX_LIST = 8


# ================================================================== 4. FLOOR + CI EVIDENCE
_CI_LO_KEYS = ("ci_lo", "ci_low", "ci_lower", "lo", "lower")
_CI_PAIR_KEYS = ("ci95", "ci", "ci_95", "conf_int", "confidence_interval", "ci99")
_MARGIN_SUBKEYS = ("margin", "delta", "diff", "difference", "gain", "d")
# Fields whose VALUE names the floor a sibling margin was taken against.
_FLOOR_NAMING_FIELDS = ("strongest_floor", "floor_source", "floor_arm", "vs", "vs_arm",
                        "against", "baseline_arm", "control_arm", "floor")


def _ci_lo_of(node: dict) -> Optional[float]:
    """Lower bound of an interval on THIS node, or None. Handles both on-disk encodings:
    scalar `ci_lo` (2257 occurrences) and 2-element `ci95` (1515)."""
    for k in _CI_LO_KEYS:
        v = node.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
    for k in _CI_PAIR_KEYS:
        v = node.get(k)
        if (isinstance(v, (list, tuple)) and len(v) == 2
                and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)):
            return float(v[0])
    for sk in _MARGIN_SUBKEYS:
        sub = node.get(sk)
        if isinstance(sub, dict):
            got = _ci_lo_of(sub)
            if got is not None:
                return got
    return None


def _floor_role_of_key(key: str) -> Optional[str]:
    """Role of the floor a delta-shaped key compares AGAINST.

    `d_A4_BOTH_minus_F_FREQUENCY` -> frequency (the RIGHT side of `_minus_` is the floor).
    A plain floor-named key -> its own role.
    """
    s = str(key)
    for sep in ("_minus_", "-minus-", "_vs_", "_over_", "_against_"):
        if sep in s:
            return classify_arm_role(s.split(sep, 1)[1])
    return classify_arm_role(s)


def floor_evidence(m: dict) -> dict:
    """Every floor role the cell RECORDS, and every CI-bearing margin against a floor.

    Shape-driven, not name-listed, and it reports what it could not interpret. Three on-disk
    encodings are covered, all verified against real files:
      1. `DECOMPOSED_per_floor: {FLOOR: {margin: {point, ci95:[lo,hi]}, band}}`
         (exp_meaning_asset_calibrated_floor_verdict_v1)
      2. `bootstrap.deltas: {d_{ARM}_minus_{FLOOR}: {ci_lo, ci_hi}}`
         (exp_meaning_supply_separation_v1 -- the shape c3_gate._floor_ci_lo already reads)
      3. `margin_over_strongest_floor: {ci95:[lo,hi]}` beside `strongest_floor: "<NAME>"`
         (exp_meaning_asset_pretrained_positive_control_v1)
    """
    roles_present: Dict[str, List[str]] = {}
    pairs: List[Tuple[float, str]] = []      # (ci_lo, source) -- fed to c3_gate.min_ci_lo
    roles_with_ci: set = set()
    per_arm: Dict[str, List[Tuple[float, str, str]]] = {}
    # For each scoped arm: every path SEGMENT that could name it, and the arm's own metrics dict.
    # Both are required by the claim-arm eligibility check -- classifying only the last segment
    # is what let a planted-answer arm carry a claim on 2026-08-16.
    per_arm_segments: Dict[str, set] = {}
    per_arm_nodes: Dict[str, dict] = {}
    node_by_path: Dict[Tuple[str, ...], dict] = {}
    tie_conventions: set = set()
    truncated = False

    budget = [MAX_NODES]
    for kpath, node in _iter_dicts(m, budget=budget):
        node_by_path[kpath] = node
        last = kpath[-1].replace("[]", "") if kpath else ""

        # --- roles PRESENT: from dict keys, and from the VALUE of a floor-naming field
        for k, v in node.items():
            r = classify_arm_role(k)
            if r:
                roles_present.setdefault(r, []).append(str(k))
            if k in _FLOOR_NAMING_FIELDS and isinstance(v, str):
                r2 = classify_arm_role(v)
                if r2:
                    roles_present.setdefault(r2, []).append(v)
            elif k in _FLOOR_NAMING_FIELDS and isinstance(v, dict):
                for fk in v:
                    r2 = classify_arm_role(fk)
                    if r2:
                        roles_present.setdefault(r2, []).append(str(fk))

        # --- CI-bearing margins against a named floor
        # (i) this node IS the margin, and its own key names the floor
        # TIE CONVENTION, MADE EXPLICIT (2026-08-16). Rank-shaped margins DO reach this tool:
        # on the cell audited today, 30 of 55 eligible arms bind on a TOP-50 margin rather than
        # on hit@1. Top-50 recall and median rank are TIE-CONVENTION DEPENDENT -- rank =
        # #(scores strictly greater) + 1 gives a gold buried in a tie of thousands rank 1, while
        # #(>=) does not -- and on that cell the trigram/spelling channel carries 15.3% of the
        # eligible pool tied with the gold while the dense read-out carries 0.0%. A cell that
        # publishes BOTH conventions (the honest thing to do) must not have the flattering one
        # picked for it silently, so the convention is APPENDED TO THE FLOOR NAME and travels
        # into `binding_floor` in every record. min_ci_lo across the two conventions then makes
        # the CONSERVATIVE one bind, and says so by name.
        # NOT IN SCOPE and deliberately not done: choosing which convention is correct, or
        # re-scoring any cell. This tool reports; the operator decides.
        def _tie_convention(path: Tuple[str, ...]) -> Optional[str]:
            for seg in path:
                if _TIE_CONVENTION_RE.search(str(seg)):
                    return str(seg)
            return None

        def _record(arm_path: Tuple[str, ...], lo: float, fname: str, role: str) -> None:
            """Bucket one CI-bearing floor margin under the arm that owns it, and keep BOTH the
            arm's naming segments and the arm's own metrics dict -- the claim-arm eligibility
            check needs each, and having only the tail segment is what produced the false pass."""
            arm, segs, arm_prefix = _owning_arm(arm_path)
            conv = _tie_convention(kpath)
            if conv:
                fname = f"{fname}|{conv}"
                tie_conventions.add(conv)
            pairs.append((lo, fname))
            roles_with_ci.add(role)
            per_arm.setdefault(arm, []).append((lo, fname, role))
            per_arm_segments.setdefault(arm, set()).update(segs)
            if arm not in per_arm_nodes:
                nd = node_by_path.get(arm_prefix)
                if isinstance(nd, dict):
                    per_arm_nodes[arm] = nd

        role = _floor_role_of_key(last)
        if role in REQUIRED_FLOOR_ROLES:
            lo = _ci_lo_of(node)
            if lo is not None:
                # THE FINAL SEGMENT IS THE FLOOR, not part of the arm's name -- drop it before
                # naming the arm. Keeping it would disqualify every honest arm whose margin is
                # recorded under a floor-named child (the genuine synthetic fixture has exactly
                # that shape: TREATMENT.DECOMPOSED_per_floor.A_ORTHOGRAPHIC).
                _record(kpath[:-1], lo, last, role)

        # (ii) this node carries a margin whose floor is named by a SIBLING field
        for k, v in node.items():
            if not isinstance(v, dict):
                continue
            if _floor_role_of_key(k) in REQUIRED_FLOOR_ROLES:
                continue                                   # already handled by (i) on the child
            if not any(tok in str(k).lower()
                       for tok in ("margin", "delta", "separation", "diff", "gain")):
                continue
            lo = _ci_lo_of(v)
            if lo is None:
                continue
            fname = None
            for f in _FLOOR_NAMING_FIELDS:
                cand = node.get(f)
                if isinstance(cand, str):
                    fname = cand
                    break
            r = classify_arm_role(fname) if fname else None
            if r in REQUIRED_FLOOR_ROLES:
                # Here the floor is named by a SIBLING FIELD, not by a path segment, so the whole
                # path belongs to the arm and nothing is dropped.
                _record(kpath, lo, fname, r)
    if budget[0] <= 0:
        truncated = True

    return {
        "floor_roles_present": sorted(roles_present),
        "floor_role_names": {r: sorted(set(v))[:8] for r, v in sorted(roles_present.items())},
        "floor_margin_ci_pairs": pairs,
        "floor_roles_with_margin_ci": sorted(roles_with_ci),
        "per_arm_floor_cis": {a: v for a, v in sorted(per_arm.items())},
        "per_arm_name_segments": {a: sorted(s) for a, s in sorted(per_arm_segments.items())},
        "per_arm_nodes": per_arm_nodes,
        "tie_conventions_present": sorted(tie_conventions),
        "traversal_truncated": truncated,
    }


# A rank/top-k metric computed under a NAMED tie convention. Both spellings found on disk:
# `CONSERVATIVE_ties` / `optimistic_ties`, and the `_tie(s)` variants.
_TIE_CONVENTION_RE = re.compile(r"_ties$|^ties_|_tie$|conservative_tie|optimistic_tie",
                                re.IGNORECASE)


_CONTAINER_KEYS = ("DECOMPOSED_per_floor", "deltas", "bootstrap", "rows", "results",
                   "per_arm", "per_w", "per_population", "margin", "delta")
# A path segment that is a CONTAINER, not an arm name. Widened to a regex 2026-08-16: the fixed
# tuple above missed `MARGIN_per_floor`, `TOP50_MARGIN_per_floor`, `regimes` and the
# tie-convention level `CONSERVATIVE_ties` / `optimistic_ties`, so `_owning_arm` named the arm
# `MARGIN_per_floor` and pushed the REAL arm name into the scope slot -- where the old
# control check, which looked only at the tail, could never see it.
_CONTAINER_RE = re.compile(
    r"^(per_arm|per_w|per_population|per_seed|per_regime|per_floor|regimes|rows|results|"
    r"bootstrap|deltas|delta|margin|margins|arms|by_arm|by_d|metrics|summary|the_bar)$"
    r"|_per_floor$|^decomposed_per_floor$|_ties$|^ci9?5?$", re.IGNORECASE)
# `the_bar` and `by_d` are on that list for a SCOPE reason, not a cosmetic one. In
# data/exp_meaning_lift_population_code_v1 the margins live at
# `by_d.<D>.per_arm.<ARM>.THE_BAR.MARGIN_per_floor.<FLOOR>`. Without `the_bar` the walker names
# the arm `THE_BAR` and pushes the real arm into the scope slot, so `by_d.256.per_arm.C4_PHASOR`
# and `by_d.1024.per_arm.C4_PHASOR` BOTH label as `C4_PHASOR::THE_BAR` and their margins POOL --
# and the standing bar requires the IDENTICAL scorer / n / pool / gold, so merging a 256- and a
# 1024-dimensional run is precisely the comparison it forbids. With both dropped the label is
# `1024::C4_PHASOR` / `256::C4_PHASOR` and the two dimensionalities are judged apart.


def _owning_arm(kpath: Tuple[str, ...]) -> Tuple[str, List[str], Tuple[str, ...]]:
    """(`<scope>::<arm>`, the arm's naming SEGMENTS, the path PREFIX of the arm's own dict).

    The SCOPE is kept deliberately. Without it, an arm name reused across populations (e.g.
    `ASSET_NORMS12` appears under both SIMLEX999 and WORDSIM353 in
    exp_meaning_asset_calibrated_floor_verdict_v1) would merge its margins into one bucket, and
    the bar requires the IDENTICAL scorer / n / pool / gold. Merging two pools is the very
    comparison the bar forbids, so the key must keep them apart.

    The SEGMENTS are returned as well, and this is the load-bearing change of 2026-08-16: the
    caller must be able to test EVERY name that could identify the arm, not just the one chosen
    for the display label. `kpath` must already have any trailing FLOOR segment removed by the
    caller -- the floor names the comparison, not the arm.
    """
    parts = [p for p in kpath
             # SEARCH, not MATCH: the non-anchored alternatives (`_per_floor$`, `_ties$`) exist
             # precisely to catch `MARGIN_per_floor` / `TOP50_MARGIN_per_floor` /
             # `CONSERVATIVE_ties`, none of which START with the token. `.match` anchored at
             # position 0 and silently caught none of them.
             if p and p != "[]" and p not in _CONTAINER_KEYS and not _CONTAINER_RE.search(p)]
    named = [p for p in parts if classify_arm_role(p) not in REQUIRED_FLOOR_ROLES]
    if not named:
        return (_dot(kpath) or "<cell>"), list(parts), kpath
    arm = named[-1]
    scope = named[-2] if len(named) >= 2 else None
    label = f"{scope}::{arm}" if scope else arm
    # The arm's own dict is the prefix of kpath ending at the LAST occurrence of `arm`.
    prefix = kpath
    for i in range(len(kpath) - 1, -1, -1):
        if kpath[i] == arm:
            prefix = kpath[:i + 1]
            break
    return label, named, prefix


# Kept as a name for the report; the authoritative list is tools/c3_gate.CONTROL_ROLES and this
# aliases it rather than restating it, because two lists of "what counts as a control" is the
# same second-implementation defect this tool exists to catch.
_CONTROL_ROLES = CONTROL_ROLES


def _finite(x) -> bool:
    """True only for a real, finite number. NaN and +/-inf are NOT evidence."""
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _best_treatment_arm(per_arm: Dict[str, list],
                        segments: Optional[Dict[str, list]] = None,
                        nodes: Optional[Dict[str, dict]] = None):
    """(best ELIGIBLE arm, its (ci_lo, floor) pairs, all scored arms, the rejected arms).

    "Best" = highest WITHIN-SCOPE min ci_lo among arms ELIGIBLE to carry a claim. Eligibility is
    tools/c3_gate.claim_arm_eligibility and it is FAIL-CLOSED: a control arm, a validity-scaffold
    arm (known-answer / planted / oracle) and an arm pinned at the instrument ceiling are all
    removed. A control arm losing to a floor is the design working, not a disagreement, so
    scoring the cell on its controls would flag every well-built cell in the repo; and a
    PLANTED-ANSWER arm BEATING a floor is likewise the design working, which is why scoring the
    cell on one produced a MEETS_BAR at +0.9044 on a cell whose every genuine arm is negative.

    The rejected arms are RETURNED, not dropped. An exclusion nobody can see is indistinguishable
    from a filter that matched nothing, which is exactly how `if base in src` inflated its own
    count in this repo.
    """
    segments = segments or {}
    nodes = nodes or {}
    scores: Dict[str, dict] = {}
    rejected: Dict[str, dict] = {}
    for scoped, cis in per_arm.items():
        segs = segments.get(scoped) or [p for p in scoped.replace("::", " ").split() if p]
        elig = claim_arm_eligibility(segs, nodes.get(scoped))
        lo, src = min_ci_lo([(c[0], c[1]) for c in cis])
        # NON-FINITE bounds are UNCLASSIFIABLE, and unclassifiable is not a pass. Measured need:
        # the d=256 f=0.002 / f=0.005 arms of the cell that produced the false pass round to
        # k=1 active unit, their permutation null has zero variance and their margin CIs come
        # back NaN. NaN comparisons are all False, so a NaN would slip through `ci_lo > 0` as a
        # FAILS_BAR by accident rather than by rule -- and `max()` over a set containing NaN is
        # order-dependent, so it could equally have been chosen as the BEST arm. Neither is a
        # decision anyone made. Reject explicitly and say so.
        nonfinite = [c[1] for c in cis if not _finite(c[0])]
        if nonfinite:
            rejected[scoped] = {"min_ci_lo": None, "binding_floor": None,
                                "reason": "NON_FINITE_CI",
                                "detail": "floor margins with a non-finite bound: "
                                          + ", ".join(sorted(set(nonfinite))[:4]),
                                "evidence": None}
            continue
        if not elig["eligible"]:
            if lo is not None:
                rejected[scoped] = {"min_ci_lo": lo, "binding_floor": src,
                                    "reason": elig["reason"], "detail": elig["detail"],
                                    "evidence": elig["evidence"]}
            continue
        if lo is None:
            continue
        scores[scoped] = {"min_ci_lo": lo, "binding_floor": src,
                          "floor_roles": sorted({c[2] for c in cis})}
    if not scores:
        return None, [], {}, rejected
    best = max(scores, key=lambda k: scores[k]["min_ci_lo"])
    return best, [(c[0], c[1]) for c in per_arm[best]], scores, rejected


def _match_declared_arm(declared: str, per_arm: Dict[str, list]) -> List[Tuple[str, list]]:
    """Every scoped bucket belonging to a declared arm name. A declared name may legitimately
    resolve to MORE than one scope (the same arm scored on two populations); each is checked on
    its own, never pooled -- see _owning_arm."""
    hits = [(k, v) for k, v in per_arm.items()
            if k == declared or k.endswith("::" + declared)]
    if hits:
        return hits
    tail = declared.split("|")[-1]
    return [(k, v) for k, v in per_arm.items() if k == tail or k.endswith("::" + tail)]


# ================================================================== 5. CHECK ONE CELL
def check_cell(path: str) -> dict:
    """Recompute ONE banked verdict against the bar. Never raises on a bad file."""
    rec: dict = {"metrics_path": path.replace("\\", "/"),
                 "cell": os.path.basename(os.path.dirname(path))}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            m = json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        rec.update({"unreadable": f"{type(exc).__name__}: {exc}",
                    "disagreement_class": NO_VERDICT, "classes": [NO_VERDICT]})
        return rec
    if not isinstance(m, dict):
        rec.update({"unreadable": "metrics.json is not a JSON object",
                    "disagreement_class": NO_VERDICT, "classes": [NO_VERDICT]})
        return rec

    verdict, vkey = extract_verdict(m)
    reads = verdict_reads_as(verdict)
    vmsg = m.get("verdict_msg") if isinstance(m.get("verdict_msg"), str) else None
    if vmsg is None and isinstance(m.get("summary"), str):
        vmsg = m["summary"]

    sat = saturation_scan(m, vmsg)
    fe = floor_evidence(m)

    known = any(classify_arm_role(k) == "known_answer" for k in _all_keys(m))
    nulla = any(classify_arm_role(k) == "null_control" for k in _all_keys(m))

    # WHICH ARM CARRIES THE CELL'S CLAIM. A cell-wide MIN over every comparison it recorded is
    # the WRONG cell-level predicate: it pools scopes (violating "IDENTICAL scorer/n/pool/gold")
    # and it is dominated by the CONTROL arms, which are supposed to lose. Measured: pooling put
    # exp_meaning_asset_fair_test_v1 at min_ci_lo -115 -- a real number, from its planted
    # GOLD_ORTHO population where an orthographic floor legitimately scores a 118x lift, and
    # nothing to do with whether any treatment arm clears.
    #
    # So: score each TREATMENT arm WITHIN ITS OWN SCOPE (min over that scope's floors, the
    # c3_gate rule), drop arms that are themselves floors / nulls / known-answer arms, and let
    # the cell's claim stand on its BEST arm. The pooled minimum is kept as an informational
    # field, never as the verdict.
    best_arm, best_pairs, arm_scores, rejected_arms = _best_treatment_arm(
        fe["per_arm_floor_cis"], fe["per_arm_name_segments"], fe["per_arm_nodes"])
    pooled_lo, pooled_src = min_ci_lo(fe["floor_margin_ci_pairs"])
    bar = evaluate_standing_bar(
        floor_ci_pairs=best_pairs if best_arm else fe["floor_margin_ci_pairs"],
        floor_roles_present=fe["floor_roles_present"],
        floor_roles_with_ci=(sorted({c[2] for c in fe["per_arm_floor_cis"][best_arm]})
                             if best_arm else fe["floor_roles_with_margin_ci"]),
        has_known_answer_arm=known, has_null_arm=nulla,
        arm_name=best_arm or rec["cell"])

    # ---------------------------------------------------------------- FAIL CLOSED
    # A checker that guesses in the PASSING direction is worse than no checker. If no arm is
    # ELIGIBLE to carry the claim -- every candidate is a control, a planted-answer arm, or
    # pinned at the instrument ceiling -- then the cell has not been shown to clear anything,
    # whatever the pooled numbers say. That is NO_EVIDENCE, never MEETS_BAR.
    #
    # This is the only place the tool is allowed to OVERRIDE evaluate_standing_bar, and it may
    # only ever move a status DOWNWARD. Asserted by
    # verification/test_verdict_bar_checker.py::test_fail_closed_never_upgrades.
    claim_arm_status = "CLAIM_ARM_IDENTIFIED"
    if best_arm is None:
        claim_arm_status = ("NO_ELIGIBLE_CLAIM_ARM" if rejected_arms
                            else "NO_ARM_WITH_A_FLOOR_MARGIN_CI")
        bar["bar_evidence_complete"] = False
        if rejected_arms:
            # Arms EXIST, and every one of them is a control, a validity-scaffold /
            # planted-answer arm, or pinned at the instrument ceiling. Two things must not
            # happen here. MEETS_BAR is obviously wrong. But FAILS_BAR is ALSO wrong, and
            # wrong in the direction this project has paid for: it asserts a MEASURED
            # refutation of a claim arm that does not exist. Without this branch the fallback
            # pools every comparison in the cell -- including the deliberately-losing null
            # arms -- and reports their negative bound as the cell's verdict. "We could not
            # identify a claim arm" and "we recomputed it and it does not separate" are
            # different findings; c3_gate.evaluate_standing_bar exists partly to keep them
            # apart, and 17 corrections-of-a-correction came from conflating them.
            prior = bar["status"]
            bar["status"] = BAR_NO_EVIDENCE
            bar["fail_closed_override"] = (
                f"{prior} withheld: no arm is eligible to carry the claim (every candidate is a "
                "control, a validity-scaffold/planted-answer arm, pinned at ceiling, or has a "
                "non-finite bound). See claim_arm_rejected.")
        # INVARIANT, asserted by
        # verification/test_verdict_bar_checker.py::test_fail_closed_never_reports_meets_bar:
        # with no eligible claim arm the status is NEVER MEETS_BAR, by any path.
        if bar["status"] == BAR_MEETS:
            bar["status"] = BAR_NO_EVIDENCE
            bar["fail_closed_override"] = (
                "MEETS_BAR withheld: no arm is eligible to carry the claim.")

    # A cell that NAMES its clearing arms is checked arm-by-arm against those names: the
    # calibrated-floor defect is exactly an arm listed as clearing whose own recorded margin
    # does not separate. Cells that name nothing are judged on the cell-wide MIN.
    declared = _declared_clearing_arms(m)
    failing_declared = []
    for arm in declared:
        for scoped, cis in _match_declared_arm(arm, fe["per_arm_floor_cis"]):
            lo, src = min_ci_lo([(c[0], c[1]) for c in cis])
            if lo is not None and lo <= 0:
                failing_declared.append({"arm": arm, "scope": scoped, "min_ci_lo": lo,
                                         "binding_floor": src})

    classes = _classify(reads, sat, bar, failing_declared)
    rec.update({
        "verdict_string": verdict, "verdict_key": vkey, "verdict_reads_as": reads,
        "verdict_msg": (vmsg or "")[:400] or None,
        "real_floor_exists": bar["conditions"]["FLOOR_PRESENT"]["ok"],
        "ci_exists": bar["conditions"]["CI_PRESENT"]["ok"],
        "margin_ci_separated": bar["conditions"]["MARGIN_CI_SEPARATED"]["ok"],
        # SCOPE MATTERS and the two are different questions, so they get different names.
        # `*_anywhere_in_cell` is the union over every arm and every population; the
        # `claim_arm_*` fields are the ONE arm the cell's claim rests on, judged within its own
        # scope. Reporting only the union produced a record that read
        # "ci=[frequency, orthographic, scramble] uncompared=[frequency]" -- self-contradictory
        # until the scopes were named apart.
        "claim_arm_floor_roles_compared":
            bar["conditions"]["ALL_REQUIRED_FLOORS_COMPARED"]["compared"],
        "claim_arm_all_required_floors_compared":
            bar["conditions"]["ALL_REQUIRED_FLOORS_COMPARED"]["ok"],
        "claim_arm_required_floors_not_compared":
            bar["conditions"]["ALL_REQUIRED_FLOORS_COMPARED"]["not_compared"],
        "min_ci_lo": bar["min_ci_lo"], "binding_floor": bar["binding_floor"],
        "claim_carrying_arm": best_arm,
        "claim_arm_status": claim_arm_status,
        "per_treatment_arm_min_ci_lo": arm_scores,
        # EXCLUSIONS ARE REPORTED, NEVER SILENT. Each entry names the arm, the min ci_lo it
        # WOULD have contributed, and why it was refused -- so a reader can see that the filter
        # matched something, and can challenge any single exclusion.
        "claim_arm_rejected": rejected_arms,
        "n_claim_arm_rejected": len(rejected_arms),
        "fail_closed_override": bar.get("fail_closed_override"),
        # Which tie conventions this cell published, if any. When a cell publishes BOTH, every
        # `binding_floor` here carries the convention that bound (`<FLOOR>|<convention>`) and the
        # conservative one wins by min_ci_lo. When a cell publishes only ONE, that is worth
        # seeing: an unnamed rank convention is an unstated choice, and on the cell audited
        # 2026-08-16 the spelling-vs-substrate top-50 comparison REVERSES between the two.
        "tie_conventions_present": fe["tie_conventions_present"],
        # informational ONLY -- pools scopes and includes control arms; never the verdict
        "most_conservative_comparison_anywhere": {"min_ci_lo": pooled_lo, "floor": pooled_src},
        "has_known_answer_arm": known, "has_null_arm": nulla,
        "bar_status": bar["status"], "bar_evidence_complete": bar["bar_evidence_complete"],
        "floor_roles_present": fe["floor_roles_present"],
        "floor_roles_with_margin_ci_anywhere_in_cell": fe["floor_roles_with_margin_ci"],
        "floor_role_names": fe["floor_role_names"],
        "n_floor_margins_with_ci": len(fe["floor_margin_ci_pairs"]),
        "declared_clearing_arms": declared,
        "declared_clearing_arms_that_fail_recompute": failing_declared,
        "saturated": sat["saturated"], "saturation_evidence": sat["evidence"],
        "traversal_truncated": fe["traversal_truncated"],
        "disagreement_class": classes[0], "classes": classes,
        "n_seeds": m.get("n_seeds") or m.get("seeds") if not isinstance(m.get("seeds"), list)
        else len(m["seeds"]),
        "N": m.get("N"), "elapsed_s": m.get("elapsed_s"), "smoke": m.get("smoke"),
        "run_mode": m.get("run_mode"),
    })
    return rec


def _all_keys(o, depth: int = 0, budget: Optional[List[int]] = None):
    if budget is None:
        budget = [MAX_NODES]
    for _, node in _iter_dicts(o, budget=budget):
        for k in node:
            yield k


_CLEARING_FIELDS = ("arms_clearing_by_population", "arms_clearing", "clearing_arms",
                    "passing_arms", "arms_that_clear")


def _declared_clearing_arms(m: dict) -> List[str]:
    """Arm names the cell itself declares as clearing. Enumerated from the cell, not guessed."""
    out: List[str] = []
    for _, node in _iter_dicts(m):
        for f in _CLEARING_FIELDS:
            v = node.get(f)
            if isinstance(v, list):
                out.extend(str(x) for x in v)
            elif isinstance(v, dict):
                for sub in v.values():
                    if isinstance(sub, list):
                        out.extend(str(x) for x in sub)
    return sorted(set(out))


def _classify(reads: str, sat: dict, bar: dict, failing_declared: List[dict]) -> List[str]:
    """Precedence: SATURATED first (a broken measurement invalidates everything downstream of
    it), then the pass-claim disagreements, then AGREES. Every applicable class is returned;
    element 0 is the primary. OUR-INVENTION: the order, not the classes.
    """
    cls: List[str] = []
    if sat["saturated"]:
        cls.append(SATURATED_CEILING)
    if reads == READS_NONE:
        cls.append(NO_VERDICT)
    claims_pass = reads == READS_PASS
    sep = bar["conditions"]["MARGIN_CI_SEPARATED"]["ok"]
    absent = bar["conditions"]["FLOOR_PRESENT"]["required_roles_absent"]
    uncompared = bar["conditions"]["ALL_REQUIRED_FLOORS_COMPARED"]["not_compared"]
    if claims_pass:
        # The bar is a margin over max(orthographic, frequency, scramble). Missing ANY of the
        # three means the max cannot be formed, so this is NO_FLOOR even when one or two floors
        # are present -- "cleared its strongest floor" is exactly the reading that let
        # exp_meaning_asset_calibrated_floor_verdict_v1 land as a clearance.
        if absent:
            cls.append(NO_FLOOR)
        # Present but never paired with a CI: the floor exists on paper and was never used.
        if [r for r in uncompared if r not in absent]:
            cls.append(NO_CI)
        if (sep is False) or failing_declared:
            cls.append(STRING_PASSES_BAR_FAILS)
    if not cls:
        cls.append(AGREES)
    # PRECEDENCE (OUR-INVENTION -- the order, not the classes). A broken measurement invalidates
    # everything downstream of it, so saturation leads. A MEASURED refutation outranks MISSING
    # evidence, so STRING_PASSES_BAR_FAILS sits above NO_FLOOR / NO_CI: "we recomputed it and it
    # does not separate" is a stronger, more actionable finding than "it never had the evidence",
    # and burying it under a missing-floor label would hide the only case where the tool has
    # actually caught a number lying.
    return sorted(set(cls), key=lambda c: _PRECEDENCE.index(c))


_PRECEDENCE = (SATURATED_CEILING, STRING_PASSES_BAR_FAILS, NO_FLOOR, NO_CI, NO_VERDICT, AGREES)


# ================================================================== 6. SCAN + REPORT
def scan(data_dir: str = DATA, limit: Optional[int] = None,
         paths: Optional[Sequence[str]] = None) -> dict:
    t0 = time.time()
    if paths is None:
        if not os.path.isdir(data_dir):
            raise SystemExit(f"[verdict-bar] data dir does not exist: {data_dir}")
        paths = enumerate_metrics(data_dir)
    walked = len(paths)
    if limit:
        paths = list(paths)[:limit]
    records = [check_cell(p) for p in paths]

    counts: Dict[str, int] = {c: 0 for c in CLASSES}
    reads_counts: Dict[str, int] = {}
    bar_counts: Dict[str, int] = {BAR_MEETS: 0, BAR_FAILS: 0, BAR_NO_EVIDENCE: 0}
    for r in records:
        counts[r["disagreement_class"]] = counts.get(r["disagreement_class"], 0) + 1
        reads_counts[r.get("verdict_reads_as", READS_NONE)] = \
            reads_counts.get(r.get("verdict_reads_as", READS_NONE), 0) + 1
        if r.get("bar_status"):
            bar_counts[r["bar_status"]] = bar_counts.get(r["bar_status"], 0) + 1

    flagged = [r for r in records if r["disagreement_class"] != AGREES]
    meets = [r for r in records if r.get("bar_status") == BAR_MEETS]
    # EVERY cell is accounted for, but a cell with nothing to say does not need 1.7 KB to say
    # it: unflagged records are emitted in a compact form (7,769 full records is 13 MB, most of
    # it empty dicts). Flagged records and bar-meeting records keep every field. This is a size
    # choice, never a filter -- `n_records_total` must equal the number scanned, and the
    # self-test asserts it.
    full = [r for r in records if _keep_full(r)]
    rest = [r for r in records if not _keep_full(r)]
    return {
        "tool": "tools/verdict_bar_check.py",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_s": round(time.time() - t0, 1),
        "enumeration": {
            "method": "os.walk over an ABSOLUTE data dir; every directory visited, every "
                      "metrics.json opened. No glob, no name filter, no registry input.",
            "data_dir": data_dir.replace("\\", "/"),
            "metrics_json_found_on_disk": walked,
            "scanned": len(records),
            "limited": bool(limit),
        },
        "the_bar": "a CI-SEPARATED margin over max(orthographic, frequency, scramble) on the "
                   "IDENTICAL scorer/n/pool/gold, never a bare absolute number, plus a "
                   "KNOWN-ANSWER arm and a NULL arm that fail INDEPENDENTLY",
        "this_is_a_report_not_an_enforcement_action": (
            "No metrics.json, atom or label was read-modify-written by this tool. Demotion is "
            "the operator's call."),
        "DISCLOSURE_FIRST": {
            "this_tool_changed_nothing": "no metrics.json, no atom, no label, no registry row. "
                                         "Verified by verification/test_verdict_bar_checker.py"
                                         "::test_scan_never_mutates_anything.",
            "what_a_class_means": {
                SATURATED_CEILING: "the cell's own headline numbers are pinned at 1.000 across "
                                   "every arm -- a broken measurement, not a pass",
                STRING_PASSES_BAR_FAILS: "recomputed: a PASS-shaped verdict string whose margin "
                                         "is NOT CI-separated from a floor the cell ITSELF "
                                         "recorded. The strongest finding this tool makes.",
                NO_FLOOR: "PASS-shaped string, and at least one of orthographic / frequency / "
                          "scramble is absent, so max(...) cannot be formed at all",
                NO_CI: "PASS-shaped string, the floor EXISTS, and it was never paired with a CI",
                AGREES: "no overstatement detected. NOT a certificate that the cell is good -- "
                        "most AGREES cells simply claim nothing.",
                NO_VERDICT: "no verdict string found; carried as residue, never dropped",
            },
            "known_limits": [
                "READS_AMBIGUOUS cells are counted, not judged: their verdict string carries no "
                "token in the lexicon either way. They are residue to read, not a clean bill.",
                "A cell is scored on its CLAIM-CARRYING ARM (best within-scope treatment arm). "
                "Cells that name their clearing arms are additionally checked arm-by-arm.",
                "Absence of a floor is detected by ARM-NAME SHAPE. A floor recorded under a name "
                "outside tools/c3_gate.classify_arm_role's patterns reads as absent.",
            ],
        },
        "reconciliation": reconcile_to_registry(records),
        "class_counts": counts,
        "verdict_reads_as_counts": reads_counts,
        "bar_status_counts": bar_counts,
        "n_flagged": len(flagged),
        "n_records_total": len(full) + len(rest),
        "n_meeting_the_bar": len(meets),
        "cells_meeting_the_bar": [r["cell"] for r in meets],
        "record_form": (
            "`records` carries EVERY field for the classes a reader opens (SATURATED_CEILING, "
            "STRING_PASSES_BAR_FAILS, NO_CI, and any bar-meeting cell). `index` carries every "
            "REMAINING cell as one row against `index.columns` -- a table, not repeated key "
            "names, because 7,769 indented dicts is 13 MB of mostly empty containers. "
            "NO CELL IS OMITTED: n_records_total == enumeration.scanned, asserted in the "
            "self-test."),
        "records": full,
        "index": {"columns": list(_COMPACT_FIELDS),
                  "rows": [[r.get(k) for k in _COMPACT_FIELDS] for r in rest]},
    }


# The index columns. `metrics_path` is omitted deliberately -- it is always
# data/<cell>/metrics.json and repeating it 7,500 times costs more than it tells anyone.
_COMPACT_FIELDS = ("cell", "verdict_string", "verdict_reads_as", "bar_status",
                   "disagreement_class", "real_floor_exists", "ci_exists",
                   "margin_ci_separated", "min_ci_lo", "binding_floor", "floor_roles_present",
                   "has_known_answer_arm", "has_null_arm", "smoke",
                   "claim_arm_status", "n_claim_arm_rejected")


_FULL_CLASSES = (SATURATED_CEILING, STRING_PASSES_BAR_FAILS, NO_CI)


def _keep_full(r: dict) -> bool:
    """Full record for the classes a reader will actually open, compact for the rest.

    NO_FLOOR is the bulk (2,966 of 7,769) and its full record adds nothing a compact one does
    not: there is no floor, so there are no margins, no per-arm CIs and no binding floor to
    print. Keeping it full cost 8.6 MB of empty containers.
    """
    return r["disagreement_class"] in _FULL_CLASSES or r.get("bar_status") == BAR_MEETS


LEDGER = os.path.join(DATA, "substrate_index", "meta", "cert_ledger.jsonl")
REGISTRY = os.path.join(DATA, "capability_registry.jsonl")
_METRICS_REF = re.compile(r"data[/\\]([^\"'\s,;)\]]+?)[/\\]metrics\.json")


def reconcile_to_registry(records: Sequence[dict]) -> dict:
    """Filesystem FIRST, then reconcile the ledger + registry TO it. Never the reverse.

    CLAUDE.md "Evidence discipline" sec 2: two audits on 2026-08-13 each missed a whole working
    subsystem by asking "does the registry match disk?" instead of "what is on disk?". So the
    disk enumeration above is the frame; this function only asks what the two indexes SAY about
    the cells the disk already produced, and reports the residue in BOTH directions.

    READ-ONLY. `data/capability_registry.jsonl` is a do-not-touch path and is opened for reading
    only; nothing here writes to either index.
    """
    on_disk = {r["cell"] for r in records}
    by_class = {r["cell"]: r["disagreement_class"] for r in records}

    def cited_cells(path):
        cells, rows = set(), 0
        if not os.path.exists(path):
            return cells, rows, f"absent: {path}"
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    rows += 1
                    for m in _METRICS_REF.findall(line):
                        c = m.replace("\\", "/").split("/")[0]
                        # `data/<anchor>/metrics.json` template strings appear verbatim in
                        # ledger notes; they are documentation, not citations.
                        if c and not (c.startswith("<") and c.endswith(">")):
                            cells.add(c)
        except OSError as exc:
            return cells, rows, f"unreadable: {exc}"
        return cells, rows, None

    led, n_led, led_err = cited_cells(LEDGER)
    reg, n_reg, reg_err = cited_cells(REGISTRY)
    cited = led | reg
    flagged_and_cited = sorted(c for c in cited & on_disk if by_class.get(c) != AGREES)
    return {
        "direction": "filesystem enumerated FIRST; both indexes reconciled TO it (never reverse)",
        "read_only": True,
        "cert_ledger": {"path": LEDGER.replace("\\", "/"), "rows": n_led,
                        "cells_cited": len(led), "error": led_err},
        "capability_registry": {"path": REGISTRY.replace("\\", "/"), "rows": n_reg,
                                "cells_cited": len(reg), "error": reg_err},
        "cells_on_disk": len(on_disk),
        "cited_by_an_index_and_on_disk": len(cited & on_disk),
        "cited_by_an_index_but_NOT_on_disk": sorted(cited - on_disk)[:60],
        "n_cited_but_not_on_disk": len(cited - on_disk),
        "on_disk_but_cited_by_NO_index": len(on_disk - cited),
        "CITED_AND_FLAGGED": flagged_and_cited,
        "n_cited_and_flagged": len(flagged_and_cited),
        "why_this_list_matters": (
            "these are cells an index POINTS AT whose banked verdict disagrees with the standing "
            "bar -- the ones whose overstatement has already propagated into the ledger or the "
            "registry. Reading this list is the operator's decision, not this tool's."),
    }


def persist(report: dict, out: Optional[str] = None, records: bool = True) -> str:
    """Write the report. `records=False` writes the SUMMARY ONLY -- that is what REPORT_DIR
    holds, because the hook reads it on every session start and must not parse 13 MB."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    if out is None:
        out = os.path.join(REPORT_DIR,
                           "verdict-bar-%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    if not records:
        report = {k: v for k, v in report.items() if k not in ("records", "index")}
        report["records_omitted"] = ("summary artifact for the session-start hook; the full "
                                     "findings are written by --out")
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(report, fh, indent=1)
    os.replace(tmp, out)
    return out


def hook_line() -> Tuple[str, int]:
    """FAST path for tools/session_start_hook.py: read the newest PERSISTED report and report
    its counts + age. Does NOT rescan -- a full scan walks 7,768 metrics.json and takes minutes.
    Same split as registry_report() and result_index_join.hook_line(), both proven under the
    hook's 10 s budget.
    """
    if not os.path.isdir(REPORT_DIR):
        return ("[verdict-bar] NEVER RUN <-- ATTENTION\n"
                "    run: python tools/verdict_bar_check.py --scan", 1)
    reps = [os.path.join(REPORT_DIR, f) for f in os.listdir(REPORT_DIR)
            if f.startswith("verdict-bar-") and f.endswith(".json")]
    if not reps:
        return ("[verdict-bar] NO REPORT RECORDED <-- ATTENTION\n"
                "    run: python tools/verdict_bar_check.py --scan", 1)
    newest = max(reps, key=lambda p: os.stat(p).st_mtime)
    age_h = max(0.0, (time.time() - os.stat(newest).st_mtime) / 3600.0)
    try:
        with open(newest, "r", encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return (f"[verdict-bar] REPORT UNREADABLE ({exc}) file={os.path.basename(newest)} "
                f"<-- ATTENTION", 1)
    c = d.get("class_counts", {})
    flag = " <-- STALE, re-run --scan" if age_h > 168 else ""
    body = (f"[verdict-bar] last recompute {age_h:.1f}h ago{flag}\n"
            f"    {d.get('n_flagged', '?')} of {d.get('enumeration', {}).get('scanned', '?')} "
            f"banked verdicts DISAGREE with the standing bar; "
            f"{d.get('n_meeting_the_bar', '?')} meet it\n"
            f"    string_passes_bar_fails={c.get(STRING_PASSES_BAR_FAILS, 0)} "
            f"saturated={c.get(SATURATED_CEILING, 0)} no_floor={c.get(NO_FLOOR, 0)} "
            f"no_ci={c.get(NO_CI, 0)}\n"
            f"    a PASS-shaped verdict string is NOT a clearance of the bar: "
            f"{os.path.basename(newest)}")
    return body, 0


# ================================================================== 7. SELF-TEST
def _fixture_genuine(tmp: str) -> str:
    """A synthetic cell that GENUINELY meets the bar, in full: three floors, three CI-separated
    margins, a known-answer arm and a null arm. THE NEGATIVE CONTROL -- if this is flagged, the
    checker flags everything and proves nothing. Synthetic on purpose: no cell on disk currently
    carries all three floors with paired CIs, which is itself the finding, and a control drawn
    from the population under audit would be circular.
    """
    cell = {
        "verdict": "GENUINE_HARD_PASS",
        "verdict_msg": "arm=0.4210 floor_max=0.0932 margin=0.3278",
        "arms_clearing": ["TREATMENT"],
        "results": {
            "rows": {
                "TREATMENT": {
                    "rho": {"point": 0.4210, "ci95": [0.3100, 0.5200], "n": 322},
                    "DECOMPOSED_per_floor": {
                        "A_ORTHOGRAPHIC": {"margin": {"point": 0.404, "ci95": [0.28, 0.52]}},
                        "HARDENED_FREQUENCY_FREQ_MIN": {"margin": {"point": 0.341,
                                                                   "ci95": [0.21, 0.47]}},
                        "SCRAMBLE_NULL_P95": {"margin": {"point": 0.328, "ci95": [0.19, 0.46]}},
                    },
                },
                "GLOVE_KNOWN_ANSWER": {"rho": {"point": 0.3462, "ci95": [0.2403, 0.4465]}},
                "CTRL_RANDINIT": {"rho": {"point": 0.004, "ci95": [-0.10, 0.11]}},
            }
        },
    }
    p = os.path.join(tmp, "metrics.json")
    with open(p, "w", encoding="utf-8", newline="") as fh:
        json.dump(cell, fh)
    return p


def _fixture_false_pass(tmp: str, scaffold_name: str = "S_INPLACE_d256_f0.020__KA",
                        degenerate_ci: bool = True) -> str:
    """THE 2026-08-16 FALSE PASS, reproduced as a 2x2 so each new rule can be tested alone.

    The real cell that produced it lives in `scratch/`, which is gitignored and periodically
    cleared, so a durable test cannot cite it (CLAUDE.md: promote or do not depend on scratch).
    This fixture carries the shape and the REAL numbers instead:

      * an honest treatment arm `R0_BASE_DENSE` whose every floor margin is NEGATIVE;
      * a PLANTED-ANSWER arm at hit@1 1.0000 with a ZERO-WIDTH CI, carrying floor margins of
        +0.9044 / +0.9342 / +0.9855 -- which are arithmetic, not evidence;
      * a per-pipeline `__NULL` arm, which the role classifier ALREADY recognised correctly and
        which was scored as a treatment arm anyway because only the tail path segment was
        classified and the tail was the CONTAINER `MARGIN_per_floor`;
      * a LITERAL DOT inside the arm name (`f0.020`), which is why the walker had to stop
        building dotted path strings.

    TWO INDEPENDENT VARIABLES, and the floor margins are held CONSTANT across all four cells so
    that the only thing that changes is whether the arm is ALLOWED to carry the claim:
      scaffold_name  -- does the NAME mark it as validity scaffolding?
      degenerate_ci  -- does the SHAPE mark it as pinned at ceiling by construction?
    Expected: FAILS_BAR unless BOTH are off, and MEETS_BAR when both are off. That last cell is
    the negative control -- without it, a rule that rejected every arm would look correct.
    """
    def margins(vals):
        return {"F1_TRIGRAM_ONLY": {"margin": {"point": vals[0] + 0.009,
                                               "ci95": [vals[0], vals[0] + 0.018]}},
                "F3_FREQUENCY_ONLY": {"margin": {"point": vals[1] + 0.004,
                                                 "ci95": [vals[1], vals[1] + 0.008]}},
                "NULL_SCRAMBLED_ANCHORS": {"margin": {"point": vals[2] + 0.003,
                                                      "ci95": [vals[2], vals[2] + 0.006]}}}

    scaffold = {"hit_at_1": 1.0 if degenerate_ci else 0.6200,
                "hit_at_1_ci95": [1.0, 1.0] if degenerate_ci else [0.6000, 0.6400],
                "n_scored": 3994,
                "MARGIN_per_floor": margins([0.9044, 0.9772, 0.9855])}
    cell = {
        "verdict": "SPARSE_CODE_DOES_NOT_CLEAR_THE_SPELLING_FLOOR_ON_THE_REAL_TASK",
        "REAL_TASK": {"regimes": {"EXACT_KEY_profile_bundle": {"per_arm": {
            "R0_BASE_DENSE": {"hit_at_1": 0.0481, "hit_at_1_ci95": [0.0418, 0.0548],
                              "n_scored": 3994,
                              "MARGIN_per_floor": margins([-0.0741, 0.0234, 0.0308])},
            scaffold_name: scaffold,
            "S_INPLACE_d256_f0.020__NULL": {
                "hit_at_1": 0.0113, "hit_at_1_ci95": [0.0081, 0.0148], "n_scored": 3994,
                "MARGIN_per_floor": margins([-0.0896, -0.0084, -0.0011])},
            "KA_QUERY_IS_GOLD_VECTOR": {
                "hit_at_1": 1.0, "hit_at_1_ci95": [1.0, 1.0], "n_scored": 3994,
                "MARGIN_per_floor": margins([0.9044, 0.9772, 0.9855])},
        }}}},
    }
    p = os.path.join(tmp, "metrics.json")
    with open(p, "w", encoding="utf-8", newline="") as fh:
        json.dump(cell, fh)
    return p


def self_test() -> int:
    """Prove the checker flags BOTH known offenders and does NOT flag genuine cells.

    A guard nobody verified is a guard that does not exist -- this repo shipped a check
    (`if base in src`) that could only ever inflate its own count.
    """
    import tempfile
    ok = True

    def check(label, got, want):
        nonlocal ok
        if got == want:
            print(f"[self-test] PASS {label} -> {got}")
        else:
            print(f"[self-test] FAIL {label} -> {got!r}, expected {want!r}", file=sys.stderr)
            ok = False

    # ---- OFFENDER 1: the label-survived / claim-died cell, from its REAL banked metrics.json.
    p1 = os.path.join(DATA, "exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384",
                      "metrics.json")
    if os.path.exists(p1):
        r = check_cell(p1)
        check("OFFENDER 1 banked verdict string still reads as a PASS",
              (r["verdict_string"], r["verdict_reads_as"]), ("4WC_HARD_PASS", READS_PASS))
        check("OFFENDER 1 is FLAGGED as SATURATED_CEILING", r["disagreement_class"],
              SATURATED_CEILING)
        check("  the 1.000-across-every-arm shape is the evidence",
              bool(r["saturation_evidence"]) and
              all(_is_ceiling(v) for v in r["saturation_evidence"][0]["values"]), True)
        # NO_FLOOR, and specifically NOT NO_CI: this cell records none of the three required
        # floors, so there is no floor whose CI is missing. NO_CI is reserved for a floor that
        # EXISTS on paper and was never paired -- keeping the two apart is what tells the
        # operator whether the fix is "add a control" or "add a bootstrap".
        check("  and it ALSO fails the bar for having none of the three required floors",
              (NO_FLOOR in r["classes"], NO_CI in r["classes"]), (True, False))
        check("  with all three named as absent", r["floor_roles_present"], [])
        # DISCRIMINATION: the honest re-run of the SAME cell must NOT be called saturated.
        p1b = p1.replace("_n16384" + os.sep, "_n16384_ckfix" + os.sep)
        if os.path.exists(p1b):
            rb = check_cell(p1b)
            check("  the REAL 5-seed N=16384 re-run is NOT saturated (0.951/0.966/0.942/0.980)",
                  rb["saturated"], False)
            check("  and its verdict string is byte-identical, so only the RECOMPUTE separates "
                  "them", rb["verdict_string"], r["verdict_string"])
        else:
            print(f"[self-test] SKIP ckfix re-run absent: {p1b}")
    else:
        print(f"[self-test] FAIL offender 1 metrics.json absent: {p1}", file=sys.stderr)
        ok = False

    # ---- OFFENDER 2: the calibrated-floor cell whose 2 of 3 clearing arms do not separate.
    p2 = os.path.join(DATA, "exp_meaning_asset_calibrated_floor_verdict_v1", "metrics.json")
    if os.path.exists(p2):
        r = check_cell(p2)
        check("OFFENDER 2 verdict string reads as a PASS", r["verdict_reads_as"], READS_PASS)
        check("OFFENDER 2 is FLAGGED as STRING_PASSES_BAR_FAILS", r["disagreement_class"],
              STRING_PASSES_BAR_FAILS)
        fails = r["declared_clearing_arms_that_fail_recompute"]
        failing = {d["arm"] for d in fails}
        check("  and it names the two arms that do not separate",
              failing, {"d512|ASSET_RETRAIN_CTX", "d512|ASSET_V2_CTX"})
        # Written to be NON-VACUOUS on purpose: `len(fails) == 2` is asserted alongside the
        # all(), so a filter that matched nothing could not pass this the way `if base in src`
        # once inflated its own count.
        check("  with the FREQUENCY channel as the binding floor on BOTH",
              (len(fails), all("FREQ" in d["binding_floor"].upper() for d in fails)), (2, True))
        check("  and the third declared arm is NOT flagged (it separates from the floors it "
              "recorded)", "d512|ASSET_RETRAIN_ISOL" in failing, False)
        check("  it DOES have real floors and real CIs -- the defect is separation, not absence",
              (r["real_floor_exists"], r["ci_exists"]), (True, True))
    else:
        print(f"[self-test] FAIL offender 2 metrics.json absent: {p2}", file=sys.stderr)
        ok = False

    # ---- NEGATIVE CONTROL 1: a synthetic cell that genuinely meets the bar must NOT be flagged.
    with tempfile.TemporaryDirectory() as td:
        r = check_cell(_fixture_genuine(td))
        check("NEGATIVE CONTROL: a genuinely-clearing cell is NOT flagged",
              r["disagreement_class"], AGREES)
        check("  it meets the bar outright", r["bar_status"], BAR_MEETS)
        check("  with all three required floors CI-compared on the CLAIM-CARRYING arm",
              r["claim_arm_floor_roles_compared"], ["frequency", "orthographic", "scramble"])
        check("  and the claim-carrying arm is named",
              r["claim_carrying_arm"].endswith("TREATMENT"), True)
        check("  and its evidence is marked complete", r["bar_evidence_complete"], True)

    # ---- NEGATIVE CONTROL 2: the same fixture with ONE floor pushed below zero must flip.
    with tempfile.TemporaryDirectory() as td:
        p = _fixture_genuine(td)
        with open(p, encoding="utf-8") as fh:
            cell = json.load(fh)
        (cell["results"]["rows"]["TREATMENT"]["DECOMPOSED_per_floor"]
             ["HARDENED_FREQUENCY_FREQ_MIN"]["margin"]["ci95"]) = [-0.02, 0.31]
        with open(p, "w", encoding="utf-8", newline="") as fh:
            json.dump(cell, fh)
        r = check_cell(p)
        check("ONE floor pushed below zero flips the SAME cell to a disagreement",
              r["disagreement_class"], STRING_PASSES_BAR_FAILS)
        check("  and the frequency floor is named as binding",
              r["binding_floor"], "HARDENED_FREQUENCY_FREQ_MIN")

    # ---- NEGATIVE CONTROL 3: an honest negative must not be flagged for lacking a floor.
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "metrics.json")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            json.dump({"verdict": "XSHARD_HARD_FAIL",
                       "verdict_msg": "mean_AUC=0.497 at chance"}, fh)
        r = check_cell(p)
        check("an honest HARD_FAIL is NOT flagged (the tool reports overstatement, not absence)",
              r["disagreement_class"], AGREES)
        check("  and its bar status is still recorded as FAILS_BAR for the record",
              r["bar_status"], BAR_FAILS)

    # ---- OFFENDER 3: THE FALSE PASS. A planted-answer arm carried a cell's claim to MEETS_BAR
    #      at min ci_lo +0.9044 while every genuine arm in the cell was negative. Run as a 2x2 so
    #      the NAME rule and the SHAPE rule are each shown to work ALONE, and so the last cell
    #      proves they can be satisfied -- a rule that rejects everything is not a rule.
    for nm, deg, want, why in (
            ("S_INPLACE_d256_f0.020__KA", True, BAR_FAILS, "name AND shape"),
            ("S_INPLACE_d256_f0.020__KA", False, BAR_FAILS, "NAME alone (arm not at ceiling)"),
            ("S_INPLACE_d256_f0.020_TREATMENT", True, BAR_FAILS, "SHAPE alone (name is clean)"),
            ("S_INPLACE_d256_f0.020_TREATMENT", False, BAR_MEETS,
             "NEGATIVE CONTROL: neither rule fires, the SAME +0.9044 margins pass")):
        with tempfile.TemporaryDirectory() as td:
            r = check_cell(_fixture_false_pass(td, scaffold_name=nm, degenerate_ci=deg))
            check(f"false-pass 2x2 [{why}] -> {want}", r["bar_status"], want)
            if want is BAR_FAILS:
                check("  and the claim falls back to the HONEST negative arm",
                      str(r["claim_carrying_arm"]).endswith("R0_BASE_DENSE"), True)
                check("  with the scaffold arm REJECTED and the reason recorded",
                      any(nm in k for k in r["claim_arm_rejected"]), True)
            else:
                check("  and the claim arm is the renamed, non-saturated arm",
                      str(r["claim_carrying_arm"]).endswith(nm), True)

    # ---- FAIL CLOSED: when EVERY arm is scaffolding there is no claim arm, and no claim arm is
    #      NO_EVIDENCE -- never MEETS_BAR. A tool that guesses in the passing direction is worse
    #      than no tool.
    with tempfile.TemporaryDirectory() as td:
        p = _fixture_false_pass(td)
        with open(p, encoding="utf-8") as fh:
            cell = json.load(fh)
        arms = cell["REAL_TASK"]["regimes"]["EXACT_KEY_profile_bundle"]["per_arm"]
        arms["R0_BASE_DENSE__KA"] = arms.pop("R0_BASE_DENSE")     # the last honest arm removed
        with open(p, "w", encoding="utf-8", newline="") as fh:
            json.dump(cell, fh)
        r = check_cell(p)
        check("FAIL CLOSED: no eligible claim arm is NO_EVIDENCE, never MEETS_BAR",
              (r["bar_status"], r["claim_carrying_arm"]), (BAR_NO_EVIDENCE, None))
        check("  and the reason is stated, not inferred",
              r["claim_arm_status"], "NO_ELIGIBLE_CLAIM_ARM")

    # ---- REGRESSION: a realised CONFIGURATION fraction at 1.0 is not a ceiling. The first cut
    #      of the shape rule excluded INC_SIMHASH -- a legitimate incumbent arm -- because a
    #      SimHash is a sign function so its `active_frac_realised` is 1.0 by construction.
    check("a config fraction at 1.0 does NOT read as an instrument ceiling",
          arm_ceiling_shape({"simlex_rho": 0.268, "active_frac_realised": 1.0,
                             "bundle_bits": 0.874}), None)
    check("but hit@1 1.0 with a ZERO-WIDTH CI does",
          (arm_ceiling_shape({"hit_at_1": 1.0, "hit_at_1_ci95": [1.0, 1.0]}) or {}).get("tell"),
          "DEGENERATE_CI_AT_CEILING")
    check("and so does every bounded score pinned at 1.0",
          (arm_ceiling_shape({"hit_at_1": 1.0, "recall": 1.0}) or {}).get("tell"),
          "ALL_SCORES_AT_CEILING")
    check("an honest arm is NOT called a ceiling",
          arm_ceiling_shape({"hit_at_1": 0.0481, "hit_at_1_ci95": [0.0418, 0.0548]}), None)

    # ---- the verdict lexicon, on strings measured on disk
    for s, want in (("4WC_HARD_PASS", READS_PASS),
                    ("ASSET_CLEARS_THE_CALIBRATED_FLOOR_ON_THE_INSTRUMENT_POPULATION", READS_PASS),
                    ("KF45_SMOKE_PASS", READS_PASS),
                    ("BID_V5_N8K_HARD_PASS", READS_PASS),
                    ("KF45_JOINT_MIDDLE_BAND", READS_NOT_PASS),
                    ("XSHARD_HARD_FAIL", READS_NOT_PASS),
                    ("NOT_SEPARATED", READS_NOT_PASS),
                    ("PARTIAL: hp=1/1 hf=0/1", READS_NOT_PASS),
                    ("KF4_V4_SMOKE_FAIL", READS_NOT_PASS),
                    ("RULER_CAN_DETECT_MEANING_AT_THIS_N", READS_AMBIGUOUS),
                    # LOCAL negation. The first cut read these four as PASSES and filed four
                    # honest negatives as disagreements; the last one proves the fix did not
                    # over-correct into flipping a genuine pass that merely contains "NO".
                    ("NO_ASSET_CLEARS_THE_STRONGEST_FLOOR", READS_AMBIGUOUS),
                    ("NORMS_DO_NOT_CLEAR_CI_SEPARATED", READS_AMBIGUOUS),
                    ("ASSET_CLEARS_THE_STRONGEST_FLOOR", READS_PASS),
                    ("HARD_PASS_STRUCTURAL_NO_LEAK", READS_PASS),
                    (None, READS_NONE)):
        check(f"verdict_reads_as({s!r})", verdict_reads_as(s), want)

    # ---- saturation, positive and negative, on the two real verdict_msgs
    banked = ("baseline_ratio=1.000 A_4way_ratio=1.000 B_cleanup_ratio=1.000 "
              "C_combined_ratio=1.000 C_verify=1.000 arm_C=HARD_PASS seeds=1 N=512")
    real = ("baseline_ratio=0.951 A_4way_ratio=0.966 B_cleanup_ratio=0.942 "
            "C_combined_ratio=0.980 C_verify=1.000 arm_C=HARD_PASS seeds=5 N=16384")
    check("saturation fires on the banked 1.000-everywhere message",
          saturation_scan({}, banked)["saturated"], True)
    check("saturation does NOT fire on the real message that keeps ONE 1.000",
          saturation_scan({}, real)["saturated"], False)
    check("saturation does NOT fire on integer config fields alone (N=512 seeds=1)",
          saturation_scan({}, "arm=HARD_PASS seeds=1 N=512")["saturated"], False)
    check("saturation needs >= 2 metrics -- a lone 1.000 is not a pinned-across-arms shape",
          saturation_scan({}, "only_one=1.000 N=512")["saturated"], False)

    # ---- NEGATIVE CONTROL for the SATURATION GUARD ITSELF: disabled, offender 1 must stop
    #      being caught by it. Proves the guard is load-bearing and not decorative.
    global GUARD_ENABLED
    GUARD_ENABLED = False
    try:
        if os.path.exists(p1):
            r = check_cell(p1)
            check("guard DISABLED: offender 1 is no longer SATURATED_CEILING "
                  "(the guard is load-bearing)", r["disagreement_class"] != SATURATED_CEILING,
                  True)
    finally:
        GUARD_ENABLED = True

    # ---- non-vacuity of the SCAN itself: it must classify a mixed fixture population correctly.
    with tempfile.TemporaryDirectory() as td:
        good = os.path.join(td, "good")
        os.makedirs(good)
        _fixture_genuine(good)
        bad = os.path.join(td, "bad")
        os.makedirs(bad)
        with open(os.path.join(bad, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
            json.dump({"verdict": "BARE_HARD_PASS", "verdict_msg": "acc=0.62 threshold=0.50"}, fh)
        rep = scan(data_dir=td)
        check("scan enumerates BOTH fixture cells from disk",
              rep["enumeration"]["metrics_json_found_on_disk"], 2)
        check("  and separates them: 1 AGREES, 1 NO_FLOOR",
              (rep["class_counts"][AGREES], rep["class_counts"][NO_FLOOR]), (1, 1))
        check("  and reports exactly 1 cell meeting the bar", rep["n_meeting_the_bar"], 1)
        check("  and NO cell is dropped by record compaction",
              rep["n_records_total"], rep["enumeration"]["scanned"])

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ================================================================== 8. CLI
def _fmt_record(r: dict) -> str:
    return ("  %-58s %-24s floor=%-5s ci=%-5s sep=%-5s  %s"
            % (r["cell"][:58], str(r.get("verdict_string"))[:24],
               r.get("real_floor_exists"), r.get("ci_exists"),
               r.get("margin_ci_separated"), r["disagreement_class"]))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scan", action="store_true", help="full audit; persists a report JSON")
    ap.add_argument("--hook", action="store_true", help="fast: read newest persisted report")
    ap.add_argument("--cell", metavar="METRICS_JSON", help="recompute ONE cell and print it")
    ap.add_argument("--self-test", action="store_true", help="prove the checker on both offenders")
    ap.add_argument("--out", default=None, help="write the full findings JSON here")
    ap.add_argument("--data-dir", default=DATA)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-persist", action="store_true")
    ap.add_argument("--json", action="store_true", help="emit the report JSON on stdout")
    ap.add_argument("--_disable_guard", action="store_true",
                    help="self-test only: negative control for the saturation guard")
    args = ap.parse_args(argv)

    if args._disable_guard:
        global GUARD_ENABLED
        GUARD_ENABLED = False
        print("[verdict-bar] WARNING saturation guard DISABLED (negative control)")

    if args.self_test:
        return self_test()
    if args.hook:
        line, rc = hook_line()
        print(line)
        return rc
    if args.cell:
        print(json.dumps(check_cell(args.cell), indent=1))
        return 0
    if not args.scan:
        ap.print_help()
        return 2

    rep = scan(data_dir=args.data_dir, limit=args.limit)
    if args.json:
        print(json.dumps(rep, indent=1))
    else:
        print(f"[verdict-bar] enumerated {rep['enumeration']['metrics_json_found_on_disk']} "
              f"metrics.json from disk in {rep['elapsed_s']}s")
        print(f"[verdict-bar] class counts: {rep['class_counts']}")
        print(f"[verdict-bar] verdict strings read as: {rep['verdict_reads_as_counts']}")
        print(f"[verdict-bar] {rep['n_meeting_the_bar']} cells MEET the standing bar")
        worst = [r for r in rep["records"]
                 if r["disagreement_class"] in (STRING_PASSES_BAR_FAILS, SATURATED_CEILING)]
        print(f"[verdict-bar] {len(worst)} cells whose STRING overstates their CLAIM:")
        for r in worst[:40]:
            print(_fmt_record(r))
        if len(worst) > 40:
            print(f"      ... and {len(worst) - 40} more (see the report JSON)")
    # ALWAYS persist into REPORT_DIR unless explicitly suppressed: that timestamped file is what
    # --hook reads, and it is the whole durability mechanism. `--out` is an ADDITIONAL copy for
    # a caller who wants the findings at a chosen path -- it must not replace the canonical one,
    # or a scan run with --out would silently leave the hook reporting NEVER RUN.
    if not args.no_persist:
        print(f"[verdict-bar] summary written: {persist(rep, records=False)}")
    if args.out:
        persist(rep, args.out)
        print(f"[verdict-bar] report also written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
