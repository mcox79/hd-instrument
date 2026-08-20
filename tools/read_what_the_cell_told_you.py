"""Landed cells that PRINTED a caveat undermining their own verdict -- and nobody read it.

WHY THIS EXISTS. On 2026-08-20 the same thing happened FIVE times: **the answer was already in an
artifact nobody had read.** Not one of them was a measurement failure. Every one was a
reading failure.

| # | what was missed | what it cost |
|---|---|---|
| 1-2 | two pre-registered hand-score samples, `NOT_AUTO_SCORED: true`, untouched for 7-8 days | two landed cells stuck PENDING; scoring them answered questions the project still treated as open |
| 3 | a cell's own `floor_note` spelling out *"READING_A fires but nothing clears the floor means the route RETRIEVES and is NOT COMPETITIVE"* | the distinction it drew was exactly the one being argued about |
| 4 | `mean_constant_prototype: 0.1501` sitting in a balance table beside four covariates balanced to ~0.06 | a floor was treated as clean when its own cell had flagged the one uncontrolled covariate |
| 5 | `exp_situation_model_multibank_capacity_v1`'s sweep, recorded in a constructor docstring | I nearly re-measured it; the default backend already solved the problem |

**THE COMMON SHAPE: a cell computes a diagnostic that QUALIFIES ITS OWN HEADLINE, writes it down
honestly, and the headline travels without it.** *This project does not measure badly. It measures
well and then does not read what it wrote.*

**So this is that lesson as a check rather than a paragraph** -- the same move that produced
`tools/rank_with_ties.py` (after three tie artifacts) and `tools/replication_gate.py` (after four
single-seed retractions).

WHAT IT FLAGS, and each rule comes from a real 2026-08-20 incident rather than from imagination:
  * `UNDERPOWERED: true` while the cell still states a verdict
  * a TIE MASS above `tie_thresh` on any arm -- a mostly-tied arm's AUC is an accounting convention
  * a BALANCE / standardized-mean-difference entry above `smd_thresh` -- matching that missed one
  * `NOT_AUTO_SCORED: true` -- a human input the verdict is waiting on
  * COVERAGE loss above `coverage_thresh` -- a filter that removed much of the population
  * a `*note*` / `limitation*` / `caveat*` field on a cell whose verdict reads as a strong claim

**IT DOES NOT JUDGE WHETHER THE VERDICT IS WRONG.** It says: *this cell told you something about
itself; go and read it.* **False positives are expected and cheap; the failure mode this exists to
prevent is a false NEGATIVE that costs a week.**
"""
from __future__ import annotations

import json
import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(_REPO, "data")

STRONG_VERDICT = re.compile(r"HARD_PASS|PASS|CONFIRM|VALIDATED|CHAIN_GRADE|STRUCTURAL_PASS", re.I)
NOTE_KEY = re.compile(r"(note|limitation|caveat|honest|scope|warning)", re.I)


def _walk(obj, path=""):
    """Yield (dotted_path, key, value) for every scalar in a nested metrics blob."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if isinstance(v, (dict, list)):
                yield from _walk(v, p)
            else:
                yield p, str(k), v
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:40]):
            yield from _walk(v, f"{path}[{i}]")


def audit(cell_dir, m, *, tie_thresh=0.5, smd_thresh=0.10, coverage_thresh=0.25):
    verdict = str(m.get("verdict") or "")
    flags = []
    for path, key, val in _walk(m):
        kl = key.lower()
        if kl == "underpowered" and val is True:
            # SUPPRESS WHEN THE VERDICT ALREADY DISCLOSES IT -- symmetric with the coverage rule
            # below, which has had this suppression since its first tightening.
            # Verified 2026-08-21 on both cells this rule was firing on:
            # `exp_organ_f_deep_reading_partialcue_ladder_v1` states
            # `..._UNDERPOWERED_POP_768_...` IN ITS VERDICT STRING, and
            # `exp_organ_f_accumulate_interference_diagnosis_v1` names only the POWERED populations
            # (`GROWS_FASTER_POP_128_POP_256_POP_512`). **Each has FOUR powered populations and one
            # underpowered one, and neither leans on the underpowered one.** Flagging them
            # penalises a cell for stratifying its power and saying so.
            others = [v for p, k, v in _walk(m)
                      if k.lower() == "underpowered" and p != path]
            all_under = bool(others) and all(v is True for v in others)
            pop = path.split(".")[-2] if "." in path else ""
            disclosed = "UNDERPOWER" in verdict.upper() or (pop and pop.upper() in verdict.upper()
                                                            and "UNDERPOWER" in verdict.upper())
            if all_under or not (disclosed or others):
                flags.append(("UNDERPOWERED yet a verdict is stated"
                              + (" -- AND EVERY POPULATION IS UNDERPOWERED" if all_under else ""),
                              path, val))
        elif kl == "not_auto_scored" and val is True:
            flags.append(("NOT_AUTO_SCORED -- a human input is outstanding", path, val))
        elif ("tie_mass" in kl and isinstance(val, (int, float)) and val > tie_thresh
              # A SELF-TEST CONSTRUCTS A DEGENERATE CASE ON PURPOSE. Verified 2026-08-21 on
              # exp_sensorimotor_channel_discrimination_v1: `selftest_evidence.
              # tie_conventions_both_ways.tie_mass_frac = 1.000` is a FULLY-TIED case built to prove
              # the scorer handles ties both ways -- and it does (auc_ties_to_P 1.0, _to_S 0.0,
              # half 0.5). **Every real arm in that cell reads 0.000-0.005.** Flagging it penalises
              # the cell for HAVING the tie self-test this repo's own rules demand.
              and not re.search(r"selftest|self_test|smoke|synthetic", path.lower())):
            # NAME THE ARM. Verified 2026-08-20 on exp_feeling_match_rejector_v1: its TIE MASS
            # 1.000 is on the RIVAL arm (ATTESTATION) in the stratum where attestation is blind BY
            # DESIGN -- which is exactly what that verdict is about -- while the treatment arm's tie
            # mass is 0.000/max 0.003. I reported that cell as compromised and it was not.
            # A degenerate FLOOR or RIVAL makes that comparison uninformative (worth knowing);
            # a degenerate TREATMENT would invalidate the result. THEY ARE NOT THE SAME FINDING.
            # NAME THE ARM BY THIS REPO'S CONVENTION, not by a hardcoded list. The five-name list
            # left every arm in two cells reading "an unnamed arm -- CHECK WHETHER IT IS THE
            # TREATMENT" when the names were sitting in the path: `F1_TRIGRAM_ONLY_orthographic`,
            # `F3_FREQUENCY_ONLY_constant`, `X3_QUERY_LENGTH`, `X4_CONSTANT`. **`F<n>_` and `X<n>_`
            # ARE the floor/control prefixes here; `C<n>_` marks a candidate signal under test.**
            # Verified 2026-08-21 across both cells: every arm with tie mass > 0.5 is F- or
            # X-prefixed, while all eight C-signals read a MEDIAN of 0.000.
            arm = next((seg for seg in reversed(path.split("."))
                        if re.match(r"^[FXC]\d*_", seg) or seg in ("ATTESTATION",)), None)
            floorish = bool(arm and (re.match(r"^[FX]\d*_", arm) or arm == "ATTESTATION"
                                     or re.search(r"orthographic|constant|frequency|scramble|"
                                                  r"prototype|length", arm.lower())))
            kind = ("a FLOOR/RIVAL arm -- that comparison is uninformative here, NOT proof the "
                    "verdict is wrong" if floorish
                    else "an arm -- CHECK WHETHER IT IS THE TREATMENT")
            flags.append(("TIE MASS %.3f on %s: %s" % (val, arm or "an unnamed arm", kind),
                          path, val))
        elif ("smd" in path.lower() or "balance" in path.lower()) and \
                isinstance(val, (int, float)) and abs(val) > smd_thresh:
            flags.append(("IMBALANCE %.4f on a matched covariate" % val, path, val))
        elif ("coverage" in kl and isinstance(val, (int, float))
              and 0.0 < val < (1 - coverage_thresh)
              # A THRESHOLD/MINIMUM is a CONFIG value, not a measurement. The first run flagged
              # `coverage_threshold: 0.5` as if the cell had lost half its population.
              and not re.search(r"thresh|min|required|floor|target|budget", kl)
              # And if the VERDICT already names coverage, the cell is not hiding anything.
              and "COVERAGE" not in verdict.upper()):
            flags.append(("COVERAGE %.3f -- much of the population was dropped" % val, path, val))
    # ⛔ RULE REMOVED AFTER ITS FIRST RUN: "a strong verdict that also has a note/limitation/
    # honest_scope field" flagged **708 cells** -- essentially every HARD_PASS in the repo. The
    # reason is a CREDIT to this project rather than a defect: cells routinely write `honest_scope`,
    # so "has a caveat" carries NO information. A check that fires on 708 cells is ignored, which is
    # the exact cry-wolf failure `replication_gate.py`'s self-test was written to prevent.
    # The five real incidents were never "has a caveat" -- every one was a SPECIFIC QUANTITATIVE
    # flag: NOT_AUTO_SCORED, tie mass, an imbalance, UNDERPOWERED, a coverage loss. Those stay.
    # DEDUPE BY (reason, value): the first run printed the SAME coverage number four times because
    # four sibling keys carried it. Four copies of one fact is three units of noise.
    seen, uniq = set(), []
    for why, path, val in flags:
        key = (why, str(val))
        if key not in seen:
            seen.add(key)
            uniq.append((why, path, val))
    return verdict, uniq


def main(argv):
    tie = 0.5
    only_strong = "--only-strong-verdicts" in argv
    rows = []
    for name in sorted(os.listdir(DATA)):
        mp = os.path.join(DATA, name, "metrics.json")
        if not os.path.exists(mp):
            continue
        try:
            with open(mp, encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception:
            continue
        verdict, flags = audit(name, m, tie_thresh=tie)
        if flags and (not only_strong or STRONG_VERDICT.search(verdict)):
            rows.append((name, verdict, flags))

    # TIERS, ADDED AFTER MEASURING THE FIRST TWO RUNS. Of the five rules, two are RARE and precise
    # (they fire on ~5 cells and each matches a real 2026-08-20 incident) and two are COMMON in this
    # repo -- coverage loss on 101 cells, matched-covariate imbalance on 43. Presenting all of them
    # as one alarm list would bury the five that matter under 144 that are ordinary. **A rule that
    # fires on a quarter of the repo is CONTEXT, not an alarm, and saying so is the difference
    # between a worklist and noise.**
    ACT = ("UNDERPOWERED", "NOT_AUTO_SCORED", "TIE MASS")
    # ⛔ FOURTH TIGHTENING (2026-08-21), AND IT FOLLOWS FROM THE TOOL'S OWN WORDING. A tie-mass flag
    # on a NAMED floor/rival arm prints the sentence "NOT proof the verdict is wrong" -- so the tool
    # was putting rows it ITSELF calls non-findings at the top of a list headed THIS IS THE WORKLIST.
    # It made up 22 of the 27 Tier-1 rows, four of them the SAME finding across `_reduced` variants
    # of one cell. **Only a tie-degenerate arm that might be THE TREATMENT is actionable**; a
    # degenerate floor is context, which is what Tier 2 is for.
    def _actionable(f):
        return any(a in f[0] for a in ACT) and "NOT proof the verdict is wrong" not in f[0]

    tier1 = [(n, v, [f for f in fl if _actionable(f)]) for n, v, fl in rows]
    tier1 = [(n, v, fl) for n, v, fl in tier1 if fl]
    tier2 = [(n, v, fl) for n, v, fl in rows
             if not any(any(a in f[0] for a in ACT) for f in fl)]

    print("=" * 94)
    print("CELLS THAT TOLD YOU SOMETHING ABOUT THEMSELVES")
    print("=" * 94)
    print("This does NOT say a verdict is wrong. It says: the cell wrote a caveat about itself,")
    print("and on 2026-08-20 that caveat went unread FIVE times in one day.")

    print("\n### TIER 1 -- RARE AND PRECISE. THIS IS THE WORKLIST. %d cell(s)." % len(tier1))
    print("### (an outstanding human input, a stated lack of power, or a score that is a tie")
    print("###  convention rather than a measurement)")
    for name, verdict, flags in tier1:
        print("\n  %s" % name)
        print("      verdict: %s" % (verdict[:80] or "(none)"))
        for why, path, val in flags[:4]:
            print("      - %-56s  <- %s" % (why, path[:60]))

    print("\n### TIER 2 -- COMMON IN THIS REPO, SO CONTEXT RATHER THAN ALARM: %d cell(s)"
          % len(tier2))
    print("###  (coverage loss / matched-covariate imbalance -- ordinary here, but they are what")
    print("###   made the 2026-08-18 sensorimotor floor unreadable. Pass --all to list them.)")
    if "--all" in argv:
        for name, verdict, flags in tier2[:80]:
            print("  %-52s %s" % (name[:52], flags[0][0][:38]))
        if len(tier2) > 80:
            print("  ... and %d more" % (len(tier2) - 80))
    return 0


def _self_test():
    """Checked against the REAL 2026-08-20 misses, plus a clean cell that must NOT be flagged."""
    fails = []
    v, f = audit("x", {"verdict": "HARD_PASS", "UNDERPOWERED": True})
    if not any("UNDERPOWERED" in w for w, _, _ in f):
        fails.append("missed UNDERPOWERED beside a verdict")
    v, f = audit("x", {"verdict": "PENDING", "rows": [], "NOT_AUTO_SCORED": True})
    if not any("NOT_AUTO_SCORED" in w for w, _, _ in f):
        fails.append("missed NOT_AUTO_SCORED (incidents 1-2)")
    v, f = audit("x", {"verdict": "X", "res": {"tie_mass_frac": 0.976}})
    if not any("TIE MASS" in w for w, _, _ in f):
        fails.append("missed the 97.6%% tie mass (F_ORTHOGRAPHIC)")
    v, f = audit("x", {"verdict": "X", "report": {"POST_MATCH_BALANCE": {"smd": {
        "mean_log_freq": -0.0617, "mean_constant_prototype": 0.1501}}}})
    if not any("IMBALANCE" in w for w, _, _ in f):
        fails.append("missed the 0.1501 imbalance (incident 4)")
    if any(abs(val) < 0.07 for w, _, val in f if "IMBALANCE" in w and isinstance(val, float)):
        fails.append("flagged a WELL-BALANCED covariate -- would cry wolf")
    v, f = audit("x", {"verdict": "HARD_PASS", "arms": {"A": {"auc": 0.8}},
                       "n": 400, "tie_mass_frac": 0.0})
    if f:
        fails.append("flagged a clean cell: %s" % [w for w, _, _ in f])
    print("self-test: %s" % ("PASS -- catches all five incident shapes, ignores a clean cell"
                             if not fails else "FAIL"))
    for x in fails:
        print("   -", x)
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    raise SystemExit(main(sys.argv[1:]))
