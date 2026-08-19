"""APPLY THE PRE-COMMITTED READINGS MECHANICALLY. The verdict is COMPUTED, not narrated.

WHY THIS EXISTS. This archive's measured failure mode is not bad arithmetic -- it is a human
reading a table after seeing it. Of 30 vetted HARD_PASS cells, ONE survived; the recurring shapes
were a stronger floor available and a weaker one used, a gate whose margin was literally 0.0, and
a ceiling guard that fired and was AMENDED AWAY AFTER THE RUN. On 2026-08-19 alone, four control
defects were built and caught in one session, and one experiment that COULD NOT SUCCEED was nearly
filed as a negative.

So the readings for `exp_substrate_end_to_end_readout_v1` are encoded here as CODE, and this tool
prints the verdict its own rules produce. It has no opinion and it cannot be talked round.

THE RULES, exactly as pre-registered in the cell's docstring before any number existed:
  (a) a substrate route clears the STRONGEST floor's UPPER bound, CI-separated, AND at least one
      ablation degrades it            -> THE ASSEMBLY WORKS; name the organ.
  (b) a route clears the floor but NO ablation moves anything
                                      -> THE FLOOR IS SCORING AND THE ORGANS ARE DECORATION.
  (c) no route clears the floor, AND the instrument is alive
                                      -> A REAL NEGATIVE.
  (d) the SCRAMBLE twin ties the real cue
                                      -> THE PIPELINE IS NOT READING; every other number is VOID.
  (e) [SR-specific] SR clears only at the SMALLEST gamma
                                      -> IT IS THE 1-STEP COUNTER WEARING A MATRIX.

INSTRUMENT-ALIVE is a PRECONDITION of (c), not a footnote: if the exact-key arm cannot retrieve an
episode it stored verbatim, the cell is broken and reports NOTHING. A negative from a dead
instrument is not a negative.

USAGE
  python tools/readout_verdict.py
  python tools/readout_verdict.py --metrics <path>
  python tools/readout_verdict.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from typing import Dict, List, Optional

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT = os.path.join(REPO, "data", "exp_substrate_end_to_end_readout_v1", "metrics.json")

SUBSTRATE_ROUTES = ("EPISODIC", "SEMANTIC")
HELD = "HELD_OUT"
SEEN = "SEEN_exact_key"


def _mean(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def _arm(units: List[dict], regime: str, arm: str, field: str = "hit@1") -> Optional[float]:
    return _mean([u.get(regime, {}).get(arm, {}).get(field) for u in units])


def analyse(metrics: dict, spec: Optional[str] = None) -> dict:
    raw = metrics.get("units", {})
    units = list(raw.values()) if isinstance(raw, dict) else list(raw)

    # *** SPEC ISOLATION, AND IT IS NOT OPTIONAL. ***
    # `units.jsonl` accumulates across runs, so after the v2 run the file holds BOTH v1 units
    # (no SR arms, COOC computed WITHOUT the cue-word exclusion) and v2 units. Averaging them
    # would put two different SPECIFICATIONS inside one number -- the same defect as importing a
    # floor across representations, which voided 21 arms in this project on 2026-08-18.
    # Default: the LATEST spec present, and the choice is reported rather than assumed.
    specs = sorted({str(u.get("unit_key", "")).split("|")[0] for u in units if u.get("unit_key")})
    chosen = spec or (specs[-1] if specs else None)
    if chosen:
        units = [u for u in units if str(u.get("unit_key", "")).startswith(chosen + "|")]

    base = [u for u in units if not u.get("ablate")]
    if not base:
        return {"error": f"no un-ablated units for spec {chosen!r}", "specs_present": specs}
    sr_arms = sorted({k for u in base for k in u.get(HELD, {}) if k.startswith("SR_g")})
    routes = list(SUBSTRATE_ROUTES) + sr_arms

    out: Dict[str, object] = {"specs_present": specs, "SPEC_ANALYSED": chosen,
                              "n_units_in_spec": len(units), "n_baseline_seeds": len(base),
                              "sr_arms": sr_arms}

    # -- PRECONDITION: is the instrument alive? -------------------------------------------------
    seen_epi = _arm(base, SEEN, "EPISODIC")
    seen_scr = _arm(base, SEEN, "SCRAMBLE")
    seen_p = _arm(base, SEEN, "SCRAMBLE", "perm_p_vs_EPISODIC")
    alive = bool(seen_epi and seen_scr is not None and seen_epi > seen_scr
                 and (seen_p is not None and seen_p < 0.05))
    out["instrument"] = {"exact_key_EPISODIC": seen_epi, "exact_key_SCRAMBLE": seen_scr,
                         "perm_p": seen_p, "ALIVE": alive}

    # -- (d) does the scramble twin tie the real cue on the REAL operating point? ----------------
    held_p = _arm(base, HELD, "SCRAMBLE", "perm_p_vs_EPISODIC")
    d_fires = bool(held_p is not None and held_p > 0.05)
    out["reading_d_scramble_ties"] = {"perm_p_held_out": held_p, "FIRES": d_fires}

    # -- the bar, and it is the floor's UPPER bound, never its point value ----------------------
    bar = _mean([u.get(HELD, {}).get("_credible_bar") for u in base])
    strongest = base[0].get(HELD, {}).get("_strongest_floor")
    out["bar"] = {"strongest_floor": strongest, "credible_bar_floor_ci_upper": bar}

    # -- which routes clear it -----------------------------------------------------------------
    clears = {}
    for r in routes:
        v = _arm(base, HELD, r)
        hw = _arm(base, HELD, r, "ci_half_width")
        p = _arm(base, HELD, r, "perm_p_vs_floor")
        sep = bool(v is not None and bar is not None and hw is not None
                   and (v - hw) > bar and p is not None and p < 0.05)
        clears[r] = {"hit@1": v, "ci_half_width": hw, "perm_p_vs_floor": p,
                     "CLEARS_CI_SEPARATED": sep}
    out["held_out_routes"] = clears
    any_clear = [r for r, c in clears.items() if c["CLEARS_CI_SEPARATED"]]

    # -- do any ablations move a clearing route? -----------------------------------------------
    abl_effect = {}
    for u in units:
        ab = "+".join(u.get("ablate") or ()) or None
        if not ab:
            continue
        for r in routes:
            b = _arm(base, HELD, r)
            v = u.get(HELD, {}).get(r, {}).get("hit@1")
            if b is None or v is None:
                continue
            abl_effect.setdefault(ab, {})[r] = round(v - b, 6)
    out["ablation_deltas_held_out"] = abl_effect
    # AN ABLATION "MOVES" ONLY IF ITS DELTA EXCEEDS THE BASELINE'S OWN CI HALF-WIDTH.
    # The first version of this rule used `abs(d) > 1e-9`, which on the landed v1 metrics counted
    # deltas of -0.001 against a 0.004 baseline as organ effects. That is a WIDTH being read as an
    # EFFECT -- standing discipline 14, and the exact error that cost this project three
    # retractions in one night. It only bites in branches (a) and (b), which is precisely where it
    # would have credited an organ with noise.
    moved_pairs = []
    for ab, m in abl_effect.items():
        for r, d in m.items():
            hw = _arm(base, HELD, r, "ci_half_width") or 0.0
            if abs(d) > max(hw, 1e-9):
                moved_pairs.append({"ablation": ab, "route": r, "delta": d,
                                    "baseline_ci_half_width": hw})
    moved = bool(moved_pairs)
    out["ablations_that_move_beyond_the_ci"] = moved_pairs
    out["any_ablation_moves_anything"] = moved

    # -- (e) SR gamma reading -------------------------------------------------------------------
    if sr_arms:
        gammas = {a: float(a.split("g")[-1]) for a in sr_arms}
        clearing = [a for a in sr_arms if clears[a]["CLEARS_CI_SEPARATED"]]
        smallest = min(sr_arms, key=lambda a: gammas[a])
        out["reading_e_sr_is_a_counter"] = {
            "clearing_sr_arms": clearing,
            "FIRES": bool(clearing and set(clearing) == {smallest})}

    # -- THE VERDICT, produced by the rules ------------------------------------------------------
    if not alive:
        verdict = ("INSTRUMENT DEAD -- THE CELL REPORTS NOTHING. The exact-key arm cannot retrieve "
                   "an episode it stored verbatim, so no negative here is attributable to the "
                   "substrate.")
    elif d_fires and not any_clear:
        verdict = ("(c)+(d) A REAL NEGATIVE, AND THE PIPELINE IS NOT READING THE HELD-OUT CUE. "
                   "No route clears the floor's upper bound, and an unrelated cue scores the same "
                   "as the real one. The instrument IS alive at exact key, which is what makes "
                   "this a result rather than a broken cell.")
    elif not any_clear:
        verdict = ("(c) A REAL NEGATIVE. No substrate route clears the strongest floor's upper "
                   "bound, and the instrument is alive.")
    elif moved:
        verdict = (f"(a) THE ASSEMBLY DOES WORK. Clearing route(s): {any_clear}, and at least one "
                   f"ablation degrades the result -- name the organ from the deltas.")
    else:
        verdict = (f"(b) THE FLOOR IS SCORING AND THE ORGANS ARE DECORATION. Route(s) {any_clear} "
                   f"clear the floor, but NO ablation moves anything. Report it that way.")
    if out.get("reading_e_sr_is_a_counter", {}).get("FIRES"):
        verdict += (" ALSO (e): SR clears ONLY at the smallest gamma -- it is the 1-step counter "
                    "wearing a matrix.")
    out["VERDICT"] = verdict
    return out


def self_test() -> int:
    ok = True

    def check(c, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if c else 'FAIL'} {label}",
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    def unit(ablate, held_epi, held_p_scr, bar, hw=0.001, p_floor=0.001, seen_epi=0.9):
        return {"ablate": list(ablate),
                SEEN: {"EPISODIC": {"hit@1": seen_epi},
                       "SCRAMBLE": {"hit@1": 0.01, "perm_p_vs_EPISODIC": 0.0005}},
                HELD: {"EPISODIC": {"hit@1": held_epi, "ci_half_width": hw,
                                    "perm_p_vs_floor": p_floor},
                       "SEMANTIC": {"hit@1": 0.0, "ci_half_width": hw, "perm_p_vs_floor": 1.0},
                       "SCRAMBLE": {"hit@1": 0.003, "perm_p_vs_EPISODIC": held_p_scr},
                       "_strongest_floor": "COOC_floor", "_credible_bar": bar}}

    # (c)+(d): nothing clears and the scramble ties
    r = analyse({"units": [unit((), 0.004, 0.9, 0.037)]})
    check("(c)+(d)" in r["VERDICT"], "fires (c)+(d) when nothing clears and scramble ties")
    check(r["instrument"]["ALIVE"], "instrument reported alive off the exact-key arm")

    # dead instrument beats every other reading
    dead = unit((), 0.5, 0.9, 0.037, seen_epi=0.005)
    dead[SEEN]["SCRAMBLE"] = {"hit@1": 0.9, "perm_p_vs_EPISODIC": 0.9}
    r2 = analyse({"units": [dead]})
    check("INSTRUMENT DEAD" in r2["VERDICT"],
          "a dead instrument overrides everything -- a negative from it is not a negative")

    # (b): clears the floor, no ablation moves
    u_base = unit((), 0.30, 0.001, 0.037)
    u_abl = unit(("episodic",), 0.30, 0.001, 0.037)
    r3 = analyse({"units": [u_base, u_abl]})
    check(r3["VERDICT"].startswith("(b)"), "fires (b) when a route clears but no ablation moves")

    # (a): clears the floor and an ablation moves BEYOND the baseline's CI half-width
    u_abl2 = unit(("episodic",), 0.10, 0.001, 0.037)
    r4 = analyse({"units": [u_base, u_abl2]})
    check(r4["VERDICT"].startswith("(a)"), "fires (a) when a route clears and an ablation degrades")

    # A WIDTH IS NOT AN EFFECT: a delta SMALLER than the baseline's own CI half-width must NOT
    # count as an organ effect. Without this the tool credits an organ with noise, which is the
    # error class behind three retractions in one night.
    u_noise = unit(("definitions",), 0.30 - 0.0005, 0.001, 0.037, hw=0.01)
    u_base_w = unit((), 0.30, 0.001, 0.037, hw=0.01)
    r5 = analyse({"units": [u_base_w, u_noise]})
    check(not r5["any_ablation_moves_anything"],
          "a delta INSIDE the baseline CI half-width does NOT count as an ablation effect")
    check(r5["VERDICT"].startswith("(b)"),
          "so the verdict falls to (b) -- the floor is scoring -- instead of crediting an organ")

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", default=DEFAULT)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not os.path.isfile(a.metrics):
        print(f"[verdict] no metrics at {a.metrics} -- has the run landed?", file=sys.stderr)
        return 1
    with open(a.metrics, "r", encoding="utf-8") as fh:
        m = json.load(fh)
    r = analyse(m)
    print(json.dumps(r, indent=2, default=str))
    print("\n" + "=" * 78)
    print("VERDICT (produced by the pre-committed rules, not by reading the table):")
    print(r.get("VERDICT", "(none)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
