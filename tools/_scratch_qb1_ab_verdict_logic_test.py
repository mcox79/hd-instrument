"""Device-independent de-risk for exp_q_b1_ab_iterate_3arm_v1_n16384 verdict logic.
Mirrors snaps_for / _depth_pass / _seed_floor_frac / compute_verdict VERBATIM (no torch),
asserts on fabricated profiles. Run on .venv before GPU dispatch. NOT a cell; scratch only."""
from typing import Dict, List, Tuple

ARMS = ["control", "cand_c_tropical", "cand2_cleanup"]
DEPTHS = [100, 276, 280, 287, 293]
RUN_MODE = "full"
HP_THRESH = {5: 0.90, 20: 0.75, 50: 0.50, 100: 0.20, 200: 0.02}
ENDPOINT_HP = 0.005
HF_D5 = 0.80; HF_D20 = 0.50; HF_ENDPOINT = 0.001
BASE_SNAPS = [1, 3, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100,
              120, 140, 160, 180, 200, 220, 240, 260, 276, 280, 287, 293]


def snaps_for(depth):
    s = [d for d in BASE_SNAPS if d < depth]; s.append(depth); return s


def _depth_pass(profile, depth):
    def g(d): return profile.get(str(d), 0.0)
    endpoint = g(depth)
    if g(5) < HF_D5 or g(20) < HF_D20 or endpoint < HF_ENDPOINT:
        return "FAIL"
    ok = True
    for d, thr in HP_THRESH.items():
        if d <= depth and d != depth:
            ok = ok and (g(d) >= thr)
    endpoint_bar = HP_THRESH.get(depth, ENDPOINT_HP)
    ok = ok and (endpoint >= endpoint_bar)
    return "PASS" if ok else "MIDDLE"


def _seed_floor_frac(units, arm, depth):
    rel = [u for u in units if u["depth"] == depth]
    if not rel: return 0.0
    ok = 0
    for u in rel:
        p = u["arms"][arm]
        if p.get("5", 0.0) >= HF_D5 and p.get("20", 0.0) >= HF_D20 and p.get(str(depth), 0.0) >= HF_ENDPOINT:
            ok += 1
    return ok / len(rel)


def compute_verdict(units):
    mean_prof = {a: {} for a in ARMS}
    for depth in DEPTHS:
        rel = [u for u in units if u["depth"] == depth]
        for arm in ARMS:
            acc = {}
            for u in rel:
                for k, v in u["arms"][arm].items():
                    acc.setdefault(k, []).append(v)
            mean_prof[arm][depth] = {k: sum(v) / len(v) for k, v in acc.items()}
    per_depth = {a: {} for a in ARMS}; robust = {a: {} for a in ARMS}
    for arm in ARMS:
        for depth in DEPTHS:
            per_depth[arm][depth] = _depth_pass(mean_prof[arm][depth], depth)
            robust[arm][depth] = _seed_floor_frac(units, arm, depth)

    def passed(arm, depth):
        need = 0.8 if RUN_MODE == "full" else 0.5
        return per_depth[arm][depth] == "PASS" and robust[arm][depth] >= need

    arm_verdict = {}
    for arm in ARMS:
        no_regression = passed(arm, 100) and passed(arm, 276)
        worse_than_control = (arm != "control") and any(
            mean_prof[arm][d].get(str(d), 0.0) + 1e-9 < mean_prof["control"][d].get(str(d), 0.0)
            for d in DEPTHS if d >= 287)
        if not no_regression:
            arm_verdict[arm] = "HARD_FAIL"
        elif worse_than_control:
            arm_verdict[arm] = "HARD_FAIL"
        elif any(passed(arm, d) for d in DEPTHS if d >= 287):
            arm_verdict[arm] = "HARD_PASS"
        elif passed(arm, 280):
            arm_verdict[arm] = "MIDDLE_BAND"
        else:
            arm_verdict[arm] = "HARD_FAIL"
    cand = [a for a in ARMS if a != "control"]
    rank = {"HARD_PASS": 3, "MIDDLE_BAND": 2, "HARD_FAIL": 1}
    best = max(cand, key=lambda a: rank[arm_verdict[a]])
    overall = arm_verdict[best] if rank[arm_verdict[best]] > 1 else "HARD_FAIL"
    return overall, arm_verdict, best


# ---- fabricated profiles ----
def prof(d5, d20, d50, d100, d200, ep, depth):
    """Build a snapshot profile dict for a chain of `depth` with given anchor values."""
    p = {}
    for d in snaps_for(depth):
        if d == 5: p["5"] = d5
        elif d == 20: p["20"] = d20
        elif d == 50: p["50"] = d50
        elif d == 100: p["100"] = d100
        elif d == 200: p["200"] = d200
        elif d == depth: p[str(d)] = ep
        else: p[str(d)] = 0.9  # other snaps healthy
    # ensure d5/d20/d50/d100/d200 present even if also endpoint
    p.setdefault("5", d5); p.setdefault("20", d20); p.setdefault("50", d50)
    p.setdefault("100", d100); p.setdefault("200", d200)
    return p


def healthy(depth, ep):       # passes all HP thresholds
    return prof(0.95, 0.85, 0.70, 0.40, 0.10, ep, depth)


def collapsed(depth, ep):     # mid-chain collapse -> FAIL (d50 below 0.50)
    return prof(0.88, 0.60, 0.30, 0.05, 0.0, ep, depth)


def make_units(arm_depth_profile):
    """arm_depth_profile: {arm: {depth: profile}}; 5 identical seeds."""
    units = []
    for seed in range(5):
        for depth in DEPTHS:
            units.append({"depth": depth, "seed": seed,
                          "arms": {a: arm_depth_profile[a][depth] for a in ARMS}})
    return units


def control_baseline():
    # control: PASS d100/d276, FAIL d280/287/293 (the known cliff)
    return {100: healthy(100, 0.40), 276: healthy(276, 0.02),
            280: collapsed(280, 0.0008), 287: collapsed(287, 0.0005), 293: collapsed(293, 0.0004)}


def run_case(name, cand2_dp, expect_overall, expect_cand2):
    adp = {"control": control_baseline(),
           "cand_c_tropical": control_baseline(),   # tropical = same as control unless overridden
           "cand2_cleanup": cand2_dp}
    overall, av, best = compute_verdict(make_units(adp))
    ok = (overall == expect_overall and av["cand2_cleanup"] == expect_cand2)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: overall={overall} cand2={av['cand2_cleanup']} "
          f"(expect overall={expect_overall} cand2={expect_cand2}) best={best}")
    assert ok, name
    return av


# Case 1: cand2 extends cleanly to d293 (passes all) -> HARD_PASS, swap to cand2
run_case("cand2 extends to d293",
         {100: healthy(100, 0.40), 276: healthy(276, 0.02), 280: healthy(280, 0.02),
          287: healthy(287, 0.015), 293: healthy(293, 0.01)},
         "HARD_PASS", "HARD_PASS")

# Case 2: cand2 only reaches d280 (MIDDLE), fails 287 -> MIDDLE_BAND
run_case("cand2 reaches d280 only",
         {100: healthy(100, 0.40), 276: healthy(276, 0.02), 280: healthy(280, 0.02),
          287: collapsed(287, 0.0006), 293: collapsed(293, 0.0004)},
         "MIDDLE_BAND", "MIDDLE_BAND")

# Case 3: cand2 extends to d293 BUT regresses at d100 -> HARD_FAIL (bad swap)
run_case("cand2 extends but regresses d100",
         {100: collapsed(100, 0.05), 276: healthy(276, 0.02), 280: healthy(280, 0.02),
          287: healthy(287, 0.015), 293: healthy(293, 0.01)},
         "HARD_FAIL", "HARD_FAIL")

# Case 4: cand2 = control (no extension) -> HARD_FAIL
run_case("cand2 no extension (== control)", control_baseline(), "HARD_FAIL", "HARD_FAIL")

# Case 5: control per-depth verdicts sanity (PASS d100/d276, FAIL beyond)
_o, _av, _b = compute_verdict(make_units({a: control_baseline() for a in ARMS}))
print(f"[INFO] all-control: overall={_o} (expect HARD_FAIL; no candidate extends)")
assert _o == "HARD_FAIL"

# Case 6: tropical wins, cand2 fails -> best = tropical, overall HARD_PASS
adp6 = {"control": control_baseline(),
        "cand_c_tropical": {100: healthy(100, 0.40), 276: healthy(276, 0.02), 280: healthy(280, 0.02),
                            287: healthy(287, 0.015), 293: healthy(293, 0.01)},
        "cand2_cleanup": control_baseline()}
o6, av6, b6 = compute_verdict(make_units(adp6))
print(f"[{'PASS' if (o6=='HARD_PASS' and b6=='cand_c_tropical') else 'FAIL'}] tropical wins: "
      f"overall={o6} best={b6} tropical={av6['cand_c_tropical']}")
assert o6 == "HARD_PASS" and b6 == "cand_c_tropical"

print("\nALL VERDICT-LOGIC CASES PASS")
