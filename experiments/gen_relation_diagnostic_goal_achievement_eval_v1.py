"""Author the POWERED, construct-valid relation-diagnostic eval for goal<->outcome
ACHIEVEMENT (met/unmet). Report-only (writes jsonl to this scratchpad only).

Construct fix (validated by relation_diagnostic_pilot[.py|_qualitative.py]): the old
eval built MET/UNMET by VARYING THE OUTCOME, so outcome-surface alone solved it and
the goal<->outcome RELATION was never tested. Here every PAIR = one fixed, neutral
OUTCOME text + two GOALS (one MET, one UNMET). Outcome text carries NO evaluative
language; the GOAL supplies the standard. Verdict depends only on comparing
outcome_value to goal_target under the item's direction (numeric) or on label
equality (attr_match).

Self-contained, pure python (no heavy imports, no WordNet). Deterministic (seeded).
"""
import json
import os
import re
import random
from collections import defaultdict

SEED = 1234
random.seed(SEED)

SCRATCHPAD = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRATCHPAD, "relation_diagnostic_eval.jsonl")

BANNED_VALENCE = [
    "won", "lost", "nailed", "aced", "crushed", "bombed", "flopped", "failed",
    "succeeded", "smashed", "botched", "ghosted", "great", "terrible", "finally",
    "unfortunately", "sadly", "thrilled", "disappointed",
]
BANNED_RE = re.compile(r"\b(" + "|".join(re.escape(w) for w in BANNED_VALENCE) + r")\b", re.IGNORECASE)

# =====================================================================
# PAIRS: relation_type, outcome_text (neutral/factual, fixed), outcome_value,
# direction, goals=[(goal_text, goal_target, gold), (goal_text, goal_target, gold)]
# =====================================================================
PAIRS = []

# ---------------- numeric_threshold (continuous magnitude) ----------------
PAIRS += [
    dict(relation_type="numeric_threshold",
         outcome_text="Priya's resting heart rate measured 62 beats per minute at her physical.",
         outcome_value=62, direction="lower_is_better",
         goals=[("Her doctor wanted it under 70 to rule out early heart strain.", 70, "MET"),
                ("Her trainer was pushing her to get it under 55 for competitive cycling.", 55, "UNMET")]),
    dict(relation_type="numeric_threshold",
         outcome_text="The car's fuel economy came out to 34 miles per gallon on the highway test.",
         outcome_value=34, direction="higher_is_better",
         goals=[("They needed at least 30 mpg to qualify for the tax credit.", 30, "MET"),
                ("The dealership had advertised 40 mpg on the window sticker.", 40, "UNMET")]),
    dict(relation_type="numeric_threshold",
         outcome_text="The new bridge design can hold a load of 18 tons.",
         outcome_value=18, direction="higher_is_better",
         goals=[("Regulations require the bridge to hold at least 15 tons for local traffic.", 15, "MET"),
                ("The county wanted a 25-ton rating to allow freight trucks.", 25, "UNMET")]),
    dict(relation_type="numeric_threshold",
         outcome_text="Jamal's long jump measured 5.8 meters at the meet.",
         outcome_value=5.8, direction="higher_is_better",
         goals=[("He needed 5.5 meters to qualify for districts.", 5.5, "MET"),
                ("He was chasing the school record of 6.4 meters.", 6.4, "UNMET")]),
    dict(relation_type="numeric_threshold",
         outcome_text="The apartment's monthly electric bill came to 95 dollars.",
         outcome_value=95, direction="lower_is_better",
         goals=[("They budgeted up to 120 dollars a month for electricity.", 120, "MET"),
                ("They set a strict cap of 80 dollars after switching providers.", 80, "UNMET")]),
    dict(relation_type="numeric_threshold",
         outcome_text="The new server responds to requests in 180 milliseconds on average.",
         outcome_value=180, direction="lower_is_better",
         goals=[("The spec called for under 250 milliseconds for the beta launch.", 250, "MET"),
                ("The performance team wanted the average under 100 milliseconds.", 100, "UNMET")]),
    dict(relation_type="numeric_threshold",
         outcome_text="The hikers' packs weighed 14 kilograms each at the trailhead scale.",
         outcome_value=14, direction="lower_is_better",
         goals=[("The guide recommended keeping packs under 16 kilograms for the altitude.", 16, "MET"),
                ("Their ultralight goal was to keep each pack under 10 kilograms.", 10, "UNMET")]),
]

# ---------------- quantity_count (discrete counts) ----------------
PAIRS += [
    dict(relation_type="quantity_count",
         outcome_text="The food truck sold 85 tacos during the lunch rush.",
         outcome_value=85, direction="higher_is_better",
         goals=[("They needed to sell at least 60 to cover the day's ingredient costs.", 60, "MET"),
                ("The owner had set a stretch goal of 150 tacos for a record day.", 150, "UNMET")]),
    dict(relation_type="quantity_count",
         outcome_text="The webinar had 210 people register.",
         outcome_value=210, direction="higher_is_better",
         goals=[("The marketing team hoped for at least 150 signups to justify the platform cost.", 150, "MET"),
                ("Leadership was targeting 500 signups for a viral launch.", 500, "UNMET")]),
    dict(relation_type="quantity_count",
         outcome_text="The animal shelter placed 9 dogs into new homes this month.",
         outcome_value=9, direction="higher_is_better",
         goals=[("The shelter's goal was at least 6 placements a month to keep kennels from overflowing.", 6, "MET"),
                ("The director had set a target of 20 placements for the adoption drive.", 20, "UNMET")]),
    dict(relation_type="quantity_count",
         outcome_text="The novelist's manuscript came in at 72,000 words.",
         outcome_value=72000, direction="higher_is_better",
         goals=[("The publisher required a minimum of 70,000 words for the imprint.", 70000, "MET"),
                ("She had been aiming to write a sprawling 120,000-word epic.", 120000, "UNMET")]),
    dict(relation_type="quantity_count",
         outcome_text="The recruiter received 34 applications for the open role.",
         outcome_value=34, direction="higher_is_better",
         goals=[("HR just wanted at least 20 applicants to have a reasonable pool.", 20, "MET"),
                ("The hiring manager was hoping for 75 applicants given the ad spend.", 75, "UNMET")]),
    dict(relation_type="quantity_count",
         outcome_text="The restaurant received 4 complaint calls during opening week.",
         outcome_value=4, direction="lower_is_better",
         goals=[("Management considered anything under 10 calls acceptable for a soft opening.", 10, "MET"),
                ("The new manager's target was at most 1 complaint all week.", 1, "UNMET")]),
    dict(relation_type="quantity_count",
         outcome_text="The app got 1,200 downloads in its first week.",
         outcome_value=1200, direction="higher_is_better",
         goals=[("The indie developer hoped for 500 downloads just to break even on ads.", 500, "MET"),
                ("The investor pitch had projected 10,000 downloads in the first week.", 10000, "UNMET")]),
]

# ---------------- temporal_deadline (time / date thresholds) ----------------
PAIRS += [
    dict(relation_type="temporal_deadline",
         outcome_text="The delivery truck arrived at the warehouse at 2:15 pm.",
         outcome_value=14.25, direction="lower_is_better",
         goals=[("The dock needed the truck by 3 pm to make the afternoon loading window.", 15.0, "MET"),
                ("The client wanted the shipment there by noon for same-day processing.", 12.0, "UNMET")]),
    dict(relation_type="temporal_deadline",
         outcome_text="The tax return was filed on April 12th.",
         outcome_value=12, direction="lower_is_better",
         goals=[("The accountant just needed it filed by April 15th to avoid penalties.", 15, "MET"),
                ("She had promised her partner she'd file by April 1st to get it out of the way early.", 1, "UNMET")]),
    dict(relation_type="temporal_deadline",
         outcome_text="The wedding cake was delivered at 9:30 am.",
         outcome_value=9.5, direction="lower_is_better",
         goals=[("The venue needed it there by 11 am before guests arrived.", 11.0, "MET"),
                ("The planner's schedule called for delivery by 8 am to allow setup time.", 8.0, "UNMET")]),
    dict(relation_type="temporal_deadline",
         outcome_text="The software team shipped the patch on day 5 of the incident.",
         outcome_value=5, direction="lower_is_better",
         goals=[("The SLA allowed up to 7 days to resolve a medium-severity incident.", 7, "MET"),
                ("The customer had been promised a fix within 2 days.", 2, "UNMET")]),
    dict(relation_type="temporal_deadline",
         outcome_text="The marathon runner crossed the finish line at the 250-minute mark.",
         outcome_value=250, direction="lower_is_better",
         goals=[("His goal was simply to finish under 5 hours, or 300 minutes.", 300, "MET"),
                ("He had trained all year to break 4 hours, or 240 minutes.", 240, "UNMET")]),
    dict(relation_type="temporal_deadline",
         outcome_text="The moving crew finished unloading the truck at 6:45 pm.",
         outcome_value=18.75, direction="lower_is_better",
         goals=[("The family just needed the truck cleared before dark, around 8 pm.", 20.0, "MET"),
                ("The crew had promised to be done by 5 pm to avoid overtime charges.", 17.0, "UNMET")]),
]

# ---------------- qualitative_attribute (same/opposed sensory or style attr) ----------------
PAIRS += [
    dict(relation_type="qualitative_attribute",
         outcome_text="The soup came out thick and creamy.",
         outcome_value="thick_creamy", direction="attr_match",
         goals=[("She was going for a hearty, stick-to-your-ribs chowder.", "thick_creamy", "MET"),
                ("She wanted a light, clear broth to start the meal.", "light_clear", "UNMET")]),
    dict(relation_type="qualitative_attribute",
         outcome_text="The band's new single has a slow, mellow groove.",
         outcome_value="slow_mellow", direction="attr_match",
         goals=[("They wanted a chill, laid-back track for a rainy-day playlist.", "slow_mellow", "MET"),
                ("They were trying to write a high-energy anthem for the stadium tour.", "high_energy", "UNMET")]),
    dict(relation_type="qualitative_attribute",
         outcome_text="The living room was repainted a warm terracotta orange.",
         outcome_value="warm_terracotta", direction="attr_match",
         goals=[("She wanted a cozy, warm palette for the reading nook.", "warm_terracotta", "MET"),
                ("She had asked for a cool, calming blue-gray for the space.", "cool_blue", "UNMET")]),
    dict(relation_type="qualitative_attribute",
         outcome_text="The stand-up set leaned heavily on dark, cynical jokes about office life.",
         outcome_value="dark_cynical", direction="attr_match",
         goals=[("The comedian wanted a biting, cynical set for the late-night crowd.", "dark_cynical", "MET"),
                ("The corporate client had asked for clean, upbeat material for the family event.", "clean_upbeat", "UNMET")]),
    dict(relation_type="qualitative_attribute",
         outcome_text="The hotel room turned out to be small and sparsely furnished.",
         outcome_value="small_sparse", direction="attr_match",
         goals=[("They'd booked expecting a cozy, minimalist budget room.", "small_sparse", "MET"),
                ("They had paid for a spacious suite with full furnishings.", "spacious_full", "UNMET")]),
    dict(relation_type="qualitative_attribute",
         outcome_text="The garden ended up wild and overgrown by midsummer.",
         outcome_value="wild_overgrown", direction="attr_match",
         goals=[("She wanted a natural, low-maintenance cottage-garden look.", "wild_overgrown", "MET"),
                ("She had been aiming for a tidy, manicured formal garden.", "tidy_manicured", "UNMET")]),
    dict(relation_type="qualitative_attribute",
         outcome_text="The essay's tone came across as formal and detached.",
         outcome_value="formal_detached", direction="attr_match",
         goals=[("The professor had asked for an objective, academic tone.", "formal_detached", "MET"),
                ("The editor wanted a warm, conversational voice for the blog.", "warm_conversational", "UNMET")]),
]

# ---------------- categorical_match (discrete category identity) ----------------
PAIRS += [
    dict(relation_type="categorical_match",
         outcome_text="The travel agent booked them a window seat on the flight.",
         outcome_value="window", direction="attr_match",
         goals=[("Maria specifically requested a window seat to watch the landing.", "window", "MET"),
                ("Maria had asked for an aisle seat so she could get up easily.", "aisle", "UNMET")]),
    dict(relation_type="categorical_match",
         outcome_text="The kitchen sent out the pasta with a mushroom cream sauce.",
         outcome_value="mushroom_cream", direction="attr_match",
         goals=[("The table had ordered the mushroom cream pasta.", "mushroom_cream", "MET"),
                ("The table had ordered the spicy arrabbiata instead.", "arrabbiata", "UNMET")]),
    dict(relation_type="categorical_match",
         outcome_text="IT provisioned him a laptop running Windows.",
         outcome_value="windows", direction="attr_match",
         goals=[("He'd requested a Windows machine to match his home setup.", "windows", "MET"),
                ("He'd specifically requested a Mac for the design work.", "mac", "UNMET")]),
    dict(relation_type="categorical_match",
         outcome_text="The print shop delivered the flyers on matte cardstock.",
         outcome_value="matte_cardstock", direction="attr_match",
         goals=[("The client's order specified matte cardstock.", "matte_cardstock", "MET"),
                ("The client's order specified glossy photo paper.", "glossy_paper", "UNMET")]),
    dict(relation_type="categorical_match",
         outcome_text="The car rental counter handed over a compact sedan.",
         outcome_value="compact_sedan", direction="attr_match",
         goals=[("The reservation was for a compact sedan.", "compact_sedan", "MET"),
                ("The reservation was for a full-size SUV.", "full_size_suv", "UNMET")]),
]

# =====================================================================
# Flatten to items
# =====================================================================
items = []
type_counter = defaultdict(int)
for p in PAIRS:
    type_counter[p["relation_type"]] += 1
    pair_id = "%s_%02d" % (p["relation_type"], type_counter[p["relation_type"]])
    for goal_text, goal_target, gold in p["goals"]:
        items.append(dict(
            id="%s_%s" % (pair_id, gold),
            pair_id=pair_id,
            relation_type=p["relation_type"],
            goal_text=goal_text,
            outcome_text=p["outcome_text"],
            gold=gold,
            goal_target=goal_target,
            outcome_value=p["outcome_value"],
            direction=p["direction"],
        ))

n_items = len(items)
n_met = sum(1 for it in items if it["gold"] == "MET")
n_unmet = sum(1 for it in items if it["gold"] == "UNMET")

# =====================================================================
# ORACLE
# =====================================================================
def oracle_predict(outcome_value, goal_target, direction):
    if direction == "attr_match":
        return "MET" if outcome_value == goal_target else "UNMET"
    try:
        ov = float(outcome_value)
        gt = float(goal_target)
    except (TypeError, ValueError):
        return "UNMET"  # scrambled type-mismatch -> not comparable, treat as miss
    if direction == "higher_is_better":
        return "MET" if ov >= gt else "UNMET"
    else:
        return "MET" if ov <= gt else "UNMET"

oracle_correct = sum(1 for it in items if oracle_predict(it["outcome_value"], it["goal_target"], it["direction"]) == it["gold"])
oracle_acc = oracle_correct / n_items

# =====================================================================
# SELF-CHECK 1: pairing integrity -> outcome-only best-possible acc
# =====================================================================
by_outcome = defaultdict(list)
for it in items:
    by_outcome[it["outcome_text"]].append(it["gold"])
pairing_ok = all(g.count("MET") == 1 and g.count("UNMET") == 1 for g in by_outcome.values())
outcome_only_best = sum(max(g.count("MET"), g.count("UNMET")) for g in by_outcome.values())
outcome_only_acc = outcome_only_best / n_items

# =====================================================================
# SELF-CHECK 2: pairscramble collapse (permute (goal_target, direction) across ALL items)
# =====================================================================
def pairscramble_acc(seed):
    rng = random.Random(seed)
    donors = [(it["goal_target"], it["direction"]) for it in items]
    perm = list(range(n_items))
    rng.shuffle(perm)
    correct = 0
    for i, it in enumerate(items):
        gt, d = donors[perm[i]]
        pred = oracle_predict(it["outcome_value"], gt, d)
        if pred == it["gold"]:
            correct += 1
    return correct / n_items

ps_scores = [pairscramble_acc(s) for s in range(5)]
ps_mean = sum(ps_scores) / len(ps_scores)
collapse_delta = oracle_acc - ps_mean

# determinism check: same seed -> bit-identical result, twice
determinism_ok = (pairscramble_acc(0) == pairscramble_acc(0)) and (ps_scores == [pairscramble_acc(s) for s in range(5)])

# =====================================================================
# SELF-CHECK 3: leakage lint on outcome_text
# =====================================================================
leak_offenders = []
seen_outcomes = set()
for it in items:
    if it["outcome_text"] in seen_outcomes:
        continue
    seen_outcomes.add(it["outcome_text"])
    m = BANNED_RE.findall(it["outcome_text"])
    if m:
        leak_offenders.append((it["outcome_text"], m))

# =====================================================================
# ASSERTIONS (fail loud, no weakening)
# =====================================================================
assert n_items >= 60, "n_items %d < 60" % n_items
assert n_met == n_unmet, "MET/UNMET imbalance: %d vs %d" % (n_met, n_unmet)
assert pairing_ok, "pairing integrity broken: some outcome_text does not have exactly 1 MET + 1 UNMET"
assert outcome_only_acc <= 0.55, "outcome-only acc too high: %.3f (leakage via outcome grouping)" % outcome_only_acc
assert oracle_acc >= 0.90, "goal-aware oracle acc too low: %.3f" % oracle_acc
assert collapse_delta >= 0.30, "pairscramble collapse too small: delta=%.3f" % collapse_delta
assert not leak_offenders, "LEAKAGE LINT FAILED: banned valence words found in outcome_text: %r" % leak_offenders
assert determinism_ok, "pairscramble is not deterministic across reruns"

# =====================================================================
# REPORT
# =====================================================================
print("=" * 90)
print("RELATION-DIAGNOSTIC EVAL (goal<->outcome ACHIEVEMENT) -- authored, self-checked")
print("=" * 90)
print("n_items = %d  (n_pairs = %d)   MET=%d  UNMET=%d" % (n_items, len(PAIRS), n_met, n_unmet))
print("-" * 90)
print("per relation_type counts:")
rt_counts = defaultdict(lambda: [0, 0])
for it in items:
    rt_counts[it["relation_type"]][0 if it["gold"] == "MET" else 1] += 1
for rt in ["numeric_threshold", "quantity_count", "temporal_deadline", "qualitative_attribute", "categorical_match"]:
    met, unmet = rt_counts[rt]
    print("  %-22s items=%3d  (MET=%d, UNMET=%d, pairs=%d)" % (rt, met + unmet, met, unmet, (met + unmet) // 2))
print("-" * 90)
print("SELF-CHECK RESULTS:")
print("  (1) pairing integrity (every outcome_text has exactly 1 MET + 1 UNMET) = %s" % pairing_ok)
print("  (2) OUTCOME-ONLY best-possible acc  = %.3f  (assert <= 0.55)  -> %s" % (
    outcome_only_acc, "PASS" if outcome_only_acc <= 0.55 else "FAIL"))
print("  (3) GOAL-AWARE oracle acc           = %.3f (%d/%d)  (assert >= 0.90) -> %s" % (
    oracle_acc, oracle_correct, n_items, "PASS" if oracle_acc >= 0.90 else "FAIL"))
print("  (4) PAIRSCRAMBLE mean acc (5 seeds) = %.3f   [seeds: %s]" % (
    ps_mean, ", ".join("%.3f" % s for s in ps_scores)))
print("      PAIRSCRAMBLE COLLAPSE delta     = %.3f  (assert >= 0.30) -> %s" % (
    collapse_delta, "PASS" if collapse_delta >= 0.30 else "FAIL"))
print("  (5) LEAKAGE LINT (banned valence words in outcome_text) offenders = %d -> %s" % (
    len(leak_offenders), "PASS" if not leak_offenders else "FAIL"))
if leak_offenders:
    for text, words in leak_offenders:
        print("      OFFENDER: %r  words=%r" % (text, words))
print("  (6) determinism (seeded, reruns bit-identical) = %s" % determinism_ok)
print("-" * 90)
print("6 SAMPLE ITEMS ACROSS SUBTYPES:")
sample_pair_ids = ["numeric_threshold_01", "quantity_count_02", "temporal_deadline_03",
                    "qualitative_attribute_04", "categorical_match_01"]
shown = 0
for pid in sample_pair_ids:
    for it in items:
        if it["pair_id"] == pid:
            print("  [%s] gold=%-5s goal=%r" % (it["relation_type"], it["gold"], it["goal_text"]))
            print("        outcome=%r" % it["outcome_text"])
            shown += 1
# one more to reach 6
for it in items:
    if shown >= 6:
        break
    if it["pair_id"] == "numeric_threshold_02":
        print("  [%s] gold=%-5s goal=%r" % (it["relation_type"], it["gold"], it["goal_text"]))
        print("        outcome=%r" % it["outcome_text"])
        shown += 1
print("=" * 90)
print("ALL ASSERTS PASSED." if True else "ASSERT FAILURE (see above)")

# =====================================================================
# WRITE JSONL (scratchpad only)
# =====================================================================
with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
    for it in items:
        f.write(json.dumps(it, ensure_ascii=True) + "\n")
print("Wrote %d items -> %s" % (n_items, OUT_PATH))
